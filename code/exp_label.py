"""Diagnostic 1: is E_S[U(m|S)] a well-posed training target?"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.stats import spearmanr, pearsonr
from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx
from ghostguard import utility as U

rs = np.random.default_rng(7)
ATT = ["none", "spoof", "collusion"]
rows = []
t0 = time.perf_counter()
for atk in ATT:
    cfg = SimConfig(attack=atk, n_attackers=2)
    for _ in range(28):
        seq = make_sequence(cfg, rs)
        for f in seq["frames"][::3]:            # subsample frames
            ctx = FrameCtx(f)
            if ctx.n_msg == 0:
                continue
            um, us_, cnt = U.coalition_labels(ctx, n_coalitions=32, rs=rs)
            usolo = U.solo_utility(ctx)
            uloo = U.loo_utility(ctx)
            _, ugre = U.greedy_oracle(ctx)
            for i, m in enumerate(ctx.msgs):
                kind = ("fabricated" if m["fabricated"]
                        else "true" if m["gt_id"] >= 0 else "honest_fp")
                ro = (m["gt_id"] >= 0 and m["gt_id"] not in ctx.ego_vis)
                rows.append(dict(atk=atk, kind=kind, remote_only=bool(ro),
                                 u_marg=um[i], u_marg_sd=us_[i], u_solo=usolo[i],
                                 u_loo=uloo[i], u_greedy=ugre[i], n_cnt=int(cnt[i])))
print(f"labelled {len(rows)} messages in {time.perf_counter()-t0:.0f}s\n")

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv("results/label_diagnostic.csv", index=False)

d = U.DELTA
print("=== class balance of E_S[U] (delta=%.2f) ===" % d)
for atk in ATT:
    s = df[df.atk == atk]
    for var in ["u_marg", "u_loo", "u_greedy"]:
        v = s[var].values
        print(f"  {atk:10s} {var:9s} helpful={np.mean(v>d):5.1%} "
              f"redundant={np.mean(np.abs(v)<=d):5.1%} harmful={np.mean(v<-d):5.1%}")
    print()

print("=== agreement between utility variants (all attacks pooled) ===")
pairs = [("u_marg","u_loo"),("u_marg","u_greedy"),("u_marg","u_solo"),("u_loo","u_greedy")]
for a,b in pairs:
    x,y = df[a].values, df[b].values
    ok = np.isfinite(x)&np.isfinite(y)
    x,y = x[ok],y[ok]
    sign_agree = np.mean(np.sign(np.where(np.abs(x)<=d,0,x)) == np.sign(np.where(np.abs(y)<=d,0,y)))
    # decision-relevant flips: one says helpful, the other says harmful
    flip = np.mean(((x>d)&(y<-d)) | ((x<-d)&(y>d)))
    print(f"  {a:8s} vs {b:9s}  pearson={pearsonr(x,y)[0]:+.3f} spearman={spearmanr(x,y)[0]:+.3f}"
          f"  3-class agree={sign_agree:5.1%}  sign FLIP={flip:5.1%}")

print("\n=== context dependence: sd of U(m|S) across coalitions vs |mean| ===")
v = df[df.n_cnt>=8]
ratio = v.u_marg_sd.values / np.maximum(np.abs(v.u_marg.values), 1e-6)
print(f"  median sd/|mean| = {np.median(ratio):.2f}   frac with sd > |mean| = {np.mean(ratio>1):.1%}")
print(f"  median sd        = {np.median(v.u_marg_sd.values):.3f} risk units")

print("\n=== mean utility by message kind ===")
print(df.groupby(["atk","kind"])[["u_marg","u_solo","u_loo","u_greedy"]].mean().round(3).to_string())
print("\n=== remote-only true messages (the ones cooperation exists for) ===")
ro = df[(df.kind=="true")]
print(ro.groupby(["atk","remote_only"])[["u_marg","u_loo"]].agg(["mean","count"]).round(3).to_string())
