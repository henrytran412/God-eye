"""Diagnostic 3: is the gate's harm probability calibrated enough for CRC?

The conformal thresholds are quantiles of p_hat_harm. If that score is
overconfident in the low tail -- lots of genuinely harmful messages assigned
p_hat < 0.02 -- then no lambda in the useful range can separate them, the
achievable risk floor jumps, and CRC's feasible set collapses to "reject
everything". This measures the reliability curve directly and checks whether a
post-hoc calibration map fixes it.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx, in_roi
from ghostguard import features as FT
from ghostguard import utility as U
from ghostguard.gate import GateModel

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def build(n, attack, rs, **kw):
    cfg = SimConfig(attack=attack, **kw)
    out = []
    for _ in range(n):
        seq = make_sequence(cfg, rs)
        prev = None
        for f in seq["frames"]:
            ctx = FrameCtx(f)
            out.append((ctx, FT.frame_features(ctx, prev_msgs=prev)))
            prev = f["msgs"]
    return out


def collect(data):
    X, u, bad = [], [], []
    for ctx, x in data:
        if ctx.n_msg == 0:
            continue
        X.append(x)
        u.append(U.solo_utility(ctx))
        bad.append(np.array([(m["gt_id"] == -1) and in_roi(m["x"], m["y"])
                             for m in ctx.msgs]))
    return np.concatenate(X), np.concatenate(u), np.concatenate(bad)


def isotonic(p, y):
    """Pool-adjacent-violators isotonic regression; returns a step function."""
    o = np.argsort(p)
    ps, ys = p[o], y[o].astype(float)
    val = list(ys)
    wt = [1.0] * len(ys)
    i = 0
    while i < len(val) - 1:
        if val[i] > val[i + 1] + 1e-12:
            tw = wt[i] + wt[i + 1]
            nv = (val[i] * wt[i] + val[i + 1] * wt[i + 1]) / tw
            val[i:i + 2] = [nv]
            wt[i:i + 2] = [tw]
            if i > 0:
                i -= 1
        else:
            i += 1
    xs, fs = [], []
    k = 0
    for v, w in zip(val, wt):
        n = int(round(w))
        xs.append(ps[k])
        fs.append(v)
        k += n
    xs, fs = np.array(xs), np.array(fs)
    return lambda q: np.interp(q, xs, fs)


def reliability(p, y, edges):
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi)
        if m.sum() < 20:
            continue
        rows.append(dict(bin=f"[{lo:.3g},{hi:.3g})", n=int(m.sum()),
                         mean_pred=float(p[m].mean()),
                         actual_ghost_frac=float(y[m].mean())))
    return pd.DataFrame(rows)


def main():
    rs = np.random.default_rng(11)
    mix = [("none", 60), ("spoof", 45), ("collusion", 30)]
    tr = sum([build(n, a, rs) for a, n in mix], [])
    ca = sum([build(n, a, rs) for a, n in [("none", 30), ("spoof", 22),
                                           ("collusion", 15)]], [])
    te = sum([build(n, a, rs) for a, n in [("none", 30), ("spoof", 22),
                                           ("collusion", 15)]], [])
    Xtr, utr, _ = collect(tr)
    model = GateModel(FT.DIM, seed=0).fit(Xtr, utr, utr < -U.DELTA)
    Xca, _, yca = collect(ca)
    Xte, _, yte = collect(te)
    _, pca, _ = model.predict(Xca)
    _, pte, _ = model.predict(Xte)

    edges = np.array([0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
    print(f"test messages {len(yte)}, base ghost rate {yte.mean():.3f}\n")
    print("=== RAW gate p_harm: reliability on test ===")
    print(reliability(pte, yte, edges).round(4).to_string(index=False))
    ece = lambda p, y: float(np.mean(np.abs(
        np.array([y[(p >= lo) & (p < hi)].mean() - p[(p >= lo) & (p < hi)].mean()
                  for lo, hi in zip(edges[:-1], edges[1:])
                  if ((p >= lo) & (p < hi)).sum() >= 20]))))
    print(f"\nmean |predicted - actual| across bins (raw): {ece(pte, yte):.4f}")
    frac_low = float((pte < 0.02).mean())
    ghosts_low = float(yte[pte < 0.02].mean()) if (pte < 0.02).any() else float("nan")
    print(f"messages with p_harm < 0.02: {frac_low:.3f} of all; "
          f"{ghosts_low:.3f} of those are ghosts")

    cal = isotonic(pca, yca)
    qte = cal(pte)
    print("\n=== ISOTONIC-CALIBRATED p_harm: reliability on test ===")
    print(reliability(qte, yte, edges).round(4).to_string(index=False))
    print(f"\nmean |predicted - actual| across bins (calibrated): {ece(qte, yte):.4f}")

    # what the achievable CRC floor looks like before vs after calibration
    print("\n=== achievable harm floor vs threshold (share of ghosts admitted) ===")
    rows = []
    for lam in [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]:
        rows.append(dict(lam=lam,
                         raw_ghost_admit=float(yte[pte < lam].sum() / max(yte.sum(), 1)),
                         raw_accept=float((pte < lam).mean()),
                         cal_ghost_admit=float(yte[qte < lam].sum() / max(yte.sum(), 1)),
                         cal_accept=float((qte < lam).mean())))
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(OUT, "gate_calibration.csv"), index=False)
    print(d.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
