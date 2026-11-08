#!/usr/bin/env python3
"""提示詞效果測試：用 prompts/system.md 讓 LLM 改寫英文，看**一次**寫對的比例。

和「手寫改寫測試」不同，這裡測的是提示詞好不好用：
模型只看系統提示詞（沒有工具、沒有檢查迴圈），第一次輸出就檢查。

用法：
    export NVIDIA_API_KEY=...
    python tools/prompt_test.py                # 測預設的 3 段
    python tools/prompt_test.py --passages 5   # 測前 5 段
    python tools/prompt_test.py --show         # 把模型的輸出全部印出來
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import check as checker  # noqa: E402

API_URL = os.environ.get('MINI_ENGLISH_API_URL') or \
    'https://integrate.api.nvidia.com/v1/chat/completions'
API_KEY = os.environ.get('NVIDIA_API_KEY') or os.environ.get('OPENAI_API_KEY') or ''
MODEL = os.environ.get('MINI_ENGLISH_MODEL', 'z-ai/glm-5.3-flash')

PASSAGES = [
    ('coffee', 'Coffee is a beverage brewed from roasted, ground coffee beans. Dark-colored and bitter, coffee has a stimulating effect on humans due to its caffeine content; however decaffeinated coffee is also commercially available.'),
    ('bicycle', 'A bicycle, also called a pedal cycle, bike, push-bike or cycle, is a human-powered or motor-assisted, pedal-driven, single-track vehicle, with two wheels attached to a frame, one behind the other. A bicycle rider is called a cyclist or bicyclist.'),
    ('dog', 'A Dog was lying in a Manger on the hay which had been put there for the cattle, and when they came and tried to eat, he growled and snapped at them and would not let them get at their food. "What a selfish beast," said one of them to his companions; "he cannot eat himself and yet he will not let those eat who can."'),
]

ASK = ('請把下面的文章改寫成 Mini-English。意思要完全一樣。\n'
       '只輸出改寫後的 Mini-English，放在 ```en 和 ``` 之間。\n\n')


def system_prompt():
    text = (ROOT / 'prompts' / 'system.md').read_text(encoding='utf-8')
    if '---' in text:
        text = text.split('---')[1]
    return text.strip()


def call(messages, tools=None):
    body = {
        'model': MODEL,
        'messages': messages,
        'max_tokens': 2048,
        'temperature': 0.2,
    }
    if tools:
        body['tools'] = tools
        body['tool_choice'] = 'auto'
    if 'nvidia' in API_URL:
        body['reasoning_effort'] = 'low'
    req = urllib.request.Request(API_URL, data=json.dumps(body).encode('utf-8'), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    })
    with urllib.request.urlopen(req, timeout=240) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data['choices'][0]['message']


TOOLS = [{
    'type': 'function',
    'function': {
        'name': 'check_minienglish',
        'description': '檢查一段 Mini-English 文字是否只用詞表內的詞。回傳是否通過與違規的詞。',
        'parameters': {
            'type': 'object',
            'properties': {'text': {'type': 'string', 'description': '要檢查的 Mini-English 文字'}},
            'required': ['text'],
        },
    },
}]


def call_with_tool(passage, max_rounds=4):
    """模型自己呼叫檢查工具 → 拿違規詞回頭改 → 再檢查。

    模型的稿子放在工具的引數裡（tool_calls[0].arguments.text），
    有些回合也會同時放在 content 裡；哪裡有就用哪裡。
    """
    sp = checker.Spec((ROOT / 'mini-english.md').read_text(encoding='utf-8'))
    convo = [{'role': 'system', 'content': system_prompt()},
             {'role': 'user', 'content': ASK + passage}]
    answer = ''
    rounds = 0
    for _ in range(max_rounds):
        msg = call(convo, tools=TOOLS)
        rounds += 1
        calls = msg.get('tool_calls') or []
        draft = msg.get('content') or ''
        for c in calls:
            try:
                draft = json.loads(c['function']['arguments'] or '{}').get('text', '') or draft
            except Exception:  # noqa: BLE001
                pass
        if draft.strip():
            answer = draft
        if not calls:
            break
        convo.append({'role': 'assistant', 'content': msg.get('content') or '',
                      'tool_calls': calls})
        for c in calls:
            args_ = json.loads(c['function']['arguments'] or '{}')
            errors, _ = checker.check_text(args_.get('text', ''), sp)
            result = {'ok': not errors,
                      'errors': [{'word': tok, 'kind': kind, 'message': m}
                                 for kind, m, tok in errors]}
            convo.append({'role': 'tool', 'tool_call_id': c['id'],
                          'content': json.dumps(result, ensure_ascii=False)})
    return answer, rounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--passages', type=int, default=len(PASSAGES))
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--tool', action='store_true', help='讓模型自己用檢查工具（最多 3 輪）')
    args = ap.parse_args()
    if not API_KEY:
        sys.exit('請先 export NVIDIA_API_KEY=...')

    spec = checker.Spec((ROOT / 'mini-english.md').read_text(encoding='utf-8'))
    ok = 0
    rows = []
    for pid, passage in PASSAGES[:args.passages]:
        t0 = time.time()
        try:
            if args.tool:
                out, rounds = call_with_tool(passage)
            else:
                out = call([{'role': 'system', 'content': system_prompt()},
                            {'role': 'user', 'content': ASK + passage}]).get('content') or ''
        except urllib.error.HTTPError as e:
            print(f'❌ {pid}：API 回應 {e.code} {e.read().decode("utf-8", "ignore")[:200]}')
            continue
        dt = time.time() - t0
        m = re.search(r'```en\n(.*?)```', out, re.S)
        mini = (m.group(1) if m else out).strip()
        errors, _ = checker.check_text(mini, spec)
        if not errors:
            ok += 1
        bad = {}
        for kind, msg, tok in errors:
            bad[tok] = bad.get(tok, 0) + 1
        rows.append((pid, len(mini.split()), len(errors), round(dt), bad))
        print(f"{'✅' if not errors else '❌'} {pid}：{len(mini.split())} 詞，{len(errors)} 個問題，{round(dt)} 秒")
        if errors:
            print('   ' + '、'.join(f'{k}({v})' for k, v in sorted(bad.items(), key=lambda x: -x[1])[:12]))
        if args.show:
            print('--- 模型輸出 ---')
            print(mini)
            print('----------------')
    print()
    print(f'一次寫對：{ok}/{len(rows)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
