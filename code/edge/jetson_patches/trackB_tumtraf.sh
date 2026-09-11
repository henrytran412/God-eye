#!/bin/bash
# Track B cross-dataset: TUMTraf Intersection, zero-shot, FP16 and INT8.
#
# Both models were produced on DAIR-V2X-I and are applied here unchanged. The INT8
# one keeps its DAIR calibration on purpose: PTQ derives per-tensor ranges from a
# SOURCE-domain calibration set, and whether those ranges still fit the target's
# activations is the effect being measured. Recalibrating would erase it.
#
# Writes a per-stage status file so failures are detectable without reading logs:
#   name|STATE|start|end|rc|seconds
set -u
R=/home/sjsujetson
BF=$R/bevfusion
TT=$R/data/tumtraf-dair
CFG=configs/V2X-I/default_tumtraf.yaml
DET=configs/V2X-I/det/centerhead/lssfpn/camera+pointpillar/resnet34/default.yaml
IMG=cmpelkk/jetson-llm:latest
OUT=$R/godeye/out/tumtraf
ST=$OUT/STATUS
mkdir -p "$OUT"
: > "$ST"

run() {
  local name="$1"; shift
  local t0=$(date +%s)
  echo "$name|RUNNING|$(date -u +%H:%M:%SZ)|-|-|-" >> "$ST"
  docker run --rm --runtime nvidia --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
    -v $R:$R -w $BF \
    -e PYTHONPATH=$R/deps/site:$BF:$BF/scripts -e LD_LIBRARY_PATH=$R/godeye/lib \
    $IMG bash -lc "$*" > "$OUT/$name.log" 2>&1
  local rc=$? t1=$(date +%s)
  grep -v "^$name|RUNNING" "$ST" > "$ST.tmp" && mv "$ST.tmp" "$ST"
  local state=OK; [ $rc -ne 0 ] && state=FAILED
  echo "$name|$state|-|$(date -u +%H:%M:%SZ)|$rc|$((t1-t0))" >> "$ST"
  if [ $rc -ne 0 ]; then
    echo "PIPELINE|FAILED|-|$(date -u +%H:%M:%SZ)|$rc|-" >> "$ST"
    return 1
  fi
  return 0
}

echo "waiting for conversion to finish..."
while pgrep -f '[c]onvert_tumtraf' >/dev/null; do sleep 20; done

N=$(ls $TT/velodyne 2>/dev/null | wc -l)
echo "converted frames: $N"
if [ "$N" -lt 2000 ]; then
  echo "PIPELINE|FAILED|-|$(date -u +%H:%M:%SZ)|only-$N-frames|-" >> "$ST"; exit 1
fi

# gen_info_dair expects a FLAT split file {"train":[],"val":[],"test":[]}; the
# converter wrote it nested under "batch_split".
python3 - <<PY
import json, pathlib
p = pathlib.Path("$TT/tumtraf-split-data.json")
d = json.loads(p.read_text())
if "batch_split" in d:
    d = d["batch_split"]
p.write_text(json.dumps(d))
print("split: train=%d val=%d test=%d" % (len(d["train"]), len(d["val"]), len(d["test"])))
PY

run 10_dair2kitti "python3 scripts/data_converter/dair2kitti.py \
    --source-root $TT --target-root ${TT}-kitti \
    --split-path $TT/tumtraf-split-data.json --temp-root ./tmp_tumtraf" || exit 1
run 11_gen_info "python3 scripts/gen_info_tumtraf.py" || exit 1

run 20_eval_fp16 "python3 -W ignore scripts/eval_crossdataset.py $CFG fp16_ref.pth \
    --out $OUT/tumtraf_fp16_outputs.pkl" || exit 1
run 21_eval_int8 "python3 -W ignore scripts/eval_crossdataset.py $CFG ptq.pth \
    --out $OUT/tumtraf_int8_outputs.pkl" || exit 1

echo "PIPELINE|DONE|-|$(date -u +%H:%M:%SZ)|0|-" >> "$ST"
echo "=== TUMTRAF CROSS-DATASET PIPELINE DONE $(date -u +%H:%M:%SZ) ==="
