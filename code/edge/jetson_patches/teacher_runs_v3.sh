#!/bin/bash
# v3: honest priors. Length/width from SOURCE labels (allowed in adaptation);
# height floor either from source labels or label-free from target LiDAR (validated:
# 1.45 estimated vs 1.50 labelled). Road-direction yaw snapping isolated by an ablation.
set -u
R=/home/sjsujetson; T=$R/godeye/out/teacher; D=$R/godeye/dock.sh
TCFG=configs/V2X-I/det/centerhead/lssfpn/camera+pointpillar/resnet34/tumtraf_recal.yaml
PRED=$R/godeye/out/tumtraf/tumtraf_int8_outputs.pkl; Y=$T/yolo_eval1620.json
log(){ echo "$(date -u +%H:%M:%SZ)|$*" >> $T/RUNS.status; }
mk(){ python3 -c "import json;v=dict(median=$2);json.dump(dict(length=dict(median=$2,p75=$2,p90=$2),width=dict(median=$3,p75=$3,p90=$3),height=dict(median=$4,p75=$4,p90=$4)),open('$T/$1','w'))"; }
mk size_srcLWH.json 4.25 1.70 1.40          # all three from source labels
mk size_srcLW_tgtH.json 4.25 1.70 1.45      # source L/W, label-free target height
fit(){ $D "python3 $R/godeye/label_free_teacher.py $TCFG $PRED --start 540 $2 --out $T/$1.pkl" > $T/$1.fit.log 2>&1
       log "$1|FIT rc=$?|$(grep -o "wrote.*" $T/$1.fit.log | sed 's/.*pkl  //') $(grep -o "snapped.*" $T/$1.fit.log)"; }
evaluate(){ KITTI_CAR_LOOSE=1 $D "python3 $R/godeye/eval_subset.py $TCFG $2 --start 0" > $T/$1.eval.log 2>&1
  $D "python3 $R/godeye/cd_ap.py $TCFG $2 --start 0 --label $1" > $T/$1.cd.log 2>&1; log "$1|EVAL rc=$?"; }
B="--yolo $Y --mode teacher --yaw-offset-deg 0 --fit2d"
log "V3_START"
fit yolo3_src_roads   "$B --size $T/size_srcLWH.json --roads $T/priors.json" &
fit yolo3_tgtH_roads  "$B --size $T/size_srcLW_tgtH.json --roads $T/priors.json" & wait
fit yolo3_tgtH_noroad "$B --size $T/size_srcLW_tgtH.json"
for n in yolo3_src_roads yolo3_tgtH_roads yolo3_tgtH_noroad; do evaluate $n $T/$n.pkl; done
log "V3_DONE"
