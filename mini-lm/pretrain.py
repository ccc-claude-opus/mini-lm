import argparse
import random
import torch
from model import build_model, save_checkpoint
from tokenizer import CharTokenizer
from data import read_unique_lines

parser = argparse.ArgumentParser(description='mini-lm 預訓練')
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--seq_len', type=int, default=96)
parser.add_argument('--max_iters', type=int, default=500)
parser.add_argument('--lr', type=float, default=5e-4)
parser.add_argument('--d_model', type=int, default=128)
parser.add_argument('--n_heads', type=int, default=4)
parser.add_argument('--n_layers', type=int, default=4)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()

torch.manual_seed(args.seed)
random.seed(args.seed)
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 1. 讀取資料（自動去重）並建立詞表
#    詞表同時涵蓋 pretrain 與 finetune 的字元，並含 <PAD> <UNK> <EOS> <Q> <A> 特殊 token
facts = read_unique_lines('pretrain.txt')
qa_lines = read_unique_lines('finetune.txt')
print(f"Pretrain 資料: {len(facts)} 句不重複的知識敘述")

tokenizer = CharTokenizer.build(facts + qa_lines)
tokenizer.save('vocab.json')
print(f"詞表大小: {tokenizer.vocab_size}（含特殊 token），已儲存為 vocab.json")

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
              n_layers=args.n_layers, seq_len=args.seq_len)
model = build_model(config).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
n_params = sum(p.numel() for p in model.parameters())
print(f"使用硬體: {device} | 參數量: {n_params/1e6:.2f}M | 開始 Pre-training...")

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
save_checkpoint('pretrain.pt', model, config, tokenizer)
print("預訓練完成！模型已儲存為 pretrain.pt")
