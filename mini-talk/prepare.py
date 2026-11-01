"""把 Mini-Lang 語料拆成兩份「知識不同」的語料，給 A、B 兩個模型。

* 兩個模型都學一般句子與文件例句（共同的語言）。
* 人物分成兩組：A 只知道 A 組的人，B 只知道 B 組的人。
* 問答涵蓋所有人：自己知道的人回答事實，不知道的人回答「我不知道」。
  這樣兩個模型都學得會「問任何人」，也知道自己哪些事不知道。
"""
import argparse
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DONT_KNOW = '我不知道'

parser = argparse.ArgumentParser(description='拆分 Mini-Lang 語料給兩個模型')
parser.add_argument('--src', default=os.path.join(HERE, '..', 'mini-lm', 'corpus', 'minilang'))
parser.add_argument('--out', default=os.path.join(HERE, 'corpus'))
args = parser.parse_args()

def read_lines(name):
    with open(os.path.join(args.src, name), encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def write_lines(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

pretrain = read_lines('pretrain.txt')
qa = read_lines('finetune.txt')

# 問答格式 <Q>名字…，名字都是兩個字
names = list(dict.fromkeys(line[len('<Q>'):len('<Q>') + 2] for line in qa))
groups = {'A': names[0::2], 'B': names[1::2]}

def subject(line):
    for n in names:
        if line.startswith(n):
            return n
    return None

os.makedirs(args.out, exist_ok=True)
write_lines(os.path.join(args.out, 'truth.txt'), qa)  # 全部的正確答案，評估用
for agent, own in groups.items():
    d = os.path.join(args.out, agent)
    os.makedirs(d, exist_ok=True)
    # 以人名開頭的句子是人物事實：只留自己這組的人
    write_lines(os.path.join(d, 'pretrain.txt'),
                [l for l in pretrain if subject(l) is None or subject(l) in own])
    write_lines(os.path.join(d, 'finetune.txt'),
                [l if subject(l[len('<Q>'):]) in own else l.split('<A>')[0] + '<A>' + DONT_KNOW
                 for l in qa])
    shutil.copy(os.path.join(args.src, 'charset.txt'), os.path.join(d, 'charset.txt'))
    print(f"{agent} 知道的人: {'、'.join(own)}")

print(f"✅ 已寫入 {args.out}/A、{args.out}/B 與 truth.txt")
