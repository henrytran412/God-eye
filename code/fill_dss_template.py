# -*- coding: utf-8 -*-
"""Pour PROPOSAL_v3 into the DSS template, preserving the cover page.

The template's own paragraph styles (ProposalSection/Subsection/Body/Bullet/
Reference) carry all the formatting, so this only supplies text and structure.
Everything on the cover page survives byte-identical except the Title and
Synopsis paragraphs, which must match the body they introduce.
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(r"D:\Thucbao\Du hoc\SJSU\Fall 2026\GhostGuard")
SRC = ROOT / "GhostGuard_Research_Proposal.docx"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC

CONTENT_W = 12240 - 1440 - 1440          # page width less both margins, in DXA


# ---------------------------------------------------------------- inline text
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _run(t, rpr):
    rpr_xml = "<w:rPr>" + rpr + "</w:rPr>" if rpr else ""
    return '<w:r>' + rpr_xml + '<w:t xml:space="preserve">' + esc(t) + '</w:t></w:r>'


PAT = re.compile(r"\*\*(.+?)\*\*|(?<!\*)\*([^*]+?)\*(?!\*)|~(.+?)~")


def runs(text, base=""):
    """**bold**, *italic*, ~subscript~ -> a sequence of <w:r>."""
    out, pos = [], 0
    for m in PAT.finditer(text):
        if m.start() > pos:
            out.append(_run(text[pos:m.start()], base))
        if m.group(1) is not None:
            out.append(_run(m.group(1), base + "<w:b/>"))
        elif m.group(2) is not None:
            out.append(_run(m.group(2), base + "<w:i/>"))
        else:
            out.append(_run(m.group(3), base + '<w:vertAlign w:val="subscript"/>'))
        pos = m.end()
    if pos < len(text):
        out.append(_run(text[pos:], base))
    return "".join(out)


def para(style, text):
    ppr = '<w:pPr><w:pStyle w:val="' + style + '"/></w:pPr>' if style else "<w:pPr/>"
    return "<w:p>" + ppr + runs(text) + "</w:p>"


# -------------------------------------------------------------------- tables
def table(widths, header, rows, caption=None):
    """A TableGrid table. `widths` are relative and rescaled to the text column."""
    tot = sum(widths)
    w = [round(x * CONTENT_W / tot) for x in widths]
    w[-1] += CONTENT_W - sum(w)

    def cell(txt, i, bold=False, shade=False):
        sh = '<w:shd w:val="clear" w:color="auto" w:fill="DEEAF6"/>' if shade else ""
        body = "**" + txt + "**" if bold and txt else txt
        p = ('<w:p><w:pPr><w:spacing w:before="20" w:after="20"/>'
             '<w:ind w:firstLine="0"/><w:jc w:val="left"/></w:pPr>'
             + (runs(body) if txt else "") + "</w:p>")
        return ('<w:tc><w:tcPr><w:tcW w:w="' + str(w[i]) + '" w:type="dxa"/>' + sh
                + '<w:vAlign w:val="center"/></w:tcPr>' + p + "</w:tc>")

    xml = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
           '<w:tblW w:w="' + str(CONTENT_W) + '" w:type="dxa"/>'
           '<w:tblLayout w:type="fixed"/>'
           '<w:tblCellMar><w:left w:w="72" w:type="dxa"/>'
           '<w:right w:w="72" w:type="dxa"/></w:tblCellMar></w:tblPr>'
           '<w:tblGrid>'
           + "".join('<w:gridCol w:w="' + str(x) + '"/>' for x in w)
           + '</w:tblGrid>']
    xml.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>'
               + "".join(cell(c, i, bold=True, shade=True) for i, c in enumerate(header))
               + "</w:tr>")
    for r in rows:
        xml.append("<w:tr>" + "".join(cell(c, i) for i, c in enumerate(r)) + "</w:tr>")
    xml.append("</w:tbl>")
    # a table must be followed by a paragraph or Word runs it into what comes next
    if caption:
        tail = para("ProposalBody", caption)
    else:
        tail = '<w:p><w:pPr><w:spacing w:after="40"/></w:pPr></w:p>'
    return "".join(xml) + tail


# ================================================================ cover fields
TITLE = "Which Component Fails When a Roadside Detector Moves?"

SYNOPSIS = (
    "Roadside 3D detectors are trained at one intersection and deployed at another. "
    "Published accuracy is measured on the training distribution; deployment is not. "
    "The loss is known to be large \u2014 a reported 70\u201390% drop in detection rate "
    "across changes in lidar, geography and weather [1] \u2014 but the field reports it as a "
    "single number and attempts to close it wholesale. "
    "Preliminary measurements on a Jetson Orin Nano suggest the loss is not uniform. "
    "Evaluating NVIDIA's pretrained V2XFusion [12] zero-shot from DAIR-V2X-I (Beijing) [10] "
    "to TUMTraf Intersection (Munich) [11], detection and position largely survive while "
    "heading estimation collapses: vehicles within \u00b15\u00b0 of true heading fall from 88% "
    "to 28%, with the median error unchanged at \u22120.2\u00b0 in both domains. Because roughly "
    "20\u00b0 of heading error on a 4.1 \u00d7 1.9 m box clears IoU 0.25 but not IoU 0.5, this "
    "one mode explains why Car accuracy falls 69.70 \u2192 0.13 AP while Pedestrian and "
    "Cyclist retain 56% and 65%. "
    "Heading is already treated as a separate error axis in-domain \u2014 nuScenes reports "
    "mAOE independently of mATE and mASE [2] \u2014 but a systematic search of the adaptation "
    "literature found it isolated only in-domain or under adversarial perturbation, never "
    "under natural cross-dataset shift, and never for roadside sensors. "
    "This project will test whether domain fragility concentrates in specific components, and "
    "whether the fragile one can be repaired without target labels. Four label-free "
    "interventions will be measured against a supervised oracle."
)

# ===================================================================== body A-F
B = []
add = B.append

add(para("ProposalSection", "A. Introduction"))

add(para("ProposalSubsection", "A.1 Current Research"))
add(para("ProposalBody",
         "**The cross-dataset drop is large and label-free adaptation partly closes it.** "
         "Self-training recovers 16\u201375% of the source-only-to-oracle gap across four "
         "LiDAR transfers using no target labels and no target statistics; on "
         "Waymo\u2192KITTI it lifts Car AP~3D~ from 27.48 to 61.83 against a 73.45 oracle "
         "[3]. Cheaper still, a purely source-side augmentation \u2014 random object scaling "
         "\u2014 recovers about 86% of what the weakly supervised size prior buys (+27.19 "
         "AP~3D~ against +31.72), and *outperforms* it on cyclist [4]."))
add(para("ProposalBody",
         "**Weak supervision is not automatically better.** Statistical Normalization "
         "consumes target-domain object-size statistics yet degrades transfer when the size "
         "gap is small: nuScenes\u2192KITTI AP~BEV~ falls 51.84 \u2192 40.03, a \u221237.55% "
         "closed gap [3]."))
add(para("ProposalBody",
         "**Orientation is already an established, separately-reported error axis.** "
         "nuScenes defines mAOE as a standalone true-positive error alongside mATE and mASE, "
         "and computes mASE only after aligning orientation, decoupling scale from heading by "
         "construction [2]. Earlier work defines paired full- and half-range metrics, FOE = "
         "|(\u03b8\u2212\u03b8\u0302) mod 360\u00b0| and HOE = |(\u03b8\u2212\u03b8\u0302) mod "
         "180\u00b0|, so that 180\u00b0 flips are distinguishable from angular imprecision [5]."))
add(para("ProposalBody",
         "**Why heading is hard has a published explanation.** Cui et al. observe that "
         "\u201cthe front and back of a vehicle may not be easily distinguishable from the "
         "LiDAR point cloud,\u201d and that parked vehicles fail because they \u201chave no "
         "moving trajectory predictions that could be used to reliably infer the "
         "orientations\u201d [5]. Heading is under-determined by appearance; detectors lean "
         "on motion to resolve it."))

add(para("ProposalSubsection", "A.2 Limitations of Current Research"))
add(para("ProposalBullet",
         "**Every adaptation result above is vehicle-mounted and LiDAR-only.** Waymo, KITTI, "
         "nuScenes and Lyft are all ego-vehicle datasets. A roadside sensor is static, has no "
         "ego-motion, and in the deployed single-frame configuration has no trajectory cue at "
         "all \u2014 precisely the cue detectors are shown to depend on for heading [5]."))
add(para("ProposalBullet",
         "**Heading has never been isolated under natural domain shift.** It is measured "
         "in-domain (mAOE, FOE/HOE) and under adversarial perturbation, where error "
         "decomposition shows yaw is disproportionately sensitive and mAP-style metrics hide "
         "it [6]. MS3D++ treats heading as a class-dependent pseudo-label problem \u2014 "
         "catastrophic for elongated vehicles because it destroys IoU, tolerable for "
         "BEV-symmetric pedestrians \u2014 but reports no yaw-specific metric [1]. None of "
         "this is cross-dataset."))
add(para("ProposalBullet",
         "**Adaptation is evaluated as one number.** No work reports which *component* "
         "failed, so it is unknown whether the loss is diffuse or concentrated, and therefore "
         "unknown whether a targeted, cheap repair is even possible."))
add(para("ProposalBullet",
         "**A methodological trap is documented.** Self-training's headline result is "
         "model-selection sensitive: Easy 3D AP has been reported fluctuating between 27.9% "
         "and 60.9% across randomizations, because best-epoch selection leaks target "
         "information [7]. A method that is label-free during training can become "
         "label-dependent at checkpoint selection."))

add(para("ProposalSubsection", "A.3 Research Gap"))
add(para("ProposalBody",
         "A systematic, adversarially-verified literature search returned **no** "
         "cross-dataset results for roadside datasets (DAIR-V2X-I, Rope3D, TUMTraf), **no** "
         "LiDAR+camera fusion transfers, and **nothing** on INT8 quantization versus "
         "out-of-distribution robustness. That is a limit of the search rather than proof of "
         "absence \u2014 the roadside literature exists \u2014 but it establishes that "
         "per-component fragility for roadside 3D detection is, at minimum, not a "
         "well-covered question."))

add(para("ProposalSection", "B. Specific Proposed Research and Why Important/Exciting"))
add(para("ProposalBody",
         "**Question.** Does domain fragility in roadside 3D perception concentrate in "
         "specific network components, and can the fragile component be repaired using only "
         "unlabeled target data?"))
add(para("ProposalBody",
         "**Preliminary evidence, already collected.** A full pipeline was built and "
         "validated on a borrowed Jetson Orin Nano. It reproduces NVIDIA's published "
         "DAIR-V2X-I accuracy [10], [12] to within 0.02\u20130.04 AP on Car and Pedestrian, "
         "establishing that subsequent measurements are trustworthy rather than artifacts. "
         "Zero-shot transfer to TUMTraf Intersection [11] (2,160 frames) gives:"))
add(table([34, 22, 22, 22],
          ["3D AP, moderate", "DAIR-V2X-I", "TUMTraf", "retained"],
          [["Car @ IoU 0.5", "69.70", "0.13", "0.2%"],
           ["Pedestrian @ IoU 0.25", "49.39", "27.61", "55.9%"],
           ["Cyclist @ IoU 0.25", "57.90", "37.76", "65.2%"]]))
add(table([34, 22, 22, 22],
          ["Vehicle heading error", "DAIR-V2X-I", "TUMTraf", ""],
          [["median (signed)", "\u22120.2\u00b0", "\u22120.2\u00b0", ""],
           ["standard deviation", "12.4\u00b0", "24.0\u00b0", ""],
           ["within \u00b15\u00b0", "88%", "28%", ""]]))
add(para("ProposalBody",
         "The median is identical across domains, which excludes a coordinate or calibration "
         "error: the bias is correct and the reliability is not. The error is multi-modal, "
         "clustering near +15\u202630\u00b0 and \u221230\u2026\u221260\u00b0 \u2014 consistent "
         "with a learned prior over road directions rather than random degradation. The class "
         "pattern independently matches MS3D++'s observation that heading error destroys IoU "
         "for elongated vehicles while symmetric classes tolerate it [1]."))
add(para("ProposalBody",
         "**Why it matters.** A missed detection is a failure mode downstream planners are "
         "built to tolerate. A confident *wrong heading* is not: heading feeds motion "
         "prediction, so a correctly located vehicle with a 25\u00b0 heading error yields a "
         "predicted trajectory going somewhere the vehicle is not. If fragility is "
         "concentrated, repair can be local and label-free; if diffuse, retraining on labeled "
         "target data is the only option, which does not scale to per-intersection deployment."))

add(para("ProposalSection", "C. Methodology and Why Innovative/Creative"))
add(para("ProposalBody",
         "**C.1 Per-component fragility profile.** Adapt the sub-task attribution protocol of "
         "monodle [8]: substitute ground truth for one predicted quantity at a time \u2014 "
         "heading, center, size, class \u2014 and re-measure AP. Applied both in-domain and "
         "cross-domain, the *difference* in each substitution's effect attributes the drop to "
         "specific components. monodle applies this in-domain to a monocular detector; "
         "applying it across a natural domain gap, to a LiDAR+camera roadside detector, is "
         "what is new."))
add(para("ProposalBody",
         "**C.2 Test the road-geometry hypothesis.** If heading rests on a learned road-angle "
         "prior, the error clusters must align with the *source* intersection's lane bearings. "
         "This is directly falsifiable, and is scheduled first because a null result redirects "
         "the work."))
add(para("ProposalBody", "**C.3 Four label-free repairs, measured against an oracle.**"))
add(table([40, 26, 34],
          ["Intervention", "Supervision", "Precedent"],
          [["Recalibrate INT8 ranges on unlabeled target frames",
            "none \u2014 forward passes", "untested in the verified literature"],
           ["Adapt orientation head only, backbone frozen",
            "pseudo-labels", "\u2014"],
           ["Random object scaling at source pre-training",
            "none \u2014 source-side", "+27.19 AP~3D~ on car [4]"],
           ["Local-structure input features",
            "none \u2014 source-side", ">21 mAP Waymo\u2192KITTI [9]"]],
          caption="A supervised oracle establishes the recoverable ceiling so each repair is "
                  "reported as *fraction of gap closed*, the convention used by the "
                  "self-training literature [3]."))
add(para("ProposalBody",
         "**C.4 Guard against the documented traps.** Checkpoints will be selected on a "
         "source-domain validation split, never on target performance, because best-epoch "
         "selection on the target leaks label information and inflates results [7]. "
         "Statistical Normalization will be included as a *negative control* rather than a "
         "baseline to beat, since it is known to degrade transfer when the size gap is small "
         "[3]. Per-class AP will be reported throughout, never a single averaged mAP, because "
         "the class balance differs between the two domains."))
add(para("ProposalBody",
         "**C.5 Compression as an axis, not the headline.** Each repair is evaluated at FP16 "
         "and INT8. Preliminary data shows quantization adds 0.0\u00b0 of heading error "
         "in-domain and +1.2\u00b0 out-of-domain; establishing whether that is real requires "
         "repeated calibration seeds and per-class confidence intervals, which C.3 supplies."))
add(para("ProposalBody",
         "**Why innovative.** Existing adaptation methods treat the detector as one object "
         "and ask how much AP returns. This asks *which part broke*, then repairs that part. "
         "It also moves the orientation question out of the vehicle-mounted, multi-frame "
         "setting where it was identified and into the static, single-frame roadside setting "
         "where the motion cue that previously rescued it does not exist."))

add(para("ProposalSection", "D. Milestones and Timeline"))
add(table([17, 47, 36],
          ["Period", "Milestone", "Deliverable"],
          [["Sep\u2013Oct 2026",
            "Lane-bearing correlation (C.2); second target domain converted",
            "Hypothesis confirmed or refuted"],
           ["Nov\u2013Dec 2026",
            "Per-component fragility profile (C.1), two dataset pairs",
            "Fragility table; figure set"],
           ["Jan\u2013Feb 2027",
            "Supervised oracle; repairs 1\u20132 with repeated seeds",
            "Fraction-of-gap-closed per repair"],
           ["Mar 2027",
            "Repairs 3\u20134; full FP16/INT8 matrix; Jetson latency for deployable repairs",
            "Complete results"],
           ["Apr 2027", "Writing; SJSU Research Showcase", "Draft manuscript"],
           ["May 2027", "Final report", "Submitted by 30 May 2027"]]))
add(para("ProposalBody",
         "**Risk and contingency.** The oracle is the only step needing substantial GPU time; "
         "without it, results are reported as absolute recovery rather than fraction-of-oracle "
         "\u2014 weaker but publishable. If C.2 refutes the road-geometry hypothesis, C.1 and "
         "C.3 are unaffected."))

add(para("ProposalSection", "E. Anticipated Outcome"))
add(para("ProposalBullet",
         "**A per-component fragility profile** for roadside 3D detection across two dataset "
         "pairs \u2014 attributing a cross-dataset drop to specific components rather than a "
         "single AP number."))
add(para("ProposalBullet",
         "**A measurement of how much of the gap each label-free repair recovers**, with "
         "confidence intervals, comparable to the fraction-of-gap convention in the adaptation "
         "literature."))
add(para("ProposalBullet",
         "**The first cross-dataset heading-error measurement for roadside sensors**, "
         "reported as a metric distinct from AP."))
add(para("ProposalBullet",
         "**An answer on quantization**: whether INT8 amplifies domain fragility, measured on "
         "a mechanism-level metric sensitive enough to resolve it."))
add(para("ProposalBullet",
         "**Released artifacts** \u2014 the TUMTraf\u2192DAIR converter, the JetPack 7 "
         "deployment recipe and all evaluation code, already public at "
         "github.com/henrytran412/God-eye."))
add(para("ProposalBody",
         "Target venues: SJSU Research Showcase; a workshop paper at CVPR, ICRA or IROS."))

add(para("ProposalSection", "F. Budget"))
add(para("ProposalBody",
         "Portable SSD for dataset storage (about $120); Jetson power-monitoring hardware and "
         "cabling (about $80); remainder for dataset access and incidentals. Maximum "
         "requested: $300."))

BODY_XML = "".join(B)

# ================================================================== references
REFS = [
    "[1] Tsai, D., Berrio, J.S., Shan, M., Nebot, E., Worrall, S. *MS3D++: Ensemble of "
    "Experts for Multi-Source Unsupervised Domain Adaptation in 3D Object Detection.* IEEE "
    "Transactions on Intelligent Vehicles, 2024. arXiv:2308.05988.",

    "[2] nuScenes detection benchmark \u2014 mAOE, mATE, mASE definitions. nuScenes devkit. "
    "github.com/nutonomy/nuscenes-devkit",

    "[3] Yang, J., Shi, S., Wang, Z., Li, H., Qi, X. *ST3D: Self-training for Unsupervised "
    "Domain Adaptation on 3D Object Detection.* IEEE/CVF CVPR, 2021. arXiv:2103.05346.",

    "[4] Yang, J., Shi, S., Wang, Z., Li, H., Qi, X. *ST3D++: Denoised Self-training for "
    "Unsupervised Domain Adaptation on 3D Object Detection.* IEEE Transactions on Pattern "
    "Analysis and Machine Intelligence, 2022. arXiv:2108.06682.",

    "[5] Cui, H., Chou, F.-C., Charland, J., Vallespi-Gonzalez, C., Djuric, N. "
    "*Uncertainty-Aware Vehicle Orientation Estimation for Joint Detection-Prediction "
    "Models.* 2020. arXiv:2011.03114.",

    "[6] Chandorkar, A. et al. *Comprehensive Robustness Analysis of LiDAR-based 3D Object "
    "Detection in Autonomous Driving.* 2026. arXiv:2607.02074.",

    "[7] Independent reproducibility analysis of ST3D self-training. 2024. arXiv:2408.12708.",

    "[8] Ma, X., Zhang, Y., Xu, D., Zhou, D., Yi, S., Li, H., Ouyang, W. *Delving into "
    "Localization Errors for Monocular 3D Object Detection.* IEEE/CVF CVPR, 2021. "
    "arXiv:2103.16237.",

    "[9] Mali\u0107, D., Fruhwirth-Reisinger, C., Schulter, S., Possegger, H. *GBlobs: "
    "Explicit Local Structure via Gaussian Blobs for Improved Cross-Domain LiDAR-based 3D "
    "Object Detection.* IEEE/CVF CVPR, 2025. arXiv:2503.08639.",

    "[10] Yu, H. et al. *DAIR-V2X: A Large-Scale Dataset for Vehicle-Infrastructure "
    "Cooperative 3D Object Detection.* IEEE/CVF CVPR, 2022.",

    "[11] Zimmer, W. et al. *TUMTraf Intersection Dataset: All You Need for Urban 3D "
    "Camera-LiDAR Roadside Perception.* IEEE ITSC, 2023.",

    "[12] NVIDIA. *CUDA-BEVFusion and CUDA-V2XFusion*, Lidar_AI_Solution. "
    "github.com/NVIDIA-AI-IOT/Lidar_AI_Solution",
]
REFS_XML = "".join(para("ProposalReference", r) for r in REFS)

# ==================================================================== assemble
z = zipfile.ZipFile(SRC)
doc = z.read("word/document.xml").decode("utf-8")
head = doc[: doc.index("<w:body>") + len("<w:body>")]
tailsect = doc[doc.rindex("<w:sectPr"):]                  # final two-column sectPr
inner = doc[len(head): doc.rindex("<w:sectPr")]
paras = re.findall(r"<w:p\b(?:(?!</w:p>).)*?</w:p>|<w:p\b[^>]*/>", inner, re.S)
assert len(paras) == 70, "template shape changed: %d paragraphs" % len(paras)


def swap_text(p, new):
    """Replace a single-run paragraph's visible text, keeping its formatting."""
    n = len(re.findall(r"<w:t[^>]*>", p))
    assert n == 1, "expected one text run, found %d" % n
    return re.sub(r"(<w:t)([^>]*)(>)(?:(?!</w:t>).)*(</w:t>)",
                  lambda m: m.group(1) + ' xml:space="preserve"' + m.group(3)
                  + esc(new) + m.group(4),
                  p, count=1, flags=re.S)


paras[14] = swap_text(paras[14], TITLE)
paras[16] = swap_text(paras[16], SYNOPSIS)

new_inner = ("".join(paras[0:22])     # cover + section break + "Body of the Proposal"
             + BODY_XML               # A-F
             + paras[53]              # sectPr paragraph closing the 1-column body section
             + paras[54]              # "G. References" heading
             + REFS_XML)
out_doc = head + new_inner + tailsect

tmp = OUT.with_suffix(".tmp.docx")
zo = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
for item in z.infolist():
    data = (out_doc.encode("utf-8") if item.filename == "word/document.xml"
            else z.read(item.filename))
    zo.writestr(item, data)
zo.close()
z.close()
shutil.move(str(tmp), str(OUT))

print("wrote %s  (%.0f KB)" % (OUT, OUT.stat().st_size / 1024))
print("synopsis: %d words (limit 250)   title: %d words (limit 10)"
      % (len(SYNOPSIS.split()), len(TITLE.split())))
print("body paragraphs: %d   tables: %d   references: %d"
      % (BODY_XML.count("<w:p>"), BODY_XML.count("<w:tbl>"), len(REFS)))
