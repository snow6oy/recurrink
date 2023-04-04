#!/bin/bash

# use randmoness to generate a recurrink
# then later ..
# post on social media and measure popularity (occasionally sneak in a curated recurrink?)
# use ranking to improve RANDOM

# TODO these are supposed to be updated interactively : need to update effect.py
# 'fill': '#fff',
# 'fill_opacity':1.0,
# 'stroke':'#000',
# 'stroke_dasharray': 0,
# 'stroke_opacity':1.0,

model_path=$(ls -1 models/*.rink| sort -R| tail -1)
model=${model_path%.*}  # retain the part before the colon
model=${model##*/}  # retain the part after the last slash
echo $model

# do a RINK test
if [ ! -f ${model_path} ]
then
  echo "File '$model_path' not found! Run recurrink.py -a"
  exit 1
fi

cells=$(./recurrink.py -c ${model})
if [ -z "${cells}" ]
then
  echo "cannot find cells for ${model}"
  exit 1
fi

get_random_index() {
  i=$((0 + $RANDOM % $1))
  return $i
}

factor() {
  declare -a a=(0.5 1.0 2.0)
  get_random_index 3
  scale=${a[$?]}
}

factor 1
# create SVG from RINK
./input.py --output /tmp/$model.svg --scale $scale $model_path

# default 'shape':'square',
shapes() {
  declare -a a=("circle" "line" "square" "triangle")
  get_random_index 4
  shape=${a[$?]}
}

# default 'shape_facing':'north',
shape_facing() {
  declare -a a=("north" "south" "east" "west")
  get_random_index 4
  facing=${a[$?]}
}

# default 'shape_size':'medium',
# call this after shapes
shape_size() {
  declare -a a=("medium" "large")
  if [ "$shape" = "triangle" ]
  then
    size="medium"
  else
    get_random_index 2
    size=${a[$?]}
  fi
}

# default 'top':False
top_boolean() {
  declare -a a=("True" "False")
  get_random_index 2
  top=${a[$?]}
}

background_colour() {
  declare -i a=("orange" "crimson" "indianred" "mediumvioletred" "indigo" "limegreen" "yellowgreen" "black" "white" "gray")
  get_random_index 10
  bg=${a[$?]}
}

# update cell attributes
echo "updating $model"
for cell in ${cells}
do
  get_random_index 10
  width=$?  # default 'stroke_width': 0

  # pretend to pass arg in order to fool the syntax highlighter
  shapes 1
  shape_facing 1
  shape_size  1
  top_boolean 1
  background_colour 1

  # update cells
  echo "${cell},${model},${shape},${width},${facing},${size},${bg},${top}" >>mondrian.log
  data="${data},${cell},${model},${shape},${width},${facing},${size},${bg},${top}"
  echo -n "$cell" 
./effect.py \
   --id ${cell}1 \
   --output /tmp/${model}.svg \
   --shape ${shape} \
   --width ${width} \
   --facing ${facing} \
   --size ${size} \
   --bg ${bg} \
   --top ${top} /tmp/${model}.svg
done

digest=$(./recurrink.py -m ${model} -d ${data})
/bin/mv "/tmp/${model}.svg" "SVG/${digest}.svg"
echo "drew new recurrink in SVG"
echo "${digest}.svg"
