"""縮放實驗：模型大小 × 資料量，另外比較正則化。

每一格都會產生語料、預訓練、微調，然後記錄 Mini-Lang 驗證集（微調沒看過的問答）答對率。
結果寫到 experiments/scaling_results.csv，並印出 Markdown 表格。

用法（在 mini-lm/ 目錄外也可以執行）：
    python experiments/scaling.py                 # 完整實驗
    python experiments/scaling.py --quick         # 只跑最小的設定，確認流程
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

LM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(LM_DIR, 'runs', 'scaling')
CSV = os.path.join(LM_DIR, 'experiments', 'scaling_results.csv')

MODELS = {  # 名稱: (d_model, n_heads, n_layers)
    'tiny': (32, 2, 2),
    'small': (64, 4, 2),
    'base': (128, 4, 4),
    'large': (256, 8, 6),
}
DATA = {  # 倍數: (人數, 一般句子數)；1 倍就是 corpus/minilang 的設定
    0.5: (8, 750),
    1: (16, 1500),
    4: (64, 6000),
    16: (256, 24000),
}
REG = {'none': (0.0, 0.01), 'reg': (0.1, 0.1)}  # (dropout, weight_decay)

parser = argparse.ArgumentParser()
parser.add_argument('--jobs', type=int, default=4, help='同時跑幾個實驗')
parser.add_argument('--threads', type=int, default=2, help='每個實驗用幾個 CPU 執行緒')
parser.add_argument('--pretrain_iters', type=int, default=2000)
parser.add_argument('--finetune_iters', type=int, default=500)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--quick', action='store_true')
args = parser.parse_args()

def data_dir(k):
    return os.path.join(OUT, f'data_x{k}')

def run(cmd, log):
    env = dict(os.environ, OMP_NUM_THREADS=str(args.threads), MKL_NUM_THREADS=str(args.threads))
    with open(log, 'w') as f:
        subprocess.run(cmd, cwd=LM_DIR, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
    return open(log, encoding='utf-8').read()

def experiment(model, k, reg):
    d, h, l = MODELS[model]
    dropout, wd = REG[reg]
    name = f'{model}_x{k}_{reg}'
    out = os.path.join(OUT, name)
    os.makedirs(out, exist_ok=True)
    common = ['--corpus', data_dir(k), '--out_dir', out, '--seed', str(args.seed), '--weight_decay', str(wd)]
    t0 = time.time()
    log = run([sys.executable, 'pretrain.py', *common, '--d_model', str(d), '--n_heads', str(h),
               '--n_layers', str(l), '--dropout', str(dropout), '--max_iters', str(args.pretrain_iters)],
              os.path.join(out, 'pretrain.log'))
    params = int(re.search(r'參數量: [\d.]+M \(([\d,]+)\)', log).group(1).replace(',', ''))
    pre_loss = float(re.findall(r'Loss: ([\d.]+)', log)[-1])
    log = run([sys.executable, 'finetune.py', *common, '--max_iters', str(args.finetune_iters), '--no_train_eval'],
              os.path.join(out, 'finetune.log'))
    m = re.search(r'驗證集.*?: (\d+)/(\d+)', log)
    correct, total = int(m.group(1)), int(m.group(2))
    row = dict(model=model, params=params, data=k, reg=reg, pretrain_loss=pre_loss,
               val_correct=correct, val_total=total, val_acc=round(correct / total, 3),
               minutes=round((time.time() - t0) / 60, 1))
    print(f"✅ {name}: {correct}/{total} ({correct / total:.0%})，{row['minutes']} 分鐘", flush=True)
    return row

# 1. 產生各種資料量的語料
models, datas = (['tiny'], [0.5]) if args.quick else (list(MODELS), list(DATA))
os.makedirs(OUT, exist_ok=True)
for k in datas:
    people, sentences = DATA[k]
    log = run([sys.executable, 'gen_minilang.py', '--out_dir', data_dir(k), '--n_people', str(people),
               '--n_sentences', str(sentences), '--seed', str(args.seed)],
              os.path.join(OUT, f'gen_x{k}.log'))
    print(log.splitlines()[0], f'（{k} 倍）', flush=True)

# 2. 實驗清單：模型 × 資料（無正則化），再加上 base 模型的正則化比較
jobs = [(m, k, 'none') for m in models for k in datas]
if not args.quick:
    jobs += [('base', k, 'reg') for k in datas]
# 大的先跑，總時間比較短
jobs.sort(key=lambda j: -MODELS[j[0]][0] * MODELS[j[0]][2] * j[1])

with ThreadPoolExecutor(args.jobs) as pool:
    rows = list(pool.map(lambda j: experiment(*j), jobs))

# 3. 輸出
rows.sort(key=lambda r: (r['reg'], r['params'], r['data']))
with open(CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f'\n結果已寫入 {CSV}\n')

for reg in REG:
    sub = [r for r in rows if r['reg'] == reg]
    if not sub:
        continue
    print(f'### {reg}\n')
    print('| 模型 | 參數 | ' + ' | '.join(f'{k} 倍' for k in datas) + ' |')
    print('|---|---:|' + '---:|' * len(datas))
    for m in models:
        cells = {r['data']: r for r in sub if r['model'] == m}
        if cells:
            params = next(iter(cells.values()))['params']
            print(f'| {m} | {params:,} | ' + ' | '.join(
                f"{cells[k]['val_correct']}/{cells[k]['val_total']} ({cells[k]['val_acc']:.0%})" if k in cells else ''
                for k in datas) + ' |')
    print()
