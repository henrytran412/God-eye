import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx

rs = np.random.default_rng(1)
for atk in ["none", "spoof", "collusion", "removal"]:
    cfg = SimConfig(attack=atk, n_attackers=2)
    seqs = [make_sequence(cfg, rs) for _ in range(25)]
    rows = {}
    for name, wfun in [("ego_only", lambda n: np.zeros(n)),
                       ("naive_all", lambda n: np.ones(n))]:
        acc = []
        for s in seqs:
            for f in s["frames"]:
                ctx = FrameCtx(f)
                r, b = ctx.risk_of(wfun(ctx.n_msg), breakdown=True)
                acc.append([r, b["n_miss"], b["n_ghost"], b["n_dup"], b["ro_hit"], b["ro_total"]])
        a = np.array(acc, dtype=float)
        rows[name] = a.mean(axis=0)
    e, n = rows["ego_only"], rows["naive_all"]
    print(f"{atk:10s} R ego={e[0]:6.2f} naive={n[0]:6.2f} | miss {e[1]:.2f}->{n[1]:.2f} "
          f"| ghost {e[2]:.2f}->{n[2]:.2f} | dup {e[3]:.2f}->{n[3]:.2f} "
          f"| RO-recall {e[4]/max(e[5],1e-9):.2f}->{n[4]/max(n[5],1e-9):.2f}")

# score fusion mode effect under collusion
cfg = SimConfig(attack="collusion", n_attackers=2)
seqs = [make_sequence(cfg, rs) for _ in range(25)]
print()
for mode in ["max", "or", "mean"]:
    acc = []
    for s in seqs:
        for f in s["frames"]:
            ctx = FrameCtx(f)
            r, b = ctx.risk_of(np.ones(ctx.n_msg), score_mode=mode, breakdown=True)
            acc.append([r, b["n_ghost"], b["n_miss"]])
    a = np.array(acc).mean(axis=0)
    print(f"score_mode={mode:5s}  R={a[0]:6.2f}  ghosts={a[1]:.2f}  misses={a[2]:.2f}")

# timing of one fusion+risk call
ctx = FrameCtx(seqs[0]["frames"][0])
t0 = time.perf_counter()
for _ in range(2000):
    ctx.risk_of(np.random.rand(ctx.n_msg) > 0.5)
print(f"\nfuse+risk: {(time.perf_counter()-t0)/2000*1e6:.0f} us/call  (n_msg={ctx.n_msg}, n_gt={len(ctx.gt)})")
