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
parser.add_argument('--n_people', type=int, default=16, help='人物數量（最多 256）')
parser.add_argument('--fact_variants', type=int, default=2, help='每個事實的說法數（2–4）')
parser.add_argument('--bios_per_person', type=int, default=0, help='每人幾段小傳（事實打亂順序寫成一段）')
parser.add_argument('--question_variants', type=int, default=1, help='每種問題的問法數（1–3）')
parser.add_argument('--holdout', type=float, default=0.0,
                    help='保留不微調的事實比例；大於 0 時另外輸出 test_*.txt')
parser.add_argument('--holdout_phrase', action='store_true',
                    help='最後一種問法完全不微調，只用來測試換句話問')
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
# 前 16 個是原本的名字；人數更多時，再用兩個字組成名字
NAME_CHARS = '明山花文天月雨心東南白紅新樂真方'
NAMES = [a + b for a in '小大' for b in NAME_CHARS[:8]]
NAMES += [a + b for a in NAME_CHARS for b in NAME_CHARS if a != b]
if args.n_people > len(NAMES):
    sys.exit(f'--n_people 最多 {len(NAMES)}')
NAMES = NAMES[:args.n_people]
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

ATTRS = ['age', 'job', 'home', 'food', 'drink', 'friend', 'kids']

def person_facts(p, n_variants=2):
    """同一個事實用多種說法，讓模型學到意思而不是背一個句型。
    回傳 {屬性: [說法…]}，前兩種說法和最早的版本相同。"""
    n, k = p['name'], count(p['kids'])
    facts = {
        'age': [f"{n}今年{num(p['age'])}歲。", f"{n}{num(p['age'])}歲了。",
                f"{n}是一個{num(p['age'])}歲的人。", f"今年{n}{num(p['age'])}歲。"],
        'job': [f"{n}是{p['job']}。", f"{n}{JOBS[p['job']]}。",
                f"大家都知道{n}是{p['job']}。", f"{n}是一個{p['job']}。"],
        'home': [f"{n}的家在{p['home']}。", f"{n}住在{p['home']}。",
                 f"{n}住在{p['home']}的一個房子裡。", f"{p['home']}有{n}的家。"],
        'food': [f"{n}喜歡吃{p['food']}。", f"{n}最喜歡吃{p['food']}。",
                 f"{n}很愛吃{p['food']}。", f"{p['food']}是{n}最喜歡吃的東西。"],
        'drink': [f"{n}喜歡喝{p['drink']}。", f"{n}每天都喝{p['drink']}。",
                  f"{n}很愛喝{p['drink']}。", f"{p['drink']}是{n}最喜歡喝的東西。"],
        'friend': [f"{n}的朋友是{p['friend']}。", f"{n}和{p['friend']}是朋友。",
                   f"{n}有一個朋友叫{p['friend']}。", f"{p['friend']}是{n}的朋友。"],
        'kids': ([f"{n}有{k}孩子。", f"{n}的家裡有{k}孩子。",
                  f"{n}有{k}孩子，都很可愛。", f"{n}家裡有{k}孩子。"] if p['kids'] else
                 [f"{n}沒有孩子。", f"{n}的家裡沒有孩子。", f"{n}還沒有孩子。", f"{n}家裡沒有孩子。"]),
    }
    return {a: v[:n_variants] for a, v in facts.items()}

# 每種問題的問法；第 0 種是最早的版本，最後一種可以保留不微調（--holdout_phrase）
QUESTIONS = {
    'age': ['{n}幾歲？', '{n}今年幾歲？', '{n}多大了？'],
    'job': ['{n}是做什麼的？', '{n}做什麼工作？', '{n}的工作是什麼？'],
    'home': ['{n}的家在哪裡？', '{n}住在哪裡？', '{n}住在哪邊？'],
    'food': ['{n}喜歡吃什麼？', '{n}最喜歡吃什麼？', '{n}愛吃什麼？'],
    'drink': ['{n}喜歡喝什麼？', '{n}每天都喝什麼？', '{n}愛喝什麼？'],
    'friend': ['{n}的朋友是誰？', '{n}和誰是朋友？', '誰是{n}的朋友？'],
    'kids': ['{n}有幾個孩子？', '{n}的家裡有幾個孩子？', '{n}的孩子有幾個？'],
}

def answer_of(p, attr):
    return {'age': f"{num(p['age'])}歲", 'job': p['job'], 'home': p['home'], 'food': p['food'],
            'drink': p['drink'], 'friend': p['friend'],
            'kids': count(p['kids']) if p['kids'] else '沒有'}[attr]

def person_qa(p, variant=0):
    return [(QUESTIONS[a][variant].format(n=p['name']), answer_of(p, a)) for a in ATTRS]

def person_bio(p, n_variants, bio_rng):
    """一段小傳：每個屬性挑一種說法，順序打亂（Allen-Zhu & Li 的 multi + permute 擴增）。"""
    facts = person_facts(p, n_variants)
    parts = [bio_rng.choice(facts[a]) for a in ATTRS]
    bio_rng.shuffle(parts)
    return ''.join(parts)

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

facts = [f for p in people for v in person_facts(p, args.fact_variants).values() for f in v]
bio_rng = random.Random(args.seed + 1)  # 獨立的亂數，不影響人物與一般句子
bios = [person_bio(p, args.fact_variants, bio_rng) for p in people for _ in range(args.bios_per_person)]
general = list(dict.fromkeys(sentence() for _ in range(args.n_sentences * 3)))[:args.n_sentences]
examples = doc_sentences()
pretrain = list(dict.fromkeys(facts + bios + general + examples))

def qa_lines(pairs):
    return [f"<Q>{q}<A>{a}" for q, a in pairs]

tests = {}
if args.holdout > 0:
    # 用和 finetune.py 相同的方式切分（第 0 種問法、相同種子），保留的事實和舊實驗一致
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data import split_holdout
    keys = [(i, a) for i, p in enumerate(people) for a in ATTRS]
    canonical = [(QUESTIONS[a][0].format(n=people[i]['name']), answer_of(people[i], a)) for i, a in keys]
    _, held = split_holdout(canonical, args.holdout, args.seed)
    held = set(held)
    held_keys = {k for k, c in zip(keys, canonical) if c in held}
    train_keys = [k for k in keys if k not in held_keys]
    test_keys = [k for k in keys if k in held_keys]
    n_train_variants = args.question_variants - (1 if args.holdout_phrase else 0)
    last = args.question_variants - 1

    def pairs_of(ks, variants):
        return [(QUESTIONS[a][v].format(n=people[i]['name']), answer_of(people[i], a)) for i, a in ks for v in variants]

    qa = qa_lines(pairs_of(train_keys, range(n_train_variants)))
    tests['test_fact.txt'] = qa_lines(pairs_of(test_keys, [0]))          # 新事實、原本的問法
    if args.holdout_phrase:
        tests['test_phrase.txt'] = qa_lines(pairs_of(train_keys, [last]))  # 練過的事實、新問法
        tests['test_both.txt'] = qa_lines(pairs_of(test_keys, [last]))     # 新事實、新問法
else:
    qa = qa_lines([pair for p in people for v in range(args.question_variants) for pair in person_qa(p, v)])

all_qa = qa + [l for t in tests.values() for l in t]
bad = unknown(''.join(pretrain + [q.replace('<Q>', '').replace('<A>', '') for q in all_qa]), charset)
if bad:
    sys.exit(f"❌ 產生的語料用了字表外的字: {''.join(bad)}")

os.makedirs(args.out_dir, exist_ok=True)
with open(os.path.join(args.out_dir, 'pretrain.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(pretrain) + '\n')
with open(os.path.join(args.out_dir, 'finetune.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(qa) + '\n')
for name, lines in tests.items():
    with open(os.path.join(args.out_dir, name), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
# 完整的 256 字（加上標點）放進詞表，讓詞表大小固定，不隨語料改變
punct = sorted({c for c in ''.join(pretrain + all_qa) if c not in charset and not c.isascii()})
with open(os.path.join(args.out_dir, 'charset.txt'), 'w', encoding='utf-8') as f:
    f.write(''.join(sorted(charset)) + ''.join(punct) + '\n')

print(f"✅ 人物 {len(people)} 位，事實 {len(facts)} 句，小傳 {len(bios)} 段，一般句子 {len(general)} 句，"
      f"文件例句 {len(examples)} 句，問答 {len(qa)} 組"
      + ''.join(f"，{n} {len(t)} 組" for n, t in tests.items()))
print(f"   已寫入 {args.out_dir}/ (pretrain.txt, finetune.txt, charset.txt)")
