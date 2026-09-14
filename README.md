# God-eye

**When a 3D detector is moved to a place it was never trained on, which part of it breaks?**

Undergraduate research, SJSU College of Engineering — Davidson Student Scholars,
AY2026–27. Faculty mentor: Prof. Kaikai Liu.

**📄 [Read the findings →](https://henrytran412.github.io/God-eye/)**

---

## The short version

A roadside 3D detector trained in Beijing, evaluated unchanged on a German intersection,
**keeps finding vehicles and keeps placing them correctly. It stops knowing which way they
point** — and that alone destroys its score.

| | DAIR-V2X-I (source) | TUMTraf (target) |
|---|---|---|
| Car 3D AP @ IoU 0.5, moderate | **69.70** | **0.13** |
| Vehicle heading within ±5° | **88%** | **28%** |
| Median heading error | −0.2° | **−0.2°** |

The median is unchanged in both domains, so this is not a coordinate or conversion bug —
the *bias* is fine and the *reliability* collapses. A ~20° heading error on a 4.1 × 1.9 m
box still clears IoU 0.25 but not IoU 0.5, which is exactly why Car (scored at the strict
threshold) reads 0.13 while Pedestrian and Cyclist (scored at 0.25) retain 56% and 65%.

## Status

| | |
|---|---|
| Baseline reproduces published numbers | ✅ within **0.02–0.04 AP** of NVIDIA's DAIR-V2X-I table |
| Edge latency measured | ✅ CUDA-BEVFusion, FP16 168.95 ms / INT8 118.88 ms |
| In-domain compression cost | ✅ Δ = **0.037 AP** (Car, moderate) |
| Cross-dataset evaluation | ✅ TUMTraf Intersection, 2160 frames, FP16 + INT8 |
| Mechanism identified | ✅ orientation, not detection or localisation |
| Compression amplifies domain shift? | ❌ **not supported** — effects at noise level, see below |
| Proposal | in drafting, due 27 September 2026 |

## What the measurements say

**1. The instrument is calibrated.** V2XFusion INT8-PTQ on the full 2016-frame DAIR-V2X-I
validation split reproduces NVIDIA's published table: Car 82.08/69.70/69.75 against their
82.06/69.70/69.75. Nothing downstream is worth reading without this.

**2. Compression is nearly free in-domain.** FP16 → INT8 costs 0.037 AP on Car, 0.518 on
Pedestrian, 0.263 on Cyclist.

**3. Edge hardware cannot run it at full precision.** On an Orin Nano at 15 W, CUDA-BEVFusion
is 168.95 ms at FP16 and 118.88 ms at INT8 — **both miss the 100 ms / 10 Hz line**. The
stages that do not compress sum to **33.98 ms, 29% of the INT8 frame**.

**4. Domain shift is severe, and localised.** Full tables in
[`results_jetson/`](results_jetson/).

**5. The original hypothesis is not supported.** Whether INT8 amplifies domain-shift damage
remains open: per-class effects disagree in sign and sit at noise level. Recorded in full in
[`results_jetson/tumtraf/CROSS_DATASET.md`](results_jetson/tumtraf/CROSS_DATASET.md) rather
than quietly dropped.

## Repository map

```
results_jetson/           All measurements, raw AP tables and logs
  trackA/                 CUDA-BEVFusion edge latency + detection output
  trackB/                 V2XFusion in-domain baseline and compression cost
  tumtraf/                Cross-dataset result and the unscoped comparison
  15W/                    Occupancy-model sweep, 3 models x 3 precisions
  sparsity/               2:4 structured sparsity measurements

code/edge/
  bench_trt.py            trtexec-driven Jetson benchmark: latency, power, thermals
  occ_model.py            FlashOcc-shaped occupancy net -> ONNX, no mmdet3d needed
  make_evidence.py        Turns results.json into tables and plots
  jetson_patches/         Everything needed to reproduce the runs (see below)

docs/index.html           The findings page published above
JETSON_SETUP.md           Board bring-up, and the JetPack 7 blockers with fixes
WORKFLOW.md               Plan to the 27 September deadline
```

## Reproducing this

`code/edge/jetson_patches/` holds the pieces that do not exist anywhere else:

| file | what it solves |
|---|---|
| `tumtraf_to_dair.py` | Converts TUMTraf OpenLABEL into DAIR-V2X-I layout so the *verified* `dair2kitti.py` and `gen_info_dair.py` run unchanged. Camera choice, transform direction and ground alignment each verified by measurement, not assumption. |
| `rotate_iou_cpu.py` + `test_rotate_iou.py` | CPU rotated-box IoU, because **numba's CUDA backend segfaults on this board** (a trivial kernel exits 139). Unit-tested, including the 90°-rotation case where a sign error hides. |
| `eval_crossdataset.py` | Runs a source-domain model on a target domain **without recalibrating** — deliberately, since source-domain calibration is the effect under test. |
| `loc_error.py`, `yaw_check.py` | The diagnostics that isolated orientation as the failure mode. |

`JETSON_SETUP.md` documents the eight blockers between a 2022 MMLab stack and JetPack 7,
including two defects in the shared lab container itself: `import scipy.sparse` fails out of
the box, and its PyTorch is built without `torch.distributed`.

## ⚠ `code/ghostguard/` is abandoned

That directory, and the numbers in `REVIEW.md`, `ADVISOR_BRIEF.md` and `results/`, belong to
an **earlier project** on cooperative-perception security. Every figure there came from a
hand-parameterised synthetic simulator with no trained detector — design checks, never
benchmark performance. The direction was dropped because V2X message attacks on deployed
vehicles have no documented real-world instance. Kept because the audit that killed it was
useful.

## References

- **DG-BEV** — cross-dataset BEV collapse, 7% of oracle on nuScenes→Waymo. CVPR 2023, arXiv:2303.01686
- **BEVHeight** — roadside 3D detection via height, the DAIR-V2X-I baseline. CVPR 2023
- **CUDA-BEVFusion / CUDA-V2XFusion** — [NVIDIA-AI-IOT/Lidar_AI_Solution](https://github.com/NVIDIA-AI-IOT/Lidar_AI_Solution)
- **TUMTraf Intersection (R2)** — German roadside dataset, [innovation-mobility.com](https://innovation-mobility.com/en/project-providentia/a9-dataset/)
- **DAIR-V2X** — infrastructure-side cooperative perception benchmark. CVPR 2022
- **Shortcut learning in deep neural networks** — Geirhos et al., *Nature Machine Intelligence* 2020

## License

MIT — see `LICENSE`.
