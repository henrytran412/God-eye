#!/bin/bash
# Run every queued repair experiment, in order, forever.
#
# Drop a new executable script into ~/godeye/repairs/ named NN_name.sh and this
# picks it up on the next scan -- no restart, no editing this file. Each one runs
# once; a marker in DONE/ stops it running again. When the queue empties the
# runner sleeps and rescans, so adding an experiment at 2am starts it at 2am
# rather than waiting for a human.
#
# Contract for a repair script:
#   - writes its own log to $LOGS/<name>.log
#   - appends one tab-separated summary line to $OUT/RESULTS.tsv
#   - exit 0 on success, non-zero on failure (the watcher greps for FAIL)
#
# Status lines land in $OUT/QUEUE.status, which the 5-minute watcher reads.

set -u
R=/home/sjsujetson
Q=$R/godeye/repairs
OUT=$R/godeye/out/repair
LOGS=$OUT/logs
DONE=$OUT/done
mkdir -p "$Q" "$LOGS" "$DONE"
touch "$OUT/RESULTS.tsv"

say() { echo "$(date -u +%H:%M:%SZ)|$*" >> "$OUT/QUEUE.status"; }

say "QUEUE|started"
while true; do
  ran=0
  for s in $(ls "$Q"/[0-9][0-9]_*.sh 2>/dev/null | sort); do
    name=$(basename "$s" .sh)
    [ -f "$DONE/$name" ] && continue
    [ -x "$s" ] || chmod +x "$s"
    ran=1
    say "$name|RUNNING"
    t0=$(date +%s)
    "$s" > "$LOGS/$name.log" 2>&1
    rc=$?
    t1=$(date +%s)
    if [ $rc -eq 0 ]; then
      say "$name|OK|${rc}|$((t1-t0))s"
    else
      say "$name|FAIL|rc=${rc}|$((t1-t0))s"
    fi
    # mark done either way; a failed experiment should not wedge the queue.
    # delete the marker by hand to retry after a fix.
    echo "rc=$rc $(date -u +%FT%TZ)" > "$DONE/$name"
  done
  [ $ran -eq 0 ] && { say "QUEUE|idle"; sleep 120; }
done
