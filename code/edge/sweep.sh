#!/bin/bash
# Full Jetson sweep: every model x every precision, at one power mode.
#
# Runs on the Jetson HOST. Serial by design -- two engine builds sharing 8 SMs
# and 7.3 GB of unified memory would corrupt each other's latency numbers and
# risk the OOM reaper.
#
#   sudo nvpmodel -m 0 && sudo jetson_clocks     # lock FIRST
#   ./sweep.sh 15W
#
# An Orin Nano at 7 W and the same board at 15 W are different machines; their
# numbers must never share a table, which is why the mode is recorded here.
#
# Order is deliberate: `scatter` is the real FlashOcc view transform and the
# riskiest build (ScatterElements with duplicate indices), so it runs first
# while there is time to react if it fails.
set -u
TAG="${1:-15W}"
ROOT=/home/sjsujetson/godeye
IMAGE=cmpelkk/jetson-llm:latest
OUT="$ROOT/out/$TAG"
mkdir -p "$OUT"

echo "=== power / clock state ==="
nvpmodel -q | tee "$OUT/power_mode.txt"
cat /sys/kernel/debug/bpmp/debug/clk/gpusysclk/rate 2>/dev/null | tee "$OUT/gpu_clk.txt"
date -u +"%Y-%m-%dT%H:%M:%SZ" | tee "$OUT/started_at.txt"

for m in flashocc_shaped_scatter flashocc_shaped_skip backbone_r50_6x256x704; do
  onnx="$ROOT/onnx/$m.onnx"
  [ -f "$onnx" ] || { echo "SKIP $m (missing)"; continue; }
  echo
  echo "################ $m ################"
  python3 "$ROOT/bench_trt.py" \
      --onnx "$onnx" \
      --docker-image "$IMAGE" \
      --stub-lib "$ROOT/lib" \
      --mount "$ROOT" \
      --precisions fp32 fp16 int8 \
      --iterations 200 --warmup-ms 2000 --workspace-mb 2048 \
      --tag "$TAG" \
      --timing-cache "$ROOT/out/timing.cache" \
      --outdir "$OUT/$m" 2>&1 | tee "$OUT/$m.console.log"
done

echo
echo "=== done: $OUT ==="
find "$OUT" -name results.json | sort
