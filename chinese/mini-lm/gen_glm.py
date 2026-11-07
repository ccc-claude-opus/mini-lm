"""用 NVIDIA 的 GLM 5.3 Flash 產生大量 Mini-Lang 語料 → corpus/glm/src/<類別>.txt

每個請求 = 一個類別 × 一個主題 × 一種文體，給模型 Mini-Lang 的系統提示詞（含 297 字的字表），
請它只用字表內的字寫。每一行都用 mini-lang/check.py 的檢查：有字表外的字，就把那些字告訴模型請它改寫
（最多 --fix_rounds 輪），還是不過就丟掉。src/ 裡只有通過檢查的行，丟掉的寫在 rejected.txt。
    python gen_glm.py --workers 6              # 產生（可以中斷，再執行會接著做）
    python build_directions.py --dir corpus/glm  # 再檢查一次字表，去掉人名與重複，切出測試句

需要環境變數 NVIDIA_API_KEY。
"""
import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mini-lang'))
from check import DOC, load_charset, unknown  # noqa: E402

API_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'
MODEL = 'z-ai/glm-5.3-flash'

parser = argparse.ArgumentParser(description='用 GLM 5.3 Flash 產生 Mini-Lang 語料')
parser.add_argument('--out_dir', default=os.path.join(HERE, 'corpus', 'glm'))
parser.add_argument('--workers', type=int, default=8, help='同時送出的請求數')
parser.add_argument('--limit', type=int, default=0, help='只做前幾個請求（試跑用）')
parser.add_argument('--rounds', type=int, default=1, help='每個請求做幾輪（第 2 輪起請模型寫不一樣的內容）')
parser.add_argument('--fix_rounds', type=int, default=2, help='有字表外的字時，請模型改寫幾輪')
args = parser.parse_args()

# ==========================================
# 1. 請求的組合：類別 × 主題 × 文體
# ==========================================
TOPICS = {
    'daily': ('日常生活', '早上起來、做飯、洗衣服、買東西、週末、生日、到新家住、等車、下雨天、晚上在家'),
    'family': ('家人與朋友', '爸媽、哥哥姐姐弟弟妹妹、和朋友見面、一起吃飯、家裡的老人、照顧小孩、打電話、想家、吵了又好了、送東西給人'),
    'school': ('學校與學習', '上課、老師、學生、寫字、問問題、學外語、看書、下課、學校的地方、學會一件事'),
    'work': ('工作', '工人、醫生、老師、開店、在店裡賣東西、工作很忙、找工作、做事的方法、休息、工作的地方'),
    'nature': ('自然', '海、河、山、樹和草、雲、雨和雪、風、星星和月、石頭和土、花'),
    'animals': ('動物', '鳥、魚、蟲、馬、牛、豬、雞、動物吃什麼、動物住在哪裡、動物和人'),
    'body': ('身體與健康', '頭和臉、手和腳、眼睛鼻子和口、牙、生病、看醫生、睡覺、多喝水、動一動身體、血'),
    'food': ('吃的和喝的', '飯和菜、肉、雞蛋、水果、茶、早飯午飯晚飯、做菜、甜和苦、在外邊吃飯、一起喝茶'),
    'places': ('地方與方向', '問路、東南西北、左右前後、城裡、家的四邊、學校在哪裡、遠和近、上邊下邊、山上、河邊'),
    'transport': ('交通', '走路、坐車、火車、飛機、電車、開車、等車、路上的車很多、去很遠的地方、回家的路'),
    'time': ('時間與數量', '幾點、週1到週日、一年的時候、多少錢、多少人、第幾、等了多長時間、早和晚、以前和以後、現在'),
    'feelings': ('心情與想法', '開心、難過、怕、生氣、喜歡和愛、想一想、覺得、不放心、樂了、哭了又笑了'),
    'talk': ('說話與禮貌', '打招呼、請和謝謝、對不起、歡迎、問別人的名字、請人幫忙、說再見、不懂再問一次、說好、客人來了'),
    'language': ('語言與文字', '學中文、字和詞、一句話的意思、名詞、唱歌、畫畫、寫一個字、說得慢一點、聽懂、用手寫'),
    'reasoning': ('推理與因果', '因為所以、要是就、比一比、為什麼、先後、可能和不可能、一樣和不一樣、多和少、對和不對、想出方法'),
    'colors': ('顏色與樣子', '紅色、綠色、藍色、白和黑、大和小、長和高、圓圓的、新和老、好看、亮和暗以外的說法'),
    'world': ('國家與天下', '中國、外國、天下、大城、國家的人、外國人學中文、去外國、國家的話、地球、很多國家'),
    'play': ('玩和運動', '打球、跳、走走、一起玩、在外邊玩、跑以外的說法、玩水、玩的東西、比一比誰快、累了休息'),
}
FORMATS = {
    'sentences': '寫 25 個不同的句子，每句 8 到 30 個字，每行一句。',
    'dialogue': '寫 10 段對話，每段 2 到 4 句話，整段寫在同一行，每句話用「」括起來。',
    'story': '寫 6 個小故事，每個故事 3 到 6 句，整個故事寫在同一行。',
    'explain': '寫 8 段說明，每段 2 到 4 句，像在對小孩說明事情，每段寫在同一行。',
}
RULES = """要求：
* 每一個漢字都必須在字表內。寫完逐字檢查，不在字表內的字一定要換掉（看系統提示詞第 3、5、6 節）。
* 不要用英文，也不要用外來語；說不出來的東西就換一個話題。
* 不要用人名；用「我、你、他、我的朋友、那個老師、一個孩子」這樣的說法。
* 數字用阿拉伯數字。
* 每一行是完整的內容；不要編號、不要標題、不要寫任何說明或註。
* 句子要自然、多樣，不要重複同樣的句型。"""


def tasks():
    out = []
    for key, (cat, topics) in TOPICS.items():
        for t in topics.split('、'):
            for fmt in FORMATS:
                for r in range(args.rounds):
                    out.append({'id': f'{key}|{t}|{fmt}|{r}', 'cat': key, 'cat_name': cat, 'topic': t, 'fmt': fmt, 'round': r})
    return out


# ==========================================
# 2. 呼叫模型
# ==========================================
def system_prompt():
    text = open(os.path.join(HERE, '..', 'mini-lang', 'prompts', 'system.md'), encoding='utf-8').read()
    return text.split('\n---\n')[1].strip()


def write_prompt(task):
    return (f"請用 Mini-Lang 寫語料。\n類別：{task['cat_name']}\n主題：{task['topic']}\n{FORMATS[task['fmt']]}\n\n{RULES}"
            + ('\n* 這是第 {} 次寫這個主題，請寫和平常不一樣的內容。'.format(task['round'] + 1) if task['round'] else ''))


def fix_prompt(bad):
    items = '\n'.join(f"{i + 1}. {line}〔不在字表：{'、'.join(chars)}〕" for i, (line, chars) in enumerate(bad))
    return (f"下面 {len(bad)} 行有字表外的字（寫在〔〕裡）。請逐行改寫，意思不變，只用字表內的字；"
            f"字表外的字要換成字表內的說法（看系統提示詞第 3、5、6 節），換不了就把那個部分改掉。\n"
            f"只輸出改好的 {len(bad)} 行，一行對一行，順序不變，不要編號、不要〔〕、不要說明。\n\n{items}")


def ask(system, user, key, task, tries=5):
    body = json.dumps({'model': MODEL, 'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                       'max_tokens': 6000, 'temperature': 0.9, 'reasoning_effort': 'low'}).encode()
    for k in range(tries):
        req = urllib.request.Request(API_URL, data=body, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.load(resp)['choices'][0]['message'].get('content') or ''
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError) as e:
            wait = 10 * (k + 1)
            print(f'   ⚠️ {task["id"]} 第 {k + 1} 次失敗（{str(e)[:80]}），{wait} 秒後重試', flush=True)
            time.sleep(wait)
    return None


def clean(text):
    """把模型的輸出切成一行一筆：去掉編號、項目符號、程式碼區塊標記。"""
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith('```') or line.startswith('〔'):
            continue
        line = re.sub(r'^(\d+[.、．)]|[-*•]\s)\s*', '', line).strip()
        if line:
            lines.append(line)
    return lines


def main():
    key = os.environ.get('NVIDIA_API_KEY')
    if not key:
        sys.exit('找不到環境變數 NVIDIA_API_KEY')
    src = os.path.join(args.out_dir, 'src')
    os.makedirs(src, exist_ok=True)
    progress_path = os.path.join(args.out_dir, 'progress.json')
    progress = json.load(open(progress_path)) if os.path.exists(progress_path) else {}
    todo = [t for t in tasks() if t['id'] not in progress]
    if args.limit:
        todo = todo[:args.limit]
    charset = set(load_charset(open(DOC, encoding='utf-8').read()))
    system = system_prompt()
    lock = threading.Lock()
    t0 = time.time()
    print(f'共 {len(tasks())} 個請求，已完成 {len(progress)}，這次做 {len(todo)} 個（{args.workers} 個同時）', flush=True)

    def bad_chars(line):
        return unknown(line, charset) + sorted(set(re.findall(r'[A-Za-z]', line)))

    def run(task):
        text = ask(system, write_prompt(task), key, task)
        if text is None:
            return task, None
        lines = clean(text)
        ok = [l for l in lines if not bad_chars(l)]
        bad = [(l, bad_chars(l)) for l in lines if bad_chars(l)]
        first_ok = len(ok)
        for _ in range(args.fix_rounds):
            if not bad:
                break
            text = ask(system, fix_prompt(bad), key, task)
            fixed = clean(text) if text else []
            if len(fixed) != len(bad):   # 行數對不上就無法一行對一行，只收通過檢查的
                ok += [l for l in fixed if not bad_chars(l)]
                break
            ok += [l for l in fixed if not bad_chars(l)]
            bad = [(l, bad_chars(l)) for l in fixed if bad_chars(l)]
        assert all(not bad_chars(l) for l in ok)
        with lock:
            with open(os.path.join(src, task['cat'] + '.txt'), 'a', encoding='utf-8') as f:
                f.write(''.join(l + '\n' for l in ok))
            with open(os.path.join(args.out_dir, 'rejected.txt'), 'a', encoding='utf-8') as f:
                f.write(''.join(f"{l}\t{''.join(c)}\n" for l, c in bad))
            progress[task['id']] = {'lines': len(lines), 'first_ok': first_ok, 'ok': len(ok)}
            with open(progress_path, 'w') as f:
                json.dump(progress, f, ensure_ascii=False)
        return task, (len(lines), first_ok, len(ok))

    done = n_lines = n_first = n_ok = 0
    with ThreadPoolExecutor(args.workers) as pool:
        for fut in as_completed([pool.submit(run, t) for t in todo]):
            task, res = fut.result()
            done += 1
            if res:
                n_lines += res[0]
                n_first += res[1]
                n_ok += res[2]
            if done % 10 == 0 or done == len(todo):
                pct = (lambda n: f'{n / n_lines:.0%}' if n_lines else '-')
                print(f'{done}/{len(todo)}｜{time.time() - t0:.0f}s｜產生 {n_lines} 行，一次就通過 {n_first}（{pct(n_first)}），'
                      f'改寫後通過 {n_ok}（{pct(n_ok)}）', flush=True)
    print('✅ 完成。下一步：python build_directions.py --dir corpus/glm', flush=True)


if __name__ == '__main__':
    main()
