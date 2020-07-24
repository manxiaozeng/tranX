#!/bin/bash

# conda environment py2torch3

model_path=${1}
data_name=${2}
cuda=${3}
test_file="data/html/${data_name}/test.bin"

exp_args=(
  --mode test
  --load_model $model_path
  --evaluator 'html_evaluator'
  --beam_size 15
  --test_file ${test_file}
  --save_decode_to decodes/html/${data_name}/$(basename $model_path).test.decode
  --decode_max_time_step 100
)

if [ ! -z "$cuda" ]; then
  echo 'Adding --cuda to test run'
  exp_args+=(--cuda);
fi

python exp.py "${exp_args[@]}"
