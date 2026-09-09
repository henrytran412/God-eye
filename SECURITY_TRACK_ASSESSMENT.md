# Assessment: do your attacker papers satisfy Prof. Liu's requirement?

He asked for evidence of **a real attacker, these days**, and a way to fix it. I read all
five papers in `raw/attacker paper/`. Verdict per paper, then the conclusion.

---

## The five papers

### 1. SPaT/MAP V2X communication … with digital twin
Wágner, Ormándi, Tettamanti, Varga · *Computers and Electrical Engineering* 106 (2023)

**Not an attack paper at all.** It implements SPaT/MAP V2X between a traffic light and
vehicles, with a digital twin and hardware-in-the-loop at the ZalaZONE proving ground.
Useful background on how SPaT/MAP actually works. Contains no adversary.
Simulation terms: SUMO ×18, OMNeT ×24.

### 2. PHANTOM: Physical Anamorphic Threats Obstructing Connected Vehicle Mobility
Shuvo & Hossain, George Mason University · arXiv 2512.19711

The most promising of the five, and it still does not clear the bar. It designs a
*physically realisable* attack — anamorphic art printed as a decal or stencilled on
asphalt, which looks natural to humans but fools YOLOv5/SSD/Faster R-CNN/RetinaNet from
a particular viewing angle. Over 90% attack success.

But the paper says plainly: **"This attack is validated using CARLA, a physics-based
simulator,"** with network effects via **SUMO-OMNeT++ co-simulation**. The decal is never
printed and never placed on a real road. It is a physically *plausible* attack evaluated
entirely in simulation — exactly the category he rejected.

Note also: PHANTOM attacks **vision**, not V2X messages. It is a perception-security
paper wearing a connected-vehicle title.

### 3. SPADE: SPaT Attack Detection from the Connected Vehicle's Perspective
Di Novo, Ragab, Leblanc · arXiv 2609.02741

This is a **defence**, not evidence of an attacker — and it is close to the original
GhostGuard idea, applied to SPaT messages instead of object messages. It is simulation-
based. Treat it as **related work you would have to beat**, not as support.

### 4. A Systematic Literature Review of Simulated Cyber Attacks on Vehicles and UTC
Wellens-Miles, Guo, Liu, Parkinson, Vallati · *IEEE T-ITS* 26(10), Oct 2025

**This paper argues his case, not yours.** It is a systematic review of *simulated*
attacks — 330 uses of "simulat". Its own justification for why the field simulates:

> "Simulations are an effective way to assess the potential impact of attacks. They are
> low-cost compared to physical experimentation, are easy to replicate…"

That is a peer-reviewed admission that physical attack evidence is scarce **because it is
expensive**, and that the literature substitutes simulation for it. If you show him this
paper, you are handing him the citation for his own objection.

### 5. Cyber resilience of connected and autonomous transportation systems (Phase I)
Noruzoliaee & Nazari · US DOT UTC final report, 22 August 2025

The most authoritative document of the five, and the only one that points at **real
documented incidents**:

> "Documented incidents demonstrate that cyber attacks on transportation systems can be
> highly targeted and disruptive. At the vehicle level, researchers have exploited
> controller area network (CAN) bus vulnerabilities to remotely assume safety-critical
> functions such as steering…"

That is the Miller & Valasek Jeep Cherokee lineage — a genuine remote attack on a
production vehicle that triggered a 1.4-million-vehicle recall. **Real. Physical.
Documented.**

But it is a **CAN bus / in-vehicle network** attack, not V2X. And it is from 2015, not
"these days."

---

## Conclusion

**None of the five documents a real-world V2X attack on a deployed autonomous vehicle.**
Two are simulated attacks, one is a simulated defence, one is infrastructure with no
adversary, and one is a survey confirming the field runs on simulation.

**More searching will not fix this, because the paper he is asking for does not exist.**
V2X is not deployed at scale, so there is nothing in the field to attack. You cannot
produce real-world evidence of attacks on a system that has not been rolled out. This is
a fact about the world, not a gap in your literature search — and it is worth saying to
him in exactly those words, because it shows you understood the objection rather than
just failing to satisfy it.

---

## What *is* real, if you want to keep security

There is a class of attacks on autonomous vehicles that **is** physically demonstrated on
real hardware — and every one of them attacks **perception**, not V2X:

| Attack | Reality |
|---|---|
| CAN bus remote control (Miller & Valasek) | Production Jeep, remote, 1.4 M recall |
| LiDAR spoofing (Cao et al.) | Real spoofing hardware against real LiDAR |
| Adversarial road-sign stickers (Eykholt et al.) | Printed, placed, drive-by tested |
| Projector "phantom" attacks (Nassi et al.) | Against real Tesla Autopilot |

So if the security instinct matters to you, the defensible version is **physical
robustness of perception** — not message trust. It needs no V2X deployment assumption,
and the attacks are documented.

**I am not recommending it for this proposal.** Reasons:

1. It re-opens the "is this two areas?" objection you just closed.
2. PHANTOM shows that even physically-realisable attack papers evaluate in CARLA — so he
   would apply the same criticism to your evaluation, and you would be back where you
   started.
3. Nineteen days.

Mention it verbally as a possible year-two extension. Keep it out of the proposal.

---

## Is his GitHub repo usable for a security baseline?

**No.** `lkk688/DeepDataMiningLearning/ngperception` is entirely occupancy prediction:
FlashOcc migration, label-free distillation, cross-dataset occupancy pretraining,
Gaussian representations. There is no attack code, no threat model, no defence, no
adversarial evaluation anywhere in it.

Using it for a security baseline would mean writing every security component yourself —
which is precisely the position that produced the untrustworthy simulation last time.

For the **perception** track it is the opposite: the repo *is* the baseline, his FlashOcc
migration plan is the exact model to reproduce, and his published mIoU is the number to
hit.

---

## What makes the perception-only work unique

Four tiers, weakest to strongest. Claim tier 2–3 in the proposal; hold tier 4 for the year.

**Tier 1 — a first measurement.** No occupancy network has been benchmarked on
Jetson-class hardware. True, but thin on its own: "we measured a thing."

**Tier 2 — an evaluation-protocol critique.** The field reports mIoU **in-domain on
datacentre GPUs** (FlashOcc: 31.95 on Occ3D-nuScenes, throughput on an RTX 3090).
Deployment is **out-of-domain on edge hardware**. The reported number does not predict
field performance and nobody has quantified the gap. *This is the contribution.*

**Tier 3 — an interaction nobody has tested.** Does compression amplify domain-shift
degradation? Established for image classifiers and LLMs; never examined for 3D occupancy.
If INT8 degrades worse under shift than FP32, the model you actually ship fails hardest in
exactly the conditions you did not train for. That is a safety finding.

**Tier 4 — a question inside his own program.** His headline is +35% detection mAP at 2k
labels from occupancy pretraining. **Does that advantage survive compression?** If it is a
full-precision artifact, that matters to him a great deal.

The supporting evidence is real and checkable: DG-BEV (CVPR 2023) measures camera BEV
retaining **7% of oracle mAP** on nuScenes→Waymo (0.040 vs 0.552). That is the collapse
your intuition predicted, published, with a table.
