"""設計泛化最好的 Mini-Lang 模型：比較三種資料設定，用四種泛化測試評估。

設定（模型都是縮放實驗中最好的 large：d=256、6 層、約 640 萬參數）：
  A 基準     縮放實驗的 large × 16 倍資料（每個事實 2 種說法、每種問題 1 種問法）
  B 加強資料 每個事實 4 種說法 + 每人 2 段打亂順序的小傳 + 每種問題 2 種問法
  C 加強＋手寫 B 再混入 corpus/handwritten 的手寫句子
  D 加強＋手寫＋方向語句 C 再混入 corpus/directions（大模型依各方向產生的語句）

測試：
  新事實   微調沒練過的事實，用原本的問法問（和縮放實驗的驗證集相同）
  新問法   練過的事實，用微調從沒出現過的問法問（例如「誰是小明的朋友？」）
  兩者皆新 沒練過的事實 + 沒出現過的問法
  新句子   手寫測試句、各方向測試句的每字 loss（越低越好），衡量對沒看過的句子的語言能力

用法：
    python experiments/best_model.py            # 訓練還沒有模型的設定，再評估全部
    python experiments/best_model.py --eval_only
    python experiments/best_model.py --retrain  # 全部重新訓練
"""
import argparse
import csv
import glob
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

LM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LM_DIR)
OUT = os.path.join(LM_DIR, 'runs', 'best')
DATA = os.path.join(OUT, 'data_aug')
HAND = os.path.join(LM_DIR, 'corpus', 'handwritten')
DIRS = os.path.join(LM_DIR, 'corpus', 'directions')
CSV = os.path.join(LM_DIR, 'experiments', 'best_model_results.csv')

parser = argparse.ArgumentParser()
parser.add_argument('--threads', type=int, default=4)
parser.add_argument('--pretrain_iters', type=int, default=2000)
parser.add_argument('--finetune_iters', type=int, default=1000)
parser.add_argument('--eval_only', action='store_true')
parser.add_argument('--retrain', action='store_true')
args = parser.parse_args()

LARGE = ['--d_model', '256', '--n_heads', '8', '--n_layers', '6']
CONFIGS = {
    'A 基準': dict(ckpt=os.path.join(LM_DIR, 'runs', 'scaling', 'large_x16_none', 'finetune.pt')),
    'B 加強資料': dict(corpus=[DATA]),
    'C 加強＋手寫': dict(corpus=[DATA, HAND]),
    'D 加強＋手寫＋方向語句': dict(corpus=[DATA, HAND, DIRS]),
}

def run(cmd, log):
    env = dict(os.environ, OMP_NUM_THREADS=str(args.threads), MKL_NUM_THREADS=str(args.threads))
    with open(log, 'w') as f:
        subprocess.run(cmd, cwd=LM_DIR, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)

def train(name, corpus):
    out = os.path.join(OUT, name.split()[0])
    os.makedirs(out, exist_ok=True)
    common = ['--corpus', *corpus, '--out_dir', out]
    t0 = time.time()
    run([sys.executable, 'pretrain.py', *common, *LARGE, '--max_iters', str(args.pretrain_iters)],
        os.path.join(out, 'pretrain.log'))
    run([sys.executable, 'finetune.py', *common, '--holdout', '0', '--no_train_eval',
         '--max_iters', str(args.finetune_iters)], os.path.join(out, 'finetune.log'))
    print(f'✅ {name} 訓練完成，{(time.time() - t0) / 60:.1f} 分鐘', flush=True)
    return os.path.join(out, 'finetune.pt')

def evaluate(name, ckpt):
    import torch
    import torch.nn.functional as F
    from model import load_checkpoint
    from data import load_qa, read_unique_lines
    from chat import answer
    torch.set_num_threads(args.threads)
    model, _, tok = load_checkpoint(ckpt, 'cpu')
    row = {'設定': name}
    for test in ['test_fact', 'test_phrase', 'test_both']:
        pairs = load_qa([os.path.join(DATA, test + '.txt')])
        correct = sum(answer(model, tok, q, 'cpu') == a for q, a in pairs)
        row[test] = f'{correct}/{len(pairs)}'
        row[test + '_acc'] = round(correct / len(pairs), 3)
    # 沒看過的句子：每字平均 loss（從第二個字開始預測，結尾預測 <EOS>）
    model.eval()

    def lm_loss(path):
        total, n = 0.0, 0
        with torch.no_grad():
            for line in read_unique_lines(path):
                ids = tok.encode(line) + [tok.eos_id]
                logits, _ = model(torch.tensor([ids[:-1]]))
                total += F.cross_entropy(logits[0], torch.tensor(ids[1:]), reduction='sum').item()
                n += len(ids) - 1
        return round(total / n, 3)

    row['handwritten_loss'] = lm_loss(os.path.join(HAND, 'test.txt'))
    row['handwritten_ppl'] = round(math.exp(row['handwritten_loss']), 2)
    for path in sorted(glob.glob(os.path.join(DIRS, 'test', '*.txt'))):
        row['dir_' + os.path.splitext(os.path.basename(path))[0]] = lm_loss(path)
    dir_losses = [v for k, v in row.items() if k.startswith('dir_')]
    if dir_losses:
        row['directions_loss'] = round(sum(dir_losses) / len(dir_losses), 3)
    print(f"📊 {name}: 新事實 {row['test_fact']}，新問法 {row['test_phrase']}，兩者皆新 {row['test_both']}，"
          f"手寫句 loss {row['handwritten_loss']}，方向句 loss {row.get('directions_loss', '-')}", flush=True)
    return row

# 1. 產生加強語料（若已存在就沿用）
if not os.path.exists(os.path.join(DATA, 'test_both.txt')):
    run([sys.executable, 'gen_minilang.py', '--out_dir', DATA, '--n_people', '256', '--n_sentences', '24000',
         '--fact_variants', '4', '--bios_per_person', '2', '--question_variants', '3',
         '--holdout', '0.2', '--holdout_phrase'], os.path.join(OUT, 'gen.log'))

# 2. 訓練還沒有模型的設定（同時進行）
ckpts = {name: c['ckpt'] for name, c in CONFIGS.items() if 'ckpt' in c}
to_train = {}
for name, c in CONFIGS.items():
    if 'corpus' in c:
        ckpt = os.path.join(OUT, name.split()[0], 'finetune.pt')
        if args.eval_only or (os.path.exists(ckpt) and not args.retrain):
            ckpts[name] = ckpt
        else:
            to_train[name] = c['corpus']
if to_train:
    with ThreadPoolExecutor(len(to_train)) as pool:
        ckpts.update(zip(to_train, pool.map(lambda kv: train(*kv), to_train.items())))

# 3. 評估
rows = [evaluate(name, ckpts[name]) for name in CONFIGS]
with open(CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
    w.writeheader()
    w.writerows(rows)
print(f'\n結果已寫入 {CSV}\n')
print('| 設定 | 新事實 | 新問法 | 兩者皆新 | 手寫新句子 loss | 方向新句子 loss |')
print('|---|---:|---:|---:|---:|---:|')
for r in rows:
    print(f"| {r['設定']} | {r['test_fact']} ({r['test_fact_acc']:.0%}) | {r['test_phrase']} ({r['test_phrase_acc']:.0%}) | "
          f"{r['test_both']} ({r['test_both_acc']:.0%}) | {r['handwritten_loss']} | {r.get('directions_loss', '-')} |")
