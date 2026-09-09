# One-week feasibility study: occupancy prediction on a Jetson Orin Nano

**Goal:** by 27 September, show Prof. Liu enough real hardware evidence that he approves
the proposal. Not accuracy. Not a trained model. **Feasibility.**

The claim you need to support is narrow and achievable:

> A FlashOcc-shaped occupancy network runs on a Jetson Orin Nano at *these* speeds, in
> *this* much memory, at *these* precisions — so a project that compresses it and
> measures its behaviour under dataset shift is executable on this hardware.

Nobody has published occupancy-network numbers on Jetson-class hardware. Whatever you
measure is new, **including a negative result** — see "If it does not fit" below.

---

## What is already built and verified

Three scripts. The export half runs on your laptop with CPU-only PyTorch.

| Artifact | Shape | Size | Status |
|---|---|---|---|
| `backbone_r50_6x256x704.onnx` | (6,3,256,704) → (6,256,32,88) | 98.8 MB | verified, 9.9e-05 vs torch |
| `flashocc_shaped_skip.onnx` | (6,3,256,704) → (1,16,18,200,200) | 59.1 MB | verified, rel 9.5e-07 |
| `flashocc_shaped_scatter.onnx` | (6,3,256,704) → (1,16,18,200,200) | 73.9 MB | verified, rel 2.2e-06 |

`occ_model.py` reproduces FlashOcc's architecture and tensor shapes — R50 → DepthNet
(59 depth bins × 80 context) → LSS view transform → 200×200 BEV → BEV encoder →
channel2height head → **200×200×16×18**, the real FlashOcc output — without mmdet3d,
mmcv, or the `bev_pool_v2` CUDA op. 14.8 M parameters.

**It is not trained.** Every number it produces is a *cost* measurement, never an
accuracy measurement. Say that out loud whenever you show a number, or the result
collapses the first time somebody checks.

### The two view-transform variants bracket the truth

Real FlashOcc scatters frustum features into BEV cells with a custom CUDA kernel that
has no ONNX equivalent. So:

- **`skip`** omits the stage → **lower bound** on total latency.
- **`scatter`** uses `scatter_add` → **upper bound**. It has to broadcast the index to
  the source shape, materialising a 19.9 M-element int64 tensor. That memory traffic is
  precisely why BEVDet ships a custom kernel, so this is pessimistic by construction.

Report both and say "the real model lies between X and Y ms." That is more honest and
more useful than one number of unknown bias, and it is a defensible thing to show.

The frustum tensor itself is **19.9 M elements — 80 MB at fp32, 40 MB at fp16**. On an
8 GB board that single intermediate is the thing most likely to break you.

---

## Do these two things today

Both have latency that you cannot compress later.

1. **Register for nuScenes** at nuscenes.org. Approval is not instant. You only need
   `v1.0-mini` (~4 GB) and it is not needed until Phase 1 — but start the clock now.
2. **Check the Jetson boots and report what it is.** JetPack version decides your
   TensorRT version, which decides everything else:
   ```bash
   cat /etc/nv_tegra_release
   dpkg-query -W -f='${Version}\n' nvidia-jetpack
   ls /usr/src/tensorrt/bin/trtexec
   free -h && df -h /
   ```
   If `trtexec` is missing, `sudo apt install tensorrt` — and if JetPack itself is old
   or absent, reflashing eats a day, so find out now, not on Thursday.

---

## Day by day

**Day 1 — toolchain.** Copy the ONNX files over. Run the backbone through `trtexec` at
FP32 only. The goal is one successful engine build, not good numbers. Expect problems
here; this is the day they surface.

```bash
scp onnx/*.onnx code/edge/bench_trt.py <user>@<jetson>:~/bench/
ssh <user>@<jetson>
cd ~/bench && python3 bench_trt.py --onnx backbone_r50_6x256x704.onnx --precisions fp32
```

**Day 2 — the real measurement.** Lock the clocks, then all three precisions on all
three models. This is the core result.

```bash
sudo nvpmodel -m 0 && sudo jetson_clocks     # record which mode you used
for m in backbone_r50_6x256x704 flashocc_shaped_skip flashocc_shaped_scatter; do
  python3 bench_trt.py --onnx $m.onnx --tag 15W-maxclk --outdir out_$m
done
```

**Day 3 — find the limits.** Where does it break? Sweep the power modes (7 W vs 15 W —
these are effectively different machines, never compare across them). Try a lower input
resolution. Find the largest configuration that fits in 8 GB. The boundary *is* the
finding.

**Day 4 — buffer.** Something will have gone wrong. This is the day for it.

**Day 5 — assemble.** Results table, one plot: latency vs precision, with a horizontal
line at the 10 Hz (100 ms) and 2 Hz (500 ms) budgets.

**Day 6 — one page for Prof. Liu.** Not a report. One page: the table, the plot, three
sentences on what it means for the proposal, and one honest paragraph on what the
numbers do *not* show.

**Day 7 — meet, then submit.**

---

## If it does not fit

**This is still a good outcome, and you should plan the sentence now.** If the model OOMs
or runs at 2 s/frame, you have measured the exact gap between a research occupancy model
and deployable hardware — which is the quantitative motivation for the entire project.
"FlashOcc needs an H100; here is what it does on the edge device an actual car would
carry" is a stronger opening than "it runs fine."

Frame it as: *the gap is N×, and closing it is the project.*

---

## Reading the numbers honestly

- `--noDataTransfers` is on, so these are pure compute times excluding host↔device
  copies. Right for comparing precisions; optimistic for deployment. Note it.
- **INT8 here is latency only.** With no calibration cache TensorRT guesses dynamic
  ranges. The speed is real; any accuracy claim from it would not be.
- Six cameras per frame. nuScenes keyframes are 2 Hz, sweeps 10 Hz — say which budget
  you are comparing against.
- Check `temp_max_c` in the output. A latency number from a throttled board is not a
  latency number.

---

## Status of each file

| File | Status |
|---|---|
| `export_backbone.py` | **Verified.** Runs, output shape and numerics checked against PyTorch. |
| `occ_model.py` | **Verified.** Both variants export; ONNX Runtime output matches PyTorch to ~1e-6 relative. |
| `bench_trt.py` | **Never run on a GPU.** Syntax checked; the `trtexec` output parser is unit-tested against known-format sample output; the missing-TensorRT path exits cleanly. Everything touching hardware is unexercised. |

Treat the first Jetson session as debugging, not measurement.
