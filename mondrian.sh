#!/bin/bash

# use randmoness to generate a recurrink
# occasionally sneak in a curated recurrink
# post on social media and measure popularity
# use ranking to improve RANDOM

model=$1
cell=$2

if [[ $# -lt 2 ]]
then
  echo "usage $0 model cell"
  exit 1
fi

# create SVG 

# ./input.py 
# --output z.svg
#  --scale SCALE    Scale in or out (0.5 - 2.0)  factor [0.5, 1.0, 2.0]
#  z.rink

# TOD these are supposed to be updated interactively :(
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

echo "
./effect.py
  --id ${cell}1
  --output ${model}.svg
  --shape ${shape}
  --width ${width}
  --facing ${facing}
  --size ${size} 
  --bg ${bg} 
  --top ${top} soleares.svg"

./effect.py \
  --id ${cell}1 \
  --output a.svg \
  --shape ${shape} \
  --width ${width} \
  --facing ${facing} \
  --size ${size} \
  --bg ${bg} \
  --top ${top} soleares.svg
