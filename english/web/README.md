# Mini-English 網頁專案

| 檔案 | 做什麼 |
|---|---|
| [index.html](index.html) | 翻譯器：English ⇄ Mini-English，附檢查、詞表、語法規則與範例。**直接打開就能用**（不用伺服器） |
| [minienglish.js](minienglish.js) | 引擎：翻譯與檢查的規則（和 `check.py` 同一套規則） |
| [app.js](app.js) | 介面 |
| [expert.html](expert.html) | Mini-English 專家：跟 LLM 對話，讓它用 Mini-English 回答、翻譯、寫文章 |
| [expert_server.py](expert_server.py) | 專家的本機伺服器（代為呼叫 LLM API、金鑰只留在伺服器裡） |
| [build.py](build.py) | 從 `mini-english.md` 與 `lexicon.tsv` 產生 `data.js` |
| [test.js](test.js) | Node 測試（26 個） |
| [crosscheck.py](crosscheck.py) | 交叉檢查：網頁的 JS 檢查器必須和 `check.py` 一致 |

## 用法

```bash
# 一、規則翻譯器：直接開檔案
open index.html          # macOS；或用任何瀏覽器開啟

# 二、重新產生資料（改了詞表或詞典之後）
python build.py

# 三、測試
node test.js             # 26 個引擎測試
python crosscheck.py     # JS 檢查器 vs check.py

# 四、LLM 專家（需要 API 金鑰）
export NVIDIA_API_KEY=...
python expert_server.py  # 打開 http://localhost:8767/expert.html
```

## 翻譯器在做什麼

* **English → Mini-English**：用 `lexicon.tsv` 逐詞換成 Mini-English 的說法。
  表內的詞照抄；表外的詞換成描述或外來詞；詞典沒有的標成紅色。
  外來詞保留原詞，括號說明放在滑鼠提示裡。
* **Mini-English → English**：用 `lexicon.tsv` 與 `data/reverse.tsv` 反查。
  這是**近似還原**，不是完美的翻譯：描述只能還原成一個可能的詞（`the place where
  doctors help sick people` → `hospital`），冠詞與時態也不會完全對上。
  想要完美的還原請用 LLM 專家。
* **檢查**：貼一段文字，按「檢查這段文字」，會列出表外的詞、禁用詞（附替代說法）、
  缺括號說明的外來詞。規則與 `check.py` 完全相同，`python crosscheck.py` 會驗證兩邊一致。

## 專家在做什麼

1. 網頁把對話送到本機的 `expert_server.py`。
2. 伺服器用 [prompts/system.md](../prompts/system.md) 當系統提示詞，並附上「這次對話用得到的詞典條目」。
3. 模型寫完 Mini-English，會自己呼叫 `check_minienglish` 工具檢查；工具回傳違規的詞與替代說法，
   模型只改違規的地方再檢查，最多 5 輪。
4. 網頁再用自己的檢查器檢一次，違規的詞標紅。

實測（GLM 5.3 Flash，同樣的 3 段文章）：

| 做法 | 一次寫對 | 每段違規詞數 | 時間 |
|---|---:|---:|---:|
| 只給系統提示詞 | **0/3** | 3～9 個 | 3～6 秒 |
| 提示詞＋檢查工具（模型自己改） | **3/3** | 0 | 15～25 秒 |

沒有工具時最常犯的錯：**忘記給外來詞加括號說明**（`caffeine`、`cyclist`）、數字寫成英文（`two`）、
以及把原文的生僻詞照抄（`cattle`、`Manger`、`growled`）。

重跑這個測試：

```bash
export NVIDIA_API_KEY=...
python ../tools/prompt_test.py --passages 3            # 只給提示詞
python ../tools/prompt_test.py --passages 3 --tool     # 讓模型自己用檢查工具
```
