Thesis/Project Title (<10 words):

GhostGuard: Set-Conditioned Counterfactual Admission for Cooperative Perception

Synopsis of Proposed Research (<=250 words):

Cooperative perception lets connected vehicles share detections that reveal pedestrians and
vehicles hidden behind obstacles. The same channel admits delayed, misaligned, and deliberately
fabricated messages, which insert objects that are not there and can trigger emergency braking for
nothing. Existing defences decide what to trust using confidence, uncertainty, cross-agent
agreement, or sender reputation, and each scores messages, features, or senders independently. All
are proxies for whether a message is false, not for whether admitting it makes the vehicle less
safe. Those are different events. In a preliminary simulation study where every message's
counterfactual effect is computable, they agree only 77% of the time: 29% of messages asserting non-existent
objects never change the fused output, while 21% of messages reporting real objects increase safety
risk. This project proposes GhostGuard, an object-level late-fusion admission policy whose decision
criterion is measured harm. Each candidate message is labelled by the change it causes in a
safety-weighted perception risk, and a policy is trained to imitate a counterfactual oracle by
scoring candidates conditioned on the messages already admitted rather than independently.
Conditioning is essential, not cosmetic: in the same simulation a per-message gate rejects 94% of
fabricated messages from a naive attacker but only 45% once the attacker copies the metadata
statistics of honest senders, while the oracle is unaffected. Context is the one input a sender cannot forge. Evaluation
separates benign faults from single-source and coordinated fabrication and reports preserved
benefit alongside reduced harm.

Body of the Proposal

A. Introduction

Connected vehicles and roadside units can share what they detect, letting a vehicle "see" a child
stepping out from behind a parked truck that its own sensors cannot observe. The same link carries
pose error, delay, association mistakes, sensor degradation, and fabricated reports, producing
duplicate, displaced, missing, and phantom objects. Fusion or Confusion? demonstrates phantom
objects after V2X fusion, and RCP-Bench documents failures under environmental, sensor, and temporal
corruption [1], [2]. The question is not how to fuse more data, but whether each received object
should affect the vehicle's output at all.

That question hides a difficulty. Admission requires knowing whether a message is harmful, and harm
is not the same event as falsehood. In a preliminary study using a controlled synthetic sandbox
built so that each message's counterfactual effect is exactly computable, the two agreed only 77% of
the time: 28.9% of messages asserting non-existent objects never changed the fused output, falling
below the operating threshold or absorbed by non-maximum suppression, while 20.9% of messages
reporting real objects raised risk through staleness, pose error, or duplicate induction. A
criterion built on detecting falsehood optimises a measurably different quantity.

A.1 Current Research

Existing methods can be organised by what they score, and each scores independently. Communication
selection: FPV-RCNN selects keypoint features with consensus localisation correction, FocalComm
query-weights hard instances under bandwidth limits, and SRA-CP triggers cooperation when ego-side
occlusion analysis finds a risk-relevant blind zone [3]-[5]. Uncertainty: evidential late fusion and
density-supervised uncertainty maps weight how strongly to trust incoming data [6], [7]. Senders:
ego consensus, temporal agent trust, occupancy-consistency checking, agent-level malicious
detection, and provenance frameworks with accept/quarantine/reject thresholds [8]-[12].

What a defence must survive has changed. MVIG learns vulnerability knowledge disclosed by defences
and cuts their success rates by up to 62% [13]; trust poisoning shows attackers accumulate
reputation faster than defences revoke it, and coordinated vehicles manufacture false majorities
[14]. On evaluation, fabrication is now argued to require measurement by unsafe driving outcomes
rather than detection evasion [15], and safety-aligned metrics weight detection errors by
consequence in cooperative settings [16].

A.2 Limitations of Current Research

- Selection targets efficiency, salience, or coverage, not realised harm. SRA-CP decides whether to
  request cooperation from ego-side occlusion risk, before any message arrives, and models no
  adversary [5]. None asks whether one admitted candidate raises risk.
- Uncertainty, agreement, and reputation have measurable blind spots. In our pilot, evidential
  weighting achieved the best average precision of any baseline in every condition while admitting
  every fabricated message, being a scoring rule and not a filter. Cross-agent agreement was the
  strongest defence against one attacker, then accepted 100% of fabricated messages under two
  colluding senders. Sender-level muting cut benefit retention to 0.41 under collusion. Removing
  reputation from our gate moved fabricated-message acceptance from 0.037 to 0.035 and removing
  agreement moved it to 0.034: both were inert, and both are what an adversary controls,
  consistent with [14].
- Independent per-message scoring cannot be made adaptively robust. A gate reading confidence,
  claimed covariance, and message age rejected 94% of fabrications from a naive attacker and 45%
  from one drawing those fields from the honest distribution, and under adaptive collusion its
  advantage over no cooperation disappeared. An oracle conditioning on the admitted set was
  unaffected, mirroring what [13] reports against feature-level defences.
- Harm has become the currency for measuring attacks [15] and scoring detection [16], but not for
  taking admission decisions.

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
counterfactual reruns are affordable; pilot inference cost was 1.3 ms per frame against a 100 ms
budget at 10 Hz. The hypothesis is that measured harm, evaluated in the context of the current
accepted set, predicts admission better than confidence, uncertainty, agreement, or reputation,
because context is the one input a sender cannot assert. Two features make this more than an
incremental defence. The counterfactual oracle is constructible, so the achievable ceiling is
knowable; pilot results place it near half the risk of the best learned policy, and no work in this
area reports such a bound. And the falsehood/harm divergence implies that fabricated-message
acceptance rate, the field's standard headline metric, misstates safety: in simulation a policy
admitting 2.8 times the share of false messages achieved 19% lower risk. The premise itself is
tested by a controlled ablation: the same architecture trained on a falsehood label against a harm
label, everything else fixed. That comparison is informative either way, since a negative result
would itself bear on an assumption the trust and provenance literature relies on.

C. Methodology and Why Innovative/Creative

Platform: OpenCOOD with PointPillars late fusion. Let F(S) be the fused output from admitted set S,
and R(F(S), y) a safety-weighted risk over missed-object, phantom-object, localisation, and
duplicate terms, severity-weighted by class, driving-corridor occupancy, and proximity, following
the consequence-weighted formulation of [16]. Association uses class-dependent centre distance,
because a fixed overlap gate is unreachable for a pedestrian footprint under realistic localisation
noise and would score a correct pedestrian detection as a miss and a phantom at once.

Label: the counterfactual utility of message m in context S is

    U(m | S) = R(F(S), y) - R(F(S ∪ {m}), y)

Positive, near-zero, and negative values mean helpful, redundant, and harmful in that context, a
property of a message-and-context pair; the three-way assignment shifted 38% between reference
contexts in our pilot, so the reference context is stated explicitly. The primary label is
U(m | ∅), with a coalition-averaged variant as an ablation, justified because leave-one-out
labelling is blind to duplicated fabrication. The detector stays frozen initially, so labels need
only association and fusion reruns.

Policy: the core contribution scores each candidate conditioned on the set already admitted, trained
by imitating a greedy counterfactual oracle, using a small permutation-invariant encoder over
current cluster state plus per-candidate geometric features. Features are partitioned into
vehicle-verifiable and sender-asserted, and the sender-asserted partition is ablated as standard
practice, since it is what an adaptive adversary controls. Actions are accept, soft-fuse, reject.
Threat model: up to k of n senders are malicious, may collude, may hold clean provenance, and may
draw confidence, covariance, and timestamps from the honest distribution; withholding is out of
scope, as admission control cannot recover information that never arrives.

Evaluation: baselines are no-cooperation, naive late fusion, tuned confidence, and the
uncertainty-, consensus-, occupancy- and agent-level families [6]-[12], compared at matched
operating points, since one threshold per method rewards whichever is tuned favourably. OPV2V and
Adv-OPV2V cover benign faults and fabrication, with an adaptive attacker after [13] as a primary
condition. Metrics are safety risk with a weight sweep, 3D
average precision, recall of objects invisible to the ego vehicle, benefit and harm rates with harm
weighted by realised effect, fabricated-message acceptance, and latency, with the oracle reported
throughout. Conformal threshold calibration [17] is left to follow-on work; a pilot showed its
target must be expressed as excess risk over no-cooperation or the feasible set collapses to
admitting nothing.

D. Milestones and Timeline

- Fall 2026 (Sep-Oct): reproduce OpenCOOD late fusion and all baselines on OPV2V; finalise the risk
  function and the benign-fault and attack perturbation suite.
- Fall 2026 (Nov-Dec): generate counterfactual labels, build the oracle, establish the achievable
  harm floor. Milestone: oracle and baseline comparison table.
- Spring 2027 (Jan-Feb): train and ablate the set-conditioned policy against a per-message gate and
  against the sender-asserted feature partition. Milestone: a measurable share of the oracle gap
  closed.
- Spring 2027 (Mar-Apr): adaptive and colluding adversaries as primary conditions;
  matched-operating-point evaluation, risk-weight sweep, and latency profiling. Stretch goal if the
  schedule permits: transfer to real V2V4Real or DAIR-V2X data.
- Spring 2027 (May): final report approved by the faculty mentor by May 30, 2027, and Student
  Research Showcase presentation.

E. Anticipated Outcome

Deliverables are reproducible code, a cooperative benefit/harm benchmark reporting an oracle upper
bound, ablations separating context-conditioning from feature engineering, a mentor-approved final
report, and a College of Engineering showcase presentation. Two results should be of independent
interest regardless of how the policy performs: the measured divergence between falsehood and harm,
which bears on how the field reports fabricated-message acceptance, and the collapse of
metadata-based gating under an adaptive attacker. If the policy closes a substantial share of the
oracle gap, a conference manuscript will be prepared.

G. References

[1] Fusion or Confusion? Fusion of Onboard Sensors and V2X Data in Cooperative Perception, IEEE
CSCN, 2025; arXiv:2607.05889.
[2] RCP-Bench: Benchmarking Robustness for Collaborative Perception Under Diverse Corruptions,
IEEE/CVF CVPR, 2025.
[3] Keypoints-Based Deep Feature Fusion for Cooperative Vehicle Detection, IEEE RA-L, 2022,
doi:10.1109/LRA.2022.3143299.
[4] FocalComm: Hard Instance-Aware Multi-Agent Perception, IEEE/CVF WACV, 2026.
[5] SRA-CP: Spontaneous Risk-Aware Selective Cooperative Perception, arXiv:2511.17461, 2025.
[6] BELT-Fusion: Bayesian Evidential Late Fusion for Trustworthy V2X Perception, IEEE T-ITS, 2025,
doi:10.1109/TITS.2025.3625597.
[7] UECP: Uncertainty-Enhanced Collaborative Perception, arXiv:2606.23046, 2026.
[8] Among Us: Adversarially Robust Collaborative Perception by Consensus, IEEE/CVF ICCV, 2023.
[9] Security-Aware Sensor Fusion with MATE: The Multi-Agent Trust Estimator, arXiv:2503.04954, 2025.
[10] On Data Fabrication in Collaborative Vehicular Perception, USENIX Security, 2024.
[11] CP-uniGuard: Malicious Agent Detection and Defense in Multi-Agent Perception,
arXiv:2506.22890, 2025.
[12] Provenance-Aware Trust Framework for Autonomous Vehicles, IEEE COMPSAC, 2026.
[13] Learning Mutual View Information Graph for Adaptive Adversarial Collaborative Perception,
IEEE/CVF CVPR, 2026; arXiv:2602.19596.
[14] Adversarial Trust Poisoning in Vehicular Collaborative Perception, arXiv:2605.22122, 2026.
[15] From Stealthy Data Fabrication to Unsafe Driving: Realistic Scenario Attacks on Collaborative
Perception, arXiv:2605.01301, 2026.
[16] Safety-Aligned 3D Object Detection: Single-Vehicle, Cooperative, and End-to-End Perspectives,
arXiv:2604.03325, 2026.
[17] Conformal Risk Control, ICLR, 2024.
