#!/bin/bash
# v4: the airtight configuration (every prior from SOURCE labels, nothing chosen by
# looking at target labels, no road snapping) and the same plus YOLO's truck class.
set -u
R=/home/sjsujetson; T=$R/godeye/out/teacher; D=$R/godeye/dock.sh
TCFG=configs/V2X-I/det/centerhead/lssfpn/camera+pointpillar/resnet34/tumtraf_recal.yaml
PRED=$R/godeye/out/tumtraf/tumtraf_int8_outputs.pkl; Y=$T/yolo_eval1620.json
log(){ echo "$(date -u +%H:%M:%SZ)|$*" >> $T/RUNS.status; }
fit(){ $D "python3 $R/godeye/label_free_teacher.py $TCFG $PRED --start 540 $2 --out $T/$1.pkl" > $T/$1.fit.log 2>&1
       log "$1|FIT rc=$?|$(grep -o "wrote.*" $T/$1.fit.log | sed 's/.*pkl  //')"; }
evaluate(){ KITTI_CAR_LOOSE=1 $D "python3 $R/godeye/eval_subset.py $TCFG $2 --start 0" > $T/$1.eval.log 2>&1
  $D "python3 $R/godeye/cd_ap.py $TCFG $2 --start 0 --label $1" > $T/$1.cd.log 2>&1; log "$1|EVAL rc=$?"; }
B="--yolo $Y --mode teacher --yaw-offset-deg 0 --fit2d --size $T/size_srcLWH.json"
log "V4_START"
fit yolo4_src         "$B" &
fit yolo4_src_truck   "$B --coco 2,7" & wait
for n in yolo4_src yolo4_src_truck; do evaluate $n $T/$n.pkl; done
log "V4_DONE"
