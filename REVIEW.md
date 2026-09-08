# GhostGuard — baseline implementation and design audit

Prepared for the office-hour discussion. Everything below comes from code in
`code/` and result files in `results/`; every number is reproducible with the
commands in the last section.

---

## 0. What was built, and what it can honestly tell us

No GPU is available here and OPV2V is not downloaded, so this is **not** a
reproduction of published numbers. Instead I built a controlled
cooperative-perception sandbox in which the ground-truth causal structure is
known — for every message we know which real object it refers to (if any),
whether the ego could ever have seen that object, and whether the sender
fabricated it. That is exactly what is needed to audit whether the GhostGuard
**decision rule is well-posed**, which is a different question from how well it
scores on a benchmark.

| Piece | File | What it is |
|---|---|---|
| Sandbox | `code/ghostguard/sim.py` | 4-lane road, ego + 3 CAVs, cars & pedestrians, real line-of-sight occlusion, range-dependent detection and localisation noise, honest clutter, sender pose error, latency, sensor degradation; attacks: `spoof`, `collusion`, `removal`, plus adaptive variants |
| Late fusion + risk | `code/ghostguard/fusion.py` | `F(S)`, and `R(F(S),y)` over missed / ghost / localisation / duplicate terms with pedestrian, driving-corridor and proximity severity weights |
| Counterfactual labels | `code/ghostguard/utility.py` | `U(m|S)`, coalition-sampled `E_S[U]`, `U(m|∅)`, leave-one-out, and a sequential greedy oracle |
| Gate | `code/ghostguard/gate.py` | 20-feature MLP, three heads (utility, harm probability, heteroscedastic σ) |
| Conformal risk control | `code/ghostguard/crc.py` | CRC threshold selection, monotonicity check, nested 4-action map |
| Baselines | `code/ghostguard/baselines.py` | ego-only, naive LF, confidence, geometric consensus, BELT-style evidential, ROBOSAC-style attestation, MATE-style temporal trust, CAD-style occupancy check, and two oracles |

**Scale.** 200 training scenarios (2,000 frames, 31,082 coalition-labelled
messages), 140 calibration scenarios, 110 test scenarios per condition across 5
conditions. Absolute values are sandbox-specific; the **signs, orderings and
failure modes** are what to take from this.

**Two implementation notes that are also proposal notes.** First, an IoU-0.3
gate is unreachable for an 0.8 m pedestrian footprint under realistic
localisation noise, so a correctly detected pedestrian would count as a miss
*and* a ghost simultaneously and corrupt `R`. I switched association to
class-dependent centre distance (nuScenes convention, 2 m / 1 m). Decide this
explicitly in the thesis. Second, `R` needs a scored region of interest, or
clutter a sender reports 90 m down the road gets charged to the ego as a ghost.

---

## 1. The headline

**The core premise of the proposal is correct, and I can now put a number on
it.** Over 16,443 messages (`results/target_mismatch.csv`):

- **28.9% of messages asserting a non-existent object cause no measurable harm.**
  Among low-confidence ones, **99.9%** are inert — they never clear the fused
  operating threshold, so they never reach the output.
- **20.9% of messages about genuinely real objects are harmful** (stale,
  pose-shifted, or duplicate-inducing).
- Agreement between "this message is false" and "this message is harmful" is
  only **77%**.

So falsehood and harm really are different quantities, and provenance-, trust-
and consensus-based filtering optimises the wrong one. That is a stronger and
more defensible motivation than the "confident fabricated box" intuition in the
current synopsis, and it is worth putting in the introduction as a measured
result rather than an assertion.

**The learned utility gate delivers on this premise.** At a fixed threshold
(`gate_binary`, τ=0.5), against the strongest baselines:

| Condition | ego-only | naive LF | best prior-art baseline | **utility gate** | oracle |
|---|---|---|---|---|---|
| Benign | 12.05 | 9.49 | 8.23 (conf 0.7) | **6.50** | 4.30 |
| Fabrication | 12.75 | 15.74 | 9.82 (consensus) | **7.30** | 4.78 |
| Collusion | 11.86 | 15.20 | 10.95 (occupancy) | **6.99** | 4.49 |
| Withholding | 11.92 | 11.33 | 10.10 (conf 0.7) | **8.95** | 7.40 |
| Sensor degraded | *12.48* | 18.31 | 12.58 (consensus) | 12.52 | 8.64 |

Mean safety risk `R`, lower is better (`results/policies.csv`). Malicious-message
acceptance under fabrication: 5.2% for the gate vs 46% (occupancy check), 26%
(ROBOSAC-style), 36% (MATE-style), 100% (confidence).

One row is not a win and should be reported as such: under heavy sensor
degradation **no policy beats ego-only** (12.48) except the oracle (8.64) — the
gate reaches 12.52. When most senders are degraded, cooperation as a whole stops
paying, and a message-admission policy cannot fix that. The oracle gap shows the
information is still there, which makes this a useful stress case rather than a
dead end.

That is a real result and it is the thing to show first. **Everything below is
about the parts that do not yet work.**

---

## 2. Corrections needed, in priority order

### 2.1 CRITICAL — the impressive anti-fabrication numbers are largely an artifact of the attacker announcing itself

This is the finding most likely to sink a defence if it surfaces late.

The feature-trust ablation (`results/feature_tiers.csv`, fabrication condition)
shows where the gate's resistance actually comes from:

| Features available to the gate | `R` | malicious acceptance |
|---|---|---|
| All | 6.92 | 0.037 |
| minus sender reputation | 6.87 | 0.035 |
| minus reputation **and** cross-agent agreement | 6.99 | 0.034 |
| minus confidence, claimed covariance, age | 8.88 | 0.260 |
| Ego-verifiable geometry only | 8.99 | 0.323 |

Two things follow. **Sender reputation and cross-agent agreement contribute
nothing** — removing both is free, or very slightly beneficial. The gate's
entire fabrication resistance rests on confidence, claimed pose covariance and
message age: **three fields the sender asserts and an adversary sets freely.**

So I built an adaptive attacker that samples those three fields from the benign
true-positive distribution instead of shouting (`results/adaptive_attack.csv`):

| Gate | fabrication | fabrication, adaptive | collusion | collusion, adaptive |
|---|---|---|---|---|
| Trained on naive attacks | **0.060** | **0.553** | 0.205 | **0.780** |
| Retrained on adaptive | 0.449 | 0.188 | 0.964 | 0.709 |
| Retrained, geometry only | 0.347 | 0.391 | 0.453 | 0.430 |
| Counterfactual oracle | 0.011 | 0.016 | 0.006 | 0.006 |

Malicious-message acceptance. Against an attacker that merely matches benign
metadata, acceptance goes from **6% to 55%**, and under adaptive collusion the
gate's risk advantage over ego-only nearly evaporates (`R` 12.14 vs 12.43).
Retraining helps but does not recover it.

**The oracle stays at ~1% in every column.** The information needed to reject
these messages is present — but it lives in the *context* (what the fused output
would become), not in the per-message feature vector. A per-message
feed-forward gate over hand-crafted features structurally cannot reach it.

**What to change.** (a) Make the adaptive attacker a *primary* experiment in
Months 6–8, not an "open problem" — the current plan would report the 6% number.
(b) Drop sender provenance and cross-agent agreement from the feature list, or
keep them only to show they do not help; the proposal currently lists both as
evidence sources. (c) Most importantly, see §2.2.

### 2.2 CRITICAL — replace independent per-message scoring with a set-conditioned or sequential policy

The gap between the gate (`R` 6.5–7.3) and the greedy counterfactual oracle
(`R` 4.3–4.8) is larger than the gap between the gate and every baseline
combined. The oracle differs from the gate in exactly one respect: **it decides
in the context of what it has already admitted.**

Supporting evidence from the label diagnostic (`results/label_diagnostic.csv`):
`E_S[U]` correlates with `U(m|∅)` at ρ=0.90 with **95.5%** three-class
agreement. A marginalised per-message label is nearly a context-free label. The
context is precisely what the oracle exploits and what the marginalisation
throws away.

**Concrete suggestion.** Reframe the contribution as *imitating the greedy
counterfactual oracle with a policy that conditions on the current accepted
set* — score candidates jointly (a small set transformer or a DeepSet over
current cluster state), or decide sequentially. That is a stronger and more
novel claim than per-message utility regression, it is supported by the oracle
gap measured here, and it directly addresses §2.1 because context is not
sender-assertable.

### 2.3 MAJOR — conformal risk control, as specified, has no useful feasible solution

`results/crc_alpha_sweep.csv`, calibrated on 1,400 benign frames
(see `results/fig2_crc.png`):

| target α | λ̂ | benign risk | benefit rate | messages admitted |
|---|---|---|---|---|
| 0.05 – 0.20 | **0.00** | 0.000 | **0.000** | **0.000** |
| 0.30 | 0.02 | 0.269 | 0.145 | 0.181 |
| 0.40 | 0.52 | 0.378 | 0.878 | 0.797 |
| 0.50 | 0.98 | 0.483 | 0.988 | 0.922 |

**For any α ≤ 0.20 the only feasible threshold rejects every message.** The
guarantee holds perfectly and cooperative perception is switched off. The
achievable harm floor at the strictest non-zero threshold is 0.286, so promising
5% or 10% is simply infeasible.

And the calibration actively hurts: the *same gate* scores `R` 6.50 at a
hand-set τ=0.5 but **10.60** at its CRC-selected threshold on benign traffic —
worse than not calibrating at all. Three separable causes:

1. **The target is absolute, not relative.** Control *excess* harm over the
   ego-only baseline. Then "reject everything" scores zero excess harm but is
   visibly dominated on the benefit axis, instead of being the optimum.
2. **The loss and the label are different events.** The gate is trained on
   `P(U < −δ)`; the conformal loss counts messages asserting non-existent
   objects. Those agree only 77% of the time (§1). The thresholds are quantiles
   of a score never trained to rank the controlled quantity. Make them the same
   currency.
3. **`p̂_harm` is miscalibrated and non-monotone exactly where CRC operates**
   (`results/gate_calibration.csv`). The bottom bin `[0, 0.01)` holds 1,842
   messages predicted 0.25% harmful of which **30.4% are ghosts** — a higher
   ghost rate than every bin up to `[0.6, 0.8)`. Isotonic recalibration cuts
   mean reliability error from 0.193 to 0.036, but it collapses the low tail into
   one flat step, so the *ranking* has to be fixed in the model, not patched
   afterwards.

Also: choose α from the measured risk–coverage curve and report the achievable
floor. Do this in Months 1–2, not Months 6–8 — the current timeline discovers
this failure four months too late.

### 2.4 MAJOR — the CRC guarantee is marginal over calibration draws, not per-deployment

`results/crc_exchangeability.csv`, 200 scenario-level splits of a 300-scenario
benign pool. Mean test risk stays ≤ α everywhere, so the theory is satisfied.
But the per-deployment picture differs by calibration unit:

| calibration unit | α=0.10 | α=0.20 | α=0.30 | α=0.40 |
|---|---|---|---|---|
| frame (n = scenarios × 10) | 18.5% | 43.0% | 37.0% | 17.0% |
| scenario (n = scenarios) | 9.5% | 16.0% | 23.5% | 9.5% |

Share of deployments whose realised risk exceeds α, at n_cal = 150 scenarios.
Ten consecutive frames of one scenario share objects, senders, pose error and
attacker, so frames are not the exchangeable unit. **Calibrate at the scenario
level and say so**, and state the guarantee as an average over calibration
draws — a safety argument that reads it as per-deployment is overclaiming.

### 2.5 MAJOR — coalition sampling may not earn its cost

The proposal's central methodological choice is `U(m) = E_S[U(m|S)]`, a
Shapley-flavoured average. Measured cost (`code/exp_cost.py`): **138 fusion
re-runs per frame at K=16, 277 at K=32**, versus ~n for a single solo
evaluation. Measured benefit, comparing gates trained on the two labels at
matched harm rate (`results/tradeoff.csv`, `results/fig1_benefit_vs_harm.png`):

| condition | harm rate | benefit, `E_S[U]` | benefit, `U(m|∅)` |
|---|---|---|---|
| Benign | 0.40 | 0.369 | **0.426** |
| Fabrication | 0.20 | 0.148 | **0.257** |
| Fabrication | 0.40 | 0.994 | 0.993 |
| Collusion | 0.20 | 0.759 | **0.831** |
| Collusion | 0.40 | 0.998 | 0.999 |

The cheap label matches or beats the expensive one at every valid operating
point and never loses. (The two converge at the most permissive settings.) At
full policy level, `gg_label_solo` also beats `ghostguard_crc` under every
condition — `R` 9.21 vs 10.60 benign, 10.20 vs 11.57 under fabrication.

**But do not delete coalition sampling — it is defensible for a reason the
proposal does not currently state.** Under collusion, leave-one-out labelling is
*blind*: a fabricated box reported by two attackers has `U_loo = −0.013`
(removing one copy changes nothing) versus `E_S[U] = −1.414`. And the LOO oracle,
which has ground-truth access, still admits **38.3%** of colluding fabrications
(`R` 9.99) where the context-aware oracle admits 0.8% (`R` 4.49). So the real
argument is *context-awareness*, and both `E_S[U]` and `U(m|∅)` have it while LOO
does not. Present coalition sampling with this ablation, and drop
"Shapley-inspired" from the contribution list unless it survives.

### 2.6 MODERATE — the four-way taxonomy is a property of a context, not of a message

"Helpful / redundant / harmful / unresolved" shifts substantially with the
reference context (`results/label_diagnostic.csv`, benign):

| label | helpful | redundant | harmful |
|---|---|---|---|
| `E_S[U]` | 50.1% | 25.8% | 24.1% |
| `U_loo` | 21.0% | 56.2% | 22.8% |
| `U_greedy` | 33.8% | 41.9% | 24.3% |

Three-class agreement between `E_S[U]` and `U_loo` is only **62%**. Outright
sign flips are rare (1.2%), so the taxonomy is not incoherent — but the
redundant class more than doubles depending on which context you ask about.
**Define the reference context explicitly in the methodology.**

There is also a concrete trap (`results/redundancy.csv`). Redundancy is a
property of a *set*: when k senders report the same remote-only pedestrian, each
copy is individually near-zero, yet dropping all k loses the object. An
"accept iff `U_loo` > 0" rule **admits zero messages for 8.2%** of
multi-sender remote-only objects, versus 3.2% for solo labelling; recovery at 3+
senders is 0.934 vs 0.985. Worth one paragraph and one experiment.

### 2.7 MODERATE — the message-level Benefit/Harm metrics can rank policies backwards

The proposal's headline metrics are "Benefit/Harm Rates, malicious-message
acceptance". These are message-level proxies, and they invert against realised
risk. Benign traffic:

| policy | harm rate | mean `R` |
|---|---|---|
| conf 0.5 | 0.183 | 8.05 |
| utility gate (τ=0.5) | **0.514** | **6.50** |

The gate admits 2.8× the share of false messages and yet achieves 19% lower
safety risk — because the ones it admits are the inert 29% from §1 while it
suppresses the damaging ones. The critique the proposal makes of prior work
("useful but indirect… they do not measure whether admitting one object message
actually makes perception safer") **applies to its own proposed metrics.**

Fix: weight Harm Rate by realised `|U|`, or define it only over messages that
change the output. Keep `R` and AP as the primary metrics. Also note
`benefit_rate` is computed over *available* messages, so under withholding the
oracle scores 0.840 benefit while remote-only recall is only 0.402 — report both.

### 2.8 MODERATE — quarantine and soft-fusion are currently unmeasurable

Within a single frame, quarantine and rejection are the same decision: both
contribute weight 0. I implemented a temporal release path (a held message is
admitted once a later frame corroborates it) so the action is at least testable.
It buys almost nothing: `ghostguard_crc` 10.60 vs `gg_no_quarantine` 10.77
benign; the 4-action variant is within noise of binary accept/reject on the
trade-off curves. Single-frame `R` also never charges for the delay a quarantine
imposes on a real pedestrian.

Either reduce to accept / soft-fuse / reject, or commit to a multi-frame
timeline metric where delay is a cost. Do not claim four actions without one.

### 2.9 MODERATE — conclusions are sensitive to the risk weights

`results/risk_weight_sensitivity.csv`, rank by mean `R` (1 = best):

| policy | default | ghost-heavy | miss-heavy | no dup/loc |
|---|---|---|---|---|
| occupancy check | 3 | 4 | **2** | 3 |
| GhostGuard | 2 | 2 | **5** | 2 |
| naive LF | 6 | 6 | **3** | 6 |
| ego-only | 4 | 3 | **6** | 4 |

Under a miss-dominant weighting the ordering substantially reverses — every
conservative policy loses to naive fusion. Since `R` is both the training target
and the evaluation metric, this is circular unless the weight sweep is reported.
Report it, and report AP and remote-only recall (which are weight-independent)
alongside.

### 2.10 SCOPE — admission control cannot address withholding attacks

A withholding attacker cuts remote-only message coverage from 0.86 to 0.50, and
no admission policy recovers it: the oracle reaches remote-only recall 0.402
under withholding versus 0.753 benign. GhostGuard gates what arrives; it is
structurally silent about what never arrives. Either scope removal out of the
claims, or add a complementary component that models what a sender *should*
have reported given its pose. The proposal currently lists spoofing and removal
together under Adv-OPV2V.

### 2.11 Minor notes

- **Bandwidth is a near-vacuous metric here.** Object-level late fusion runs at
  ~6 KiB/s per ego (15 messages/frame × ~40 B × 10 Hz). Do not benchmark bytes
  against FPV-RCNN or FocalComm — those are intermediate-feature methods, and the
  comparison is not like-for-like.
- **Latency is a non-issue**, which is worth stating: feature extraction 0.62 ms
  + gate 0.30 ms + fusion 0.40 ms = **1.32 ms/frame** on CPU, against a 100 ms
  budget at 10 Hz. Coalition labelling is a training-time cost only.
- **Score-fusion mode** (max / noisy-OR / mean) made no measurable difference at
  a fixed operating threshold, since cross-agent clusters are rare. If you want
  to claim a fusion-rule contribution you need score-threshold sweeps.
- The gate's σ head is worth keeping for a reason not in the proposal: for ~30%
  of messages the spread of `U(m|S)` across coalitions **exceeds the magnitude
  of its mean**, so a large part of "unresolved" is irreducible label noise
  rather than model ignorance. Those are different quantities and should be
  reported separately.

---

## 3. What I would change in the proposal text

1. **Synopsis / Introduction.** Replace the assertion with the measurement:
   *"29% of messages asserting non-existent objects change the fused output not
   at all, while 21% of messages reporting real objects increase safety risk;
   falsehood and harm agree only 77% of the time."*
2. **Methodology.** State the reference context for the utility label. Make
   `U(m|∅)` the primary label and `E_S[U(m|S)]` an ablation justified by the
   collusion argument in §2.5.
3. **Methodology — architecture.** Change "a lightweight gate predicts utility…
   from confidence, class/size/range, age, pose uncertainty…" to a policy that
   conditions on the currently accepted set. Cite the oracle gap as motivation.
   Remove sender provenance and cross-agent agreement, or keep them as a
   negative result.
4. **Methodology — conformal.** State the loss in the same currency as the label,
   define it as excess risk over ego-only, calibrate at the scenario level, and
   report the achievable floor and the risk–coverage curve. State plainly that
   the guarantee does not extend to adversarial traffic — exchangeability fails
   by construction — and that it is an average over calibration draws.
5. **Evaluation.** Add an adaptive attacker that mimics benign metadata as a
   primary condition. Add the risk-weight sweep. Redefine Harm Rate to weight by
   realised effect. Report remote-only recall next to benefit rate.
6. **Timeline.** Move the achievability study (risk floor, target currency,
   probability calibration) into Months 1–2. Move the adaptive attacker from
   "future work" into Months 6–8. The current plan finds §2.3 and §2.1 too late
   to respond to them.
7. **Claims.** The evidence supports "an object-level admission policy that
   reduces cooperative harm under fabrication while preserving remote-only
   detections". It does not currently support a calibrated-guarantee claim, and
   in benign traffic a tuned confidence threshold keeps more benefit per unit of
   harm than the gate does (see the left panel of `fig1`) — so scope the
   contribution to the adversarial and degraded regimes, where the gate wins
   decisively.

---

## 4. Reproducing this

```bash
python code/run_all.py            # main comparison, CRC sweep, ablations (~12 min)
python code/exp_label.py          # §2.5, §2.6  label well-posedness
python code/exp_crc.py            # §2.4        exchangeable calibration unit
python code/exp_calib.py          # §2.3(3)     harm-probability reliability
python code/exp_mismatch.py       # §1, §2.3(2) falsehood vs harm
python code/exp_redundancy.py     # §2.6        the redundancy trap
python code/exp_adaptive.py       # §2.1        adaptive attacker
python code/exp_cost.py           # §2.11       latency and label cost
python code/make_figs.py          # figures
```

Smaller/faster: `python code/run_all.py --n-train 40 --n-cal 40 --n-test 30
--n-sweep 20 --coalitions 8`. Requires numpy, scipy, pandas, matplotlib, torch
(CPU is fine). The full log of the run these numbers come from is
`results/full_run.log`.
