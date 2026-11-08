#!/usr/bin/env python3
"""交叉檢查：網頁的 JS 檢查器（web/minienglish.js）和 Python 的 check.py 必須一致。

用法：python web/crosscheck.py
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import check  # noqa: E402

TEXTS = [
    'I am a student and she goes to work by bus.',
    "I don't like it. She's my friend. It's fine.",
    'The children went to the shops and he was running.',
    '2 children and 3 women with many feet.',
    'I have 20 books and 3 pens at 7:30.',
    'The worker was quickly unhappy with the taller man.',
    'Please look for my book and put on your coat.',
    'I went to Paris (a big city in France) last year.',
    'I went to Paris (a big city in France). Paris is nice.',
    'Marie Curie (a woman from Poland) won a prize.',
    '我住在上海 (a big city in China)。',
    'I ate a hamburger.',
    'a lot of books',
    'I went to Paris last year.',
    'Zebras run.',
    'The Zebra runs.',
    'The hospital is big.',
    'This is a test of the checker.',
    'She has 3 pens, 2 books and a lot of time.',
    'The Great Wall of China (a long wall) is old.',
    'A panda (a black and white animal) lives here.',
    'he went to the shops and bought some milk',
]


def js_check(texts):
    script = """
const fs=require('fs'),path=require('path'),vm=require('vm');
const ctx={}; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(DATAJS,'utf8')+';this.DATA=DATA;',ctx);
const ME=require(MEJS).create(ctx.DATA);
const texts=JSON.parse(fs.readFileSync(0,'utf8'));
const out=texts.map(t=>ME.check(t).map(e=>e.type+':'+e.token));
process.stdout.write(JSON.stringify(out));
"""
    script = script.replace('DATAJS', json.dumps(str(HERE / 'data.js')))
    script = script.replace('MEJS', json.dumps(str(HERE / 'minienglish.js')))
    p = subprocess.run(['node', '-e', script], input=json.dumps(TEXTS), capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr)
        sys.exit(1)
    return json.loads(p.stdout)


def main():
    doc = (ROOT / 'mini-english.md').read_text(encoding='utf-8')
    spec = check.Spec(doc)
    py = []
    for t in TEXTS:
        errs, _ = check.check_text(t, spec)
        py.append([f'{k}:{tok}' for k, _, tok in errs])
    js = js_check(TEXTS)
    bad = 0
    for t, a, b in zip(TEXTS, py, js):
        if a != b:
            bad += 1
            print(f'❌ {t[:60]}')
            print(f'   Python：{a}')
            print(f'   JS    ：{b}')
    print(f'比對 {len(TEXTS)} 句：' + ('✅ 兩邊完全一致' if not bad else f'❌ {bad} 句不一致'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
