"""Collect Car/Ped/Cyc AP rows from the teacher run logs into one table."""
import re, sys, glob, os
T = sys.argv[1]
def block(t, cls, thr):
    m = re.findall(re.escape(cls) + r" AP@" + re.escape(thr) + r":\n(.*?)\n(?:aos|[A-Z])", t, re.S)
    if not m: return None
    d = {k.strip(): [float(x) for x in v.split(",")] for k, v in (l.split(" AP:") for l in m[-1].strip().split("\n") if " AP:" in l)}
    return d
names = ["baseline", "oracle_m90", "oracle_0", "oracleB_fix", "oracleB_fit2d", "yolo_teacher", "yolo_refine", "yolo_union", "yolo_both", "yolo2_teacher", "yolo2_refine", "yolo2_union", "yolo2_both", "yolo3_src_roads", "yolo3_tgtH_roads", "yolo3_tgtH_noroad", "yolo4_src", "yolo4_src_truck", "yolo5_mono"]
print(f"{'run':<14}{'Car3d@.5':>9}{'CarBEV@.5':>10}{'Car3d@.25':>10}{'CarBEV@.25':>11}{'Ped3d':>7}{'Cyc3d':>7}{'CD-AP':>7}")
for n in names:
    p = os.path.join(T, n + ".eval.log")
    if not os.path.exists(p): continue
    t = open(p, errors="ignore").read().replace("\r", "\n")
    c5, c25 = block(t, "Car", "0.70, 0.50, 0.50"), block(t, "Car", "0.50, 0.25, 0.25")
    pd, cy = block(t, "Pedestrian", "0.50, 0.25, 0.25"), block(t, "Cyclist", "0.50, 0.25, 0.25")
    cd = re.findall(r"mean CD-AP\s+([\d.]+)", open(os.path.join(T, n + ".cd.log"), errors="ignore").read()) if os.path.exists(os.path.join(T, n + ".cd.log")) else []
    f = lambda d, k: f"{d[k][1]:.2f}" if d and k in d else "-"
    print(f"{n:<14}{f(c5,'3d'):>9}{f(c5,'bev'):>10}{f(c25,'3d'):>10}{f(c25,'bev'):>11}{f(pd,'3d'):>7}{f(cy,'3d'):>7}{(cd[-1] if cd else '-'):>7}")
