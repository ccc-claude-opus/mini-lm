import argparse
import os
import random
import re
import sys

# 借用 ../mini-lang/check.py 讀取 256 字表
MINILANG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mini-lang')
sys.path.insert(0, MINILANG_DIR)
from check import DOC, load_charset, unknown

parser = argparse.ArgumentParser(description='依 mini-lang.md 的字表與語法產生 Mini-Lang 語料')
parser.add_argument('--out_dir', default='corpus/minilang')
parser.add_argument('--n_sentences', type=int, default=1500, help='一般句子的數量')
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()
rng = random.Random(args.seed)

DIGITS = '一二三四五六七八九'

def num(n):
    """1–99 的中文數字。"""
    tens, ones = divmod(n, 10)
    s = ('' if tens <= 1 else DIGITS[tens - 1]) + ('十' if tens else '')
    return s + (DIGITS[ones - 1] if ones else '')

# ==========================================
# 1. 人物與事實：預訓練學事實，微調學問答格式
# ==========================================
# 名字用字表內的字組成，避開一般句子會用到的「我、你、他」
NAMES = [a + b for a in '小大' for b in '明山花文天月雨心']
JOBS = {'老師': '在學校教書', '醫生': '給人看病', '學生': '在學校學習', '工人': '每天都很忙'}
HOMES = ['東邊', '西邊', '南邊', '北邊']
FOODS = ['肉', '菜', '水果', '飯']
DRINKS = ['茶', '水', '紅茶']

people = []
for name in NAMES:
    age = rng.randint(8, 80)
    job = '學生' if age < 20 else rng.choice(['老師', '醫生', '工人'])
    kids = 0 if age < 25 else rng.randint(0, 3)
    people.append(dict(name=name, age=age, job=job, home=rng.choice(HOMES),
                       food=rng.choice(FOODS), drink=rng.choice(DRINKS), kids=kids))
for p in people:
    p['friend'] = rng.choice([q['name'] for q in people if q is not p])

def count(k):
    return '兩個' if k == 2 else num(k) + '個'

def person_facts(p):
    """同一個事實用兩種說法，讓模型學到意思而不是背一個句型。"""
    n = p['name']
    facts = [
        f"{n}今年{num(p['age'])}歲。", f"{n}{num(p['age'])}歲了。",
        f"{n}是{p['job']}。", f"{n}{JOBS[p['job']]}。",
        f"{n}的家在{p['home']}。", f"{n}住在{p['home']}。",
        f"{n}喜歡吃{p['food']}。", f"{n}最喜歡吃{p['food']}。",
        f"{n}喜歡喝{p['drink']}。", f"{n}每天都喝{p['drink']}。",
        f"{n}的朋友是{p['friend']}。", f"{n}和{p['friend']}是朋友。",
    ]
    if p['kids']:
        facts += [f"{n}有{count(p['kids'])}孩子。", f"{n}的家裡有{count(p['kids'])}孩子。"]
    else:
        facts += [f"{n}沒有孩子。", f"{n}的家裡沒有孩子。"]
    return facts

def person_qa(p):
    n = p['name']
    return [
        (f"{n}幾歲？", f"{num(p['age'])}歲"),
        (f"{n}是做什麼的？", p['job']),
        (f"{n}的家在哪裡？", p['home']),
        (f"{n}喜歡吃什麼？", p['food']),
        (f"{n}喜歡喝什麼？", p['drink']),
        (f"{n}的朋友是誰？", p['friend']),
        (f"{n}有幾個孩子？", count(p['kids']) if p['kids'] else '沒有'),
    ]

# ==========================================
# 2. 一般句子：依 mini-lang.md 第 4 節的語法規則產生
# ==========================================
SUBJECTS = ['我', '你', '他', '我們', '他們', '我的朋友', '那個老師', '這個學生',
            '我媽媽', '我爸爸', '我哥哥', '我姐姐', '我弟弟', '我妹妹']
# (動詞, 可接的賓語, 可在的地方)
ACTIONS = [
    ('吃', ['飯', '肉', '菜', '水果'], ['家裡', '飯店']),
    ('喝', ['水', '茶', '紅茶'], ['家裡', '飯店']),
    ('看', ['書'], ['家裡', '學校', '房間裡']),
    ('寫', ['字'], ['家裡', '學校']),
    ('學', ['中文'], ['家裡', '學校']),
    ('買', ['東西', '水果', '衣服'], ['店裡']),
    ('做', ['飯', '菜'], ['家裡']),
    ('洗', ['手', '衣服'], ['家裡']),
    ('打', ['電話'], ['家裡', '外邊']),
    ('開', ['車'], ['外邊']),
]
PAST = ['昨天', '昨天晚上', '上週', '去年']
FUTURE = ['明天', '明天早上', '下週', '明年']
HABIT = ['每天', '每天早上', '週日']
ADJ = [('天氣', ['冷', '熱', '好']), ('這個菜', ['好吃', '貴']), ('那個房間', ['大', '小']),
       ('中文', ['難', '有意思']), ('火車站', ['遠', '近']), ('那個山', ['高']), ('這些衣服', ['貴', '新'])]
FAMILY = ['我爸爸', '我媽媽', '我哥哥', '我姐姐', '我弟弟', '我妹妹']
SIBLINGS = ['我哥哥', '我姐姐', '我弟弟', '我妹妹']
BECAUSE = [('下雨了', '不去外邊'), ('天氣很冷', '要多穿衣服'), ('很忙', '沒有時間'),
           ('生病了', '要去看醫生'), ('想學中文', '每天都寫字'), ('太貴了', '不買')]
IF = [('明天下雨', '在家裡看書'), ('你有時間', '來我家吃飯'), ('天氣好', '去外邊玩'),
      ('你不懂', '問老師'), ('這個不貴', '買兩個')]

def pronoun(s):
    """第二次提到同一個人時改用代詞，例如「我妹妹…，所以他…」。"""
    return s if s in ('我', '你', '他', '我們', '他們') else '他'

def sentence():
    s = rng.choice(SUBJECTS)
    v, objs, places = rng.choice(ACTIONS)
    o, pl = rng.choice(objs), rng.choice(places)
    kind = rng.randrange(10)
    if kind == 0:   # 規則 2、3、11：過去完成
        return f"{rng.choice(PAST)}{s}在{pl}{v}了{o}。"
    if kind == 1:   # 規則 9：過去否定用「沒」
        return f"{rng.choice(PAST)}{s}沒{v}{o}。"
    if kind == 2:   # 規則 12：將來
        return f"{rng.choice(FUTURE)}{s}{rng.choice(['要', '想', '不想', '會'])}{v}{o}。"
    if kind == 3:   # 習慣
        return f"{s}{rng.choice(HABIT)}都在{pl}{v}{o}。"
    if kind == 4:   # 規則 11：正在
        return f"{s}現在在{v}{o}。"
    if kind == 5:   # 規則 10：是非問句
        return f"{s}{rng.choice(['喜歡', '想', '要'])}{v}{o}嗎？"
    if kind == 6:   # 規則 6：性質謂語
        n, adjs = rng.choice(ADJ)
        adv = rng.choice(['很', '太', '不', '真'])
        return f"{n}{adv}{rng.choice(adjs)}{'了' if adv == '太' else ''}。"
    if kind == 7:   # 規則 13：比較
        adj = rng.choice(['高', '大', '忙'])
        a, b = rng.sample(SIBLINGS if adj == '大' else FAMILY, 2)
        return f"{a}比{b}{adj}。"
    if kind == 8:   # 規則 17：因為…所以…
        r, res = rng.choice(BECAUSE)
        return f"因為{s}{r}，所以{pronoun(s)}{res}。" if r in ('很忙', '生病了', '想學中文') else f"因為{r}，所以{s}{res}。"
    c, act = rng.choice(IF)  # 規則 17：如果…就…
    return f"如果{c}，{'我們' if c.startswith('你') else s}就{act}。"

# ==========================================
# 3. mini-lang.md 中的例句與對話
# ==========================================
def doc_sentences():
    text = open(DOC, encoding='utf-8').read()
    lines = []
    for block in re.findall(r'```zh\n(.*?)```', text, re.S):
        for line in block.splitlines():
            line = line.replace(' ', '').strip()
            if line:
                lines.append(line)
    return lines

# ==========================================
# 4. 輸出並檢查
# ==========================================
charset = set(load_charset(open(DOC, encoding='utf-8').read()))

facts = [f for p in people for f in person_facts(p)]
general = list(dict.fromkeys(sentence() for _ in range(args.n_sentences * 3)))[:args.n_sentences]
examples = doc_sentences()
pretrain = list(dict.fromkeys(facts + general + examples))
qa = [f"<Q>{q}<A>{a}" for p in people for q, a in person_qa(p)]

bad = unknown(''.join(pretrain + [q.replace('<Q>', '').replace('<A>', '') for q in qa]), charset)
if bad:
    sys.exit(f"❌ 產生的語料用了字表外的字: {''.join(bad)}")

os.makedirs(args.out_dir, exist_ok=True)
with open(os.path.join(args.out_dir, 'pretrain.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(pretrain) + '\n')
with open(os.path.join(args.out_dir, 'finetune.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(qa) + '\n')
# 完整的 256 字（加上標點）放進詞表，讓詞表大小固定，不隨語料改變
punct = sorted({c for c in ''.join(pretrain + qa) if c not in charset and not c.isascii()})
with open(os.path.join(args.out_dir, 'charset.txt'), 'w', encoding='utf-8') as f:
    f.write(''.join(sorted(charset)) + ''.join(punct) + '\n')

print(f"✅ 人物 {len(people)} 位，事實 {len(facts)} 句，一般句子 {len(general)} 句，"
      f"文件例句 {len(examples)} 句，問答 {len(qa)} 組")
print(f"   已寫入 {args.out_dir}/ (pretrain.txt, finetune.txt, charset.txt)")
