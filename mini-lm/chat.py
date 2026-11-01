import argparse
import torch
from model import load_checkpoint
from data import load_qa, split_holdout, format_prompt

def answer(model, tokenizer, question, device, temperature=0.0, top_k=None, max_new_tokens=64):
    prompt = format_prompt(question)
    idx = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long, device=device)
    out = model.generate(idx, max_new_tokens, temperature=temperature, top_k=top_k,
                         eos_id=tokenizer.eos_id)
    return tokenizer.decode(out[0, idx.size(1):].tolist(), skip_special=True).strip()

def evaluate(model, tokenizer, pairs, name, device, show=0):
    """以 greedy 解碼回答每一題，回傳完全一致的比例。"""
    correct = 0
    for i, (q, a) in enumerate(pairs):
        pred = answer(model, tokenizer, q, device)
        ok = pred == a
        correct += ok
        if i < show:
            print(f"{'✅' if ok else '❌'} {q} → {pred}" + ('' if ok else f"（正解: {a}）"))
    acc = correct / len(pairs) if pairs else 0.0
    print(f"📊 {name}: {correct}/{len(pairs)} 正確 ({acc:.0%})")
    return acc

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mini-lm 問答')
    parser.add_argument('question', nargs='?', help='要問的問題；省略則進入互動模式')
    parser.add_argument('--ckpt', default='finetune.pt')
    parser.add_argument('--temperature', type=float, default=0.0, help='0 為 greedy')
    parser.add_argument('--top_k', type=int, default=None)
    parser.add_argument('--eval', action='store_true', help='在 finetune.txt 的訓練/驗證集上評估')
    parser.add_argument('--holdout', type=float, default=0.2)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, _, tokenizer = load_checkpoint(args.ckpt, device)

    if args.eval:
        # 與 finetune.py 相同的種子與比例，才會切出同一份驗證集
        train_pairs, val_pairs = split_holdout(load_qa('finetune.txt'), args.holdout, args.seed)
        evaluate(model, tokenizer, train_pairs, '訓練集', device)
        if val_pairs:
            evaluate(model, tokenizer, val_pairs, '驗證集', device, show=len(val_pairs))
    elif args.question:
        print(answer(model, tokenizer, args.question, device, args.temperature, args.top_k))
    else:
        print("輸入問題（空行離開）")
        while True:
            try:
                q = input('Q> ').strip()
            except EOFError:
                break
            if not q:
                break
            print('A>', answer(model, tokenizer, q, device, args.temperature, args.top_k))
