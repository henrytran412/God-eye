"""Gate features for one candidate message.

Every feature is tagged as ego-verifiable or sender-asserted. That split is the
point: an attacker controls everything it asserts (its confidence, its claimed
pose covariance, its timestamp, its reputation history, and -- if it has
partners -- cross-agent agreement). Only features the ego computes from its own
sensor output are outside the attacker's reach. Keeping the tag in the code
makes the adaptive-attack ablation a one-line change instead of a rewrite.
"""
import numpy as np

from .sim import PED

FEATURES = [
    # name,                    sender_asserted
    ("conf",                   True),
    ("is_ped",                 True),
    ("log_area",               True),
    ("age",                    True),
    ("claimed_std",            True),
    ("sender_range",           True),
    ("sender_history",         True),
    ("sender_load",            True),
    ("n_agree_msgs",           True),   # forgeable by colluding senders
    ("n_agree_senders",        True),   # forgeable by colluding senders
    ("range_ego",              False),
    ("abs_bearing",            False),
    ("in_corridor",            False),
    ("lateral_offset",         False),
    ("dist_nearest_ego_det",   False),
    ("matches_ego_det",        False),
    ("ego_should_see",         False),  # free-space / occupancy consistency
    ("unexplained",            False),  # ego should see it but reports nothing
    ("local_msg_density",      False),
    ("persistence",            False),  # temporal confirmation over past frames
]
NAMES = [n for n, _ in FEATURES]
ASSERTED = np.array([a for _, a in FEATURES], dtype=bool)
EGO_VERIFIABLE = ~ASSERTED
DIM = len(FEATURES)

EGO_RANGE = 60.0
CORRIDOR_HALF_W = 2.5
CORRIDOR_LEN = 50.0


def _ray_blocked_by_ego_dets(x, y, ego_xy):
    """Would one of the ego's OWN detections occlude the point (x, y)?

    This is the ego-side occupancy-consistency test used by fabrication
    defences: if the ego has clear line of sight to a location and sees
    nothing there, a claim that an object sits there is unsupported.
    """
    d = np.hypot(x, y)
    if d < 1e-6:
        return True
    ux, uy = x / d, y / d
    for (ex, ey, el, ew) in ego_xy:
        t = ex * ux + ey * uy
        if t <= 0.5 or t >= d - 0.5:
            continue
        perp = abs(-ex * uy + ey * ux)
        if perp < 0.5 * max(el, ew) * 0.9:
            return True
    return False


def frame_features(ctx, prev_msgs=None):
    """Return (n_msg, DIM) feature matrix for the messages in ctx."""
    n = ctx.n_msg
    X = np.zeros((n, DIM), dtype=np.float32)
    if n == 0:
        return X
    ego_occ = [(e["x"], e["y"], e["l"], e["w"]) for e in ctx.ego]
    ego_xy = np.array([[e["x"], e["y"]] for e in ctx.ego]).reshape(-1, 2)
    senders = np.array([m["sender"] for m in ctx.msgs])
    load = {s: int((senders == s).sum()) for s in np.unique(senders)}

    prev_by_sender = {}
    for pm in (prev_msgs or []):
        prev_by_sender.setdefault(pm["sender"], []).append(pm)

    for i, m in enumerate(ctx.msgs):
        gi = ctx.n_ego + i
        x, y = float(m["x"]), float(m["y"])
        r_ego = float(np.hypot(x, y))
        gate = ctx.cluster_gate[gi]

        # cross-agent agreement, excluding the sender's own messages
        d_row = ctx.d_cc[gi, ctx.n_ego:]
        near = (d_row <= gate) & (np.arange(n) != i)
        other = near & (senders != m["sender"])
        n_agree = int(other.sum())
        n_agree_senders = int(len(np.unique(senders[other]))) if n_agree else 0

        if len(ego_xy):
            d_ego = float(np.min(ctx.d_cc[gi, :ctx.n_ego]))
        else:
            d_ego = np.inf
        matches_ego = float(np.isfinite(d_ego) and d_ego <= gate)
        should_see = float(r_ego <= EGO_RANGE
                           and not _ray_blocked_by_ego_dets(x, y, ego_occ))
        unexplained = float(should_see and not matches_ego)

        density = int(((ctx.d_cc[gi, ctx.n_ego:] <= 10.0)).sum()) - 1

        pers = 0.0
        pl = prev_by_sender.get(m["sender"], [])
        if pl:
            dd = min(float(np.hypot(p["x"] - x, p["y"] - y)) for p in pl)
            pers = float(dd <= max(gate, 2.0) + 1.5)

        X[i] = [
            m["conf"],
            1.0 if m["cls"] == PED else 0.0,
            np.log(max(m["l"] * m["w"], 1e-3)),
            m["age"],
            np.sqrt(max(m["claimed_cov"], 1e-6)),
            m["range_sender"] / 60.0,
            m["history"],
            load[m["sender"]] / 10.0,
            n_agree,
            n_agree_senders,
            r_ego / 60.0,
            abs(np.arctan2(y, x)),
            1.0 if (abs(y) < CORRIDOR_HALF_W and 0.0 < x < CORRIDOR_LEN) else 0.0,
            abs(y) / 12.0,
            min(d_ego, 20.0) / 20.0 if np.isfinite(d_ego) else 1.0,
            matches_ego,
            should_see,
            unexplained,
            density / 10.0,
            pers,
        ]
    return X


def mask_asserted(X):
    """Zero out every sender-asserted feature (adaptive-attacker ablation)."""
    Xm = X.copy()
    Xm[:, ASSERTED] = 0.0
    return Xm


# Graded trust tiers. The all-or-nothing version above is too blunt to be
# informative: it also removes class and size, which a benign sender reports
# honestly. These tiers correspond to attackers of increasing capability.
TIERS = {
    "all": [],
    "no_reputation": ["sender_history"],
    "no_collusion_signals": ["sender_history", "n_agree_msgs", "n_agree_senders"],
    "no_asserted_quality": ["sender_history", "n_agree_msgs", "n_agree_senders",
                            "conf", "claimed_std", "age"],
    "ego_verifiable_only": [n for n, a in FEATURES if a],
}


def drop_mask(names_to_drop):
    keep = np.array([n not in set(names_to_drop) for n in NAMES], dtype=bool)
    return keep


def mask_features(X, names_to_drop):
    """Zero the named features, keeping the input dimension fixed."""
    Xm = X.copy()
    for n in names_to_drop:
        Xm[:, NAMES.index(n)] = 0.0
    return Xm
