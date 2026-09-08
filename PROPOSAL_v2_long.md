Thesis/Project Title (<10 words):

GhostGuard: Set-Conditioned Counterfactual Admission for Cooperative Perception

Synopsis of Proposed Research (<=250 words):

Cooperative perception lets connected vehicles share detections that reveal pedestrians and
vehicles hidden behind obstacles. The same channel admits delayed, misaligned, and deliberately
fabricated messages, which insert objects that are not there and can trigger emergency braking for
nothing. Existing defences decide what to trust using confidence, uncertainty, cross-agent
agreement, or sender reputation, and they score each message, feature, or sender independently.
All of these are proxies for whether a message is false, not for whether admitting it makes the
vehicle less safe. Those are different events. In a preliminary study where every message's
counterfactual effect is computable, they agree only 77% of the time: 29% of messages asserting
non-existent objects never change the fused output, while 21% of messages reporting real objects
increase safety risk. This project proposes GhostGuard, an object-level late-fusion admission
policy whose decision criterion is measured harm. Each candidate message is labelled by the change
it causes in a safety-weighted perception risk, and a policy is trained to imitate a counterfactual
oracle by scoring candidates conditioned on the messages already admitted rather than
independently. Conditioning is essential, not cosmetic: our preliminary gate rejects 94% of
fabricated messages from a naive attacker but only 45% once the attacker copies the metadata
statistics of honest senders, while the oracle is unaffected. Context is the one input a sender
cannot forge. Evaluation separates benign faults from single-source and coordinated fabrication and
reports preserved benefit alongside reduced harm.

Body of the Proposal

A. Introduction

Connected vehicles and roadside units can share what they detect, letting a vehicle "see" a child
stepping out from behind a parked truck that its own sensors cannot observe. The same link also
carries pose error, delay, association mistakes, sensor degradation, and fabricated reports, which
produce duplicate, displaced, missing, and phantom objects. Fusion or Confusion? demonstrates
phantom objects after V2X fusion, and RCP-Bench documents failures under environmental, sensor, and
temporal corruption [1], [2]. The question is therefore not how to fuse more data, but whether each
received object should be allowed to affect the vehicle's output at all.

That question hides a specific difficulty. Deciding admission requires knowing whether a message is
harmful, and harm is not the same event as falsehood. In a preliminary study using a controlled
synthetic sandbox, built so that the counterfactual effect of each message is exactly computable,
the two agree only 77% of the time. 28.9% of messages asserting objects that do not exist never
change the fused output, because they fall below the operating threshold or are absorbed by
non-maximum suppression, while 20.9% of messages reporting genuinely real objects raise risk
through staleness, pose error, or duplicate induction. A criterion built on detecting falsehood is
optimising a quantity measurably decorrelated from the one that matters.

A.1 Current Research

Existing methods can be organised by what they score, and each scores independently. Communication
selection: FPV-RCNN selects keypoint features with consensus-based localisation correction, and
FocalComm query-weights hard instances under bandwidth limits [3], [4]; SRA-CP triggers cooperation
when ego-side occlusion analysis finds a risk-relevant blind zone [5]. Uncertainty: evidential late
fusion and density-supervised uncertainty maps weight how strongly to trust incoming data [6], [7].
Senders: ROBOSAC uses ego consensus, MATE models agent trust over time, occupancy-consistency
checking targets fabrication, and CP-Guard and CP-uniGuard perform agent-level malicious detection
[8], [9], [10], [11], [12]; a provenance framework adds cryptography, reputation, and
accept/quarantine/reject thresholds [13].

What a defence must now survive has changed. MVIG learns vulnerability knowledge disclosed by
defensive systems and reduces defence success rates by up to 62% [14]. Adversarial Trust Poisoning
shows attackers accumulate reputation faster than defences revoke it and that coordinated vehicles
manufacture false majorities [15]. On evaluation, recent work argues fabrication attacks must be
measured by unsafe driving outcomes rather than detection evasion [16], and safety-aligned detection
metrics weight errors by consequence across single-vehicle and cooperative settings [17].

A.2 Limitations of Current Research

- Selection targets efficiency, salience, or coverage, not realised harm. FPV-RCNN is synthetic-only
  and models delay through message size; FocalComm is LiDAR-only [3], [4]. SRA-CP decides whether to
  request cooperation from ego-side occlusion risk, before any message arrives, and models no
  adversary [5]. None asks whether one admitted candidate raises risk.
- Uncertainty and agreement have measurable blind spots. In our preliminary tests an evidential
  weighting achieved the best average precision of any baseline in every condition while admitting
  every fabricated message, because it is a scoring rule and not a filter. Cross-agent agreement was
  the strongest defence against a single attacker and then accepted 100% of fabricated messages
  under two colluding senders, and it collapsed when senders withheld reports, because corroboration
  needs a second witness that withholding removes.
- Sender-level defences discard the occlusion benefit and rest on forgeable evidence. Muting senders
  wholesale killed honest messages with dishonest ones, cutting benefit retention to 0.41 under
  collusion; removing reputation history from our gate changed fabricated-message acceptance from
  0.037 to 0.035, and removing cross-agent agreement changed it to 0.034. Both signals were inert,
  and both are what an adversary controls. Trust poisoning and coordinated agreement defeat these
  families independently [15].
- Independent per-message scoring cannot be made adaptively robust. A gate reading confidence,
  claimed pose covariance, and message age rejected 94% of fabrications from a naive attacker and
  45% from one drawing those fields from the honest distribution; under adaptive collusion its
  advantage over using no cooperation at all disappeared. A counterfactual oracle conditioning on
  the admitted set was unaffected. This mirrors what MVIG reports against feature-level defences
  [14]: evaluating against a non-adaptive attacker measures the attacker's carelessness.
- Harm has become the currency for measuring attacks [16] and for scoring detection [17], but not
  for taking admission decisions.

A.3 Research Gap

No identified method decides whether to admit one cooperative object message by its
context-dependent change in a safety-weighted perception risk, conditioned on the messages already
admitted, and evaluated against an adaptive adversary. GhostGuard combines counterfactual harm
labelling, set-conditioned admission, a reported oracle upper bound, and separated benefit/harm
evaluation across benign faults, fabrication, and collusion. This is narrower than claiming the
first trustworthy or value-aware fusion system.

Research question: Does conditioning admission on the already-admitted set, supervised by
counterfactual perception harm, reduce cooperative harm under adaptive fabrication while preserving
detections of objects the vehicle cannot see itself?

B. Specific Proposed Research and Why Important/Exciting

GhostGuard operates at object-level late fusion, where decisions are interpretable and
counterfactual reruns are affordable; measured inference cost in the preliminary study was 1.3 ms
per frame against a 100 ms budget at 10 Hz. The hypothesis is that measured harm, evaluated in the
context of the current accepted set, predicts which messages to admit better than confidence,
uncertainty, agreement, or reputation, and that it does so because context is the one input a
sender cannot assert.

Two features make this more than an incremental defence. First, the counterfactual oracle is
constructible, so the achievable ceiling is knowable. Preliminary results place it at roughly half
the risk of the best learned policy, which quantifies how much of the problem remains open; no work
in this area reports such a bound. Second, the divergence between falsehood and harm is a
transferable finding: it implies that fabricated-message acceptance rate, the field's standard
headline metric, systematically misstates safety. We observed a policy admitting 2.8 times the
share of false messages achieving 19% lower safety risk. The aim is evidence for these claims, not
a universal safety guarantee.

C. Methodology and Why Innovative/Creative

Platform. OpenCOOD with PointPillars late fusion. Let F(S) be the fused output from admitted set S,
and R(F(S), y) a safety-weighted risk over missed-object, phantom-object, localisation, and
duplicate terms, with severity weighted by class, driving-corridor occupancy, and proximity,
following the consequence-weighted formulation of [17]. Association uses class-dependent centre
distance rather than a fixed overlap gate, because an overlap threshold is unreachable for a
pedestrian footprint under realistic localisation noise and would score a correct pedestrian
detection as a miss and a phantom simultaneously.

Label. The counterfactual utility of message m in context S is

    U(m | S) = R(F(S), y) - R(F(S ∪ {m}), y)

Positive, near-zero, and negative values mean helpful, redundant, and harmful in that context, a
property of a message-and-context pair rather than of a message; the three-way assignment shifted by
38% between reference contexts in our pilot, so the reference context is stated explicitly. The
primary label is U(m | ∅). A coalition-averaged variant is retained as an ablation, justified by one
failure it avoids: leave-one-out labelling is blind to duplicated fabrication, since removing one of
two identical fabricated reports changes nothing. The detector stays frozen initially, so labels
need only association and fusion reruns.

Policy. The core contribution is a policy scoring each candidate conditioned on the set already
admitted, trained by imitating a greedy counterfactual oracle: a small permutation-invariant
encoder over current cluster state plus per-candidate geometric features, applied sequentially or as
a joint set score. Features are partitioned into vehicle-verifiable and sender-asserted, and the
sender-asserted partition is ablated as standard practice, because that partition is what an
adaptive adversary controls. Reputation and cross-agent agreement are excluded from the primary
model and reported as a negative result. Actions are accept, soft-fuse, and reject.

Threat model. Up to k of n senders are malicious, may collude, may hold clean provenance records,
and may draw confidence, claimed covariance, and timestamps from the honest distribution.
Withholding is out of scope: admission control cannot recover information that never arrives.

Evaluation. Baselines are no-cooperation, naive late fusion, tuned confidence, cross-agent
agreement, evidential weighting, ROBOSAC, MATE where reproducible, occupancy consistency, and
CP-Guard/CP-uniGuard as agent-level references [8]-[12]. Comparisons are made at matched operating
points, since one threshold per method rewards whichever is tuned favourably. OPV2V and Adv-OPV2V
cover benign faults and fabrication, with an adaptive attacker after [14] as a primary condition;
V2V4Real or DAIR-V2X tests transfer. Metrics are safety risk with a reported weight sweep, 3D
average precision, recall of objects invisible to the ego vehicle, benefit and harm rates with harm
weighted by realised effect, fabricated-message acceptance, and latency. The oracle is reported in
every table. Distribution-free calibration of the action thresholds by conformal risk control [18]
is left to follow-on work; a pilot showed the target must be specified as excess risk over
no-cooperation, in the same currency as the training label, or the feasible set collapses to
admitting nothing.

D. Milestones and Timeline

- Fall 2026 (Sep-Oct): Reproduce OpenCOOD late fusion and all baselines on OPV2V. Finalise the risk
  function and the benign-fault and attack perturbation suite.
- Fall 2026 (Nov-Dec): Generate counterfactual labels and build the oracle. Establish the achievable
  harm floor and calibrate the harm estimate. Milestone: oracle and baseline comparison table.
- Spring 2027 (Jan-Feb): Train and ablate the set-conditioned policy against a per-message gate and
  against the sender-asserted feature partition. Milestone: policy that closes a measurable share of
  the oracle gap.
- Spring 2027 (Mar-Apr): Adaptive and colluding adversaries as primary conditions.
  Matched-operating-point evaluation, risk-weight sweep, latency profiling, and transfer to V2V4Real
  or DAIR-V2X.
- Spring 2027 (May): Final report approved by the faculty mentor by May 30, 2027, Student Research
  Showcase presentation, and a manuscript draft if results support the hypothesis.

E. Anticipated Outcome

Deliverables are reproducible code, a cooperative benefit/harm benchmark that reports an oracle
upper bound, quantitative ablations separating context-conditioning from feature engineering, a
mentor-approved final report, and a College of Engineering research showcase presentation. Two
results are expected to be of independent interest regardless of how the policy performs: the
measured divergence between falsehood and harm, which bears on how the field reports
fabricated-message acceptance, and the collapse of metadata-based gating under an adaptive attacker.
If the policy closes a substantial share of the oracle gap, a conference manuscript will be
prepared.

G. References

[1] Fusion or Confusion? Potential and Challenges in Fusion of Onboard Sensors and V2X Data in
Cooperative Perception, IEEE CSCN, 2025; arXiv:2607.05889.
[2] RCP-Bench: Benchmarking Robustness for Collaborative Perception Under Diverse Corruptions,
IEEE/CVF CVPR, 2025.
[3] Keypoints-Based Deep Feature Fusion for Cooperative Vehicle Detection of Autonomous Driving,
IEEE Robotics and Automation Letters, 2022, doi:10.1109/LRA.2022.3143299.
[4] FocalComm: Hard Instance-Aware Multi-Agent Perception, IEEE/CVF WACV, 2026.
[5] J. Liu et al., SRA-CP: Spontaneous Risk-Aware Selective Cooperative Perception,
arXiv:2511.17461, 2025.
[6] BELT-Fusion: Bayesian Evidential Late Fusion for Trustworthy V2X Perception, IEEE Transactions
on Intelligent Transportation Systems, 2025, doi:10.1109/TITS.2025.3625597.
[7] K. Yang et al., UECP: Uncertainty-Enhanced Collaborative Perception, arXiv:2606.23046, 2026.
[8] Among Us: Adversarially Robust Collaborative Perception by Consensus, IEEE/CVF ICCV, 2023.
[9] Security-Aware Sensor Fusion with MATE: The Multi-Agent Trust Estimator, arXiv:2503.04954, 2025.
[10] On Data Fabrication in Collaborative Vehicular Perception: Attacks and Countermeasures, USENIX
Security, 2024.
[11] CP-Guard: Malicious Agent Detection and Defense in Collaborative Bird's Eye View Perception,
arXiv:2412.12000, 2024.
[12] CP-uniGuard: A Unified, Probability-Agnostic, and Adaptive Framework for Malicious Agent
Detection and Defense in Multi-Agent Embodied Perception Systems, arXiv:2506.22890, 2025.
[13] Provenance-Aware Trust Framework for Autonomous Vehicles: A Generative AI-Inspired Hybrid
Approach for Decentralized Information Validation, IEEE COMPSAC, 2026.
[14] Y. Tao et al., Learning Mutual View Information Graph for Adaptive Adversarial Collaborative
Perception, IEEE/CVF CVPR, 2026; arXiv:2602.19596.
[15] Y. Liu, C. Wang, M. F. Li, Q. Zhang, Adversarial Trust Poisoning in Vehicular Collaborative
Perception, arXiv:2605.22122, 2026.
[16] Q. Zhang, R. Zhang, Z. M. Mao, From Stealthy Data Fabrication to Unsafe Driving: Realistic
Scenario Attacks on Collaborative Perception, arXiv:2605.01301, 2026.
[17] B. H.-C. Liao, C.-H. Cheng, H. Esen, A. Knoll, Safety-Aligned 3D Object Detection:
Single-Vehicle, Cooperative, and End-to-End Perspectives, arXiv:2604.03325, 2026.
[18] Conformal Risk Control, ICLR, 2024.
