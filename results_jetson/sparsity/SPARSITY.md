# Third compression axis: 2:4 structured sparsity (Orin Nano, 15 W)

`trtexec --sparsity=force` tells TensorRT to assume 2:4 sparse weights and use the
sparse kernels. The models here are not sparsity-trained, so this measures the
**speed ceiling** the hardware offers, not an achievable accuracy/speed point.

| model | precision | dense ms | +sparsity ms | gain |
|---|---|---|---|---|
| scatter | FP16 | 79.92 | 71.61 | 1.12x |
| scatter | INT8 | 54.93 | 50.01 | 1.10x |
| skip | FP16 | 65.85 | 57.79 | 1.14x |
| skip | INT8 | 39.88 | 34.73 | 1.15x |

**Validation.** The dense column reproduces the earlier 15 W sweep to within 0.2%
(79.92/79.92, 54.93/54.91, 65.85/65.74, 39.88/39.85) — a third independent run.

**Finding.** NVIDIA reports sparsity lifting V2XFusion on Orin **AGX** by 1.17x at
FP16 (81 -> 95 FPS) and 1.24x at INT8 (127 -> 158 FPS). This board gets 1.10-1.15x,
falling short by 6-12%, with the largest shortfall at INT8 where AGX gains most.

Set against the quantisation result — where the Orin Nano's INT8 speedup matched
AGX within 2% (1.42x vs 1.39x) — the conclusion is that **compression techniques
differ in how well their benefit transfers across hardware tiers.** Quantisation's
does; structured sparsity's does not, plausibly because sparse tensor cores need
more parallel work than 8 SMs can keep fed. Anyone extrapolating a sparsity speedup
from a datacentre or AGX measurement to a Nano-class device would overstate it.
