"""Mini-Lang 專家的本機伺服器：提供 mini-lang-expert.html，並代為呼叫 NVIDIA 的 GLM 5.3 Flash。

金鑰從環境變數 NVIDIA_API_KEY 讀取，只留在這個伺服器裡，不會送到瀏覽器。
只聽本機（127.0.0.1），不對外開放。

用法：
    python web/expert_server.py            # 再打開 http://localhost:8766/mini-lang-expert.html
    python web/expert_server.py --port 9000
"""
import argparse
import csv
import glob
import json
import os
import sys
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).resolve().parent
PROMPTS = WEB.parent / 'mini-lang' / 'prompts'
LEXICON = WEB.parent / 'mini-lang' / 'lexicon'
API_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
MODEL = 'z-ai/glm-5.3-flash'
REASONING_EFFORT = 'low'
MAX_TOKENS = 8192
MAX_BODY = 200_000  # 一次對話最多約 20 萬字元
MAX_TOOL_ROUNDS = 5  # 一次回答最多呼叫幾次工具（檢查、查詞典）
MAX_RELEVANT = 120   # 系統提示詞最多附上幾條「對話中出現的詞」

sys.path.insert(0, str(WEB.parent / 'mini-lang'))
from check import DOC, load_charset, unknown  # noqa: E402



def charset():
    # 每次都重新讀字表，改了 mini-lang.md 不用重開伺服器
    return set(load_charset(DOC.read_text(encoding='utf-8')))

# 給模型用的工具：檢查 Mini-Lang 的文字，和 check.py 相同
TOOLS = [{
    'type': 'function',
    'function': {
        'name': 'check_minilang',
        'description': '檢查一段 Mini-Lang 文字是否只用 297 字字表內的漢字（數字、標點、英文外來語不算）。'
                       '回傳是否通過、字表外的字出現在哪裡，以及詞典中相關的換法。輸出任何 Mini-Lang 之前都要先用它檢查。',
        'parameters': {
            'type': 'object',
            'properties': {'text': {'type': 'string', 'description': '要檢查的 Mini-Lang 文字（不含 minilang 區塊的標記）'}},
            'required': ['text'],
        },
    },
}, {
    'type': 'function',
    'function': {
        'name': 'lookup_word',
        'description': '查 Mini-Lang 詞典：一般中文的詞在 Mini-Lang 怎麼說。可以一次查好幾個詞。'
                       '回傳每個詞是否已經在字表內（可以直接寫），或詞典的標準說法（外來語會附上第一次出現時的說明）。'
                       '寫作或翻譯時，想用字表外的詞就先查。',
        'parameters': {
            'type': 'object',
            'properties': {'words': {'type': 'array', 'items': {'type': 'string'}, 'description': '要查的一般中文詞，例如 ["比賽", "球員"]'}},
            'required': ['words'],
        },
    },
}]


def section(path):
    """提示詞檔案中兩條「---」之間的內容。"""
    return path.read_text(encoding='utf-8').split('\n---\n')[1].strip()


def entry_line(r):
    """詞典的一行：一般中文 → Mini-Lang（外來語附上第一次出現時的說明）。"""
    note = f"（{r['說明']}）" if r['說明'] else ''
    return f"{r['中文']} → {r['Mini-Lang']}{note}"


def relevant_lexicon(messages):
    """只附上對話中出現的詞（使用者的訊息）。整份詞典約 1.5 萬字，大部分用不到；其他詞讓模型用 lookup_word 查。"""
    text = '\n'.join(m['content'] for m in messages if m['role'] == 'user')
    hits = [r for r in lexicon_rows() if r['中文'] != r['Mini-Lang'] and r['中文'] in text]
    hits.sort(key=lambda r: -len(r['中文']))  # 長的詞優先（例如「沒關係」比「關係」重要）
    if not hits:
        return '## 相關詞典\n\n（使用者的訊息裡沒有詞典登記的詞。寫作時想用字表外的詞，用 lookup_word 查。）'
    return ('## 相關詞典（使用者的訊息中出現的詞；其他詞用 lookup_word 查）\n\n'
            + '\n'.join(entry_line(r) for r in hits[:MAX_RELEVANT]))


def lexicon_rows():
    rows = []
    for path in sorted(glob.glob(str(LEXICON / '*.tsv'))):
        with open(path, encoding='utf-8') as f:
            rows.extend(csv.DictReader(f, delimiter='\t'))
    return rows


def check_minilang(text):
    """檢查工具：回傳 {ok, out_of_set: [{char, where}], suggestions: [{word, mini_lang}]}。"""
    bad = unknown(text, charset())
    if not bad:
        return {'ok': True, 'message': '全部只用字表內的字，可以輸出。'}
    out = []
    for c in bad:
        where = []
        for k, ch in enumerate(text):
            if ch == c and len(where) < 3:
                where.append(text[max(0, k - 6):k + 7])
        out.append({'char': c, 'where': where})
    # 詞典裡含有這些字、而且出現在文字中的詞，附上標準換法
    suggestions = []
    for r in lexicon_rows():
        if r['中文'] != r['Mini-Lang'] and r['中文'] in text and any(c in r['中文'] for c in bad):
            suggestions.append({'word': r['中文'], 'mini_lang': r['Mini-Lang']})
    return {'ok': False, 'out_of_set': out, 'suggestions': suggestions[:20],
            'message': '請只改寫含有這些字的句子，改完再檢查一次。'}


def lookup_word(words):
    """查詞典工具：回傳每個詞在 Mini-Lang 怎麼說。"""
    cs = charset()
    rows = lexicon_rows()
    out = []
    for w in [str(w).strip() for w in words if str(w).strip()][:20]:
        if not unknown(w, cs):
            out.append({'word': w, 'in_charset': True, 'mini_lang': w, 'message': '字表內就有，直接寫'})
            continue
        exact = [r for r in rows if r['中文'] == w]
        if exact:
            r = exact[0]
            out.append({'word': w, 'mini_lang': r['Mini-Lang'], 'note': r['說明'], 'method': r['方式']})
            continue
        # 沒有完全相同的：找含有這個詞、或被這個詞包含的詞條
        near = [r for r in rows if r['中文'] != r['Mini-Lang'] and (w in r['中文'] or r['中文'] in w)][:5]
        out.append({'word': w, 'found': False,
                    'similar': [{'word': r['中文'], 'mini_lang': r['Mini-Lang']} for r in near],
                    'message': '詞典沒有這個詞；請依系統提示詞第 3 節，用描述或外來語說出來'})
    return {'results': out}


def system_prompt(messages):
    # 每次對話重新讀檔，改了提示詞或詞典不用重開伺服器
    return '\n\n'.join([section(PROMPTS / 'system.md'), section(PROMPTS / 'expert.md'), relevant_lexicon(messages)])


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write('%s\n' % (fmt % args))

    def do_GET(self):
        if self.path in ('/', '/index'):
            self.send_response(302)
            self.send_header('Location', '/mini-lang-expert.html')
            self.end_headers()
            return
        if self.path == '/api/status':
            return self.send_json({'model': MODEL, 'reasoning_effort': REASONING_EFFORT,
                                   'key': bool(os.environ.get('NVIDIA_API_KEY'))})
        super().do_GET()

    def do_POST(self):
        if self.path != '/api/chat':
            return self.send_error(404)
        length = int(self.headers.get('Content-Length', 0))
        if length > MAX_BODY:
            return self.send_error(413, '對話太長了，請開新的對話')
        try:
            messages = json.loads(self.rfile.read(length))['messages']
            messages = [{'role': m['role'], 'content': str(m['content'])}
                        for m in messages if m.get('role') in ('user', 'assistant')]
        except (ValueError, KeyError, TypeError):
            return self.send_error(400, '格式不對')
        key = os.environ.get('NVIDIA_API_KEY')
        if not key:
            return self.send_json({'error': '伺服器找不到環境變數 NVIDIA_API_KEY'}, 500)

        convo = [{'role': 'system', 'content': system_prompt(messages)}] + messages

        # 給網頁的串流：每行一個 JSON，type 是 reasoning、content、tool、error 或 done
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        try:
            for _ in range(MAX_TOOL_ROUNDS + 1):
                calls = self.stream_round(key, convo, tools=True)
                if not calls:
                    break
                # 模型要檢查：在本機執行，把結果交回給模型，再讓它繼續
                convo.append({'role': 'assistant', 'content': '', 'tool_calls': calls})
                for call in calls:
                    try:
                        args = json.loads(call['function']['arguments'] or '{}')
                    except ValueError:
                        args = {}
                    if call['function']['name'] == 'lookup_word':
                        words = args.get('words') or []
                        result = lookup_word(words if isinstance(words, list) else [words])
                        self.send_event({'type': 'lookup', 'words': [x['word'] for x in result['results']]})
                    else:
                        result = check_minilang(args.get('text', ''))
                        self.send_event({'type': 'tool', 'ok': result['ok'],
                                         'chars': [x['char'] for x in result.get('out_of_set', [])]})
                    convo.append({'role': 'tool', 'tool_call_id': call['id'],
                                  'content': json.dumps(result, ensure_ascii=False)})
            else:
                # 工具次數用完了還沒寫出答案：不給工具，請它直接寫出最後的答案
                self.stream_round(key, convo, tools=False)
            self.send_event({'type': 'done'})
        except urllib.error.HTTPError as e:
            self.send_event({'type': 'error', 'text': f'NVIDIA API 錯誤 {e.code}：{e.read().decode("utf-8", "replace")[:300]}'})
        except (urllib.error.URLError, TimeoutError) as e:
            self.send_event({'type': 'error', 'text': f'連不上 NVIDIA API：{e}'})
        except (BrokenPipeError, ConnectionResetError):
            pass  # 使用者關掉頁面或按了停止

    def stream_round(self, key, convo, tools):
        """呼叫模型一次，把思考與回答轉送給網頁；回傳模型要呼叫的工具（沒有就是空的）。"""
        body = {
            'model': MODEL,
            'messages': convo,
            'stream': True,
            'max_tokens': MAX_TOKENS,
            'temperature': 0.6,
            'reasoning_effort': REASONING_EFFORT,
        }
        if tools:
            body['tools'] = TOOLS
        req = urllib.request.Request(API_URL, data=json.dumps(body).encode(), headers={
            'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Accept': 'text/event-stream'})
        calls = {}
        with urllib.request.urlopen(req, timeout=300) as resp:
            for raw in resp:
                line = raw.decode('utf-8').strip()
                if not line.startswith('data:'):
                    continue
                data = line[5:].strip()
                if data == '[DONE]':
                    break
                chunk = json.loads(data)
                if not chunk.get('choices'):
                    continue
                delta = chunk['choices'][0].get('delta', {})
                for field, kind in (('reasoning_content', 'reasoning'), ('reasoning', 'reasoning'), ('content', 'content')):
                    if delta.get(field):
                        self.send_event({'type': kind, 'text': delta[field]})
                # 工具呼叫是分段送來的，依 index 拼起來
                for tc in delta.get('tool_calls') or []:
                    c = calls.setdefault(tc.get('index', 0), {'id': '', 'type': 'function',
                                                              'function': {'name': '', 'arguments': ''}})
                    c['id'] = tc.get('id') or c['id']
                    fn = tc.get('function') or {}
                    c['function']['name'] += fn.get('name') or ''
                    c['function']['arguments'] += fn.get('arguments') or ''
        return [calls[k] for k in sorted(calls)]

    def send_event(self, obj):
        self.wfile.write(f'data: {json.dumps(obj, ensure_ascii=False)}\n\n'.encode('utf-8'))
        self.wfile.flush()

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    p = argparse.ArgumentParser(description='Mini-Lang 專家的本機伺服器')
    p.add_argument('--port', type=int, default=8766)
    args = p.parse_args()
    if not os.environ.get('NVIDIA_API_KEY'):
        print('⚠️  找不到環境變數 NVIDIA_API_KEY，請先 export NVIDIA_API_KEY=...', file=sys.stderr)
    prompt = system_prompt([])
    print(f'系統提示詞 {len(prompt)} 字元（詞典改成只附對話中出現的詞，其他用 lookup_word 查）；模型 {MODEL}，reasoning effort {REASONING_EFFORT}')
    print(f'打開 http://localhost:{args.port}/mini-lang-expert.html')
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
