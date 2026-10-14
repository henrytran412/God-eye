"""Evaluation: safety risk, AP, remote-only recall, benefit/harm rates.

Benefit and Harm are defined on the messages, not on the fused output, because
the proposal's claim is about admission decisions:

  Harm Rate    = share of admitted messages that assert an object that is not
                 there (fabricated or honest clutter) inside the scored region.
  Benefit Rate = share of admitted messages that carry a real object the ego
                 cannot see at all -- the reason cooperative perception exists.

Reporting only one of the two is how a defence can look good while quietly
throwing away the occlusion benefit, so both are always reported together.
"""
import numpy as np

from .fusion import MATCH_DIST, TAU_OP, in_roi, _dist_matrix


def ap_pairs(ctx, F):
    """Score-ranked matching for AP. Returns (scores, tp_flags, n_gt)."""
    ng = len(ctx.gt)
    nc = len(F["score"])
    if nc == 0:
        return np.zeros(0), np.zeros(0), ng
    keep = [k for k in range(nc)
            if in_roi(float(F["xy"][k][0]), float(F["xy"][k][1]))]
    if not keep:
        return np.zeros(0), np.zeros(0), ng
    keep = np.array(keep)
    order = keep[np.argsort(-F["score"][keep])]
    used = np.zeros(ng, dtype=bool)
    scores, tps = [], []
    D = _dist_matrix(F["xy"][order], ctx.gt_xy) if ng else np.zeros((len(order), 0))
    for row, k in enumerate(order):
        tp = 0
        if ng:
            gate = MATCH_DIST[int(F["cls"][k])]
            d = np.where((ctx.gt_cls == F["cls"][k]) & ~used, D[row], np.inf)
            j = int(np.argmin(d))
            if np.isfinite(d[j]) and d[j] <= gate:
                used[j] = True
                tp = 1
        scores.append(float(F["score"][k]))
        tps.append(tp)
    return np.array(scores), np.array(tps), ng


def average_precision(scores, tps, n_gt):
    if n_gt == 0 or len(scores) == 0:
        return float("nan")
    o = np.argsort(-scores)
    tp = np.cumsum(tps[o])
    fp = np.cumsum(1 - tps[o])
    rec = tp / n_gt
    prec = tp / np.maximum(tp + fp, 1e-9)
    # 101-point interpolated AP
    ap = 0.0
    for t in np.linspace(0, 1, 101):
        p = prec[rec >= t]
        ap += (p.max() if p.size else 0.0)
    return float(ap / 101)


class Accum:
    def __init__(self):
        self.R = []
        self.n_miss = []
        self.n_ghost = []
        self.n_dup = []
        self.ro_hit = 0
        self.ro_tot = 0
        self.scores = []
        self.tps = []
        self.n_gt = 0
        self.acc_fab = [0, 0]      # accepted, total
        self.acc_clutter = [0, 0]
        self.acc_ro_true = [0, 0]
        self.acc_all = [0, 0]
        self.quarantined = 0
        self.soft = 0

    def add(self, ctx, w, score_mode="max"):
        F = ctx.fuse(w, score_mode)
        r, b = ctx.risk(F, breakdown=True)
        self.R.append(r)
        self.n_miss.append(b["n_miss"])
        self.n_ghost.append(b["n_ghost"])
        self.n_dup.append(b["n_dup"])
        self.ro_hit += b["ro_hit"]
        self.ro_tot += b["ro_total"]
        s, t, ng = ap_pairs(ctx, F)
        self.scores.append(s)
        self.tps.append(t)
        self.n_gt += ng
        for i, m in enumerate(ctx.msgs):
            adm = w[i] > 0
            self.acc_all[1] += 1
            self.acc_all[0] += int(adm)
            if 0 < w[i] < 1:
                self.soft += 1
            inside = in_roi(m["x"], m["y"])
            if m["fabricated"] and inside:
                self.acc_fab[1] += 1
                self.acc_fab[0] += int(adm)
            elif m["gt_id"] == -1 and inside:
                self.acc_clutter[1] += 1
                self.acc_clutter[0] += int(adm)
            elif m["gt_id"] >= 0 and m["gt_id"] not in ctx.ego_vis:
                self.acc_ro_true[1] += 1
                self.acc_ro_true[0] += int(adm)

    def summary(self):
        sc = np.concatenate(self.scores) if self.scores else np.zeros(0)
        tp = np.concatenate(self.tps) if self.tps else np.zeros(0)
        rate = lambda p: (p[0] / p[1]) if p[1] else float("nan")
        ghost_msgs = [self.acc_fab[0] + self.acc_clutter[0],
                      self.acc_fab[1] + self.acc_clutter[1]]
        return dict(
            R=float(np.mean(self.R)),
            R_se=float(np.std(self.R) / max(np.sqrt(len(self.R)), 1)),
            misses=float(np.mean(self.n_miss)),
            ghosts=float(np.mean(self.n_ghost)),
            dups=float(np.mean(self.n_dup)),
            AP=average_precision(sc, tp, self.n_gt),
            RO_recall=self.ro_hit / max(self.ro_tot, 1),
            harm_rate=rate(ghost_msgs),
            malicious_accept=rate(self.acc_fab),
            benefit_rate=rate(self.acc_ro_true),
            accept_rate=rate(self.acc_all),
            soft_frac=self.soft / max(self.acc_all[1], 1),
            quarantine_frac=self.quarantined / max(self.acc_all[1], 1),
        )
