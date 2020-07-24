#!/bin/bash

message=$1
data_name=$2

floyd run \
  --env pytorch-0.3:py2 \
  --gpu2 \
  -m "$message" \
  "chmod +x ./floyd_train.sh && ./floyd_train.sh $data_name true"
