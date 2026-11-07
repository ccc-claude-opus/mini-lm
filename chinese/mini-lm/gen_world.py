"""產生「世界知識」問答語料：比人物資料更寬廣的事實與問法，用來測試泛化。

gen_minilang.py 的問答只問人物的 7 種屬性；這裡的事實分成 4 個領域，比較接近 GLM 語料的內容：
  家人   爸爸、媽媽、太太、先生、哥哥、姐姐、弟弟、妹妹、有幾個孩子（用關係詞指稱人）
  動物   是什麼動物、什麼色、幾歲、是誰家的（主人是家人領域的人）
  店     賣什麼、在哪個城、幾點開門
  城     在國的哪邊、在山邊／海邊／河邊、有幾個學校
名字都是 5 個字母以內的英文（universal.md：人名、地名是外來語），和 gen_minilang.py 的人名不重複。

和 gen_minilang.py 一樣：預訓練學事實（每個事實 3 種說法＋每個人或東西 1 段打亂順序的介紹），
微調學問答；每種問題有 3 種問法，最後一種保留不微調。輸出：
  pretrain.txt  finetune.txt  charset.txt
  test_fact.txt    微調沒練過的事實，用練過的問法問
  test_phrase.txt  練過的事實，用沒練過的問法問
  test_both.txt    沒練過的事實＋沒練過的問法
  （每一行前面加上領域，例如 test_both.txt 的「家人\t<Q>…<A>…」，評估時可以分領域計算）

用法：python gen_world.py --out_dir runs/glm/world
"""
import argparse
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mini-lang'))
from check import DOC, load_charset, unknown  # noqa: E402
from names import EN_NAMES, spaced  # noqa: E402

parser = argparse.ArgumentParser(description='產生世界知識問答語料')
parser.add_argument('--out_dir', default=os.path.join(HERE, 'corpus', 'world'))
parser.add_argument('--families', type=int, default=40)
parser.add_argument('--pets', type=int, default=60)
parser.add_argument('--shops', type=int, default=60)
parser.add_argument('--towns', type=int, default=30)
parser.add_argument('--holdout', type=float, default=0.2, help='保留不微調的事實比例')
parser.add_argument('--seed', type=int, default=7)
args = parser.parse_args()
rng = random.Random(args.seed)


# ==========================================
# 1. 名字：英文、5 個字母以內，和 gen_minilang.py 的人名不重複
# ==========================================
def make_names(n, taken):
    """用常見的英文音節拼出名字，例如 Kalo、Mirun。"""
    onsets = 'b d f g h j k l m n p r s t v w z br dr fr gr kr pr tr st'.split()
    vowels = 'a e i o u'.split()
    codas = ['', '', 'n', 'l', 'r', 's', 'm']
    names = []
    while len(names) < n:
        name = (rng.choice(onsets) + rng.choice(vowels) + rng.choice(onsets[:16]) + rng.choice(vowels)
                + rng.choice(codas)).capitalize()
        if len(name) <= 5 and name not in taken:
            taken.add(name)
            names.append(name)
    return names


taken = set(EN_NAMES)

# ==========================================
# 2. 事實：(領域, 主體, 屬性, 答案, [說法…], [問法…])
# ==========================================
facts = []


def fact(domain, who, attr, answer, statements, questions):
    facts.append(dict(domain=domain, who=who, attr=attr, answer=answer,
                      statements=[spaced(s) for s in statements], questions=[spaced(q) for q in questions]))


# --- 城 ---
towns = make_names(args.towns, taken)
for t in towns:
    side = rng.choice(['東邊', '西邊', '南邊', '北邊'])
    near = rng.choice(['山邊', '海邊', '河邊'])
    k = f'{rng.randint(1, 5)}個'
    fact('城', t, 'side', side,
         [f'{t}在國的{side}。', f'{t}是國{side}的一個城。', f'國的{side}有一個城叫{t}。'],
         [f'{t}在國的哪邊？', f'{t}這個城在國的哪一邊？', f'{t}在哪邊？'])
    fact('城', t, 'near', near,
         [f'{t}在{near}。', f'{t}是{near}的一個城。', f'住在{t}的人每天都可以去{near}玩。'],
         [f'{t}在山邊、海邊還是河邊？', f'{t}是什麼地方的城？', f'住在{t}的人可以去哪裡玩？'])
    fact('城', t, 'schools', k,
         [f'{t}有{k}學校。', f'{t}這個城裡有{k}學校。', f'{t}的學校有{k}。'],
         [f'{t}有幾個學校？', f'{t}的學校有幾個？', f'{t}這個城裡有多少個學校？'])

# --- 店 ---
GOODS = ['水果', '菜', '肉', '茶', '衣服', '書', '紙', '刀', '球', '雞蛋']
for s in make_names(args.shops, taken):
    goods, town, h = rng.choice(GOODS), rng.choice(towns), f'{rng.randint(6, 10)}點'
    fact('店', s, 'goods', goods,
         [f'{s}這個店賣{goods}。', f'{s}店裡賣的是{goods}。', f'要買{goods}，可以去{s}這個店。'],
         [f'{s}這個店賣什麼？', f'{s}店裡賣的是什麼？', f'去{s}這個店可以買到什麼？'])
    fact('店', s, 'town', town,
         [f'{s}這個店在{town}。', f'{s}店開在{town}。', f'{town}有一個店叫{s}。'],
         [f'{s}這個店在哪個城？', f'{s}店開在哪裡？', f'哪個城有{s}這個店？'])
    fact('店', s, 'open', h,
         [f'{s}這個店早上{h}開門。', f'{s}店每天{h}開門。', f'每天早上{h}，{s}這個店就開門了。'],
         [f'{s}這個店幾點開門？', f'{s}店每天幾點開門？', f'{s}這個店早上什麼時候開門？'])

# --- 家人：每家爸爸、媽媽和 1–3 個孩子 ---
people = []
for _ in range(args.families):
    dad, mom = make_names(2, taken)
    kids = [dict(name=n, boy=rng.random() < 0.5, age=rng.randint(3, 30)) for n in make_names(rng.randint(1, 3), taken)]
    while len({k['age'] for k in kids}) < len(kids):   # 年紀不同，才分得出哥哥、弟弟
        for k in kids:
            k['age'] = rng.randint(3, 30)
    people += [dad, mom] + [k['name'] for k in kids]
    fact('家人', dad, 'wife', mom,
         [f'{dad}的太太是{mom}。', f'{mom}是{dad}的太太。', f'{dad}和他的太太{mom}住在一起。'],
         [f'{dad}的太太是誰？', f'誰是{dad}的太太？', f'{dad}的太太叫什麼名字？'])
    fact('家人', mom, 'husband', dad,
         [f'{mom}的先生是{dad}。', f'{dad}是{mom}的先生。', f'{mom}和他的先生{dad}住在一起。'],
         [f'{mom}的先生是誰？', f'誰是{mom}的先生？', f'{mom}的先生叫什麼名字？'])
    k = f'{len(kids)}個'
    for p in (dad, mom):
        fact('家人', p, 'kids', k,
             [f'{p}有{k}孩子。', f'{p}家有{k}孩子。', f'{p}的孩子有{k}。'],
             [f'{p}有幾個孩子？', f'{p}家有幾個孩子？', f'{p}的孩子有幾個？'])
    for kid in kids:
        x = kid['name']
        for rel, parent in (('爸爸', dad), ('媽媽', mom)):
            fact('家人', x, rel, parent,
                 [f'{x}的{rel}是{parent}。', f'{parent}是{x}的{rel}。', f'{x}和他的{rel}{parent}一起去河邊走走。'],
                 [f'{x}的{rel}是誰？', f'誰是{x}的{rel}？', f'{x}的{rel}叫什麼名字？'])
        # 兄弟姐妹：同一種關係只有一個人時才問，答案才唯一
        rels = {}
        for o in kids:
            if o is not kid:
                rel = ('哥哥' if o['boy'] else '姐姐') if o['age'] > kid['age'] else ('弟弟' if o['boy'] else '妹妹')
                rels.setdefault(rel, []).append(o['name'])
        for rel, (w, *more) in rels.items():
            if not more:
                fact('家人', x, rel, w,
                     [f'{x}的{rel}是{w}。', f'{w}是{x}的{rel}。', f'{x}有一個{rel}叫{w}。'],
                     [f'{x}的{rel}是誰？', f'誰是{x}的{rel}？', f'{x}的{rel}叫什麼名字？'])

# --- 動物：主人是家人領域的人 ---
for a in make_names(args.pets, taken):
    kind = rng.choice(['牛', '馬', '豬', '雞', '鳥', '魚'])
    color = rng.choice(['白色', '黑色', '金色', '紅色'])
    age, owner = f'{rng.randint(1, 12)}歲', rng.choice(people)
    fact('動物', a, 'kind', kind,
         [f'{a}是一個{kind}。', f'{a}這個動物是{kind}。', f'大家都知道{a}是{kind}。'],
         [f'{a}是什麼動物？', f'{a}這個動物是什麼？', f'{a}是什麼？'])
    fact('動物', a, 'color', color,
         [f'{a}是{color}的。', f'{a}身上是{color}的。', f'{a}的身體是{color}的。'],
         [f'{a}是什麼色的？', f'{a}身上是什麼色的？', f'{a}的身體是什麼色？'])
    fact('動物', a, 'age', age,
         [f'{a}今年{age}。', f'{a}{age}了。', f'{a}是一個{age}的{kind}。'],
         [f'{a}幾歲？', f'{a}今年幾歲？', f'{a}多大了？'])
    fact('動物', a, 'owner', owner,
         [f'{a}是{owner}家的。', f'{owner}家有一個動物叫{a}。', f'{owner}每天都和{a}一起玩。'],
         [f'{a}是誰家的？', f'誰家有{a}？', f'{a}每天和誰一起玩？'])

# ==========================================
# 3. 預訓練、微調、測試
# ==========================================
pretrain = [s for f in facts for s in f['statements']]
by_who = {}
for f in facts:
    by_who.setdefault(f['who'], []).append(f)
for who, fs in by_who.items():   # 每個人或東西一段介紹：每個事實挑一種說法，順序打亂
    parts = [rng.choice(f['statements']) for f in fs]
    rng.shuffle(parts)
    pretrain.append(''.join(parts))
pretrain = list(dict.fromkeys(pretrain))

order = list(range(len(facts)))
rng.shuffle(order)
held = set(order[:int(len(facts) * args.holdout)])


def qa(f, v):
    return f"<Q>{f['questions'][v]}<A>{f['answer']}"


finetune = [qa(f, v) for i, f in enumerate(facts) if i not in held for v in (0, 1)]
tests = {
    'test_fact.txt': [f"{f['domain']}\t{qa(f, 0)}" for i, f in enumerate(facts) if i in held],
    'test_phrase.txt': [f"{f['domain']}\t{qa(f, 2)}" for i, f in enumerate(facts) if i not in held],
    'test_both.txt': [f"{f['domain']}\t{qa(f, 2)}" for i, f in enumerate(facts) if i in held],
}

charset = set(load_charset(open(DOC, encoding='utf-8').read()))
everything = '\n'.join(pretrain + finetune + [l for t in tests.values() for l in t]).replace('<Q>', '').replace('<A>', '')
bad = unknown(everything, charset)
if bad:
    sys.exit(f"❌ 用了字表外的字: {''.join(bad)}")

os.makedirs(args.out_dir, exist_ok=True)
for name, lines in [('pretrain.txt', pretrain), ('finetune.txt', finetune), *tests.items()]:
    with open(os.path.join(args.out_dir, name), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
with open(os.path.join(args.out_dir, 'charset.txt'), 'w', encoding='utf-8') as f:
    f.write(''.join(sorted(charset)) + '0123456789' + letters + '\n')
count = {d: sum(f['domain'] == d for f in facts) for d in ['家人', '動物', '店', '城']}
print(f"✅ 事實 {len(facts)} 個（{'、'.join(f'{d} {n}' for d, n in count.items())}），預訓練 {len(pretrain)} 句，"
      f"微調 {len(finetune)} 組，" + '，'.join(f'{n} {len(t)} 組' for n, t in tests.items()))
print(f'   已寫入 {args.out_dir}/')
