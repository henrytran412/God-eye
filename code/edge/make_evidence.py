"""Turn the Jetson sweep results into the table and plot for the evidence pack.

  python code/edge/make_evidence.py results_jetson/15W

Writes results_jetson/<tag>/EVIDENCE.md and latency.png. Reads only
results.json files, so it runs on the laptop with no Jetson attached.
"""
import json
import pathlib
import sys

RT_BUDGET_MS = 100.0  # 10 Hz, the conventional AV perception line


def load(root: pathlib.Path) -> dict:
    out = {}
    for rj in sorted(root.rglob("results.json")):
        d = json.loads(rj.read_text())
        out[rj.parent.name] = d
    return out


def table(data: dict) -> list[str]:
    L = ["| model | precision | e2e ms | GPU ms | qps | power W | peak RAM MB | max °C | 10 Hz |",
         "|---|---|---|---|---|---|---|---|---|"]
    for model, d in data.items():
        for r in d["results"]:
            if r.get("returncode") != 0 or "e2e_median_ms" not in r:
                L.append(f"| {model} | {r['precision']} | FAILED | | | | | | |")
                continue
            e2e = r["e2e_median_ms"]
            ok = "PASS" if e2e < RT_BUDGET_MS else "**FAIL**"
            L.append(
                f"| {model} | {r['precision']} | {e2e:.2f} | {r.get('gpu_median_ms', 0):.2f} | "
                f"{r.get('throughput_qps', 0):.2f} | {r.get('power_mean_mw', 0)/1000:.1f} | "
                f"{r.get('ram_peak_mb', 0)} | {r.get('temp_max_c', 0):.1f} | {ok} |")
    return L


def view_transform_cost(data: dict) -> list[str]:
    """scatter - skip, per precision. The two differ ONLY by the LSS view
    transform, so the difference is that operator's cost in isolation."""
    a, b = data.get("flashocc_shaped_scatter"), data.get("flashocc_shaped_skip")
    if not (a and b):
        return []
    ma = {r["precision"]: r for r in a["results"]}
    mb = {r["precision"]: r for r in b["results"]}
    L = ["", "### Cost of the LSS view transform (scatter - skip)", "",
         "| precision | with | without | cost ms | share of frame |", "|---|---|---|---|---|"]
    for p in ("fp32", "fp16", "int8"):
        if p not in ma or p not in mb:
            continue
        x, y = ma[p].get("e2e_median_ms"), mb[p].get("e2e_median_ms")
        if x is None or y is None:
            continue
        L.append(f"| {p} | {x:.2f} | {y:.2f} | **{x-y:.2f}** | {(x-y)/x*100:.0f}% |")
    return L


def stage_breakdown(data: dict) -> list[str]:
    """Decompose the frame into three stages by differencing the three models.

    backbone_r50            = image backbone alone
    skip - backbone         = BEV encoder + occupancy head
    scatter - skip          = LSS view transform

    The models are identical except for the stage each adds, so the differences
    isolate each stage's cost without any profiler instrumentation.
    """
    need = ("backbone_r50_6x256x704", "flashocc_shaped_skip", "flashocc_shaped_scatter")
    if not all(k in data for k in need):
        return []
    g = {k: {r["precision"]: r.get("e2e_median_ms") for r in data[k]["results"]} for k in need}
    L = ["", "### Where the frame goes, and what compresses", "",
         "| precision | backbone | BEV enc + head | view transform | total |",
         "|---|---|---|---|---|"]
    rows = {}
    for pr in ("fp32", "fp16", "int8"):
        b  = g[need[0]].get(pr)
        sk = g[need[1]].get(pr)
        sc = g[need[2]].get(pr)
        if None in (b, sk, sc):
            continue
        rows[pr] = (b, sk - b, sc - sk, sc)
        L.append(f"| {pr} | {b:.2f} ({b/sc*100:.0f}%) | {sk-b:.2f} ({(sk-b)/sc*100:.0f}%) | "
                 f"{sc-sk:.2f} ({(sc-sk)/sc*100:.0f}%) | {sc:.2f} |")
    if "fp32" in rows and "int8" in rows:
        f, i = rows["fp32"], rows["int8"]
        L += ["", "| stage | FP32 -> INT8 speedup |", "|---|---|"]
        for name, idx in (("backbone", 0), ("BEV enc + head", 1), ("view transform", 2)):
            L.append(f"| {name} | **{f[idx]/i[idx]:.2f}x** |")
        L += ["", "The view transform is a scatter into a 200x200 BEV grid -- memory-bound, "
              "not compute-bound -- so quantisation does almost nothing for it. As the "
              "compute-bound stages shrink, it becomes a hard floor on what compression "
              "can buy for this architecture."]
    return L


def plot(data: dict, out: pathlib.Path) -> str | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    order = ["fp32", "fp16", "int8"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for model, d in data.items():
        m = {r["precision"]: r.get("e2e_median_ms") for r in d["results"]}
        xs = [p for p in order if m.get(p)]
        ax.plot(xs, [m[p] for p in xs], marker="o", label=model)
    ax.axhline(RT_BUDGET_MS, ls="--", c="crimson")
    ax.text(0.02, RT_BUDGET_MS + 2, "100 ms (10 Hz) real-time budget",
            color="crimson", transform=ax.get_yaxis_transform(), fontsize=9)
    ax.set_ylabel("end-to-end latency (ms, median)")
    ax.set_title("Jetson Orin Nano, 15 W, clocks locked")
    ax.legend(fontsize=8)
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    return str(out)


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results_jetson/15W")
    data = load(root)
    if not data:
        print(f"no results.json under {root}")
        return 1
    dev = next(iter(data.values()))["device"]
    lines = [f"# Jetson evidence pack — {root.name}", "",
             f"Board: {dev.get('model')}  |  {dev.get('power_mode')}  |  "
             f"{dev.get('mem_total_kb', 0)//1024} MB RAM", "",
             "**Weights are random — these are cost measurements, not accuracy.** "
             "Latency is set by architecture and tensor shapes, so it is representative; "
             "no accuracy claim is made or implied.", ""]
    lines += table(data)
    lines += view_transform_cost(data)
    lines += stage_breakdown(data)
    png = plot(data, root / "latency.png")
    if png:
        lines += ["", f"![latency]({pathlib.Path(png).name})"]
    (root / "EVIDENCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {root/'EVIDENCE.md'}" + (f" and {png}" if png else " (no matplotlib, plot skipped)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
