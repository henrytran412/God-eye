"""Admission policies: the baselines from the proposal plus two oracles.

Each policy maps one frame to a length-n_msg weight vector (1 accept, 0 reject,
in between = soft fusion). Policies that need memory across frames carry a
mutable `state` dict, which is how MATE-style temporal sender trust is modelled.

The oracles matter as much as the baselines. `oracle_loo` and `oracle_greedy`
use the ground-truth utility, so they bound what ANY per-message gate can do
with this risk function. If the learned gate lands near a cheap heuristic and
far from the oracle, the gap is a learning problem; if the oracle itself is
close to naive fusion, the whole premise is weak. That distinction is not
visible without them.
"""
import numpy as np

from . import features as FT
from . import utility as U

IDX = {n: i for i, n in enumerate(FT.NAMES)}


def ego_only(ctx, X, state=None):
    return np.zeros(ctx.n_msg)


def naive(ctx, X, state=None):
    return np.ones(ctx.n_msg)


def conf_thresh(tau=0.5):
    def f(ctx, X, state=None):
        return (X[:, IDX["conf"]] >= tau).astype(float)
    return f


def geom_consensus(k=1):
    """Accept if another sender corroborates, or the ego sees it itself."""
    def f(ctx, X, state=None):
        agree = X[:, IDX["n_agree_senders"]] >= k
        ego = X[:, IDX["matches_ego_det"]] > 0.5
        return (agree | ego).astype(float)
    return f


def belt_like(ctx, X, state=None):
    """Evidential-style soft weighting: trust scales with confidence and with
    the inverse of the claimed pose uncertainty. Accepts everything, but
    down-weights weak evidence (the BELT-Fusion / UECP family)."""
    conf = X[:, IDX["conf"]]
    std = X[:, IDX["claimed_std"]]
    e = conf / (std + 0.25)
    return np.clip(e / (1.0 + e), 0.05, 1.0)


def cad_like(ctx, X, state=None):
    """Occupancy-consistency check: reject a claim the ego can see through to
    and yet detects nothing at (the fabrication countermeasure family)."""
    return (X[:, IDX["unexplained"]] < 0.5).astype(float)


def robosac_like(thr=0.5):
    """Ego-consensus sender attestation: a sender whose in-view claims are
    mostly contradicted by the ego's own detections is dropped wholesale."""
    def f(ctx, X, state=None):
        senders = np.array([m["sender"] for m in ctx.msgs])
        w = np.ones(ctx.n_msg)
        for s in np.unique(senders):
            sel = senders == s
            inview = sel & (X[:, IDX["ego_should_see"]] > 0.5)
            if inview.sum() == 0:
                continue
            contradiction = X[inview, IDX["unexplained"]].mean()
            if contradiction > thr:
                w[sel] = 0.0
        return w
    return f


def mate_like(thr=0.45, lr=0.3):
    """Temporal sender trust: contradiction evidence accumulates across frames,
    and a sender below the trust floor is muted (the MATE family)."""
    def f(ctx, X, state):
        trust = state.setdefault("trust", {})
        senders = np.array([m["sender"] for m in ctx.msgs])
        w = np.ones(ctx.n_msg)
        for s in np.unique(senders):
            sel = senders == s
            inview = sel & (X[:, IDX["ego_should_see"]] > 0.5)
            t = trust.get(int(s), 0.8)
            if inview.sum() > 0:
                obs = 1.0 - X[inview, IDX["unexplained"]].mean()
                t = (1 - lr) * t + lr * obs
            trust[int(s)] = t
            if t < thr:
                w[sel] = 0.0
        return w
    return f


def oracle_loo(ctx, X, state=None):
    return (U.loo_utility(ctx) > 0).astype(float)


def oracle_greedy(ctx, X, state=None):
    w, _ = U.greedy_oracle(ctx)
    return w


def gate_policy(model, lam_reject, lam_quar=None, lam_soft=None,
                sigma_gate=None, soft_weight=0.4, mask_asserted=False,
                temporal_release=False, drop=None):
    """GhostGuard: learned utility gate with nested conformal action thresholds.

    `temporal_release` is what makes quarantine a distinct action rather than a
    relabelled rejection. Inside one frame a quarantined message and a rejected
    message both contribute weight 0, so they are the same decision. Quarantine
    only earns its place if a held message can be released once a later frame
    corroborates it -- here, when the same sender re-reports the same location.
    The cost of that is one frame of delay on a real object, which the
    single-frame risk R does not charge for and the timeline metric does.
    """
    from .crc import nested_actions

    def f(ctx, X, state=None):
        if ctx.n_msg == 0:
            return np.zeros(0)
        Xi = FT.mask_asserted(X) if mask_asserted else X
        if drop:
            Xi = FT.mask_features(Xi, drop)
        _, ph, sg = model.predict(Xi)
        lq = lam_quar if lam_quar is not None else lam_reject
        ls = lam_soft if lam_soft is not None else lam_reject
        w, quar = nested_actions(ph, sg, lam_reject, lq, ls,
                                 sigma_gate=sigma_gate, soft_weight=soft_weight)
        released = np.zeros(ctx.n_msg, dtype=bool)
        if temporal_release:
            confirmed = X[:, IDX["persistence"]] > 0.5
            released = quar & confirmed
            w[released] = soft_weight
        if state is not None:
            st = state.setdefault("q", dict(held=0, released=0, msgs=0))
            st["held"] += int(quar.sum())
            st["released"] += int(released.sum())
            st["msgs"] += ctx.n_msg
        return w
    return f


def gate_accept_only(model, tau, mask_asserted=False, drop=None):
    """Ablation: binary accept/reject on predicted harm, no soft-fuse, no
    quarantine, no conformal calibration. Isolates what the 4-action set buys."""
    def f(ctx, X, state=None):
        if ctx.n_msg == 0:
            return np.zeros(0)
        Xi = FT.mask_asserted(X) if mask_asserted else X
        if drop:
            Xi = FT.mask_features(Xi, drop)
        _, ph, _ = model.predict(Xi)
        return (ph < tau).astype(float)
    return f
