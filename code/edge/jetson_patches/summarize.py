"""Pull the moderate-difficulty AP out of an eval log and append one TSV row.

Car is scored at IoU 0.5, Pedestrian and Cyclist at 0.25 -- the same thresholds
the published tables use, so rows here drop straight into a comparison without
re-deriving which column is which.

  python3 summarize.py <label> <log> <results.tsv>
"""
import re
import sys

WANT = (("Car", "0.70, 0.50, 0.50"),
        ("Pedestrian", "0.50, 0.25, 0.25"),
        ("Cyclist", "0.50, 0.25, 0.25"))


def main() -> int:
    label, log, tsv = sys.argv[1], sys.argv[2], sys.argv[3]
    t = open(log, errors="ignore").read().replace("\r", "\n")
    row = [label]
    for cls, thr in WANT:
        m = re.findall(re.escape(cls) + r" AP@" + re.escape(thr) + r":\n(.*?)\naos",
                       t, re.S)
        if not m:
            row += ["-", "-"]
            continue
        d = {k.strip(): [float(x) for x in v.split(",")]
             for k, v in (l.split(" AP:") for l in m[-1].strip().split("\n"))}
        row += [f"{d['3d'][1]:.2f}", f"{d['bev'][1]:.2f}"]
    n = re.findall(r"predictions emitted: (\d+) \(([\d.]+) per frame\)", t)
    row.append(n[-1][1] if n else "-")
    with open(tsv, "a") as f:
        f.write("\t".join(row) + "\n")
    print("SUMMARY\t" + "\t".join(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
