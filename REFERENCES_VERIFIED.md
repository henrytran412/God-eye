# Reference verification status

Deep-research extracted 25 claims across 9 sources, but **every verification panel
failed on a usage limit** — the searches ran, the adversarial checking did not. What
follows records which claims were then checked by hand against the primary source,
because a proposal that cites an unchecked paraphrase is worse than one that cites
less.

Raw unverified output: `research_claims.md`.

## Verified against the primary source — safe to cite

| claim | source | status |
|---|---|---|
| "a significant 70-90% drop in detection rate due to variations in lidar, geography, or weather" | MS3D++, arXiv:2308.05988 | quoted verbatim from abstract |
| HOE = \|(θ−θ̂) mod 180°\|, FOE = \|(θ−θ̂) mod 360°\|, reported separately from AP | Cui et al., arXiv:2011.03114 | equation (6), extracted from PDF |
| "the front and back of a vehicle may not be easily distinguishable from the LiDAR point cloud" | Cui et al., arXiv:2011.03114 | quoted verbatim from PDF |
| parked vehicles "have no moving trajectory predictions that could be used to reliably infer the orientations" | Cui et al., arXiv:2011.03114 | quoted verbatim from PDF |
| Evaluated on nuScenes; vehicle-mounted | Cui et al., arXiv:2011.03114 | confirmed in PDF |
| "over-reliance on these global geometric features can cause 3D detectors to prioritize object location and absolute position, resulting in poor cross-domain performance" | GBlobs, CVPR 2025, arXiv:2503.08639 | quoted verbatim from abstract |
| GBlobs gains: >21 mAP Waymo→KITTI, 13 KITTI→Waymo, 12 nuScenes→KITTI; all vehicle-mounted | GBlobs, CVPR 2025 | confirmed in abstract |
| MLC-Net is unsupervised, needs source annotations only | Luo et al., arXiv:2107.11355 | confirmed in abstract |

## Corrected during verification

**GBlobs does NOT use the words "shortcut" or "spurious."** The research agent's
paraphrase framed it as shortcut learning; the paper describes "over-reliance on
global geometric features." The proposal uses the paper's own wording. This is the
single most important catch — the shortcut framing was load-bearing for the original
novelty claim and would not have survived a reader opening the paper.

## Extracted but NOT yet verified — do not cite without checking

* ST3D / ST3D++ transfer numbers (Waymo→KITTI 27.48 → 61.83 / 65.64 AP_3D against a
  73.45 oracle; Waymo→nuScenes recovering only ~21% of the gap). Plausible and widely
  cited, but the specific table values were not confirmed.
* SN degrading orientation while improving scale (AOE 0.368 vs 0.212 direct transfer
  on KITTI→nuScenes). **This is the most valuable unverified claim** — it would be
  independent published evidence that orientation is dissociable from scale and can be
  made worse by a method that fixes something else. Worth confirming from the MLC-Net
  paper's tables before it appears anywhere.
* MS3D++ on heading destroying IoU for elongated vehicles while symmetric classes
  survive. Not in the abstract; would corroborate the Car-vs-Pedestrian pattern
  measured here.
* SF-UDA³D and DPO test-time-adaptation figures.
* MonoDLE's in-domain sub-task numbers (GT orientation +0.76 AP vs GT location
  → 78.84). The *protocol* is what the proposal borrows, and that is described in
  the abstract; the specific values are not yet confirmed.

## Own measurements

Everything in the preliminary-results tables was measured directly and is reproducible
from this repository — see `results_jetson/`. The baseline reproduces NVIDIA's
published DAIR-V2X-I numbers to within 0.02–0.04 AP, which is the check that makes the
rest of the measurements worth reading.
