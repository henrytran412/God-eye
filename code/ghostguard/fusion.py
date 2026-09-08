"""Late fusion F(S) and the safety-weighted perception risk R(F(S), y).

Design note on cost. The counterfactual label U(m|S) = R(F(S)) - R(F(S u {m}))
needs thousands of fusion re-runs per frame. To make that tractable we build a
FrameCtx once per frame that precomputes candidate-to-GT and candidate-to-
candidate centre-distance matrices (and rotated BEV IoU, used by the AP metric).
Fusion then reduces to greedy NMS over a boolean mask, and a cluster inherits
the row of its highest-scoring member -- exactly the box NMS would emit.
Localisation error uses the confidence-weighted mean centre of the cluster, so
soft-fused poses are still measured.

Matching convention. Association uses class-dependent centre distance
(nuScenes convention: a 2 m gate for vehicles, 1 m for pedestrians) rather than
a fixed IoU gate. With an 0.8 m pedestrian footprint an IoU-0.3 gate is
unreachable under realistic localisation noise, which would make every
correctly detected pedestrian count as a miss AND a ghost at the same time and
corrupt the risk function. Rotated IoU is still used for the reported AP.
"""
import numpy as np

from .geometry import iou_matrix
from .sim import CAR, PED, box_of

# risk weights -- exposed so sensitivity to them can be measured
RISK_W = dict(miss=1.0, ghost=1.0, loc=0.20, dup=0.30)
MATCH_DIST = {CAR: 2.0, PED: 1.0}      # association gate, metres
CLUSTER_DIST = {CAR: 2.5, PED: 1.2}    # cross-agent duplicate collapse
IOU_AP = {CAR: 0.5, PED: 0.3}          # only for the reported IoU-based AP
TAU_OP = 0.30                          # operating threshold on fused score
CORRIDOR_HALF_W = 2.5
CORRIDOR_LEN = 50.0
# evaluation region of interest around the ego, ego frame (metres).
# Detections outside it are not scored at all -- the same convention OPV2V
# uses. Without this, clutter a sender reports 90 m down the road would be
# charged to the ego as a ghost.
ROI_X = (-20.0, 100.0)
ROI_Y = 12.0


def in_roi(x, y):
    return (ROI_X[0] <= x <= ROI_X[1]) and (abs(y) <= ROI_Y)


def severity(x, y, cls):
    """Safety weight of an object at (x, y). Higher = worse to get wrong."""
    s = 2.0 if cls == PED else 1.0
    if abs(y) < CORRIDOR_HALF_W and 0.0 < x < CORRIDOR_LEN:
        s *= 1.8
    d = float(np.hypot(x, y))
    s *= float(np.clip(2.0 - d / 50.0, 1.0, 2.0))
    return s


def _dist_matrix(xy_a, xy_b):
    if len(xy_a) == 0 or len(xy_b) == 0:
        return np.zeros((len(xy_a), len(xy_b)))
    d = xy_a[:, None, :] - xy_b[None, :, :]
    return np.sqrt((d ** 2).sum(axis=2))


class FrameCtx:
    """Precomputed geometry for one frame."""

    def __init__(self, frame, risk_w=None, want_iou=False):
        self.risk_w = dict(RISK_W if risk_w is None else risk_w)
        self.gt = frame["gt"]
        self.ego_vis = frame["ego_vis"]
        self.gt_cls = np.array([g["cls"] for g in self.gt], dtype=int)
        self.gt_xy = np.array([[g["x"], g["y"]] for g in self.gt],
                              dtype=float).reshape(-1, 2)
        self.gt_sev = np.array([severity(g["x"], g["y"], g["cls"]) for g in self.gt])
        self.gt_ids = np.array([g["id"] for g in self.gt], dtype=int)
        self.gt_remote_only = np.array(
            [g["id"] not in self.ego_vis for g in self.gt], dtype=bool)

        self.ego = frame["ego"]
        self.msgs = frame["msgs"]
        self.n_ego = len(self.ego)
        self.n_msg = len(self.msgs)
        cands = self.ego + self.msgs
        self.cands = cands
        self.cls = np.array([c["cls"] for c in cands], dtype=int)
        self.conf = np.array([c["conf"] for c in cands], dtype=float)
        self.xy = np.array([[c["x"], c["y"]] for c in cands],
                           dtype=float).reshape(-1, 2)
        self.is_fab = np.array([c["fabricated"] for c in cands], dtype=bool)
        self.gt_of = np.array([c["gt_id"] for c in cands], dtype=int)

        self.d_gt = _dist_matrix(self.xy, self.gt_xy)
        self.d_cc = _dist_matrix(self.xy, self.xy)
        if len(cands):
            same = self.cls[:, None] == self.cls[None, :]
            # cluster (and match) only within a class
            self.d_cc = np.where(same, self.d_cc, np.inf)
            self.cluster_gate = np.array([CLUSTER_DIST[int(c)] for c in self.cls])
        else:
            self.cluster_gate = np.zeros(0)
        if len(cands) and len(self.gt):
            ok = self.cls[:, None] == self.gt_cls[None, :]
            self.d_gt = np.where(ok, self.d_gt, np.inf)

        self.boxes = [box_of(c) for c in cands]
        self.gt_boxes = [box_of(g) for g in self.gt]
        self.iou_gt = (iou_matrix(self.boxes, self.gt_boxes)
                       if want_iou and cands and self.gt else None)

    # ------------------------------------------------------------ fusion

    def fuse(self, weights, score_mode="max"):
        """weights: length n_msg in [0,1]; 0 = rejected. Ego always included."""
        w = np.ones(self.n_ego + self.n_msg)
        if self.n_msg:
            w[self.n_ego:] = weights
        active = np.nonzero(w > 0)[0]
        if active.size == 0:
            return dict(rep=np.zeros(0, dtype=int), score=np.zeros(0),
                        xy=np.zeros((0, 2)), cls=np.zeros(0, dtype=int),
                        n_members=np.zeros(0, dtype=int), members=[])
        sc = self.conf[active] * w[active]
        order = active[np.argsort(-sc)]
        taken = np.zeros(len(self.cls), dtype=bool)
        reps, scores, centres, clses, nmem, members = [], [], [], [], [], []
        for i in order:
            if taken[i]:
                continue
            gate = self.cluster_gate[i]
            grp = [int(j) for j in order if not taken[j] and self.d_cc[i, j] <= gate]
            if i not in grp:
                grp.append(int(i))
            for j in grp:
                taken[j] = True
            gs = self.conf[grp] * w[grp]
            if score_mode == "max":
                s = float(gs.max())
            elif score_mode == "or":
                s = float(1.0 - np.prod(1.0 - np.clip(gs, 0, 0.999)))
            elif score_mode == "mean":
                s = float(gs.mean())
            else:
                raise ValueError(score_mode)
            ws = gs / max(gs.sum(), 1e-9)
            reps.append(int(i))
            scores.append(s)
            centres.append((self.xy[grp] * ws[:, None]).sum(axis=0))
            clses.append(int(self.cls[i]))
            nmem.append(len(grp))
            members.append(grp)
        return dict(rep=np.array(reps, dtype=int), score=np.array(scores),
                    xy=np.array(centres).reshape(-1, 2),
                    cls=np.array(clses, dtype=int),
                    n_members=np.array(nmem, dtype=int), members=members)

    # ------------------------------------------------------------ risk

    def match(self, F, tau_op=TAU_OP):
        """Greedy one-to-one association of kept clusters to GT by centre distance.

        Matching uses the *fused* centre, so pose refinement is credited.
        Returns (gt_match, cl_match, n_dup).
        """
        keep = np.nonzero(F["score"] >= tau_op)[0]
        ng = len(self.gt)
        gt_match = -np.ones(ng, dtype=int)
        cl_match = -np.ones(len(F["score"]), dtype=int)
        if keep.size == 0 or ng == 0:
            return gt_match, cl_match, 0
        D = _dist_matrix(F["xy"][keep], self.gt_xy)
        ok = F["cls"][keep][:, None] == self.gt_cls[None, :]
        gate = np.array([MATCH_DIST[int(c)] for c in F["cls"][keep]])[:, None]
        D = np.where(ok & (D <= gate), D, np.inf)
        pairs = np.argwhere(np.isfinite(D))
        pairs = pairs[np.argsort(D[pairs[:, 0], pairs[:, 1]])]
        used_c, used_g = set(), set()
        for ci, gj in pairs:
            ci, gj = int(ci), int(gj)
            if ci in used_c or gj in used_g:
                continue
            used_c.add(ci)
            used_g.add(gj)
            gt_match[gj] = int(keep[ci])
            cl_match[keep[ci]] = gj
        n_dup = 0
        for ci in range(len(keep)):
            if ci in used_c:
                continue
            if np.isfinite(D[ci]).any():   # in gate of a GT another cluster claimed
                n_dup += 1
        self._n_kept_roi = int(sum(
            1 for k in keep if in_roi(float(F["xy"][k][0]), float(F["xy"][k][1]))))
        return gt_match, cl_match, n_dup

    def risk(self, F, tau_op=TAU_OP, breakdown=False):
        gt_match, cl_match, n_dup = self.match(F, tau_op)
        w = self.risk_w
        miss = float(((gt_match < 0) * self.gt_sev).sum())
        keep = F["score"] >= tau_op
        ghost = 0.0
        n_ghost = 0
        for k in np.nonzero(keep)[0]:
            if cl_match[k] < 0 and in_roi(float(F["xy"][k][0]), float(F["xy"][k][1])):
                x, y = F["xy"][k]
                ghost += severity(float(x), float(y), int(F["cls"][k]))
                n_ghost += 1
        # a duplicate was already counted as a ghost; the dup term is the extra
        # charge for tracker instability it causes on top of that
        loc = 0.0
        for j, k in enumerate(gt_match):
            if k >= 0:
                e = float(np.hypot(*(F["xy"][k] - self.gt_xy[j])))
                loc += min(e, 3.0) / 3.0 * self.gt_sev[j]
        dup = n_dup * (float(self.gt_sev.mean()) if len(self.gt) else 1.0)
        total = w["miss"] * miss + w["ghost"] * ghost + w["loc"] * loc + w["dup"] * dup
        if breakdown:
            return total, dict(miss=miss, ghost=ghost, loc=loc, dup=dup,
                               n_dup=n_dup, n_miss=int((gt_match < 0).sum()),
                               n_ghost=n_ghost,
                               ro_hit=int(((gt_match >= 0) & self.gt_remote_only).sum()),
                               ro_total=int(self.gt_remote_only.sum()))
        return total

    def risk_of(self, weights, score_mode="max", tau_op=TAU_OP, breakdown=False):
        return self.risk(self.fuse(weights, score_mode), tau_op, breakdown)
