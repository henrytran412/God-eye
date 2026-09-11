# Build the DAIR-style data_info.json that gen_lidar2cam requires.
# tumtraf_to_dair.py wrote frame_index.json (weather/time_of_day metadata) but
# never emitted data_info.json. This is a pure file-path index: no geometry,
# no class mapping, no thresholds -- nothing that affects the measured result.
import json, os, sys

root = "/home/sjsujetson/data/tumtraf-dair"
frames = [r["frame"] for r in json.load(open(os.path.join(root, "frame_index.json")))]
print("frames in index: %d" % len(frames))

specs = [
    ("image_path",                         "image",                        ".jpg"),
    ("pointcloud_path",                    "velodyne",                     ".pcd"),
    ("calib_camera_intrinsic_path",        "calib/camera_intrinsic",       ".json"),
    ("calib_virtuallidar_to_camera_path",  "calib/virtuallidar_to_camera", ".json"),
    ("label_camera_std_path",              "label/camera",                 ".json"),
    ("label_lidar_std_path",               "label/virtuallidar",           ".json"),
]

info, missing = [], []
for sid in frames:
    rec = {}
    for key, sub, ext in specs:
        rel = "%s/%s%s" % (sub, sid, ext)
        if not os.path.isfile(os.path.join(root, rel)):
            missing.append(rel)
        rec[key] = rel
    info.append(rec)

if missing:
    print("MISSING %d files, first 10: %s" % (len(missing), missing[:10]))
    sys.exit(1)

with open(os.path.join(root, "data_info.json"), "w") as f:
    json.dump(info, f)
print("wrote data_info.json with %d records" % len(info))
print("sample: %s" % json.dumps(info[0], indent=2))

# The pipeline needs a FLAT split file; the converter nested it under batch_split.
sp = os.path.join(root, "tumtraf-split-data.json")
d = json.load(open(sp))
if "batch_split" in d:
    d = d["batch_split"]
    with open(sp, "w") as f:
        json.dump(d, f)
    print("unwrapped batch_split")
print("split: train=%d val=%d test=%d" % (len(d["train"]), len(d["val"]), len(d["test"])))
