# Track A — CUDA-BEVFusion on Jetson Orin Nano (15 W, clocks locked)

NVIDIA pretrained resnet50 weights, a real nuScenes frame, NVIDIA's own TensorRT
pipeline. Detection output in `cuda-bevfusion.jpg`.

| stage | FP16 ms | INT8 ms | speedup |
|---|---|---|---|
| CopyLidar | 0.55 | 0.57 | **0.97x** |
| ImageNrom | 5.86 | 5.98 | **0.98x** |
| Lidar Backbone | 66.29 | 46.56 | 1.42x |
| Camera Depth | 0.34 | 0.34 | **1.00x** |
| Camera Backbone | 51.45 | 29.50 | 1.74x |
| Camera Bevpool | 6.57 | 6.44 | **1.02x** |
| VTransform | 6.08 | 6.09 | **1.00x** |
| Transfusion | 23.68 | 15.40 | 1.54x |
| Head BoundingBox | 14.54 | 14.56 | **1.00x** |
| **Total** | 168.95 | 118.88 | 1.42x |

**Unquantisable floor: 33.98 ms** — the stages under 1.10x, 29% of the INT8 frame. Quantisation cannot touch it.

| | NVIDIA Orin AGX (published) | this Orin Nano | ratio |
|---|---|---|---|
| FP16 | 18 FPS / 55.6 ms | 5.9 FPS / 168.95 ms | 3.04x |
| INT8 | 25 FPS / 40 ms | 8.4 FPS / 118.88 ms | 2.97x |
| INT8 gain | 1.39x | 1.42x | — |

Both precisions miss the 100 ms / 10 Hz line. The hardware gap is stable across
precisions, and the relative INT8 benefit matches AGX within 2% — compression
behaviour is hardware-portable even though absolute performance is not.

The view transform at ~1.00x independently reproduces the same finding from our
own untrained FlashOcc-shaped model (1.03x), so it is a property of the operator,
not of either implementation.
