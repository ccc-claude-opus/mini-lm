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


def section(path):
    """提示詞檔案中兩條「---」之間的內容。"""
    return path.read_text(encoding='utf-8').split('\n---\n')[1].strip()


def lexicon_appendix():
    """整份詞典，一行一個：一般中文 → Mini-Lang（外來語附上第一次出現時的說明）。"""
    lines = []
    for path in sorted(glob.glob(str(LEXICON / '*.tsv'))):
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                if r['中文'] == r['Mini-Lang']:
                    continue  # 本詞不用查
                note = f"（{r['說明']}）" if r['說明'] else ''
                lines.append(f"{r['中文']} → {r['Mini-Lang']}{note}")
    return '## 附錄：詞典（一般中文 → Mini-Lang）\n\n' + '\n'.join(lines)


def system_prompt():
    # 每次對話重新讀檔，改了提示詞或詞典不用重開伺服器
    return '\n\n'.join([section(PROMPTS / 'system.md'), section(PROMPTS / 'expert.md'), lexicon_appendix()])


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

        body = json.dumps({
            'model': MODEL,
            'messages': [{'role': 'system', 'content': system_prompt()}] + messages,
            'stream': True,
            'max_tokens': MAX_TOKENS,
            'temperature': 0.6,
            'reasoning_effort': REASONING_EFFORT,
        }).encode()
        req = urllib.request.Request(API_URL, data=body, headers={
            'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Accept': 'text/event-stream'})

        # 把模型的串流轉成給網頁的串流：每行一個 JSON，type 是 reasoning、content、error 或 done
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        try:
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
            self.send_event({'type': 'done'})
        except urllib.error.HTTPError as e:
            self.send_event({'type': 'error', 'text': f'NVIDIA API 錯誤 {e.code}：{e.read().decode("utf-8", "replace")[:300]}'})
        except (urllib.error.URLError, TimeoutError) as e:
            self.send_event({'type': 'error', 'text': f'連不上 NVIDIA API：{e}'})
        except (BrokenPipeError, ConnectionResetError):
            pass  # 使用者關掉頁面或按了停止

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
    prompt = system_prompt()
    print(f'系統提示詞 {len(prompt)} 字元（含詞典）；模型 {MODEL}，reasoning effort {REASONING_EFFORT}')
    print(f'打開 http://localhost:{args.port}/mini-lang-expert.html')
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
