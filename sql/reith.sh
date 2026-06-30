#!/bin/bash

RINKDIR='/Users/gavin/pCloud Drive/Art/rinks'
PLOTQ=/Users/gavin/Pictures/plotq
TMPDIR=/tmp/recurrink

model_name() {
  local id=$1
  info=$(./recurrink info -d ${id})
  name=$(echo $info|cut -d' ' -f 4)
  echo "$name"
}

add_to_queue() {
  local name=$1
  local id=$2
  if [ ! -d ${PLOTQ}/${id} ]
  then 
    mkdir ${PLOTQ}/${id}
  fi
  # build files
  for source in paint draw 
  do
    if [ -f "${TMPDIR}/${name}_${source}.svg" ]
    then
      mv "${TMPDIR}/${name}_${source}.svg" \
         "${PLOTQ}/${id}/${source}.svg"
      echo ${source}
    fi
  done 
  # exploded
  if [ -f "${TMPDIR}/${name}.svg" ]
  then
    mv "${TMPDIR}/${name}.svg" \
       "${PLOTQ}/${id}/${name}.svg"
  fi
  echo "${name} added to plot queue"
}

move_to_cloud() {
  local name=$1
  local id=$2
  if [ ! -d ${PLOTQ}/${id} ]
  then 
    echo "${PLOTQ}/${id} not found"
    exit
  fi
  mv -i ${PLOTQ}/${id} "${RINKDIR}"
  touch "${RINKDIR}/$id/$name"
  commit=$(./recurrink commit -d ${id})
  echo "${RINKDIR}/$id/$name"
  echo "$commit"
}

if [ "$#" -ne 2 ]
then
  echo "usage: cd recurrink"
  echo "$0 [-q | -c] rinkid"
  echo "  -q add to queue"
  echo "  -c move to cloud"
  exit
fi

arg=$1
rinkid=$2 # 08907cb891fe49644ecb1f56604a7cda

if [ "$arg" = '-q' ] 
then # push a rink to the plotq
  model=$(model_name ${rinkid})
  add_to_queue ${model} ${rinkid}
elif [ "$arg" = '-c' ]
then # move a plotted rink to the cloud
  model=$(model_name ${rinkid})
  move_to_cloud ${model} ${rinkid}
else
  echo "unknown $arg"
fi
# the
# end
