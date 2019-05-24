#!/bin/bash
set -e

source activate py2torch3
seed=${1:-0}
vocab="data/html/vocab.freq15.bin"
train_file="data/html/train.bin"
dev_file="data/html/dev.bin"
test_file="data/html/test.bin"
dropout=0.3
hidden_size=256
embed_size=128
action_embed_size=128
field_embed_size=64
type_embed_size=64
ptrnet_hidden_dim=32
lr=0.001
lr_decay=0.5
beam_size=15
lstm='lstm'  # lstm
model_name=model.sup.html.${lstm}.hidden${hidden_size}.embed${embed_size}.action${action_embed_size}.field${field_embed_size}.type${type_embed_size}.dropout${dropout}.lr${lr}.lr_decay${lr_decay}.beam_size${beam_size}.$(basename ${vocab}).$(basename ${train_file}).glorot.par_state_w_field_embe.seed${seed}

python exp.py \
    --seed ${seed} \
    --mode train \
    --batch_size 2 \
    --asdl_file asdl/lang/html/html_asdl.txt \
    --transition_system html \
    --evaluator html_evaluator \
    --train_file ${train_file} \
    --dev_file ${dev_file} \
    --vocab ${vocab} \
    --lstm ${lstm} \
    --no_parent_field_type_embed \
    --no_parent_production_embed \
    --hidden_size ${hidden_size} \
    --embed_size ${embed_size} \
    --action_embed_size ${action_embed_size} \
    --field_embed_size ${field_embed_size} \
    --type_embed_size ${type_embed_size} \
    --dropout ${dropout} \
    --patience 5 \
    --max_num_trial 5 \
    --glorot_init \
    --lr ${lr} \
    --lr_decay ${lr_decay} \
    --beam_size ${beam_size} \
    --log_every 50 \
    --save_to saved_models/html/${model_name} 2>logs/html/${model_name}.log

. my-scripts/html/test.sh saved_models/html/${model_name}.bin 2>>logs/html/${model_name}.log
