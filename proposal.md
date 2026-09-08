Thesis/Project Title (<10 words):

GhostGuard: Counterfactual Risk-Calibrated Cooperative Perception

Synopsis of Proposed Research (<=250 words):

Cooperative  perception  allows  connected  vehicles  and  roadside  units  to  share  detections  that
reveal  objects  outside  an  ego  vehicle's  field  of  view.  However,  delayed,  misaligned,  uncertain,  or
fabricated  messages  can  also  introduce  duplicate  detections  and  false-positive  ghost  objects.  Current
research improves communication efficiency, hard-object coverage, uncertainty weighting, consensus, or
sender  trust.  These  signals  are  useful  but  indirect:  they  do  not  measure  whether  admitting  one  object
message actually makes the ego vehicle's final perception safer. A confident, provenance-valid false box
may  be  harmful,  while  an  uncertain  remote-only  pedestrian  may  be  valuable.  This  project  proposes
GhostGuard,  a  late-fusion  framework  that  learns  the  counterfactual  marginal  utility  of  each  object
message.  During  training,  messages  will  be  added  to  sampled  message  subsets  and  labeled  by  the
resulting  change  in  a  safety-weighted  perception  risk.  A  lightweight  gate  will  use  detector,  geometric,
temporal,  and  cross-agent  evidence  to accept, soft-fuse, quarantine, or reject each candidate. Conformal
risk  calibration  will  define  an  abstention  region  when  evidence  is insufficient. Evaluation will separate
benign  faults  from  fabricated  messages  and  will  measure  both  harm  reduction  and  preservation  of
remote-only detections.

Body of the Proposal

A. Introduction

Cooperative perception reveals vehicles and vulnerable road users hidden by occlusion or
distance. Yet pose error, delay, association mistakes, sensor degradation, and fabricated reports can create
duplicates, displacement, misses, or ghost objects. Fusion or Confusion? demonstrates ghosts after V2X
fusion, and RCP-Bench documents failures under environmental, sensor, and temporal corruption [8], [9].
The central question is not how to fuse more data, but whether each received object should affect the ego
output.

A.1 Current Research

FPV-RCNN selects 3D keypoint features and applies maximum-consensus localization correction

[12]; FocalComm mines hard instances and query-weights exchanged features, improving compressed
pedestrian detection [13]. They show that selective communication can preserve useful evidence under
bandwidth limits.

Reliability methods estimate how strongly to trust data: BELT uncertainty, CoDynTrust
asynchronous-region uncertainty, UECP LiDAR-density uncertainty, and CoDS inter-agent disagreement
[1]-[4]. ROBOSAC uses ego consensus; MATE models agent/track trust over time; and Collaborative
Anomaly Detection checks cross-vehicle occupancy consistency against fabrication [5]-[7].

Adjacent work adds two relevant ideas. VGMR uses cross-modal agreement and discrepancy for

context-conditioned pre-fusion refinement [14]. A provenance-aware AV framework combines
cryptography, reputation, a transformer, and accept/quarantine/reject thresholds [15]. These establish that
generic value gating and AV-message abstention are not new.

A.2 Limitations of Current Research

·   Selection is optimized for efficiency or salience, not realized harm. FPV-RCNN is
synthetic-only and represents delay through message size; FocalComm is LiDAR-only and leaves

adverse weather, multimodal fusion, and convergence analysis open [12], [13]. Both optimize
compact or hard-instance features, not whether one candidate increases ego risk; fabricated-message
tests are outside their reported evaluations.
·   Uncertainty, agreement, and sender trust remain proxy signals. A confident fabricated box may
harm, while a low-agreement remote-only pedestrian may help. Coordinated attackers can agree, and
defenses requiring ego or benign-agent confirmation may discard the occlusion benefit [1]-[7].
·   Existing contextual value estimation is too coarse for object messages. VGMR pools modality
summaries, which its authors note may miss localized conflicts such as occlusion or frame drops; it is
evaluated on non-driving tasks and controlled corruptions [14]. It neither labels individual object
messages counterfactually nor calibrates perception harm.
·   Existing quarantine decisions do not measure perception utility. The provenance framework
uses engineered synthetic records without temporal correlations, reports a 21.67% malicious-update
miss rate in its test setting, and leaves adaptive attacks and distribution shift open [15]. Its fixed
thresholds judge provenance/update records, not the change an object report causes in detection risk.

A.3 Research Gap

The gap is therefore specific: no identified method labels one cooperative object message by its

context-dependent marginal change in ego perception risk, then calibrates an abstaining policy against
that harm. GhostGuard combines coalition-sampled counterfactual utility, object-level selective fusion,
conformal risk control, and separate benefit/harm evaluation across benign faults and fabrication. This is
narrower than claiming the first trustworthy, value-aware, or abstaining fusion system.

Research question: Can message-level marginal utility reduce cooperative harm while preserving
valuable remote-only detections?

B. Specific Proposed Research and Why Important/Exciting

GhostGuard begins at object-level late fusion, where decisions are interpretable and
counterfactual reruns are manageable. It will classify each candidate as helpful, redundant, harmful, or
unresolved, then accept, soft-fuse, quarantine, or reject it. The hypothesis is that measured safety-risk
change predicts harm better than confidence, agreement, or reputation alone. The aim is evidence for this
hypothesis, not a universal safety guarantee. MOT-CUP already applies conformal uncertainty to
cooperative tracking [10]; GhostGuard contributes the complete message-utility and calibrated-harm
pipeline.

C. Methodology and Why Innovative/Creative

OpenCOOD with PointPillars late fusion will serve as the initial platform. Let F(S) be the fused

output from message set S, and let R(F(S), y) combine missed-object, ghost-object, localization,
duplicate, and driving-corridor losses.

U(m | S) = R(F(S), y) - R(F(S ∪ {m}), y)
Positive, near-zero, and negative utility indicate helpful, redundant, and harmful messages.

Because interactions matter, training samples coalitions and estimates U(m) = E_S[U(m | S)], a
Shapley-inspired approximation rather than exact Shapley value or causal identification. The detector
stays frozen initially; labels require only association and fusion reruns.

A lightweight gate predicts utility, harm probability, and uncertainty from confidence,

class/size/range, age, pose uncertainty, association residuals, agreement, temporal persistence, path
relevance, and optional sender provenance or history. Metadata is not assumed trustworthy. Actions are

accept, soft-fuse, quarantine for temporal confirmation, or reject; quarantine protects unsupported but real
remote-only objects.

Conformal risk control [11] will calibrate nested action thresholds against cooperative harm on

held-out data; risk-coverage will also be tested under shift. Baselines are ego-only, naive late fusion,
confidence/geometry, BELT-Fusion, ROBOSAC, MATE when reproducible, and CAD.
OPV2V/Adv-OPV2V cover benign faults and spoofing/removal; V2V4Real or DAIR-V2X tests transfer.
Metrics are 3D AP, remote-only recall, Benefit/Harm Rates, malicious-message acceptance,
risk-coverage, bytes, and latency.

D. Milestones and Timeline

·   Months 1-2: Reproduce late fusion/baselines; finalize risk and perturbations.
·   Months 3-5: Generate coalition labels; train and ablate the utility gate.
·   Months 6-8: Calibrate actions; evaluate benign faults and fabrication attacks.
·   Months 9-12: Test real data, profile latency, and complete the report, presentation, and manuscript
draft.

E. Anticipated Outcome

Deliverables are reproducible code, a cooperative benefit/harm benchmark, quantitative ablations,

an adviser-approved report, and a CoE/SJSU presentation. If results support the hypothesis, a manuscript
will also be prepared.

G. References

[1] BELT-Fusion: Bayesian Evidential Late Fusion for Trustworthy V2X Perception, IEEE
Transactions on Intelligent Transportation Systems, 2025, doi:10.1109/TITS.2025.3625597.
[2] CoDynTrust: Robust Asynchronous Collaborative Perception via Dynamic Feature Trust
Modulus, IEEE ICRA, 2025, doi:10.1109/ICRA55743.2025.11127779.
[3] UECP: Uncertainty-Enhanced Collaborative Perception, accepted ECCV 2026;
arXiv:2606.23046.
[4] CoDS: Robust Collaborative Perception via Expert-driven Detection and BEV Segmentation,
ACM Multimedia 2026, forthcoming, doi:10.1145/3767308.3835282.
[5] Among Us: Adversarially Robust Collaborative Perception by Consensus, IEEE/CVF ICCV,
2023.
[6] Security-Aware Sensor Fusion with MATE: The Multi-Agent Trust Estimator, arXiv preprint
arXiv:2503.04954, 2025.
[7] On Data Fabrication in Collaborative Vehicular Perception: Attacks and Countermeasures,
USENIX Security, 2024.
[8] RCP-Bench: Benchmarking Robustness for Collaborative Perception Under Diverse Corruptions,
IEEE/CVF CVPR, 2025.
[9] Fusion or Confusion? Potential and Challenges in Fusion of Onboard Sensors and V2X Data in
Cooperative Perception, IEEE CSCN, 2025; arXiv:2607.05889.
[10] Collaborative Multi-Object Tracking With Conformal Uncertainty Propagation, IEEE Robotics
and Automation Letters, 2024.
[11] Conformal Risk Control, ICLR, 2024.

[12] Keypoints-Based Deep Feature Fusion for Cooperative Vehicle Detection of Autonomous
Driving, IEEE Robotics and Automation Letters, 2022, doi:10.1109/LRA.2022.3143299.
[13] FocalComm: Hard Instance-Aware Multi-Agent Perception, IEEE/CVF WACV, 2026.
[14] Before Fusion, Ask What to Keep: Contextual Calibration of Multimodal Signals, arXiv preprint
arXiv:2606.02679, 2026.
[15] Provenance-Aware Trust Framework for Autonomous Vehicles: A Generative AI-Inspired
Hybrid Approach for Decentralized Information Validation, IEEE COMPSAC, 2026.

