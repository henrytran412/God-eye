# God-eye

**Does compressing a 3D perception model to run on automotive edge hardware make it lose
more accuracy under dataset shift than the full-precision model does?**

Undergraduate research, SJSU College of Engineering — Davidson Student Scholars,
AY2026–27. Faculty mentor: Prof. Kaikai Liu.

---

## Why the question

3D perception models are published with accuracy measured **in-domain, on datacentre
GPUs**. FlashOcc reports mIoU 31.95 on Occ3D-nuScenes; CUDA-BEVFusion reports 67.89 mAP
with throughput on an RTX 3090. A car runs them **compressed, on embedded hardware, in
places the training data never covered**. Every condition differs.

Both losses are documented separately:

- **Compression:** NVIDIA publishes an in-domain INT8 cost for BEVFusion — 67.89 → 67.66
  mAP, a 0.23 drop.
- **Domain shift:** DG-BEV (CVPR 2023) measures a camera BEV detector moved
  nuScenes → Waymo scoring **0.040 mAP against a 0.552 oracle — 7% retained**.

Nobody has measured whether they *interact*. If compression amplifies domain-shift damage,
the model actually shipped in a vehicle is the one that fails hardest in exactly the
conditions it was not trained for. If it does not, edge deployment is free of robustness
cost — which has not been shown either. Both answers are worth having.

## Status

**Pre-proposal.** Proposal due to the department 27 September 2026. This repository
currently holds the feasibility work being done to support it.

| | |
|---|---|
| Research direction | Settled — perception only |
| Datasets | DAIR-V2X-I complete (7,058 frames, assembled); nuScenes example ships with BEVFusion |
| ONNX export path | Verified against PyTorch |
| Jetson board | Orin Nano, JetPack 7 / L4T r39.2, TensorRT 10.7 in container — reachable, TensorRT working (see `JETSON_SETUP.md`) |
| Jetson benchmark harness | Runs; first engine build in progress |
| Accuracy results | **None yet** |

## Repository map

```
code/edge/          Edge benchmarking harness — the active work
  occ_model.py        FlashOcc-shaped occupancy net (200x200x16x18) → ONNX,
                      with no mmdet3d and no bev_pool_v2 CUDA op
  export_backbone.py  R50 image backbone → ONNX (latency lower bound)
  bench_trt.py        trtexec-driven Jetson benchmark: latency, memory, power, thermals

WORKFLOW.md         Day-by-day plan to the 27 September deadline
PERCEPTION_PIVOT.md Research behind the direction; the literature and the gap
SECURITY_TRACK_ASSESSMENT.md  Why the security direction was dropped
PROPOSAL_v2.{md,tex}          Proposal draft in the DSS template

code/ghostguard/    ⚠ ABANDONED — see below
REVIEW.md           Audit of the abandoned direction
ADVISOR_BRIEF.md    Findings from the abandoned direction
```

## ⚠ About `code/ghostguard/` and its results

That directory, and the numbers in `REVIEW.md`, `ADVISOR_BRIEF.md`, and `results/`, belong
to an **earlier, abandoned project** on cooperative-perception security. Read them with two
things in mind:

1. **Every number came from a synthetic simulator** (`code/ghostguard/sim.py`) whose
   parameters — detection rates, pose error, attacker behaviour, risk weights — were chosen
   by hand. They are design checks on whether a decision rule was well-posed, **never
   benchmark performance**, and nothing in them was validated against real data.
2. **The direction was dropped** on advice that it combined two research areas and rested
   on a threat model with no real-world evidence: V2X message attacks on deployed
   autonomous vehicles have no documented instance, because V2X is not deployed at scale.

The work is kept because the audit that killed it was useful, and because the
falsehood-versus-harm measurement in it is still an interesting result. It is not the
current project.

## Running the edge harness

Export the ONNX models on any machine — CPU-only PyTorch is fine, no GPU needed:

```bash
pip install --user onnx
python code/edge/export_backbone.py                       # backbone only
python code/edge/occ_model.py --view-transform skip       # lower bound
python code/edge/occ_model.py --view-transform scatter    # upper bound
```

Then benchmark on the Jetson:

```bash
scp onnx/*.onnx code/edge/bench_trt.py jetson:~/bench/
ssh jetson "sudo nvpmodel -m 0 && sudo jetson_clocks"
ssh jetson "cd ~/bench && python3 bench_trt.py --onnx flashocc_shaped_skip.onnx --tag 15W"
```

See `code/edge/README.md` for the full procedure, failure branches, and how to read the
numbers honestly. The occupancy model is **untrained** — it reproduces FlashOcc's
architecture and tensor shapes so that latency and memory are representative, and it
predicts nothing. Every number from it is a cost measurement, never an accuracy
measurement.

## References

- **FlashOcc** — occupancy via channel-to-height, no 3D decoder. arXiv:2311.12058
- **DG-BEV** — cross-dataset BEV detection collapse. CVPR 2023, arXiv:2303.01686
- **CUDA-BEVFusion / CUDA-V2XFusion** — NVIDIA TensorRT deployments with published Jetson
  Orin numbers. [NVIDIA-AI-IOT/Lidar_AI_Solution](https://github.com/NVIDIA-AI-IOT/Lidar_AI_Solution)
- **Occ3D** — occupancy benchmark. NeurIPS 2023
- **UniOcc** — unified occupancy benchmark enabling cross-dataset analysis. ICCV 2025

## License

MIT — see `LICENSE`.
