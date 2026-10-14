#!/bin/bash
# Jetson watchdog: every 5 minutes, check every running experiment for errors.
#
# Runs on the board itself under setsid, so it keeps checking whether or not anyone
# is connected. Each cycle appends to $LOG either one HEARTBEAT line (all clear, with
# load / memory / disk / temperature / job counts) or one ALERT line per problem.
# A heartbeat every cycle means silence is itself a signal: no new line within ~6
# minutes means the watchdog is dead, not that all is well.
#
# Each problem is reported once, the cycle it first appears, so a crashed log
# does not repeat the same alert forever.
#
#   setsid nohup ~/godeye/jetson_watchdog.sh >/dev/null 2>&1 </dev/null &
#   tail -f ~/godeye/out/WATCHDOG.log

INTERVAL=${INTERVAL:-300}
R=/home/sjsujetson/godeye
LOG=$R/out/WATCHDOG.log
SEEN=$R/out/.watchdog_seen
touch "$SEEN"
say() { echo "$(date -u +%FT%H:%M:%SZ) $*" >> "$LOG"; }
once() {                       # report a problem only the first time it is seen
  grep -qxF "$1" "$SEEN" && return 1
  echo "$1" >> "$SEEN"; return 0
}

say "WATCHDOG started, interval ${INTERVAL}s, pid $$"
while true; do
  alerts=0

  # 1. crash signatures in any experiment log
  for f in $(grep -lE "Traceback|CUDA error|out of memory|CUDA out of|Killed|Segmentation fault|core dumped|RuntimeError|AssertionError" \
             $R/out/teacher/*.log $R/out/repair/logs/*.log 2>/dev/null); do
    sig=$(grep -m1 -oE "Traceback|CUDA error|out of memory|Killed|Segmentation fault|core dumped|RuntimeError.{0,60}|AssertionError.{0,60}" "$f")
    once "crash:$f" && { say "ALERT crash in $(basename $f): $sig"; alerts=$((alerts+1)); }
  done

  # 2. any step that exited non-zero
  grep -hE "rc=[1-9]" $R/out/teacher/RUNS.status $R/out/repair/QUEUE.status 2>/dev/null | while read -r line; do
    once "rc:$line" && say "ALERT step failed: $line"
  done

  # 3. a runner that disappeared before writing its completion marker. Every runner
  #    logs <TAG>_START and <TAG>_DONE (v1 uses START / ALL_DONE), so any future
  #    teacher_runs_vN.sh is covered without editing this file.
  for f in $R/teacher_runs*.sh; do
    [ -e "$f" ] || continue
    base=$(basename "$f" .sh); ver=${base#teacher_runs}; ver=${ver#_}
    if [ -z "$ver" ]; then smark=START; dmark=ALL_DONE
    else tag=$(echo "$ver" | tr a-z A-Z); smark=${tag}_START; dmark=${tag}_DONE; fi
    status=$R/out/teacher/RUNS.status
    if grep -q "|$smark\$" "$status" 2>/dev/null && ! grep -q "|$dmark\$" "$status" 2>/dev/null        && ! pgrep -f "[${base:0:1}]${base:1}.sh" >/dev/null; then
      once "died:$base" && { say "ALERT runner $base died before $dmark"; alerts=$((alerts+1)); }
    fi
  done

  # 4. resources: memory, disk, temperature
  avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  disk=$(df /home | awk 'NR==2{print $5+0}')
  temp=$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -n | tail -1)
  temp=$(( ${temp:-0} / 1000 ))
  [ "$avail" -lt 400 ] && { say "ALERT low memory: ${avail} MB available"; alerts=$((alerts+1)); }
  [ "$disk" -gt 92 ]   && { say "ALERT disk ${disk}% full"; alerts=$((alerts+1)); }
  [ "$temp" -gt 85 ]   && { say "ALERT hot: ${temp} C"; alerts=$((alerts+1)); }

  jobs=$(pgrep -fc "python3 .*godeye/" 2>/dev/null)
  last=$(tail -1 $R/out/teacher/RUNS.status 2>/dev/null | cut -c1-80)
  say "HEARTBEAT load=$(cut -d' ' -f1 /proc/loadavg) mem_free=${avail}MB disk=${disk}% temp=${temp}C python_jobs=${jobs} | last: ${last}"
  sleep "$INTERVAL"
done
