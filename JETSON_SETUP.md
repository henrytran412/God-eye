# Jetson Orin Nano — bring-up log

Board borrowed from Prof. Kaikai Liu to screen the proposal's feasibility. Nothing is
trained on it; it measures deployment cost only.

## Access

Connected over USB-C. The board runs its own DHCP on the link and is always `192.168.55.1`.

```
Host jetson
    HostName 192.168.55.1
    User sjsujetson
    IdentityFile ~/.ssh/jetson_ed25519
    IdentitiesOnly yes
```

Key auth is installed, so no password is needed and none is stored in this repo.

## What is on the board

| | |
|---|---|
| Board | Jetson Orin Nano Developer Kit, sm_87, 8 SMs |
| Memory | 7.3 GiB shared CPU/GPU, **no swap** |
| Disk | 915 GB NVMe, 826 GB free |
| L4T | **R39.2.0** (JetPack 7), Ubuntu 24.04.4 |
| Power modes | **only two**: `0` = 15 W, `1` = 7 W (base Orin Nano, not the 25 W "Super") |
| Host CUDA / TensorRT | **none** |
| Container | `cmpelkk/jetson-llm:latest` — CUDA 12.6, TensorRT 10.7.0, torch 2.6.0a0, Python 3.12 |

The host is deliberately bare; the whole stack lives in the container. The container is
built on **JetPack 6.1 (L4T R36.4)** and the host is **JetPack 7 (L4T R39.2)** — that
mismatch causes the one real problem below.

## Blocker: `libnvdla_compiler.so`, and the fix

Any TensorRT call failed with:

```
[E] Uncaught exception detected: Unable to open library: libnvinfer_plugin.so.10
    due to libnvdla_compiler.so: cannot open shared object file
```

Cause, in order:

1. `libnvinfer.so.10` has a hard `DT_NEEDED` on `libnvdla_compiler.so`.
2. The container ships only a **0-byte placeholder** at that path and expects the host to
   inject the real library.
3. The host's `/etc/nvidia-container-runtime/host-files-for-container.d/drivers.csv`
   still lists `libnvdla_compiler.so`, but **JetPack 7 does not ship it** — because
   **Orin Nano has no DLA hardware at all**. DLA is Orin NX / AGX only.
4. `nvidia-container-runtime` creates the mountpoint, finds no source to bind, and leaves
   a 0-byte file — destroying the container's own placeholder path.

So it is a stale entry in NVIDIA's own CSV, not a misconfiguration of this board.

**Fix.** Generate a stub exporting the 16 `nvdla::` symbols `libnvinfer.so.10` references,
and put it first on `LD_LIBRARY_PATH`. None of them is ever called — there is no DLA to
compile for. `code/edge/make_stub.sh` builds it:

```bash
scp code/edge/make_stub.sh jetson:~/godeye/
ssh jetson "docker run --rm -v /home/sjsujetson/godeye:/work \
    cmpelkk/jetson-llm:latest bash /work/make_stub.sh"
```

Verify:

```bash
ssh jetson "docker run --rm --runtime nvidia -v /home/sjsujetson/godeye:/work \
  cmpelkk/jetson-llm:latest bash -lc \
  'LD_LIBRARY_PATH=/work/lib python3 -c \"import tensorrt;print(tensorrt.__version__)\"'"
# -> 10.7.0
```

## Running a benchmark

`bench_trt.py` runs on the **host** (so `tegrastats`, `/sys` thermals and the power mode
are readable) and wraps each `trtexec` call in the container. The work directory is
bind-mounted at the *same absolute path* inside, so no path translation is needed.

```bash
ssh jetson "python3 ~/godeye/bench_trt.py \
    --onnx /home/sjsujetson/godeye/onnx/flashocc_shaped_skip.onnx \
    --docker-image cmpelkk/jetson-llm:latest \
    --stub-lib /home/sjsujetson/godeye/lib \
    --precisions fp32 fp16 --tag 15W --outdir ~/godeye/out"
```

## Open items

- **No internet on the board.** Its default route is the laptop over USB-C, which does not
  forward. WiFi hardware exists (`wlP1p1s0`) and a `SJSU_guest` profile is saved, but that
  network is not in range at the current location. Until this is fixed there is no
  `apt install`, no `docker pull`, and no downloading datasets on the board — everything
  must be `scp`'d from the laptop.
- **Clocks are not locked.** Observed CPU at 729–883 MHz during a build. `jetson_clocks`
  needs sudo and must be applied before any number is quoted, with the power mode recorded
  beside it. 7 W and 15 W results must never share a table.
- **RTC does not persist.** The board boots at epoch 0; set the date after every power
  cycle or timestamps in logs are meaningless.
