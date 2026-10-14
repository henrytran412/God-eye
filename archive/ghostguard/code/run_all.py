"""GhostGuard baseline reproduction + design audit.

Stages
  1  build datasets (train / calibration / per-attack test)
  2  coalition-label the training messages, train the gates
  3  conformal risk control: sweep alpha, show the achievable floor, and test
     whether the guarantee transfers under shift and under attack
  4  evaluate every policy on every condition at its calibrated operating point
  5  matched-operating-point trade-off curves (the fair comparison)
  6  feature-trust tiers (adaptive attacker)
  7  risk-weight sensitivity (does the ranking survive re-weighting?)
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

from ghostguard.sim import SimConfig, make_sequence
from ghostguard.fusion import FrameCtx, RISK_W, in_roi
from ghostguard import features as FT
from ghostguard import utility as U
from ghostguard import baselines as B
from ghostguard.gate import GateModel
from ghostguard.crc import crc_threshold, check_monotone
from ghostguard.metrics import Accum

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
os.makedirs(OUT, exist_ok=True)
CORE = ["none", "spoof", "collusion"]


def build(n_seq, attack, rs, risk_w=None, **kw):
    cfg = SimConfig(attack=attack, **kw)
    out = []
    for _ in range(n_seq):
        seq = make_sequence(cfg, rs)
        prev, frames = None, []
        for f in seq["frames"]:
            ctx = FrameCtx(f, risk_w=risk_w)
            frames.append((ctx, FT.frame_features(ctx, prev_msgs=prev)))
            prev = f["msgs"]
        out.append(frames)
    return out


def build_mixed(n_seq, rs, mix, **kw):
    out = []
    for attack, frac in mix.items():
        out += build(max(1, int(round(n_seq * frac))), attack, rs, **kw)
    return out


def evaluate(data, policy, score_mode="max"):
    acc = Accum()
    for seq in data:
        state = {}
        for ctx, X in seq:
            acc.add(ctx, policy(ctx, X, state), score_mode)
        q = state.get("q")
        if q:
            acc.quarantined += q["held"] - q["released"]
    return acc.summary()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-train", type=int, default=200)
    ap.add_argument("--n-cal", type=int, default=140)
    ap.add_argument("--n-test", type=int, default=110)
    ap.add_argument("--n-sweep", type=int, default=70)
    ap.add_argument("--coalitions", type=int, default=16)
    args = ap.parse_args()
    rs = np.random.default_rng(2024)
    T0 = time.perf_counter()
    log = lambda m: print(f"[{time.perf_counter()-T0:6.0f}s] {m}", flush=True)

    # -------------------------------------------------- 1. data
    log("building data ...")
    mix = {"none": 0.40, "spoof": 0.30, "collusion": 0.20, "removal": 0.10}
    train = build_mixed(args.n_train, rs, mix, n_attackers=2)
    cal_benign = build(args.n_cal, "none", rs)
    tests = {a: build(args.n_test, a, rs, n_attackers=2)
             for a in ["none", "spoof", "collusion", "removal"]}
    tests["degraded"] = build(args.n_test, "none", rs, degraded_frac=0.75,
                              pose_err_std=0.8, latency_frames=(1, 3))
    sweep_sets = {a: build(args.n_sweep, a, rs, n_attackers=2) for a in CORE}
    log(f"train {len(train)} seq / {sum(len(s) for s in train)} frames")

    # -------------------------------------------------- 2. labels + gates
    log("coalition labelling ...")
    Xs, u_marg, u_solo = [], [], []
    for seq in train:
        for ctx, X in seq:
            if ctx.n_msg == 0:
                continue
            um, _, _ = U.coalition_labels(ctx, n_coalitions=args.coalitions, rs=rs)
            Xs.append(X)
            u_marg.append(um)
            u_solo.append(U.solo_utility(ctx))
    Xtr = np.concatenate(Xs)
    u_marg, u_solo = np.concatenate(u_marg), np.concatenate(u_solo)
    log(f"{len(Xtr)} labelled messages")
    np.savez(os.path.join(OUT, "train_labels.npz"), X=Xtr, u_marg=u_marg,
             u_solo=u_solo, names=np.array(FT.NAMES))

    log("training gates ...")
    gate = GateModel(FT.DIM, seed=0).fit(Xtr, u_marg, u_marg < -U.DELTA)
    gate_solo = GateModel(FT.DIM, seed=0).fit(Xtr, u_solo, u_solo < -U.DELTA)
    tier_gates = {}
    for tname, drop in FT.TIERS.items():
        if tname == "all":
            tier_gates[tname] = gate
        else:
            tier_gates[tname] = GateModel(FT.DIM, seed=0).fit(
                FT.mask_features(Xtr, drop), u_marg, u_marg < -U.DELTA)

    # -------------------------------------------------- 3. CRC
    log("conformal risk control ...")
    lam_grid = np.concatenate([[0.0], np.linspace(0.02, 1.0, 50)])

    def crc_losses(data, model, cap=3.0, drop=None):
        """Per-frame loss = capped count of admitted objects that do not exist.

        Monotone non-decreasing in the permissiveness lambda by construction,
        which is what the CRC theorem requires of the per-instance loss.
        """
        rows = []
        for seq in data:
            for ctx, X in seq:
                if ctx.n_msg == 0:
                    continue
                Xi = FT.mask_features(X, drop) if drop else X
                _, ph, _ = model.predict(Xi)
                bad = np.array([(m["gt_id"] == -1) and in_roi(m["x"], m["y"])
                                for m in ctx.msgs])
                rows.append([min(1.0, float(((ph < lam) & bad).sum()) / cap)
                             for lam in lam_grid])
        return np.array(rows)

    L_cal = crc_losses(cal_benign, gate)
    frac_ok, frac_viol = check_monotone(L_cal)
    Rhat_cal = L_cal.mean(axis=0)
    log(f"per-instance monotone on {frac_ok:.1%} of calibration frames "
        f"(violating steps {frac_viol:.2%})")
    log(f"achievable loss range on calibration: "
        f"[{Rhat_cal.min():.3f}, {Rhat_cal.max():.3f}]  "
        f"(lambda=0 rejects everything)")

    L_test = {c: crc_losses(d, gate) for c, d in tests.items()}
    crc_rows = []
    for alpha in [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]:
        k, Rh, bound = crc_threshold(L_cal, alpha)
        lam = float(lam_grid[k]) if k >= 0 else 0.0
        row = dict(alpha=alpha, lam_hat=lam, cal_risk=float(Rh[k]) if k >= 0 else 0.0,
                   bound=bound)
        for c in tests:
            row[f"risk_{c}"] = float(L_test[c][:, k].mean())
            row[f"holds_{c}"] = bool(L_test[c][:, k].mean() <= alpha)
        # what does that lambda cost in benefit?
        pol = B.gate_policy(gate, lam, 0.8 * lam, 0.6 * lam, temporal_release=True)
        s = evaluate(sweep_sets["none"], pol)
        row.update(accept_rate=s["accept_rate"], benefit_rate=s["benefit_rate"],
                   RO_recall=s["RO_recall"], R_benign=s["R"])
        crc_rows.append(row)
    crc_df = pd.DataFrame(crc_rows)
    crc_df.to_csv(os.path.join(OUT, "crc_alpha_sweep.csv"), index=False)
    print(crc_df[["alpha", "lam_hat", "cal_risk", "risk_none", "risk_degraded",
                  "risk_spoof", "risk_collusion", "holds_spoof",
                  "holds_collusion", "accept_rate", "benefit_rate"]]
          .round(3).to_string(index=False))
    pd.DataFrame(dict(lam=lam_grid, cal_risk=Rhat_cal)).to_csv(
        os.path.join(OUT, "crc_curve.csv"), index=False)

    # operating point used below: largest alpha that still holds on benign iid
    k_op, _, _ = crc_threshold(L_cal, 0.30)
    lam_op = float(lam_grid[k_op]) if k_op >= 0 else 0.5
    log(f"operating lambda (alpha=0.30) = {lam_op:.3f}")

    # -------------------------------------------------- 4. policies
    log("evaluating policies ...")
    policies = {
        "ego_only": B.ego_only,
        "naive_lf": B.naive,
        "conf_0.5": B.conf_thresh(0.5),
        "conf_0.7": B.conf_thresh(0.7),
        "conf_0.85": B.conf_thresh(0.85),
        "geom_consensus": B.geom_consensus(1),
        "belt_like": B.belt_like,
        "cad_like": B.cad_like,
        "robosac_like": B.robosac_like(0.5),
        "mate_like": B.mate_like(0.45),
        "gate_binary": B.gate_accept_only(gate, 0.5),
        "ghostguard_crc": B.gate_policy(gate, lam_op, 0.8 * lam_op, 0.6 * lam_op,
                                        temporal_release=True),
        "gg_no_quarantine": B.gate_policy(gate, lam_op, 0.8 * lam_op, 0.6 * lam_op,
                                          temporal_release=False),
        "gg_label_solo": B.gate_policy(gate_solo, lam_op, 0.8 * lam_op,
                                       0.6 * lam_op, temporal_release=True),
        "oracle_loo": B.oracle_loo,
        "oracle_greedy": B.oracle_greedy,
    }
    rows = []
    for cond, data in tests.items():
        for pname, pol in policies.items():
            s = evaluate(data, pol)
            s.update(condition=cond, policy=pname)
            rows.append(s)
        log(f"  {cond} done")
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "policies.csv"), index=False)
    cols = ["R", "R_se", "misses", "ghosts", "AP", "RO_recall", "harm_rate",
            "malicious_accept", "benefit_rate", "accept_rate"]
    for cond in tests:
        print(f"\n=== {cond} ===")
        print(df[df.condition == cond].set_index("policy")[cols]
              .round(3).to_string())

    # -------------------------------------------------- 5. trade-off curves
    log("matched-operating-point sweep ...")
    trs = []
    for cond, data in sweep_sets.items():
        for tau in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
            s = evaluate(data, B.conf_thresh(tau))
            s.update(family="confidence", knob=tau, condition=cond)
            trs.append(s)
        for lam in [0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 0.95]:
            s = evaluate(data, B.gate_accept_only(gate, lam))
            s.update(family="gate_umarg", knob=lam, condition=cond)
            trs.append(s)
            s = evaluate(data, B.gate_accept_only(gate_solo, lam))
            s.update(family="gate_usolo", knob=lam, condition=cond)
            trs.append(s)
            s = evaluate(data, B.gate_policy(gate, lam, 0.8 * lam, 0.6 * lam,
                                             temporal_release=True))
            s.update(family="gate_4action", knob=lam, condition=cond)
            trs.append(s)
        for nm, pol in [("cad_like", B.cad_like),
                        ("robosac_like", B.robosac_like(0.5)),
                        ("mate_like", B.mate_like(0.45)),
                        ("geom_consensus", B.geom_consensus(1)),
                        ("oracle_greedy", B.oracle_greedy),
                        ("ego_only", B.ego_only), ("naive_lf", B.naive)]:
            s = evaluate(data, pol)
            s.update(family=nm, knob=np.nan, condition=cond)
            trs.append(s)
        log(f"  sweep {cond} done")
    tdf = pd.DataFrame(trs)
    tdf.to_csv(os.path.join(OUT, "tradeoff.csv"), index=False)

    print("\n=== benefit at matched harm (interpolated), per condition ===")
    for cond in CORE:
        print(f"\n  -- {cond}")
        sub = tdf[tdf.condition == cond]
        for target in [0.05, 0.10, 0.20, 0.40]:
            line = []
            for fam in ["confidence", "gate_umarg", "gate_usolo", "gate_4action"]:
                f = sub[sub.family == fam].sort_values("harm_rate")
                if f.empty:
                    continue
                b = np.interp(target, f.harm_rate.values, f.benefit_rate.values)
                r = np.interp(target, f.harm_rate.values, f.R.values)
                line.append(f"{fam}: benefit={b:.3f} R={r:.2f}")
            print(f"    harm={target:.2f}  " + " | ".join(line))

    # -------------------------------------------------- 6. feature tiers
    log("feature-trust tiers ...")
    frows = []
    for tname, drop in FT.TIERS.items():
        g = tier_gates[tname]
        for cond in CORE:
            s = evaluate(sweep_sets[cond],
                         B.gate_accept_only(g, 0.5, drop=drop))
            s.update(tier=tname, condition=cond, n_dropped=len(drop))
            frows.append(s)
    fdf = pd.DataFrame(frows)
    fdf.to_csv(os.path.join(OUT, "feature_tiers.csv"), index=False)
    print("\n=== gate at tau=0.5 under feature-trust tiers ===")
    print(fdf.pivot(index="tier", columns="condition",
                    values=["R", "benefit_rate", "malicious_accept"])
          .round(3).to_string())

    # -------------------------------------------------- 7. risk weights
    log("risk-weight sensitivity ...")
    variants = {"default": RISK_W,
                "ghost_heavy": dict(miss=1.0, ghost=3.0, loc=0.2, dup=0.3),
                "miss_heavy": dict(miss=3.0, ghost=1.0, loc=0.2, dup=0.3),
                "no_dup_no_loc": dict(miss=1.0, ghost=1.0, loc=0.0, dup=0.0)}
    srows = []
    for vname, w in variants.items():
        d = build(60, "spoof", np.random.default_rng(99), risk_w=w, n_attackers=2)
        for pname in ["ego_only", "naive_lf", "conf_0.7", "cad_like",
                      "ghostguard_crc", "oracle_greedy"]:
            s = evaluate(d, policies[pname])
            srows.append(dict(weights=vname, policy=pname, R=s["R"],
                              AP=s["AP"], RO_recall=s["RO_recall"],
                              harm_rate=s["harm_rate"]))
    sdf = pd.DataFrame(srows)
    sdf.to_csv(os.path.join(OUT, "risk_weight_sensitivity.csv"), index=False)
    piv = sdf.pivot(index="policy", columns="weights", values="R")
    print("\nmean R by risk weighting:")
    print(piv.round(2).to_string())
    print("\nrank under each weighting (1 = lowest risk):")
    print(piv.rank().astype(int).to_string())

    log(f"done -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
