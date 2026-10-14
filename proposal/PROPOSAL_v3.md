# Davidson Student Scholars Proposal — AY2026–27

**Name:** Tran, Thuc Bao · **Email:** thucbao.tran@sjsu.edu
**Department:** Computer Engineering, College of Engineering
**Faculty Mentor:** Prof. Kaikai Liu
**Track:** Undergraduate Research Project ($1,500)
**Period:** Fall 2026 – Spring 2027 · Final report due 30 May 2027

**Title:** Which Component Fails When a Roadside Detector Moves?

---

## Synopsis of Proposed Research (240 words)

Roadside 3D detectors are trained at one intersection and deployed at another. Published
accuracy is measured on the training distribution; deployment is not. The loss is known to
be large — a reported 70–90% drop in detection rate across changes in lidar, geography and
weather [1] — but the field reports it as a single number and attempts to close it wholesale.

Preliminary measurements on a Jetson Orin Nano suggest the loss is not uniform. Evaluating
NVIDIA's pretrained V2XFusion [12] zero-shot from DAIR-V2X-I (Beijing) [10] to TUMTraf
Intersection (Munich) [11], detection and position largely survive while heading estimation collapses:
vehicles within ±5° of true heading fall from 88% to 28%, with the median error unchanged
at −0.2° in both domains. Because roughly 20° of heading error on a 4.1 × 1.9 m box clears
IoU 0.25 but not IoU 0.5, this one mode explains why Car accuracy falls 69.70 → 0.13 AP
while Pedestrian and Cyclist retain 56% and 65%.

Heading is already treated as a separate error axis in-domain — nuScenes reports mAOE
independently of mATE and mASE [2] — but a systematic search of the adaptation literature
found it isolated only in-domain or under adversarial perturbation, never under natural
cross-dataset shift, and never for roadside sensors.

This project will test whether domain fragility concentrates in specific components, and
whether the fragile one can be repaired without target labels. Four label-free
interventions will be measured against a supervised oracle.

---

# A. Introduction

## A.1 Current Research

**The cross-dataset drop is large and label-free adaptation partly closes it.** Self-training
recovers 16–75% of the source-only-to-oracle gap across four LiDAR transfers using no target
labels and no target statistics; on Waymo→KITTI it lifts Car AP₃D from 27.48 to 61.83 against
a 73.45 oracle [3]. Cheaper still, a purely source-side augmentation — random object scaling —
recovers about 86% of what the weakly supervised size prior buys (+27.19 AP₃D against +31.72),
and *outperforms* it on cyclist [4].

**Weak supervision is not automatically better.** Statistical Normalization consumes
target-domain object-size statistics yet degrades transfer when the size gap is small:
nuScenes→KITTI AP_BEV falls 51.84 → 40.03, a −37.55% closed gap [3].

**Orientation is already an established, separately-reported error axis.** nuScenes defines
mAOE as a standalone true-positive error alongside mATE and mASE, and computes mASE only
after aligning orientation, decoupling scale from heading by construction [2]. Earlier work
defines paired full- and half-range metrics, FOE = |(θ−θ̂) mod 360°| and HOE = |(θ−θ̂) mod
180°|, so that 180° flips are distinguishable from angular imprecision [5].

**Why heading is hard has a published explanation.** Cui et al. observe that "the front and
back of a vehicle may not be easily distinguishable from the LiDAR point cloud," and that
parked vehicles fail because they "have no moving trajectory predictions that could be used
to reliably infer the orientations" [5]. Heading is under-determined by appearance; detectors
lean on motion to resolve it.

## A.2 Limitations of Current Research

**Every adaptation result above is vehicle-mounted and LiDAR-only.** Waymo, KITTI, nuScenes
and Lyft are all ego-vehicle datasets. A roadside sensor is static, has no ego-motion, and in
the deployed single-frame configuration has no trajectory cue at all — precisely the cue
detectors are shown to depend on for heading [5].

**Heading has never been isolated under natural domain shift.** It is measured in-domain
(mAOE, FOE/HOE) and under adversarial perturbation, where error decomposition shows yaw is
disproportionately sensitive and mAP-style metrics hide it [6]. MS3D++ treats heading as a
class-dependent pseudo-label problem — catastrophic for elongated vehicles because it destroys
IoU, tolerable for BEV-symmetric pedestrians — but reports no yaw-specific metric [1]. None of
this is cross-dataset.

**Adaptation is evaluated as one number.** No work reports which *component* failed, so it is
unknown whether the loss is diffuse or concentrated, and therefore unknown whether a targeted,
cheap repair is even possible.

**A methodological trap is documented.** Self-training's headline result is model-selection
sensitive: Easy 3D AP has been reported fluctuating between 27.9% and 60.9% across
randomizations, because best-epoch selection leaks target information [7]. A method that is
label-free during training can become label-dependent at checkpoint selection.

## A.3 Research Gap

A systematic, adversarially-verified literature search returned **no** cross-dataset results
for roadside datasets (DAIR-V2X-I, Rope3D, TUMTraf), **no** LiDAR+camera fusion transfers, and
**nothing** on INT8 quantization versus out-of-distribution robustness. That is a limit of the
search rather than proof of absence — the roadside literature exists — but it establishes that
per-component fragility for roadside 3D detection is, at minimum, not a well-covered question.

# B. Specific Proposed Research and Why Important

**Question.** Does domain fragility in roadside 3D perception concentrate in specific network
components, and can the fragile component be repaired using only unlabeled target data?

**Preliminary evidence, already collected.** A full pipeline was built and validated on a
borrowed Jetson Orin Nano. It reproduces NVIDIA's published DAIR-V2X-I accuracy [10,12] to within
0.02–0.04 AP on Car and Pedestrian, establishing that subsequent measurements are trustworthy
rather than artifacts. Zero-shot transfer to TUMTraf Intersection [11] (2,160 frames) gives:

| 3D AP, moderate | DAIR-V2X-I | TUMTraf | retained |
|---|---|---|---|
| Car @ IoU 0.5 | 69.70 | 0.13 | 0.2% |
| Pedestrian @ IoU 0.25 | 49.39 | 27.61 | 55.9% |
| Cyclist @ IoU 0.25 | 57.90 | 37.76 | 65.2% |

| vehicle heading error | DAIR-V2X-I | TUMTraf |
|---|---|---|
| median (signed) | −0.2° | −0.2° |
| standard deviation | 12.4° | 24.0° |
| within ±5° | 88% | 28% |

The median is identical across domains, which excludes a coordinate or calibration error: the
bias is correct and the reliability is not. The error is multi-modal, clustering near +15…30°
and −30…−60° — consistent with a learned prior over road directions rather than random
degradation. The class pattern independently matches MS3D++'s observation that heading error
destroys IoU for elongated vehicles while symmetric classes tolerate it [1].

**Why it matters.** A missed detection is a failure mode downstream planners are built to
tolerate. A confident *wrong heading* is not: heading feeds motion prediction, so a correctly
located vehicle with a 25° heading error yields a predicted trajectory going somewhere the
vehicle is not. If fragility is concentrated, repair can be local and label-free; if diffuse,
retraining on labeled target data is the only option, which does not scale to per-intersection
deployment.

# C. Methodology and Why Innovative

**C.1 Per-component fragility profile.** Adapt the sub-task attribution protocol of monodle
[8]: substitute ground truth for one predicted quantity at a time — heading, center, size,
class — and re-measure AP. Applied both in-domain and cross-domain, the *difference* in each
substitution's effect attributes the drop to specific components. monodle applies this
in-domain to a monocular detector; applying it across a natural domain gap, to a LiDAR+camera
roadside detector, is what is new.

**C.2 Test the road-geometry hypothesis.** If heading rests on a learned road-angle prior, the
error clusters must align with the *source* intersection's lane bearings. This is directly
falsifiable, and is scheduled first because a null result redirects the work.

**C.3 Four label-free repairs, measured against an oracle.**

| intervention | supervision | precedent |
|---|---|---|
| Recalibrate INT8 ranges on unlabeled target frames | none — forward passes | untested in the verified literature |
| Adapt orientation head only, backbone frozen | pseudo-labels | — |
| Random object scaling at source pre-training | none — source-side | +27.19 AP₃D on car [4] |
| Local-structure input features | none — source-side | >21 mAP Waymo→KITTI [9] |

A supervised oracle establishes the recoverable ceiling so each repair is reported as
*fraction of gap closed*, the convention used by the self-training literature [3].

**C.4 Guard against the documented traps.** Checkpoints will be selected on a source-domain
validation split, never on target performance, because best-epoch selection on the target
leaks label information and inflates results [7]. Statistical Normalization will be included
as a *negative control* rather than a baseline to beat, since it is known to degrade transfer
when the size gap is small [3]. Per-class AP will be reported throughout, never a single
averaged mAP, because the class balance differs between the two domains.

**C.5 Compression as an axis, not the headline.** Each repair is evaluated at FP16 and INT8.
Preliminary data shows quantization adds 0.0° of heading error in-domain and +1.2°
out-of-domain; establishing whether that is real requires repeated calibration seeds and
per-class confidence intervals, which C.3 supplies.

**Why innovative.** Existing adaptation methods treat the detector as one object and ask how
much AP returns. This asks *which part broke*, then repairs that part. It also moves the
orientation question out of the vehicle-mounted, multi-frame setting where it was identified
and into the static, single-frame roadside setting where the motion cue that previously
rescued it does not exist.

# D. Milestones and Timeline

| period | milestone | deliverable |
|---|---|---|
| Sep–Oct 2026 | Lane-bearing correlation (C.2); second target domain converted | Hypothesis confirmed or refuted |
| Nov–Dec 2026 | Per-component fragility profile (C.1), two dataset pairs | Fragility table; figure set |
| Jan–Feb 2027 | Supervised oracle; repairs 1–2 with repeated seeds | Fraction-of-gap-closed per repair |
| Mar 2027 | Repairs 3–4; full FP16/INT8 matrix; Jetson latency for deployable repairs | Complete results |
| Apr 2027 | Writing; SJSU Research Showcase | Draft manuscript |
| May 2027 | Final report | Submitted by 30 May 2027 |

**Risk and contingency.** The oracle is the only step needing substantial GPU time; without
it, results are reported as absolute recovery rather than fraction-of-oracle — weaker but
publishable. If C.2 refutes the road-geometry hypothesis, C.1 and C.3 are unaffected.

# E. Anticipated Outcome

1. **A per-component fragility profile** for roadside 3D detection across two dataset pairs —
   attributing a cross-dataset drop to specific components rather than a single AP number.
2. **A measurement of how much of the gap each label-free repair recovers**, with confidence
   intervals, comparable to the fraction-of-gap convention in the adaptation literature.
3. **The first cross-dataset heading-error measurement for roadside sensors**, reported as a
   metric distinct from AP.
4. **An answer on quantization**: whether INT8 amplifies domain fragility, measured on a
   mechanism-level metric sensitive enough to resolve it.
5. **Released artifacts** — the TUMTraf→DAIR converter, the JetPack 7 deployment recipe and
   all evaluation code, already public at `github.com/henrytran412/God-eye`.

Target venues: SJSU Research Showcase; a workshop paper at CVPR, ICRA or IROS.

**Budget ($300).** Portable SSD for dataset storage (~$120); Jetson power-monitoring hardware
and cabling (~$80); remainder for dataset access and incidentals.

---

## References

1. Tsai, D., Berrio, J.S., Shan, M., Nebot, E., Worrall, S. *MS3D++: Ensemble of Experts for
   Multi-Source Unsupervised Domain Adaptation in 3D Object Detection.* IEEE T-IV, 2024.
   arXiv:2308.05988.
2. nuScenes detection benchmark — mAOE, mATE, mASE definitions. nuScenes devkit.
   github.com/nutonomy/nuscenes-devkit
3. Yang, J., Shi, S., Wang, Z., Li, H., Qi, X. *ST3D: Self-training for Unsupervised Domain
   Adaptation on 3D Object Detection.* CVPR 2021. arXiv:2103.05346.
4. Yang, J., Shi, S., Wang, Z., Li, H., Qi, X. *ST3D++: Denoised Self-training for
   Unsupervised Domain Adaptation on 3D Object Detection.* IEEE T-PAMI 2022.
   arXiv:2108.06682.
5. Cui, H., Chou, F.-C., Charland, J., Vallespi-Gonzalez, C., Djuric, N. *Uncertainty-Aware
   Vehicle Orientation Estimation for Joint Detection-Prediction Models.* 2020.
   arXiv:2011.03114.
6. Chandorkar, A. et al. *Comprehensive Robustness Analysis of LiDAR-based 3D Object Detection
   in Autonomous Driving.* 2026. arXiv:2607.02074.
7. Independent reproducibility analysis of ST3D self-training. 2024. arXiv:2408.12708.
8. Ma, X., Zhang, Y., Xu, D., Zhou, D., Yi, S., Li, H., Ouyang, W. *Delving into Localization
   Errors for Monocular 3D Object Detection.* CVPR 2021. arXiv:2103.16237.
9. Malić, D., Fruhwirth-Reisinger, C., Schulter, S., Possegger, H. *GBlobs: Explicit Local
   Structure via Gaussian Blobs for Improved Cross-Domain LiDAR-based 3D Object Detection.*
   CVPR 2025. arXiv:2503.08639.
10. Yu, H. et al. *DAIR-V2X: A Large-Scale Dataset for Vehicle-Infrastructure Cooperative 3D
    Object Detection.* CVPR 2022.
11. Zimmer, W. et al. *TUMTraf Intersection Dataset: All You Need for Urban 3D Camera-LiDAR
    Roadside Perception.* IEEE ITSC 2023.
12. NVIDIA. *CUDA-BEVFusion and CUDA-V2XFusion*, Lidar_AI_Solution.
    github.com/NVIDIA-AI-IOT/Lidar_AI_Solution
