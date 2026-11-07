import json
import re

# 特殊 token：各自佔用一個 id，不會被拆成多個字元
PAD, UNK, EOS, Q, A = '<PAD>', '<UNK>', '<EOS>', '<Q>', '<A>'
SPECIAL_TOKENS = [PAD, UNK, EOS, Q, A]
_SPECIAL_RE = re.compile('(' + '|'.join(re.escape(t) for t in SPECIAL_TOKENS) + ')')

class CharTokenizer:
    """字元級 tokenizer，外加 <PAD> <UNK> <EOS> <Q> <A> 五個特殊 token。"""

    def __init__(self, itos):
        self.itos = list(itos)
        self.stoi = {ch: i for i, ch in enumerate(self.itos)}
        self.pad_id = self.stoi[PAD]
        self.unk_id = self.stoi[UNK]
        self.eos_id = self.stoi[EOS]

    @classmethod
    def build(cls, texts):
        chars = set()
        for text in texts:
            for part in _SPECIAL_RE.split(text):
                if part not in SPECIAL_TOKENS:
                    chars.update(part)
        return cls(SPECIAL_TOKENS + sorted(chars))

    @property
    def vocab_size(self):
        return len(self.itos)

    def encode(self, text):
        ids = []
        for part in _SPECIAL_RE.split(text):
            if part in SPECIAL_TOKENS:
                ids.append(self.stoi[part])
            else:
                ids.extend(self.stoi.get(ch, self.unk_id) for ch in part)
        return ids

    def decode(self, ids, skip_special=False):
        tokens = [self.itos[i] for i in ids]
        if skip_special:
            tokens = [t for t in tokens if t not in SPECIAL_TOKENS]
        return ''.join(tokens)

    def unknown_chars(self, text):
        return sorted({ch for part in _SPECIAL_RE.split(text) if part not in SPECIAL_TOKENS
                       for ch in part if ch not in self.stoi})

    def to_dict(self):
        return {'itos': self.itos, 'vocab_size': self.vocab_size}

    @classmethod
    def from_dict(cls, d):
        return cls(d['itos'])

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            return cls.from_dict(json.load(f))
