# Davidson Student Scholars Proposal — AY2026–27

**Name:** Tran, Thuc Bao · **Email:** thucbao.tran@sjsu.edu
**Department:** Computer Engineering, College of Engineering
**Faculty Mentor:** Prof. Kaikai Liu
**Track:** Undergraduate Research Project ($1,500)
**Period:** Fall 2026 – Spring 2027 · Final report due 30 May 2027

**Title:** Diagnosing and Repairing Orientation Failure in Roadside 3D Detection

---

## Synopsis of Proposed Research (243 words)

Roadside 3D object detectors are trained at one intersection and deployed at
another. Published accuracy is measured on the training distribution; deployment is
not. Prior work establishes that this costs a great deal — a 70–90% drop in
detection rate across LiDAR, geography and weather [Tsai 2023] — but treats the
loss as a single number and attempts to close it wholesale.

Preliminary measurements on a Jetson Orin Nano suggest the loss is not uniform.
Evaluating NVIDIA's pretrained V2XFusion zero-shot from DAIR-V2X-I (Beijing) to
TUMTraf Intersection (Munich), detection and position largely survive, while
heading estimation collapses: vehicles within ±5° of true heading fall from 88% to
28%, with the median error unchanged at −0.2° in both domains. Because a ~20°
heading error on a 4.1 × 1.9 m box clears IoU 0.25 but not IoU 0.5, this single
mode explains why Car accuracy falls 69.70 → 0.13 AP while Pedestrian and Cyclist
retain 56% and 65%.

This project will test whether domain fragility concentrates in specific network
components, and whether the fragile component can be repaired without target-domain
labels. Three interventions will be evaluated against a supervised oracle:
recalibrating INT8 quantization ranges on unlabeled target data, adapting only the
orientation head, and replacing global coordinates with local-structure features.
The deliverable is a per-component fragility profile and a measurement of how much
of the gap each label-free repair recovers.

---

# A. Introduction

## A.1 Current Research

Three research communities each measure part of the deployment problem, and none
measures the intersection.

**Efficiency and deployment.** NVIDIA publishes compressed accuracy for
CUDA-BEVFusion and V2XFusion on the datasets those models were trained on. Their
V2XFusion table reports INT8 post-training quantization costing essentially nothing
in-domain on DAIR-V2X-I.

**Domain generalization.** ST3D [Yang, CVPR 2021] and ST3D++ [Yang 2021] adapt
detectors to a target domain using only unlabeled target point clouds. MS3D++
[Tsai 2023] reports that deployment in an unfamiliar domain produces "a significant
70–90% drop in detection rate due to variations in lidar, geography, or weather."
MLC-Net [Luo 2021] achieves unsupervised adaptation from source annotations alone.
GBlobs [Malić, CVPR 2025] traces cross-domain failure to input representation:
"over-reliance on these global geometric features can cause 3D detectors to
prioritize object location and absolute position, resulting in poor cross-domain
performance," and recovers >21 mAP on Waymo→KITTI by encoding local neighborhoods
instead.

**Orientation estimation.** Cui et al. [2020] define half- and full-range
orientation error, HOE = |(θ − θ̂) mod 180°| and FOE = |(θ − θ̂) mod 360°|, and
report them separately from AP. They identify why heading is hard: "the front and
back of a vehicle may not be easily distinguishable from the LiDAR point cloud,"
and detectors therefore lean on motion — parked vehicles fail because they "have no
moving trajectory predictions that could be used to reliably infer the
orientations."

## A.2 Limitations of Current Research

**Every result above is vehicle-mounted.** Waymo, KITTI, nuScenes, Lyft and ONCE
are all ego-vehicle datasets. A roadside sensor is static, has no ego-motion, and
in the deployed single-frame configuration has no trajectory cue at all — precisely
the cue Cui et al. show detectors depend on for heading.

**Domain gaps are reported as one number.** ST3D, MS3D++ and MLC-Net report AP
recovered. None reports which *component* of the network failed, so it is not
known whether the loss is diffuse or concentrated — and therefore not known whether
a targeted, cheap repair is even possible.

**Compression and domain shift are never measured together.** Quantized accuracy is
reported in-domain; cross-domain accuracy is reported at full precision on
datacenter GPUs. PTQ derives its numeric ranges from a calibration set drawn from
the *source* domain, so there is a specific reason to expect an interaction, and
no published measurement of it.

## A.3 Research Gap

No published work measures **per-component** domain fragility for roadside 3D
detection, or tests whether the fragile component can be repaired without target
labels. Cui et al. show heading is under-determined by LiDAR appearance in the
vehicle-mounted case; whether a static roadside detector substitutes a *scene
geometry* prior for the motion cue it lacks is untested.

# B. Specific Proposed Research and Why Important

**Question.** Does domain fragility in roadside 3D perception concentrate in
specific network components, and can the fragile component be repaired using only
unlabeled target data?

**Preliminary evidence (already collected).** A full pipeline was built and
validated on a borrowed Jetson Orin Nano. It reproduces NVIDIA's published
DAIR-V2X-I accuracy to within 0.02–0.04 AP on Car and Pedestrian, which
establishes that subsequent measurements are trustworthy rather than artifacts.
Zero-shot transfer to TUMTraf Intersection (2,160 frames) then gives:

| 3D AP, moderate | DAIR-V2X-I | TUMTraf | retained |
|---|---|---|---|
| Car @ IoU 0.5 | 69.70 | 0.13 | 0.2% |
| Pedestrian @ IoU 0.25 | 49.39 | 27.61 | 55.9% |
| Cyclist @ IoU 0.25 | 57.90 | 37.76 | 65.2% |

| heading error, vehicles | DAIR-V2X-I | TUMTraf |
|---|---|---|
| median (signed) | −0.2° | −0.2° |
| standard deviation | 12.4° | 24.0° |
| within ±5° | 88% | 28% |

The median is identical across domains, which excludes a coordinate or calibration
error — the bias is correct and the reliability is not. The error is also
multi-modal, clustering near +15…30° and −30…−60°, consistent with a learned prior
over road directions rather than random degradation.

**Why it matters.** A missed detection is a failure mode downstream planners are
built to tolerate. A confident *wrong heading* is not: heading feeds motion
prediction, so a correctly located vehicle with a 25° heading error yields a
predicted trajectory that goes somewhere the vehicle does not. The failure is
invisible to any metric that does not isolate orientation, and mAP at loose IoU
hides it entirely. If fragility is concentrated, repair can be cheap and local; if
diffuse, retraining on labeled target data is the only option, which does not scale
to per-intersection deployment.

# C. Methodology and Why Innovative

**C.1 Per-component fragility profile.** Adapt the sub-task error decomposition of
MonoDLE [Ma, CVPR 2021]: substitute ground truth for one predicted quantity at a
time — heading, center, size, class — and re-measure AP. Applied in-domain and
cross-domain, the *difference* in each substitution's effect attributes the
cross-dataset drop to specific components. MonoDLE applies this protocol in-domain
to a monocular detector; applying it across a domain gap, to a LiDAR+camera
roadside detector, is new.

**C.2 Test the scene-geometry hypothesis.** If heading rests on a learned road-angle
prior, the multi-modal error clusters must align with the *source* intersection's
lane headings. This is directly falsifiable: extract lane bearings for both
intersections and correlate against the error distribution. A null result refutes
the hypothesis and redirects the work, which is why it is scheduled first.

**C.3 Three label-free repairs, measured against an oracle.**

| intervention | supervision needed | cost |
|---|---|---|
| Recalibrate INT8 ranges on unlabeled target frames | none — forward passes only | minutes |
| Adapt orientation head only, backbone frozen | pseudo-labels, self-training | hours |
| Local-structure input features (after GBlobs) | none — source-side change | retrain source |

A supervised oracle — fine-tuned on labeled target data — establishes the
recoverable ceiling, so each repair is reported as a *fraction of the gap closed*,
the convention used by ST3D and MS3D++, rather than as a raw delta.

**C.4 Compression as an axis, not the headline.** Each repair is evaluated at FP16
and INT8. Preliminary data shows quantization adds 0.0° of heading error in-domain
and +1.2° out-of-domain; whether that is real requires repeated calibration seeds
and per-class confidence intervals, which C.3 provides for free.

**Why innovative.** Existing adaptation methods treat the detector as one object
and ask how much AP returns. This project asks *which part broke*, then repairs
that part. It also moves the orientation question from the vehicle-mounted,
multi-frame setting where it was first identified into the static, single-frame
roadside setting where the motion cue that previously rescued it does not exist.

# D. Milestones and Timeline

| period | milestone | deliverable |
|---|---|---|
| Sep–Oct 2026 | Lane-bearing correlation (C.2); second target domain (Rope3D or V2X-Seq-SPD) converted | Hypothesis confirmed or refuted |
| Nov–Dec 2026 | Per-component fragility profile (C.1), in- and cross-domain, two dataset pairs | Fragility table; first draft figure set |
| Jan–Feb 2027 | Supervised oracle; repairs 1 and 2 (C.3) with repeated seeds | Fraction-of-gap-closed for each |
| Mar 2027 | Repair 3; full FP16/INT8 matrix; Jetson latency for any deployable repair | Complete results |
| Apr 2027 | Writing; SJSU Research Showcase | Draft manuscript |
| May 2027 | Final report | Submitted by 30 May 2027 |

**Risk and contingency.** The oracle is the only step requiring substantial GPU
time. If unavailable, results are reported as absolute recovery rather than
fraction-of-oracle — weaker, but publishable. If C.2 refutes the scene-geometry
hypothesis, C.1 and C.3 are unaffected: the fragility profile and the repairs stand
on their own.

# E. Anticipated Outcome

1. **A per-component fragility profile** for roadside 3D detection across two
   dataset pairs — the first attribution of a cross-dataset drop to specific network
   components rather than a single AP number.
2. **A measurement of how much of the gap each label-free repair recovers**, with
   confidence intervals, directly comparable to the fraction-of-gap convention used
   by ST3D and MS3D++.
3. **An answer on quantization**: whether INT8 amplifies domain fragility, measured
   on a mechanism-level metric sensitive enough to resolve it.
4. **Released artifacts**: the TUMTraf→DAIR converter, the JetPack 7 deployment
   recipe, and all evaluation code, already public at
   `github.com/henrytran412/God-eye`.

Target venues: SJSU Research Showcase; a workshop paper at CVPR, ICRA or IROS.

**Budget ($300 implementation).** Portable SSD for dataset storage (~$120);
Jetson power monitoring and cabling (~$80); remaining for dataset access and
incidental hardware.

---

## References

1. Tsai, D., Berrio, J.S., Shan, M., Nebot, E., Worrall, S. *MS3D++: Ensemble of
   Experts for Multi-Source Unsupervised Domain Adaptation in 3D Object Detection.*
   arXiv:2308.05988, 2023.
2. Cui, H., Chou, F.-C., Charland, J., Vallespi-Gonzalez, C., Djuric, N.
   *Uncertainty-Aware Vehicle Orientation Estimation for Joint Detection-Prediction
   Models.* arXiv:2011.03114, 2020.
3. Malić, D., Fruhwirth-Reisinger, C., Schulter, S., Possegger, H. *GBlobs: Explicit
   Local Structure via Gaussian Blobs for Improved Cross-Domain LiDAR-based 3D
   Object Detection.* CVPR 2025. arXiv:2503.08639.
4. Luo, Z., Cai, Z., Zhou, C., Zhang, G., Zhao, H., Yi, S., Lu, S., Li, H., Zhang,
   S., Liu, Z. *Unsupervised Domain Adaptive 3D Detection with Multi-Level
   Consistency (MLC-Net).* arXiv:2107.11355, 2021.
5. Yang, J., Shi, S., Wang, Z., Li, H., Qi, X. *ST3D: Self-training for Unsupervised
   Domain Adaptation on 3D Object Detection.* CVPR 2021. arXiv:2103.05346.
6. Yang, J. et al. *ST3D++: Denoised Self-training for Unsupervised Domain
   Adaptation on 3D Object Detection.* arXiv:2108.06682, 2021.
7. Ma, X., Zhang, Y., Xu, D., Zhou, D., Yi, S., Li, H., Ouyang, W. *Delving into
   Localization Errors for Monocular 3D Object Detection (MonoDLE).* CVPR 2021.
   arXiv:2103.16237.
8. Yang, L. et al. *BEVHeight: A Robust Framework for Vision-based Roadside 3D
   Object Detection.* CVPR 2023.
9. Yu, H. et al. *DAIR-V2X: A Large-Scale Dataset for Vehicle-Infrastructure
   Cooperative 3D Object Detection.* CVPR 2022.
10. Zimmer, W. et al. *TUMTraf Intersection Dataset: All You Need for
    Urban 3D Camera-LiDAR Roadside Perception.* IEEE ITSC 2023.
11. NVIDIA. *CUDA-BEVFusion and CUDA-V2XFusion*, Lidar_AI_Solution.
    github.com/NVIDIA-AI-IOT/Lidar_AI_Solution.
