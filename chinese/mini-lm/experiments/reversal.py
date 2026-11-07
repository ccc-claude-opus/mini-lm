"""反轉詛咒（reversal curse）實驗：只學過「A 的老師是 B」，答得出「B 是誰的老師？」嗎？

世界：128 對師生，學生與老師的名字不重疊，每個老師只教一個學生，所以反過來問也只有一個答案。

三種預訓練語料（都另外混入一般句子、手寫句子與 13 個方向的語句）：
  F 只有正向   所有師生都只用「學生在前」的說法（小明的老師是小花。）
  M 部分雙向   訓練組的師生兩種方向都有，測試組只有正向
               → 模型能不能從別人的例子學會「反過來想」？
  B 全部雙向   所有師生都有兩種方向（小花是小明的老師。）

微調（三種設定相同）：訓練組 64 對，正向問題與反向問題都練。
  正向  小明的老師是誰？ → 小花
  反向  小花是誰的老師？ → 小明
測試：沒微調過的 64 對，正向與反向各問一次。亂猜反向問題的答對率約 1/128。

模型與訓練步數和 best-model 的 D 相同（d=256、6 層、8 頭，預訓練 2,000 步、微調 1,000 步）。

用法：
    python experiments/reversal.py            # 產生語料、訓練還沒有模型的設定，再評估
    python experiments/reversal.py --eval_only
"""
import argparse
import csv
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

LM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LM_DIR)
OUT = os.path.join(LM_DIR, 'runs', 'reversal')
HAND = os.path.join(LM_DIR, 'corpus', 'handwritten')
DIRS = os.path.join(LM_DIR, 'corpus', 'directions')
CSV = os.path.join(LM_DIR, 'experiments', 'reversal_results.csv')

parser = argparse.ArgumentParser()
parser.add_argument('--threads', type=int, default=4)
parser.add_argument('--pretrain_iters', type=int, default=2000)
parser.add_argument('--finetune_iters', type=int, default=1000)
parser.add_argument('--seed', type=int, default=0)
parser.add_argument('--eval_only', action='store_true')
parser.add_argument('--retrain', action='store_true')
args = parser.parse_args()

LARGE = ['--d_model', '256', '--n_heads', '8', '--n_layers', '6']
CONDITIONS = {'F': 'F 只有正向', 'M': 'M 部分雙向', 'B': 'B 全部雙向'}

# ==========================================
# 1. 師生世界
# ==========================================
NAME_CHARS = '明山花文天月雨心東南白紅新樂真方'  # 和 gen_minilang.py 相同的人名用字
NAMES = [a + b for a in '小大' for b in NAME_CHARS[:8]] + \
        [a + b for a in NAME_CHARS for b in NAME_CHARS if a != b]
rng = random.Random(args.seed)
names = NAMES[:]
rng.shuffle(names)
pairs = list(zip(names[0::2], names[1::2]))  # (學生, 老師)
train_pairs, test_pairs = pairs[:len(pairs) // 2], pairs[len(pairs) // 2:]

def forward(s, t):   # 學生在前
    return [f'{s}的老師是{t}。', f'{s}有一個老師叫{t}。', f'{s}在學校的老師是{t}。', f'大家都知道{s}的老師是{t}。']

def backward(s, t):  # 老師在前
    return [f'{t}是{s}的老師。', f'{t}有一個學生叫{s}。', f'{t}在學校教{s}。', f'大家都知道{t}教{s}。']

def fwd_q(s, t):
    return f'<Q>{s}的老師是誰？<A>{t}'

def bwd_q(s, t):
    return f'<Q>{t}是誰的老師？<A>{s}'

def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def run(cmd, log):
    env = dict(os.environ, OMP_NUM_THREADS=str(args.threads), MKL_NUM_THREADS=str(args.threads))
    with open(log, 'w') as f:
        subprocess.run(cmd, cwd=LM_DIR, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)

def make_data():
    general = os.path.join(OUT, 'general')
    if not os.path.exists(os.path.join(general, 'pretrain.txt')):
        # 一般句子與文件例句（沒有人物），和 D 的一般句子相同
        tmp = os.path.join(OUT, 'general_tmp')
        run([sys.executable, 'gen_minilang.py', '--out_dir', tmp, '--n_people', '0', '--n_sentences', '24000'],
            os.path.join(OUT, 'gen.log'))
        os.makedirs(general, exist_ok=True)
        for name in ['pretrain.txt', 'charset.txt']:
            os.replace(os.path.join(tmp, name), os.path.join(general, name))
        subprocess.run(['rm', '-rf', tmp], check=True)
    for c in CONDITIONS:
        d = os.path.join(OUT, 'data_' + c)
        facts = [f for s, t in pairs for f in forward(s, t)]
        both = {'F': [], 'M': train_pairs, 'B': pairs}[c]
        facts += [f for s, t in both for f in backward(s, t)]
        write(os.path.join(d, 'pretrain.txt'), facts)
        write(os.path.join(d, 'finetune.txt'), [q for s, t in train_pairs for q in (fwd_q(s, t), bwd_q(s, t))])
    write(os.path.join(OUT, 'test_fwd.txt'), [fwd_q(s, t) for s, t in test_pairs])
    write(os.path.join(OUT, 'test_bwd.txt'), [bwd_q(s, t) for s, t in test_pairs])
    write(os.path.join(OUT, 'train_fwd.txt'), [fwd_q(s, t) for s, t in train_pairs])
    write(os.path.join(OUT, 'train_bwd.txt'), [bwd_q(s, t) for s, t in train_pairs])

# ==========================================
# 2. 訓練與評估
# ==========================================
def train(c):
    out = os.path.join(OUT, c)
    os.makedirs(out, exist_ok=True)
    common = ['--corpus', os.path.join(OUT, 'data_' + c), os.path.join(OUT, 'general'), HAND, DIRS, '--out_dir', out]
    t0 = time.time()
    run([sys.executable, 'pretrain.py', *common, *LARGE, '--max_iters', str(args.pretrain_iters)],
        os.path.join(out, 'pretrain.log'))
    run([sys.executable, 'finetune.py', *common, '--holdout', '0', '--no_train_eval',
         '--max_iters', str(args.finetune_iters)], os.path.join(out, 'finetune.log'))
    print(f'✅ {CONDITIONS[c]} 訓練完成，{(time.time() - t0) / 60:.1f} 分鐘', flush=True)

def complete(model, tok, prompt, max_new=8):
    """預訓練模型（還沒微調）的 greedy 續寫，用來看事實本身有沒有學到。"""
    import torch
    idx = torch.tensor([tok.encode(prompt)])
    out = model.generate(idx, max_new, temperature=1e-6, top_k=1, eos_id=tok.eos_id)
    return tok.decode(out[0, idx.shape[1]:].tolist(), skip_special=True)

def evaluate(c):
    import torch
    from model import load_checkpoint
    from data import load_qa
    from chat import answer
    torch.set_num_threads(args.threads)
    row = {'設定': CONDITIONS[c]}
    model, _, tok = load_checkpoint(os.path.join(OUT, c, 'finetune.pt'), 'cpu')
    for test in ['train_fwd', 'train_bwd', 'test_fwd', 'test_bwd']:
        qa = load_qa([os.path.join(OUT, test + '.txt')])
        correct = sum(answer(model, tok, q, 'cpu') == a for q, a in qa)
        row[test] = f'{correct}/{len(qa)}'
        row[test + '_acc'] = round(correct / len(qa), 3)
    # 預訓練模型：正向「小明的老師是」→ 小花；反向「小花是」→ 小明
    model, _, tok = load_checkpoint(os.path.join(OUT, c, 'pretrain.pt'), 'cpu')
    model.eval()
    fwd = sum(complete(model, tok, f'{s}的老師是').startswith(t) for s, t in test_pairs)
    bwd = sum(complete(model, tok, f'{t}是').startswith(s) for s, t in test_pairs)
    row['pretrain_fwd'] = f'{fwd}/{len(test_pairs)}'
    row['pretrain_bwd'] = f'{bwd}/{len(test_pairs)}'
    print(f"📊 {row['設定']}: 測試正向 {row['test_fwd']}，測試反向 {row['test_bwd']}，"
          f"預訓練續寫 正向 {row['pretrain_fwd']} 反向 {row['pretrain_bwd']}", flush=True)
    return row

os.makedirs(OUT, exist_ok=True)
make_data()
todo = [c for c in CONDITIONS if not args.eval_only and
        (args.retrain or not os.path.exists(os.path.join(OUT, c, 'finetune.pt')))]
if todo:
    with ThreadPoolExecutor(len(todo)) as pool:
        list(pool.map(train, todo))

rows = [evaluate(c) for c in CONDITIONS]
with open(CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f'\n結果已寫入 {CSV}\n')
print('| 設定 | 訓練組 正向 | 訓練組 反向 | 測試組 正向 | 測試組 反向 | 預訓練續寫 正向 | 預訓練續寫 反向 |')
print('|---|---:|---:|---:|---:|---:|---:|')
for r in rows:
    print(f"| {r['設定']} | {r['train_fwd']} | {r['train_bwd']} | {r['test_fwd']} | {r['test_bwd']} | "
          f"{r['pretrain_fwd']} | {r['pretrain_bwd']} |")
