import torch
import torch.nn as nn
import torch.nn.functional as F
from tokenizer import CharTokenizer

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm_x = torch.mean(x ** 2, dim=-1, keepdim=True)
        return self.weight * (x * torch.rsqrt(norm_x + self.eps))

def precompute_freqs_cis(dim, end, theta=10000.0):
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim))
    t = torch.arange(end, device=freqs.device)
    freqs = torch.outer(t, freqs).float()
    return torch.polar(torch.ones_like(freqs), freqs)

def apply_rotary_emb(xq, xk, freqs_cis):
    xq_ = torch.view_as_complex(xq.float().reshape(*xq.shape[:-1], -1, 2))
    xk_ = torch.view_as_complex(xk.float().reshape(*xk.shape[:-1], -1, 2))
    freqs_cis = freqs_cis.unsqueeze(0).unsqueeze(2)
    xq_out = torch.view_as_real(xq_ * freqs_cis).flatten(3)
    xk_out = torch.view_as_real(xk_ * freqs_cis).flatten(3)
    return xq_out.type_as(xq), xk_out.type_as(xk)

class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden_dim, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))

class Attention(nn.Module):
    def __init__(self, dim, n_heads):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.wq = nn.Linear(dim, dim, bias=False)
        self.wk = nn.Linear(dim, dim, bias=False)
        self.wv = nn.Linear(dim, dim, bias=False)
        self.wo = nn.Linear(dim, dim, bias=False)

    def forward(self, x, freqs_cis):
        B, T, C = x.shape
        q = self.wq(x).view(B, T, self.n_heads, self.head_dim)
        k = self.wk(x).view(B, T, self.n_heads, self.head_dim)
        v = self.wv(x).view(B, T, self.n_heads, self.head_dim)

        q, k = apply_rotary_emb(q, k, freqs_cis[:T])
        q, k, v = q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)

        # 因果遮罩：每個位置只能看到自己與之前的 token
        out = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.wo(out)

class TransformerBlock(nn.Module):
    def __init__(self, dim, n_heads, dropout=0.0):
        super().__init__()
        self.attention = Attention(dim, n_heads)
        self.ffn = FeedForward(dim, hidden_dim=4 * dim)
        self.norm1 = RMSNorm(dim)
        self.norm2 = RMSNorm(dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, freqs_cis):
        x = x + self.dropout(self.attention(self.norm1(x), freqs_cis))
        x = x + self.dropout(self.ffn(self.norm2(x)))
        return x

IGNORE_INDEX = -100  # targets 中標成這個值的位置不計 loss

class ModernLanguageModel(nn.Module):
    def __init__(self, vocab_size, d_model=128, n_heads=4, n_layers=4, seq_len=64, dropout=0.0):
        super().__init__()
        self.seq_len = seq_len
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([TransformerBlock(d_model, n_heads, dropout) for _ in range(n_layers)])
        self.norm = RMSNorm(d_model)
        self.output = nn.Linear(d_model, vocab_size, bias=False)
        self.tok_emb.weight = self.output.weight
        # 註冊成 buffer，model.to(device) 時會一起搬移；不存進 state_dict
        self.register_buffer('freqs_cis', precompute_freqs_cis(d_model // n_heads, seq_len * 2), persistent=False)

    def forward(self, idx, targets=None):
        x = self.tok_emb(idx)
        for layer in self.layers:
            x = layer(x, self.freqs_cis)
        logits = self.output(self.norm(x))

        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B*T, C), targets.view(B*T), ignore_index=IGNORE_INDEX)
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None, eos_id=None):
        """temperature=0 為 greedy（每次取機率最高者）；
        top_k 只從前 k 名抽樣；生成到 eos_id 就停止。"""
        self.eval()
        finished = torch.zeros(idx.size(0), dtype=torch.bool, device=idx.device)
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.seq_len:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            if temperature == 0:
                idx_next = logits.argmax(dim=-1, keepdim=True)
            else:
                logits = logits / temperature
                if top_k is not None:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = float('-inf')
                probs = F.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)
            if eos_id is not None:
                # 已經結束的序列持續補 eos，不再產生新內容
                idx_next[finished] = eos_id
                finished |= idx_next.squeeze(1) == eos_id
            idx = torch.cat((idx, idx_next), dim=1)
            if eos_id is not None and finished.all():
                break
        return idx

def build_model(config):
    return ModernLanguageModel(**config)

def save_checkpoint(path, model, config, tokenizer):
    torch.save({'model': model.state_dict(), 'config': config, 'vocab': tokenizer.to_dict()}, path)

def load_checkpoint(path, device='cpu'):
    ckpt = torch.load(path, map_location=device)
    model = build_model(ckpt['config']).to(device)
    model.load_state_dict(ckpt['model'])
    return model, ckpt['config'], CharTokenizer.from_dict(ckpt['vocab'])
