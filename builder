#!/bin/bash

# usage ./builder /tmp/soleares.csv

basedir=/home/gavin/Pictures/artWork/recurrences
model=${1%.*}  # retain the part before the colon
model=${model##*/}  # retain the part after the last slash
digest=$(./recurrink.py -m ${model} --output JSON)

if [ -f "${basedir}/${model}/h/${digest}.json" ]
then
  echo "File '$digest.json' exits, not overwriting"
  exit 1
else
  mv "/tmp/${digest}.json" "$basedir/${model}/h/${digest}.json"
fi
echo $digest
