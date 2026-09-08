# GhostGuard — baseline results and revised direction

**For:** thesis advisor meeting · **From:** Thuc Bao Tran · **Date:** 6 September 2026
**Supporting material:** `REVIEW.md` (full audit), `PROPOSAL_v2.md` (rewritten proposal),
`results/` (all CSVs and the run log), `code/` (implementation)

---

## Bottom line

I implemented the baselines first, as you suggested. The **premise of GhostGuard survived
testing and got stronger** — I can now put a number on it instead of arguing it. The
**mechanism did not survive intact**: the headline anti-fabrication result turned out to
depend on the attacker announcing itself through metadata, and the conformal-risk-control
layer has no useful feasible solution as I specified it.

The experiments also pointed at a better mechanism, and a literature check confirms the
field moved in the same direction over the last twelve months. I would like to change the
core of the method and narrow the claims. Details below; two decisions I need from you at
the end.

---

## 1. What I built, and what it is not

No GPU is available on my machine and OPV2V is not downloaded, so this is **not** a
benchmark reproduction. I built a controlled cooperative-perception sandbox instead — ego
plus three CAVs on a 4-lane road, real line-of-sight occlusion, range-dependent detection
and localisation noise, honest clutter, sender pose error, latency, sensor degradation, and
four attack families. The point of a sandbox is that the **causal ground truth is known**:
for every message I know which real object it refers to, whether the ego could *ever* have
seen that object, and whether the sender fabricated it.

That is what makes it possible to ask whether the decision rule is *well-posed*, which is a
different question from how it scores on a leaderboard. Scale: 31,082 counterfactually
labelled messages for training, 110 scenarios per test condition across five conditions.
**Read the signs, orderings and failure modes; the absolute values are sandbox-specific.**

---

## 2. Baseline strengths and weaknesses

All nine baselines from the proposal are implemented. Mean safety risk `R` (lower better):

| Policy | Benign | Fabrication | Collusion | Withholding | Degraded |
|---|---|---|---|---|---|
| Ego-only | 12.05 | 12.75 | 11.86 | 11.92 | **12.48** |
| Naive late fusion | 9.49 | 15.74 | 15.20 | 11.33 | 18.31 |
| Confidence 0.5 | 8.05 | 14.32 | 13.82 | 10.06 | 16.02 |
| Geometric consensus | 9.03 | 9.82 | 14.89 | 11.71 | 12.58 |
| BELT-style evidential | 7.36 | 13.57 | 13.22 | 9.61 | 14.04 |
| CAD-style occupancy | 8.86 | 11.73 | **10.95** | 10.71 | 15.41 |
| ROBOSAC-style | 9.36 | 11.55 | 11.56 | 10.98 | 14.07 |
| MATE-style trust | 9.36 | 12.18 | 12.25 | 10.95 | 14.29 |
| **Utility gate (ours)** | **6.50** | **7.30** | **6.99** | **8.95** | 12.52 |
| Counterfactual oracle | 4.30 | 4.78 | 4.49 | 7.40 | 8.64 |

Each baseline family has a **characteristic failure**, and naming them is more useful than
the aggregate numbers:

**Confidence thresholding** — *strongest in benign traffic*, and it beats our gate there on
benefit kept per unit of harm. But **100% of fabricated messages pass** under both attacks,
because a spoofer simply asserts high confidence. Confidence is a detector-internal quantity
and carries no information about honesty.

**Geometric consensus** — best baseline under single-source fabrication (`R` 9.82, 5.6%
malicious acceptance), then **fails completely under collusion: 100% malicious acceptance**,
`R` 14.89. Two attackers manufacture their own corroboration. It also collapses under
withholding — remote-only recall 0.003, benefit rate 0.011 — because corroboration requires
a second witness and withholding removes it. A defense that needs a second witness inherits
a second attack surface.

**Evidential / uncertainty weighting (BELT, UECP family)** — the **best AP of any baseline in
every condition** (0.731 benign, 0.605 under fabrication). But it is a *scoring* method, not
a defense: it admits everything with a weight, so harm rate and malicious acceptance are
1.000 throughout. Excellent as a fusion component, not a filter.

**Occupancy / free-space consistency (CAD family)** — the **most stable benefit preservation**
of all baselines (0.92–0.94 in every condition) and the best baseline under collusion. But
42–46% of fabricated messages pass, because an attacker placing a box in genuinely occluded
space is unfalsifiable from the ego's viewpoint.

**Sender-level attestation and reputation (ROBOSAC, MATE family)** — lowest malicious
acceptance among prior art (20–36%), but they mute senders wholesale, so honest messages die
with the dishonest ones: benefit drops to 0.413 under collusion. And in my feature ablation,
**reputation history contributed nothing measurable** — removing it changed malicious
acceptance from 0.037 to 0.035.

**Everything fails under heavy sensor degradation.** Only ego-only (12.48) is competitive;
naive fusion reaches 18.31. When most senders are degraded, cooperation stops paying and no
admission policy fixes it. Worth reporting honestly as a limit.

---

## 3. Where the GhostGuard idea wins

**The premise, measured.** Over 16,443 messages, "this message is false" and "this message is
harmful" agree only **77%** of the time:

- **28.9%** of messages asserting non-existent objects cause no measurable harm. Among
  low-confidence ones, **99.9%** never clear the fused operating threshold at all.
- **20.9%** of messages reporting genuinely real objects *are* harmful — stale,
  pose-shifted, or duplicate-inducing.

This is the strongest thing the project has, and it is a direct empirical refutation of the
assumption under the whole trust/provenance/consensus literature. It belongs in the
introduction as a result, not an intuition.

**The gate delivers on it.** Under fabrication: `R` 7.30 against 9.82 for the best baseline
and 15.74 for naive fusion; 5.2% malicious acceptance against 46% (occupancy), 26%
(ROBOSAC-style), 36% (MATE-style), 100% (confidence). It also has the **best AP of any
non-oracle policy under attack** (0.681 vs 0.605 for the next best).

---

## 4. What the data says is wrong with the method as written

### 4.1 The anti-fabrication number is an artifact of a lazy attacker

The feature ablation shows the gate's resistance rests on exactly three fields — confidence,
claimed pose covariance, message age — **all of which the sender asserts and an adversary
sets freely**. Reputation and cross-agent agreement contribute nothing.

So I built an adaptive attacker that samples those three from the benign true-positive
distribution instead of shouting. Malicious acceptance:

| Gate | Fabrication | …adaptive | Collusion | …adaptive |
|---|---|---|---|---|
| Trained on naive attacks | 0.060 | **0.553** | 0.205 | **0.780** |
| Retrained on adaptive | 0.449 | 0.188 | 0.964 | 0.709 |
| Retrained, geometry only | 0.347 | 0.391 | 0.453 | 0.430 |
| Counterfactual oracle | 0.011 | 0.016 | 0.006 | 0.006 |

**6% becomes 55%.** Under adaptive collusion the gate's advantage over ego-only nearly
vanishes (`R` 12.14 vs 12.43). Retraining helps but does not recover it.

**The oracle stays near 1% in every column.** The information needed to reject these
messages exists — it lives in the *context* of what the fused output would become, not in
the per-message feature vector.

### 4.2 Per-message scoring leaves most of the gain on the table

The gap between the gate (`R` 6.5–7.3) and the greedy counterfactual oracle (`R` 4.3–4.8) is
**wider than the gap between the gate and every baseline combined**. The oracle differs in
one respect only: it decides conditioned on what it has already admitted.

Supporting this, `E_S[U]` correlates with the context-free `U(m|∅)` at ρ = 0.90 with **95.5%**
three-class agreement — the marginalised per-message label is very nearly a context-free
label, and context is exactly what the oracle exploits.

### 4.3 Conformal risk control, as specified, has no useful solution

For **any α ≤ 0.20 the only feasible threshold rejects every message** — the guarantee holds
perfectly and cooperative perception is switched off (benefit rate 0.000). The achievable
harm floor is 0.286, so promising 5% or 10% is infeasible. Worse, the same gate scores `R`
6.50 hand-tuned and **10.60** CRC-calibrated: the calibration makes it worse than no
calibration.

Three separable causes: the target is absolute rather than excess-over-ego-only; the
conformal loss and the training label are different events (the same 77% disagreement); and
`p̂_harm` is non-monotone exactly where CRC operates — the bottom bin predicts 0.25% harm and
is 30.4% ghosts.

---

## 5. What the field did while I was writing the proposal

I checked the literature to Sept 2026. Three shifts, and **all three support the change of
direction rather than undermining it**:

1. **Adaptive attackers are now the standard bar.** *MVIG* (CVPR 2026, arXiv:2602.19596)
   learns vulnerability patterns from the defense itself and **cuts defense success rates by
   up to 62%**. *GLST* (arXiv:2607.23059) targets confidence-driven V2X defenses with stealthy
   multi-attacker injection. A defense evaluated only against a non-adaptive spoofer will not
   be taken seriously — which is precisely the failure I measured in §4.1.
2. **Trust and consensus are being actively broken.** *Adversarial Trust Poisoning*
   (arXiv:2605.22122) shows attackers build reputation faster than defenses revoke it, and
   that coordinated vehicles manufacture false majorities. This independently confirms my two
   ablation results — reputation contributes nothing, consensus collapses under collusion.
   *All Vehicles Can Lie* (arXiv:2603.08498) takes the fully-untrusted setting as the premise.
3. **Harm-based evaluation has arrived on the attack side.** *From Stealthy Data Fabrication
   to Unsafe Driving* (arXiv:2605.01301) argues attack success must be measured by unsafe
   driving outcomes, not detection evasion. And *Safety-Aligned 3D Object Detection*
   (arXiv:2604.03325) builds safety-weighted detection metrics covering the cooperative case.

**That last point is the important one for us.** The field has accepted harm-based evaluation
of *attacks*, and safety-weighted metrics for *detection*. Nobody has made harm the
**decision criterion for admission**. That is a sharper, more current gap statement than the
one in my draft — and it means my risk function `R` should *cite* arXiv:2604.03325 rather
than present itself as novel, which strengthens rather than weakens the proposal.

Two papers I must now position against, both missing from my draft: **CP-Guard**
(arXiv:2412.12000) and **CP-uniGuard** (arXiv:2506.22890) do agent-level malicious detection
and defense. Our granularity is different (object-level admission, not agent exclusion), and
§2's ROBOSAC/MATE results show why granularity matters — but a reviewer will ask.
**SRA-CP** (arXiv:2511.17461) is "risk-aware selective cooperative perception", which sounds
like us: it selects *whether to request cooperation and from whom* based on ego-side
occlusion risk, before receiving anything, and does not treat adversaries. Different problem,
adjacent name, must be cited and distinguished.

One reference correction: my draft calls arXiv:2606.02679 "VGMR". The paper is
*Before Fusion, Ask What to Keep: Contextual Calibration of Multimodal Signals*
(Liu et al., June 2026) and does not use that acronym. I should also verify the
"accepted ECCV 2026" status I claimed for UECP — I cannot confirm it.

---

## 6. The revised idea

### Changed — the core mechanism

**From:** a lightweight gate that predicts per-message utility from confidence, class, range,
age, pose uncertainty, agreement, persistence and sender provenance.

**To:** a policy that scores candidate messages **conditioned on the set already admitted**,
trained to imitate the greedy counterfactual oracle. Concretely: decide sequentially, or
score the candidate set jointly with a small set encoder over current cluster state.

Three reasons, all measured: it is where the headroom is (§4.2); context is not
sender-assertable, so it answers the adaptive attacker (§4.1); and it is genuinely novel
against the literature — every method in my reference list scores messages, features, or
senders *independently*.

### Changed — the training label

`U(m|∅)` becomes primary; `E_S[U(m|S)]` is demoted to an ablation. The coalition average
costs **138–277 fusion re-runs per frame** and the cheap label matches or beats it at every
matched operating point. But coalition sampling stays in the paper for one reason worth
stating: leave-one-out labelling is **blind to collusion** — a box reported by two attackers
has `U_loo = −0.013` versus `E_S[U] = −1.414`, and the LOO oracle still admits **38%** of
colluding fabrications where the context-aware oracle admits 0.8%. The real argument is
context-awareness, not Shapley.

### Added

- **Adaptive attacker as a primary experimental condition**, not future work.
- **The counterfactual oracle as a reported upper bound** in every table. It is cheap, it is
  informative, and no paper in this area reports one.
- **Achievability study in Months 1–2**: the risk floor, the loss currency, probability
  calibration of the harm head.

### Cut, or deferred

- **Conformal risk control** — I recommend cutting it from the thesis and keeping it as the
  follow-up paper. Doing it properly (excess-risk target, matched currency, scenario-level
  calibration, a calibrated monotone score) is a project in itself. Cutting it removes the
  most attackable claim and costs nothing that the risk–coverage curve cannot deliver.
- **Sender provenance and cross-agent agreement** as evidence sources — keep them only as a
  negative result, which is publishable in its own right given arXiv:2605.22122.
- **Withholding attacks** from the claims. Admission control is structurally silent about
  messages that never arrive: the oracle itself only reaches remote-only recall 0.402 under
  withholding against 0.753 benign.
- **Bandwidth as a metric.** Object-level late fusion runs at ~6 KiB/s per ego. Benchmarking
  bytes against FPV-RCNN or FocalComm is not like-for-like — those are feature-level methods.

### Narrowed — the claim

The evidence supports *"an object-level admission policy that reduces cooperative harm under
fabrication while preserving remote-only detections."* It does not support a
calibrated-guarantee claim, and in benign traffic a tuned confidence threshold is better.
Scoping to the adversarial and degraded regimes is a strength, not a retreat — that is where
every baseline breaks and where we beat them by a wide margin.

---

## 7. Two decisions I need from you

1. **Compute.** Coalition labelling on real OPV2V means thousands of association-and-fusion
   reruns per frame across a full split, plus a GPU for the detector. My machine is CPU-only.
   What can I actually get? This is the likeliest cause of a timeline slip and it is cheap to
   solve now, expensive in month four.
2. **Scope of the conformal component.** I recommend cutting it to a follow-up. If you want
   it kept in the thesis, I need Months 1–2 reallocated to the achievability study, which
   pushes the real-data transfer work in Months 9–12.

A third, smaller one: whether to report the sandbox results at all in the thesis. My view is
yes, as a controlled diagnostic chapter with the causal-structure argument stated plainly —
because several of the findings above (oracle gap, adaptive-attacker collapse, LOO blindness)
are *only* measurable when you know the ground-truth counterfactual, which no public dataset
gives you.
