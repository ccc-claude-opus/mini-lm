#!/usr/bin/env python3
"""檢查 Mini-English：文字是不是只用詞表內的詞。

用法：
    python check.py                 # 自我檢查 mini-english.md（詞表、例句、附錄一致）
    python check.py "some text"     # 檢查一段文字
    python check.py --file a.txt …  # 逐行檢查檔案（同一個檔案算同一篇文章）

規則摘要：
  * 只接受：附錄「完整詞表」裡的詞、附錄「保留的不規則形式」、片語動詞例外、
    以及用允許字首字尾接在表內詞後面的形式（un-/re-、-er/-est/-ly/-ness）。
  * 大寫開頭、表外的詞 = 外來詞（人名、地名、物種、品牌、術語）：
    第一次出現時必須有括號說明，之後可以直接用。
  * 括號裡的說明本身也要檢查（只能用 Mini-English 的詞）。
  * 阿拉伯數字、標點、中文字（作外來詞用）另外處理。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from morph import accepted_forms

HERE = Path(__file__).parent
DOC = HERE / 'mini-english.md'

# 表格中這些欄名的內容必須是 Mini-English
CHECKED_COLUMNS = {'例子', '例句', '組合例', 'Mini-English 替代', 'Mini-English'}

# ── 讀規格 ───────────────────────────────────────────────────────────────────


def _text_block(text, heading):
    m = re.search(re.escape(heading) + r'.*?```text\n(.*?)```', text, re.S)
    if not m:
        sys.exit(f'找不到「{heading}」的 ```text 區塊')
    return [l.strip() for l in m.group(1).splitlines() if l.strip()]


def _table_after(text, heading):
    """取 heading 之後的第一個 markdown 表格，回傳 list of dict。"""
    i = text.index(heading) + len(heading)
    rows = []
    header = None
    for line in text[i:].splitlines():
        line = line.strip()
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            if header is None:
                header = cells
            else:
                rows.append(dict(zip(header, cells)))
        elif header is not None and rows:
            break
    return rows


def _section_tables(text, start_heading, end_heading):
    """取一個章節裡的所有表格（可以有多個），回傳 list of dict。"""
    i = text.index(start_heading) + len(start_heading)
    j = text.index(end_heading) if end_heading in text else len(text)
    rows, header = [], None
    for line in text[i:j].splitlines():
        line = line.strip()
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            if header is None:
                header = cells
            else:
                rows.append(dict(zip(header, cells)))
        else:
            header = None
    return rows


class Spec:
    def __init__(self, text):
        self.words = set()
        self.levels = {}
        for line in _text_block(text, '## 附錄：完整詞表'):
            if line.startswith('#'):
                continue
            self.words.add(line.lower())
            self.levels[line.lower()] = line
        irr = {}
        for row in _table_after(text, '## 附錄：保留的不規則形式'):
            lemma = row['原形'].lower()
            self.words.add(lemma)
            irr[lemma] = [f.strip().lower() for f in row['不規則形式'].split(' / ') if f.strip()]
        # 詞性
        self.pos = {}
        for row in _section_tables(text, '## 2. 詞表', '## 3. 三層表達法'):
            if '詞' in row and 'IPA' in row:
                self.pos[row['詞'].strip().lower()] = row.get('詞性', '')
        # 可以直接寫出來的形式（屈折 + 不規則）
        self.forms = set(self.words)
        for w, pos in self.pos.items():
            self.forms.update(accepted_forms(w, pos, irr))
        for lemma, fs in irr.items():
            self.forms.update(fs)
        self.phrasal = set()
        for line in _text_block(text, '## 附錄：片語動詞（例外）'):
            self.phrasal.add(line.lower())
            self.forms.add(line.lower())
        self.prefixes, self.suffixes = [], []
        for row in _table_after(text, '## 附錄：允許的字首字尾'):
            affix = row['字首／字尾'].strip('`').lower()
            if row['類型'] == 'prefix':
                self.prefixes.append(affix.rstrip('-'))     # un- → un
            else:
                self.suffixes.append(affix.lstrip('-'))     # -er → er
        self.replace = {}
        for row in _table_after(text, '## 附錄：常用但禁止的詞與替代說法'):
            self.replace[row['英文（不在核心層、常用）'].lower()] = row['Mini-English 說法']
        self.common = set()
        cw = HERE / 'data' / 'common_words.tsv'
        if cw.exists():
            self.common = {l.split('\t')[0] for l in cw.read_text(encoding='utf-8').splitlines()[1:] if l.strip()}

    def is_derivable(self, w):
        """是不是「表內詞 ＋ 允許的字首字尾」。"""
        for p in self.prefixes:
            if w.startswith(p) and len(w) > len(p):
                stem = w[len(p):]
                if stem in self.words or stem in self.forms:
                    kinds = self.pos.get(stem, '')
                    if p == 'un' and 'adj' in kinds:
                        return True
                    if p == 're' and 'v' in kinds:
                        return True
                    if p not in ('un', 're') and (stem in self.words or stem in self.forms):
                        return True
        for s in self.suffixes:
            if w.endswith(s) and len(w) > len(s):
                stem = w[:-len(s)]
                if stem in self.words or stem in self.forms:
                    kinds = self.pos.get(stem, '')
                    if s == 'er' and ('v' in kinds or 'adj' in kinds):
                        return True
                    if s == 'est' and 'adj' in kinds:
                        return True
                    if s == 'ly' and 'adj' in kinds:
                        return True
                    if s == 'ness' and 'adj' in kinds:
                        return True
        return False


# ── 檢查一段文字 ─────────────────────────────────────────────────────────────
TOKEN = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*(?:-[A-Za-z]+)*|\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?|[\u4e00-\u9fff\u3400-\u4dbf]+")
PAREN = re.compile(r'\(([^()]*)\)')
SPEAKER = re.compile(r'^\s*[A-Za-z][A-Za-z ]{0,12}:\s*')

# 常見的專有名詞（即使在句首，也要當外來詞處理）
PROPER = {
    'paris', 'china', 'japan', 'korea', 'taiwan', 'india', 'england', 'scotland',
    'wales', 'ireland', 'france', 'germany', 'italy', 'spain', 'russia', 'canada',
    'australia', 'brazil', 'mexico', 'london', 'tokyo', 'beijing', 'shanghai',
    'hong', 'kong', 'taipei', 'seoul', 'new', 'york', 'los', 'angeles', 'paris',
    'tokyo', 'osaka', 'kyoto', 'europe', 'asia', 'africa', 'america', 'european',
    'asian', 'african', 'american', 'chinese', 'japanese', 'korean', 'english',
    'french', 'german', 'spanish', 'italian', 'russian', 'british', 'covid',
    'instagram', 'google', 'apple', 'microsoft', 'amazon', 'toyota', 'samsung',
    'wifi', 'internet', 'email', 'iphone', 'youtube', 'facebook', 'twitter',
}

NOT_STEMS = {'wo': 'will', 'ca': 'can', 'sha': 'shall', 'mu': 'must', 'ne': 'need',
             'ai': 'is', 'ar': 'are', 'we': 'were', 'ha': 'has', 'do': 'does'}


def _sentence_start(text, pos):
    """這個位置是不是句子的開頭。"""
    head = text[:pos]
    for ch in reversed(head):
        if ch in '.!?\n':
            return True
        if ch.isalnum():
            return False
    return True


def contraction_ok(token, spec):
    """縮寫是不是表內的詞。回傳 (ok, 說明)。"""
    t = token.lower().replace('’', "'")
    if t in spec.words or t in spec.forms:
        return True, ''
    if t == 'cannot':
        return True, ''
    if t.endswith("n't"):
        stem = t[:-3]
        stem = NOT_STEMS.get(stem, stem)
        if stem in spec.words or stem in spec.forms:
            return True, ''
        return False, f'{token} 的原形 {stem} 不在表內'
    if t.endswith("'s"):
        base = t[:-2]
        if base in spec.words or base in spec.forms:
            return True, ''
        return False, f'{token} 的原形 {base} 不在表內'
    for suf, repl in (("'ll", 'will'), ("'ve", 'have'), ("'re", 'are'), ("'m", 'am')):
        if t.endswith(suf):
            base = t[:-len(suf)]
            if suf == "'d":
                if base in spec.words or base in spec.forms:
                    return True, ''
                return False, f'{token} 的原形 {base} 不在表內'
            if base in spec.words or base in spec.forms:
                return True, ''
            return False, f'{token} 的原形 {base} 不在表內'
    return False, ''


def check_text(text, spec, defined=None, in_paren=False, allow_proper=False):
    """回傳錯誤清單 [(類型, 說明, 片段)]。"""
    errors = []
    if defined is None:
        defined = set()
    # 多字禁用詞（a lot of、in order to…）先抓，抓到後整段跳過
    phrase_spans = []
    for phrase in sorted((p for p in spec.replace if ' ' in p), key=len, reverse=True):
        for m in re.finditer(r'(?<![A-Za-z])' + re.escape(phrase) + r'(?![A-Za-z])', text, re.I):
            errors.append(('禁用詞', f'「{m.group(0)}」是禁用詞，改用「{spec.replace[phrase.lower()]}」', m.group(0)))
            phrase_spans.append((m.start(), m.end()))
    # 專有名詞（例如 Li Ming、The Great Wall of China）＋括號說明 → 全部視為已說明
    for m in re.finditer(r'([A-Z][A-Za-z]*(?:\s+[A-Za-z]+)*)\s*\(', text):
        for w in m.group(1).split():
            if w[0].isupper():
                defined.add(w)
    # 先找出括號的位置：括號裡的說明也要檢查，但裡面的外來詞不用再說明
    paren_spans = [(m.start(), m.end()) for m in PAREN.finditer(text)]
    # 對應每個字元的括號狀態
    def is_in_paren(pos):
        return any(a <= pos < b for a, b in paren_spans)

    for m in TOKEN.finditer(text):
        tok = m.group(0)
        pos = m.start()
        par = is_in_paren(pos)
        # 在多字禁用詞裡的片段，不再重複報
        if any(a <= pos < b for a, b in phrase_spans):
            continue
        # 數字
        if tok[0].isdigit():
            continue
        # 中文 = 外來詞
        if re.match(r'[\u4e00-\u9fff\u3400-\u4dbf]', tok):
            if par:
                continue
            nxt = text[m.end():].lstrip()
            if nxt.startswith('('):
                defined.add(tok)
                continue
            if tok in defined:
                continue
            errors.append(('外來詞', f'中文外來詞「{tok}」第一次出現時必須有括號說明', tok))
            continue
        # 連字符：拆開檢查
        if '-' in tok:
            parts = [p for p in tok.split('-') if p]
            ok = all(p.lower() in spec.words or p.lower() in spec.forms for p in parts)
            if not ok:
                for p in parts:
                    if not (p.lower() in spec.words or p.lower() in spec.forms):
                        errors.append(('未知詞', f'「{p}」不在詞表內', tok))
            continue
        low = tok.lower()
        if low in spec.words or low in spec.forms:
            continue
        ok, why = contraction_ok(tok, spec)
        if ok:
            continue
        if why:
            errors.append(('未知詞', why, tok))
            continue
        if spec.is_derivable(low):
            continue
        # 表外的詞，後面緊接著括號說明 → 當成外來詞（先定義、後沿用）
        nxt = text[m.end():].lstrip()
        if nxt.startswith('(') and not par:
            defined.add(tok)
            continue
        # 前面已經說明過的外來詞，之後直接用
        if tok in defined or tok.lower() in defined:
            continue
        # 分類
        if low in spec.replace and not tok[0].isupper():
            errors.append(('禁用詞', f'「{tok}」是禁用詞，改用「{spec.replace[low]}」', tok))
            continue
        # 大寫開頭、表外的詞 = 外來詞（人名、地名、物種、品牌、術語）
        if tok[0].isupper():
            if par:
                continue
            nxt = text[m.end():].lstrip()
            if nxt.startswith('('):
                defined.add(tok)
                continue
            if tok in defined:
                continue
            if allow_proper:
                continue
            if low in PROPER or not _sentence_start(text, pos):
                errors.append(('外來詞', f'「{tok}」是外來詞，第一次出現時必須有括號說明', tok))
                continue
        if low in spec.common:
            errors.append(('未知詞', f'「{tok}」不在詞表內（用描述或外來詞）', tok))
            continue
        errors.append(('未知詞', f'「{tok}」不在詞表內（用描述或外來詞）', tok))
    return errors, defined


# ── 從 mini-english.md 取出要檢查的片段 ──────────────────────────────────────
def snippets(text):
    """產生 (位置說明, 要檢查的文字, 文件編號)。同一個英文區塊算同一篇文章。"""
    lines = text.splitlines()
    in_en, header, block_no = False, None, 0
    for no, line in enumerate(lines, 1):
        if line.startswith('```'):
            if line.strip() == '```en':
                in_en = True
                block_no += 1
            else:
                in_en = False
            continue
        if in_en:
            s = SPEAKER.sub('', line)
            if s.strip():
                yield f'第 {no} 行（英文區塊 {block_no}）', s, f'en{block_no}'
            continue
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            if header is None:
                header = cells
            else:
                for name, cell in zip(header, cells):
                    if name in CHECKED_COLUMNS:
                        s = re.sub(r'（.*?）', '', cell)
                        s = s.replace('\\|', '|')
                        if s.strip():
                            yield f'第 {no} 行（{name}欄）', s, f'cell{no}-{name}'
        else:
            header = None


def main():
    if not DOC.exists():
        sys.exit('找不到 mini-english.md')
    doc = DOC.read_text(encoding='utf-8')
    spec = Spec(doc)

    if sys.argv[1:2] == ['--file']:
        return check_files(sys.argv[2:], spec)
    if sys.argv[1:2] == ['--md']:
        return check_md(sys.argv[2] if len(sys.argv) > 2 else 'examples.md', spec)
    if sys.argv[1:2] == ['--lexicon']:
        return check_lexicon(sys.argv[2] if len(sys.argv) > 2 else 'lexicon.tsv', spec)
    if len(sys.argv) > 1:
        errors, _ = check_text(' '.join(sys.argv[1:]), spec)
        if not errors:
            print('✅ 全部在字表內')
            return 0
        for kind, msg, tok in errors:
            print(f'❌ {kind}：{msg}')
        return 1
    return self_check(doc, spec)


def check_md(path, spec):
    """檢查 markdown 檔裡的 ```en 區塊（Mini-English 文字），其他內容不檢查。"""
    p = Path(path)
    if not p.exists():
        print(f'❌ 找不到 {path}')
        return 1
    defined = set()
    blocks = []
    cur = None
    for no, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if line.startswith('```'):
            if line.strip() == '```en':
                cur = []
                start = no
            else:
                if cur is not None:
                    blocks.append((start, '\n'.join(cur)))
                cur = None
            continue
        if cur is not None:
            cur.append(line)
    if cur is not None:
        blocks.append((start, '\n'.join(cur)))
    bad = 0
    for start, text in blocks:
        for i, line in enumerate(text.splitlines()):
            s = SPEAKER.sub('', line)
            if not s.strip():
                continue
            errs, defined = check_text(s, spec, defined)
            if errs:
                bad += 1
                for k, m, _ in errs:
                    print(f'❌ {path}:{start+i} {k}：{m}　→　{s.strip()[:90]}')
    print(f'{path}：{len(blocks)} 個 ```en 區塊，' + ('✅ 全部在字表內' if not bad else f'❌ {bad} 行有問題'))
    return 1 if bad else 0


def check_lexicon(path, spec):
    """檢查詞典 lexicon.tsv：每一列的 Mini-English 都要合規則。"""
    p = Path(path)
    if not p.exists():
        print(f'❌ 找不到 {path}')
        return 1
    lines = p.read_text(encoding='utf-8').splitlines()
    header = lines[0].split('\t')
    want = ['English', 'Mini-English', '方式', '說明']
    if header != want:
        print(f'❌ 欄位必須是 {want}，現在是 {header}')
        return 1
    ways = {'本詞', '描述', '外來詞'}
    seen = set()
    bad = 0
    stat = {'本詞': 0, '描述': 0, '外來詞': 0}
    words = 0
    for no, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        f = line.split('\t')
        while len(f) < 4:
            f.append('')
        eng, mini, way, note = f
        words += 1
        if eng.lower() in seen:
            print(f'❌ 第 {no} 行：{eng} 重複')
            bad += 1
            continue
        seen.add(eng.lower())
        if way not in ways:
            print(f'❌ 第 {no} 行：方式必須是 本詞／描述／外來詞')
            bad += 1
            continue
        stat[way] += 1
        if way == '本詞':
            if mini.lower() not in spec.words:
                print(f'❌ 第 {no} 行：{eng} 標成本詞，但 {mini} 不在詞表內')
                bad += 1
            continue
        if way == '外來詞':
            if not note.strip():
                print(f'❌ 第 {no} 行：{eng} 是外來詞，必須有說明')
                bad += 1
                continue
            errs, _ = check_text(note, spec, allow_proper=True)
            if errs:
                bad += 1
                for k, m, _ in errs:
                    print(f'❌ 第 {no} 行（{eng} 的說明）{k}：{m}')
            continue
        # 描述
        errs, _ = check_text(mini, spec)
        if errs:
            bad += 1
            for k, m, _ in errs:
                print(f'❌ 第 {no} 行（{eng}）{k}：{m}　→　{mini}')
    print(f'詞典 {path}：{words} 列（本詞 {stat["本詞"]}／描述 {stat["描述"]}／外來詞 {stat["外來詞"]}）')
    print('✅ 全部通過' if not bad else f'❌ {bad} 列有問題')
    return 1 if bad else 0


def check_files(paths, spec):
    total = bad = 0
    for path in paths:
        p = Path(path)
        defined = set()          # 同一個檔案算同一篇文章
        in_text = False
        for no, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            if line.startswith('```'):
                # ```text 是「一般英文」或權威詞表，不檢查；```en 是 Mini-English，要檢查
                in_text = not line.startswith('```en')
                if in_text:
                    continue
            if in_text:
                continue
            if not line.strip():
                continue
            total += 1
            errors, defined = check_text(line, spec, defined)
            if errors:
                bad += 1
                if bad <= 30:
                    for kind, msg, _ in errors:
                        print(f'❌ {path}:{no} {kind}：{msg}　→　{line.strip()[:80]}')
    print(f'檢查了 {len(paths)} 個檔案、{total} 行：' +
          ('✅ 全部在字表內' if not bad else f'❌ {bad} 行有問題'))
    return 1 if bad else 0


def self_check(doc, spec):
    ok = True
    # 1. 附錄沒有重複
    words = [l for l in _text_block(doc, '## 附錄：完整詞表') if not l.startswith('#')]
    dups = sorted({w for w in words if words.count(w) > 1})
    print(f'詞表：{len(words)} 詞，不重複 {len(set(words))} 詞')
    if dups:
        print(f"❌ 詞表有重複：{', '.join(dups)}")
        ok = False
    # 2. 第 2 節的表格與附錄一致
    table_words = set()
    for row in _section_tables(doc, '## 2. 詞表', '## 3. 三層表達法'):
        if '詞' in row and 'IPA' in row:
            table_words.add(row['詞'].strip().lower())
    appendix = {w.lower() for w in words}
    if table_words != appendix:
        extra = sorted(table_words - appendix)
        lack = sorted(appendix - table_words)
        print(f'❌ 詞表表格與完整詞表不一致：多 {extra}　少 {lack}')
        ok = False
    # 3. 所有例句通過檢查
    n = 0
    defined_by_doc = {}
    for where, s, key in snippets(doc):
        n += 1
        errors, _ = check_text(s, spec, defined_by_doc.setdefault(key, set()))
        if errors:
            ok = False
            for kind, msg, _ in errors:
                print(f'❌ {where} {kind}：{msg}　→　{s[:90]}')
    print(f'檢查了 {n} 段例句與例子')
    # 4. 提示詞的詞表與本文件一致
    prompt = HERE / 'prompts' / 'system.md'
    if prompt.exists():
        try:
            pwords = []
            for line in _text_block(prompt.read_text(encoding='utf-8'), '## 1. 詞表'):
                if not line.startswith('#'):
                    pwords.append(line.lower())
            if set(pwords) != appendix:
                print('❌ prompts/system.md 的詞表和 mini-english.md 不一樣，請重新複製附錄的詞表')
                ok = False
            else:
                print(f'✅ prompts/system.md 的詞表一致（{len(pwords)} 詞）')
        except SystemExit:
            pass
    print('✅ 全部通過' if ok else '❌ 有錯誤')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
