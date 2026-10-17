---
title: Jetson
tags:
  - context
  - hardware
---

# Jetson

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
