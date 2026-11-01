import random
import torch
from model import IGNORE_INDEX
from data import format_prompt

def encode_qa(tokenizer, q, a, seq_len, train_question=False):
    """序列為 <Q>問題<A>答案<EOS>。
    預設只對「答案 + <EOS>」計算 loss；train_question=True 時問題也算 loss，模型才學得會發問。"""
    prompt = tokenizer.encode(format_prompt(q))
    answer = tokenizer.encode(a) + [tokenizer.eos_id]
    tokens = (prompt + answer)[:seq_len + 1]
    x = tokens[:-1]
    y = tokens[1:]
    if not train_question:
        y = [IGNORE_INDEX] * (len(prompt) - 1) + y[len(prompt) - 1:]
    return x, y

def train_qa(model, tokenizer, pairs, device, max_iters, lr, batch_size, seq_len,
             train_question=False, log_every=100, tag='Finetune'):
    samples = [encode_qa(tokenizer, q, a, seq_len, train_question) for q, a in pairs]

    def get_batch():
        batch = random.choices(samples, k=batch_size)
        T = max(len(x) for x, _ in batch)
        xs = [x + [tokenizer.pad_id] * (T - len(x)) for x, _ in batch]
        ys = [y + [IGNORE_INDEX] * (T - len(y)) for _, y in batch]
        return torch.tensor(xs, device=device), torch.tensor(ys, device=device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    for iter in range(max_iters):
        model.train()
        xb, yb = get_batch()

        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if log_every and (iter % log_every == 0 or iter == max_iters - 1):
            print(f"{tag} Step {iter:4d} | Loss: {loss.item():.4f}")
