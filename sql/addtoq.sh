# push a rink to the plotq

if [ "$#" -ne 2 ]
then
  echo "usage: $0 MODEL RINKID"
  exit
fi

MODEL=$1
RINKID=$2
PLOTQ=/Users/gavin/Pictures/plotq
TMPDIR=/tmp/recurrink

if [ ! -d ${PLOTQ}/${RINKID} ]
then 
  mkdir ${PLOTQ}/${RINKID}
fi
# build files
for source in paint draw 
do
  if [ -f "${TMPDIR}/${MODEL}_${source}.svg" ]
  then
    mv "${TMPDIR}/${MODEL}_${source}.svg" \
       "${PLOTQ}/${RINKID}/${source}.svg"
    echo ${source}
  fi
done 
# exploded
if [ -f "${TMPDIR}/${MODEL}.svg" ]
then
  mv "${TMPDIR}/${MODEL}.svg" \
     "${PLOTQ}/${RINKID}/${MODEL}.svg"
fi
echo "${MODEL} added to plot queue"
