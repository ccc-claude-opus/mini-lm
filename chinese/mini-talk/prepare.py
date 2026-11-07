"""產生最佳模型（best-model.md 的設定 D）的語料，拆成兩份「知識不同」的語料給 A、B。

* 人物資料和 D 相同：256 人、每個事實 4 種說法、每人 2 段打亂順序的小傳、每種問題 2 種問法。
* 兩個模型都學一般句子、文件例句（共同的語言）；run.sh 另外混入手寫句子與 13 個方向的語句。
* 人物分成兩組：A 只知道 A 組的人，B 只知道 B 組的人。
* 問答涵蓋所有人：自己知道的人回答事實，不知道的人回答「我不知道」。
  這樣兩個模型都學得會「問任何人」，也知道自己哪些事不知道。

事實句可能同時提到兩個人（「小花是小明的朋友」），所以用 gen_minilang.py --owners
輸出的 owners.txt 判斷每句話是誰的事實，而不是比對人名。
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LM = os.path.join(HERE, '..', 'mini-lm')
DONT_KNOW = '我不知道'

parser = argparse.ArgumentParser(description='產生 Mini-Lang 語料並拆給兩個模型')
parser.add_argument('--out', default=os.path.join(HERE, 'corpus'))
parser.add_argument('--n_people', type=int, default=256)
parser.add_argument('--n_sentences', type=int, default=24000)
parser.add_argument('--fact_variants', type=int, default=4)
parser.add_argument('--bios_per_person', type=int, default=2)
parser.add_argument('--question_variants', type=int, default=2)
args = parser.parse_args()

full = os.path.join(args.out, 'full')
subprocess.run([sys.executable, os.path.join(LM, 'gen_minilang.py'), '--out_dir', full, '--owners',
                '--n_people', str(args.n_people), '--n_sentences', str(args.n_sentences),
                '--fact_variants', str(args.fact_variants), '--bios_per_person', str(args.bios_per_person),
                '--question_variants', str(args.question_variants)], check=True)

def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f if line.strip()]

def write_lines(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

pretrain = read_lines(os.path.join(full, 'pretrain.txt'))
qa = read_lines(os.path.join(full, 'finetune.txt'))
owner = dict(reversed(line.split('\t', 1)) for line in read_lines(os.path.join(full, 'owners.txt')))

names = list(dict.fromkeys(owner[l] for l in qa))
groups = {'A': set(names[0::2]), 'B': set(names[1::2])}

write_lines(os.path.join(args.out, 'truth.txt'), qa)  # 全部的正確答案，評估用
for agent, own in groups.items():
    d = os.path.join(args.out, agent)
    os.makedirs(d, exist_ok=True)
    # 人物事實與小傳只留自己這組的人；一般句子兩邊都有
    write_lines(os.path.join(d, 'pretrain.txt'), [l for l in pretrain if l not in owner or owner[l] in own])
    write_lines(os.path.join(d, 'finetune.txt'),
                [l if owner[l] in own else l.split('<A>')[0] + '<A>' + DONT_KNOW for l in qa])
    shutil.copy(os.path.join(full, 'charset.txt'), os.path.join(d, 'charset.txt'))
    print(f"{agent} 知道 {len(own)} 人: {'、'.join(n for n in names if n in own)[:60]}…")
shutil.rmtree(full)

print(f"✅ 已寫入 {args.out}/A、{args.out}/B 與 truth.txt")
