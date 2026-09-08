"""Latency and label-cost accounting (the proposal lists both as metrics)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx
from ghostguard import features as FT
from ghostguard.gate import GateModel
from ghostguard import utility as U

rs = np.random.default_rng(5)
cfg = SimConfig(attack="spoof", n_attackers=2)
seqs = [make_sequence(cfg, rs) for _ in range(12)]
frames, prev = [], None
for s in seqs:
    prev = None
    for f in s["frames"]:
        ctx = FrameCtx(f)
        frames.append((ctx, FT.frame_features(ctx, prev_msgs=prev)))
        prev = f["msgs"]

model = GateModel(FT.DIM, seed=0)
X = np.concatenate([x for _, x in frames if len(x)])
model.fit(X, np.zeros(len(X)), np.zeros(len(X), dtype=bool), epochs=3)

# inference: feature extraction + gate forward, per frame
t = time.perf_counter()
for ctx, x in frames:
    FT.frame_features(ctx)
t_feat = (time.perf_counter() - t) / len(frames) * 1e3
t = time.perf_counter()
for ctx, x in frames:
    model.predict(x)
t_gate = (time.perf_counter() - t) / len(frames) * 1e3
t = time.perf_counter()
for ctx, x in frames:
    ctx.fuse(np.ones(ctx.n_msg))
t_fuse = (time.perf_counter() - t) / len(frames) * 1e3
nmsg = np.mean([c.n_msg for c, _ in frames])

print(f"messages/frame          {nmsg:.1f}")
print(f"feature extraction      {t_feat:.2f} ms/frame")
print(f"gate forward pass       {t_gate:.2f} ms/frame")
print(f"late fusion + NMS       {t_fuse:.2f} ms/frame")
print(f"INFERENCE TOTAL         {t_feat+t_gate+t_fuse:.2f} ms/frame  "
      f"(budget at 10 Hz = 100 ms)")

# training-time label cost
for K in [8, 16, 32]:
    t = time.perf_counter()
    for ctx, _ in frames[:40]:
        U.coalition_labels(ctx, n_coalitions=K, rs=rs)
    dt = (time.perf_counter() - t) / 40
    reruns = K * (1 + nmsg * 0.5)
    print(f"coalition labelling K={K:2d}: {dt*1e3:6.1f} ms/frame  "
          f"~{reruns:.0f} fusion re-runs/frame")

# message payload: object-level late fusion is tiny
print("\npayload per object message: 5 box floats + class + conf + timestamp"
      " + pose cov ~= 40 B")
print(f"at {nmsg:.0f} msgs/frame, 10 Hz  ->  ~{nmsg*40*10/1024:.1f} KiB/s per ego")
