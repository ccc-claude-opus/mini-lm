"""檢查通用 Mini-Lang：規格文件的例句與詞典是否只用到 256 字，詞典格式是否正確。

用法：
    python check_universal.py             # 檢查 universal.md 與 lexicon/*.tsv
    python check_universal.py --stats     # 另外列出各領域詞數與反譯時會撞在一起的說法
"""
import csv
import glob
import re
import sys
from pathlib import Path

from check import DOC, load_charset, snippets, unknown

HERE = Path(__file__).parent
SPEC = HERE / 'universal.md'
LEXICON = sorted(glob.glob(str(HERE / 'lexicon' / '*.tsv')))
COLUMNS = ['中文', 'Mini-Lang', '說明', '方式']
METHODS = {'本詞', '組詞', '描述', '音寫'}
SOUND = re.compile(r'〔[^〕]*〕')

def load_lexicon():
    """回傳 [(檔名, 行號, {欄位: 值})]。"""
    rows = []
    for path in LEXICON:
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            if reader.fieldnames != COLUMNS:
                sys.exit(f'❌ {path} 的欄位應為 {COLUMNS}，實際是 {reader.fieldnames}')
            for no, row in enumerate(reader, 2):
                rows.append((Path(path).name, no, row))
    return rows

def main():
    charset = set(load_charset(DOC.read_text(encoding='utf-8')))
    ok = True

    n = 0
    for no, s in snippets(SPEC.read_text(encoding='utf-8')):
        n += 1
        bad = unknown(s, charset)
        if bad:
            print(f"❌ universal.md 第 {no} 行用了字表外的字 {''.join(bad)}: {s}")
            ok = False
    print(f'universal.md：檢查了 {n} 段例句')

    rows = load_lexicon()
    seen, reverse = {}, {}
    for name, no, r in rows:
        where = f'{name}:{no}'
        for col in ('Mini-Lang', '說明'):
            bad = unknown(r[col] or '', charset)
            if bad:
                print(f"❌ {where} {r['中文']} 的「{col}」用了字表外的字 {''.join(bad)}: {r[col]}")
                ok = False
        if r['方式'] not in METHODS:
            print(f"❌ {where} {r['中文']} 的方式「{r['方式']}」不是 {'/'.join(sorted(METHODS))}")
            ok = False
        if r['方式'] == '音寫' and not SOUND.search(r['Mini-Lang']):
            print(f"❌ {where} {r['中文']} 標為音寫，但沒有〔〕")
            ok = False
        if r['方式'] == '音寫' and not r['說明']:
            print(f"❌ {where} {r['中文']} 是音寫，第一次出現要有說明")
            ok = False
        if r['中文'] in seen:
            print(f"❌ {where} {r['中文']} 重複（先前在 {seen[r['中文']]}）")
            ok = False
        seen[r['中文']] = where
        reverse.setdefault(r['Mini-Lang'], []).append(r['中文'])

    by_file = {}
    for name, _, r in rows:
        by_file.setdefault(name, []).append(r)
    print(f'詞典：{len(rows)} 條，' + '、'.join(f'{Path(k).stem} {len(v)}' for k, v in by_file.items()))
    methods = {}
    for _, _, r in rows:
        methods[r['方式']] = methods.get(r['方式'], 0) + 1
    print('方式：' + '、'.join(f'{k} {v}' for k, v in sorted(methods.items(), key=lambda kv: -kv[1])))

    shared = {k: v for k, v in reverse.items() if len(v) > 1}
    print(f'反譯時有 {len(shared)} 個說法對應多個中文詞（近義詞，反譯取第一個）')
    if '--stats' in sys.argv:
        for k, v in sorted(shared.items(), key=lambda kv: -len(kv[1])):
            print(f"  {k} ← {'、'.join(v)}")

    print('✅ 全部通過' if ok else '❌ 有錯誤')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
