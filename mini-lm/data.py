import os
import random

# 語料目錄的約定檔名：
#   pretrain.txt  每行一句，用於預訓練
#   finetune.txt  每行一組 <Q>問題<A>答案，用於微調
#   charset.txt   （可選）一定要放進詞表的字元
PRETRAIN_FILE = 'pretrain.txt'
FINETUNE_FILE = 'finetune.txt'
CHARSET_FILE = 'charset.txt'

def read_unique_lines(path):
    """讀取檔案中不重複的非空行（保留第一次出現的順序）。
    舊版資料是把幾十句重複打亂拼接成十萬字，這裡會自動去重。"""
    seen, lines = set(), []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                lines.append(line)
    return lines

def parse_qa(line):
    """'<Q>問題？<A>答案' -> ('問題？', '答案')，格式不符回傳 None。"""
    if not line.startswith('<Q>') or '<A>' not in line:
        return None
    q, a = line[len('<Q>'):].split('<A>', 1)
    q, a = q.strip(), a.strip()
    return (q, a) if q and a else None

def read_files(paths):
    """依序讀取多個檔案的不重複行（跨檔案也去重）。"""
    lines = []
    for path in paths:
        lines.extend(read_unique_lines(path))
    return list(dict.fromkeys(lines))

def load_qa(paths):
    pairs = [parse_qa(line) for line in read_files(paths)]
    return [p for p in pairs if p is not None]

def add_corpus_args(parser):
    """--corpus 指定語料目錄（可多個，會合併）；--pretrain / --finetune 再額外加入個別檔案。"""
    parser.add_argument('--corpus', nargs='*', default=[], metavar='DIR',
                        help='語料目錄，內含 pretrain.txt / finetune.txt / charset.txt')
    parser.add_argument('--pretrain', nargs='*', default=[], metavar='FILE', help='額外的預訓練檔')
    parser.add_argument('--finetune', nargs='*', default=[], metavar='FILE', help='額外的問答檔')

def corpus_files(args, kind):
    """kind 為 'pretrain' / 'finetune' / 'charset'，回傳存在的檔案清單。"""
    name = {'pretrain': PRETRAIN_FILE, 'finetune': FINETUNE_FILE, 'charset': CHARSET_FILE}[kind]
    files = [os.path.join(d, name) for d in args.corpus if os.path.exists(os.path.join(d, name))]
    files += getattr(args, kind, [])
    for f in files:
        if not os.path.exists(f):
            raise FileNotFoundError(f'找不到語料檔: {f}')
    return files

def default_out_dir(args):
    """沒有指定 --out_dir 時，用語料目錄名稱組成 runs/<名稱>。"""
    names = [os.path.basename(os.path.normpath(d)) for d in args.corpus]
    names += [os.path.splitext(os.path.basename(f))[0] for f in args.pretrain + args.finetune]
    return os.path.join('runs', '+'.join(dict.fromkeys(names)) or 'default')

def split_holdout(pairs, holdout_ratio, seed):
    """固定亂數種子切出驗證集：驗證集的問答不參與微調，
    用來看模型能否靠預訓練學到的知識回答沒看過的問題。"""
    pairs = list(pairs)
    random.Random(seed).shuffle(pairs)
    n_holdout = int(len(pairs) * holdout_ratio)
    return pairs[n_holdout:], pairs[:n_holdout]

def format_prompt(question):
    return f'<Q>{question}<A>'
