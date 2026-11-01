import argparse
import random
import torch
from model import load_checkpoint, save_checkpoint, IGNORE_INDEX
from data import load_qa, split_holdout, format_prompt
from chat import evaluate

parser = argparse.ArgumentParser(description='mini-lm 問答微調')
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--max_iters', type=int, default=300)
parser.add_argument('--lr', type=float, default=1e-4)
parser.add_argument('--holdout', type=float, default=0.2, help='保留不訓練的驗證集比例')
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()

torch.manual_seed(args.seed)
random.seed(args.seed)
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 1. 載入預訓練模型（checkpoint 內含模型設定與詞表）
model, config, tokenizer = load_checkpoint('pretrain.pt', device)
print("成功載入 pretrain.pt 權重！")
seq_len = config['seq_len']

# 2. 載入問答資料（自動去重）並切出驗證集
pairs = load_qa('finetune.txt')
train_pairs, val_pairs = split_holdout(pairs, args.holdout, args.seed)
print(f"Finetune 資料: {len(pairs)} 組問答 → 訓練 {len(train_pairs)} / 驗證 {len(val_pairs)}")

unknown = tokenizer.unknown_chars(''.join(q + a for q, a in pairs))
if unknown:
    print(f"⚠️ 有 {len(unknown)} 個字元不在詞表中（會變成 <UNK>）: {''.join(unknown)}")
    print("   請重新執行 pretrain.py 以更新詞表。")

def encode_sample(q, a):
    """序列為 <Q>問題<A>答案<EOS>；只對「答案 + <EOS>」計算 loss，問題部分遮掉。"""
    prompt = tokenizer.encode(format_prompt(q))
    answer = tokenizer.encode(a) + [tokenizer.eos_id]
    tokens = (prompt + answer)[:seq_len + 1]
    x = tokens[:-1]
    y = tokens[1:]
    y = [IGNORE_INDEX] * (len(prompt) - 1) + y[len(prompt) - 1:]
    return x, y

train_samples = [encode_sample(q, a) for q, a in train_pairs]

def get_batch():
    batch = random.choices(train_samples, k=args.batch_size)
    T = max(len(x) for x, _ in batch)
    xs = [x + [tokenizer.pad_id] * (T - len(x)) for x, _ in batch]
    ys = [y + [IGNORE_INDEX] * (T - len(y)) for _, y in batch]
    return torch.tensor(xs, device=device), torch.tensor(ys, device=device)

# 3. 微調訓練迴圈
optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
print(f"使用硬體: {device} | 開始 Fine-tuning...")

for iter in range(args.max_iters):
    model.train()
    xb, yb = get_batch()

    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    if iter % 100 == 0 or iter == args.max_iters - 1:
        print(f"Finetune Step {iter:4d} | Loss: {loss.item():.4f}")

save_checkpoint('finetune.pt', model, config, tokenizer)
print("微調完成！模型已儲存為 finetune.pt")

# 4. 評估：greedy 解碼，答案完全一致才算對
print("\n" + "=" * 50)
evaluate(model, tokenizer, train_pairs, '訓練集', device, show=3)
if val_pairs:
    evaluate(model, tokenizer, val_pairs, '驗證集（微調沒看過的問題）', device, show=len(val_pairs))
print("=" * 50)
