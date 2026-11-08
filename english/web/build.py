"""把 Mini-English 的詞表、詞典、範例打包成 data.js，給網頁使用。

詞表或詞典更新後重新執行：
    python web/build.py
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from check import DOC, Spec  # noqa: E402

LEXICON = ROOT / 'lexicon.tsv'


def words():
    """§2 的詞表：[詞, IPA, 層, 詞性, 中文意思, 允許的形式, 例子, 類別]。"""
    doc = DOC.read_text(encoding='utf-8')
    m = re.search(r'## 2\. 詞表(.*?)\n## 3\.', doc, re.S)
    if not m:
        sys.exit('找不到 §2 詞表')
    out = []
    category = ''
    for line in m.group(1).splitlines():
        head = re.match(r'### 2\.\d+ (.+?)（', line)
        if head:
            category = head.group(1)
            continue
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) != 7 or cells[0] in ('詞', '---'):
            continue
        w, ipa, level, pos, zh, forms, example = cells
        out.append([w, ipa.strip('/'), level, pos, zh, forms, example, category])
    return out


def groups():
    """附錄的分類：[[類別, 層, 詞…]]。"""
    doc = DOC.read_text(encoding='utf-8')
    m = re.search(r'## 附錄：完整詞表.*?```text\n(.*?)```', doc, re.S)
    out = []
    for line in m.group(1).splitlines():
        if line.startswith('#'):
            head = line.lstrip('# ').strip()
            level, _, name = head.partition('｜')
            out.append([name.strip(), level.strip(), []])
        elif line.strip() and out:
            out[-1][2].append(line.strip())
    return out


def lexicon():
    """詞典：[English, Mini-English, 方式, 說明]。"""
    rows = []
    with open(LEXICON, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            rows.append([r['English'], r['Mini-English'], r['方式'], r['說明']])
    return rows


def reverse_map():
    """描述 → 英文詞（給 Mini-English → English 用）。"""
    path = ROOT / 'data' / 'reverse.tsv'
    out = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines()[1:]:
            if line.strip():
                mini, eng = line.split('\t')[:2]
                out[mini.strip()] = eng.strip()
    return out


def forbidden():
    """禁用詞 → 替代說法。"""
    doc = DOC.read_text(encoding='utf-8')
    m = re.search(r'## 附錄：常用但禁止的詞與替代說法(.*?)(\n## |\Z)', doc, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) != 2 or cells[0] in ('英文（不在核心層、常用）', '---'):
            continue
        out[cells[0]] = cells[1]
    return out


def examples():
    """examples.md 的範例：[標題, 方向, 文字]。"""
    text = (ROOT / 'examples.md').read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r'## (範例[^\n：]*：.+?|反向翻譯[^\n：]*：.+?)\n(.*?)(?=\n## |\Z)', text, re.S):
        title, body = m.group(1), m.group(2)
        en = re.search(r'```text\n(.*?)\n```', body, re.S)
        mini = re.search(r'```en\n(.*?)\n```', body, re.S)
        if mini:
            out.append([title, 'to-mini', mini.group(1)])
        elif en:
            out.append([title, 'to-en', en.group(1)])
    return out


def rules():
    """語法規則：[[規則, 例句…]]。"""
    doc = DOC.read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r'### (規則 \d+　.+?)\n\n```en\n(.*?)\n```', doc, re.S):
        out.append([m.group(1).strip(), m.group(2).strip()])
    return out


def main():
    spec = Spec(DOC.read_text(encoding='utf-8'))
    data = {
        'words': words(),
        'groups': groups(),
        'lexicon': lexicon(),
        'reverse': reverse_map(),
        'forbidden': forbidden(),
        'examples': examples(),
        'rules': rules(),
        'forms': sorted(spec.forms),
        'affixes': {'prefixes': spec.prefixes, 'suffixes': spec.suffixes},
        'phrasal': sorted(spec.phrasal),
        'stats': {
            'words': len(spec.words),
            'core': sum(1 for w in spec.pos if spec.pos[w]),
            'lexicon': sum(1 for _ in lexicon()),
        },
    }
    out = ROOT / 'web' / 'data.js'
    out.parent.mkdir(exist_ok=True)
    out.write_text('const DATA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')
    print(f'✅ {out}：{len(data["words"])} 個詞、{len(data["lexicon"])} 條詞典、'
          f'{len(data["examples"])} 段範例、{len(data["rules"])} 條規則')


if __name__ == '__main__':
    main()
