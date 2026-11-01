import random

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

def load_qa(path):
    pairs = [parse_qa(line) for line in read_unique_lines(path)]
    return [p for p in pairs if p is not None]

def split_holdout(pairs, holdout_ratio, seed):
    """固定亂數種子切出驗證集：驗證集的問答不參與微調，
    用來看模型能否靠預訓練學到的知識回答沒看過的問題。"""
    pairs = list(pairs)
    random.Random(seed).shuffle(pairs)
    n_holdout = int(len(pairs) * holdout_ratio)
    return pairs[n_holdout:], pairs[:n_holdout]

def format_prompt(question):
    return f'<Q>{question}<A>'
