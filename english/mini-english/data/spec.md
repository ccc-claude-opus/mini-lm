# Mini-English：1,256 個英文詞（核心 600 ＋ 擴充 656）

> **Mini-English 是「用 1,000 個英文詞學會英文」的受限英語。** 學會核心層 600 個詞與 20 條語法規則之後，
> 就能說日常生活的話、讀懂別人寫的 Mini-English、把一般英文文章改寫成 Mini-English——
> 而且寫出來的**就是正確、自然的英文**，母語者讀起來不怪。
>
> 本文件是 Mini-English 的唯一規格來源。附錄「完整詞表」是唯一的權威詞表；
> [check.py](check.py)、[lexicon.tsv](lexicon.tsv)、[prompts/system.md](prompts/system.md) 都從那裡讀取。
>
> **第 1 版（2026-11-07）。** 設計調查與取捨理由見 [design.md](design.md)，驗證數據見 [report.md](report.md)。

---

## 1. 設計目標與原則

| 目標 | 做法 |
|---|---|
| 學會 n 個詞就能說日常話 | 6 個生活場景（自我介紹、買東西、問路、看醫生、說感受、講故事）全部只用核心層 |
| 能把一般文章改寫成 Mini-English | 三層表達：本詞 → 描述 → 外來詞 |
| 能讀懂別人寫的 Mini-English | 附錄詞表＋描述慣例＋外來詞先定義後沿用 |
| 寫出來是自然、正確的英文 | **語法就是正常英語**（不改寫語法，只限制選詞）；描述用日常說法 |
| 全部可程式檢查 | check.py 逐詞檢查；所有交付物都通過檢查 |

### 1.1 九條設計原則

1. **選詞看「表達力」與「生成力」，不看詞頻。** 收進來的詞要能描述很多東西（`tool`, `machine`, `thing`, `person`…），
   或能組成很多有用的說法。詞頻只用來排序與驗證，不用來決定收不收。
2. **一個概念一個詞，去掉同義詞。** `large` → `big`；`huge` → `very big`；`purchase` → `buy`；
   `utilize` → `use`；`tiny` → `very small`；`great` → `very good`。
3. **「詞」= 詞元。** 屈折形式免費（`-s/-es, -ed, -ing, -er, -est, -ly, 's`）；
   派生只允許 3 個字尾、2 個字首；複合詞逐個列入；片語動詞只留 13 個例外。
4. **不規則形式照抄。** Mini-English 必須是正確英文，所以 `went` 不能寫成 `goed`：
   不規則形式列在附錄裡，算同一個詞，不另外計 n。
5. **語法盡量少、盡量規則。** 20 條規則涵蓋日常需要；被動、完成式、關係子句、假設語氣不收，改用固定替代。
6. **三層表達法。** 本詞 → 描述 → 外來詞；先定義、後沿用。
7. **數字用阿拉伯數字。** 不學 `one, two, three`；保留 `many, few, several, half, first` 等不可替換的量詞。
8. **發音友善。** 每個詞標 IPA（General American，單一標準）；不收發音容易混淆的詞（`accept/except`、`desert/dessert` 都不收）。
9. **描述優先用日常說法。** 描述要短（≤10 個詞）、要能分辨同類的東西、要像母語者會說的話。

### 1.2 兩層詞表

| 層 | 詞數 | 誰要學 | 內容 |
|---|---:|---|---|
| **核心層** | **600** | 必學 | 語法（功能詞）＋ 日常生活所需的一切 |
| **擴充層** | 400 | 選學，學了更方便 | 常用但能描述、比較專門的詞 |
| 例外 | 13 片語動詞 | — | 不計入 n，見 §4.3 |

**核心層 600 詞怎麼分的：** 語法（功能詞）116、動作 128、性質 74、事物 48、方位 44、社交 34、時間 30、自然 29、抽象 29、代詞 60、數量 8（詳細數字見 §2 的統計表）。
文法層給到 116 個，是因為英文 32.6% 的 token 是功能詞，少一個就會壞掉文法而不只是少一個意思。

**擴充層存在的理由：** 只學 600 詞時，改寫一般文章會出現大量描述，句子會變長；
學了擴充層，很多描述可以換成一個詞，句子短很多、也更像英文。

---

## 2. 詞表

下表是全部 1,256 個詞。**「層」欄**說明這個詞屬於核心層還是擴充層；**「允許的形式」**是這個詞可以寫出來的樣子
（check.py 只接受表裡出現過的形式，加上 §4.1 的規則字首字尾）。

{{SUMMARY}}

{{TABLES}}

---

## 3. 三層表達法

詞表外的概念，用下面三層之一處理。**由上而下**：先試本詞，再試描述，最後才用外來詞。

| 層 | 什麼時候用 | 例子 |
|---|---|---|
| **本詞** | 概念在表內 | `doctor`, `bus`, `hungry` |
| **描述** | 表外的一般概念（能說出「是哪一類」） | `the place where doctors help sick people` |
| **外來詞** | 表外的專有概念（說不出是哪一個：人名、地名、物種、品牌、術語） | `Paris (a big city in France)` |

### 3.1 描述

描述就是**用表內的詞把一個概念說清楚**。規則只有四條：

1. **短**：盡量 10 個詞以內。超過 10 個詞，改用外來詞。
2. **像母語者會說的**：用日常詞。`a place where you buy food` 比 `a commercial establishment for purchasing provisions` 好。
3. **能分辨同類的東西**：`doctor` = `a person who helps sick people`；`nurse` = `a person who helps a doctor`。
4. **先定義、後沿用**：同一個概念在文章中出現 3 次以上，可以先給它一個短名，之後用短名。

**描述的骨架**（建議，不是硬性規則；check.py 只檢查詞，不檢查描述的品質）：

| 骨架 | 例子 |
|---|---|
| `a [類頭] that ...` | `a thing that you use to cut paper` |
| `a [類頭] for ...` | `a place for seeing a doctor` |
| `a [类頭] with ...` | `a machine that moves people and things on the road` |
| `a [類頭] in ...` | `a thing in the sky that moves at night` |
| `a [類頭] of ...` | `a word for the sound of water` |
| `a [類頭] who ...` | `a person who helps a doctor` |
| `a [類頭] like ...` | `a color like the color of the sun` |

**類頭**（描述的最後一個詞，建議從這個清單裡挑，見附錄）：

{{HEAD}}

### 3.2 外來詞

> **外來詞 = 這個概念「本來的名字」，用原文寫，第一次出現時加括號說明。**
> 括號裡的說明只能用 Mini-English 的詞。

| 情況 | 寫法 |
|---|---|
| 人名 | `Anna (a woman who works with me)` |
| 地名 | `Paris (a big city in France)` |
| 物種 | `panda (a black and white animal from China)` |
| 品牌 | `Toyota (a company that makes cars)` |
| 專門術語 | `COVID-19 (a disease that started in 2019)` |

**中文專有名詞**也允許直接用中文寫（目標讀者是中文使用者，這樣最自然）：
`上海 (a big city in China)`、`王教授 (a teacher at my school)`。
括號說明仍然是規則：**第一次出現時必須說明，之後直接用。**

### 3.3 先定義、後沿用

```en
I went to Paris (a big city in France) last year.
The weather in Paris is cold in winter.
```

---

## 4. 構詞法

### 4.1 允許的字首字尾

只有下面這些。**其他字首字尾產生的詞不在表內**，必須改用描述或外來詞。

{{AFFIX}}

### 4.2 保留的不規則形式

因為 Mini-English 必須是正確英文，這些形式照抄英文本來寫法，算同一個詞，不另外計 n。

{{IRREGULAR}}

### 4.3 片語動詞（例外，不計入 n）

片語動詞是初學者最大的記憶負擔（`look for / look after / look at / look out` 意思完全不同），
所以大部分片語動詞都用表內的單一動詞或「動詞＋介系詞」取代
（`give up` → `stop`、`find out` → `know`、`put on` → `wear`、`get up` → `stand up`）。

只有下面 13 個保留，而且只在真的需要時用：

```text
{{PHRASAL}}
```

### 4.4 數字與量詞

- **數字一律用阿拉伯數字**：`1, 2, 3, 100, 2026, 3:30, 20%, 3rd`。
- **不收** `one … twenty`：用數字取代（`one` 因為 `one of them` 而保留）。
- **保留的量詞**（不能被數字取代）：`a / an / the, each, every, some, any, all, none, both, either, neither,
  many, much, few, a few, several, enough, more, most, less, least, half, whole, double, first, last, next, once, twice`。
- **判斷準則**：能換成別的數字還說得通的，就是數字，用阿拉伯數字。

---

## 5. 語法：20 條規則

Mini-English **不改寫英語語法**，只限制用哪些詞。每一條規則都是母語者每天在寫的結構。

### 規則 1　主詞 + 動詞 + 賓語

```en
I eat rice every day.
She writes a letter to her friend.
```

### 規則 2　be 動詞：am / is / are / was / were

```en
I am a student.
You are my friend.
She was very tired yesterday.
```

### 規則 3　第三人稱單數：動詞加 -s / -es

```en
He goes to work by bus.
My mother works in a shop.
```

### 規則 4　進行式：be + V-ing

```en
I am eating lunch now.
They are waiting for the bus.
```

### 規則 5　過去式：規則 -ed；不規則照附錄

```en
I went to the doctor yesterday.
She cooked dinner for her family.
```

### 規則 6　將來式：will + V

```en
I will call you tomorrow.
We will go to the market on Sunday.
```

### 規則 7　否定：not / no

```en
I do not like this one.
There is no water in the cup.
```

### 規則 8　是非問句：be / 助動詞 / do 移到句首

```en
Are you ready?
Do you live here?
Can she sing?
```

### 規則 9　wh- 問句：who / what / where / when / why / how / which

```en
Where do you work?
What is this thing for?
How much is it?
```

### 規則 10　冠詞：a / an / the

```en
This is a small shop.
The shop is on this street.
I want an apple.
```

### 規則 11　所有格：'s

```en
This is my sister's book.
```

### 規則 12　複數：-s / -es / -ies；不規則照附錄

```en
2 children play in the park.
I have many books and 3 pens.
```

### 規則 13　形容詞在名詞前；副詞用 -ly 或表內的副詞

```en
She has a very long hair.
He runs fast.
```

### 規則 14　介系詞：in / on / at / to / for / with / from / by …

```en
I go to work with a friend.
The book is on the table.
```

### 規則 15　連接詞：and / or / but / because / so / if / when / until / while

```en
I go home because I am tired.
If it rains, I will stay at home.
```

### 規則 16　比較：more … than / as … as / 最高級

```en
He is taller than me.
She runs as fast as her brother.
```

### 規則 17　能力與義務：can / must / should / have to

```en
I can swim very well.
You must wait here until I come back.
```

### 規則 18　數量：many / much / a few / few / some / all / every / half

```en
I have many books and a little water.
Every student in my class has a phone.
```

### 規則 19　目的：to + V

```en
I go to the market to buy food.
She calls me to say hello.
```

### 規則 20　存在：there is / there are

```en
There is a book on the table.
There are many people in the park.
```

---

## 6. 困難結構的替代說法

這些結構不收。每一個都有固定的替代，寫的時候照替代說。

| 困難結構 | 一般英文 | Mini-English 替代 |
|---|---|---|
| 被動語態 | The room was cleaned by my brother. | My brother cleaned the room. |
| 完成式 | I have eaten my lunch. | I ate my lunch already. |
| 關係子句（who / which / that） | The man who came is my uncle. | That man came. He is my uncle. |
| 虛擬語氣 | If I were rich, I would travel. | If I have money, I will travel. |
| 間接引語 | He said that he was late. | He said he was late. |
| 動名詞當主語 | Using a phone is fun. | It is fun to use a phone. |
| 分詞片語 | A car stopped at the door. | A car that stopped at the door. |
| 倒裝、強調 | It is my car that I want. | I want my car. |
| too much / too many | too much water | very much water |
| a lot of | a lot of books | many books |
| 完成式的 since | since 2010 | since 2010 |
| 比較級 of 兩者 | He is taller than me. | He is taller than me. |
| 各種片語動詞 | I gave up my job. | I stopped my job. |

---

## 7. 範例對話與短文

下面的對話全部只用核心層 600 詞（除了標成外來詞的地方）。

### 對話一：自我介紹

```en
A: Hello, my name is Li Ming (a man from China). What is your name?
B: I am Anna (a woman from Spain). Nice to meet you.
A: Nice to meet you too. I am from China (a big country in Asia). I am a student.
B: I am a doctor. I work in a big hospital in my city.
A: That is interesting. What do you do in your free time?
B: I read books and I like music.
A: I like movies. I often watch movies with my friends.
```

### 對話二：買東西

```en
A: Hello. What do you want?
B: I want a cup of tea and some bread, please.
A: Do you want anything more?
B: Yes, I want a small bottle of milk too. How much is it?
A: It is $5.
B: Here is the money. Thank you.
A: Here is your tea. Thank you.
```

### 對話三：問路

```en
A: Excuse me, where is the train station?
B: Go straight, then turn left at the big street.
A: Is it far from here?
B: No, it is very near. About 5 minutes on foot.
A: Thank you very much.
B: You are welcome.
```

### 對話四：看醫生

```en
A: I do not feel well. I have a pain in my head.
B: How long do you have this problem?
A: Since yesterday. I also feel tired.
B: You have a cold. You need to rest and take medicine 2 times a day.
A: Thank you, doctor.
B: Come back in 2 days.
```

### 對話五：說感受

```en
A: How do you feel today?
B: I feel very happy. I had a good time with my family.
A: That is very good. Why are you so happy?
B: Because I got a good job in a new company.
A: I am very happy for you. I am a little tired, but I am fine.
```

### 對話六：講一個小故事

```en
A: Do you want to hear a story about a small dog?
B: Yes, please.
A: Long ago, a small dog lived in a small town. He was very hungry every day.
B: Why was he hungry?
A: Because he had no food and no money. One day, he met an old woman.
B: What did the old woman do?
A: She gave him food every day. After 1 year, the dog was big and strong.
B: That is a good story. I want to hear more stories like this.
```

### 短文：我的一天

```en
I get up at 7 in the morning. I eat bread and drink tea with my family.
Then I go to work by bus. My work is in a big shop in the middle of the city.
At noon I eat lunch with my friends. In the afternoon I work until 6.
After work I go home. In the evening I read a book and watch a movie.
I am tired, but every day is a good day.
```

---

## 8. 怎麼改詞表

詞表是資料，不是手抄的：真正的來源是 `data/*.tsv`（每個類別一個檔案），
`python build.py` 會重新產生本文件的第 2 節表格與所有附錄。

改一個詞的步驟：

1. 改 `data/<類別>.tsv` 的一行（詞、層、詞性、中文意思）。
2. 如果是新的不規則形式，改 `data/irregular.tsv`。
3. 如果是新的字首字尾，改 `data/affix.tsv`（並確定它的意思固定）。
4. 執行 `python build.py` 重新產生 `mini-english.md`。
5. 執行 `python check.py`：詞表不能有重複、表格要與附錄一致、所有例句要通過。
6. 執行 `python build.py`（會把新詞表同步到 `prompts/system.md`）與重新產生 `lexicon.tsv`。

`check.py` 讀的就是本文件的附錄，所以「改了 data 卻忘了 build」會被自我檢查抓到。

---

## 9. 已知的取捨

| 取捨 | 說明 |
|---|---|
| **描述不受固定模板限制** | 描述只要用表內的詞就接受，check.py 只驗證詞、不驗證描述的品質。代價是描述的長短與自然度要靠提示詞與人工審查；好處是表達力不受限。 |
| **不用被動、完成式** | 改寫新聞與科學文章時句子會變長、也會失去原句的語氣。 |
| **片語動詞只剩 13 個** | 有些自然說法必須拆開寫，會稍顯正式。 |
| **複合詞要背** | `bus stop`、`bookstore` 這類詞要逐個記，不能自由組合。 |
| **不收慣用語** | `piece of cake`、`break a leg` 一律不收。對初學者是負擔，而且無法幫助表達意思。 |
| **核心層 600 詞仍不夠寫任何文章** | 改寫一般文章時，一定會出現描述與外來詞，句子會變長（實測見 report.md 與 examples.md）。 |
| **擴充層從 400 增到 656** | 第 3 階段做詞典時發現：要做自然的描述，必須有 `throat`、`pig`、`grain`、`liquid`、`thread`、`mark`… 這類具體名詞。核心層不變（600，仍然是必學的量），擴充層吸收了這些缺口。 |
| **中文專有名詞會讓英文母語者讀不懂** | 這是為了目標讀者（中文使用者）做的取捨。 |

---

## 附錄：完整詞表

這是唯一的權威詞表。`#` 開頭的行是類別與層級。

```text
{{APPENDIX}}
```

## 附錄：允許的字首字尾

{{AFFIX}}

## 附錄：保留的不規則形式

{{IRREGULAR}}

## 附錄：片語動詞（例外）

```text
{{PHRASAL}}
```

## 附錄：描述用的類頭

{{HEAD}}

## 附錄：常用但禁止的詞與替代說法

這些詞很常用，但不在 Mini-English 裡。寫的時候用右欄的說法。

{{REPLACE}}
