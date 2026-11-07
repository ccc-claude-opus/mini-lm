import argparse
import os
import random
import torch
from model import build_model, save_checkpoint
from tokenizer import CharTokenizer
from data import add_corpus_args, corpus_files, default_out_dir, read_files

parser = argparse.ArgumentParser(description='mini-lm 預訓練')
add_corpus_args(parser)
parser.add_argument('--out_dir', default=None, help='輸出目錄，預設 runs/<語料名稱>')
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--seq_len', type=int, default=96)
parser.add_argument('--max_iters', type=int, default=500)
parser.add_argument('--lr', type=float, default=5e-4)
parser.add_argument('--d_model', type=int, default=128)
parser.add_argument('--n_heads', type=int, default=4)
parser.add_argument('--n_layers', type=int, default=4)
parser.add_argument('--dropout', type=float, default=0.0)
parser.add_argument('--weight_decay', type=float, default=0.01)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()
if not args.corpus and not args.pretrain:
    parser.error('請用 --corpus 或 --pretrain 指定語料，例如 --corpus corpus/planets')
out_dir = args.out_dir or default_out_dir(args)
os.makedirs(out_dir, exist_ok=True)

torch.manual_seed(args.seed)
random.seed(args.seed)
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 1. 讀取資料（自動去重）並建立詞表
#    詞表涵蓋 pretrain、finetune 與 charset 的所有字元，並含 <PAD> <UNK> <EOS> <Q> <A> 特殊 token
pretrain_files = corpus_files(args, 'pretrain')
vocab_files = pretrain_files + corpus_files(args, 'finetune') + corpus_files(args, 'charset')
facts = read_files(pretrain_files)
print(f"Pretrain 語料: {', '.join(pretrain_files)}")
print(f"Pretrain 資料: {len(facts)} 句不重複的句子")

tokenizer = CharTokenizer.build(read_files(vocab_files))
tokenizer.save(os.path.join(out_dir, 'vocab.json'))
print(f"詞表大小: {tokenizer.vocab_size}（含特殊 token），已儲存於 {out_dir}/vocab.json")

# 每句結尾加上 <EOS>，讓模型學會「一句話在哪裡結束」
encoded_facts = [tokenizer.encode(f) + [tokenizer.eos_id] for f in facts]

def get_batch():
    # 每個樣本都重新打亂句子順序再拼接，避免模型背下固定的「句子接句子」順序
    xs, ys = [], []
    for _ in range(args.batch_size):
        stream = []
        while len(stream) < 2 * (args.seq_len + 1):
            stream += [t for f in random.sample(encoded_facts, len(encoded_facts)) for t in f]
        i = random.randint(0, len(stream) - args.seq_len - 1)
        xs.append(stream[i:i + args.seq_len])
        ys.append(stream[i + 1:i + args.seq_len + 1])
    return torch.tensor(xs, device=device), torch.tensor(ys, device=device)

# 2. 初始化模型
config = dict(vocab_size=tokenizer.vocab_size, d_model=args.d_model, n_heads=args.n_heads,
              n_layers=args.n_layers, seq_len=args.seq_len, dropout=args.dropout)
model = build_model(config).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
n_params = sum(p.numel() for p in model.parameters())
print(f"使用硬體: {device} | 參數量: {n_params/1e6:.2f}M ({n_params:,}) | 開始 Pre-training...")

# 3. 訓練迴圈
for iter in range(args.max_iters):
    model.train()
    xb, yb = get_batch()

    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

    if iter % 100 == 0 or iter == args.max_iters - 1:
        print(f"Pretrain Step {iter:4d} | Loss: {loss.item():.4f}")

# 4. 儲存模型（權重 + 模型設定 + 詞表，載入時不必再對齊參數）
ckpt_path = os.path.join(out_dir, 'pretrain.pt')
save_checkpoint(ckpt_path, model, config, tokenizer)
print(f"預訓練完成！模型已儲存為 {ckpt_path}")
