#!/bin/bash
bs='1000'
bn=`basename $1`
pardir=`dirname $1`
newMetaPath="${pardir}/${bn}_splits-of-${bs}/meta_od_track_${bn}.txt"

python3 split.py $1 --bs $bs 
python3 ptzaurusmeta2cvatxml_splits.py $newMetaPath --splitsof $bs
