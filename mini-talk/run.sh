#!/bin/sh
# 準備兩份語料 → 同時訓練 A、B（最佳模型 D 的設定）→ 交談並從對話中學習
set -e
cd "$(dirname "$0")"
LM=../mini-lm
# 共同的語言：手寫句子 + 13 個方向的語句（和 D 相同）
SHARED="$LM/corpus/handwritten $LM/corpus/directions"
# large：d=256、8 頭、6 層，約 640 萬參數
LARGE="--d_model 256 --n_heads 8 --n_layers 6"
export OMP_NUM_THREADS=${THREADS:-4} MKL_NUM_THREADS=${THREADS:-4}
python prepare.py
PIDS=
for X in A B; do
  mkdir -p runs/$X
  (
    python $LM/pretrain.py --corpus corpus/$X $SHARED --out_dir runs/$X $LARGE --max_iters 2000
    # --train_question：問題也計算 loss，模型才學得會發問
    python $LM/finetune.py --corpus corpus/$X $SHARED --out_dir runs/$X --max_iters 1000 \
      --holdout 0 --no_train_eval --train_question
  ) > runs/$X/train.log 2>&1 &
  PIDS="$PIDS $!"
done
for P in $PIDS; do wait $P; done  # 任一個訓練失敗就停止
python talk.py --learn "$@"
