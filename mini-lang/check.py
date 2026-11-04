"""檢查 mini-lang.md：字表是否沒有重複的字（目前 297 字），例句與組合例是否只用到字表內的字。

用法：
    python check.py                 # 檢查 mini-lang.md
    python check.py "我想喝茶。"     # 檢查自己寫的句子
    python check.py --file a.txt …  # 逐行檢查語料檔（漢字都要在字表內，也不能有英文字母；問答標記 <Q> <A> 不算）
"""
import re
import sys
from pathlib import Path

DOC = Path(__file__).with_name('mini-lang.md')
# 表格中這些欄位的內容必須是 Mini-Lang
CHECKED_COLUMNS = {'組合例', '例子', '例句', 'Mini-Lang 說法'}
CJK = re.compile(r'[一-鿿]')

def load_charset(text):
    m = re.search(r'## 附錄：完整字表.*?```text\n(.*?)```', text, re.S)
    if not m:
        sys.exit('找不到「附錄：完整字表」區塊')
    chars = ''.join(line.strip() for line in m.group(1).splitlines()
                    if line.strip() and not line.startswith('#'))
    return chars

def snippets(text):
    """產生 (位置說明, 要檢查的文字)。"""
    lines = text.splitlines()
    in_zh, header = False, None
    for no, line in enumerate(lines, 1):
        if line.startswith('```'):
            in_zh = line.strip() == '```zh'
            continue
        if in_zh:
            # 對話中「名字：」是說話者標籤，不算內容
            yield no, re.sub(r'^[^：]{1,3}：', '', line)
        elif line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            if header is None:
                header = cells
            else:
                for name, cell in zip(header, cells):
                    if name in CHECKED_COLUMNS:
                        # 全形括號內是一般中文的對照說明，不檢查
                        yield no, re.sub(r'（.*?）', '', cell)
        else:
            header = None

def unknown(text, charset):
    return sorted({c for c in CJK.findall(text) if c not in charset})

def main():
    text = DOC.read_text(encoding='utf-8')
    chars = load_charset(text)
    charset = set(chars)

    if sys.argv[1:2] == ['--file']:
        return check_files(sys.argv[2:], charset)

    if len(sys.argv) > 1:
        bad = unknown(' '.join(sys.argv[1:]), charset)
        print('✅ 全部在字表內' if not bad else f"❌ 字表外的字: {''.join(bad)}")
        return 1 if bad else 0

    ok = True
    dups = sorted({c for c in chars if chars.count(c) > 1})
    print(f'字表: {len(chars)} 字，不重複 {len(charset)} 字')
    if dups:
        print(f"❌ 字表有重複的字: {''.join(dups)}")
        ok = False

    # 第 2 節各類表格第一欄的字，必須和完整字表一致
    section2 = text[text.index('## 2.'):text.index('## 3.')]
    table_chars = set(re.findall(r'^\| (\S) \| ', section2, re.M))
    if table_chars != charset:
        print(f"❌ 字表表格與完整字表不一致: 多 {''.join(sorted(table_chars - charset))}"
              f" 少 {''.join(sorted(charset - table_chars))}")
        ok = False

    n = 0
    for no, s in snippets(text):
        n += 1
        bad = unknown(s, charset)
        if bad:
            print(f"❌ 第 {no} 行用了字表外的字 {''.join(bad)}: {s}")
            ok = False
    print(f'檢查了 {n} 段例句與組合例')
    print('✅ 全部通過' if ok else '❌ 有錯誤')
    return 0 if ok else 1

def check_files(paths, charset):
    n = n_bad = 0
    for path in paths:
        for no, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
            n += 1
            line = re.sub(r'<[QA]>', '', line)
            bad = unknown(line, charset) + sorted(set(re.findall(r'[A-Za-z]', line)))
            if bad:
                n_bad += 1
                if n_bad <= 20:
                    print(f"❌ {path}:{no} 字表外的字 {''.join(bad)}: {line}")
    print(f'檢查了 {len(paths)} 個檔案、{n} 行：' + ('✅ 全部在字表內' if not n_bad else f'❌ {n_bad} 行有字表外的字'))
    return 1 if n_bad else 0

if __name__ == '__main__':
    sys.exit(main())
