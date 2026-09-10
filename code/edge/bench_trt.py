"""Benchmark an ONNX model on a Jetson with TensorRT, at FP32 / FP16 / INT8.

Runs ON THE JETSON. Copy this file plus the .onnx over and run it there.

Design choice worth stating: this drives `trtexec`, the CLI that ships with
TensorRT, rather than the TensorRT Python bindings. The Python path needs
correct device-buffer management, a working pycuda or cuda-python install, and
a hand-written INT8 calibrator -- three things that can each silently produce a
wrong number. `trtexec` is NVIDIA's own benchmarking tool, it reports latency
percentiles directly, and when it fails it fails loudly. For a first
measurement that has to be trustworthy, that trade is worth it.

Power and thermal state are captured from `tegrastats` alongside each run,
because a latency number from a throttled device is not a latency number. The
script also records the active power mode: an Orin Nano at 7 W and the same
board at 15 W are effectively different machines, and results are not
comparable across them.

  python3 bench_trt.py --onnx backbone_r50_6x256x704.onnx
  python3 bench_trt.py --onnx model.onnx --precisions fp16 int8 --iterations 500

NOT YET RUN ON HARDWARE. Written against the TensorRT 8.5/10.x trtexec output
format; if parsing fails the raw log is kept in the output directory so nothing
is lost.
"""
import argparse
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import threading
import time

TRTEXEC_CANDIDATES = [
    "/usr/src/tensorrt/bin/trtexec",
    "/usr/local/tensorrt/bin/trtexec",
    "trtexec",
]


def find_trtexec() -> str | None:
    for c in TRTEXEC_CANDIDATES:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


def trtexec_command(docker_image: str, stub_lib: str, mount: str) -> list[str] | None:
    """Return the argv PREFIX that invokes trtexec, host-native or in a container.

    On JetPack 7 (L4T r39.x) the host ships no TensorRT at all -- the stack lives
    in a JetPack 6 container. Two consequences handled here:

    * The container is mounted at the SAME absolute path as the host directory,
      so every --onnx=/abs/path argument resolves identically either way and the
      rest of this script needs no path translation.
    * Orin Nano has no DLA hardware, so JetPack 7 does not ship
      libnvdla_compiler.so -- but the host's drivers.csv still lists it, so
      nvidia-container-runtime truncates the container's copy to 0 bytes and
      libnvinfer.so.10 (which DT_NEEDEDs it) fails to load. --stub-lib puts a
      directory holding a generated stub first on LD_LIBRARY_PATH. Nothing in
      the stub is ever called; there is no DLA to compile for.
    """
    if not docker_image:
        found = find_trtexec()
        return [found] if found else None
    cmd = ["docker", "run", "--rm", "--runtime", "nvidia", "-v", f"{mount}:{mount}"]
    if stub_lib:
        cmd += ["-e", f"LD_LIBRARY_PATH={stub_lib}:/usr/lib/aarch64-linux-gnu"]
    cmd += [docker_image, "/usr/src/tensorrt/bin/trtexec"]
    return cmd


# ---------------------------------------------------------------- device info


def read_first(*paths: str) -> str | None:
    for p in paths:
        try:
            return pathlib.Path(p).read_text(errors="ignore").strip()
        except OSError:
            continue
    return None


def device_info() -> dict:
    info = {
        "hostname": platform.node(),
        "machine": platform.machine(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "model": read_first("/proc/device-tree/model"),
        "l4t": read_first("/etc/nv_tegra_release"),
        "jetpack": None,
        "cuda": None,
        "tensorrt": None,
        "power_mode": None,
        "mem_total_kb": None,
    }
    if info["model"]:
        info["model"] = info["model"].replace("\x00", "").strip()

    meminfo = read_first("/proc/meminfo") or ""
    m = re.search(r"MemTotal:\s+(\d+)", meminfo)
    if m:
        info["mem_total_kb"] = int(m.group(1))

    v = read_first("/usr/local/cuda/version.json")
    if v:
        try:
            info["cuda"] = json.loads(v).get("cuda", {}).get("version")
        except json.JSONDecodeError:
            pass
    if not info["cuda"]:
        out = run_quiet(["nvcc", "--version"])
        if out:
            m = re.search(r"release (\d+\.\d+)", out)
            info["cuda"] = m.group(1) if m else None

    out = run_quiet(["dpkg-query", "-W", "-f=${Version}", "tensorrt"])
    if out:
        info["tensorrt"] = out.strip()

    out = run_quiet(["nvpmodel", "-q"])
    if out:
        info["power_mode"] = " / ".join(
            l.strip() for l in out.splitlines() if l.strip())
    return info


def run_quiet(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------- tegrastats


class TegraMonitor:
    """Sample tegrastats in a thread while a benchmark runs."""

    def __init__(self, interval_ms: int = 200):
        self.interval_ms = interval_ms
        self.samples: list[str] = []
        self._proc = None
        self._thread = None
        self._stop = threading.Event()

    def _pump(self):
        try:
            self._proc = subprocess.Popen(
                ["tegrastats", "--interval", str(self.interval_ms)],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        except (OSError, subprocess.SubprocessError):
            return
        for line in self._proc.stdout:
            if self._stop.is_set():
                break
            self.samples.append(line.strip())

    def __enter__(self):
        self._thread = threading.Thread(target=self._pump, daemon=True)
        self._thread.start()
        time.sleep(0.5)
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self._proc:
            self._proc.terminate()
        return False

    def summary(self) -> dict:
        """Peak RAM, peak GPU load, mean power, max temperature."""
        ram, gpu, pwr, temp = [], [], [], []
        for s in self.samples:
            m = re.search(r"RAM (\d+)/(\d+)MB", s)
            if m:
                ram.append(int(m.group(1)))
            m = re.search(r"GR3D_FREQ (\d+)%", s)
            if m:
                gpu.append(int(m.group(1)))
            # VDD_IN 4500mW/4200mW  or  POM_5V_IN 4500/4200
            for m in re.finditer(r"(VDD_IN|POM_5V_IN|VDD_GPU_SOC)\s+(\d+)mW", s):
                pwr.append(int(m.group(2)))
            for m in re.finditer(r"(?:cpu|gpu|tj)@([\d.]+)C", s):
                temp.append(float(m.group(1)))
        out = {"n_samples": len(self.samples)}
        if ram:
            out["ram_peak_mb"] = max(ram)
        if gpu:
            out["gpu_util_mean_pct"] = round(sum(gpu) / len(gpu), 1)
        if pwr:
            out["power_mean_mw"] = round(sum(pwr) / len(pwr))
            out["power_peak_mw"] = max(pwr)
        if temp:
            out["temp_max_c"] = max(temp)
        return out


# ---------------------------------------------------------------- benchmark


LAT_KEYS = {
    "min": r"min = ([\d.]+) ms",
    "max": r"max = ([\d.]+) ms",
    "mean": r"mean = ([\d.]+) ms",
    "median": r"median = ([\d.]+) ms",
    "p90": r"percentile\(90%?\) = ([\d.]+) ms",
    "p99": r"percentile\(99%?\) = ([\d.]+) ms",
}


def parse_trtexec(log: str) -> dict:
    res: dict = {}
    # "GPU Compute Time: min = ... max = ... mean = ... median = ... percentile(99%) = ..."
    block = ""
    for line in log.splitlines():
        if "GPU Compute Time" in line:
            block = line
    target = block or log
    for name, pat in LAT_KEYS.items():
        m = re.search(pat, target)
        if m:
            res[f"gpu_{name}_ms"] = float(m.group(1))
    m = re.search(r"Throughput: ([\d.]+) qps", log)
    if m:
        res["throughput_qps"] = float(m.group(1))
    m = re.search(r"Latency: min = ([\d.]+) ms.*?median = ([\d.]+) ms", log, re.S)
    if m:
        res["e2e_min_ms"] = float(m.group(1))
        res["e2e_median_ms"] = float(m.group(2))
    return res


def bench_one(trtexec: list[str], onnx: pathlib.Path, precision: str,
              iterations: int, warmup_ms: int, workspace_mb: int,
              outdir: pathlib.Path, extra: list[str]) -> dict:
    cmd = [*trtexec, f"--onnx={onnx}", f"--iterations={iterations}",
           f"--warmUp={warmup_ms}", "--avgRuns=100", "--noDataTransfers",
           "--useSpinWait", "--separateProfileRun"]
    # memory-pool flag name changed across TensorRT majors; pass both forms and
    # let trtexec ignore the one it does not recognise is NOT safe -- it errors.
    # So pick based on --help text.
    help_txt = run_quiet([*trtexec, "--help"]) or ""
    if "--memPoolSize" in help_txt:
        cmd.append(f"--memPoolSize=workspace:{workspace_mb}M")
    elif "--workspace" in help_txt:
        cmd.append(f"--workspace={workspace_mb}")

    if precision == "fp16":
        cmd.append("--fp16")
    elif precision == "int8":
        cmd.append("--int8")
        # No calibration cache: trtexec falls back to dynamic-range guessing,
        # which is fine for LATENCY but produces meaningless ACCURACY. This
        # script measures latency only -- accuracy under INT8 needs a real
        # calibrator over real images, which is Phase 2 of the project.
    elif precision == "best":
        cmd.append("--best")
    cmd += extra

    print(f"\n=== {precision.upper()} ===")
    print(" ".join(cmd))
    t0 = time.time()
    with TegraMonitor() as mon:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=3600)
        except subprocess.TimeoutExpired:
            return {"precision": precision, "error": "timeout after 3600s"}
        tegra = mon.summary()
    log = (proc.stdout or "") + (proc.stderr or "")
    (outdir / f"trtexec_{precision}.log").write_text(log, errors="ignore")

    rec = {"precision": precision, "returncode": proc.returncode,
           "wall_s": round(time.time() - t0, 1), **tegra}
    if proc.returncode != 0:
        rec["error"] = "trtexec failed - see log"
        tail = [l for l in log.splitlines() if l.strip()][-6:]
        rec["tail"] = tail
        for l in tail:
            print("   ", l)
        return rec
    rec.update(parse_trtexec(log))
    if "gpu_median_ms" in rec:
        print(f"    median {rec['gpu_median_ms']:.2f} ms  "
              f"p99 {rec.get('gpu_p99_ms', float('nan')):.2f} ms  "
              f"{rec.get('throughput_qps', float('nan')):.1f} qps")
        if "ram_peak_mb" in rec:
            print(f"    peak RAM {rec['ram_peak_mb']} MB  "
                  f"power {rec.get('power_mean_mw', '?')} mW  "
                  f"max temp {rec.get('temp_max_c', '?')} C")
    else:
        print("    could not parse latency - raw log kept")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--precisions", nargs="+", default=["fp32", "fp16", "int8"],
                    choices=["fp32", "fp16", "int8", "best"])
    ap.add_argument("--iterations", type=int, default=200)
    ap.add_argument("--warmup-ms", type=int, default=2000)
    ap.add_argument("--workspace-mb", type=int, default=2048)
    ap.add_argument("--outdir", default="bench_out")
    ap.add_argument("--tag", default="", help="label for this run, e.g. '15W'")
    ap.add_argument("--docker-image", default="",
                    help="run trtexec inside this image (JetPack 7 hosts have no "
                         "host TensorRT); e.g. cmpelkk/jetson-llm:latest")
    ap.add_argument("--stub-lib", default="",
                    help="dir holding a stub libnvdla_compiler.so, put first on "
                         "LD_LIBRARY_PATH inside the container")
    ap.add_argument("--mount", default="",
                    help="host dir bind-mounted at the same path in the container "
                         "(default: parent of --onnx)")
    ap.add_argument("--extra", nargs=argparse.REMAINDER, default=[],
                    help="extra flags passed through to trtexec")
    args = ap.parse_args()

    onnx = pathlib.Path(args.onnx)
    if not onnx.exists():
        print(f"ERROR: {onnx} not found")
        return 1
    onnx = onnx.resolve()
    mount = args.mount or str(onnx.parent)
    trtexec = trtexec_command(args.docker_image, args.stub_lib, mount)
    if not trtexec:
        print("ERROR: trtexec not found. On JetPack it is usually at")
        print("       /usr/src/tensorrt/bin/trtexec")
        print("       Install with: sudo apt install tensorrt")
        print("       On JetPack 7 the host ships no TensorRT; the stack is in a")
        print("       container. Re-run with --docker-image <image> --stub-lib <dir>.")
        return 1

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    info = device_info()
    print("device:")
    for k, v in info.items():
        if v is not None:
            print(f"  {k:12s} {v}")
    print(f"\nonnx: {onnx.name} ({onnx.stat().st_size/1e6:.1f} MB)")
    print(f"trtexec: {' '.join(trtexec)}")
    if info.get("mem_total_kb") and info["mem_total_kb"] < 9_000_000:
        print("\nNOTE: <9 GB total RAM. If engine builds are killed by the OOM "
              "reaper, lower --workspace-mb or add a swapfile.")

    results = []
    for p in args.precisions:
        results.append(bench_one(trtexec, onnx, p, args.iterations,
                                 args.warmup_ms, args.workspace_mb, outdir,
                                 args.extra))

    payload = {"device": info, "onnx": str(onnx), "tag": args.tag,
               "iterations": args.iterations, "results": results}
    (outdir / "results.json").write_text(json.dumps(payload, indent=2))

    print(f"\n{'precision':<10} {'median ms':>10} {'p99 ms':>9} {'qps':>9} "
          f"{'RAM MB':>8} {'mW':>7}")
    for r in results:
        if "gpu_median_ms" in r:
            print(f"{r['precision']:<10} {r['gpu_median_ms']:>10.2f} "
                  f"{r.get('gpu_p99_ms', 0):>9.2f} "
                  f"{r.get('throughput_qps', 0):>9.1f} "
                  f"{r.get('ram_peak_mb', 0):>8} "
                  f"{r.get('power_mean_mw', 0):>7}")
        else:
            print(f"{r['precision']:<10} {'FAILED':>10}  {r.get('error','')}")
    print(f"\nwrote {outdir/'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
