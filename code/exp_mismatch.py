"""Is the gate's training target the same quantity the guarantee is about?

The gate learns P(U(m) < -delta): "admitting this lowers safety".
The conformal loss counts messages that assert an object which is not there.
These are only the same event if every non-existent object that is admitted
actually changes the fused output. It does not: a ghost that NMS folds into an
existing cluster, or one that lands below the operating score threshold, or one
outside the scored region, costs nothing -- so it is harmless by utility and
harmful by count.

If the two disagree, the conformal thresholds are quantiles of a score that was
never trained to rank the thing being controlled.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx, in_roi
from ghostguard import features as FT
from ghostguard import utility as U

rs = np.random.default_rng(17)
rows = []
for atk, n in [("none", 45), ("spoof", 35), ("collusion", 25)]:
    cfg = SimConfig(attack=atk, n_attackers=2)
    for _ in range(n):
        seq = make_sequence(cfg, rs)
        for f in seq["frames"]:
            ctx = FrameCtx(f)
            if ctx.n_msg == 0:
                continue
            us = U.solo_utility(ctx)
            um, _, _ = U.coalition_labels(ctx, n_coalitions=8, rs=rs)
            for i, m in enumerate(ctx.msgs):
                rows.append(dict(
                    atk=atk,
                    nonexistent=(m["gt_id"] == -1) and in_roi(m["x"], m["y"]),
                    fabricated=bool(m["fabricated"]),
                    harmful_solo=bool(us[i] < -U.DELTA),
                    harmful_marg=bool(um[i] < -U.DELTA),
                    u_solo=us[i], u_marg=um[i], conf=m["conf"]))
df = pd.DataFrame(rows)
df.to_csv("results/target_mismatch.csv", index=False)

print(f"{len(df)} messages\n")
print("=== agreement: 'asserts a non-existent object' vs 'utility is negative' ===")
for lab, col in [("U(m|empty) < -delta", "harmful_solo"),
                 ("E_S[U] < -delta", "harmful_marg")]:
    a = df.nonexistent.values
    b = df[col].values
    tp = (a & b).sum(); fn = (a & ~b).sum(); fp = (~a & b).sum(); tn = (~a & ~b).sum()
    print(f"\n  {lab}")
    print(f"    non-existent AND flagged harmful : {tp:6d}")
    print(f"    non-existent BUT not harmful     : {fn:6d}   <- guarantee charges, gate does not")
    print(f"    real object BUT flagged harmful  : {fp:6d}")
    print(f"    real object and not harmful      : {tn:6d}")
    print(f"    agreement = {(tp+tn)/len(df):.3f};  "
          f"of non-existent objects, {fn/max(tp+fn,1):.1%} have ~zero utility cost")

print("\n=== why a non-existent object can be free: utility of ghost messages ===")
g = df[df.nonexistent]
print(f"  n={len(g)}  mean U(m|empty)={g.u_solo.mean():.3f}  "
      f"median={g.u_solo.median():.3f}")
print(f"  share with |U| <= delta (no measurable effect): "
      f"{float((g.u_solo.abs() <= U.DELTA).mean()):.3f}")
print(f"  share with U > 0 (a ghost that HELPS the risk): "
      f"{float((g.u_solo > U.DELTA).mean()):.3f}")
lo = g[g.conf < 0.3]
print(f"  of low-confidence ghosts (conf<0.3, n={len(lo)}): "
      f"{float((lo.u_solo.abs() <= U.DELTA).mean()):.3f} have no effect "
      f"(they fall below the operating threshold)")
