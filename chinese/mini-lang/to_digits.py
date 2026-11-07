"""把 Mini-Lang 文字中的中文數字換成阿拉伯數字（字表刪除了「二三四五六七八九十」）。

規則：
* 含有「二三四五六七八九十」的數字，整個換成阿拉伯數字：二十二歲 → 22歲、三百 → 300、三點半 → 3點半。
* 整萬的數保留「萬」：三萬 → 3萬。
* 多位數也換：一百 → 100、兩百多 → 200多、一千 → 1000。
* 單獨的「一、兩」不動：一個、兩點、一樣。它們常是冠詞或固定說法，程式分不出是不是在計數。
* 「第」後面一律用數字：第一次 → 第1次。
* 週幾一律用數字：週一 → 週1、星期六 → 週6（週日不變）。
* 概數：兩三天 → 2到3天。
* 固定說法另外處理（IDIOMS）。

用法：
    python to_digits.py --check 檔案...     # 只列出會怎麼換，不寫入
    python to_digits.py 檔案...             # 直接改寫檔案
"""
import re
import sys

DELETED = set('二三四五六七八九十')
DIGIT = {'零': 0, '一': 1, '二': 2, '兩': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
UNIT = {'十': 10, '百': 100, '千': 1000}
# 不是數字、或不能逐字換的說法
IDIOMS = {'十分好': '很好', '十字路口': '路口', '十幾': '10多', '幾十': '很多'}
NUMBER = re.compile(r'[零一二兩三四五六七八九十百千萬]+')
WEEK = re.compile(r'週([一二三四五六])')
ORDINAL = re.compile(r'第([一兩])(?![百千萬])')

def value(s):
    """中文數字 → 整數：二十二 → 22、一百二十 → 120、三萬 → 30000。"""
    total, section, num = 0, 0, 0
    for c in s:
        if c in DIGIT:
            num = DIGIT[c]
        elif c in UNIT:
            section += (num or 1) * UNIT[c]
            num = 0
        elif c == '萬':
            total += (section + num) * 10000
            section, num = 0, 0
    return total + section + num

def convert(text):
    for a, b in IDIOMS.items():
        text = text.replace(a, b)
    text = re.sub(r'(星期|禮拜)(?=[一二三四五六日天])', '週', text)
    text = WEEK.sub(lambda m: '週' + str(DIGIT[m.group(1)]), text)
    text = ORDINAL.sub(lambda m: '第' + str(DIGIT[m.group(1)]), text)

    def repl(m):
        s = m.group(0)
        if len(s) == 2 and all(c in DIGIT for c in s) and DIGIT[s[1]] == DIGIT[s[0]] + 1:
            return f'{DIGIT[s[0]]}到{DIGIT[s[1]]}'  # 兩三天 → 2到3天
        if not DELETED & set(s) and not (len(s) > 1 and set(s) & set('百千萬')):
            return s
        v = value(s)
        return f'{v // 10000}萬' if v >= 10000 and v % 10000 == 0 else str(v)
    return NUMBER.sub(repl, text)

def main():
    check = sys.argv[1] == '--check'
    for path in sys.argv[2:] if check else sys.argv[1:]:
        old = open(path, encoding='utf-8').read()
        new = '\n'.join(convert(line) for line in old.split('\n'))
        if check:
            for a, b in zip(old.split('\n'), new.split('\n')):
                if a != b:
                    print(f'{path}: {a}\n{" " * len(path)}→ {b}')
        elif new != old:
            open(path, 'w', encoding='utf-8').write(new)
            print(f'已改寫 {path}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
