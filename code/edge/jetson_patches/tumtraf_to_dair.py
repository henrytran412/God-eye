"""Convert TUMTraf Intersection (R2, OpenLABEL) into DAIR-V2X-I's original layout.

Targeting DAIR's layout rather than KITTI directly means the already-verified
dair2kitti.py and gen_info_dair.py run unchanged, so the cross-dataset evaluation
goes through exactly the same code path as the in-domain baseline. That is the
point: any difference in the result should come from the data, not the pipeline.

Three alignment decisions, each measured rather than assumed:

1. CAMERA. south1's optical axis in the LiDAR frame is [0.872, -0.090, -0.482];
   DAIR's is [0.974, -0.042, -0.202]. Both are dominantly +x. south2 points 37 deg
   off-axis, so south1 is the analogue of DAIR's single infrastructure camera.

2. TRANSFORM DIRECTION. coordinate_systems[cam].pose_wrt_parent.matrix4x4 is
   LiDAR->camera as-is: applied directly, 14/15 sample objects land in front of the
   camera and 7/15 project inside the image; inverted, 0/15 project inside.

3. GROUND ALIGNMENT. The Ouster sits 7.48 m above s110_base, so object centres sit
   at z ~ -6.45 in the sensor frame while DAIR's sit at ~ -1.22 and the model's
   point_cloud_range only admits [-5, 3]. Unshifted, 5.6% of objects are in range;
   shifted, 92.2%. The result is insensitive to the exact value (+5.0/+5.23/+5.5 all
   give 92.2%), so this aligns a frame convention rather than tuning a number. It is
   NOT a domain-gap eraser: appearance, sensor, geometry and fleet differences all
   survive it.

4. CAMERA SCOPING. TUMTraf labels the full 360 deg LiDAR scene; DAIR labels only
   what its single camera sees. Measured over the same frames: 0 of 14099 DAIR
   objects fail to project into the image, against 56.8% of TUMTraf Cars, 67.7% of
   Vans and 26.8% of Pedestrians. Keeping those would score the model against
   objects its camera physically cannot see, and the damage would fall hardest on
   whichever classes happen to sit off-axis -- which is exactly the artefact first
   observed (Cyclist 0% invisible scored 39.3 AP, Car 56.8% invisible scored 0.12).
   Objects that do not project into the image are therefore dropped, matching DAIR's
   convention. --keep-invisible restores the old behaviour for comparison.

Shifting the cloud changes the extrinsic: with p_new = p_old + [0,0,dz],
T_cam<-new = T_cam<-old @ Translate(0,0,-dz), so R is unchanged and
t_new = t_old - dz * R[:, 2].
"""
import argparse
import json
import pathlib
import shutil

import numpy as np

Z_SHIFT = 5.23          # metres, LiDAR frame -> DAIR-like ground-referenced height
CAM = "s110_camera_basler_south1_8mm"
LID = "s110_lidar_ouster_south"

# TUMTraf -> DAIR vocabulary. DAIR has no TRAILER or EMERGENCY_VEHICLE; TUMTraf has
# no Trafficcone or Barrowlist. Recorded explicitly because class-name alignment is
# part of the domain gap, not a detail to bury.
CLASS_MAP = {
    "CAR": "Car", "VAN": "Van", "TRUCK": "Truck", "TRAILER": "Truck",
    "BUS": "Bus", "PEDESTRIAN": "Pedestrian", "BICYCLE": "Cyclist",
    "MOTORCYCLE": "Motorcyclist", "EMERGENCY_VEHICLE": "Car",
}
OCC_MAP = {"NOT_OCCLUDED": "0", "PARTIALLY_OCCLUDED": "1", "MOSTLY_OCCLUDED": "2"}


def quat_to_yaw(qx, qy, qz, qw):
    return float(np.arctan2(2.0 * (qw * qz + qx * qy),
                            1.0 - 2.0 * (qy * qy + qz * qz)))


def corners_3d(x, y, z, l, w, h, yaw):
    """8 corners of a yaw-rotated box, in the same frame as the centre."""
    xc = np.array([1, 1, -1, -1, 1, 1, -1, -1]) * l / 2
    yc = np.array([1, -1, -1, 1, 1, -1, -1, 1]) * w / 2
    zc = np.array([1, 1, 1, 1, -1, -1, -1, -1]) * h / 2
    c, s = np.cos(yaw), np.sin(yaw)
    return np.stack([c * xc - s * yc + x, s * xc + c * yc + y, zc + z], axis=1)


def read_tumtraf_pcd(path):
    """TUMTraf ships ASCII PCDs with 9 fields; we need x y z intensity."""
    fields, n_hdr = None, 0
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            n_hdr += 1
            if line.startswith("FIELDS"):
                fields = line.split()[1:]
            if line.startswith("DATA"):
                break
    arr = np.loadtxt(path, skiprows=n_hdr, dtype=np.float32, ndmin=2)
    idx = [fields.index(k) for k in ("x", "y", "z", "intensity")]
    return arr[:, idx]


def write_dair_pcd(path, pts):
    """DAIR-style binary PCD: x y z intensity, float32."""
    n = len(pts)
    header = ("# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\n"
              "FIELDS x y z intensity\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\n"
              f"WIDTH {n}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {n}\nDATA binary\n")
    with open(path, "wb") as fh:
        fh.write(header.encode())
        fh.write(np.ascontiguousarray(pts, dtype=np.float32).tobytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="dir holding a9_dataset_r02_s0*")
    ap.add_argument("--dst", required=True, help="output root, DAIR layout")
    ap.add_argument("--limit", type=int, default=0, help="convert only N frames (smoke test)")
    ap.add_argument("--no-points", action="store_true", help="skip point clouds (fast check)")
    ap.add_argument("--keep-invisible", action="store_true",
                    help="keep objects that do not project into the camera image "
                         "(off by default; see CAMERA SCOPING in the module docstring)")
    args = ap.parse_args()

    src, dst = pathlib.Path(args.src), pathlib.Path(args.dst)
    for sub in ("image", "velodyne", "calib/camera_intrinsic",
                "calib/virtuallidar_to_camera", "label/camera", "label/virtuallidar"):
        (dst / sub).mkdir(parents=True, exist_ok=True)

    pattern = "a9_dataset_r02_s0*/a9_dataset_r02_s0*/labels_point_clouds/" + LID + "/*.json"
    labels = sorted(src.glob(pattern))
    if args.limit:
        labels = labels[:args.limit]
    print(str(len(labels)) + " frames")

    stats = {"objects": 0, "kept": 0, "unmapped": {}, "no_image": 0,
             "no_pcd": 0, "in_img_2d": 0, "dropped_not_in_image": 0}
    index, split = [], []

    for i, lab in enumerate(labels):
        sid = "%06d" % i
        ol = json.loads(lab.read_text())["openlabel"]
        T = np.array(ol["coordinate_systems"][CAM]["pose_wrt_parent"]["matrix4x4"]).reshape(4, 4)
        R, t = T[:3, :3], T[:3, 3]
        t_shift = t - Z_SHIFT * R[:, 2]          # see module docstring
        ip = ol["streams"][CAM]["stream_properties"]["intrinsics_pinhole"]
        K34 = np.array(ip["camera_matrix_3x4"]).reshape(3, 4)
        K = K34[:3, :3]
        W, H = int(ip["width_px"]), int(ip["height_px"])

        frame = next(iter(ol["frames"].values()))
        fp = frame.get("frame_properties", {})
        seq_dir = lab.parents[2]

        names = fp.get("image_file_names", [])
        if isinstance(names, str):
            names = json.loads(names.replace("'", '"'))
        img_name = None
        for n in names:
            if CAM in n:
                img_name = n
                break
        if img_name and (seq_dir / "images" / CAM / img_name).exists():
            shutil.copy2(seq_dir / "images" / CAM / img_name, dst / "image" / (sid + ".jpg"))
        else:
            stats["no_image"] += 1

        if not args.no_points:
            pcd_name = fp.get("point_cloud_file_name") or lab.name.replace(".json", ".pcd")
            pcd = seq_dir / "point_clouds" / LID / pcd_name
            if pcd.exists():
                pts = read_tumtraf_pcd(pcd)
                pts[:, 2] += Z_SHIFT
                write_dair_pcd(dst / "velodyne" / (sid + ".pcd"), pts)
            else:
                stats["no_pcd"] += 1

        (dst / "calib" / "camera_intrinsic" / (sid + ".json")).write_text(json.dumps({
            "height": H, "width": W, "cam_D": [0.0] * 5,
            "cam_K": [float(v) for v in K.reshape(-1)],
            "P": [float(v) for v in K34.reshape(-1)],
        }))
        (dst / "calib" / "virtuallidar_to_camera" / (sid + ".json")).write_text(json.dumps({
            "rotation": [[float(v) for v in r] for r in R],
            "translation": [[float(v)] for v in t_shift],
        }))

        objs = []
        for ob in frame.get("objects", {}).values():
            od = ob["object_data"]
            cub = od.get("cuboid", {}).get("val")
            if not cub:
                continue
            stats["objects"] += 1
            name = CLASS_MAP.get(od["type"])
            if name is None:
                stats["unmapped"][od["type"]] = stats["unmapped"].get(od["type"], 0) + 1
                continue
            x, y, z, qx, qy, qz, qw, l, w, h = cub[:10]
            z += Z_SHIFT
            yaw = quat_to_yaw(qx, qy, qz, qw)

            occ = "0"
            for a in od.get("cuboid", {}).get("attributes", {}).get("text", []):
                if a["name"] == "occlusion_level":
                    occ = OCC_MAP.get(a["val"], "0")

            cam = (R @ corners_3d(x, y, z, l, w, h, yaw).T).T + t_shift
            front = cam[:, 2] > 0.1
            if front.any():
                uv = (K @ cam[front].T).T
                uv = uv[:, :2] / uv[:, 2:3]
                x0, y0 = float(uv[:, 0].min()), float(uv[:, 1].min())
                x1, y1 = float(uv[:, 0].max()), float(uv[:, 1].max())
                cx0, cy0 = max(0.0, x0), max(0.0, y0)
                cx1, cy1 = min(float(W), x1), min(float(H), y1)
                full = max((x1 - x0) * (y1 - y0), 1e-6)
                vis = max(cx1 - cx0, 0.0) * max(cy1 - cy0, 0.0) / full
                trunc = "0" if vis > 0.95 else ("1" if vis > 0.5 else "2")
                if cx1 > cx0 and cy1 > cy0:
                    stats["in_img_2d"] += 1
                box = {"xmin": cx0, "ymin": cy0, "xmax": cx1, "ymax": cy1}
            else:
                trunc = "2"
                box = {"xmin": 0.0, "ymin": 0.0, "xmax": 0.0, "ymax": 0.0}

            # Camera scoping: DAIR labels only camera-visible objects (0 of 14099
            # degenerate), so keeping 360-degree LiDAR labels here would compare
            # unlike GT sets. See CAMERA SCOPING in the module docstring.
            visible = box["xmax"] > box["xmin"] and box["ymax"] > box["ymin"]
            if not visible and not args.keep_invisible:
                stats["dropped_not_in_image"] += 1
                continue

            objs.append({
                "type": name, "occluded_state": occ, "truncated_state": trunc,
                "alpha": "0", "2d_box": box,
                "3d_dimensions": {"h": float(h), "w": float(w), "l": float(l)},
                "3d_location": {"x": float(x), "y": float(y), "z": float(z)},
                "rotation": float(yaw),
            })
            stats["kept"] += 1

        payload = json.dumps(objs)
        (dst / "label" / "camera" / (sid + ".json")).write_text(payload)
        (dst / "label" / "virtuallidar" / (sid + ".json")).write_text(payload)
        index.append({"image_path": "image/" + sid + ".jpg", "frame": sid,
                      "weather": fp.get("weather_type"),
                      "time_of_day": fp.get("time_of_day"),
                      "source": str(lab.relative_to(src))})
        split.append(sid)
        if (i + 1) % 200 == 0:
            print("  %d/%d" % (i + 1, len(labels)))

    (dst / "frame_index.json").write_text(json.dumps(index, indent=1))

    # gen_info_dair expects a FLAT split file, matching DAIR's own
    # single-infrastructure-split-data.json. Everything is val: the cross-dataset
    # experiment is zero-shot, nothing is trained on TUMTraf.
    (dst / "tumtraf-split-data.json").write_text(json.dumps(
        {"train": [], "val": split, "test": []}))

    # data_info.json is required by gen_lidar2cam inside dair2kitti. Pure path
    # index -- no geometry, no classes, no thresholds.
    specs = [
        ("image_path", "image", ".jpg"),
        ("pointcloud_path", "velodyne", ".pcd"),
        ("calib_camera_intrinsic_path", "calib/camera_intrinsic", ".json"),
        ("calib_virtuallidar_to_camera_path", "calib/virtuallidar_to_camera", ".json"),
        ("label_camera_std_path", "label/camera", ".json"),
        ("label_lidar_std_path", "label/virtuallidar", ".json"),
    ]
    info, missing = [], []
    for sid in split:
        rec = {}
        for key, sub, ext in specs:
            rel = sub + "/" + sid + ext
            if not (dst / rel).is_file():
                missing.append(rel)
            rec[key] = rel
        info.append(rec)
    if missing:
        print("WARNING: %d referenced files missing, e.g. %s" % (len(missing), missing[:3]))
    (dst / "data_info.json").write_text(json.dumps(info))
    print("data_info.json: %d frames, %d missing files" % (len(info), len(missing)))

    print(json.dumps(stats, indent=1))
    print("wrote " + str(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
