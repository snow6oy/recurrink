#!/bin/bash

pid=/tmp/rink.pid

echo ${pid}

model=`readlink $pid | awk -v FS='_' '{print $1}'`

auth=`readlink $pid | awk -v FS='_' '{print $2}'`
view=`readlink $pid | awk -v FS='_' '{print $3}'`
echo "m ${model} v ${view} a ${author}"
