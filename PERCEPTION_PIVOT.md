# Pivot to perception: research findings and proposed direction

Prepared 8 September 2026 · deadline for the DSS submission is 28 September

---

## 1. Your professor is right, and it is worth understanding exactly why

Three separate criticisms, all of which hold.

**"Too complicated."** Cooperative perception *and* adversarial security is two research areas. Each has
its own literature, threat model, datasets, and evaluation protocol. For a nine-month undergraduate
project that must finish by 30 May 2027, that is not a scope problem you can trim your way out of.

**"No evidence of real-world attackers."** This is the strongest of the three and it is correct in the
way that matters. Physical sensor attacks *are* demonstrated in the literature — LiDAR spoofing,
adversarial patches on road signs. But V2X message injection against a deployed autonomous vehicle
has no documented real-world instance, because V2X is not deployed at scale. Every attack paper in
that space simulates its own adversary. You would spend a year defending against a threat model
nobody can show occurring, and a committee can ask "has this ever happened?" and you have no answer.

**"The baseline is not trustworthy — simulation without evidence for why you use that technique."**
This is the deepest one, and it applies directly to what we built. In the sandbox I chose the
false-positive rate, the sender pose error, the attacker's confidence range, and the four risk
weights. Every headline number descended from parameters I invented. Some of that was flagged in the
audit, but he has named the real problem: there was no empirical warrant for the parameter choices
in the first place. A reviewer cannot check any of it against anything.

The pivot is the right call. What follows is built so that **every number can be checked against a
published one**.

---

## 2. The most important thing found in this research

`lkk688` is **Prof. Kaikai Liu** — SJSU Computer Engineering, NVIDIA University Ambassador, Cisco
Corporate Chair Professor. He did not send you a reference; he sent you **his own active research
program**. His `ngperception/docs` folder is a live lab notebook, not a tutorial set.

What is in it:

| Finding | Number |
|---|---|
| Occupancy pretraining → low-label detection | **+35% mAP at 2k labels** (0.163 vs 0.121 from scratch) |
| Advantage across label budgets | 1.4–2.1× |
| Label-free voxel-soft pretraining | **null** — no improvement |
| Label-free occupancy quality | mIoU ≈ 0.10 |
| FlashOcc supervised reference | mIoU 31.95 (R50), 43.52 (Swin-B) |
| Target venue | CVPR / ICCV |

And four gaps stated **in his own documents**:

1. *"Cross-dataset domain gaps"* — sensor layout, ego-frame conventions, class-name alignment — listed
   as open work.
2. *"Detection transfer results lack a from-scratch control … preventing causal claims."*
3. *"Plan external validation on public backbones (FlashOcc/BEVDet-Occ) rather than their own
   architecture."* Planned. Not done.
4. **The entire stack targets an H100.** There is no edge-deployment arm anywhere in the program.

You own a Jetson Orin Nano. Gap 4 is yours to fill, and it is the one his program is not equipped to
close.

---

## 3. What the literature says about your "efficiency drops on a different dataset" instinct

Your instinct is correct, and it is far more dramatic than you probably realised. This is the
published evidence, verified from the papers' own tables.

### Camera-based BEV detection collapses across datasets

**DG-BEV**, Wang et al., CVPR 2023 — Table 1, BEVDepth backbone, mAP / NDS*:

| Transfer | Source-only | Oracle | Retained |
|---|---|---|---|
| nuScenes → Waymo | **0.040** / 0.178 | 0.552 / 0.649 | **7%** of oracle mAP |
| Waymo → nuScenes | **0.032** / 0.133 | 0.475 / 0.587 | **7%** |
| nuScenes → Lyft | 0.112 / 0.296 | 0.602 / 0.684 | 19% |
| Lyft → nuScenes | 0.102 / 0.213 | 0.401 / 0.482 | 25% |

A camera BEV detector moved to a new dataset retains roughly **7% of its accuracy**. Not a
degradation — a collapse. This is the single most useful citation you now have.

### LiDAR detection degrades too, and the cause is identified

**Wang et al., "Train in Germany, Test in the USA," CVPR 2020** — a KITTI-trained detector is *"36
percent worse on Waymo"* than one trained on Waymo. The dominant cause turned out to be
embarrassingly concrete: **average car size differs by geography**. Correcting for it (statistical
normalization) took KITTI→Waymo AP_3D from 12.3 to 49.4.

**ST3D**, CVPR 2021 — Waymo→KITTI source-only 67.64/27.48, oracle 83.29/73.45. Also shows statistical
normalization is *not* universal: on nuScenes→KITTI it actively hurts (51.84 → 40.03 AP_BEV).

### For occupancy specifically, the numbers do not exist yet

Cross-dataset transfer for 3D *occupancy* is acknowledged as a problem but I could not find published
mIoU-drop numbers for it. **UniOcc** (ICCV 2025) has just built the unified benchmark that makes such
a measurement possible across datasets. This is a gap with the infrastructure newly in place — good
timing for you, and it matches gap 1 in your mentor's own list.

### Nobody has benchmarked occupancy networks on Jetson-class hardware

FlashOcc's published throughput is measured on an **RTX 3090** with TensorRT FP16. I found no
published occupancy-network benchmark on any Jetson platform. Meanwhile quantization-under-
distribution-shift *is* an established question in other fields — "Quantization Meets OOD"
(arXiv:2509.00859), ODG-Q — just not in 3D perception.

---

## 4. The proposed direction

> **When a 3D occupancy network is compressed to run on automotive edge hardware, does it lose more
> accuracy under dataset shift than the full-precision model does?**

Three measurements, in order:

1. **Reproduce.** Take FlashOcc/BEVDet-Occ, reproduce its published Occ3D-nuScenes mIoU. This is the
   trustworthy baseline — a public model with a public number you either hit or you don't.
2. **Compress.** Export to TensorRT, quantize to FP16 and INT8, deploy on the Jetson Orin Nano.
   Measure accuracy *and* latency at each precision. These are the first such numbers published.
3. **Shift.** Evaluate every variant under dataset shift. Compare the degradation curve of the
   compressed model against the full-precision one.

The hypothesis worth testing: **compression and domain shift interact**. If the INT8 model loses
more under shift than FP32 does, then the model you actually ship is the one that fails worst in
exactly the conditions you did not train for — which is a safety result, not just an efficiency one.
If they degrade identically, that is also publishable and useful: it means edge deployment is free of
robustness cost, which nobody has shown either.

### Why this satisfies each of his objections

| His objection | How this answers it |
|---|---|
| Too complicated | One area. Perception. No adversary, no threat model, no security literature. |
| No real-world evidence | Dataset shift is not hypothetical — DG-BEV measures a 93% collapse. Deployment on constrained hardware is not hypothetical either. |
| Untrustworthy baseline | Public model, public checkpoint, published mIoU 31.95 to reproduce. Failure to reproduce is visible. |
| No evidence for the technique | FlashOcc because it is his own migration target with published numbers. TensorRT INT8 because it is the standard automotive deployment path. Cross-dataset because DG-BEV shows the collapse. Every choice has a citation. |

### Why it fits you specifically

It needs no novel architecture — it is careful measurement, which is undergraduate-scale and finishes
on time. It runs on hardware you already own. It sits inside NVIDIA's ecosystem, where your mentor is
an Ambassador. And it produces the edge-deployment arm his CVPR/ICCV program currently lacks, which
is the strongest possible argument for him to say yes.

---

## 5. Honest risks

**The Orin Nano may not fit the model.** 8 GB shared memory, and FlashOcc at 200×200×16 was built for
datacentre GPUs. Mitigation: reduce input resolution, use the R50 rather than Swin-B backbone, and
fall back to a smaller BEV grid. **This needs a feasibility check before the proposal is submitted**
— if the model does not run at all, the project has no hardware arm.

**Dataset size.** Occ3D-nuScenes is large. The nuScenes mini split plus the corresponding occupancy
labels is the practical starting point; full-scale evaluation needs real storage and probably lab
compute.

**Reproduction is not guaranteed.** Hitting the published mIoU takes work, and mmlab-era dependencies
are notoriously painful — his own notes record a `bev_pool_v2` CUDA compile blocker on H100. Budget
real time for the environment.

---

## 6. Research still open

Two threads did not finish and should be closed before the proposal is final:

- **CUDA-V2XFusion.** Correction to what I said earlier: it lives in **NVIDIA-AI-IOT/Lidar_AI_Solution**,
  not DL4AGX. Its pipeline, dataset (likely DAIR-V2X), and supported Jetson platforms are unverified.
  It matters because it is the closest existing example of NVIDIA shipping a V2X perception model for
  Jetson — but note it is *V2X*, which is the direction you are stepping away from. Worth checking
  whether its Jetson deployment tooling is reusable for a single-vehicle occupancy model.
- **Cross-dataset occupancy numbers.** Whether any paper reports an Occ3D-nuScenes → Occ3D-Waymo mIoU
  drop. If none does, that strengthens the proposal; it should be confirmed rather than assumed.

---

## 7. Suggested next actions

1. **Feasibility check on the Jetson, this week.** Get *any* BEV or occupancy model running under
   TensorRT and record the latency. This is the one result that de-risks the whole proposal, and it
   is worth more to the meeting than another page of prose.
2. **Rewrite the proposal** around the direction in §4, reusing the DSS structure already in
   `PROPOSAL_v2.tex` (cover page, ≤3 body pages, Fall 2026 – Spring 2027 timeline).
3. **Ask him three things:** whether this slots into his program the way it appears to; whether lab
   GPU access is available for the reproduction step; and whether the work could contribute to the
   CVPR/ICCV submission his notes describe.
