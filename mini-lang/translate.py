"""通用 Mini-Lang 的翻譯輔助：查詞典，正向標出要換的詞，反向把描述與音寫還原。

這不是完整的翻譯器：正向只做「查詞典 + 標出字表外的字」，語法替換與改寫仍然要人（或大模型）做；
反向只還原詞典裡登記的描述與音寫，句子結構保持 Mini-Lang 的樣子（本來就是中文）。

用法：
    python translate.py --to-mini "雖然下雨，我還是去了醫院。"
    python translate.py --to-zh "我家有一個〔個走〕，那是會看家、會叫的小東西。"
    python translate.py --to-zh -f 文章.txt
"""
import argparse
import re
import sys

from check import DOC, load_charset, unknown
from check_universal import load_lexicon

def forward(text, rows, charset):
    """用詞典最長匹配，標出一般中文中要換掉的詞。"""
    entries = {r['中文']: r for _, _, r in rows if '…' not in r['中文']}
    longest = max(map(len, entries)) if entries else 1
    out, i, todo = [], 0, []
    while i < len(text):
        for n in range(min(longest, len(text) - i), 0, -1):
            w = text[i:i + n]
            if w in entries and unknown(w, charset):  # 只換含字表外字的詞
                r = entries[w]
                out.append(f"[{w}→{r['Mini-Lang']}]")
                todo.append(r)
                i += n
                break
        else:
            c = text[i]
            out.append(f'[{c}?]' if unknown(c, charset) else c)
            i += 1
    return ''.join(out), todo

def backward(text, rows):
    """音寫與描述還原成一般中文的詞；音寫第一次出現時的說明一併去掉。"""
    for _, _, r in rows:
        if r['方式'] == '音寫' and r['說明']:
            # 〔個走〕（說明）、〔個走〕，說明、〔個走〕，那是說明
            text = re.sub(re.escape(r['Mini-Lang']) + r'(（' + re.escape(r['說明']) + r'）|，(那是|是)?'
                          + re.escape(r['說明']) + r')', r['Mini-Lang'], text)
    phrases = {}
    for _, _, r in rows:
        # 兩個字以下的描述（例如「幾個」）太常見，還原會改錯，只還原音寫和較長的描述
        long_enough = r['方式'] == '音寫' or len(r['Mini-Lang']) >= 3
        if r['方式'] in ('描述', '音寫') and long_enough and '…' not in r['Mini-Lang'] and '／' not in r['Mini-Lang']:
            phrases.setdefault(r['Mini-Lang'], r['中文'])  # 近義詞取第一個
    if not phrases:
        return text
    pattern = re.compile('|'.join(sorted(map(re.escape, phrases), key=len, reverse=True)))
    return pattern.sub(lambda m: phrases[m.group(0)], text)

def main():
    p = argparse.ArgumentParser(description='通用 Mini-Lang 翻譯輔助')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--to-mini', action='store_true', help='一般中文 → 標出要換的詞')
    g.add_argument('--to-zh', action='store_true', help='Mini-Lang → 還原描述與音寫')
    p.add_argument('text', nargs='?')
    p.add_argument('-f', '--file')
    args = p.parse_args()
    text = open(args.file, encoding='utf-8').read() if args.file else args.text
    if not text:
        p.error('請給文字或 -f 檔案')
    rows = load_lexicon()
    charset = set(load_charset(DOC.read_text(encoding='utf-8')))
    if args.to_mini:
        marked, todo = forward(text, rows, charset)
        print(marked)
        left = unknown(re.sub(r'\[[^\]]*→[^\]]*\]', '', marked), charset)
        print(f"\n詞典換了 {len(todo)} 個詞；還要改寫的字：{''.join(left) or '無'}")
    else:
        print(backward(text, rows))
    return 0

if __name__ == '__main__':
    sys.exit(main())
