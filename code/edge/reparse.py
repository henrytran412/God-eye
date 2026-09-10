"""Rebuild results.json from the raw trtexec logs.

The logs are the source of truth; results.json is derived. When a parsing bug
is fixed, this recovers the metrics from runs that already happened instead of
spending hours of GPU time re-measuring them.

  python3 reparse.py /home/sjsujetson/godeye/out/15W
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bench_trt import parse_trtexec  # noqa: E402


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    n = 0
    for rj in sorted(root.rglob("results.json")):
        payload = json.loads(rj.read_text())
        for rec in payload.get("results", []):
            log = rj.parent / f"trtexec_{rec['precision']}.log"
            if not log.exists():
                continue
            fresh = parse_trtexec(log.read_text(errors="ignore"))
            added = [k for k in fresh if k not in rec]
            rec.update(fresh)
            if added:
                print(f"  {rj.parent.name:32s} {rec['precision']:5s} +{','.join(added)}")
                n += 1
        rj.write_text(json.dumps(payload, indent=2))
    print(f"updated {n} record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
