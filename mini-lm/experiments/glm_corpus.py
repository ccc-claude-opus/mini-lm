"""GLM 5.3 Flash 產生的語料（corpus/glm）對 Mini-Lang 模型有沒有幫助？

設定（模型都是 large：d=256、6 層、約 640 萬參數；語料都是第 3 版 297 字）：
  D       加強資料＋手寫＋方向語句（best_model.py 的最佳設定，用第 3 版語料重新訓練）
  E       D 再混入 corpus/glm
  E 加長  E，預訓練步數加倍（語料變多了，2000 步可能看不完）

測試（和 best_model.py 相同，另加 GLM 測試句）：
  新事實、新問法、兩者皆新   人物問答的泛化
  手寫句、方向句、GLM 句     沒看過的句子的每字 loss（越低越好）

用法：
    python experiments/glm_corpus.py            # 訓練還沒有模型的設定，再評估全部
    python experiments/glm_corpus.py --eval_only
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
OUT = os.path.join(LM_DIR, 'runs', 'glm')
DATA = os.path.join(OUT, 'data_aug')
HAND = os.path.join(LM_DIR, 'corpus', 'handwritten')
DIRS = os.path.join(LM_DIR, 'corpus', 'directions')
GLM = os.path.join(LM_DIR, 'corpus', 'glm')
CSV = os.path.join(LM_DIR, 'experiments', 'glm_corpus_results.csv')

parser = argparse.ArgumentParser()
parser.add_argument('--threads', type=int, default=3)
parser.add_argument('--pretrain_iters', type=int, default=2000)
parser.add_argument('--finetune_iters', type=int, default=1000)
parser.add_argument('--eval_only', action='store_true')
parser.add_argument('--retrain', action='store_true')
parser.add_argument('--only', nargs='*', help='只訓練這些設定（例如 D），不評估')
args = parser.parse_args()

LARGE = ['--d_model', '256', '--n_heads', '8', '--n_layers', '6']
CONFIGS = {
    'D 加強＋手寫＋方向語句': dict(corpus=[DATA, HAND, DIRS], iters=args.pretrain_iters),
    'E D＋GLM 語料': dict(corpus=[DATA, HAND, DIRS, GLM], iters=args.pretrain_iters),
    'E2 D＋GLM 語料，預訓練加倍': dict(corpus=[DATA, HAND, DIRS, GLM], iters=2 * args.pretrain_iters),
}

def run(cmd, log):
    env = dict(os.environ, OMP_NUM_THREADS=str(args.threads), MKL_NUM_THREADS=str(args.threads))
    with open(log, 'w') as f:
        subprocess.run(cmd, cwd=LM_DIR, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)

def train(name, c):
    out = os.path.join(OUT, name.split()[0])
    os.makedirs(out, exist_ok=True)
    common = ['--corpus', *c['corpus'], '--out_dir', out]
    t0 = time.time()
    run([sys.executable, 'pretrain.py', *common, *LARGE, '--max_iters', str(c['iters'])],
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
    model.eval()

    def lm_loss(paths):
        total, n = 0.0, 0
        with torch.no_grad():
            for path in paths:
                for line in read_unique_lines(path):
                    ids = tok.encode(line) + [tok.eos_id]
                    logits, _ = model(torch.tensor([ids[:-1]]))
                    total += F.cross_entropy(logits[0], torch.tensor(ids[1:]), reduction='sum').item()
                    n += len(ids) - 1
        return round(total / n, 3)

    row['handwritten_loss'] = lm_loss([os.path.join(HAND, 'test.txt')])
    row['directions_loss'] = lm_loss(sorted(glob.glob(os.path.join(DIRS, 'test', '*.txt'))))
    row['glm_loss'] = lm_loss(sorted(glob.glob(os.path.join(GLM, 'test', '*.txt'))))
    for k in ['handwritten', 'directions', 'glm']:
        row[k + '_ppl'] = round(math.exp(row[k + '_loss']), 2)
    print(f"📊 {name}: 新事實 {row['test_fact']}，新問法 {row['test_phrase']}，兩者皆新 {row['test_both']}，"
          f"手寫句 {row['handwritten_loss']}，方向句 {row['directions_loss']}，GLM 句 {row['glm_loss']}", flush=True)
    return row

# 1. 用第 3 版產生加強語料（設定和 best_model.py 相同；若已存在就沿用）
if not os.path.exists(os.path.join(DATA, 'test_both.txt')):
    os.makedirs(OUT, exist_ok=True)
    run([sys.executable, 'gen_minilang.py', '--out_dir', DATA, '--n_people', '256', '--n_sentences', '24000',
         '--fact_variants', '4', '--bios_per_person', '2', '--question_variants', '3',
         '--holdout', '0.2', '--holdout_phrase'], os.path.join(OUT, 'gen.log'))

# 2. 訓練還沒有模型的設定（同時進行）
ckpts, to_train = {}, {}
for name, c in CONFIGS.items():
    ckpt = os.path.join(OUT, name.split()[0], 'finetune.pt')
    if args.only is not None and name.split()[0] not in args.only:
        continue
    if args.eval_only or (os.path.exists(ckpt) and not args.retrain):
        ckpts[name] = ckpt
    else:
        to_train[name] = c
if to_train:
    with ThreadPoolExecutor(len(to_train)) as pool:
        ckpts.update(zip(to_train, pool.map(lambda kv: train(*kv), to_train.items())))

if args.only is not None:
    sys.exit(0)

# 3. 評估
rows = [evaluate(name, ckpts[name]) for name in CONFIGS]
with open(CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
    w.writeheader()
    w.writerows(rows)
print(f'\n結果已寫入 {CSV}\n')
print('| 設定 | 新事實 | 新問法 | 兩者皆新 | 手寫句 loss | 方向句 loss | GLM 句 loss |')
print('|---|---:|---:|---:|---:|---:|---:|')
for r in rows:
    print(f"| {r['設定']} | {r['test_fact']} ({r['test_fact_acc']:.0%}) | {r['test_phrase']} ({r['test_phrase_acc']:.0%}) | "
          f"{r['test_both']} ({r['test_both_acc']:.0%}) | {r['handwritten_loss']} | {r['directions_loss']} | {r['glm_loss']} |")
