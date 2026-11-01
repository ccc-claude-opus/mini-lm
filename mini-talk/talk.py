"""讓兩個 Mini-Lang 小語言模型互相交談，並從對話中學習對方的知識。

流程：
1. A、B 輪流發問：發問者自己生成問題，只問「自己回答會說我不知道」的事。
2. 對方用 greedy 解碼回答。
3. 每句話都檢查是否只用到 Mini-Lang 的 256 字，答案也和 truth.txt 對照。
4. （--learn）每個模型拿自己聽到的答案再微調一次，比較學習前後對「對方那組人」的了解。
"""
import argparse
import os
import random
import sys
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mini-lm'))
sys.path.insert(0, os.path.join(HERE, '..', 'mini-lang'))
from model import load_checkpoint, save_checkpoint
from data import load_qa, format_prompt
from chat import answer
from trainer import train_qa
from check import DOC, load_charset, unknown

DONT_KNOW = '我不知道'

parser = argparse.ArgumentParser(description='兩個 Mini-Lang 模型互相交談')
parser.add_argument('--a', default=os.path.join(HERE, 'runs', 'A', 'finetune.pt'))
parser.add_argument('--b', default=os.path.join(HERE, 'runs', 'B', 'finetune.pt'))
parser.add_argument('--corpus', default=os.path.join(HERE, 'corpus'), help='prepare.py 的輸出目錄')
parser.add_argument('--rounds', type=int, default=20, help='每人各問幾題')
parser.add_argument('--temperature', type=float, default=0.7, help='發問時的抽樣溫度')
parser.add_argument('--learn', action='store_true', help='交談後從聽到的答案學習')
parser.add_argument('--learn_iters', type=int, default=200)
parser.add_argument('--lr', type=float, default=1e-4)
parser.add_argument('--out', default=os.path.join(HERE, 'runs', 'talk.md'), help='對話紀錄')
parser.add_argument('--seed', type=int, default=0)
args = parser.parse_args()

random.seed(args.seed)
torch.manual_seed(args.seed)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
charset = set(load_charset(open(DOC, encoding='utf-8').read()))
truth = dict(load_qa([os.path.join(args.corpus, 'truth.txt')]))

class Agent:
    def __init__(self, name, ckpt):
        self.name = name
        self.model, self.config, self.tok = load_checkpoint(ckpt, device)
        self.a_id = self.tok.stoi['<A>']
        self.heard = {}    # 從對方聽來的 問題 → 答案
        self.asked = set()

    def reply(self, question):
        return answer(self.model, self.tok, question, device)

    def ask(self, tries=30):
        """生成一個問題（生成到 <A> 為止）；已經會答或問過的就重新生成。"""
        prompt = torch.tensor([self.tok.encode('<Q>')], dtype=torch.long, device=device)
        for _ in range(tries):
            out = self.model.generate(prompt, 32, temperature=args.temperature, eos_id=self.a_id)
            q = self.tok.decode(out[0, 1:].tolist(), skip_special=True).strip()
            if q.endswith('？') and q not in self.asked and self.reply(q) == DONT_KNOW:
                self.asked.add(q)
                return q
        return None

def knows(agent, questions):
    """agent 能正確回答幾題。"""
    return sum(agent.reply(q) == truth[q] for q in questions)

A, B = Agent('A', args.a), Agent('B', args.b)
log = ['# 對話紀錄', '']
stats = {'utter': 0, 'off': 0, 'answered': 0, 'correct': 0, 'dont_know': 0, 'invalid_q': 0}

def say(who, text):
    bad = unknown(text, charset)
    stats['utter'] += 1
    stats['off'] += bool(bad)
    line = f"{who}：{text}" + (f"　⚠️ 字表外: {''.join(bad)}" if bad else '')
    print(line)
    log.append(line + '  ')
    return line

# ==========================================
# 1. 交談
# ==========================================
print('=' * 50)
for r in range(args.rounds):
    for asker, replier in ((A, B), (B, A)):
        q = asker.ask()
        if q is None:
            say(asker.name, '我沒有問題了。')
            continue
        say(asker.name, q)
        a = replier.reply(q)
        mark = ''
        if q not in truth:
            stats['invalid_q'] += 1
            mark = '（這個問題不在 truth.txt 中）'
        elif a == DONT_KNOW:
            stats['dont_know'] += 1
        else:
            stats['answered'] += 1
            stats['correct'] += a == truth[q]
            mark = '　✅' if a == truth[q] else f'　❌（正解: {truth[q]}）'
        say(replier.name, a + mark if not mark.startswith('（') else a)
        if a != DONT_KNOW:
            asker.heard[q] = a
print('=' * 50)

summary = [
    f"* 共 {stats['utter']} 句話，其中 {stats['off']} 句用了字表外的字",
    f"* 對方回答「我不知道」{stats['dont_know']} 次；不在知識範圍內的問題 {stats['invalid_q']} 個",
    f"* 對方給出答案 {stats['answered']} 次，其中正確 {stats['correct']} 次",
]
print('\n'.join(summary))
log += ['', '## 統計', ''] + summary

# ==========================================
# 2. 從對話中學習
# ==========================================
if args.learn:
    log += ['', '## 從對話中學習', '', '| 模型 | 聽到的答案 | 學習前答對（對方那組人） | 學習後答對 | 其中聽過的題目 |', '|---|---:|---:|---:|---:|']
    for agent in (A, B):
        other = [q for q in truth if agent.reply(q) == DONT_KNOW]
        before = knows(agent, other)
        own_qa = load_qa([os.path.join(args.corpus, agent.name, 'finetune.txt')])
        # 聽到的新知識 + 原本的問答（避免忘記）；聽過的問題不再用「我不知道」當答案
        pairs = list(agent.heard.items()) + [(q, a) for q, a in own_qa if q not in agent.heard]
        print(f"\n{agent.name} 從對話中學習 {len(agent.heard)} 個答案...")
        train_qa(agent.model, agent.tok, pairs, device, args.learn_iters, args.lr, 32,
                 agent.config['seq_len'], train_question=True, tag=f'Learn {agent.name}')
        heard_valid = [q for q in agent.heard if q in other]
        after = knows(agent, other)
        after_heard = knows(agent, heard_valid)
        row = (f"| {agent.name} | {len(agent.heard)} | {before}/{len(other)} | {after}/{len(other)} | "
               f"{after_heard}/{len(heard_valid)} |")
        print(f"{agent.name}：對方那組人的問題，學習前 {before}/{len(other)}，學習後 {after}/{len(other)}"
              f"（聽過的 {after_heard}/{len(heard_valid)}）")
        log.append(row)
        out_dir = os.path.join(HERE, 'runs', agent.name + '_learned')
        os.makedirs(out_dir, exist_ok=True)
        save_checkpoint(os.path.join(out_dir, 'finetune.pt'), agent.model, agent.config, agent.tok)

os.makedirs(os.path.dirname(args.out), exist_ok=True)
with open(args.out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log) + '\n')
print(f"\n對話紀錄已儲存為 {args.out}")
