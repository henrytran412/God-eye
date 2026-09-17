# Reference verification — final

Deep-research harness, run `wf_bde5f60f-0cb`, resumed across five sessions until
**104/104 agents completed with zero errors**. Each claim was put to a three-vote
adversarial panel; 2 of 3 refutes kills a claim. Panels fetched primary sources,
extracted PDFs with `pdftotext` rather than trusting summaries, and re-derived the
arithmetic.

**Outcome: 11 findings survived, 13 were refuted.** The refutations matter more than
the confirmations — several were claims this project was about to cite.

---

## Safe to cite — verified

| # | claim | vote | conf |
|---|---|---|---|
| 1 | **ST3D** (CVPR 2021) is label-free (no target labels, no target size statistics) and closes **16–75%** of the source-only-to-oracle gap across four transfers. Waymo→KITTI, SECOND-IoU, Car moderate, IoU 0.7: AP_3D **27.48 → 61.83** against a **73.45** oracle (**+74.72%**); AP_BEV 67.64 → 82.19 (+92.97%). | 3-0 | high |
| 2 | **ROS** (random object scaling, source-side, fully label-free) recovers ~86% of SN's car gain: **+27.19 AP_3D** over source-only against SN's +31.72, only **4.53 AP** behind — and *beats* SN on cyclist (46.96 vs 41.43), where SN is net-harmful relative to source-only (43.84). Aggregated over three classes, 92% of SN's gain. | 3-0 | high |
| 3 | **SN is not a safe default.** It requires target-domain object-size statistics and degrades transfer when the size gap is small: nuScenes→KITTI AP_BEV **51.84 → 40.03** (−37.55% closed gap, SECOND-IoU; −36.82% PV-RCNN); Waymo→Lyft −5.11% BEV (−24.34% PV-RCNN). | 3-0 | high |
| 4 | **DPO** (ACM MM 2024) is the *only* verified method meeting "no target labels, no source data, no retraining" — single-pass test-time adaptation with a Hungarian-matcher pseudo-label filter and an early cutoff. | 3-0 | high |
| 5 | **MLC-Net** (ICCV 2021) is target-label-free but **NOT source-free and NOT test-time**: it streams labeled source data throughout and needs 5–20 epochs of joint fine-tuning. | 2-1 | high |
| 6 | **nuScenes mAOE** is a standalone true-positive error reported alongside mATE/mASE, entering NDS with weight 1 against mAP's weight 5; **mASE is computed after aligning orientation**, decoupling scale from heading by construction. **FOE**=\|(θ−θ̂) mod 360°\| and **HOE**=\|(θ−θ̂) mod 180°\| are defined in Cui et al. 2020. Both **in-domain only**. | 3-0 | high |
| 7 | Yaw is a **distinct failure axis**, not one that tracks translation/scale: error decomposition shows yaw disproportionately sensitive to perturbation, and mAP-style metrics hide it. **Adversarial perturbation, in-domain — no cross-dataset experiment.** Cite for the metric argument only. | 3-0 | med |
| 8 | **MS3D++** treats heading error as a **class-dependent** pseudo-label failure: catastrophic for elongated vehicles because it destroys IoU, tolerable for BEV-symmetric pedestrians. Architectural/rhetorical — **the paper reports no yaw-specific metric**. **monodle** (CVPR 2021) supplies a reusable per-sub-task attribution *protocol* via ground-truth substitution (monocular, in-domain). | 3-0 | med |
| 9 | **ST3D's headline is model-selection sensitive**: an independent 2024 analysis reports Easy 3D AP fluctuating between **27.9% and 60.9%** across randomizations, because best-epoch selection leaks target information. A method label-free in training can become label-dependent at checkpoint selection. | — | med |
| 10 | ST3D **+ SN** reaches 85.83 AP_BEV vs an 83.29 oracle on Waymo→KITTI — but this is **detector-specific** (PV-RCNN: 86.65/76.86 vs oracle 88.98/82.50, clearly below) and partly a **weak-oracle artifact** (the KITTI oracle trains on a small split while the adapted model is pre-trained on far larger Waymo). | 2-1 | med |

### Hand-verified separately (WebFetch / local PDF extraction)

* **MS3D++**: *"Deploying 3D detectors in unfamiliar domains has been demonstrated to
  result in a significant 70-90% drop in detection rate due to variations in lidar,
  geography, or weather."* — quoted verbatim from the abstract.
* **Cui et al. 2020** (arXiv:2011.03114), extracted from the PDF: *"the front and back of
  a vehicle may not be easily distinguishable from the LiDAR point cloud"*; parked
  vehicles *"have no moving trajectory predictions that could be used to reliably infer
  the orientations."* nuScenes, vehicle-mounted.
* **GBlobs** (CVPR 2025): *"over-reliance on these global geometric features can cause 3D
  detectors to prioritize object location and absolute position, resulting in poor
  cross-domain performance."* Gains >21 / 13 / 12 mAP on Waymo→KITTI / KITTI→Waymo /
  nuScenes→KITTI. All vehicle-mounted.

---

## REFUTED — must not be cited

| claim | vote | why it died |
|---|---|---|
| SN **alone** exceeds the supervised oracle on every category (Waymo→KITTI) | 0-3 | The oracle-beating row is ST3D++ **(w/ SN)** — the full pipeline. SN alone: car 59.20 vs oracle 73.45; cyclist 41.43 vs 60.32, *below source-only* in AP_BEV. |
| monodle sub-task numbers: GT orientation 11.12→11.88 (+0.76), GT location →78.84 | 1-2 | Specific values did not survive. The **protocol** is citable; these figures are not. |
| FOE/HOE ~13× gap: 59.9° full-range vs 4.7° half-range | 0-3 | Numbers did not survive. The **metric definitions** are citable; these values are not. |
| nuScenes matches by 2D center distance rather than IoU, so a wrong-heading box still counts as a true positive | 0-3 | Refuted as stated. |
| MS3D++ is source-free (no source data at adaptation) | 1-2 | Not source-free. |
| MS3D++ closes the gap to within 3–4 AP_BEV of a GT-trained oracle | 0-3 | Did not survive. |
| DPO: 57.72% relative gain, 91% of the supervised upper bound | 0-3 | Did not survive; the *method characterisation* did. |
| MLC-Net Table 1 transfer numbers (KITTI→Waymo 9.17→38.21 etc.) | 1-2 | Did not survive. |
| SF-UDA³D source-free framing and its Avg-AP figures | 1-2 | Did not survive. |
| ST3D++ per-class gains of 38–44 / 10–11 / 9–10 AP_3D | 0-3 | Did not survive. |
| MLC-Net attributes the gap to geometric/size mismatch, offering no support for an orientation-specific failure mode | 1-2 | Did not survive. |

---

## The gap the run could not fill

The harness returned a finding of its own, at high confidence:

> The evidence set contains **zero** verified results for roadside/infrastructure datasets
> (DAIR-V2X-I, Rope3D, TUMTraf), **zero** LiDAR+camera fusion transfers, and **nothing** on
> INT8 post-training quantization versus OOD robustness.

All 11 surviving findings concern vehicle-mounted, LiDAR-only datasets (Waymo, KITTI,
nuScenes, Lyft) plus one monocular diagnostic paper.

**This is a coverage gap in the verification run, not established absence.** The roadside
cross-dataset literature (BEVHeight, Rope3D) and the PTQ-robustness literature both exist
and simply were not reached. The proposal must therefore say that the size of the roadside
cross-dataset drop is **uncited in this evidence base**, not that it is unpublished.

## What this project measured itself

Everything in the preliminary-results tables was measured directly and is reproducible from
this repository (`results_jetson/`). The baseline reproduces NVIDIA's published DAIR-V2X-I
figures to within **0.02–0.04 AP**, which is the check that licenses the rest.
