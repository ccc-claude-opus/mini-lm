#!/usr/bin/env python3
"""Mini-English → 一般英文 的反向翻譯。

用 lexicon.tsv 當字典：Mini-English 那一欄的字串（描述或外來詞）對應到 English 那一欄。

用法：
    python translate.py "a place where doctors help sick people"   # 反譯一句
    python translate.py --file article.txt                          # 反譯整個檔案（存成 .en.txt）
    python translate.py --file article.txt --out result.txt

外來詞的括號說明在反譯時會刪掉（英文不需要）。
"""
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
LEXICON = HERE / 'lexicon.tsv'

# 這些 Mini-English 字串太短或太常見，直接替換會改壞句子
SKIP = {'a', 'an', 'the', 'is', 'are', 'be', 'of', 'in', 'on', 'and', 'or', 'not',
        'very', 'some', 'more', 'most', 'one', 'two', 'many', 'much', 'few', 'it',
        'he', 'she', 'they', 'we', 'you', 'i', 'a thing', 'a person', 'a place'}


def frequencies():
    """常用詞的次數，用來挑最貼切的那個英文對應詞。"""
    path = HERE / 'data' / 'common_words.tsv'
    freq = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines()[1:]:
            w, c = line.split('\t')
            freq[w.lower()] = int(c)
    return freq


def load():
    """回傳 [(mini, english)]，長的排前面。

    同一個 Mini-English 說法可能對應好幾個英文詞（help／assist），
    這裡挑**最常用**的那個當作反譯的結果。
    """
    freq = frequencies()
    best = {}
    # data/reverse.tsv：描述 → 英文詞（包含表內的詞，例如 hospital）
    rev = HERE / 'data' / 'reverse.tsv'
    if rev.exists():
        for line in rev.read_text(encoding='utf-8').splitlines()[1:]:
            if not line.strip():
                continue
            mini, eng = line.split('\t')
            best[mini.strip().lower()] = (10 ** 9, eng.strip())
    with open(LEXICON, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            eng, mini = r['English'], r['Mini-English']
            if not eng or not mini or mini == eng:
                continue
            if mini.lower() in SKIP:
                continue
            key = mini.lower()
            score = freq.get(eng.lower(), 0)
            if key not in best or score > best[key][0]:
                best[key] = (score, eng)
    rows = [(key, eng) for key, (score, eng) in best.items()]
    rows.sort(key=lambda x: -len(x[0]))
    return rows


def build_pattern(rows):
    """把字串變成「最長優先」的正則。"""
    pats = sorted({m for m, _ in rows}, key=len, reverse=True)
    regex = re.compile('|'.join(re.escape(p) for p in pats))
    table = {m: e for m, e in rows}
    return regex, table


def to_english(text, regex, table):
    """把 Mini-English 換成一般英文；回傳 (譯文, 換掉的次數, 換不掉的表外詞)。"""
    # 外來詞的括號說明先收起來
    notes = []

    def stash(m):
        notes.append(m.group(1))
        return f'\x00{len(notes) - 1}\x00'

    text = re.sub(r'\(([^()]*)\)', stash, text)

    def sub(m):
        return table.get(m.group(0), m.group(0))

    out = regex.sub(sub, text)
    # 括號說明放回去（標成「說明」）
    for i, note in enumerate(notes):
        out = out.replace(f'\x00{i}\x00', f' ({note})')
    return out


def main():
    rows = load()
    regex, table = build_pattern(rows)
    if sys.argv[1:2] == ['--file']:
        paths = [a for a in sys.argv[2:] if not a.startswith('--')]
        out_path = None
        if '--out' in sys.argv:
            out_path = sys.argv[sys.argv.index('--out') + 1]
        for path in paths:
            src = Path(path).read_text(encoding='utf-8')
            dst = to_english(src, regex, table)
            if out_path:
                Path(out_path).write_text(dst, encoding='utf-8')
                print(f'✅ {path} → {out_path}')
            else:
                print(dst)
        return 0
    text = ' '.join(sys.argv[1:])
    print(to_english(text, regex, table))
    return 0


if __name__ == '__main__':
    sys.exit(main())
