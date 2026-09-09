# Workflow: from here to a submitted proposal

**Department deadline: 27 September.** Prof. Liu must approve first, so aim to meet him
around **24 September**.

---

# ⏱ DO THIS IN THE NEXT HOUR

Ordered so that anything with **human-approval delay starts first**. Do not reorder.

### 0–10 min · Request DAIR-V2X-I access
The long pole. V2XFusion cannot run without it and approval is not instant.

Open the CUDA-V2XFusion README, follow its DAIR-V2X-I dataset link, register, and request
the **infrastructure-side (DAIR-V2X-I)** data. Note in your calendar that you asked today.
```
https://github.com/NVIDIA-AI-IOT/Lidar_AI_Solution/tree/master/CUDA-V2XFusion
```

### 10–15 min · Request nuScenes access
nuscenes.org → register → request access. You may not need it (BEVFusion ships example
data) but it costs five minutes and unblocks Phase 1 later.

### 15–30 min · Identify the Jetson
Boot it, open a terminal, paste this whole block, and **save the output to a file**:
```bash
{
  echo "=== model ==="            ; cat /proc/device-tree/model; echo
  echo "=== L4T ==="              ; cat /etc/nv_tegra_release
  echo "=== JetPack ==="          ; dpkg-query -W -f='${Version}\n' nvidia-jetpack 2>/dev/null
  echo "=== TensorRT ==="         ; dpkg-query -W -f='${Version}\n' tensorrt 2>/dev/null
  ls -l /usr/src/tensorrt/bin/trtexec 2>/dev/null || echo "trtexec MISSING"
  echo "=== CUDA ==="             ; nvcc --version 2>/dev/null | tail -2
  echo "=== memory ==="           ; free -h
  echo "=== disk ==="             ; df -h /
  echo "=== power mode ==="       ; nvpmodel -q 2>/dev/null
  echo "=== arch ==="             ; uname -m
} 2>&1 | tee ~/jetson_info.txt
```
**The decision this makes:** you need **TensorRT ≥ 8.5**, so **JetPack ≥ 5.1**. If it is
older, reflashing costs a day — and you need to know that today, not Thursday.

### 30–40 min · Enable SSH from the laptop
So this session can drive the board and pull results into the repo.

On the Jetson: `sudo apt install -y openssh-server && hostname -I`

On the laptop:
```bash
ssh <user>@<jetson-ip> "uname -m"      # expect: aarch64
ssh-copy-id <user>@<jetson-ip>
```
Then add to `~/.ssh/config` on the laptop:
```
Host jetson
    HostName <jetson-ip>
    User <user>
```
Verify: `ssh jetson "echo ok"` with no password prompt.

### 40–55 min · Start the BEVFusion downloads in the background
```bash
ssh jetson
git clone https://github.com/NVIDIA-AI-IOT/Lidar_AI_Solution.git
cd Lidar_AI_Solution/CUDA-BEVFusion
# follow the README links for model.zip and nuScenes-example-data.zip
```
Leave them downloading. Free at least **20 GB** first — both tracks plus engine builds.

### 55–60 min · Send me `jetson_info.txt`
Paste the contents here. It determines everything about the next step, and I can tell you
immediately whether you can proceed or must reflash.

**If you only manage two things: the two dataset registrations.** Everything else can be
done tomorrow; approval latency cannot be compressed.

---

## The shape of the project

**Spine (the year, on a proper GPU): cross-dataset generalisation of 3D perception.**
How much accuracy is lost when the domain changes, why, and whether it can be reduced.
This is **gap #1 in Prof. Liu's own documents** — *"cross-dataset domain gaps: sensor
layout, ego-frame conventions, class-name alignment"* — and it needs no borrowed hardware.

**Supporting axis (on the Jetson): what this costs on car-grade hardware.**

**The Jetson right now** is a screening instrument he lent you: prove the idea is worth a
year and that you can execute. Nothing is trained on it.

---

## Two tracks, and why both

A correction worth knowing: **V2XFusion is roadside/infrastructure perception**, one
camera plus one LiDAR on a roadside unit doing 3D detection. It is *not* vehicle-to-vehicle
fusion and *not* message security. Despite the name it is a perception project, which is
why your professor pointed at it.

| | **Track A — CUDA-BEVFusion** | **Track B — CUDA-V2XFusion** |
|---|---|---|
| Viewpoint | **Vehicle**, 6 cameras at road level | **Roadside**, elevated looking down |
| Dataset | **nuScenes** (example data ships) | **DAIR-V2X-I** (must download + convert to KITTI) |
| Backbone | ResNet50 / Swin-T | ResNet34 + PointPillars |
| Published Orin | R50 FP16 **67.89 mAP / 18 FPS**<br>R50-PTQ INT8 **67.66 mAP / 25 FPS** | FP16 dense **81 FPS**, sparsity **95**<br>INT8 dense **127**, sparsity **158** |
| Compression studied | FP16, INT8-PTQ | FP16/INT8 × dense/**sparsity** |
| Setup risk | Low — example data included | Higher — dataset access, plus patches from two repos |

**Why both is the right answer, not a compromise.** Same vendor, same architecture family,
same TensorRT toolchain, same INT8 PTQ method — **two different domains**. You do not have
to construct a domain shift; NVIDIA shipped you two. And the shift between them is
physically real: elevated roadside viewpoint versus road-level vehicle viewpoint, which is
exactly the *"sensor layout, ego-frame conventions"* failure in Liu's gap list.

Both publish an **in-domain** INT8 cost. The thesis question falls straight out:

> *In-domain, INT8 costs BEVFusion 0.23 mAP (67.89 → 67.66). Does compression still cost
> that little when the domain changes?*

Anchored to published numbers, on real data, no simulation anywhere.

---

## Stage 1 — bring-up (Days 1–3)

Run Track A first: it has example data, so it is the fastest route to a real number.
Track B starts as soon as DAIR-V2X-I lands.

### Track A — CUDA-BEVFusion
- [ ] Configure `tool/environment.sh` for the board's CUDA/TensorRT paths
- [ ] `bash tool/build_trt_engine.sh` (slow — let it run)
- [ ] `bash src/onnx/make_pb.sh && bash tool/run.sh`
- [ ] **Gate:** one successful inference on real nuScenes data

### Track B — CUDA-V2XFusion
- [ ] Convert DAIR-V2X-I to KITTI format per the README
- [ ] Clone BEVFusion, apply the BEVHeight and CUDA-V2XFusion patches
- [ ] Fetch the pretrained checkpoints from NVIDIA Box — **you are not training.** Ignore
      the `torchpack dist-run -np 8` command; that is training from scratch and needs 8 GPUs
- [ ] `scripts/ptq_v2xfusion.py` → `scripts/export_v2xfusion.py --precision [fp16|int8]`
- [ ] **Gate:** one successful inference on real DAIR-V2X-I data

**Failure branches:**

| Symptom | Action |
|---|---|
| TensorRT < 8.5 | Reflash JetPack, or fall back to `code/edge/` ONNX |
| OOM during engine build | Use **ResNet50**, not Swin-T. Close the desktop session. Add swap. |
| DAIR-V2X access denied or slow | Run Track A only; report Track B as in progress |
| Either build unresolved after 2 days | **Stop.** Fall back to `code/edge/`. Protect the schedule. |

---

## Stage 2 — measurement (Days 3–5)

- [ ] **2.1 Lock clocks, record the power mode.** 7 W and 15 W numbers are not comparable
      and must never share a table.
      ```bash
      ssh jetson "sudo nvpmodel -m 0 && sudo jetson_clocks && nvpmodel -q"
      ```
- [ ] **2.2 Every precision available in each track.** Latency, throughput, peak memory,
      power, max temperature.
- [ ] **2.3 Compare against the published Orin numbers and record the ratio.** This is your
      correctness check. Expect to be **well below** the published figures — those are Orin
      AGX, several times larger than an Orin Nano. Quantifying that ratio is itself a result.
- [ ] **2.4 Also benchmark the occupancy-shaped ONNX** in `code/edge/` — it is the
      architecture family the thesis targets and costs one command.
- [ ] **2.5 Pull results into the repo:** `scp -r jetson:~/bench/out_* results_jetson/`

---

## Stage 3 — evidence pack (Day 5)

- [ ] One plot: latency by precision, with a 100 ms (10 Hz) line
- [ ] One table: your numbers beside the published Orin numbers, both tracks
- [ ] One page: what was measured, the table and plot, three sentences on what it means,
      and **one honest paragraph on what it does not show**

**If nothing runs**, that is still a result — you measured the gap between a published
deployment model and the hardware you have. Write that sentence before the meeting.

---

## Stage 4 — proposal rewrite (Days 5–6)

Reuse the DSS structure in `PROPOSAL_v2.tex`: cover page, ≤3 body pages, title under 10
words, synopsis ≤250 words, sections A–E, Fall 2026 → Spring 2027, report due 30 May 2027.

- [ ] Remove every security element — attacks, threat model, adversary, trust, provenance,
      conformal risk control
- [ ] Spine = cross-dataset generalisation; edge deployment is one supporting section
- [ ] Cite FlashOcc, DG-BEV (7%-of-oracle collapse), Occ3D, UniOcc, CUDA-BEVFusion,
      CUDA-V2XFusion, and your own Jetson numbers as preliminary results
- [ ] Recheck the page budget
- [ ] Rename the project — "GhostGuard" is a security name

---

## Stage 5 — meeting and submission (Day 7)

- [ ] Send the one-pager **24 h ahead**, not in the room
- [ ] Lead with the measurement, not the plan
- [ ] Ask him four things:
      1. Does this slot into your `ngperception` program the way it looks like it does?
      2. Which GPU will I have for Phase 1?
      3. Can I keep Jetson access for Phase 2 in Dec–Jan, or is this a one-time loan?
      4. Could this contribute to the CVPR/ICCV submission your notes describe?
- [ ] Submit `Tran_ThucBao_DSS_F26.pdf` by 27 September

---

## Compute plan

| Machine | Job | When |
|---|---|---|
| **Laptop** (CPU) | ONNX export, analysis, plots, writing | Throughout |
| **Proper GPU** | Train, reproduce, all accuracy and cross-dataset evaluation | Phase 1 on |
| **Jetson Orin Nano** | Deployment measurement only — latency, memory, power | This week; Phase 2 if access continues |

---

## After approval: the year

| Phase | When | Machine | Deliverable |
|---|---|---|---|
| 1 — Reproduce | Oct–Nov | GPU | Hit a published number you either match or miss |
| 2 — Cross-dataset | Dec–Feb | GPU | Transfer measured across domains. **The spine.** |
| 3 — Compression × shift | Feb–Mar | GPU + Jetson | Does the in-domain INT8 cost grow under shift? |
| 4 — Write | Apr–May | Laptop | Report approved by 30 May 2027, Research Showcase |
