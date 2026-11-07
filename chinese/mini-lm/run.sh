#!/bin/sh
# 用法: ./run.sh [語料目錄...]
#   ./run.sh                                  # 預設 corpus/planets
#   ./run.sh corpus/minilang
#   ./run.sh corpus/planets corpus/minilang   # 合併多個語料
# 其他參數用環境變數傳入，例如:
#   PRETRAIN_ARGS="--max_iters 2000" ./run.sh corpus/minilang
set -e
cd "$(dirname "$0")"
[ $# -eq 0 ] && set -- corpus/planets
# python gen_data_distill.py --out_dir corpus/planets
# python gen_minilang.py --out_dir corpus/minilang
python pretrain.py --corpus "$@" $PRETRAIN_ARGS
python finetune.py --corpus "$@" $FINETUNE_ARGS
