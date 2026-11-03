# Mini-Lang 提示詞

讓一般的 LLM（Claude、GPT、Gemini、MiniMax…）認識 Mini-Lang，能翻譯、也能直接用 Mini-Lang 寫文章。

| 檔案 | 內容 |
|---|---|
| [system.md](system.md) | 系統提示詞：297 字的字表、四個原則、換詞的三層、外來語、數字與量詞、語法替代表、自我檢查 |
| [expert.md](expert.md) | 網頁版「Mini-Lang 專家」加在 system.md 後面的部分：專家的角色、回答格式（Mini-Lang 放在 minilang 區塊）、專案背景 |
| [tasks.md](tasks.md) | 六個任務的模板：中文 → Mini-Lang、Mini-Lang → 中文、English → Mini-Lang、Mini-Lang → English、寫文章、修改 |

## 使用方法

1. 把 [system.md](system.md) 中兩條「---」之間的內容，整段放進系統提示詞。
2. 從 [tasks.md](tasks.md) 選一個模板，把 `{{…}}` 換成實際內容，當使用者訊息送出。
3. 用 [check.py](../check.py) 檢查輸出有沒有字表外的字；有的話，用任務 F 請 LLM 只改那幾句。

```bash
python mini-lang/check.py "LLM 寫出來的 Mini-Lang 文章"
```

## 和規格的關係

提示詞是 [mini-lang.md](../mini-lang.md) 與 [universal.md](../universal.md) 的濃縮版，只收 LLM 寫作時最需要的規則和最常用的換法。

* 提示詞裡的字表直接從規格複製；[check_universal.py](../check_universal.py) 會檢查兩者是否一致，以及提示詞中所有 Mini-Lang 例句是否只用字表內的字。
* 改了字表或規則之後，要同步修改 system.md，再執行 `python mini-lang/check_universal.py`。

## 測試結果

把提示詞交給完全不認識 Mini-Lang 的模型（只給 system.md 和任務，不給其他資料），再用 check.py 檢查輸出。所有原文都是為測試新寫的。

| 模型 | 任務 | 字表外的字 | 結果 |
|---|---|---|---|
| Claude Sonnet | A 中文 → Mini-Lang（借書、下大雨） | 無 | 通順，〔註〕清楚列出改寫的地方（借書 → 拿書回家看） |
| Claude Sonnet | C English → Mini-Lang（外婆的村子） | 面 | 寫了「裡面」，應為「裡邊」 |
| Claude Sonnet | E 寫文章（搬家，150 字） | 無 | 141 字；發現「搬」不在字表，題目改成「到新家」 |
| Claude Sonnet | D Mini-Lang → English | — | 英文通順，「他」正確翻成 him（狗） |
| Claude Haiku | A 中文 → Mini-Lang（被選為經理、雖然、已經、前面…） | 無 | 陷阱都避開：被選為 → 有人叫他做、前面 → 前邊、她 → 他 |
| Claude Haiku | C English → Mini-Lang | 她 | 第三人稱寫成「她」 |

依測試結果修改了提示詞：「…面」改「…邊」、第三人稱一律「他」提到最前面的原則，並補上借、搬家、安靜、專心、很久、祖父母的換法。

**結論：** 能力較強的模型大多一次就寫對；較弱的模型偶爾會寫出一兩個字表外的字，所以建議照[工作流程](tasks.md#建議的工作流程)用 check.py 檢查、再用任務 F 修改。
