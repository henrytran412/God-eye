"""Diagnostic 2: what is the exchangeable unit for conformal calibration?

Conformal risk control guarantees E[L_test(lambda_hat)] <= alpha, where the
expectation is over the draw of the calibration set as well as the test point,
and only when calibration points and the test point are exchangeable.

Cooperative-perception data is sequential: ten consecutive frames of one
scenario share the same objects, the same senders, the same sender pose error
and the same attacker. So there are two candidate calibration units:

  frame_unit  each frame is one calibration point (n = scenarios x frames).
              This is the natural reading of "calibrate on held-out data".
  seq_unit    each scenario is one calibration point, its loss being the mean
              over its frames (n = scenarios).

Both are compared over many random scenario-level splits and several
calibration sizes. Two quantities are reported, and the difference between
them is the point:

  mean_test_risk           what CRC actually bounds by alpha.
  frac_splits_over_alpha   the share of individual deployments whose realised
                           risk exceeds alpha anyway.

A method can be perfectly valid on the first and still overshoot the target on
a third of deployments -- which is what a safety argument would need to know.
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
from ghostguard.crc import crc_threshold

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
LAM = np.concatenate([[0.0], np.logspace(-4, 0, 80)])
ALPHAS = [0.10, 0.20, 0.30, 0.40]
N_SPLIT = 200


def build(n_seq, attack, rs, **kw):
    cfg = SimConfig(attack=attack, **kw)
    out = []
    for _ in range(n_seq):
        seq = make_sequence(cfg, rs)
        prev, frames = None, []
        for f in seq["frames"]:
            ctx = FrameCtx(f)
            frames.append((ctx, FT.frame_features(ctx, prev_msgs=prev)))
            prev = f["msgs"]
        out.append(frames)
    return out


def loss_table(data, model, cap=3.0):
    """(n_seq, n_frame, n_lambda) loss array."""
    out = []
    for seq in data:
        rows = []
        for ctx, X in seq:
            if ctx.n_msg == 0:
                rows.append(np.zeros(len(LAM)))
                continue
            _, ph, _ = model.predict(X)
            bad = np.array([(m["gt_id"] == -1) and in_roi(m["x"], m["y"])
                            for m in ctx.msgs])
            rows.append(np.array([min(1.0, float(((ph < l) & bad).sum()) / cap)
                                  for l in LAM]))
        out.append(np.stack(rows))
    return np.stack(out)


def main():
    rs = np.random.default_rng(31)
    print("building + training gate ...", flush=True)
    train = build(90, "none", rs)
    Xs, us = [], []
    for seq in train:
        for ctx, X in seq:
            if ctx.n_msg == 0:
                continue
            Xs.append(X)
            us.append(U.solo_utility(ctx))
    Xtr, utr = np.concatenate(Xs), np.concatenate(us)
    model = GateModel(FT.DIM, seed=0).fit(Xtr, utr, utr < -U.DELTA)

    print("building calibration pool ...", flush=True)
    pool = build(300, "none", rs)
    Lc = loss_table(pool, model)          # (n_seq, n_frame, n_lam)
    n_seq = Lc.shape[0]
    print(f"pool: {n_seq} scenarios x {Lc.shape[1]} frames", flush=True)

    rows = []
    rng = np.random.default_rng(7)
    for n_cal_seq in [25, 75, 150]:
      for alpha in ALPHAS:
        stat = {p: [] for p in ["frame_unit", "seq_unit"]}
        degen = {p: 0 for p in stat}
        for _ in range(N_SPLIT):
            perm = rng.permutation(n_seq)
            cal_s, test_s = perm[:n_cal_seq], perm[n_cal_seq:]

            # frame as the calibration unit: n = n_cal_seq * frames_per_seq
            k, _, _ = crc_threshold(Lc[cal_s].reshape(-1, Lc.shape[2]), alpha)
            degen["frame_unit"] += int(k <= 0)
            stat["frame_unit"].append(
                Lc[test_s].reshape(-1, Lc.shape[2])[:, k].mean() if k >= 0 else 0.0)

            # scenario as the calibration unit: n = n_cal_seq
            k, _, _ = crc_threshold(Lc[cal_s].mean(axis=1), alpha)
            degen["seq_unit"] += int(k <= 0)
            stat["seq_unit"].append(
                Lc[test_s].mean(axis=1)[:, k].mean() if k >= 0 else 0.0)

        for proto, v in stat.items():
            v = np.array(v)
            rows.append(dict(n_cal_seq=n_cal_seq, alpha=alpha, protocol=proto,
                             mean_test_risk=v.mean(),
                             frac_splits_over_alpha=float((v > alpha).mean()),
                             p90_test_risk=float(np.quantile(v, 0.9)),
                             frac_degenerate_reject_all=degen[proto] / N_SPLIT))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "crc_exchangeability.csv"), index=False)
    print(f"\n{N_SPLIT} random splits of {n_seq} benign scenarios, "
          f"calibration = half the pool\n")
    print(df.round(4).to_string(index=False))
    print("\nCRC bounds the MEAN test risk by alpha. A protocol whose mean")
    print("exceeds alpha has an invalid guarantee, not merely an unlucky split.")


if __name__ == "__main__":
    main()
