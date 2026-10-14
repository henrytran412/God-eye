"""Diagnostic 4: the redundancy trap.

The proposal reads near-zero utility as "redundant" and routes it away from
plain acceptance. But redundancy is a property of a SET, not of a message. When
k senders all report the same remote-only pedestrian, each copy is individually
near-zero -- dropping any one changes nothing -- yet dropping all k loses the
object entirely.

This measures recovery of remote-only objects split by how many messages cover
them, for three admission rules:

  keep_positive_loo   accept iff U(m | everything else) > 0   (the trap)
  keep_positive_solo  accept iff U(m | {}) > 0                (immune: each copy
                      is judged on its own, so at least one survives)
  greedy              sequential, context-aware                (the oracle)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx
from ghostguard import utility as U

rs = np.random.default_rng(23)
rows = []
for atk, n in [("none", 55), ("spoof", 35)]:
    cfg = SimConfig(attack=atk, n_attackers=2, n_cav=4)
    for _ in range(n):
        seq = make_sequence(cfg, rs)
        for f in seq["frames"]:
            ctx = FrameCtx(f)
            if ctx.n_msg == 0 or not len(ctx.gt):
                continue
            pol = {
                "keep_positive_loo": (U.loo_utility(ctx) > 0).astype(float),
                "keep_positive_solo": (U.solo_utility(ctx) > 0).astype(float),
                "greedy": U.greedy_oracle(ctx)[0],
                "accept_all": np.ones(ctx.n_msg),
            }
            gt_ids = {int(g["id"]): j for j, g in enumerate(ctx.gt)}
            cover = {}
            for m in ctx.msgs:
                if m["gt_id"] >= 0 and m["gt_id"] not in ctx.ego_vis:
                    cover.setdefault(int(m["gt_id"]), []).append(m)
            for oid, ms in cover.items():
                k = len(set(mm["sender"] for mm in ms))
                idx = [i for i, m in enumerate(ctx.msgs) if m["gt_id"] == oid]
                for pname, w in pol.items():
                    gm, _, _ = ctx.match(ctx.fuse(w))
                    rows.append(dict(atk=atk, policy=pname, n_senders=k,
                                     admitted=int((w[idx] > 0).sum()),
                                     recovered=bool(gm[gt_ids[oid]] >= 0)))
df = pd.DataFrame(rows)
df.to_csv("results/redundancy.csv", index=False)

df["cover"] = np.where(df.n_senders == 1, "1 sender",
                np.where(df.n_senders == 2, "2 senders", "3+ senders"))
print(f"{len(df)//4} remote-only object instances observed\n")
print("=== recovery rate of remote-only objects, by how many senders report them ===")
piv = df.pivot_table(index="policy", columns="cover", values="recovered")
print(piv.round(3).to_string())
print("\n=== messages admitted per object (of those available) ===")
piv2 = df.pivot_table(index="policy", columns="cover", values="admitted")
print(piv2.round(2).to_string())
print("\n=== objects LOST although at least one message carried them ===")
for pname in ["keep_positive_loo", "keep_positive_solo", "greedy", "accept_all"]:
    s = df[df.policy == pname]
    multi = s[s.n_senders >= 2]
    print(f"  {pname:20s} overall lost {1-s.recovered.mean():.3f} | "
          f"multi-sender objects lost {1-multi.recovered.mean():.3f} "
          f"(n={len(multi)}) | admitted 0 msgs for {float((multi.admitted==0).mean()):.3f}")
