"""Synthetic cooperative-perception sandbox.

Scope claim, stated up front: this is NOT a substitute for OPV2V/V2V4Real. It
is a controlled environment where the *ground-truth causal structure is known*
-- we know which object each message refers to, whether the ego could ever have
seen it, and whether the sender fabricated it. That is what makes it possible
to audit whether the GhostGuard decision rule is well-posed. Absolute numbers
here mean nothing; the sign and the ordering of effects mean something.

Scene layout: ego at origin heading +x along a straight 4-lane road.
Other CAVs are placed along the road. Objects (cars + pedestrians) are placed
in lanes and on the shoulder, and move with roughly constant velocity.

Visibility uses a real occlusion test: an object is hidden from an agent if
another object's footprint blocks the line of sight. This is what generates
"remote-only" objects -- the ones cooperative perception exists for.
"""
import numpy as np

CAR, PED = 0, 1
CLASS_NAMES = {CAR: "car", PED: "ped"}
CLASS_DIMS = {CAR: (4.4, 1.9), PED: (0.8, 0.8)}

# ---------------------------------------------------------------- config


class SimConfig:
    def __init__(self, **kw):
        self.n_frames = 10
        self.dt = 0.1
        self.n_cav = 3               # cooperating senders besides the ego
        self.n_obj = (6, 12)
        self.ped_frac = 0.35
        self.road_len = 100.0
        self.lane_y = (-5.25, -1.75, 1.75, 5.25)
        self.max_range = 60.0
        self.fp_rate = 0.8           # expected false positives per agent-frame
        self.pose_err_std = 0.35     # benign sender pose error (m)
        self.pose_yaw_std = 0.015    # rad
        self.latency_frames = (0, 2)
        self.degraded_frac = 0.25    # fraction of senders with degraded sensing
        # attacks
        self.attack = "none"         # none | spoof | removal | collusion
                                     #   | spoof_adaptive | collusion_adaptive
        self.n_attackers = 1
        self.spoof_rate = 2.0        # fabricated boxes per attacker-frame
        self.spoof_conf = (0.75, 0.97)
        self.spoof_in_corridor = 0.6
        for k, v in kw.items():
            if not hasattr(self, k):
                raise KeyError(k)
            setattr(self, k, v)


# ---------------------------------------------------------------- helpers


def _occluded(agent_xy, obj, others):
    """True if the segment agent->obj centre passes through another footprint."""
    ax, ay = agent_xy
    ox, oy = obj["x"], obj["y"]
    d = np.hypot(ox - ax, oy - ay)
    if d < 1e-6:
        return False
    ux, uy = (ox - ax) / d, (oy - ay) / d
    for o in others:
        if o is obj:
            continue
        # project blocker centre onto the ray
        t = (o["x"] - ax) * ux + (o["y"] - ay) * uy
        if t <= 0.5 or t >= d - 0.5:
            continue
        perp = abs(-(o["x"] - ax) * uy + (o["y"] - ay) * ux)
        halfw = 0.5 * max(o["l"], o["w"])
        if perp < halfw * 0.9:
            return True
    return False


def _det_prob(cls, rng_m, degraded):
    base = 0.95 if cls == CAR else 0.82
    fall = np.exp(-max(0.0, rng_m - 15.0) / (45.0 if cls == CAR else 25.0))
    p = base * (0.45 + 0.55 * fall)
    if degraded:
        p *= 0.6
    return float(np.clip(p, 0.02, 0.99))


def _loc_std(rng_m, degraded):
    s = 0.10 + 0.011 * rng_m
    return s * (2.0 if degraded else 1.0)


# ---------------------------------------------------------------- generator


def make_sequence(cfg, rs):
    """Return dict with agents, per-frame ground truth, and per-frame messages."""
    n_obj = rs.integers(cfg.n_obj[0], cfg.n_obj[1] + 1)
    objs = []
    for i in range(n_obj):
        is_ped = rs.random() < cfg.ped_frac
        cls = PED if is_ped else CAR
        l, w = CLASS_DIMS[cls]
        if is_ped:
            y = rs.uniform(-9.0, 9.0)
            vx = rs.normal(0.0, 0.4)
            vy = rs.normal(0.0, 0.6)
        else:
            y = cfg.lane_y[rs.integers(0, 4)] + rs.normal(0, 0.25)
            vx = rs.uniform(4.0, 16.0) * (1 if y > 0 else -1)
            vy = rs.normal(0.0, 0.05)
        objs.append(dict(id=i, cls=cls, x=rs.uniform(2.0, cfg.road_len),
                         y=y, vx=vx, vy=vy,
                         l=l * rs.uniform(0.9, 1.1), w=w * rs.uniform(0.9, 1.1),
                         yaw=(0.0 if vx >= 0 else np.pi) + rs.normal(0, 0.03)))

    # senders: ego (id 0) plus CAVs strung along the road
    agents = [dict(id=0, x=0.0, y=0.0, ego=True, degraded=False, lag=0,
                   pose_dx=0.0, pose_dy=0.0, pose_dyaw=0.0, attacker=False,
                   history=1.0)]
    for a in range(1, cfg.n_cav + 1):
        degraded = rs.random() < cfg.degraded_frac
        agents.append(dict(
            id=a,
            x=rs.uniform(15.0, cfg.road_len), y=cfg.lane_y[rs.integers(0, 4)],
            ego=False, degraded=degraded,
            lag=int(rs.integers(cfg.latency_frames[0], cfg.latency_frames[1] + 1)),
            pose_dx=rs.normal(0, cfg.pose_err_std),
            pose_dy=rs.normal(0, cfg.pose_err_std),
            pose_dyaw=rs.normal(0, cfg.pose_yaw_std),
            attacker=False,
            history=float(np.clip(rs.normal(0.85, 0.1), 0.2, 1.0)),
        ))

    attackers = []
    if cfg.attack != "none":
        cand = [a for a in agents if not a["ego"]]
        k = min(cfg.n_attackers, len(cand))
        idx = rs.choice(len(cand), size=k, replace=False)
        for i in np.atleast_1d(idx):
            cand[int(i)]["attacker"] = True
            # an attacker with a clean provenance record: history is not a defence
            cand[int(i)]["history"] = float(np.clip(rs.normal(0.93, 0.05), 0.5, 1.0))
            attackers.append(cand[int(i)])

    frames = []
    for f in range(cfg.n_frames):
        t = f * cfg.dt
        gt = []
        for o in objs:
            g = dict(o)
            g["x"] = o["x"] + o["vx"] * t
            g["y"] = o["y"] + o["vy"] * t
            if 0.0 < g["x"] < cfg.road_len + 10 and abs(g["y"]) < 12:
                gt.append(g)
        # which GT objects the ego can see at all (defines "remote-only")
        ego_vis = set()
        for g in gt:
            r = np.hypot(g["x"], g["y"])
            if r <= cfg.max_range and not _occluded((0.0, 0.0), g, gt):
                ego_vis.add(g["id"])

        msgs, ego_dets = [], []
        for a in agents:
            lag_t = max(0.0, t - a["lag"] * cfg.dt)
            for g in gt:
                r = np.hypot(g["x"] - a["x"], g["y"] - a["y"])
                if r > cfg.max_range:
                    continue
                if _occluded((a["x"], a["y"]), g, gt):
                    continue
                if rs.random() > _det_prob(g["cls"], r, a["degraded"]):
                    continue
                if a["attacker"] and cfg.attack == "removal" and g["id"] not in ego_vis:
                    continue  # withhold exactly the objects only it can see
                s = _loc_std(r, a["degraded"])
                # stale message: report where the object was `lag` frames ago
                bx = g["x"] - g["vx"] * (t - lag_t) + rs.normal(0, s) + a["pose_dx"]
                by = g["y"] - g["vy"] * (t - lag_t) + rs.normal(0, s) + a["pose_dy"]
                q = np.exp(-r / 55.0) * (0.6 if a["degraded"] else 1.0)
                conf = float(np.clip(rs.beta(2 + 6 * q, 2.2), 0.05, 0.999))
                det = dict(sender=a["id"], cls=g["cls"], x=bx, y=by,
                           l=g["l"] * rs.uniform(0.93, 1.07),
                           w=g["w"] * rs.uniform(0.93, 1.07),
                           yaw=g["yaw"] + a["pose_dyaw"] + rs.normal(0, 0.05),
                           conf=conf, gt_id=g["id"], fabricated=False,
                           age=a["lag"] * cfg.dt, claimed_cov=s ** 2,
                           range_sender=r, history=a["history"],
                           attacker=a["attacker"])
                (ego_dets if a["ego"] else msgs).append(det)

            # honest false positives (clutter / mis-classification)
            n_fp = rs.poisson(cfg.fp_rate * (1.6 if a["degraded"] else 1.0))
            for _ in range(int(n_fp)):
                cls = PED if rs.random() < 0.5 else CAR
                l, w = CLASS_DIMS[cls]
                # place clutter in the sender's own sensing footprint
                rr = cfg.max_range * np.sqrt(rs.random())
                th = rs.uniform(-np.pi, np.pi)
                fx = a["x"] + rr * np.cos(th)
                fy = float(np.clip(a["y"] + rr * np.sin(th), -11.0, 11.0))
                # clutter confidence overlaps the true-positive range on purpose
                conf = float(np.clip(rs.beta(2.0, 4.0), 0.05, 0.999))
                det = dict(sender=a["id"], cls=cls, x=fx, y=fy, l=l, w=w,
                           yaw=rs.uniform(-np.pi, np.pi), conf=conf, gt_id=-1,
                           fabricated=False, age=a["lag"] * cfg.dt,
                           claimed_cov=_loc_std(np.hypot(fx - a["x"], fy - a["y"]),
                                                a["degraded"]) ** 2,
                           range_sender=np.hypot(fx - a["x"], fy - a["y"]),
                           history=a["history"], attacker=a["attacker"])
                (ego_dets if a["ego"] else msgs).append(det)

        # fabricated messages
        if cfg.attack in ("spoof", "collusion", "spoof_adaptive",
                          "collusion_adaptive") and attackers:
            n_spoof = int(rs.poisson(cfg.spoof_rate))
            shared = []
            for _ in range(n_spoof):
                in_corr = rs.random() < cfg.spoof_in_corridor
                cls = CAR if rs.random() < 0.6 else PED
                l, w = CLASS_DIMS[cls]
                if in_corr:
                    sx = rs.uniform(8.0, 45.0)
                    sy = rs.normal(0.0, 0.8)
                else:
                    sx = rs.uniform(5.0, cfg.road_len)
                    sy = rs.uniform(-9, 9)
                if cfg.attack.endswith("adaptive"):
                    # An attacker that has read this paper: instead of shouting
                    # (high confidence, implausibly tight covariance, zero age)
                    # it samples its metadata from the benign true-positive
                    # distribution for the range it is claiming. Nothing about
                    # the message is then statistically distinguishable except
                    # its geometry.
                    conf = float(np.clip(rs.beta(2 + 6 * np.exp(-30.0 / 55.0),
                                                 2.2), 0.05, 0.999))
                else:
                    conf = float(rs.uniform(*cfg.spoof_conf))
                shared.append(dict(cls=cls, x=sx, y=sy, l=l, w=w,
                                   yaw=0.0 + rs.normal(0, 0.05), conf=conf))
            for atk in attackers:
                for sp in shared:
                    # collusion: every attacker reports the *same* fabricated box,
                    # so cross-agent agreement is manufactured, not evidence.
                    jitter = 0.15 if cfg.attack.startswith("collusion") else 0.0
                    msgs.append(dict(
                        sender=atk["id"], cls=sp["cls"],
                        x=sp["x"] + rs.normal(0, jitter),
                        y=sp["y"] + rs.normal(0, jitter),
                        l=sp["l"], w=sp["w"], yaw=sp["yaw"],
                        conf=sp["conf"], gt_id=-1, fabricated=True,
                        age=(float(rs.integers(0, 3)) * cfg.dt
                             if cfg.attack.endswith("adaptive") else 0.0),
                        claimed_cov=(_loc_std(np.hypot(sp["x"] - atk["x"],
                                                       sp["y"] - atk["y"]),
                                              atk["degraded"]) ** 2
                                     if cfg.attack.endswith("adaptive") else 0.02),
                        range_sender=np.hypot(sp["x"] - atk["x"], sp["y"] - atk["y"]),
                        history=atk["history"], attacker=True))
                if cfg.attack in ("spoof", "spoof_adaptive"):
                    break  # single-source fabrication

        frames.append(dict(t=t, gt=gt, ego_vis=ego_vis, ego=ego_dets, msgs=msgs))

    return dict(agents=agents, frames=frames, cfg=cfg)


def box_of(d):
    return np.array([d["x"], d["y"], d["l"], d["w"], d["yaw"]], dtype=float)
