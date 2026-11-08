"""Mini-English 專家的本機伺服器：提供 expert.html，並代為呼叫 LLM API。

金鑰從環境變數讀取，只留在這個伺服器裡，不會送到瀏覽器。只聽本機（127.0.0.1）。

用法：
    export NVIDIA_API_KEY=...        # 或 OPENAI_API_KEY / OPENAI_BASE_URL
    python web/expert_server.py
    python web/expert_server.py --port 9000

模型預設 z-ai/glm-5.3-flash（NVIDIA），也可以用 --model 換。
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).resolve().parent
ROOT = WEB.parent
sys.path.insert(0, str(ROOT))
import check as checker  # noqa: E402

API_URL = os.environ.get('MINI_ENGLISH_API_URL') or \
    'https://integrate.api.nvidia.com/v1/chat/completions'
API_KEY = os.environ.get('NVIDIA_API_KEY') or os.environ.get('OPENAI_API_KEY') or ''
MODEL = 'z-ai/glm-5.3-flash'
REASONING_EFFORT = 'low'
MAX_TOKENS = 8192
MAX_BODY = 200_000
MAX_TOOL_ROUNDS = 5

TOOLS = [{
    'type': 'function',
    'function': {
        'name': 'check_minienglish',
        'description': '檢查一段 Mini-English 文字是否只用詞表內的詞（數字、標點、外來詞不算）。'
                       '回傳是否通過、違規的詞出現在哪裡，以及違規詞的替代說法。'
                       '輸出任何 Mini-English 之前都要先用它檢查。',
        'parameters': {
            'type': 'object',
            'properties': {'text': {'type': 'string', 'description': '要檢查的 Mini-English 文字'}},
            'required': ['text'],
        },
    },
}, {
    'type': 'function',
    'function': {
        'name': 'lookup_word',
        'description': '查 Mini-English 詞典：表外的英文詞在 Mini-English 怎麼說。'
                       '可以一次查好幾個詞。回傳每個詞的 Mini-English 說法與方式（本詞／描述／外來詞）。'
                       '寫作或翻譯時，想用表外的詞就先查。',
        'parameters': {
            'type': 'object',
            'properties': {'words': {'type': 'array', 'items': {'type': 'string'},
                                     'description': '要查的英文詞，例如 ["hospital", "museum"]'}},
            'required': ['words'],
        },
    },
}]


def spec():
    """每次都重新讀規格，改了 mini-english.md 不用重開伺服器。"""
    return checker.Spec((ROOT / 'mini-english.md').read_text(encoding='utf-8'))


def lexicon_rows():
    """詞典：[(english, mini, way, note)]。"""
    import csv
    rows = []
    with open(ROOT / 'lexicon.tsv', encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            rows.append((r['English'], r['Mini-English'], r['方式'], r['說明']))
    return rows


def check_minienglish(text):
    sp = spec()
    errors, _ = checker.check_text(text, sp)
    if not errors:
        return {'ok': True, 'errors': [], 'message': '全部在詞表內。'}
    hints = []
    repl = sp.replace
    for kind, msg, tok in errors:
        hint = repl.get(tok.lower())
        hints.append({'word': tok, 'kind': kind, 'message': msg,
                      'suggestion': hint or ('用描述或外來詞' if kind == '未知詞' else '')})
    return {'ok': False, 'errors': hints,
            'message': f'{len(errors)} 個問題：' + '、'.join(sorted({h["word"] for h in hints}))}


def lookup_word(words):
    rows = lexicon_rows()
    out = []
    sp = spec()
    for w in words:
        w = w.strip()
        hit = next((r for r in rows if r[0].lower() == w.lower()), None)
        if hit:
            out.append({'word': w, 'mini': hit[1], 'how': hit[2], 'note': hit[3]})
        elif w.lower() in sp.forms:
            out.append({'word': w, 'mini': w, 'how': '本詞', 'note': '已經在詞表內，可以直接用。'})
        else:
            out.append({'word': w, 'mini': '', 'how': '沒有',
                        'note': '詞典裡沒有這個詞：請用描述（10 個詞以內）或當成外來詞並加括號說明。'})
    return {'results': out}


def relevant_lexicon(messages, limit=150):
    """系統提示詞只附上「這次對話中出現的詞」的詞典條目，其餘用 lookup_word 查。"""
    text = ' '.join(str(m.get('content', '')) for m in messages).lower()
    words = set(w for w in __import__('re').findall(r'[A-Za-z]{3,}', text))
    out = []
    for eng, mini, way, note in lexicon_rows():
        if eng.lower() in words:
            out.append(f'{eng} → {mini}（{way}{"，說明：" + note if note else ""}）')
        if len(out) >= limit:
            break
    return out


def system_prompt(messages):
    base = (ROOT / 'prompts' / 'system.md').read_text(encoding='utf-8')
    # system.md 裡的「---」包裝拿掉
    if '---' in base:
        base = base.split('---')[1]
    rel = relevant_lexicon(messages)
    if rel:
        base += '\n\n## 8. 這次對話用得到的詞典條目\n\n' + '\n'.join('- ' + r for r in rel)
    return base.strip()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith('/api/config'):
            return self.send_json({'model': MODEL, 'has_key': bool(API_KEY)})
        return super().do_GET()

    def do_POST(self):
        if not self.path.startswith('/api/chat'):
            return self.send_json({'error': 'not found'}, 404)
        length = int(self.headers.get('Content-Length', 0))
        if length > MAX_BODY:
            return self.send_json({'error': 'too long'}, 413)
        payload = json.loads(self.rfile.read(length).decode('utf-8'))
        messages = payload.get('messages', [])
        self.stream(messages)

    # ── 呼叫 API，把回應以 SSE 串流給瀏覽器 ──
    def stream(self, messages):
        convo = [{'role': 'system', 'content': system_prompt(messages)}] + messages
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

        def event(obj):
            self.wfile.write(f'data: {json.dumps(obj, ensure_ascii=False)}\n\n'.encode('utf-8'))
            self.wfile.flush()

        try:
            for _ in range(MAX_TOOL_ROUNDS):
                text, calls = self.one_round(convo)
                if text:
                    event({'type': 'text', 'text': text})
                if not calls:
                    break
                convo.extend(calls)
                for c in calls:
                    if c.get('function', {}).get('name') == 'check_minienglish':
                        try:
                            result = check_minienglish(json.loads(c['function']['arguments']).get('text', ''))
                        except Exception as e:  # noqa: BLE001
                            result = {'ok': False, 'message': f'檢查失敗：{e}'}
                        event({'type': 'tool', 'name': 'check_minienglish', 'result': result})
                    elif c.get('function', {}).get('name') == 'lookup_word':
                        try:
                            result = lookup_word(json.loads(c['function']['arguments']).get('words', []))
                        except Exception as e:  # noqa: BLE001
                            result = {'results': [], 'message': f'查詢失敗：{e}'}
                        event({'type': 'tool', 'name': 'lookup_word', 'result': result})
        except urllib.error.HTTPError as e:
            event({'type': 'error', 'message': f'API 回應 {e.code}：{e.read().decode("utf-8", "ignore")[:400]}'})
        except Exception as e:  # noqa: BLE001
            event({'type': 'error', 'message': str(e)})
        event({'type': 'done'})

    def one_round(self, convo):
        body = {'model': MODEL, 'messages': convo, 'stream': False,
                'max_tokens': MAX_TOKENS, 'tools': TOOLS, 'tool_choice': 'auto'}
        if 'nvidia' in API_URL:
            body['reasoning_effort'] = REASONING_EFFORT
        req = urllib.request.Request(API_URL, data=json.dumps(body).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}',
        })
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        msg = data['choices'][0]['message']
        calls = []
        for c in msg.get('tool_calls') or []:
            calls.append({'role': 'assistant', 'content': msg.get('content') or '',
                          'tool_calls': [c]})
            calls.append({'role': 'tool', 'tool_call_id': c['id'],
                          'content': json.dumps(self.run_tool(c), ensure_ascii=False)})
        return msg.get('content') or '', calls

    def run_tool(self, call):
        name = call['function']['name']
        args = json.loads(call['function']['arguments'] or '{}')
        if name == 'check_minienglish':
            return check_minienglish(args.get('text', ''))
        if name == 'lookup_word':
            return lookup_word(args.get('words', []))
        return {'error': 'unknown tool'}


def main():
    global MODEL
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8767)
    p.add_argument('--model', default=MODEL)
    args = p.parse_args()
    MODEL = args.model
    if not API_KEY:
        print('⚠️  找不到 API 金鑰：請先 export NVIDIA_API_KEY=...（或 OPENAI_API_KEY）', file=sys.stderr)
    prompt = system_prompt([{'content': 'hello'}])
    print(f'系統提示詞 {len(prompt)} 字元；模型 {MODEL}')
    print(f'打開 http://localhost:{args.port}/expert.html')
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
