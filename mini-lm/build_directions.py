"""把 corpus/directions/src/ 中各方向的語句整理成一個語料（--dir corpus/glm 整理 GLM 產生的語料）。

* 只保留字表內（mini-lang/check.py）、沒有英文字母的句子（人名是英文，所以也不會和人物事實衝突）
* 去掉重複句，以及和其他語料、手寫測試句重複的句子
* 每個方向切出一部分當測試句，放在 corpus/directions/test/<方向>.txt
* 其餘合併成 corpus/directions/pretrain.txt
"""
import argparse
import glob
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mini-lang'))
from check import DOC, load_charset, unknown

parser = argparse.ArgumentParser()
parser.add_argument('--dir', default=os.path.join(HERE, 'corpus', 'directions'))
parser.add_argument('--test_ratio', type=float, default=0.1)
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()

charset = set(load_charset(open(DOC, encoding='utf-8').read()))
def lines_of(path):
    with open(path, encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]

# 其他語料中出現過的句子，以及手寫測試句，都不能放進來
others = set()
for path in glob.glob(os.path.join(HERE, 'corpus', '*', '*.txt')) + glob.glob(os.path.join(HERE, 'corpus', '*', 'test', '*.txt')):
    if not os.path.abspath(path).startswith(os.path.abspath(args.dir) + os.sep):
        others.update(lines_of(path))

rng = random.Random(args.seed)
seen, train = set(), []
os.makedirs(os.path.join(args.dir, 'test'), exist_ok=True)
print(f"{'方向':<20}{'原始':>6}{'字表外':>7}{'重複':>6}{'訓練':>6}{'測試':>6}")
for path in sorted(glob.glob(os.path.join(args.dir, 'src', '*.txt'))):
    name = os.path.splitext(os.path.basename(path))[0]
    raw = lines_of(path)
    off = [l for l in raw if unknown(l, charset) or re.search(r'[A-Za-z]', l)]
    keep, dup = [], 0
    for l in raw:
        if l in off:
            continue
        if l in seen or l in others:
            dup += 1
            continue
        seen.add(l)
        keep.append(l)
    rng.shuffle(keep)
    n_test = max(1, int(len(keep) * args.test_ratio))
    test, rest = keep[:n_test], keep[n_test:]
    with open(os.path.join(args.dir, 'test', name + '.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(test) + '\n')
    train += rest
    print(f"{name:<20}{len(raw):>6}{len(off):>7}{dup:>6}{len(rest):>6}{len(test):>6}")

with open(os.path.join(args.dir, 'pretrain.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(train) + '\n')
print(f"✅ 訓練 {len(train)} 行 → {args.dir}/pretrain.txt，測試句在 {args.dir}/test/")
