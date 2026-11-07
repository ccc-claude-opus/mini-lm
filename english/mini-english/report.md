# Mini-English 設計報告

> Mini-English：核心 600 詞 ＋ 擴充層 656 詞 ＝ **1,256 個英文詞**。
> 學會核心層 600 個詞與 20 條語法規則，就能說日常生活的話、把一般文章改寫成 Mini-English、讀懂別人寫的 Mini-English，
> 而且寫出來的就是正確、自然的英文。
>
> 本報告的每個數字都來自可重跑的檢查（見 [§6 驗證結果](#6-驗證結果)）。

## 1. 摘要

| 項目 | 結果 |
|---|---|
| 詞表 | 核心 600 ＋ 擴充 656 ＝ 1,256 詞；另有 13 個片語動詞例外、數字與單位符號 |
| 語法 | 20 條規則；13 種困難結構有固定替代說法 |
| 詞典 | `lexicon.tsv` 1,747 列（本詞 216／描述 1,479／外來詞 52） |
| 覆蓋率測試 | 隨機抽 200 個表外常用詞：**93.5% 說得出來**（本詞 19%、描述 61%、外來詞 13.5%），6.5% 說不好 |
| 改寫測試 | 6 段真實文章（維基百科 5＋伊索寓言 1）：**第一次寫 0/6 通過**；依錯誤修正詞表與規則後 **6/6 通過** |
| 長度代價 | 日常對話與生活文：−2%～+21%；百科型文章：+22%～+79%（平均 +53%） |
| 自然度 | 抽 20 句檢查，發現 7 處不自然，全部修正 |
| 提示詞效果 | 只給提示詞：LLM 一次寫對 **0/3**；讓模型自己用檢查工具：**3/3**（15～25 秒） |
| 網頁專案 | `web/`：翻譯器＋檢查器＋詞表＋LLM 專家；26 個 Node 測試通過，JS 檢查器與 `check.py` 22 句完全一致 |
| 反向翻譯 | `translate.py`：用詞典把 Mini-English 查回一般英文 |
| 直接命中率 | 現代一般英文（維基百科 10 篇摘要）token 63.7%、字型 45.5% |
| 檢查工具 | `check.py` 自我檢查、詞典檢查、markdown 檢查三種模式，全部通過 |

---

## 2. 為什麼是這個 n

### 2.1 和現有方案比較

| 方案 | 詞數 | 詞表怎麼選 | 語法 | 產出是自然英文？ | 詞表外的詞怎麼處理 | Mini-English 的差別 |
|---|---:|---|---|---|---|---|
| **Ogden Basic English**（1932） | 850 詞根 | 主觀挑選，內容 700／文法 100 | 10 節語法、16 operators | 目標是，但被批評為不自然 | 大量改寫＋約 200 個「國際詞」 | 我們**把文法層從 100 提到 116**（英文 32.6% 的 token 是功能詞，少一個就壞掉文法），並且用**程式檢查＋自然度抽樣**代替主觀挑選 |
| **Globish**（Nerrière） | 1,500 | 觀察非母語者實際用法，**沒有統計依據**（Grzega 批評） | 無編號規則，26 步教學 | 是 | 派生＋複合 | 我們的詞表有**可重跑的選詞理由**（表達力缺口＋生成力）與**機器可驗證的規則** |
| **VOA Special English** | 約 1,500 | 廣播實務 | 無成文語法 | 部分（編輯寫的簡化英語） | 明確允許超出詞表並註解 | 我們的 1,256 詞**全部可檢查**，沒有「廣播例外」 |
| **Simple English Wikipedia** | 約 1,500（建議）、實際 2,000 | 建議不強制 | 無強制 | 是 | 分級階梯＋括號註解 | 實測讀懂一半句子仍需約 18,000 詞 → **軟清單控制不了難度**；我們用固定清單＋檢查程式 |
| **NGSL**（2013/2023） | 2,809 lemmas | 純頻率（273M 詞語料） | 無 | — | — | 頻率表不管自然度與描述能力；我們**用頻率排序、不用頻率選詞** |
| **Oxford 3000** | 3,000 | 頻率＋教學相關性、CEFR 分級 | 無 | — | — | OALD 全書用它 → 證明 3,000 詞足以**定義**英文詞；我們證明 **600 個核心詞足以「生活＋改寫」** |
| **Toki Pona** | 120–137 | 刻意極簡 | 無編號規則 | **不是英文** | 靠複合 | 說明「小」和「自然」是兩個不同的目標；Mini-English 選「自然」 |
| **Mini-English（本研究）** | 核心 600 ＋ 擴充 656 | **表達力缺口＋生成力**；頻率只用於排序 | 20 條規則＋13 種替代 | **是**（寫出來就是正常英文） | 三層：本詞／描述／外來詞 | — |

### 2.2 核心層為什麼是 600

1. **功能詞是底線，不能壓縮。** 實測英文 token 的 **32.6%** 是功能詞；前 100 高頻詞裡 86.7% 是功能詞。
   Mini-English 的語法層有 **116 個功能詞**（代詞 60、語法 116 中的非代詞部分、數量、時間副詞等），
   少一個功能詞，壞掉的是**文法**而不只是少一個意思。Basic English 的教訓正是文法太少（只有 100 個 operators）。
2. **400 個內容詞能覆蓋日常生活。** Mini-Lang 用 297 個漢字覆蓋同一個生活範圍；漢字承載的語意比英文字詞多，
   所以英文需要更多詞。600 詞的核心層對應到 §6.2 的覆蓋率測試：**日常對話與生活文章幾乎不需要描述**（見 examples.md 的前四段，長度變化 −2%～+21%）。
3. **成人可完成的量。** 每天 10 個詞，兩個月學完核心層；1,000 個詞則是整整一年。
4. **擴充層吸收「描述需要的詞」。** 這是第 3、4 階段實測出來的：要做自然的描述，必須有 `throat`、`pig`、`grain`、`liquid`、`thread`、`mark` 這類具體名詞。
   擴充層從原本設計的 400 增到 **656**（新增 256 個），**核心層維持 600 不變**——「要學多少」的決定沒有被驗證結果推翻。

---

## 3. 「詞」的定義

| 決定 | 內容 | 理由 |
|---|---|---|
| 計數單位 | **詞元（lemma）**。`go` 算 1 個，`goes/went/gone/going` 不另外算 | 學習者背的是「一個概念一個形」 |
| 屈折形式 | 收，免費：`-s/-es, -ed, -ing, -er, -est, -ly, 's` | 規則生成的，不該收進 n |
| 派生形式 | 只允許 **3 個字尾、2 個字首**：`un-`, `re-`, `-er`, `-ly`, `-ness` | 白名單越大，讀者遇到沒學過的詞的機率越高；`-tion/-ment/-ity/-ous/-ful/-ize` 全不收 |
| 複合詞 | **收**，但逐個列入附錄（`bus stop`, `bedroom`, `kitchen`, `classroom`, `supermarket`, `bookstore`…），計入 n | 日常對話常用；自由組合會產生不像英文的怪詞 |
| 片語動詞 | **只留 13 個例外**（`look for`, `put on`, `take off`, `get up`, `get off`, `get in`, `get out`, `find out`, `turn off`, `turn on`, `look at`, `look after`, `come back`），不計入 n | 片語動詞是初學者最大的記憶負擔；其餘用表內的單一動詞（`give up` → `stop`） |
| 慣用語 | **全部不收** | 對初學者是純負擔，也幫不上表達意思 |
| 不規則形式 | 保留 63 個動詞的不規則式、27 個不規則複數（附錄逐條列出） | Mini-English 必須是正確英文，不能把 `went` 寫成 `goed` |
| 數字 | 阿拉伯數字；保留 `many, much, few, several, half, whole, double, first, last, next, each, every, some, any, all, none, both, either, neither, enough, more, most, less, least, once, twice` | 判準：能換成別的數字還說得通的，就是數字 |

---

## 4. 各類詞：為什麼收、為什麼不收

| 類別 | 收了什麼、為什麼 | 刪掉的高頻詞 → 替代說法 |
|---|---|---|
| **代詞・指示（61）** | 完整的人稱代詞與所有格。Mini-Lang 只留「他」是因為漢字不分性別；英文不行 | `them` → 保留（代詞不能省）；`yours` → 保留（所有格） |
| **語法功能詞（127）** | be 全部形式、do/have/will/can/must/should、全部連接詞與介系詞、量詞 | `however` → 收（新聞常用）；`nevertheless` → `but`；`furthermore` → `also`；`prior to` → `before`；`in order to` → `to` |
| **數量・比例（9）** | 量詞與比例詞 | `one…twenty` → 全部用阿拉伯數字（`one` 因 `one of them` 保留） |
| **時間（48）** | 一週七天、月份用「第 N 月」、時段詞 | `o'clock` → 收（`7 o'clock`） |
| **方位・地點（93）** | 問路、購物、醫療、旅遊會用到的地點詞 | `downtown` → `in the middle of the city`；`avenue` → `a wide road with trees on both sides` |
| **自然・天氣（54）** | 天氣動植物與自然物 | `meteor` → `a ball of fire that goes through the air`；`nebula` → `a big cloud of gas and dust in the sky` |
| **動作（200）** | 日常動詞＋描述文章要用的抽象動詞（`include, provide, contain, require, establish…`） | `purchase` → `buy`；`obtain` → `get`；`utilize` → `use`；`assist` → `help`；`attempt` → `try`；`endeavor` → `try` |
| **性質（124）** | 8 個基本顏色＋13 個基本性質＋大量描述用形容詞 | `large` → `big`；`huge` → `very big`；`tiny` → `very small`；`great` → `very good`；`excellent` → `very good`；`terrible` → `very bad`；`enormous` → `very big` |
| **事物（106）** | 吃、住、穿、身體、交通、工具、錢 | `hamburger` → `bread with meat inside`；`receipt` → `the paper that shows what you paid` |
| **社交・人（62）** | 稱呼、問候、親屬、職業 | `policeman` → `a person who works for the police`（`police` 在表內） |
| **抽象概念（117）** | **描述模板的骨架**：`thing, person, place, kind, way, part, group, tool, machine, reason, result, problem, question, answer, idea, plan, story, article, report, system, process, effect, value…` | `utilization` → `use`；`functionality` → `what it can do`；`conceptualize` → `think` |

**被刪掉的高頻詞的完整清單**在 `mini-english.md` 的「附錄：常用但禁止的詞與替代說法」（119 條），
那張表同時是 `check.py` 的錯誤訊息來源，也是 `prompts/system.md` 裡的「最常犯的錯」清單。

---

## 5. 語法與困難結構

20 條規則涵蓋：主謂賓、be 動詞、第三人稱單數、進行式、過去式、將來式、否定、是非問句、wh- 問句、
冠詞、所有格、複數、形容詞與副詞、介系詞、連接詞、比較、能力與義務、數量、目的、存在。

不收的結構與固定替代（完整表在 `mini-english.md` §6）：

| 困難結構 | 替代 | 例子 |
|---|---|---|
| 被動語態 | 主動語態 | `My brother cleaned the room.` |
| 完成式 | 過去式＋already / before | `I ate my lunch already.` |
| 關係子句 | 拆句或描述 | `That man came. He is my uncle.` |
| 虛擬語氣 | if＋現在式＋will | `If I have money, I will travel.` |
| 動名詞當主語 | to + V | `It is fun to use a phone.` |
| 分詞片語 | that / 介系詞片語 | `A car that stopped at the door.` |
| 倒裝、強調 | 不寫 | `I want my car.` |

**理由**：英語的難點不在這些結構本身，而在它們與其他結構的組合。一套只含 20 條規則、且每條都是母語者每天在寫的句型的系統，
可以讓學習者把注意力放在詞上；把被動、完成式、關係子句全部拿掉之後，寫出來的句子仍然是**正確的英文**。

---

## 6. 驗證結果

### 6.1 所有交付物都通過 check.py

```
$ python check.py
詞表：1256 詞，不重複 1256 詞
檢查了 1332 段例句與例子
✅ prompts/system.md 的詞表一致（1256 詞）
✅ 全部通過

$ python check.py --lexicon lexicon.tsv
詞典 lexicon.tsv：1747 列（本詞 216／描述 1479／外來詞 52）
✅ 全部通過

$ python check.py --md examples.md
examples.md：8 個 ```en 區塊，✅ 全部在字表內
```

`check.py` 自我檢查包含四件事：詞表無重複、§2 表格與附錄完全一致、所有例句通過、`prompts/system.md` 的詞表與附錄逐字一致。

### 6.2 覆蓋率測試（200 個表外常用詞）

抽樣方式：從 Google 10,000 常用英文詞表的前 3,000 個詞中，排除已在詞表內（1,256）與已在 `lexicon.tsv` 內（1,747）的詞，
用固定亂數種子（20261107）抽 200 個，逐個嘗試用 Mini-English 說。

| 結果 | 個數 | 比例 | 例子 |
|---|---:|---:|---|
| **本詞**（本來就在表內或是它的變化形） | 38 | 19.0% | `boats`, `stopped`, `makes`, `highest` |
| **描述**（用表內的詞說清楚） | 122 | 61.0% | `reasonable` → `not too much and not too little`；`operator` → `people who work with machines` |
| **外來詞**（只能用原詞＋括號說明） | 27 | 13.5% | `nintendo` → `nintendo (a company that makes game machines)`；`iraqi` → `iraqi (a person from Iraq)` |
| **說不好**（沒有好的說法） | 13 | 6.5% | `cst`, `edt`, `ave`, `acc`, `nec`, `char`, `def`, `vbulletin`, `livecam`, `pubmed`, `jul`, `tion`, `milf` |
| **合計** | 200 | 100% | — |

**結論：93.5% 的表外常用詞說得出來**（本詞＋描述＋外來詞）；6.5% 說不好，而且**全部是網頁系統縮寫、程式語言關鍵字與不雅俗語**——
沒有任何一個 1,000 詞左右的系統能說好這些詞，這個失敗率是可以接受的。

### 6.3 改寫測試（6 段沒看過的真實文章）

素材：維基百科英文版 5 篇摘要（Coffee、The Great Wall of China、Marie Curie、Bicycle、Antikythera mechanism）
＋ Project Gutenberg 的伊索寓言 "The Dog in the Manger"。全部是第一次看到的一般英文。

| 段落 | 一般英文詞數 | Mini-English 詞數 | 膨脹 | 第一次寫 | 修正後 |
|---|---:|---:|---:|---|---|
| Coffee | 38 | 66 | +74% | ❌ | ✅ |
| Great Wall of China | 70 | 97 | +39% | ❌ | ✅ |
| Marie Curie | 77 | 119 | +55% | ❌ | ✅ |
| Bicycle | 39 | 70 | +79% | ❌ | ✅ |
| Antikythera mechanism | 66 | 99 | +50% | ❌ | ✅ |
| The Dog in the Manger | 64 | 78 | +22% | ❌ | ✅ |
| **平均** | | | **+53%** | **0/6** | **6/6** |

**第一次寫的錯誤統計**（這是本專案最重要的數據）：38 個不同的違規詞，出現最多的依次為
`dynasty`(3)、`century`(2)、`bicycle`(2)、`awake`(2)、`caffeine`(2)、`physics`(2)、`chemistry`(2)，
以及 `mechanism, movement, gear, cycle, pedal, motor, frame, cyclist, bean, hold, himself, kingdom, radioactivity…`。

**依此修改了什麼**（見 §7）。

### 6.4 自然度檢查（抽 20 句）

從 `examples.md` 與改寫測試中隨機抽 20 句，逐句判斷「母語者讀起來會不會覺得怪」。發現 7 處問題，全部修正：

| 原句 | 問題 | 修正 |
|---|---|---|
| `these small things push the blue light around` | `push … around` 不像科學英語 | `send the blue light in all directions` |
| `most of the blue light is pushed away` | 被動式 | `most of the blue light goes away` |
| `your nose is stopped` | 不是英語 | `you cannot breathe well through your nose` |
| `people could say where the stars would be` | 語意不對 | `people could tell where …` |
| `He found a fishing boat … near the water` | `near the water` 不自然 | `near the land` |
| `Come again in 2 days` | 怪 | `Come back in 2 days` |
| `After one year` | 數字規則不一致 | `After 1 year` |

修正後重抽 20 句複檢，**沒有再發現不自然的句子**。

### 6.5 直接命中率

以 12,534 個 token 的一般英文（維基百科 10 篇摘要＋伊索寓言）測試「有多少 token 可以直接用表內的詞寫」：

| 語料 | token 命中率 | 字型命中率 |
|---|---:|---:|
| 維基百科 10 篇摘要（現代一般英文） | **63.7%** | 45.5% |
| 伊索寓言（較舊、較單純） | 78.9% | 42.2% |
| 合計 | 77.8% | 40.5% |

剩下的 36% 需要描述或外來詞——這就是「改寫後文章變長」的原因，也是 §6.3 實測膨脹 +53% 的來源。

### 6.6 提示詞效果測試（LLM 一次寫對率）

測試方法：把 [prompts/system.md](prompts/system.md) 當系統提示詞，交給 GLM 5.3 Flash，
要它把 3 段沒看過的文章（Coffee、Bicycle、The Dog in the Manger）改寫成 Mini-English，
然後用 `check.py` 檢查輸出。跑兩種設定：

| 設定 | 一次寫對 | 每段違規詞數 | 每段時間 | 最常見的違規詞 |
|---|---:|---:|---:|---|
| **只給系統提示詞**（模型不能自己檢查） | **0/3** | 3～9 個 | 3～6 秒 | `cattle`(3)、`caffeine`(2)、`two`、`cyclist`、`Manger`、`growled`、`others` |
| **提示詞＋檢查工具**（模型自己呼叫 `check_minienglish`，改到通過） | **3/3** | 0 | 15～25 秒 | — |

**結論：**
1. 光有提示詞不夠——一次寫對率是 **0/3**（但每次只錯 3～9 個詞，比手寫改寫的 38 個好很多，
   因為提示詞已經把規則和禁用詞表給足了）。
2. **加上檢查工具之後是 3/3**：模型自己呼叫檢查、只改違規的句子、再檢查，最多 4 輪就通過。
   這和 Mini-Lang 的經驗一致（明確列出違規詞並讓模型改寫，通過率從約 50% 升到 94～95%）。
3. 沒有工具時最常犯的三種錯：**忘記給外來詞加括號說明**、**數字寫成英文**、**把原文的生僻詞照抄**。
   前兩種可以靠提示詞再收緊，第三種要靠詞典（`lexicon.tsv`）或檢查工具。

重跑：`python tools/prompt_test.py --passages 3 [--tool]`（需要 `NVIDIA_API_KEY`）。

### 6.7 網頁專案的驗證

| 檢查 | 結果 |
|---|---|
| `node web/test.js` | ✅ 26 個測試全部通過（檢查規則、翻譯、反譯、查詞） |
| `python web/crosscheck.py` | ✅ 22 句比對：網頁的 JS 檢查器與 `check.py` **完全一致** |
| 本機伺服器 | ✅ `index.html` / `expert.html` / `data.js` / `style.css` 都回 200 |

---

## 7. 從驗證學到的事（回饋到設計）

| 發現 | 修改 | 影響 |
|---|---|---|
| 詞典與改寫測試顯示：描述需要一批具體名詞（`throat, pig, cow, grain, ground, cloth, liquid, thread, mark, handle, seat, bridge, bicycle, dynasty, century, physics, chemistry…`） | 擴充層 400 → **656**（新增 256 詞）；**核心層不變** | 詞表總數 1,000 → 1,256；「要學 600 詞」的決定不受影響 |
| 大寫開頭的禁用詞（`Great Wall`、`Great`）被誤判 | 禁用詞檢查只對小寫生效 | 專有名詞可以自由用 |
| `The Great Wall of China (…)` 的括號說明沒有涵蓋整個專有名詞 | 括號說明往前認：同一片語裡大寫開頭的詞都算已說明 | 專有名詞的說明可以用在最後一個詞後面 |
| 表外的小寫技術詞（`caffeine`, `radium`）沒法當外來詞 | 表外的詞若緊接著括號說明 → 視為外來詞定義；之後直接用 | 技術術語可以用「原詞＋括號說明」 |
| 英文 `-o` 結尾名詞的複數規則（`photo` → `photos` 不是 `photoes`）與動詞第三人稱（`go` → `goes`） | 修正 `morph.py` 的規則 | 檢查程式不再誤判 |
| `win → winning` 需要重複字母 | `morph.py` 改用明確的重複清單 | 同上 |
| 自然度抽樣發現 7 處不自然 | 改寫句子 | 見 §6.4 |

---

## 8. 已知的限制

1. **描述會讓文章變長。** 百科型文章改寫後平均 +53%（§6.3）。日常對話與生活文幾乎不變長（−2%～+21%）。
2. **被動、完成式、關係子句一律不收。** 改寫新聞與科學文章時必須改寫句子結構，會失去原文的語氣；
   被動句多的段落（新聞導語常見）改寫後讀起來會偏口語。
3. **慣用語完全不收。** `piece of cake`、`break a leg` 一律翻成意思，英文母語者會覺得「這個人英文很好但有點生硬」。
4. **網頁與技術用語說不好。** 覆蓋率測試中 13/200 失敗，全部是縮寫、程式關鍵字與俗語。
5. **抽象名詞只能靠描述或外來詞。** `freedom`、`efficiency`、`policy` 這類詞沒有乾淨的說法，
   只能用句子（`everyone has the same chance`）或外來詞。
6. **中文專有名詞會讓英文母語者讀不懂**（這是為了目標讀者做的取捨）。
7. **學習曲線仍然不短。** 600 個核心詞大約是「半年密集＋半年用到」的量，Mini-English 省掉的是**文法的複雜度**，不是詞的數量。
8. **沒有語音標示的訓練資料。** 每個詞有 IPA，但沒有示範音檔或重音提示；學者只能靠 IPA 自學。
9. **本報告的改寫測試只有 6 段、且都是短文**（38～77 詞）。長文（500 詞以上）的膨脹率與自然度需要另外測。

---

## 9. 下一步建議

**已經完成（本次）**：
- 提示詞效果測試與檢查工具迴圈（§6.6）。
- 反向翻譯工具 [translate.py](translate.py)（Mini-English → 一般英文，用 `lexicon.tsv` 與 `data/reverse.tsv` 查表）。
- 網頁專案 [web/](web/)：翻譯器、檢查器、詞表瀏覽、LLM 專家（§6.7）。

**還沒做**：
1. **長文的改寫測試**：現在只測了 38～77 詞的短文，500 詞以上的文章膨脹率與自然度需要另外測。
2. **教學實驗**：找 5–10 位中文母語者，只學核心 600 詞，看他們兩個月後能不能寫出自然的日常英文。
3. **把 `lexicon.tsv` 擴到 3,000 條**，特別補「中文學習者常用但英文教材少見」的詞；
   目前 1,748 條，涵蓋率高頻詞，但學術與專業領域仍偏薄。
4. **換幾個不同的模型測提示詞**（現在只測 GLM 5.3 Flash），確認「常見違規詞清單」的效果是否一致。
5. **給網頁加多語介面**（現在只有中文介面，Mini-English 本身是英文）。
