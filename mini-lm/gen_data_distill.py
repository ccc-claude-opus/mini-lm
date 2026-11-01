import argparse
import os
from openai import OpenAI

parser = argparse.ArgumentParser(description='用大模型蒸餾出訓練語料')
parser.add_argument('--out_dir', default='corpus/planets', help='輸出的語料目錄')
args = parser.parse_args()
os.makedirs(args.out_dir, exist_ok=True)

print("=== 開始執行大模型資料蒸餾 (Knowledge Distillation) ===")

# ==========================================
# 1. 初始化 NVIDIA API Client
# ==========================================
# 從環境變數讀取 API KEY
api_key = os.environ.get("NVIDIA_API_KEY")
if not api_key:
    raise ValueError("找不到 NVIDIA_API_KEY！請先在終端機執行: export NVIDIA_API_KEY='你的金鑰'")

client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=api_key
)

# ==========================================
# 2. 設計 Prompt 逼迫大模型產出特定格式的訓練資料
# ==========================================
# 為了避免我們的小模型詞表爆掉，我們要求大模型使用簡單的詞彙，並嚴格限制格式。
prompt = """
請扮演一個嚴格的資料生成器。我要訓練一個微型語言模型，請幫我生成關於「太陽系八大行星」的訓練資料。
請使用極度簡單的繁體中文，並且嚴格遵守以下兩種格式，不要輸出任何其他廢話或解說。

格式1 (知識敘述)：[FACT] 敘述句。
格式2 (問答訓練)：[QA] <Q>問題？<A>答案

請生成 50 句 [FACT] 和 50 句對應的 [QA]。

範例：
[FACT] 地球是太陽系中唯一有生命的行星。
[FACT] 火星的表面是紅色的。
[QA] <Q>哪顆行星有生命？<A>地球
[QA] <Q>火星的表面是什麼顏色？<A>紅色
"""

print("-> 正在呼叫 Minimax 大模型生成教材，請稍候...\n")

completion = client.chat.completions.create(
  model="minimaxai/minimax-m2.7",
  messages=[{"role":"user", "content": prompt}],
  temperature=0.7, # 稍微降低溫度，讓格式更穩定
  top_p=0.95,
  max_tokens=8192,
  stream=True
)

# ==========================================
# 3. 接收 Streaming 回應並解析資料
# ==========================================
teacher_response = ""
print("👨‍🏫 Teacher 產出中：")
for chunk in completion:
    if not getattr(chunk, "choices", None):
        continue
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        print(content, end="")
        teacher_response += content

print("\n\n-> 接收完畢，開始解析資料...")

# 解析大模型的輸出
pretrain_facts = []
finetune_qa = []

for line in teacher_response.split('\n'):
    line = line.strip()
    if line.startswith("[FACT]"):
        pretrain_facts.append(line.replace("[FACT]", "").strip()+"\n")
    elif line.startswith("[QA]"):
        finetune_qa.append(line.replace("[QA]", "").strip() + "\n")

if len(pretrain_facts) == 0 or len(finetune_qa) == 0:
    raise ValueError("大模型沒有按照格式輸出，請重新執行一次。")

print(f"-> 成功解析出 {len(pretrain_facts)} 條知識，{len(finetune_qa)} 條問答。")

# ==========================================
# 4. 去除重複句子
# ==========================================
# 舊版會把幾十句重複打亂拼接到十萬字，那只是讓同樣的句子出現上千次，
# 並沒有增加資訊量；現在只存不重複的句子，打亂與取樣交給 pretrain.py / finetune.py。
pretrain_facts = list(dict.fromkeys(pretrain_facts))
finetune_qa = list(dict.fromkeys(finetune_qa))
pretrain_text = "".join(pretrain_facts)
finetune_text = "".join(finetune_qa)

# ==========================================
# 5. 儲存純文字檔 (供後續 pretrain.py 建立詞表與張量)
# ==========================================
print(f"-> 儲存純文字檔到 {args.out_dir}/ (pretrain.txt, finetune.txt)...")
with open(os.path.join(args.out_dir, 'pretrain.txt'), 'w', encoding='utf-8') as f:
    f.write(pretrain_text)

with open(os.path.join(args.out_dir, 'finetune.txt'), 'w', encoding='utf-8') as f:
    f.write(finetune_text)

print("✅ 大模型蒸餾資料準備完成！請繼續執行 ./run.sh")
