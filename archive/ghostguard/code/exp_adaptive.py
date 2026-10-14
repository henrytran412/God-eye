"""Diagnostic 5: does the gate detect fabrication, or the attacker's fingerprint?

The tier ablation showed the gate's resistance to fabrication rests on
confidence, claimed pose covariance and message age -- three fields the sender
asserts and an adversary sets freely. A naive spoofer gives itself away by
shouting: near-certain confidence, an implausibly tight covariance, zero age.
An adaptive spoofer samples those fields from the benign distribution instead,
leaving only geometry to give it away.

Three gates, so transfer and re-training are separated:

  trained on naive attacks   -> tested on naive, then on adaptive  (transfer)
  trained on adaptive        -> tested on adaptive                 (ceiling)
  trained on adaptive, ego-verifiable features only                (what the
                                geometry alone can carry)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx
from ghostguard import features as FT
from ghostguard import utility as U
from ghostguard import baselines as B
from ghostguard.gate import GateModel
from ghostguard.metrics import Accum

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def build(n, attack, rs, **kw):
    cfg = SimConfig(attack=attack, **kw)
    out = []
    for _ in range(n):
        seq = make_sequence(cfg, rs)
        prev, fr = None, []
        for f in seq["frames"]:
            ctx = FrameCtx(f)
            fr.append((ctx, FT.frame_features(ctx, prev_msgs=prev)))
            prev = f["msgs"]
        out.append(fr)
    return out


def label(data):
    X, u = [], []
    for seq in data:
        for ctx, x in seq:
            if ctx.n_msg == 0:
                continue
            X.append(x)
            u.append(U.solo_utility(ctx))
    return np.concatenate(X), np.concatenate(u)


def ev(data, pol):
    acc = Accum()
    for seq in data:
        st = {}
        for ctx, x in seq:
            acc.add(ctx, pol(ctx, x, st))
    return acc.summary()


def main():
    rs = np.random.default_rng(41)
    mix_naive = [("none", 55), ("spoof", 40), ("collusion", 30)]
    mix_adapt = [("none", 55), ("spoof_adaptive", 40), ("collusion_adaptive", 30)]
    print("building ...", flush=True)
    tr_naive = sum([build(n, a, rs) for a, n in mix_naive], [])
    tr_adapt = sum([build(n, a, rs) for a, n in mix_adapt], [])
    te = {a: build(45, a, rs, n_attackers=2)
          for a in ["spoof", "spoof_adaptive", "collusion", "collusion_adaptive"]}

    Xn, un = label(tr_naive)
    Xa, ua = label(tr_adapt)
    print("training ...", flush=True)
    g_naive = GateModel(FT.DIM, seed=0).fit(Xn, un, un < -U.DELTA)
    g_adapt = GateModel(FT.DIM, seed=0).fit(Xa, ua, ua < -U.DELTA)
    drop = FT.TIERS["ego_verifiable_only"]
    g_geo = GateModel(FT.DIM, seed=0).fit(FT.mask_features(Xa, drop), ua,
                                          ua < -U.DELTA)

    rows = []
    setups = [
        ("gate trained on naive attacks", g_naive, None),
        ("gate retrained on adaptive", g_adapt, None),
        ("gate retrained, geometry only", g_geo, drop),
    ]
    for lab, g, dr in setups:
        for cond, data in te.items():
            s = ev(data, B.gate_accept_only(g, 0.5, drop=dr))
            s.update(gate=lab, condition=cond)
            rows.append(s)
    for cond, data in te.items():
        for nm, pol in [("naive_lf", B.naive), ("ego_only", B.ego_only),
                        ("cad_like", B.cad_like), ("oracle_greedy", B.oracle_greedy)]:
            s = ev(data, pol)
            s.update(gate=nm, condition=cond)
            rows.append(s)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "adaptive_attack.csv"), index=False)

    for metric in ["malicious_accept", "R", "AP", "RO_recall"]:
        print(f"\n=== {metric} ===")
        print(df.pivot(index="gate", columns="condition", values=metric)
              [["spoof", "spoof_adaptive", "collusion", "collusion_adaptive"]]
              .round(3).to_string())


if __name__ == "__main__":
    main()
