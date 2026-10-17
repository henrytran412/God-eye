"""Build an Obsidian vault from the project's measured results.

The findings live in long markdown reports (results_jetson/) that read
top-to-bottom. A vault is the other shape: small linked notes you arrive at from
any direction. This writes that second shape from the same numbers, so the vault
never drifts from the reports -- rerun it after new results land.

    python code/make_vault.py            # writes notes/vault/

Numbers here are transcribed from results_jetson/repair/ATTRIBUTION.md and
results_jetson/teacher/TEACHER.md, which remain the source of truth.
"""
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
VAULT = ROOT / "notes" / "vault"

# --------------------------------------------------------------- the measurements
# Car, moderate difficulty, 1620-frame evaluation split unless noted.
REPAIRS = [
    # name, car3d05, verdict, why it was tried, what happened
    ("Baseline", 1.83, "reference", "V2XFusion moved to TUMTraf unchanged.", ""),
    ("INT8 recalibration", 0.15, "worse",
     "PTQ picks activation ranges from the source domain; if the target's activations fall outside them, everything saturates.",
     "Calibrated on 540 unlabeled target frames. Car fell to 0.15, Pedestrian rose to 47.34."),
    ("Head threshold", 1.83, "no effect",
     "The detection head discards proposals below 0.1, which might be erasing real detections.",
     "Two more boxes per frame, not one digit of movement. `result2kitti.py:253` cuts at 0.45 *before* AP is computed, so the head's floor never reaches the metric."),
    ("Operating point", 2.30, "not adaptation",
     "That 0.45 cut was chosen where the median score is 0.987; on the target the median is 0.286, so it discards 64% of predictions.",
     "Car +0.47 then plateaus, but the **source domain gains as much** (Ped +1.10 source vs +0.14 target). Threshold tuning, not domain adaptation."),
    ("Intensity neutralised", 0.23, "much worse",
     "PointPillars consumes intensity as a feature and two lidars report it differently.",
     "The medians already agree (13 vs 11). Blanking it cost Pedestrian 43.11 -> 19.03, so the channel carries signal."),
    ("Camera blanked", 0.00, "collapse",
     "The target camera's optical axis sits ~16 deg lower; a fusion model fed unfamiliar geometry might be suppressing detections.",
     "Every class reads exactly 0.00. The camera is load-bearing, so gating it is not available."),
    ("Density control", None, "exonerated",
     "The target supplies 9,508 in-range points per frame against the source's 37,930.",
     "Thinning the *source* to that density and scoring in-domain cost Car only **5.12 AP** of a 67.87 AP gap."),
    ("Calibration audit", None, "sound",
     "The camera is essential, so broken projection geometry would poison the fused features everywhere.",
     "100% of GT centres project in front of the camera in both domains. It did reveal a **1.69x focal-length gap** (1293 vs 2183)."),
    ("Ground-plane sweep", 2.08, "no peak",
     "Target labels sit where source labels do, but the point cloud ground looked ~1 m lower.",
     "Seven shifts from -0.5 to +1.5 m with z=0 as control. No peak near the predicted offset; the curve just tracks the range crop."),
    ("Ground-plane, confirmed", 1.32, "did not replicate",
     "The sweep's -0.5 m point showed 2.08 against a 1.73 control on 400 frames.",
     "On the full 1620 frames Car goes **down** 0.51. The peak was subset noise."),
]

# name, car3d05, bev05, car3d025, bev025, cdap, note
TEACHER = [
    ("Baseline", 1.83, 3.69, 6.26, 9.21, 6.45, "V2XFusion unchanged."),
    ("Teacher, LiDAR only", 1.42, 9.22, 11.87, 24.02, 14.71, "YOLO frustum + minimum-area rectangle."),
    ("+ 2D refinement", 0.97, 14.19, 24.25, 36.79, 24.10, "Box slid until its projection matches the 2D box. Used leaked size priors."),
    ("Source priors", 2.00, 18.16, 27.02, 36.51, 24.75, "**Airtight.** Every prior from source labels."),
    ("+ ground-plane lift", 1.95, 17.87, 27.98, 37.57, 27.21, "**Airtight, best.** Recovers boxes with too few points."),
    ("+ LiDAR height floor", 3.77, 18.63, 29.20, 36.61, 25.06, "Upper reference only: the height estimate was trusted after a target-label check."),
    ("Oracle: perfect 2D", 5.22, 14.90, 24.82, 33.40, 25.49, "Ceiling of LiDAR fitting given a flawless 2D detector."),
]

SUBSTITUTION = [
    ("nothing (baseline)", 69.70, 0.79),
    ("heading (yaw)", 69.83, 0.85),
    ("size", 69.36, 2.61),
    ("centre", 71.19, 4.36),
    ("all three at once", 71.74, 14.10),
]


def fm(title, tags, **extra):
    lines = ["---", f"title: {title}", "tags:"]
    lines += [f"  - {t}" for t in tags]
    for k, v in extra.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def tbl(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join("" if c is None else str(c) for c in r) + " |")
    return "\n".join(out) + "\n"


NOTES = {}

# ------------------------------------------------------------------------ index
NOTES["00 Index.md"] = fm("Index", ["moc"]) + """# God-eye — research vault

What fails when a roadside 3D detector is deployed at an intersection it was never
trained on, and can it be repaired without labels there.

> [!abstract] The one-line result
> Detection does not degrade gracefully: Car accuracy falls **69.70 -> 1.83**. No
> single component explains it, nine training-free repairs recovered nothing, and a
> label-free teacher built from a frozen 2D model plus raw LiDAR gets Car to
> **27.21** centre-distance AP without training or target labels.

## Start here

- [[Research Question]] — what is actually being asked
- [[Domain Shift]] — the collapse, measured
- [[Component Attribution]] — which part breaks, and why "orientation" was wrong
- [[Metrics]] — ==read this before quoting any number==
- [[Repair Attempts]] — nine things that did not work
- [[Label-Free Teacher]] — the thing that did
- [[Corrections]] — claims this project made and then withdrew
- [[Open Questions]] — what comes next

## Context

- [[Datasets]] · [[Jetson]] · [[Proposal]]

## Map

![[Research Map.canvas]]
"""

# --------------------------------------------------------------------- question
NOTES["Research Question.md"] = fm("Research Question", ["core"]) + """# Research Question

> [!question] The question
> Does domain fragility in roadside 3D perception concentrate in specific network
> components, and can the fragile component be repaired using only unlabeled
> target data?

A roadside detector is trained at one intersection and deployed at another. Published
accuracy is measured on the training distribution; deployment is not.

What makes the roadside case distinct from the vehicle-mounted literature: the sensor
is **static**, has no ego-motion, and in single-frame deployment has no trajectory cue
— precisely the cue detectors are shown to rely on for heading.

## Why it matters

A missed detection is a failure downstream planners tolerate. A confident *wrong*
heading is not: heading feeds motion prediction. At 15 m/s over a 3 s horizon, the
measured heading spread moves a predicted position by **~8.6 m**, about two and a half
lane widths.

See [[Domain Shift]] for what was measured, and [[Proposal]] for the framing that
needs rewriting.
"""

# ------------------------------------------------------------------ domain shift
NOTES["Domain Shift.md"] = fm("Domain Shift", ["finding", "domain-shift"]) + """# Domain Shift

V2XFusion trained on [[Datasets#DAIR-V2X-I|DAIR-V2X-I]] (Beijing), evaluated unchanged
on [[Datasets#TUMTraf Intersection|TUMTraf]] (Munich). Zero-shot, no recalibration.

""" + tbl(["3D AP, moderate", "Source", "Target", "Retained"],
          [["Car @ IoU 0.5", "69.70", "**1.83**", "3%"],
           ["Pedestrian @ IoU 0.25", "48.87", "43.11", "88%"],
           ["Cyclist @ IoU 0.25", "57.63", "43.13", "75%"]]) + """
> [!warning] The classes are not scored alike
> Car is judged at IoU 0.5, the other two at 0.25. That single difference drives most
> of the apparent class pattern — see [[Metrics]].

## It is not a metric artefact

Scored by nuScenes centre distance, the loosest standard metric, the target still
reads **6.45** against **95.51** in-domain. For each target GT car, the nearest
prediction within 2 m was:

- a car — 23.0%
- **nothing at all — 73.7%**
- some other class — ~3%

In-domain, 98.7% of cars get a car prediction. ==The detector does not see
three-quarters of the target cars.==

## Input differences, measured

""" + tbl(["", "Source", "Target"],
          [["points inside `point_cloud_range`", "37,930/frame", "9,508/frame"],
           ["GT cars with >=5 LiDAR points", "96.5%", "89.4%"],
           ["median points on a car", "52", "21"],
           ["camera focal length", "2183", "1293"],
           ["median object depth", "68.3 m", "31.6 m"],
           ["median detection score", "0.987", "0.286"]]) + """
Sparser input is real but is **not** the cause — see the density control in
[[Repair Attempts]].

Next: [[Component Attribution]].
"""

# ----------------------------------------------------------------- attribution
NOTES["Component Attribution.md"] = fm("Component Attribution", ["finding", "attribution"]) + """# Component Attribution

The C.1 protocol from the [[Proposal]], run for real: substitute ground truth for one
predicted field, re-score, read off the ceiling that fixing that component could reach.

> [!success] Harness validated
> The in-domain baseline reproduces **69.70** exactly, matching the published table.

""" + tbl(["GT substituted for", "In-domain", "Cross-domain"],
          [[n, f"{a:.2f}", f"**{b:.2f}**"] for n, a, b in SUBSTITUTION]) + """
> [!danger] The hypothesis was wrong
> Perfect heading buys **+0.06 AP** on Car — 0.09% of a 68.91 AP drop. The
> [[Proposal]] was built on orientation being the fragile component. It is not.

## The failure is conjunctive

Matched cars carry several moderate errors *at once*:

""" + tbl(["Axis", "Measured", "Effect on a 4.1 x 1.9 m box"],
          [["Heading", "std 22.3 deg", "BEV IoU falls to ~0.47"],
           ["Height", "0.786x", "3D IoU falls to ~0.37"],
           ["Width", "0.904x", "compounds both"],
           ["Elevation", "0.49 m low", "compounds vertical overlap"],
           ["Length", "0.996x", "correct"]]) + """
Each error alone is survivable. Together they put the box the wrong side of IoU 0.5,
while Pedestrian and Cyclist at IoU 0.25 stay on the right side of theirs. That is the
whole class pattern in [[Domain Shift]], explained.

This also resolves the apparent contradiction: one field substituted recovers almost
nothing, three recover +13.31.

## The recall ceiling

Even with every matched box made perfect, cross-domain AP reaches only **14.10**,
because just **22.9%** of target objects get any prediction within 2.5 m against
**76.5%** in-domain. Box quality cannot be repaired on objects never found.

Decomposing the 68.91 AP Car drop: ~84% ceiling collapse (detection), ~16% box quality.

Next: [[Repair Attempts]].
"""

# --------------------------------------------------------------------- metrics
NOTES["Metrics.md"] = fm("Metrics", ["method", "metrics"]) + """# Metrics

> [!important] Say which metric, every time
> "Car AP" is ambiguous here by a factor of fourteen. The same predictions read
> **1.95** or **27.21** depending only on the rule.

## The three in use

| metric | what it demands | baseline | best achieved |
|---|---|---|---|
| **3D AP @ IoU 0.5** | height, elevation, footprint, heading all near-exact | 1.83 | 1.95 |
| **BEV AP @ IoU 0.5** | footprint and heading; ignores height | 3.69 | **17.87** |
| **Centre distance (nuScenes)** | a box within 0.5–4 m; ignores size and heading entirely | 6.45 | **27.21** |

Prof. Liu's `ngperception` TUTORIAL reports centre distance, where his own model reads
0.467 by centre distance against 0.157 by IoU 0.5. The "usually around 30%" expectation
is a centre-distance number.

## Why Car looks so much worse than Pedestrian

Car is scored at IoU 0.5; Pedestrian and Cyclist at 0.25. A 22 deg heading error on a
4.1 x 1.9 m box gives BEV IoU ~0.47 — fails 0.5, passes 0.25 comfortably. The classes
were never compared at a matched threshold.

`KITTI_CAR_LOOSE=1` adds a Car-at-0.25 column to the evaluator; unset, results are
bit-identical to before.

## Three baseline numbers, all correct

| value | what it is |
|---|---|
| 0.13 | FP16, all 2160 frames — the published headline |
| 0.79 | INT8, all 2160 frames |
| **1.83** | INT8, 1620-frame eval split — the baseline for every repair |

Earlier I guessed this was a scoping difference. It is precision: the delta table gives
Car -0.654 with INT8 better, and 0.13 + 0.654 = 0.78. See [[Corrections]].
"""

# -------------------------------------------------------------- repair attempts
rows = [[f"[[{n}]]" if n != "Baseline" else n,
         "—" if c is None else f"{c:.2f}", v] for n, c, v, _, _ in REPAIRS]
NOTES["Repair Attempts.md"] = fm("Repair Attempts", ["experiment", "negative-result"]) + """# Repair Attempts

Nine training-free interventions, in the order they ran. Each was chosen by what the
previous one ruled out, so the sequence is the argument.

""" + tbl(["Attempt", "Car 3D@0.5", "Verdict"], rows) + """
> [!failure] Net domain-specific improvement: zero
> The only positive — lowering the evaluator's operating point, +0.47 — helps the
> **source** domain just as much, so it is threshold tuning rather than adaptation.

## Why none of them worked

[[Component Attribution]] predicts it. The failure is conjunctive: four axes degrade at
once, and no intervention that leaves the weights untouched moves more than one. Nothing
in the input space crosses a threshold that needs three fixed simultaneously.

## A methodological scar worth keeping

A seven-point sweep on a 400-frame slice produced a clean, interpretable maximum at
z = -0.5 that **was not real** — it reversed sign on the full split. Section C.4 of the
[[Proposal]] already warns about selecting on noisy evidence; this is that trap, met on
our own data.

What did eventually work came from changing the source of the boxes, not post-processing
them: [[Label-Free Teacher]].
"""

for name, c, verdict, why, what in REPAIRS:
    if name == "Baseline":
        continue
    body = fm(name, ["experiment"], verdict=verdict,
              car_3d_05=("null" if c is None else c))
    body += f"# {name}\n\n> [!question] Why it was tried\n> {why}\n\n"
    body += f"**Result — {verdict}.** {what}\n\n"
    body += "Part of [[Repair Attempts]]. Diagnosis in [[Component Attribution]].\n"
    NOTES[f"Experiments/{name}.md"] = body

# -------------------------------------------------------------------- teacher
NOTES["Label-Free Teacher.md"] = fm("Label-Free Teacher", ["experiment", "result", "teacher"]) + """# Label-Free Teacher

Prof. Liu's [`ngperception/gaussian4d`](https://github.com/lkk688/DeepDataMiningLearning/tree/main/DeepDataMiningLearning/ngperception)
builds occupancy targets with **no human labels**: raw LiDAR geometry for structure,
frozen 2D foundation models for semantics. This applies the same recipe to detection.

## The pipeline

1. A **COCO-pretrained YOLO** — trained on neither dataset — finds cars in the target image.
2. The **LiDAR points inside each 2D box** are cut out, ground removed, clustered, and a
   minimum-area rectangle fitted.
3. **2D-guided refinement**: the box is slid and rotated until its projection matches the
   2D box, while staying on the points.
4. **Ground-plane lift** for boxes with too few points: the 2D box's bottom edge is
   projected onto the mapped road surface.

Nothing is trained. No target label is read. V2XFusion's Pedestrian and Cyclist
predictions pass through untouched, so any change in the Car row is the teacher's doing.

""" + tbl(["Run", "3D@0.5", "BEV@0.5", "3D@0.25", "BEV@0.25", "CD-AP", "Note"],
          [[n, f"{a:.2f}", f"{b:.2f}", f"{c:.2f}", f"{d:.2f}", f"**{e:.2f}**", note]
           for n, a, b, c, d, e, note in TEACHER]) + """
> [!success] Best airtight result
> **CD-AP 6.45 -> 27.21** (4.2x), **BEV@0.5 3.69 -> 17.87** (4.8x), using only
> source-domain priors. At the 4 m threshold, CD-AP reaches **50.53**.

> [!warning] Strict 3D barely moves
> 1.83 -> 1.95. IoU 0.5 in 3D needs height, elevation and footprint near-exact at once,
> and ~21 points per car cannot pin that down. See [[Metrics]].

## What the refinement fixes

With perfect 2D boxes, a car's LiDAR cluster holds a median **13 points**, all on the
sensor-facing side, so its centroid sits **1.74 m** from the true centre. Matching the
projection to the 2D box roughly doubled every metric (oracle CD-AP 13.75 -> 25.49).

## Tried and rejected

| variant | effect |
|---|---|
| refine V2XFusion's own boxes | worse (CD-AP 6.19) — its scores are collapsed, so refined boxes rank badly |
| union with V2XFusion cars | ~ teacher alone |
| snap yaw to road directions | worse (BEV@0.5 18.63 -> 14.19) — three directions from noisy yaws are too coarse |
| add YOLO's `truck` class | best BEV@0.25 (41.09), worse elsewhere |

Next: [[Open Questions]].
"""

# ----------------------------------------------------------------- corrections
NOTES["Corrections.md"] = fm("Corrections", ["method", "corrections"]) + """# Corrections

Claims this project made and then withdrew. Kept because each one changed a conclusion,
and because a reader of the older documents will otherwise trust them.

> [!bug] "Orientation is what breaks"
> The [[Proposal]] title, synopsis and four sections rest on it. Substituting perfect
> heading recovers **+0.06 AP**. Overturned by [[Component Attribution]].
> `docs/index.html` still carries this headline publicly.

> [!bug] "Only ~48% of target cars have LiDAR points"
> The correct figure is **89.4%** (median 21 points). The probe that produced 48% was
> testing footprints rotated 90 degrees. This matters: it means the fitter discards cars
> it could fit, which is a cheap remaining gain.

> [!bug] "Target cars are 1.70 m tall"
> Inferred from a ratio mid-session. Measured: **1.50 m** against the source's 1.40 m.
> So the height difference explains little of the 0.786x under-prediction.

> [!bug] "The point cloud ground sits ~1 m below the labels"
> Read off a z-histogram. Measured directly, points and labels agree vertically:
> **+0.01 m** on target, -0.10 m on source. The converter is not at fault.

> [!bug] "The 0.13 vs 0.79 gap is a scoping difference"
> It is precision: 0.13 is FP16, 0.79 is INT8, on the same frames. See [[Metrics]].

> [!bug] An oracle that scored *below* real YOLO
> The "perfect 2D box" oracle initially drew GT boxes rotated 90 degrees, so it looked
> worse than the real detector. A gate comparing both yaw conventions caught it
> (BEV@0.5 6.43 against 0.004).
"""

# -------------------------------------------------------------- open questions
NOTES["Open Questions.md"] = fm("Open Questions", ["next"]) + """# Open Questions

## 1. Teacher -> student

Everything in [[Label-Free Teacher]] runs *alongside* an unchanged V2XFusion. The step
`gaussian4d` is actually built for is to use the teacher boxes as **pseudo-labels to
fine-tune the detection head** on unlabeled target frames, backbone frozen.

- First experiment here that trains weights
- Feasible on the [[Jetson]] for the head alone, but slow
- The obvious use of the 540-frame calibration split, which no result has touched

## 2. Recover the cars the fitter drops

[[Corrections]] showed 89.4% of target cars have LiDAR points, yet the fitter converts
only 53% of YOLO's boxes. The losses are inside the pipeline — the 8% frustum shrink,
ground removal, the 5-point cluster minimum — not for lack of evidence. ==Cheapest
remaining gain.==

## 3. Recall before box quality

Perfect boxes on everything currently detected reach only 14.10, because 77% of objects
are never found. Until detection improves, box-refinement is capped at a fifth of source
performance. This orders the whole programme.

## 4. Things the measurements cannot yet separate

- **Sensor vs geography.** One source and one target cannot tell them apart. A second
  target pair turns a case study into an attribution.
- **The 1.69x focal gap** feeding a camera branch the model cannot run without
  ([[Domain Shift]]). Measured, untested as a cause.
- **A supervised oracle** would let every repair be reported as a fraction of the
  recoverable gap, the convention the adaptation literature uses.

## 5. The proposal needs rewriting

Title, synopsis, A.2, A.3, all of B, and two of C.3's four repairs rest on the
orientation claim. See [[Proposal]].
"""

# -------------------------------------------------------------------- context
NOTES["Datasets.md"] = fm("Datasets", ["context", "dataset"]) + """# Datasets

## DAIR-V2X-I

Beijing roadside infrastructure, the **source** domain. V2XFusion's training set.
2,016 validation frames. Dense: 37,930 in-range points per frame, median 52 points on a
car. Camera focal length 2183, median object depth 68.3 m.

## TUMTraf Intersection

Munich roadside gantry (R2), the **target** domain. 2,160 frames, split here into 540
calibration and 1,620 evaluation. Converted to DAIR layout by
`code/edge/jetson_patches/tumtraf_to_dair.py`.

Sparser and closer: 9,508 in-range points per frame, median 21 points on a car, focal
1293, median depth 31.6 m. 54.5% of its cloud sits above the +3 m ceiling and is cropped.

> [!note] Labels are sound
> 99.8% of TUMTraf GT sits inside `point_cloud_range`, better than DAIR's own 80.9%, and
> GT z matches (-1.00 vs -0.90). The conversion is not the problem — see [[Corrections]].

Both feed [[Domain Shift]].
"""

NOTES["Jetson.md"] = fm("Jetson", ["context", "hardware"]) + """# Jetson

Borrowed **Orin Nano**, JetPack 7 / L4T R39.2, sm_87, 8 SMs, 7.3 GiB unified memory, no
swap, 15 W. Every measurement in this vault ran here.

Full bring-up and the eight JetPack 7 blockers: `notes/JETSON_SETUP.md`.

## Working notes

- Experiments run inside `cmpelkk/jetson-llm` via `~/godeye/dock.sh`, which needs
  `--ipc=host --ulimit memlock=-1` or `/dev/shm` SIGBUS
- numba's CUDA backend segfaults on this board, hence `rotate_iou_cpu.py`
- `~/godeye/jetson_watchdog.sh` checks every 5 minutes for crashes, failed steps, dead
  runners, memory, disk and temperature; it survives disconnects but **not a reboot**

> [!warning] Never `pkill -f` a script name here
> The pattern matches the SSH command line and kills your own session. It has happened
> three times. Send scripts on stdin, or kill by exact PID.

## It cannot train

8 SMs and 7.3 GiB are enough for inference and for fine-tuning a detection head, not for
retraining a detector. That constraint shapes [[Open Questions]].
"""

NOTES["Proposal.md"] = fm("Proposal", ["context", "proposal"]) + """# Proposal

Davidson Student Scholars, AY2026-27. Mentor Prof. Kaikai Liu. Sources in
`proposal/`; cover-page documents stay in the gitignored `proposal/private/`.

Current title: *Which Component Fails When a Roadside Detector Moves?*

> [!danger] The framing is obsolete
> The synopsis says "detection and position largely survive while heading estimation
> collapses." [[Component Attribution]] contradicts both halves: detection is ~84% of
> the loss and heading contributes ~0.1%.

## What needs rewriting

- Title, synopsis, A.2, A.3, all of B
- C.3's repair list — two of its four are now measured negatives
  ([[Repair Attempts]]: INT8 recalibration hurts Car; the others never cross the threshold)
- C.5, which treats compression as the axis of interest

## What replaces it

A stronger result than the original: a systematic demonstration, each with a control,
that **nine label-free interventions cannot close a roadside cross-domain gap**, plus a
label-free teacher that recovers 4.2x without training ([[Label-Free Teacher]]). That is
the evidence-backed case for the compute the next stage needs, rather than asking on spec.
"""

# -------------------------------------------------------------------- the canvas
def nid(rng):
    return "".join(rng.choice("0123456789abcdef") for _ in range(16))


rng = random.Random(7)                       # deterministic, so reruns do not churn
panels = [
    ("Datasets.md",            -440,    0, 320, 190, "5"),
    ("Jetson.md",              -440,  240, 320, 190, "5"),
    ("Research Question.md",      0,    0, 340, 200, "6"),
    ("Domain Shift.md",           0,  260, 340, 260, "1"),
    ("Metrics.md",                0,  580, 340, 220, "2"),
    ("Component Attribution.md",440,  120, 380, 300, "1"),
    ("Corrections.md",          440,  480, 380, 260, "2"),
    ("Repair Attempts.md",      920,    0, 380, 280, "2"),
    ("Label-Free Teacher.md",   920,  340, 380, 320, "4"),
    ("Open Questions.md",      1400,  160, 340, 300, "6"),
]
ids = {}
nodes, edges = [], []
for f, x, y, w, h, col in panels:
    i = nid(rng); ids[f] = i
    nodes.append(dict(id=i, type="file", file=f, x=x, y=y, width=w, height=h, color=col))

links = [
    ("Datasets.md", "Research Question.md", "right", "left", None),
    ("Jetson.md", "Research Question.md", "right", "left", "measured on"),
    ("Research Question.md", "Domain Shift.md", "bottom", "top", None),
    ("Domain Shift.md", "Metrics.md", "bottom", "top", "read first"),
    ("Domain Shift.md", "Component Attribution.md", "right", "left", "which part?"),
    ("Component Attribution.md", "Corrections.md", "bottom", "top", "overturned"),
    ("Component Attribution.md", "Repair Attempts.md", "right", "left", "9 tried"),
    ("Repair Attempts.md", "Label-Free Teacher.md", "bottom", "top", "all failed"),
    ("Label-Free Teacher.md", "Open Questions.md", "right", "left", "4.2x, then?"),
    ("Repair Attempts.md", "Open Questions.md", "right", "left", None),
]
for a, b, fs, ts, label in links:
    e = dict(id=nid(rng), fromNode=ids[a], fromSide=fs, toNode=ids[b], toSide=ts, toEnd="arrow")
    if label:
        e["label"] = label
    edges.append(e)

title = dict(id=nid(rng), type="text", x=-440, y=-190, width=1080, height=120, color="6",
             text="# God-eye — how the findings connect\n"
                  "Follow the arrows. Red is what broke, green is what worked.")
nodes.insert(0, title)
canvas = dict(nodes=nodes, edges=edges)

# ---------------------------------------------------------------------- write
VAULT.mkdir(parents=True, exist_ok=True)
(VAULT / "Experiments").mkdir(exist_ok=True)
for name, body in NOTES.items():
    (VAULT / name).write_text(body, encoding="utf-8")
(VAULT / "Research Map.canvas").write_text(json.dumps(canvas, indent=2), encoding="utf-8")

# validate the canvas against the spec before claiming success
all_ids = [n["id"] for n in nodes] + [e["id"] for e in edges]
assert len(all_ids) == len(set(all_ids)), "duplicate canvas id"
node_ids = {n["id"] for n in nodes}
for e in edges:
    assert e["fromNode"] in node_ids and e["toNode"] in node_ids, "dangling edge"
for n in nodes:
    assert n["type"] in ("text", "file", "link", "group")
    if n["type"] == "file":
        assert (VAULT / n["file"]).exists(), f"canvas points at a missing note: {n['file']}"

print(f"vault: {VAULT.relative_to(ROOT)}")
print(f"  {len(NOTES)} notes, {len(nodes)} canvas nodes, {len(edges)} edges")
for name in sorted(NOTES):
    print(f"    {name}")
