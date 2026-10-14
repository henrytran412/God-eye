import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from ghostguard.sim import SimConfig, make_sequence

rs = np.random.default_rng(0)
for atk in ["none", "spoof", "collusion", "removal"]:
    cfg = SimConfig(attack=atk, n_attackers=2)
    seqs = [make_sequence(cfg, rs) for _ in range(30)]
    fr = [f for s in seqs for f in s["frames"]]
    ngt = np.mean([len(f["gt"]) for f in fr])
    nro = np.mean([len([g for g in f["gt"] if g["id"] not in f["ego_vis"]]) for f in fr])
    nm = np.mean([len(f["msgs"]) for f in fr])
    ne = np.mean([len(f["ego"]) for f in fr])
    nfab = np.mean([len([m for m in f["msgs"] if m["fabricated"]]) for f in fr])
    # how many remote-only GT objects are actually covered by some message
    cov = []
    for f in fr:
        ro = set(g["id"] for g in f["gt"]) - f["ego_vis"]
        if ro:
            hit = set(m["gt_id"] for m in f["msgs"]) & ro
            cov.append(len(hit) / len(ro))
    honest_fp = np.mean([len([m for m in f["msgs"] if m["gt_id"] == -1 and not m["fabricated"]]) for f in fr])
    print(f"{atk:10s} gt={ngt:5.2f} remote_only={nro:4.2f} ego_det={ne:5.2f} "
          f"msgs={nm:5.2f} honest_fp={honest_fp:4.2f} fabricated={nfab:4.2f} "
          f"RO_coverage={np.mean(cov) if cov else float('nan'):.2f}")

# confidence separability: can confidence alone separate real from fake?
cfg = SimConfig(attack="spoof", n_attackers=1)
seqs = [make_sequence(cfg, rs) for _ in range(60)]
tp = [m["conf"] for s in seqs for f in s["frames"] for m in f["msgs"] if m["gt_id"] >= 0]
fp = [m["conf"] for s in seqs for f in s["frames"] for m in f["msgs"] if m["gt_id"] == -1 and not m["fabricated"]]
fb = [m["conf"] for s in seqs for f in s["frames"] for m in f["msgs"] if m["fabricated"]]
print(f"\nconf  true-pos  mean={np.mean(tp):.3f}  n={len(tp)}")
print(f"conf  honest-FP mean={np.mean(fp):.3f}  n={len(fp)}")
print(f"conf  fabricated mean={np.mean(fb):.3f}  n={len(fb)}   <- high-confidence lies")
