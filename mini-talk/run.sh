#!/bin/sh
# 準備兩份語料 → 分別訓練 A、B → 交談並從對話中學習
set -e
cd "$(dirname "$0")"
LM=../mini-lm
python prepare.py
for X in A B; do
  python $LM/pretrain.py --corpus corpus/$X --out_dir runs/$X --max_iters 2000
  # --train_question：問題也計算 loss，模型才學得會發問
  python $LM/finetune.py --corpus corpus/$X --out_dir runs/$X --max_iters 500 --holdout 0 --train_question
done
python talk.py --learn "$@"
