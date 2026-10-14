#!/bin/bash
# Label-free teacher: convention gate first, then the four YOLO modes.
# Fits write separate pickles so they may run in parallel; evaluations share the
# config's result_root, so they run strictly one at a time.
set -u
R=/home/sjsujetson; T=$R/godeye/out/teacher; D=$R/godeye/dock.sh
TCFG=configs/V2X-I/det/centerhead/lssfpn/camera+pointpillar/resnet34/tumtraf_recal.yaml
PRED=$R/godeye/out/tumtraf/tumtraf_int8_outputs.pkl
log(){ echo "$(date -u +%H:%M:%SZ)|$*" >> $T/RUNS.status; }
fit(){ $D "python3 $R/godeye/label_free_teacher.py $TCFG $PRED --start 540 $2 --out $T/$1.pkl" > $T/$1.fit.log 2>&1
       log "$1|FIT rc=$?|$(grep -o "wrote.*" $T/$1.fit.log | sed 's/.*pkl  //')"; }
evaluate(){ local pkl=$2 start=$3
  KITTI_CAR_LOOSE=1 $D "python3 $R/godeye/eval_subset.py $TCFG $pkl --start $start" > $T/$1.eval.log 2>&1
  $D "python3 $R/godeye/cd_ap.py $TCFG $pkl --start $start --label $1" > $T/$1.cd.log 2>&1
  log "$1|EVAL rc=$?"; }
bev(){ python3 - "$1" <<'PY'
import re,sys
t=open(sys.argv[1],errors="ignore").read().replace("\r","\n")
m=re.findall(r"Car AP@0\.70, 0\.50, 0\.50:\n.*?\nbev  AP:([\d.]+), ([\d.]+)",t,re.S)
print(m[-1][1] if m else "0")
PY
}
: > $T/RUNS.status; log "START"
while ! grep -q "rc=" $T/yolo.log 2>/dev/null; do sleep 15; done; log "yolo|$(grep -o 'wrote.*' $T/yolo.log)"

# --- phase A: is the yaw convention right? perfect 2D boxes, two offsets ---
fit oracle_m90 "--oracle2d --mode teacher --yaw-offset-deg -90" & fit oracle_0 "--oracle2d --mode teacher --yaw-offset-deg 0" & wait
evaluate baseline $PRED 540
evaluate oracle_m90 $T/oracle_m90.pkl 0
evaluate oracle_0   $T/oracle_0.pkl 0
A=$(bev $T/oracle_m90.eval.log); B=$(bev $T/oracle_0.eval.log)
OFF=$(python3 -c "print(-90 if float('$A')>=float('$B') else 0)")
log "convention|oracle BEV@0.5 m90=$A off0=$B -> yaw offset $OFF"

# --- phase B: YOLO-driven teacher, four ways ---
fit yolo_teacher "--yolo $T/yolo_eval1620.json --mode teacher --yaw-offset-deg $OFF" & fit yolo_refine "--yolo $T/yolo_eval1620.json --mode refine --yaw-offset-deg $OFF" & wait
fit yolo_union "--yolo $T/yolo_eval1620.json --mode union --yaw-offset-deg $OFF" & fit yolo_both "--yolo $T/yolo_eval1620.json --mode both --yaw-offset-deg $OFF" & wait
for n in yolo_teacher yolo_refine yolo_union yolo_both; do evaluate $n $T/$n.pkl 0; done
log "ALL_DONE"
