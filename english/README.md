# Mini-English

用 **600 個核心英文詞** 學會英文。設計文件與驗證報告：

| 檔案 | 內容 |
|---|---|
| [design.md](design.md) | 第 1 階段：調查現有方案、n 的提案、詞的定義、分類與選詞方法、你的四個決定 |
| [mini-english.md](mini-english.md) | 規格：設計原則、1,256 詞的分類表、20 條語法規則、困難結構替代、6 段對話與短文、附錄（唯一權威詞表） |
| [check.py](check.py) | 檢查程式 |
| [lexicon.tsv](lexicon.tsv) | 1,747 個常用英文詞的 Mini-English 說法（本詞／描述／外來詞） |
| [examples.md](examples.md) | 6 段一般英文→Mini-English ＋ 2 段反向，附長度比較 |
| [prompts/system.md](prompts/system.md) | 給 LLM 的系統提示詞（含完整詞表） |
| [prompts/tasks.md](prompts/tasks.md) | 任務模板 A–F 與建議工作流程 |
| [report.md](report.md) | 設計報告：與現有方案比較、各類詞的取捨、六項驗證結果、已知限制 |
| [translate.py](translate.py) | 反向翻譯：Mini-English → 一般英文（用詞典查表） |
| [web/](web/) | 網頁專案：翻譯器、檢查器、詞表瀏覽、LLM 專家（[web/README.md](web/README.md)） |
| [tools/prompt_test.py](tools/prompt_test.py) | 提示詞效果測試（LLM 一次寫對率） |

## 怎麼用

```bash
python check.py                    # 自我檢查 mini-english.md
python check.py "some text"        # 檢查一段文字
python check.py --md examples.md   # 檢查 markdown 裡的 ```en 區塊
python check.py --lexicon lexicon.tsv
python check.py --file corpus.txt  # 逐行檢查語料
```

網頁專案：

```bash
python web/build.py          # 重新產生 web/data.js
node web/test.js             # 26 個測試
python web/crosscheck.py     # JS 檢查器 vs check.py
python web/expert_server.py  # LLM 專家（需要 NVIDIA_API_KEY）
```

## 改詞表

詞表住在 `data/*.tsv`，`python build.py` 會重新產生 `mini-english.md` 的詞表與所有附錄（也會同步 `prompts/system.md`）。
改完務必跑 `python check.py`：它會檢查詞表有沒有重複、表格與附錄是否一致、所有例句是否通過、提示詞與規格是否同步。
