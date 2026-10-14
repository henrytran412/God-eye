#!/bin/bash
# v2: corrected box convention for the oracle, plus 2D-guided refinement.
# Waits for v1 to finish so the shared evaluator output folder is never contended.
set -u
R=/home/sjsujetson; T=$R/godeye/out/teacher; D=$R/godeye/dock.sh
TCFG=configs/V2X-I/det/centerhead/lssfpn/camera+pointpillar/resnet34/tumtraf_recal.yaml
PRED=$R/godeye/out/tumtraf/tumtraf_int8_outputs.pkl
Y=$T/yolo_eval1620.json
log(){ echo "$(date -u +%H:%M:%SZ)|$*" >> $T/RUNS.status; }
fit(){ $D "python3 $R/godeye/label_free_teacher.py $TCFG $PRED --start 540 $2 --out $T/$1.pkl" > $T/$1.fit.log 2>&1
       log "$1|FIT rc=$?|$(grep -o "wrote.*" $T/$1.fit.log | sed 's/.*pkl  //')"; }
evaluate(){ KITTI_CAR_LOOSE=1 $D "python3 $R/godeye/eval_subset.py $TCFG $2 --start 0" > $T/$1.eval.log 2>&1
  $D "python3 $R/godeye/cd_ap.py $TCFG $2 --start 0 --label $1" > $T/$1.cd.log 2>&1; log "$1|EVAL rc=$?"; }
while ! grep -q ALL_DONE $T/RUNS.status 2>/dev/null; do sleep 20; done
log "V2_START"
fit oracleB_fix   "--oracle2d --mode teacher --yaw-offset-deg 0" &
fit oracleB_fit2d "--oracle2d --mode teacher --yaw-offset-deg 0 --fit2d" & wait
evaluate oracleB_fix   $T/oracleB_fix.pkl
evaluate oracleB_fit2d $T/oracleB_fit2d.pkl
fit yolo2_teacher "--yolo $Y --mode teacher --yaw-offset-deg 0 --fit2d" &
fit yolo2_both    "--yolo $Y --mode both    --yaw-offset-deg 0 --fit2d" & wait
fit yolo2_refine  "--yolo $Y --mode refine  --yaw-offset-deg 0 --fit2d" &
fit yolo2_union   "--yolo $Y --mode union   --yaw-offset-deg 0 --fit2d" & wait
for n in yolo2_teacher yolo2_both yolo2_refine yolo2_union; do evaluate $n $T/$n.pkl; done
log "V2_DONE"
