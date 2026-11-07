# Mini-English 設計文件（第 1 階段：調查與提案）

> 狀態：第 1 階段完成，等你確認後才寫完整詞表。
> 本文件說明：現有方案的調查結果、n 的提案、「詞」的定義、分類、選詞方法、三層表達與語法的骨架。
> 完整詞表、語法規則、check.py 在第 2 階段交付（`mini-english.md`、`check.py`）。

## 0. 檔案位置與流程

| 檔案 | 內容 | 階段 |
|---|---|---|
| `mini-english/design.md` | 本文件：調查與提案 | 1 |
| `mini-english/mini-english.md` | 規格：設計原則、詞表、語法規則、附錄完整詞表 | 2 |
| `mini-english/check.py` | 檢查程式（讀 `mini-english.md` 的附錄） | 2 |
| `mini-english/lexicon.tsv` | 1,000+ 常用英文詞的 Mini-English 說法 | 3 |
| `mini-english/examples.md` | 6+2 段翻譯範例與長度比較 | 3 |
| `mini-english/prompts/system.md` | 給 LLM 的系統提示詞 | 3 |
| `mini-english/report.md` | 設計報告與驗證結果 | 4 |

放在 `english/mini-english/`（對照 `chinese/mini-lang/`），`english/doc/` 留給說明文件。

---

## 1. 現有方案調查

### 1.1 比較表

| 方案 | 詞數 | 語法限制 | 產出是自然英文？ | 詞表外的詞怎麼處理 | 已知問題 |
|---|---|---|---|---|---|
| **Basic English**（Ogden & Richards, 1932） | **850 個詞根** = 400 一般名詞 + 200 可視物體 + 100 形容詞 + 50 反義對 + 100 operators；另有 ~180–200 個「國際詞」 | 10 節語法；16 個 operators + 7 個代詞；正常英語語序；可自由屈折 | 目標是自然，但結果被批評為不自然 | **大量改寫**（I made an attempt to come）；國際詞＋數字貨幣保留英文形式；技術術語加引號再用 Basic 詞解釋 | Flesch (1944)《Harper's》「It's not basic, and it's not English」；選詞「任意」；無實證；Hall Jr./Lauwerys (1966)《Basic English: A Protest》；Shannon: 高冗餘 |
| **Globish**（Nerrière, 1989 提案 / 2004 定稿 / 2009 修訂） | **1,500**（Globish Foundation, 2011）+「國際與特殊詞」 | 無編號規則表；26 步教學；短句、正面陳述、避免插入語、always use "that" | 是（自稱 "perfectly correct English"） | 派生與複合（un-/re-/pre-、-ity/-ness/-able/-ly）；複合名詞 work man、bed room | Grzega：無任何實證觀察；商標化、商業化；文化帝國主義批評；句式偏機械 |
| **VOA Learning English / Special English**（1959– ） | **~1,500**（2018 版 Word Book 實測 1,526 個 headword） | 無成文語法；短句、無成語、1/3 慢速、主動語態 | 部分（編輯寫的簡化英語） | 明確允許超出詞表，但要用詞表詞說明意思 | 「簡化 vs 樸素」的分寸；廣播體，不是自由寫作；美式發音中心 |
| **Simple English Wikipedia** | 目標 ~1,500，實際 2,000；**沒有強制清單** | 無強制；主動語態、避免成語與縮寫 | 是（明確目標） | 分級階梯 BE850 → BE1500 → VOA1500；括號註解；偏好古英語詞（sweep 而非 sweep-perspiration） | 實測：讀懂一半句子仍需 ~18,000 詞（英文維基 ~39,000）——軟清單控制不了難度 |
| **New GSL**（2013, v1.2 2023） | **2,809 lemmas / 2,368 word families**，覆蓋 92% 日常英語 | 無（純頻率表） | — | — | 5.7% 是功能詞，但功能詞承載 ~33% token |
| **Oxford 3000 / 5000** | **3,000 / 5,000**，CEFR 分級 | 無 | — | — | 教學 curated，不是原始頻率表；OALD 全書用它 |
| **Toki Pona**（2014 / 2021） | **120–125**（lipu pu）；**137**（lipu ku, 2021） | 無編號規則；SVO、頭首；14 音素 | **不是英文，是另一種語言** | 靠複合與修飾，不靠詞表 | 刻意犧牲表達力；不是 IAL |
| **ASD-STE100**（2025 Issue 9） | **~900 核准詞** | **53 條寫作規則**；禁被動、禁輔助動詞堆疊、句長 ≤20/25 詞 | **不是**（刻意機械） | 逐詞替換表 | 只適用技術文件 |
| **Plain English**（Gowers 1948 / 英國 Plain English Campaign 1979） | **沒有固定清單**，只有編輯規範 | 散文規則 | **是**（重點） | 用白話取代行話 | 沒有詞數上限 → 無法保證難度 |
| **BGE**（Grzega 2005– ） | 750 + 250 自選 | 20 條初級規則；允許不規則動詞 | 部分 | — | 是 Globish 最嚴厲的批評者 |

### 1.2 從調查得到的 5 條教訓（直接決定本設計）

1. **自然度是硬限制。** 所有存活的「受控英語」（STE、E-Prime、Seaspeak）都是文件語言，母語者讀起來彆扭；所有以「自然」為目標的受限英語（Basic English、Globish）都失敗了。**Mini-English 因此只限制「選詞」，不改造「語法」**：語法就是正常英語，Mother tongue 不會覺得怪。
2. **改寫 + 偏好日常詞，比自造句法有效。** Basic English 自己的例子（blood, hard work, drops from eyes, and body water vs blood, toil, tears, and sweat）證明：符合清單的改寫可能比原文更難懂。→ 描述要自然，優先用「常用、具體」的說法。
3. **功能詞是剛需，而且必須完整。** 實測英文 token 中 **32.6%** 是功能詞；前 100 個高頻詞裡 86.7% 是功能詞。功能詞缺一個，壞掉的是**文法**不是意思。→ Mini-English 的文法層（~200 個）必須一次給齊。
4. **純頻率表不管用。** NGSL 2,809 個詞覆蓋 92% token，但那是「讀懂」不是「用自然英文寫」。→ 選詞看表達力，頻率只用來排序與驗證。
5. **句長目標 15–20 詞。** 新聞散文句子中位數 >15 詞（Kornai）；VOA/STE 把下限壓到 12–20。→ Mini-English 的改寫句長目標 12–18 詞。

---

## 2. 設計目標

| 目標 | 做法 | 驗證方式 |
|---|---|---|
| 學會 n 個詞 + 20 條規則後能說日常話 | 6 大生活場景的 5 段對話 + 短文全在核心層 | examples.md 對話全部通過 check.py |
| 能把一般文章改寫成 Mini-English | 三層表達（本詞 / 描述 / 外來詞）+ 描述模板 | 改寫測試（第 4 階段） |
| 能讀懂別人寫的 Mini-English | 附錄詞表 + 描述模板 + 外來詞註解慣例 | 讀測（第 4 階段） |
| 寫出來就是自然、正確的英文 | 語法=正常英語；描述用自然短語；不做 Chinglish | 自然度抽樣 20 句（第 4 階段） |
| 全部可程式檢查 | 附錄是唯一權威詞表，check.py 逐詞檢查 | check.py 自我檢查 + 全部交付物通過 |

---

## 3. 「詞」的定義（決策 D1–D5）

這是整個設計的地基，因為英文有形態變化，中文沒有。

### D1. 計數單位 = 詞元（lemma）

一個「詞」= 字典的一個原形（headword），在 n 裡只算 1 個。例：`go` 算 1 個，`goes / went / gone / going` 不另外算。

**理由：** 學習者背的是「一個概念一個形」，屈折形式是規則產生的，不該收進 n。

### D2. 屈折形式：收，免費（同一個詞）

允許的屈折（自動接受，不列入 n）：

| 形式 | 用例 |
|---|---|
| `-s / -es` | 複數、第三人稱單數（boxes, watches, goes） |
| `-ed` | 過去式、過去分詞（worked, waited） |
| `-ing` | 現在分詞、動名詞（working, eating） |
| `-er` | 比較級（bigger）、-agent 名詞（worker, teacher） |
| `-est` | 最高級（biggest） |
| `-ly` | 副詞（quickly） |
| `'s` | 所有格（Tom's book） |

**保留的不規則屈折**（列在附錄，逐條列，因為無法用規則生成）：
- 不規則動詞：只保留「我們確實要用的那些動詞」的不規則形，例如 `go/goes/went/gone/going`、`eat/ate/eaten`、`buy/bought`、`see/saw/seen`、`say/said`、`make/made`、`take/took/taken`、`come/came`、`give/gave/given`、`know/knew/known`、`think/thought`、`write/wrote/written`、`read/read/read`、`find/found`、`lose/lost`、`meet/met`、`pay/paid`、`send/sent`、`tell/told`、`hear/heard`、`keep/kept`、`leave/left`、`feel/felt`、`put/put`、`cut/cut`、`hit/hit`、`cost/cost`、`sit/sat`、`stand/stood`、`win/won`、`wear/wore`、`grow/grew/grown`、`drive/drove/driven`、`ride/rode/ridden`、`fly/flew/flew`、`speak/spoke/spoken`、`break/broke/broken`、`choose/chose/chosen`、`forget/forgot/forgotten`、`understand/understood`、`bring/brought`、`catch/caught`、`fall/fell/fallen`、`throw/threw/thrown`、`wake/woke/woken`、`sleep/slept`、`drink/drank/drunk`、`run/ran`、`swim/swam`、`sing/sang`、`begin/began/begun`、`become/became`、`build/built`、`burn/burnt`、`buy/bought` 等。
- 不規則複數：`child/children`、`man/men`、`woman/women`、`foot/feet`、`tooth/teeth`、`person/people`、`mouse/mice`、`knife/knives`、`wife/wives`、`life/lives`、`half/halves`、`shelf/shelves`、`wolf/wolves`、`thief/thieves`、`potato/potatoes`、`tomato/tomatoes`、`hero/heroes`、`city/cities`、`baby/babies`、`story/stories`、`country/countries`、`family/families`、`party/parties`、`lady/ladies`。
- 不規則過去分詞（做被動式替代用）：`done, seen, given, taken, written, spoken, broken, chosen, forgotten, understood, driven, ridden, grown, flown, drunk, sung, swum, begun, become, built, lost, found, told, held, kept, left, felt, heard, paid, sent, met, sat, stood, won, worn, cut, hit, put, read`。

**理由：** Mini-English 必須是正確英文，不能把 `went` 寫成 `goed`。所以不規則形式只能「記下來」，不能「改寫」。控制負擔的方法是：**能用規則過去式的動詞就不用不規則動詞**（例如用 `ask` 不用 `interrogate`、`use` 不用 `employ`），並讓描述模板填補差額。

### D3. 派生形式：只允許 3 個字尾、2 個字首（白名單）

| 字首 | 意思 | 例 |
|---|---|---|
| `un-` | 否定 | `unhappy`, `unclear`, `unusual` |
| `re-` | again / back | `redo`, `reopen`, `rewrite` |

| 字尾 | 意思 | 例 |
|---|---|---|
| `-er` | 做某事的人 / 某種東西 | `worker`, `teacher`, `runner` |
| `-ly` | 副詞 | `quickly`, `carefully` |
| `-ness` | 性質名詞（只給少數基礎詞） | `kindness`, `sadness` |

**不允許** `-tion, -ment, -ity, -ance, -ous, -ive, -ful, -less, -ize, -ise` 等：這些會大量製造「聽起來像英文但沒學過」的詞，學習者讀到會卡住，而且長度失控。→ 這類概念走**描述**（例如 `the thing that can help you write a letter` → 不行，太長 → 用外來詞或改用其他說法）。

**理由：** 派生規則是「免費」的表達力來源，但白名單越大，讀者碰到沒學過的詞的機率越高。3 個字尾 + 2 個字首是經驗值：`-er` 與 `-ly` 幾乎涵蓋日常對話所需；`-ness` 只用於少數情緒詞。

### D4. 複合詞：收，但列為正式詞（計入 n）

`bedroom`、`bus stop`、`coffee shop` 這類要看得出組成的複合詞收進詞表，因為它們在日常對話中出現率高，且「學會組成規則」比「背 300 個複合詞」划算。

**但是：複合詞必須逐個列在附錄**（check.py 只認清單裡的形狀），所以它跟一般詞一樣計入 n。

**限制規則：** 只收「A + B」而 A、B 都在表內、而且這個複合詞本身就是一個常用詞的；不收臨時自造的複合詞（`paper-surgery-table`）。

**替代方案（如果你要更嚴格）：** 完全不收複合詞，一律用「A 的 B」（a room for sleep）或拆成兩個詞（the room where I sleep）。→ 見第 12 節決策 Q2。

### D5. 片語動詞與慣用語：不進 n，改用「動詞 + 介系詞」或單一動詞

| 片語動詞 | Mini-English 寫法 |
|---|---|
| give up | stop（放棄做某事） |
| look for | want（想找到）/ find |
| put on | wear（衣服） |
| take off (plane) | fly away / leave |
| pick up | take（拿起） |
| find out | know（知道結果） |
| get up | stand up（起床） |
| sit down | sit（坐下來 — 英文 sit 本身就是坐下） |
| turn off | stop（關掉 — 上下文會說明是機器） |
| break out | start suddenly（用兩個詞說明） |
| look after | watch（照看） |

**例外清單（不計入 n，另列，約 12 個）：** `look for`, `put on`, `take off`, `get up`, `get off`, `get in`, `get out`, `find out`, `look at`, `look after`, `look for`, `come back`? → 這些在第 2 階段最後確定。

**理由：** 片語動詞是英文學習者最大的記憶負擔（`look for / look after / look at / look out` 意思完全不同），而且很多可以用一個動詞取代。慣用語（`break a leg`、`piece of cake`）直接不收——慣用語對初學者是純負擔，而且 Mini-English 的目標是「說清楚」，不是「說得像本地人」。

---

## 4. n 的決定（決策 D6）

### 4.1 提案：核心 600 詞 + 擴充層 400 詞（合計 1,000）

| 層 | 詞數 | 誰要學 | 內容 |
|---|---:|---|---|
| **核心層** | **600** | 必學 | 文法/功能詞 ~200 + 每日生活內容詞 ~400 |
| **擴充層** | 400 | 學了更方便（選學） | 常用但「描述得出來」的內容詞：weather, computer, science, government, company, market, energy, culture… |
| 例外 | ~12 + 數字 + 單位符號 | — | 片語動詞例外、阿拉伯數字、%、°C、km |

**理由：**

1. **功能詞沒有省。** 英文 token 的 32.6% 是功能詞，前 100 高頻詞 86.7% 是功能詞。文法層 ~200 個（代詞、限定詞、助動詞、介系詞、連接詞、副詞、數量詞）**是底線**，不可壓縮。Basic English 的教訓正是文法太少（只有 16 個 operators + 7 個代詞），結果文法層缺到要另外允許 60 個表外變化。
2. **400 個內容詞能覆蓋「日常生活」**（Mini-Lang 用 297 個漢字覆蓋同一範圍，但漢字承載的語意比英文字詞多）。第 4 階段的覆蓋率測試會用數據驗證這一點。
3. **1,000 詞時的「直接命中率」估算：** 依 Google Web Trillion Word Corpus 實測，top 1,000 高頻詞覆蓋 ~60.6% token；Mini-English 的 1,000 詞不是照頻率挑，但會含掉幾乎所有 top-1,000 裡的表達力強的詞，預估直接覆蓋 **60–68%**，剩下 32–40% 的 token 需靠描述或外來詞。這意味**改寫後長度會膨脹約 1.4–1.8 倍**（第 4 階段實測）。
4. **與 Mini-Lang 的類比：** Mini-Lang 297 字 ≈ 涵蓋 44.6% 一般用字。Mini-English 600 核心詞預估直接涵蓋 ~45–50% token。兩者量級相當，可視為「Mini-Lang 的英文版」。

### 4.2 與其他 n 的比較（取捨理由）

| 方案 | 差在哪 | Mini-English 的取捨 |
|---|---|---|
| **Toki Pona 120** | 詞數最小，但它是另一種語言，且沒有形態 → 談不上「自然英文」 | 我們要 4（自然），所以 n 必然比 120 大一個數量級 |
| **Ogden 850** | 內容詞 700 / 文法詞 100，重心錯了；被批評不自然 | 我們 **600 = 文法 200 + 內容 400**，文法層翻倍，內容層靠描述補；再用擴充層補回內容詞 |
| **Basic English 1,500 / Globish 1,500 / VOA 1,500** | 廣播與服務用途，允許表外詞、不管自然度、不管學得會不會 | 我們把「學得會」當硬約束：核心 600 是成人初學者可完成的量 |
| **NGSL 2,809 / Oxford 3,000** | 純頻率表，覆蓋高但表達力與自然度不保證 | 我們的表達力選詞法會保留一些低頻但高表達力的詞（`tool`, `machine`, `sound`, `shape`…），這些是描述模板的骨架 |

### 4.3 如果你想改 n（見第 12 節 Q1）

| 選項 | 核心 / 擴充 | 效果 |
|---|---|---|
| A（提案） | 600 / 400 | 每天學 10 個詞，2 個月學完核心 |
| B | 500 / 300（總 800） | 更省，但改寫會更冗長、描述更多 |
| C | 700 / 500（總 1,200） | 覆蓋更好，但學習負擔明顯上升 |
| D | 單層 800 | 少一層好管理，但無法區分「必學」與「選學」 |

---

## 5. 分類（詞表的骨架）

沿用 Mini-Lang 的 9 類，英文版調整如下（括號內是預估字數）：

| 類別 | 預估 | 內容 | 英文版特有的調整 |
|---|---:|---|---|
| **1. 代詞・指示** | 40 | I/you/he/she/it/we/they + me/him/her/us/them + my/your/his/her/its/our/their + this/that/these/those + someone/everyone/something/everything/nobody/nothing + who/what/which/whose | Mini-Lang 只有 15 個；英文需要完整代詞系統（第三人類別只能用 he/she/it，不能像中文只留「他」） |
| **2. 語法（功能詞）** | 165 | be 全部形式、do/does/did、have/has/had、will/can/could/must/should/may/might、not/no/yes、and/or/but/if/because/so/than/as、very/too/also/just/still/only/even/almost/always/never/often/sometimes/usually/again/soon/now/then、in/on/at/to/from/of/for/with/about/by/during/between/among/into/without/against/toward/under/over/above/below/behind/around/across/along/near、there/here、some/any/all/every/each/both/either/neither/many/much/few/several/most/more/less/other/another/such/same/own、first/second?/last/next/half/whole | 英文的文法層比中文大得多：所有介系詞都要有，且 be/do/have 的形式要列全 |
| **3. 數量・比例** | 25 | 阿拉伯數字 + a/an/the、each/every、one?、few/several/many/much、half/double、dozen?、percent、more/most、all/most/some | 數字全部用阿拉伯數字；保留的量詞見第 9 節 |
| **4. 時間** | 40 | time/day/week/month/year/hour/minute、morning/afternoon/evening/night、today/tomorrow/yesterday/now/then/before/after/early/late/always/never/often/sometimes/usually/already/still/soon/again/until/ago/birthday/holiday/weekend/season/spring/summer/autumn/winter/clock | 增加 clock, minute, second, since(=from) |
| **5. 方位・地點** | 70 | place/house/home/room/door/window/floor/wall/road/street/city/town/country/world/shop/store/market/restaurant/hotel/station/airport/school/office/hospital/bank/park/library/museum + north/south/east/west/left/right/front/back/near/far/above/below/inside/outside/behind/around/map/sign/way/street/corner | 增加 corner, way（描述模板需要） |
| **6. 動作** | 130 | 日常動詞：go/come/walk/run/sit/stand/eat/drink/sleep/read/write/speak/say/tell/ask/answer/look/see/watch/hear/give/take/get/put/make/buy/sell/pay/open/close/start/stop/wait/work/play/study/learn/teach/help/use/find/lose/keep/send/bring/move/turn/change/grow/live/die/meet/visit/drive/fly/cook/wash/clean/cut/fix/wear/feel/hurt/need/want/try/like/love/hate/begin/finish/choose/decide/hope/wish/remember/forget/know/think/mean/happen/become/stay/leave/arrive/return/call + 高階動詞 add/allow/include/need/offer/support/show/cause/affect/change/increase/decrease/prepare/complete/continue/compare/notice/believe | 需要一批「抽象動詞」才能描述文章（新聞、科普） |
| **7. 性質** | 90 | good/bad/big/small/long/short/tall/high/low/old/new/young/hot/cold/warm/cool/wet/dry/easy/hard/simple/important/different/same/right/wrong/true/false/real/nice/fine/free/busy/happy/sad/angry/tired/hungry/thirsty/sick/healthy/strong/weak/heavy/light/fast/slow/beautiful/ugly/afraid/fun/interesting/boring/possible/clear/ready/sure + 顏色 red/blue/green/yellow/black/white/brown/gray/orange/pink/purple | 顏色只收 8 個基本色 + pink；purple = red-blue color（用描述） |
| **8. 事物** | 130 | food/water/rice/bread/meat/fish/egg/milk/tea/coffee/juice/fruit/apple/vegetable + 身體 head/hair/eye/ear/nose/mouth/tooth/tongue/neck/shoulder/arm/hand/finger/leg/foot/knee/back/heart/stomach/skin/bone/blood + 衣物 shirt/pants/dress/coat/shoes/hat/socks + 家具 table/chair/bed/sofa/lamp/cup/bowl/plate/knife/fork/spoon/bottle/box/bag/paper/book/pen/phone/computer/key/money/card/ticket/map/sign/clock/calendar/picture/medicine/bill/glass/mirror/towel/umbrella/radio + 交通 car/bus/bike/train/plane/boat/taxi/subway + 抽象 thing/person/place/kind/way/part/piece/group/system/tool/machine/material/sound/voice/language/word/letter/number/shape/size/level/degree/reason/result/problem/question/answer/idea/plan/story/news/article/report/study/work/job/meeting/rule/law/company/team/game/sport/music/art/science/history | 尾巴的「抽象頭部詞」是**描述模板的骨架**，一定要收（這是 Mini-Lang「類頭」的英文版） |
| **9. 社交・人** | 50 | hello/hi/goodbye/bye/thanks/please/sorry/excuse me/welcome/name/meet/friend/family/mother/father/parent/brother/sister/child/son/daughter/husband/wife/baby/grandmother/grandfather/uncle/aunt/cousin/teacher/student/doctor/nurse/worker/boss/customer/person/man/woman/guy/lady/people/everyone/somebody/stranger/guest/neighbor | 加上 Mini-Lang 對應的「稱呼、問候、道謝」 |

**合計估計：740**（含擴充層的部分）。核心層會先挑 600 個，其餘 140 放擴充層，最後視覆蓋率測試再調整。

---

## 6. 選詞方法

### 6.1 入選 4 條件（全部滿足才收）

1. **缺口（Describability Gap）**：現在的詞表描述不出來，或只能用很長的描述說出來。
   量測：這個詞在 `lexicon.tsv`（1,000 個常用詞）裡，現在用「描述」要花幾個詞？≥6 個詞的描述 → 缺口大。
2. **組合力（Generative Power）**：加了之後，能和現有詞組出很多有用的說法。
   量測：這個詞能作為描述模板裡的**類頭**（thing/person/place/tool…）、**形容詞修飾**、**動詞**或**類別名**，且能覆蓋多個概念。
3. **自然度（Naturalness）**：用這個詞造出的句子，母語者讀起來不怪。
   量測：寫 3 個例句給自己看；不像英文就刪。
4. **可用性（Utterability）**：學習者真的用得到，且沒有更簡單的說法可以取代。

### 6.2 刪除 3 條件（任一成立就刪）

1. **同義詞**：一個概念只留一個詞（`large` → `big`；`huge` → `very big`；`purchase` → `buy`）。
2. **能輕鬆改寫**：可以用 3 個以內的表內詞說出來（`hospital` → `a place where doctors help sick people` → 刪）。
3. **長尾罕見**：只在專業領域出現（`hemoglobin`, `kilowatt`）→ 外來詞處理。

### 6.3 頻率怎麼用

頻率**不用來決定收不收**，只用來：
- **排序**：核心層 600 詞的先後順序（先學高頻的）。
- **驗證**：把覆蓋率測試的 200 個抽樣詞和 `lexicon.tsv` 的 1,000 詞分開，避免自我循環。
- **刪除信號**：如果一個詞頻率很高但我們刪了它，報告裡要寫明替代說法（這是報告的要求）。

### 6.4 與 Mini-Lang 選字法的對照

Mini-Lang 的兩個指標（缺口 / 組合力）直接沿用（見 `chinese/doc/charset-expansion.md`）。英文版新增第 3 個指標「自然度」，因為英文是母語者的母語，詞選錯會直接被聽出來。Mini-Lang 用 4 萬個中文詞頻表算組合力；英文版用 **Oxford 3000 + NGSL + 常用詞表** 當候選池，再用手工判斷。

---

## 7. 三層表達法

### 7.1 三層

| 層 | 什麼時候用 | 例子 |
|---|---|---|
| **本詞** | 概念在表內 | `doctor`, `bus`, `hungry` |
| **描述** | 表外的一般概念（可描述出「是哪一類」） | `the place where doctors help sick people` |
| **外來詞** | 表外的專有概念（說不出是哪一個：人名、地名、物種、品牌、術語） | `Paris (a big city in France)`, `COVID-19 (a disease that came from an animal)` |

### 7.1b 外來語層的通則（依你的說明推廣）

Mini-Lang 的第三層是「英文原字」：`Beijing (a big city in China)`。同一個通則推廣到 Mini-English：

> **第三層 = 這個概念「本來的名字」，用原文寫，第一次出現時加括號說明。**
> 對 Mini-English 而言，概念的本名通常就是英文，所以第三層＝**直接用表外的原英文詞**。

| 情況 | Mini-English 寫法 | 括號說明 |
|---|---|---|
| 人名 | `Anna (a woman who works with me)` | 說明只能用 Mini-English 詞 |
| 地名 | `Paris (a big city in France)` | 同上 |
| 物種 | `panda (a black and white animal from China)` | 同上 |
| 品牌 | `Toyota (a company that makes cars)` | 同上 |
| 專門術語 | `COVID-19 (a disease that started in 2019)` | 同上 |
| 沒有名稱但只有一行之差的概念 | `shampoo (a thing you use to wash your hair)` | 同上 |

**要點：**

1. **括號說明是唯一允許「括號裡的東西不是英文」的例外**——說明本身必須全部由 Mini-English 詞組成（check.py 會檢查）。
2. **不影響自然度**：括號註解在一般英文裡也是標準做法（`Paris (a city in France)`），母語者不會覺得怪。
3. **後續沿用**：同一篇文章中第二次出現就直接用原詞，不再加括號（「先定義、後沿用」）。

**待決定的子情況（Q4）：** 目標讀者是中文使用者，所以中文專有名詞可以選擇「直接用中文寫」，
例如 `上海 (a big city in China)`、`王教授 (a teacher at my school)`。
這和 Mini-Lang 寫 `Beijing` 一模一樣的邏輯（用讀者熟悉的文字），對中文讀者更友善，但會讓英文母語者讀不懂。
→ 建議：**英文原名優先，中文原名只在本國地名/人名第一次出現時允許**（因為 Mini-English 也要讓英文母語者讀得懂，目標 3）。

### 7.2 描述模板（固定 7 種）

描述 = **修飾語 + 類頭**。類頭是封閉清單（英文版的「類頭表」）。

| 模板 | 例子 |
|---|---|
| `a [類頭] that ...` | `a thing that you use to cut paper` |
| `a [類頭] for ...` | `a place for seeing a doctor` |
| `a [類頭] with ...` | `a machine with wheels that goes on the road` |
| `a [類頭] in ...` | `a thing in the sky that moves at night` |
| `a [類頭] of ...` | `a word for the sound of water` |
| `a [類頭] who ...`（只給 person） | `a person who helps a doctor` |
| `a [類頭] like ...` | `a color like the color of the sun` |

**類頭封閉清單（初版，約 30 個）：**
`thing, person, place, kind, way, part, piece, group, system, tool, machine, material, food, drink, animal, plant, language, word, letter, number, shape, size, level, degree, reason, result, problem, question, answer, idea, plan, story, news, article, report, study, work, job, rule, law, company, team, game, sport, music, art, science, history, feeling, idea`

> 這些詞本身就是 Mini-Lang 的「類頭表」（對應中文版的 28 個類頭），它們**必須在核心層**。

### 7.3 先定義、後沿用

- **外來詞**：第一次出現時加括號說明，說明本身只能用 Mini-English 詞 → `Paris (a big city in France)`。之後直接用 `Paris`。
- **描述**：描述本身是自足定義，不需要括號。但如果同一個概念在文章裡出現 3 次以上，可以先給它一個短名：
  > `I have a health card (a card from my company that pays for the doctor). I use my health card every year.`
- **括號說明裡的詞也要檢查**（check.py 會檢查）。

### 7.4 描述的品質規則（自然度關鍵）

1. **描述要短**：盡量 ≤10 個詞。超過就改用外來詞。
2. **描述要能分辨同類的東西**：`doctor` = `a person who helps sick people`；`nurse` = `a person who helps a doctor`。
3. **能用常用詞就不用怪詞**：`the place where they sell medicine` 好過 `pharmacy` 的繞路。
4. **不要把抽象名詞硬翻譯**：中文的「和諧」「效率」→ 用句子說（`everyone has the same chance` / `they do more work with less time`），和 Mini-Lang 的「抽象名詞改成句子」原則一致。

---

## 8. 語法：規則骨架（第 2 階段會給完整 18–20 條與例句）

### 8.1 保留（用正常英語語法，不改造）

| # | 規則 | 例句 |
|---|---|---|
| 1 | 主語 + 動詞 + 賓語 | `I eat rice.` |
| 2 | be 動詞：am/is/are/was/were | `I am a student. She was tired.` |
| 3 | 第三人稱單數加 -s/-es | `He goes to work.` |
| 4 | 進行式 be + V-ing | `I am eating rice.` |
| 5 | 過去式（規則 / 保留的不規則） | `I went to work.` |
| 6 | 將來式 will + V | `I will go tomorrow.` |
| 7 | 否定：not / no | `I do not like it. There is no water.` |
| 8 | 是非問句：be/modal/do 提前 | `Are you a student? Do you like it?` |
| 9 | wh- 問句 | `Where do you live?` |
| 10 | 冠詞 a/an/the | `a book`, `the book` |
| 11 | 所有格 `'s` | `Tom's book` |
| 12 | 複數（規則 / 保留的不規則） | `books`, `children` |
| 13 | 形容詞在名詞前，-ly 副詞 | `a big house`, `he runs fast` |
| 14 | 介系詞（全部列在表內） | `in the room`, `with my friend` |
| 15 | 連接：and / or / but / because / so / if…then / when | `I go because I want to see him.` |
| 16 | 比較：more…than / as…as / the most | `He is taller than me.` |
| 17 | 能力與義務：can / must / should / have to | `I can swim. You must wait.` |
| 18 | 數量與量詞：many / much / a few / few / some / all | `many books`, `a little water` |
| 19 | 目的：to + V | `I go to buy food.` |
| 20 | 存在：there is / there are | `There is a book on the table.` |

### 8.2 不收的結構與固定替代

| 困難結構 | Mini-English 替代 | 理由 |
|---|---|---|
| 被動語態 | 主動：`The room was cleaned by Tom.` → `Tom cleaned the room.` | 被動是學習者最常出錯的結構；而且主動更自然 |
| 完成式 | 過去式 + `already` / `before` / `yet` / `since`：`I have eaten.` → `I ate already.` | 簡單、可預測；語意幾乎等價 |
| 關係子句（which/who 從句） | 描述 + 拆句：`The man who came is my uncle.` → `That man came. He is my uncle.` | 從句是中文母語者最難的結構；拆句仍算自然英文 |
| 虛擬語氣 | `if` + 現在式 + `will`：`If I were rich…` → `If I have money, I will…` | 語意足夠 |
| 間接引語 | 保留 `say that`（that 可省略）：`He said (that) he was late.` | 這個本身不難，保留 |
| 動名詞作主語 | `to + V` 或改成句子：`Using a phone is fun.` → `It is fun to use a phone.` | 避免 `-ing` 開頭的句子 |
| 分詞片語 | 介系詞片語：`a car stopped at the door` → `a car that stopped at the door` | 一致性 |
| 倒裝、強調 (`It is X that...`) | 不收 | 太難 |
| 比較級 of 二者 | `as ... as` | `taller than me` 是可接受的自然英文，保留 |

**結果：Mini-English 的句子結構集合很小，但每一種都是母語者每天在寫的結構。** 這是「自然」與「好學」同時成立的關鍵。

---

## 9. 數字與量詞

- **數字一律用阿拉伯數字**：`1, 2, 3, 100, 2026, 3:30, 20%, $5`。
- **不收**：`one, two, three … twenty, hundred, thousand`（用數字取代）。理由：`one` 作為代詞仍需要（`one of them`），所以 `one` 保留在代詞類。
- **保留的量詞/數量詞**（約 20 個，理由是它們不是「數字」而是「語意」）：

| 保留 | 為什麼 |
|---|---|
| `a / an / the` | 冠詞，必須 |
| `each, every` |  distributive，不能用數字取代 |
| `some, any, all, none, both, either, neither` | 邏輯詞 |
| `many, much, few, a few, several, enough, more, most, less, least` | 量的模糊度 |
| `half, whole, double` | 比例 |
| `first, last, next, second` | 序數（其他序數用 `the 3rd`→`the 3rd`? → 用 `the 3rd` 需要序數字尾，第 2 階段決定） |
| `once, twice` | 頻率 |
| `many` vs `much` | 不可數 vs 可數 |

**判斷準則（沿用 Mini-Lang）：能換成別的數字還說得通的，就是數字，用阿拉伯數字。**

---

## 10. 發音（IPA）

- 每個詞標 IPA，用**單一標準**（建議 General American；英式差異大者（schedule, ask, box）在報告裡註明）。
- 不標變體（不寫 `/ˈæsk/ or /ˈɑːsk/`），只標一個；報告裡說明差異。
- **避免收發音太近的詞**：例如 `quite` / `quit` 同時收會混淆 → 只留 `quite`?（或都不收）；`accept` / `except` 不收；`desert` / `dessert` 不收；`affect` / `effect` 只收 `affect`?（需要 `effect` 名詞嗎？→ 用 `effect` 作名詞描述「影響」）。
- 同一音位差異大但都很常用的（如 `through / threw`）→ 只收 `through`（`threw` 描述成 `past of throw`，但保留不規則形在附錄，不另外計 n）。

---

## 11. 已知風險與取捨（先寫出來，第 4 階段會給數據）

| 風險 | 說明 | 目前的對策 |
|---|---|---|
| **描述爆炸** | 只用 400 個內容詞寫一般文章，描述會到處都是，讀起來像 Basic English 那樣彆扭 | 描述模板限 7 種；描述 ≤10 詞；能用單一詞就不描述；必要時用外來詞 |
| **自然 vs 覆蓋的拉扯** | 越是限制詞表，越不自然 | 設「自然度」為硬約束（6.1 條件 3），並在第 4 階段抽 20 句檢查 |
| **抽象名詞難說** | freedom, efficiency, policy 這類詞 | 用「抽象名詞改句子」原則 + 外來詞 |
| **被動與完成式** | 新聞與科學文章大量使用 | 固定替代（主動 / 過去式 + already） |
| **LLM 一次寫對率低** | Mini-Lang 實測約 50% | 提示詞要附「常見違規詞表」+ 檢查迴圈（把違規詞列給模型改寫，2 輪） |
| **功能詞太多** | ~200 個功能詞背起來枯燥 | 分兩層教學：先學 100 個最高頻的，其餘隨用隨學；核心層內仍算 600 |

---

## 12. 你的決定（第 1 階段結束後已拍板）

| # | 問題 | 你的決定 | 實作方式 |
|---|---|---|---|
| Q1 | n 要多少？ | **A：核心 600 ＋ 擴充 400** | `data/*.tsv` 每個詞有 `C`（核心）／`E`（擴充）標記 |
| Q2 | 複合詞與片語動詞 | **A：複合詞正式收（計入 n）、片語動詞少收** | 複合詞逐個列進附錄（`bus stop`, `bedroom`, `kitchen`…）；片語動詞只留 13 個例外，附錄另列、不計 n |
| Q3 | 描述要多嚴格？ | **B：自由描述，只要詞都在表內** | §3.1 只給「建議骨架」與類頭清單，check.py 只驗證詞、不驗證描述品質；代價寫在 §8 |
| Q4 | 中文專有名詞 | **C：中文原名可以用** | §3.2 明寫 `上海 (a big city in China)`；括號說明仍是規則 |

### 實作後的最終規模

| 項目 | 設計時 | 實作後 | 為什麼變了 |
|---|---:|---:|---|
| 核心層 | 600 | **600** | 沒有變——驗證沒有推翻「要學 600 詞」這個決定 |
| 擴充層 | 400 | **656** | 詞典與改寫測試顯示，描述需要一批具體名詞（`throat, pig, grain, liquid, thread, mark, bicycle, dynasty…`），共 256 個 |
| 總詞數 | 1,000 | **1,256** | 同上 |
| 詞典 | 1,000+ | **1,747 列** | 本詞 216／描述 1,479／外來詞 52 |
| 覆蓋率（200 詞抽樣） | 預估 85% | **93.5%** | 描述模板比預期好用 |
| 改寫膨脹 | 預估 +40～80% | 日常文 +21%、百科文 +53% | 見 `report.md` §6.3 |

## 13. 第 3、4 階段的結果摘要

* **詞典**：`lexicon.tsv` 1,747 列，每一列的 Mini-English 都通過 `check.py`。
* **範例**：`examples.md` 6 段一般英文→Mini-English ＋ 2 段反向，每段附長度比較。
* **提示詞**：`prompts/system.md`（含完整詞表，check.py 驗證與規格附錄逐字一致）＋ `prompts/tasks.md`（任務 A–F）。
* **覆蓋率測試**：200 個表外常用詞 → 38 本詞／122 描述／27 外來詞／13 說不好（**93.5% 說得出來**）。
* **改寫測試**：6 段真實文章，第一次寫 **0/6** 通過；依錯誤補了 256 個詞、修了 4 條檢查規則後 **6/6** 通過。
* **自然度**：抽 20 句發現 7 處不自然，全部修正後複檢通過。



| # | 問題 | 我的建議 |
|---|---|---|

其他我會自行決定、不再打擾你的（會在文件裡說明理由）：
- IPA 用 General American 單一標準。
- 序數：只收 `first`；其他序數用 `the 3rd`? → 需收 `-rd/-st/-nd/-th` 序數字尾（規則字尾，允许）→ 決定：**允許序數字尾**（1st/2nd/3rd/4th），因為是規則的。
- 縮寫：允許 `don't, I'm, it's, that's, we're, they're, he's, she's, can't, won't, isn't, don't` 等基礎縮寫（母語者天天用，寫出來才自然）；但 check.py 要能正確拆解。
- 屬格：`'s` 允許（自然且必要）。

---

## 13. 下一階段（Phase 2）要做的事

1. 產出完整詞表（核心 600 + 擴充 400），每詞：詞、IPA、詞性、中文意思、允許的形式、例子。
2. 產出 20 條語法規則與例句、困難結構替代表、描述模板與類頭表、允許字首字尾表、不規則形式表、片語動詞例外表。
3. 寫 `check.py`：詞元化、縮寫拆解、屈折/派生/複合詞白名單、數字與單位、括號說明、外來詞首次出現須有說明、附錄與表格一致性、自我檢查（重複、表格與附錄相符、所有例句通過）。
4. 用 check.py 檢查 mini-english.md 自己，輸出寫進報告。
