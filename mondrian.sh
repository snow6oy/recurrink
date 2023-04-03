#!/bin/bash

# use randmoness to generate a recurrink
# then later ..
# post on social media and measure popularity (occasionally sneak in a curated recurrink?)
# use ranking to improve RANDOM

model=$1
if [ ! -f "SVG/${model}.svg" ]
then
  echo "File not found!"
  exit 1
fi

cells=$(./recurrink.py -c ${model})
if [ -z "$cells" ]
then
  echo "cannot find cells for ${model}"
  exit 1
fi

# create SVG 

# ./input.py 
# --output SVG/z.svg
#  --scale SCALE    Scale in or out (0.5 - 2.0)  factor [0.5, 1.0, 2.0]
#  z.rink

# TODO these are supposed to be updated interactively :(
# 'fill': '#fff',
# 'fill_opacity':1.0,
# 'stroke':'#000',
# 'stroke_dasharray': 0,
# 'stroke_opacity':1.0,

get_random_index() {
  i=$((0 + $RANDOM % $1))
  return $i
}

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
for cell in ${cells}
do
  # default 'stroke_width': 0
  get_random_index 10
  width=$?

  # pretend to pass arg in order to fool the syntax highlighter
  shapes 1
  shape_facing 1
  shape_size  1
  top_boolean 1
  background_colour 1

  # update cells
  echo "${cell} ${model}"
  echo "${cell},${model},${shape},${width},${facing},${size},${bg},${top}" >>mondrian.log
./effect.py \
   --id ${cell}1 \
   --output SVG/${model}.svg \
   --shape ${shape} \
   --width ${width} \
   --facing ${facing} \
   --size ${size} \
   --bg ${bg} \
   --top ${top} SVG/${model}.svg
done
