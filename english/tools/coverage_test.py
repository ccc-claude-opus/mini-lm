#!/usr/bin/env python3
"""覆蓋率測試：把抽樣的 200 個表外常用詞重新檢查一遍，印出統計。

用法：
    python tools/coverage_test.py            # 用 data/coverage.tsv 裡的答案
    python tools/coverage_test.py --sample   # 只看抽樣名單（重新抽一次做對照）

抽樣母體與答案是固定的（data/coverage_sample.txt、data/coverage.tsv），
所以這個數字每一個人重跑都一樣；改了詞表之後要重跑，看有沒有變差。
"""
import argparse
import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import check as checker  # noqa: E402

COVER = ROOT / 'data' / 'coverage.tsv'
SAMPLE = ROOT / 'data' / 'coverage_sample.txt'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', action='store_true', help='只印抽樣名單')
    args = ap.parse_args()

    spec = checker.Spec((ROOT / 'mini-english.md').read_text(encoding='utf-8'))
    sample = [w.strip() for w in SAMPLE.read_text(encoding='utf-8').splitlines() if w.strip()]
    if args.sample:
        print(f'抽樣 {len(sample)} 個詞：')
        print(' '.join(sample))
        return 0

    rows = []
    seen = set()
    for line in COVER.read_text(encoding='utf-8').splitlines()[1:]:
        if not line.strip():
            continue
        f = line.split('\t')
        while len(f) < 5:
            f.append('')
        if f[0].lower() in seen:
            continue
        seen.add(f[0].lower())
        rows.append(f)

    ways = collections.Counter()
    lengths = []
    bad = []
    for eng, mini, way, note, res in rows:
        ways[way] += 1
        if way == '描述':
            lengths.append(len(mini.split()))
        if way in ('-', ''):
            continue
        if way == '外來詞':
            errs, _ = checker.check_text(note, spec, allow_proper=True)
        else:
            errs, _ = checker.check_text(mini, spec)
        if errs:
            bad.append((eng, errs[0][1]))

    total = len(rows)
    ok = ways['本詞'] + ways['描述'] + ways['外來詞']
    print(f'覆蓋率測試：{total} 個表外常用詞')
    for way, desc in (('本詞', '本來就在詞表內'), ('描述', '用表內的詞說清楚'),
                      ('外來詞', '只能用原詞＋括號說明'), ('-', '說不好')):
        n = ways[way]
        print(f'  {way:4s}（{desc}）：{n:4d} 個，{n / total * 100:5.1f}%')
    print(f'  → 說得出來：{ok}/{total} = {ok / total * 100:.1f}%')
    if lengths:
        print(f'  → 描述的平均長度：{sum(lengths) / len(lengths):.1f} 個詞'
              f'（最長 {max(lengths)}）')
    if bad:
        print(f'  ❌ {len(bad)} 列不再通過檢查：')
        for eng, msg in bad[:20]:
            print(f'     {eng}：{msg}')
    else:
        print('  ✅ 每一列都通過 check.py')
    missing = [w for w in sample if w.lower() not in seen]
    if missing:
        print(f'  ⚠️  抽樣名單裡有 {len(missing)} 個詞沒有答案：{" ".join(missing)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
