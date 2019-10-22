#!/bin/bash

data_name=${2}
test_file="data/html/${data_name}/test.bin"

python exp.py \
    --mode test \
    --load_model $1 \
    --beam_size 15 \
    --test_file ${test_file} \
    --save_decode_to decodes/html/${data_name}/$(basename $1).test.decode \
    --decode_max_time_step 100
