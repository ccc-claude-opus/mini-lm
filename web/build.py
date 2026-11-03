"""把 mini-lang/ 的字表、詞典、讀音與範例打包成 data.js，給網頁使用。

詞典或範例更新後重新執行：
    python web/build.py
"""
import csv
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'mini-lang'))
from check import DOC, load_charset  # noqa: E402

def lexicon():
    rows = []
    for path in sorted(glob.glob(str(ROOT / 'mini-lang' / 'lexicon' / '*.tsv'))):
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                rows.append([r['中文'], r['Mini-Lang'], r['說明'], r['方式']])
    return rows

def pinyin():
    with open(ROOT / 'mini-lang' / 'pinyin.tsv', encoding='utf-8') as f:
        return {r['詞']: r['拼音'] for r in csv.DictReader(f, delimiter='\t')}

def examples():
    """examples.md 的範例：中文 → Mini-Lang 取「原文」，Mini-Lang → 中文 取「Mini-Lang 原文」。"""
    text = (ROOT / 'mini-lang' / 'examples.md').read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r'### 範例 \d+：(.+?)\n(.*?)(?=\n### |\n## |\Z)', text, re.S):
        title, body = m.group(1), m.group(2)
        zh = re.search(r'^原文：\n\n```text\n(.*?)\n```', body, re.S | re.M)
        mini = re.search(r'^Mini-Lang 原文：\n\n```zh\n(.*?)\n```', body, re.S | re.M)
        if zh:
            out.append({'title': title, 'dir': 'to-mini', 'text': zh.group(1)})
        elif mini:
            out.append({'title': title, 'dir': 'to-zh', 'text': mini.group(1)})
    return out

def charset_groups():
    """附錄字表的分類：[[類別, 字…]]。"""
    m = re.search(r'## 附錄：完整字表.*?```text\n(.*?)```', DOC.read_text(encoding='utf-8'), re.S)
    groups = []
    for line in m.group(1).splitlines():
        if line.startswith('#'):
            groups.append([line.lstrip('# ').strip(), ''])
        elif line.strip():
            groups[-1][1] += line.strip()
    return groups

def main():
    data = {
        'charset': load_charset(DOC.read_text(encoding='utf-8')),
        'groups': charset_groups(),
        'lexicon': lexicon(),
        'pinyin': pinyin(),
        'examples': examples(),
    }
    out = Path(__file__).parent / 'data.js'
    out.write_text('// 由 build.py 產生，請勿手動修改\nconst DATA = '
                   + json.dumps(data, ensure_ascii=False) + ';\n', encoding='utf-8')
    print(f"✅ {out.name}：字表 {len(data['charset'])} 字、詞典 {len(data['lexicon'])} 條、"
          f"讀音 {len(data['pinyin'])} 條、範例 {len(data['examples'])} 段")

if __name__ == '__main__':
    main()
