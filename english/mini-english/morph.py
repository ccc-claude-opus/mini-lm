"""Mini-English 的屈折規則：build.py（產生表格）與 check.py（檢查）共用。"""


# 需要重複最後一個字母的動詞（cut → cutting, stop → stopping）
DOUBLE_V = {
    'cut', 'stop', 'plan', 'sit', 'run', 'swim', 'drop', 'beg', 'hug', 'rub', 'jog',
    'fit', 'get', 'put', 'let', 'set', 'bet', 'shut', 'ship', 'shop', 'skip', 'step',
    'stir', 'tap', 'wrap', 'grab', 'occur', 'prefer', 'refer', 'admit', 'permit',
    'commit', 'regret', 'forget', 'begin', 'control', 'pat', 'chat', 'clap', 'plot',
    'spot', 'strap', 'tug', 'ban', 'eject', 'equip', 'hand', 'win',
}
# 需要重複最後一個字母的形容��（big → bigger, hot → hotter）
DOUBLE_ADJ = {'big', 'hot', 'sad', 'wet', 'fat', 'mad', 'dim', 'grim', 'flat', 'thin', 'slim'}


# 動詞第三人稱單數要加 -es 的 -o 結尾動詞（go → goes, do → does）
VERB_O_ES = {'go', 'do', 'echo'}

# -o 結尾但複數要加 -es 的少數名詞
O_ES = {'cargo', 'domino', 'echo', 'embargo', 'hero', 'torpedo', 'veto', 'volcano'}


def plural(w):
    if w.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return w + 'es'
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'ies'
    if w.endswith('o') and w in O_ES:
        return w + 'es'
    return w + 's'


def third(w):
    if w.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return w + 'es'
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'ies'
    if w.endswith('o') and w in VERB_O_ES:
        return w + 'es'
    return w + 's'


def ing(w):
    if w.endswith('ie'):
        return w[:-2] + 'ying'
    if w.endswith('e') and not w.endswith(('ee', 'ye', 'oe')):
        return w[:-1] + 'ing'
    if w in DOUBLE_V:
        return w + w[-1] + 'ing'
    return w + 'ing'


def ed(w):
    if w.endswith('e'):
        return w + 'd'
    if w.endswith('y') and w[-2:-1] not in 'aeiou':
        return w[:-1] + 'ied'
    if w in DOUBLE_V:
        return w + w[-1] + 'ed'
    return w + 'ed'


def compar(w):
    """短形容詞用 -er/-est，長的用 more/most。回傳 (比較級, 最高級)。"""
    if len(w) <= 6 and not w.endswith(('ful', 'ous', 'ing')):
        if w.endswith('e'):
            return w + 'r', w + 'st'
        if w.endswith('y') and w[-2:-1] not in 'aeiou':
            return w[:-1] + 'ier', w[:-1] + 'iest'
        if w in DOUBLE_ADJ:
            return w + w[-1] + 'er', w + w[-1] + 'est'
        return w + 'er', w + 'est'
    return 'more ' + w, 'most ' + w


IRREG_PARADIGM = {
    'be': 'be / am / is / are / was / were / been / being',
    'have': 'have / has / had',
    'do': 'do / does / did',
    'will': 'will / would',
    'can': 'can / could',
    'shall': 'shall / should',
    'may': 'may / might',
    'must': 'must',
    'need': 'need',
    'let': 'let',
}


def forms_of(w, pos, irr):
    """這個詞可以寫出來的形式（顯示用）。"""
    if w in IRREG_PARADIGM:
        return IRREG_PARADIGM[w]
    kinds = pos.split('/')
    if 'v' in kinds:
        if w in irr:
            extra = irr[w]
            past = extra[0]
            pp = extra[1] if len(extra) > 1 else extra[0]
            return ' / '.join([w, third(w), past, pp, ing(w)])
        return ' / '.join([w, third(w), ed(w), ed(w), ing(w)])
    if 'n' in kinds:
        if w in irr:
            return ' / '.join([w] + irr[w])
        return f'{w} / {plural(w)}'
    if 'adj' in kinds:
        if w in irr:
            return ' / '.join([w] + irr[w])
        c, s = compar(w)
        return ' / '.join([w, c, s])
    return w


def accepted_forms(w, pos, irr):
    """檢查時可以接受的全部形式（屈折 + 不規則）。"""
    out = {w}
    kinds = pos.split('/')
    if 'v' in kinds:
        out.add(third(w))
        out.add(ing(w))
        if w in irr:
            out.update(irr[w])      # 不規則動詞沒有規則 -ed
        else:
            out.add(ed(w))
    if 'n' in kinds:
        out.add(plural(w))
        if w in irr:
            out.update(irr[w])
    if 'adj' in kinds:
        if w in irr:
            out.update(irr[w])
        else:
            c, s = compar(w)
            out.add(c)
            out.add(s)
    if w in IRREG_PARADIGM:
        out.update(x.strip() for x in IRREG_PARADIGM[w].split(' / '))
    return out
