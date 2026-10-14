#!/bin/bash
# v5: recover the cars YOLO finds but LiDAR barely touches, via the ground plane.
# Same airtight priors as v4 (all from source labels). Waits for v4 to free the evaluator.
set -u
R=/home/sjsujetson; T=$R/godeye/out/teacher; D=$R/godeye/dock.sh
TCFG=configs/V2X-I/det/centerhead/lssfpn/camera+pointpillar/resnet34/tumtraf_recal.yaml
PRED=$R/godeye/out/tumtraf/tumtraf_int8_outputs.pkl; Y=$T/yolo_eval1620.json
log(){ echo "$(date -u +%H:%M:%SZ)|$*" >> $T/RUNS.status; }
fit(){ $D "python3 $R/godeye/label_free_teacher.py $TCFG $PRED --start 540 $2 --out $T/$1.pkl" > $T/$1.fit.log 2>&1
       log "$1|FIT rc=$?|$(grep -o "wrote.*" $T/$1.fit.log | sed 's/.*pkl  //')"; }
evaluate(){ KITTI_CAR_LOOSE=1 $D "python3 $R/godeye/eval_subset.py $TCFG $2 --start 0" > $T/$1.eval.log 2>&1
  $D "python3 $R/godeye/cd_ap.py $TCFG $2 --start 0 --label $1" > $T/$1.cd.log 2>&1; log "$1|EVAL rc=$?"; }
while ! grep -q V4_DONE $T/RUNS.status 2>/dev/null; do sleep 20; done
log "V5_START"
fit yolo5_mono "--yolo $Y --mode teacher --yaw-offset-deg 0 --fit2d --size $T/size_srcLWH.json --mono"
evaluate yolo5_mono $T/yolo5_mono.pkl
log "V5_DONE"
