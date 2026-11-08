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

| 類別 | 核心 | 擴充 | 合計 |
|---|---:|---:|---:|
| 代詞・指示 | 60 | 7 | 67 |
| 語法（功能詞） | 116 | 16 | 132 |
| 數量・比例 | 8 | 2 | 10 |
| 時間 | 30 | 22 | 52 |
| 方位・地點 | 44 | 79 | 123 |
| 自然・天氣 | 29 | 48 | 77 |
| 動作 | 128 | 103 | 231 |
| 性質 | 74 | 80 | 154 |
| 事物 | 48 | 133 | 181 |
| 社交・人 | 34 | 40 | 74 |
| 抽象概念 | 29 | 126 | 155 |
| **合計** | **600** | **656** | **1256** |


### 2.1 代詞・指示（核心 60 ＋ 擴充 7 ＝ 67）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| I | /aɪ/ | 核心 | pron | 我 | I | I am a student |
| me | /ˈmiː/ | 核心 | pron | 我（賓語） | me | （me） |
| my | /maɪ/ | 核心 | det | 我的 | my | （my） |
| myself | /ˌmaɪˈsɛlf/ | 核心 | pron | 我自己 | myself | （myself） |
| you | /juː/ | 核心 | pron | 你；你們 | you | （you） |
| your | /ˈjɔɹ/ | 核心 | det | 你的 | your | （your） |
| yourself | /jɚˈsɛlf/ | 核心 | pron | 你自己 | yourself | （yourself） |
| he | /hiː/ | 核心 | pron | 他 | he | he is my brother |
| him | /ˈhɪm/ | 核心 | pron | 他（賓語） | him | （him） |
| his | /ˈhɪz/ | 核心 | det | 他的 | his | （his） |
| she | /ʃiː/ | 核心 | pron | 她 | she | she is my sister |
| her | /ˈhɝ/ | 核心 | det/poss | 她的 | her | （her） |
| hers | /hɚz/ | 擴充 | pron | 她的（所有格） | hers | （hers） |
| it | /ɪt/ | 核心 | pron | 它 | it | it is a good day |
| its | /ˈɪts/ | 核心 | det | 它的 | its | （its） |
| we | /wiː/ | 核心 | pron | 我們 | we | we are good friends |
| us | /ˈʌs/ | 核心 | pron | 我們（賓格） | us | （us） |
| our | /ˈaʊɚ/ | 核心 | det | 我們的 | our | （our） |
| they | /ðeɪ/ | 核心 | pron | 他們 | they | they are at home |
| them | /ðɛm/ | 核心 | pron | 他們（賓格） | them | （them） |
| their | /ðɛr/ | 核心 | det/poss | 他們的 | their | （their） |
| this | /ðɪs/ | 核心 | det | 這 | this | this is my book |
| that | /ðæt/ | 核心 | det/pron | 那 | that | that is my house |
| these | /ˈðiːz/ | 核心 | det | 這些 | these | these are my books |
| those | /ˈðoʊz/ | 核心 | det | 那些 | those | those are my friends |
| who | /ˈhuː/ | 核心 | pron | 誰 | who | who is that? |
| whom | /ˈhuːm/ | 核心 | pron | 誰（賓格） | whom | （whom） |
| whose | /ˈhuːz/ | 核心 | det/poss | 誰的 | whose | （whose） |
| what | /ˈwʌt/ | 核心 | pron/det | 什麼 | what | what is that? |
| which | /ˈwɪtʃ/ | 核心 | det/pron | 哪一個 | which | which one do you want? |
| someone | /ˈsʌˌmwʌn/ | 核心 | pron | 某人 | someone | （someone） |
| somebody | /ˈsʌˌmbɑdi/ | 核心 | pron | 某人 | somebody | somebody is here |
| something | /ˈsʌmθɪŋ/ | 核心 | pron | 某事 | something | something is wrong |
| anyone | /ˈɛniˌwʌn/ | 核心 | pron | 任何人 | anyone | （anyone） |
| anybody | /ˈɛnibədi/ | 核心 | pron | 任何人 | anybody | （anybody） |
| anything | /ˈɛniˌθɪŋ/ | 核心 | pron | 任何事 | anything | （anything） |
| everyone | /ˈɛvɹiˌwʌn/ | 核心 | pron | 每個人 | everyone | everyone is here |
| everybody | /ˈɛvɹiˌbɑdi/ | 核心 | pron | 每個人 | everybody | （everybody） |
| everything | /ˈɛvɹiˌθɪŋ/ | 核心 | pron | 每件事 | everything | （everything） |
| nobody | /ˈnoʊˌbɑˌdiː/ | 核心 | pron | 沒有人 | nobody | nobody knows |
| nothing | /ˈnʌθɪŋ/ | 核心 | pron | 沒什麼 | nothing | nothing happened |
| one | /wʌn/ | 核心 | pron/num | 一個；其中之一 | one | （one） |
| other | /ˈʌðər/ | 核心 | adj/pron | 另一個 | other / otherer / otherest | very other |
| another | /əˈnʌðɚ/ | 核心 | det | 另一個 | another | （another） |
| both | /ˈboʊθ/ | 核心 | det/pron | 兩者都 | both | （both） |
| either | /ˈiːðɚ/ | 核心 | det/pron | 任一 | either | （either） |
| neither | /ˈniːðɚ/ | 核心 | det/pron | 兩者都不 | neither | （neither） |
| each | /ˈiːtʃ/ | 核心 | det | 每一個 | each | （each） |
| all | /ˈɔl/ | 核心 | det/pron | 全部 | all | （all） |
| some | /ˈsʌm/ | 核心 | det | 一些 | some | （some） |
| any | /ˈɛni/ | 核心 | det | 任何 | any | （any） |
| none | /ˈnʌn/ | 核心 | pron | 沒有一個 | none | （none） |
| many | /ˈmɛni/ | 核心 | det | 許多 | many | （many） |
| much | /ˈmʌtʃ/ | 核心 | det/adv | 許多 | much | very much |
| few | /fjuː/ | 核心 | det | 很少 | few | （few） |
| several | /ˈsɛvɹəl/ | 核心 | det | 幾個 | several | （several） |
| more | /ˈmɔɹ/ | 核心 | det/adv | 更多 | more | very more |
| most | /ˈmoʊst/ | 核心 | det/adv | 大部分 | most | very most |
| such | /ˈsʌtʃ/ | 核心 | adj | 這樣的 | such / sucher / suchest | very such |
| same | /ˈseɪm/ | 核心 | adj | 同一個 | same / samer / samest | very same |
| own | /ˈoʊn/ | 核心 | adj/pron | 自己的 | own / owner / ownest | very own |
| yours | /ˈjʊɹz/ | 擴充 | pron | 你的（所有格） | yours | （yours） |
| himself | /hɪˈmsɛlf/ | 擴充 | pron | 他自己 | himself | （himself） |
| herself | /hɚˈsɛlf/ | 擴充 | pron | 她自己 | herself | （herself） |
| itself | /ˌɪˈtsɛlf/ | 擴充 | pron | 它自己 | itself | （itself） |
| themselves | /ðɛˈmsɛlvz/ | 擴充 | pron | 他們自己 | themselves | （themselves） |
| ourselves | /aʊɚˈsɛlvz/ | 擴充 | pron | 我們自己 | ourselves | （ourselves） |

### 2.2 語法（功能詞）（核心 116 ＋ 擴充 16 ＝ 132）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| a | /ə/ | 核心 | det | 一個（不特定的） | a | （a） |
| an | /ən/ | 核心 | det | 一個（元音前） | an | （an） |
| the | /ðə/ | 核心 | det | 這個（特定的） | the | （the） |
| be | /ˈbiː/ | 核心 | v | 是；存在 | be / am / is / are / was / were / been / being | be careful |
| am | /ˈæm/ | 核心 | v | 是（I） | am / ams / amed / amed / aming | I am ready |
| is | /ɪz/ | 核心 | v | 是（he/she/it） | is / ises / ised / ised / ising | he is ready |
| are | /ˈɑɹ/ | 核心 | v | 是（you/we/they） | are / ares / ared / ared / aring | you are ready |
| was | /wəz/ | 核心 | v | 是（過去，單數） | was / wases / wased / wased / wasing | he was late |
| were | /wɜːr/ | 核心 | v | 是（過去，複數） | were / weres / wered / wered / wering | they were late |
| been | /bɪn/ | 核心 | v | 是（過去分詞） | been / beens / beened / beened / beening | to been |
| being | /biːɪŋ/ | 核心 | v | 正在是 | being / beings / beinged / beinged / beinging | to being |
| do | /duː/ | 核心 | v | 做 | do / does / did | do your work |
| does | /dʌz/ | 核心 | v | 做（第三人稱單數） | does / doeses / doesed / doesed / doesing | he does his work |
| did | /dɪd/ | 核心 | v | 做（過去） | did / dids / dided / dided / diding | did you call? |
| have | /hæv/ | 核心 | v | 有；吃 | have / has / had | have a good day |
| has | /hæz/ | 核心 | v | 有（第三人稱單數） | has / hases / hased / hased / hasing | he has a car |
| had | /hæd/ | 核心 | v | 有（過去） | had / hads / haded / haded / hading | I had a car |
| will | /wɪl/ | 核心 | v | 將會 | will / would | I will go |
| would | /wʊd/ | 核心 | v | 會（委婉語／過去式） | would / woulds / woulded / woulded / woulding | I would go |
| can | /kæn/ | 核心 | v | 能 | can / could | I can swim |
| could | /kʊd/ | 核心 | v | 能（過去式；委婉語） | could / coulds / coulded / coulded / coulding | I could swim |
| shall | /ˈʃæl/ | 核心 | v | 將（少用） | shall / should | shall we go? |
| should | /ʃʊd/ | 核心 | v | 應該 | should / shoulds / shoulded / shoulded / shoulding | you should go |
| may | /meɪ/ | 核心 | v | 可能 | may / might | you may go |
| might | /maɪt/ | 核心 | v | 可能（過去式） | might / mights / mighted / mighted / mighting | it might rain |
| must | /mʌst/ | 核心 | v | 必須 | must | you must go |
| need | /ˈniːd/ | 核心 | v | 需要 | need | to need |
| let | /ˈlɛt/ | 核心 | v | 讓 | let | to let |
| not | /nɑːt/ | 核心 | adv | 不 | not | do not go |
| no | /noʊ/ | 核心 | det/adv | 不；沒有 | no | no water |
| yes | /ˈjɛs/ | 核心 | adv | 是 | yes | yes, I do |
| than | /ˈðæn/ | 核心 | conj | 比 | than | taller than my brother |
| as | /æz/ | 核心 | conj/prep | 像；作為 | as | as fast as you |
| if | /ˈɪf/ | 核心 | conj | 如果 | if | if it rains |
| because | /bɪˈkɔːz/ | 核心 | conj | 因為 | because | because I am busy |
| so | /ˈsoʊ/ | 核心 | conj | 所以 | so | so I go home |
| and | /ænd/ | 核心 | conj | 和 | and | you and I |
| or | /ɔːr/ | 核心 | conj | 或 | or | tea or coffee |
| but | /ˈbʌt/ | 核心 | conj | 但是 | but | but I am busy |
| when | /ˈwɛn/ | 核心 | conj | 當…時 | when | when I arrive |
| while | /ˈwaɪl/ | 核心 | conj | 當…時；然而 | while | while I work |
| before | /bɪˈfɔɹ/ | 核心 | conj/prep | 在…之前 | before | before I go |
| after | /ˈæftɚ/ | 核心 | conj/prep | 在…之後 | after | after I go |
| until | /əˈntɪl/ | 核心 | conj/prep | 直到 | until | until tomorrow |
| since | /ˈsɪns/ | 核心 | conj/prep | 自從 | since | since last year |
| although | /ˌɔˈlðoʊ/ | 擴充 | conj | 雖然 | although | （although） |
| however | /ˌhaʊˈɛvɚ/ | 擴充 | adv | 然而 | however | very however |
| therefore | /ˈðɛˌɹfɔɹ/ | 核心 | adv | 因此 | therefore | therefore I go |
| also | /ˈɔlsoʊ/ | 核心 | adv | 也 | also | also my friend |
| too | /ˈtuː/ | 核心 | adv | 也 | too | me too |
| very | /ˈvɛɹi/ | 核心 | adv | 很 | very | very good |
| quite | /ˈkwaɪt/ | 核心 | adv | 相當 | quite | quite good |
| really | /ˈɹɪli/ | 核心 | adv | 真的 | really | really good |
| just | /ˈdʒʌst/ | 核心 | adv | 剛好；只 | just | just now |
| still | /ˈstɪl/ | 核心 | adv | 仍然 | still | still here |
| only | /ˈoʊnli/ | 核心 | adv | 只 | only | only one |
| even | /ˈiːvɪn/ | 核心 | adv | 甚至 | even | even at night |
| almost | /ˈɔˌlmoʊst/ | 核心 | adv | 幾乎 | almost | almost finished |
| already | /ɔˈlɹɛdi/ | 核心 | adv | 已經 | already | already finished |
| always | /ˈɔˌlweɪz/ | 核心 | adv | 總是 | always | always at home |
| never | /ˈnɛvɚ/ | 核心 | adv | 從不 | never | never at home |
| often | /ˈɔfən/ | 核心 | adv | 常常 | often | often at home |
| sometimes | /səˈmtaɪmz/ | 核心 | adv | 有時候 | sometimes | sometimes at home |
| usually | /ˈjuːʒəwəli/ | 核心 | adv | 通常 | usually | usually at home |
| again | /əˈɡɛn/ | 核心 | adv | 又；再 | again | say it again |
| soon | /ˈsuːn/ | 核心 | adv | 很快 | soon | soon |
| now | /ˈnaʊ/ | 核心 | adv | 現在 | now | right now |
| then | /ˈðɛn/ | 核心 | adv | 那時；然後 | then | and then |
| yet | /ˈjɛt/ | 核心 | adv | 還（尚未） | yet | not yet |
| here | /ˈhiːɹ/ | 核心 | adv | 這裡 | here | come here |
| there | /ðɛr/ | 核心 | adv | 那裡 | there | over there |
| up | /ˈʌp/ | 核心 | adv/prep | 向上 | up | go up |
| down | /ˈdaʊn/ | 核心 | adv/prep | 向下 | down | go down |
| out | /ˈaʊt/ | 核心 | adv/prep | 出去 | out | go out |
| off | /ˈɔf/ | 核心 | adv/prep | 離開；關掉 | off | turn it off |
| over | /ˈoʊvɚ/ | 核心 | adv/prep | 在…上方；超過 | over | come over |
| under | /ˈʌndɚ/ | 核心 | adv/prep | 在…下面 | under | under the table |
| away | /əˈweɪ/ | 核心 | adv | 離開 | away | go away |
| back | /ˈbæk/ | 核心 | adv | 回 | back | come back |
| together | /təˈɡɛðər/ | 核心 | adv | 一起 | together | do it together |
| less | /ˈlɛs/ | 核心 | det/adv | 較少 | less | less money |
| least | /ˈliːst/ | 核心 | det/adv | 最少 | least | at least one |
| enough | /ɪˈnʌf/ | 核心 | det/adv | 足夠 | enough | enough time |
| first | /ˈfɝst/ | 核心 | num/adv | 第一 | first | the first day |
| last | /ˈlæst/ | 核心 | adj/adv | 最後的 | last / laster / lastest | the last day |
| next | /ˈnɛkst/ | 核心 | adj/adv | 下一個 | next / nexter / nextest | the next day |
| second | /ˈsɛkənd/ | 核心 | num/adv/n | 第二；秒 | second / seconds | very second |
| every | /ˈɛvɚi/ | 核心 | det | 每一個 | every | every morning |
| of | /əv/ | 核心 | prep | …的 | of | a cup of tea |
| in | /ɪn/ | 核心 | prep | 在…裡 | in | in the room |
| on | /ɑn/ | 核心 | prep | 在…上 | on | on the table |
| at | /æt/ | 核心 | prep | 在（地點、時間） | at | at the door |
| to | /tuː/ | 核心 | prep | 到；為了 | to | go to school |
| for | /fɔːr/ | 核心 | prep | 為了；給 | for | for me |
| with | /ˈwɪð/ | 核心 | prep | 和…一起 | with | with my friend |
| from | /ˈfɹʌm/ | 核心 | prep | 從 | from | from my home |
| by | /baɪ/ | 核心 | prep | 靠…；被 | by | by bus |
| about | /əˈbaʊt/ | 核心 | prep/adv | 關於；大約 | about | about the work |
| above | /əˈbʌv/ | 核心 | prep | 在…上面 | above | above the door |
| below | /bɪˈloʊ/ | 核心 | prep | 在…下面 | below | below the table |
| across | /əˈkɹɔs/ | 核心 | prep | 橫過 | across | across the road |
| along | /əˈlɔŋ/ | 擴充 | prep | 沿著 | along | （along） |
| around | /ɚˈaʊnd/ | 核心 | prep | 在…周圍 | around | around the corner |
| behind | /bɪˈhaɪnd/ | 核心 | prep | 在…後面 | behind | behind the door |
| between | /bɪˈtwiːn/ | 核心 | prep | 在…之間 | between | between 2 people |
| among | /əˈmʌŋ/ | 擴充 | prep | 在…之中 | among | among my friends |
| into | /ˈɪntu/ | 核心 | prep | 進入 | into | into the room |
| onto | /ˈɑntu/ | 核心 | prep | 到…上 | onto | onto the table |
| through | /ˈθɹuː/ | 擴充 | prep | 穿過 | through | through the door |
| during | /ˈdʊɹɪŋ/ | 擴充 | prep | 在…期間 | during | during the day |
| against | /əˈɡɛnst/ | 擴充 | prep | 反對；靠著 | against | against the wall |
| beside | /bɪˈsaɪd/ | 擴充 | prep | 在…旁邊 | beside | beside the door |
| toward | /təˈwɔɹd/ | 核心 | prep | 朝著 | toward | toward the door |
| without | /wɪˈθaʊt/ | 核心 | prep | 沒有 | without | without water |
| near | /ˈnɪɹ/ | 核心 | prep/adj | 在…附近 | near / nearer / nearest | near my home |
| like | /ˈlaɪk/ | 核心 | prep/v | 像；喜歡 | like / likes / liked / liked / liking | like my mother |
| whether | /ˈwɛðɚ/ | 擴充 | conj | 是否 | whether | I do not know whether |
| unless | /əˈnlɛs/ | 擴充 | conj | 除非 | unless | unless it rains |
| well | /ˈwɛl/ | 核心 | adv | 好地 | well | I am well |
| maybe | /ˈmeɪbi/ | 核心 | adv | 也許 | maybe | maybe tomorrow |
| instead | /ˌɪˈnstɛd/ | 擴充 | adv | 代替 | instead | instead of that |
| little | /ˈlɪtəl/ | 核心 | adj/adv | 少量；小的 | little / less / least | a little water |
| okay | /ˌoʊˈkeɪ/ | 核心 | adv/adj | 好吧；可以 | okay / okayer / okayest | okay, thanks |
| actually | /ˈæˌktʃuːəli/ | 核心 | adv | 實際上 | actually | actually I like it |
| where | /ˈwɛɹ/ | 核心 | pron/det | 哪裡 | where | （where） |
| why | /waɪ/ | 核心 | adv | 為什麼 | why | very why |
| how | /ˈhaʊ/ | 核心 | adv | 怎麼 | how | very how |
| completely | /kəˈmpliːtli/ | 擴充 | adv | 完全地 | completely | very completely |
| easily | /ˈiːzəli/ | 擴充 | adv | 容易地 | easily | very easily |
| especially | /əˈspɛʃli/ | 擴充 | adv | 特別地 | especially | very especially |
| forward | /ˈfɔɹwɚd/ | 擴充 | adv | 向前 | forward | very forward |
| anyway | /ˈɛniˌweɪ/ | 擴充 | adv | 總之 | anyway | very anyway |

### 2.3 數量・比例（核心 8 ＋ 擴充 2 ＝ 10）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| number | /ˈnʌmbɚ/ | 核心 | n | 數字；號碼 | number / numbers | my phone number |
| half | /ˈhæf/ | 核心 | num | 一半 | half | half of the work |
| whole | /ˈhoʊl/ | 核心 | adj | 整個的 | whole / wholer / wholest | the whole day |
| double | /ˈdʌbəl/ | 核心 | adj/v | 兩倍的；加倍 | double / doubles / doubled / doubled / doubling | double the price |
| percent | /pɚˈsɛnt/ | 核心 | n | 百分比 | percent / percents | 10 percent |
| zero | /ˈzɪɹoʊ/ | 核心 | num | 零 | zero | （zero） |
| once | /ˈwʌns/ | 核心 | adv | 一次 | once | very once |
| twice | /ˈtwaɪs/ | 核心 | adv | 兩次 | twice | very twice |
| hundred | /ˈhʌndɹəd/ | 擴充 | num | 一百 | hundred | （hundred） |
| third | /ˈθɝd/ | 擴充 | num/adv | 第三 | third | very third |

### 2.4 時間（核心 30 ＋ 擴充 22 ＝ 52）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| time | /ˈtaɪm/ | 核心 | n | 時間 | time / times | a long time |
| year | /ˈjɪɹ/ | 核心 | n | 年 | year / years | last year |
| month | /ˈmʌnθ/ | 核心 | n | 月 | month / months | next month |
| week | /ˈwiːk/ | 核心 | n | 星期 | week / weeks | next week |
| day | /ˈdeɪ/ | 核心 | n | 天 | day / days | a good day |
| hour | /ˈaʊɚ/ | 核心 | n | 小時 | hour / hours | one hour |
| minute | /ˈmɪnɪt/ | 核心 | n | 分鐘 | minute / minutes | 5 minutes |
| morning | /ˈmɔɹnɪŋ/ | 核心 | n | 早上 | morning / mornings | in the morning |
| afternoon | /ˌæftɚˈnuːn/ | 核心 | n | 下午 | afternoon / afternoons | in the afternoon |
| evening | /ˈiːvnɪŋ/ | 核心 | n | 傍晚 | evening / evenings | in the evening |
| night | /ˈnaɪt/ | 核心 | n | 夜晚 | night / nights | at night |
| noon | /ˈnuːn/ | 擴充 | n | 中午 | noon / noons | the noon |
| midnight | /ˈmɪˌdnaɪt/ | 擴充 | n | 午夜 | midnight / midnights | the midnight |
| today | /təˈdeɪ/ | 核心 | n | 今天 | today / todays | today |
| tomorrow | /təˈmɑˌɹoʊ/ | 核心 | n | 明天 | tomorrow / tomorrows | tomorrow |
| yesterday | /ˈjɛstɚˌdeɪ/ | 核心 | n | 昨天 | yesterday / yesterdays | yesterday |
| tonight | /təˈnaɪt/ | 核心 | n | 今天晚上 | tonight / tonights | tonight |
| weekend | /ˈwiːˌkɛnd/ | 核心 | n | 週末 | weekend / weekends | this weekend |
| birthday | /ˈbɝˌθdeɪ/ | 核心 | n | 生日 | birthday / birthdays | my birthday |
| holiday | /ˈhɑləˌdeɪ/ | 核心 | n | 假日 | holiday / holidays | a long holiday |
| season | /ˈsiːzən/ | 擴充 | n | 季節 | season / seasons | the season |
| spring | /ˈspɹɪŋ/ | 擴充 | n | 春天 | spring / springs | the spring |
| summer | /ˈsʌmɚ/ | 擴充 | n | 夏天 | summer / summers | the summer |
| autumn | /ˈɔtəm/ | 擴充 | n | 秋天 | autumn / autumns | the autumn |
| winter | /ˈwɪntɚ/ | 擴充 | n | 冬天 | winter / winters | the winter |
| date | /ˈdeɪt/ | 核心 | n | 日期 | date / dates | today is the date |
| clock | /ˈklɑk/ | 核心 | n | 鐘 | clock / clocks | look at the clock |
| calendar | /ˈkæləndɚ/ | 擴充 | n | 日曆 | calendar / calendars | the calendar |
| moment | /ˈmoʊmənt/ | 擴充 | n | 片刻 | moment / moments | the moment |
| future | /ˈfjuːtʃɚ/ | 擴充 | n | 將來 | future / futures | the future |
| past | /ˈpæst/ | 擴充 | n/adj | 過去 | past / pasts | very past |
| present | /ˈpɹɛzənt/ | 擴充 | n/adj | 現在；禮物 | present / presents | very present |
| early | /ˈɝli/ | 核心 | adj/adv | 早 | early / earlier / earliest | get up early |
| late | /ˈleɪt/ | 核心 | adj/adv | 晚；遲 | late / later / latest | come late |
| ago | /əˈɡoʊ/ | 核心 | adv | 以前 | ago | 2 days ago |
| daily | /ˈdeɪli/ | 擴充 | adj | 每天的 | daily / dailier / dailiest | very daily |
| weekly | /ˈwiːkli/ | 擴充 | adj | 每週的 | weekly / weeklier / weekliest | very weekly |
| monthly | /ˈmʌnθli/ | 擴充 | adj | 每月的 | monthly / more monthly / most monthly | very monthly |
| yearly | /ˈjɪɹli/ | 擴充 | adj | 每年的 | yearly / yearlier / yearliest | very yearly |
| recently | /ˈɹiːsəntli/ | 擴充 | adv | 最近 | recently | very recently |
| schedule | /ˈskɛdʒuːl/ | 擴充 | n | 時刻表 | schedule / schedules | the schedule |
| Monday | /ˈmʌndi/ | 核心 | n | 星期 | Monday / Mondays | the Monday |
| Tuesday | /ˈtuːzdi/ | 核心 | n | 星期 | Tuesday / Tuesdays | the Tuesday |
| Wednesday | /ˈwɛnzdi/ | 核心 | n | 星期 | Wednesday / Wednesdays | the Wednesday |
| Thursday | /ˈθɝˌzdeɪ/ | 核心 | n | 星期 | Thursday / Thursdays | the Thursday |
| Friday | /ˈfɹaɪdi/ | 核心 | n | 星期 | Friday / Fridays | the Friday |
| Saturday | /ˈsætɚdi/ | 核心 | n | 星期 | Saturday / Saturdays | the Saturday |
| Sunday | /ˈsʌˌndeɪ/ | 核心 | n | 星期 | Sunday / Sundays | the Sunday |
| o'clock | /əˈklɑk/ | 擴充 | adv | …點鐘 | o'clock | very o'clock |
| sunrise | /ˈsʌˌnɹaɪz/ | 擴充 | n | 日出 | sunrise / sunrises | the sunrise |
| sunset | /ˈsʌˌnsɛt/ | 擴充 | n | 日落 | sunset / sunsets | the sunset |
| century | /ˈsɛntʃɚi/ | 擴充 | n | 世紀 | century / centuries | the century |

### 2.5 方位・地點（核心 44 ＋ 擴充 79 ＝ 123）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| place | /ˈpleɪs/ | 核心 | n/v | 地方；放置 | place / places / placed / placed / placing | a place to eat |
| house | /ˈhaʊs/ | 核心 | n | 房子 | house / houses | my house |
| home | /ˈhoʊm/ | 核心 | n | 家 | home / homes | at home |
| room | /ˈɹuːm/ | 核心 | n | 房間 | room / rooms | a small room |
| door | /ˈdɔɹ/ | 核心 | n | 門 | door / doors | open the door |
| window | /ˈwɪndoʊ/ | 核心 | n | 窗 | window / windows | the window |
| floor | /ˈflɔɹ/ | 核心 | n | 地板；樓層 | floor / floors | the top floor |
| wall | /ˈwɔl/ | 核心 | n | 牆 | wall / walls | a white wall |
| road | /ˈɹoʊd/ | 核心 | n | 道路 | road / roads | a long road |
| street | /ˈstɹiːt/ | 核心 | n | 街道 | street / streets | a busy street |
| way | /ˈweɪ/ | 核心 | n | 路；方式 | way / ways | on the way |
| corner | /ˈkɔɹnɚ/ | 核心 | n | 角落 | corner / corners | the corner of the street |
| side | /ˈsaɪd/ | 核心 | n | 邊 | side / sides | on the other side |
| city | /ˈsɪti/ | 核心 | n | 城市 | city / cities | a big city |
| town | /ˈtaʊn/ | 核心 | n | 城鎮 | town / towns | a small town |
| village | /ˈvɪlədʒ/ | 擴充 | n | 村莊 | village / villages | the village |
| country | /ˈkʌntɹi/ | 核心 | n | 國家 | country / countries | my country |
| world | /ˈwɝld/ | 核心 | n | 世界 | world / worlds | around the world |
| shop | /ˈʃɑp/ | 核心 | n | 商店 | shop / shops | a small shop |
| store | /ˈstɔɹ/ | 核心 | n | 店 | store / stores | a big store |
| market | /ˈmɑɹkət/ | 擴充 | n | 市場 | market / markets | the market |
| restaurant | /ˈɹɛstɚˌɑnt/ | 擴充 | n | 餐廳 | restaurant / restaurants | the restaurant |
| hotel | /hoʊˈtɛl/ | 擴充 | n | 旅館 | hotel / hotels | the hotel |
| station | /ˈsteɪʃən/ | 核心 | n | 車站 | station / stations | the train station |
| airport | /ˈɛˌɹpɔɹt/ | 擴充 | n | 機場 | airport / airports | the airport |
| school | /ˈskuːl/ | 核心 | n | 學校 | school / schools | go to school |
| office | /ˈɔfɪs/ | 核心 | n | 辦公室 | office / offices | a small office |
| hospital | /ˈhɑˌspɪtəl/ | 擴充 | n | 醫院 | hospital / hospitals | the hospital |
| bank | /ˈbæŋk/ | 核心 | n | 銀行 | bank / banks | the bank on the street |
| park | /ˈpɑɹk/ | 核心 | n | 公園 | park / parks | in the park |
| library | /ˈlaɪbɹɛˌɹiː/ | 擴充 | n | 圖書館 | library / libraries | the library |
| museum | /mjuˈziːəm/ | 擴充 | n | 博物館 | museum / museums | the museum |
| cinema | /ˈsɪnəmə/ | 擴充 | n | 電影院 | cinema / cinemas | the cinema |
| theater | /ˈθiːətɚ/ | 擴充 | n | 劇場 | theater / theaters | the theater |
| stadium | /ˈsteɪdiəm/ | 擴充 | n | 體育場 | stadium / stadiums | the stadium |
| factory | /ˈfæktɚi/ | 擴充 | n | 工廠 | factory / factories | the factory |
| church | /ˈtʃɝtʃ/ | 擴充 | n | 教堂 | church / churches | the church |
| building | /ˈbɪldɪŋ/ | 擴充 | n | 建築物 | building / buildings | the building |
| area | /ˈɛriːə/ | 擴充 | n | 地區 | area / areas | the area |
| region | /ˈɹiːdʒən/ | 擴充 | n | 區域 | region / regions | the region |
| north | /ˈnɔɹθ/ | 核心 | n | 北方 | north / norths | the north side |
| south | /ˈsaʊθ/ | 核心 | n | 南方 | south / souths | the south side |
| east | /ˈiːst/ | 核心 | n | 東方 | east / easts | the east side |
| west | /ˈwɛst/ | 核心 | n | 西方 | west / wests | the west side |
| left | /ˈlɛft/ | 核心 | adj/adv | 左 | left / lefter / leftest | on the left |
| right | /ˈɹaɪt/ | 核心 | adj/adv | 右；對的；對 | right / righter / rightest | on the right |
| front | /ˈfɹʌnt/ | 核心 | n | 前面 | front / fronts | in front of the door |
| far | /ˈfɑɹ/ | 擴充 | adj | 遠的 | far / farther / farthest | very far |
| inside | /ˌɪˈnsaɪd/ | 核心 | prep/adv | 裡面 | inside | inside the house |
| outside | /ˈaʊˈtsaɪd/ | 核心 | prep/adv | 外面 | outside | outside the house |
| map | /ˈmæp/ | 核心 | n | 地圖 | map / maps | read a map |
| sign | /ˈsaɪn/ | 擴充 | n/v | 標誌；簽名 | sign / signs / signed / signed / signing | sign your name |
| bus stop | // | 核心 | n | 公車站 | bus stop / bus stops | at the bus stop |
| subway | /ˈsʌˌbweɪ/ | 擴充 | n | 地下鐵 | subway / subways | the subway |
| block | /ˈblɑk/ | 擴充 | n | 街區 | block / blocks | the block |
| neighborhood | /ˈneɪbɚˌhʊd/ | 擴充 | n | 社區 | neighborhood / neighborhoods | the neighborhood |
| gate | /ˈɡeɪt/ | 擴充 | n | 門口 | gate / gates | the gate |
| yard | /ˈjɑɹd/ | 擴充 | n | 院子 | yard / yards | the yard |
| roof | /ˈɹuːf/ | 擴充 | n | 屋頂 | roof / roofs | the roof |
| address | /ˈæˌdɹɛs/ | 擴充 | n | 地址 | address / addresses | the address |
| downtown | /ˈdaʊˈntaʊn/ | 擴充 | adv | 市中心 | downtown | very downtown |
| abroad | /əˈbɹɔd/ | 擴充 | adv | 在國外 | abroad | very abroad |
| capital | /ˈkæpətəl/ | 擴充 | n | 首都 | capital / capitals | the capital |
| continent | /ˈkɑntənənt/ | 擴充 | n | 大洲 | continent / continents | the continent |
| space | /ˈspeɪs/ | 擴充 | n | 空間；太空 | space / spaces | the space |
| distance | /ˈdɪstəns/ | 擴充 | n | 距離 | distance / distances | the distance |
| direction | /dɚˈɛkʃən/ | 擴充 | n | 方向 | direction / directions | the direction |
| position | /pəˈzɪʃən/ | 擴充 | n | 位置 | position / positions | the position |
| middle | /ˈmɪdəl/ | 擴充 | n | 中間 | middle / middles | the middle |
| edge | /ˈɛdʒ/ | 擴充 | n | 邊緣 | edge / edges | the edge |
| top | /ˈtɑp/ | 核心 | n | 頂部 | top / tops | on the top |
| bottom | /ˈbɑtəm/ | 擴充 | n | 底部 | bottom / bottoms | the bottom |
| entrance | /ˈɛntɹəns/ | 擴充 | n | 入口 | entrance / entrances | the entrance |
| exit | /ˈɛɡzɪt/ | 擴充 | n | 出口 | exit / exits | the exit |
| platform | /ˈplæˌtfɔɹm/ | 擴充 | n | 月台 | platform / platforms | the platform |
| line | /ˈlaɪn/ | 核心 | n | 線；排隊 | line / lines | stand in line |
| queue | /ˈkjuː/ | 擴充 | n | 隊伍 | queue / queues | the queue |
| ticket | /ˈtɪkət/ | 核心 | n | 票 | ticket / tickets | a bus ticket |
| counter | /ˈkaʊntɚ/ | 擴充 | n | 櫃檯 | counter / counters | the counter |
| mall | /ˈmɔl/ | 擴充 | n | 購物中心 | mall / malls | the mall |
| clinic | /ˈklɪnɪk/ | 擴充 | n | 診所 | clinic / clinics | the clinic |
| pharmacy | /ˈfɑɹməsi/ | 擴充 | n | 藥局 | pharmacy / pharmacies | the pharmacy |
| police | /pəˈliːs/ | 擴充 | n | 警察 | police / polices | the police |
| bus | /bʌs/ | 核心 | n | 公車 | bus / buses | take the bus |
| train | /ˈtɹeɪn/ | 核心 | n | 火車 | train / trains | take the train |
| plane | /ˈpleɪn/ | 核心 | n | 飛機 | plane / planes | take the plane |
| boat | /ˈboʊt/ | 擴充 | n | 船 | boat / boats | the boat |
| ship | /ˈʃɪp/ | 擴充 | n | 船 | ship / ships | the ship |
| taxi | /ˈtæksi/ | 擴充 | n | 計程車 | taxi / taxis | the taxi |
| car | /ˈkɑɹ/ | 核心 | n | 車 | car / cars | my car |
| bike | /ˈbaɪk/ | 核心 | n | 自行車 | bike / bikes | ride a bike |
| gym | /ˈdʒɪm/ | 核心 | n | 健身房 | gym / gyms | the gym |
| pool | /ˈpuːl/ | 擴充 | n | 游泳池 | pool / pools | the pool |
| africa | /ˈæfɹəkɑ/ | 擴充 | n | 非洲 | africa / africas | the africa |
| america | /əˈmɛɹəkə/ | 擴充 | n | 美國 | america / americas | the america |
| australia | /ɔˈstɹeɪljə/ | 擴充 | n | 澳洲 | australia / australias | the australia |
| bathroom | /ˈbæˌθɹuːm/ | 擴充 | n | 浴室 | bathroom / bathrooms | the bathroom |
| bridge | /ˈbɹɪdʒ/ | 擴充 | n | 橋 | bridge / bridges | the bridge |
| center | /ˈsɛntɚ/ | 擴充 | n | 中心 | center / centers | the center |
| china | /ˈtʃaɪnə/ | 擴充 | n | 中國 | china / chinas | the china |
| college | /ˈkɑlɪdʒ/ | 擴充 | n | 學院 | college / colleges | the college |
| court | /ˈkɔɹt/ | 擴充 | n | 法院 | court / courts | the court |
| desert | /ˈdɛzɚt/ | 擴充 | n | 沙漠 | desert / deserts | the desert |
| germany | /ˈdʒɝməni/ | 擴充 | n | 德國 | germany / germanies | the germany |
| ground | /ˈɡɹaʊnd/ | 擴充 | n | 地面 | ground / grounds | the ground |
| italy | /ˈɪtəli/ | 擴充 | n | 義大利 | italy / italies | the italy |
| japan | /dʒəˈpæn/ | 擴充 | n | 日本 | japan / japans | the japan |
| korea | /ˌkɔˈɹiːə/ | 擴充 | n | 韓國 | korea / koreas | the korea |
| path | /ˈpæθ/ | 擴充 | n | 小路 | path / paths | the path |
| rail | /ˈɹeɪl/ | 擴充 | n | 鐵軌 | rail / rails | the rail |
| seat | /ˈsiːt/ | 擴充 | n | 座位 | seat / seats | the seat |
| slope | /ˈsloʊp/ | 擴充 | n | 斜坡 | slope / slopes | the slope |
| spain | /ˈspeɪn/ | 擴充 | n | 西班牙 | spain / spains | the spain |
| temple | /ˈtɛmpəl/ | 擴充 | n | 神殿 | temple / temples | the temple |
| truck | /ˈtɹʌk/ | 擴充 | n | 卡車 | truck / trucks | the truck |
| university | /ˌjuːnəˈvɝsəti/ | 擴充 | n | 大學 | university / universities | the university |
| vehicle | /ˈviːhɪkəl/ | 擴充 | n | 車輛 | vehicle / vehicles | the vehicle |
| accident | /ˈæksədənt/ | 擴充 | n | 意外 | accident / accidents | the accident |
| toilet | /ˈtɔɪlət/ | 擴充 | n | 廁所 | toilet / toilets | the toilet |
| lake | /ˈleɪk/ | 擴充 | n | 湖 | lake / lakes | the lake |
| playground | /ˈpleɪˌɡɹaʊnd/ | 擴充 | n | 遊樂場 | playground / playgrounds | the playground |
| garden | /ˈɡɑɹdən/ | 擴充 | n | 花園 | garden / gardens | the garden |
| bicycle | /ˈbaɪsɪkəl/ | 擴充 | n | 腳踏車 | bicycle / bicycles | the bicycle |

### 2.6 自然・天氣（核心 29 ＋ 擴充 48 ＝ 77）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| weather | /ˈwɛðɚ/ | 核心 | n | 天氣 | weather / weathers | the weather today |
| sun | /ˈsʌn/ | 核心 | n | 太陽 | sun / suns | the sun is hot |
| moon | /ˈmuːn/ | 擴充 | n | 月亮 | moon / moons | the moon at night |
| star | /ˈstɑɹ/ | 擴充 | n | 星星 | star / stars | the star |
| sky | /ˈskaɪ/ | 核心 | n | 天空 | sky / skies | a blue sky |
| cloud | /ˈklaʊd/ | 擴充 | n | 雲 | cloud / clouds | a white cloud |
| rain | /ˈɹeɪn/ | 核心 | n/v | 雨；下雨 | rain / rains / rained / rained / raining | it is going to rain |
| snow | /ˈsnoʊ/ | 核心 | n/v | 雪；下雪 | snow / snows / snowed / snowed / snowing | snow in winter |
| wind | /wɪnd/ | 核心 | n | 風 | wind / winds | strong wind |
| sea | /ˈsiː/ | 核心 | n | 海 | sea / seas | the sea is big |
| river | /ˈɹɪvɚ/ | 核心 | n | 河 | river / rivers | a long river |
| mountain | /ˈmaʊntən/ | 擴充 | n | 山 | mountain / mountains | the mountain |
| hill | /ˈhɪl/ | 擴充 | n | 小山 | hill / hills | the hill |
| tree | /ˈtɹiː/ | 核心 | n | 樹 | tree / trees | a tall tree |
| flower | /ˈflaʊɚ/ | 核心 | n | 花 | flower / flowers | a yellow flower |
| grass | /ˈɡɹæs/ | 擴充 | n | 草 | grass / grasses | the grass |
| leaf | /ˈliːf/ | 擴充 | n | 葉子 | leaf / leafs | the leaf |
| plant | /ˈplænt/ | 核心 | n/v | 植物；種植 | plant / plants / planted / planted / planting | a green plant |
| animal | /ˈænəməl/ | 核心 | n | 動物 | animal / animals | a small animal |
| dog | /ˈdɔɡ/ | 核心 | n | 狗 | dog / dogs | a big dog |
| cat | /ˈkæt/ | 核心 | n | 貓 | cat / cats | a black cat |
| bird | /ˈbɝd/ | 核心 | n | 鳥 | bird / birds | a small bird |
| fish | /ˈfɪʃ/ | 核心 | n/v | 魚 | fish / fishes / fished / fished / fishing | many fish |
| earth | /ˈɝθ/ | 核心 | n | 地球；土 | earth / earths | the earth |
| fire | /ˈfaɪɚ/ | 核心 | n/v | 火；著火 | fire / fires / fired / fired / firing | a big fire |
| ice | /ˈaɪs/ | 擴充 | n | 冰 | ice / ices | the ice |
| sand | /ˈsænd/ | 擴充 | n | 沙子 | sand / sands | the sand |
| stone | /ˈstoʊn/ | 擴充 | n | 石頭 | stone / stones | the stone |
| rock | /ˈɹɑk/ | 擴充 | n | 岩石 | rock / rocks | the rock |
| wood | /ˈwʊd/ | 核心 | n | 木頭 | wood / woods | a piece of wood |
| oil | /ˈɔɪl/ | 核心 | n | 油 | oil / oils | much oil |
| gas | /ˈɡæs/ | 核心 | n | 氣體；瓦斯 | gas / gases | the gas in the car |
| air | /ˈɛɹ/ | 核心 | n | 空氣 | air / airs | clean air |
| land | /ˈlænd/ | 核心 | n | 土地 | land / lands | dry land |
| field | /ˈfiːld/ | 核心 | n | 田地 | field / fields | a green field |
| farm | /ˈfɑɹm/ | 核心 | n | 農場 | farm / farms | a small farm |
| forest | /ˈfɔɹəst/ | 擴充 | n | 森林 | forest / forests | the forest |
| island | /ˈaɪlənd/ | 擴充 | n | 島 | island / islands | the island |
| beach | /ˈbiːtʃ/ | 擴充 | n | 海灘 | beach / beaches | the beach |
| light | /ˈlaɪt/ | 核心 | n/adj | 光；燈；輕 | light / lights | turn on the light |
| heat | /ˈhiːt/ | 擴充 | n/v | 熱；加熱 | heat / heats / heated / heated / heating | to heat |
| storm | /ˈstɔɹm/ | 擴充 | n | 暴風雨 | storm / storms | the storm |
| temperature | /ˈtɛmpɹətʃɚ/ | 擴充 | n | 溫度 | temperature / temperatures | the temperature |
| nature | /ˈneɪtʃɚ/ | 擴充 | n | 自然 | nature / natures | the nature |
| environment | /ɪˈnvaɪɹənmənt/ | 擴充 | n | 環境 | environment / environments | the environment |
| pollution | /pəˈluːʃən/ | 擴充 | n | 污染 | pollution / pollutions | the pollution |
| climate | /ˈklaɪmət/ | 擴充 | n | 氣候 | climate / climates | the climate |
| energy | /ˈɛnɚdʒi/ | 擴充 | n | 能量；能源 | energy / energies | the energy |
| electricity | /ɪˌlɛˈktɹɪsəti/ | 擴充 | n | 電 | electricity / electricities | the electricity |
| metal | /ˈmɛtəl/ | 擴充 | n | 金屬 | metal / metals | the metal |
| plastic | /ˈplæstɪk/ | 擴充 | n | 塑膠 | plastic / plastics | the plastic |
| glass | /ˈɡlæs/ | 核心 | n | 玻璃；玻璃杯 | glass / glasses | a glass of water |
| paper | /ˈpeɪpɚ/ | 核心 | n | 紙 | paper / papers | a piece of paper |
| water | /ˈwɔːtər/ | 核心 | n | 水 | water / waters | the water |
| atom | /ˈætəm/ | 擴充 | n | 原子 | atom / atoms | the atom |
| bee | /ˈbiː/ | 擴充 | n | 蜜蜂 | bee / bees | the bee |
| cell | /ˈsɛl/ | 擴充 | n | 細胞 | cell / cells | the cell |
| cow | /ˈkaʊ/ | 擴充 | n | 牛 | cow / cows | the cow |
| dirt | /ˈdɝt/ | 擴充 | n | 泥土 | dirt / dirts | the dirt |
| fuel | /ˈfjuːəl/ | 擴充 | n | 燃料 | fuel / fuels | the fuel |
| fur | /ˈfɝ/ | 擴充 | n | 毛皮 | fur / furs | the fur |
| grain | /ˈɡɹeɪn/ | 擴充 | n | 穀物 | grain / grains | the grain |
| hay | /ˈheɪ/ | 擴充 | n | 乾草 | hay / hays | the hay |
| horse | /ˈhɔɹs/ | 擴充 | n | 馬 | horse / horses | the horse |
| insect | /ˈɪˌnsɛkt/ | 擴充 | n | 昆蟲 | insect / insects | the insect |
| iron | /ˈaɪɚn/ | 擴充 | n | 鐵 | iron / irons | the iron |
| liquid | /ˈlɪkwəd/ | 擴充 | n | 液體 | liquid / liquids | the liquid |
| pig | /ˈpɪɡ/ | 擴充 | n | 豬 | pig / pigs | the pig |
| planet | /ˈplænət/ | 擴充 | n | 行星 | planet / planets | the planet |
| root | /ˈɹuːt/ | 擴充 | n | 根 | root / roots | the root |
| seed | /ˈsiːd/ | 擴充 | n | 種子 | seed / seeds | the seed |
| sheep | /ˈʃiːp/ | 擴充 | n | 羊 | sheep / sheeps | the sheep |
| snake | /ˈsneɪk/ | 擴充 | n | 蛇 | snake / snakes | the snake |
| soil | /ˈsɔɪl/ | 擴充 | n | 泥土 | soil / soils | the soil |
| volcano | /vɑˈlkeɪnoʊ/ | 擴充 | n | 火山 | volcano / volcanoes | the volcano |
| wing | /ˈwɪŋ/ | 擴充 | n | 翅膀 | wing / wings | the wing |
| dust | /ˈdʌst/ | 擴充 | n | 灰塵 | dust / dusts | the dust |

### 2.7 動作（核心 128 ＋ 擴充 103 ＝ 231）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| go | /ˈɡoʊ/ | 核心 | v | 去 | go / goes / went / gone / going | go to work |
| come | /ˈkʌm/ | 核心 | v | 來 | come / comes / came / came / coming | come home |
| walk | /ˈwɔk/ | 核心 | v | 走 | walk / walks / walked / walked / walking | to walk |
| run | /ˈɹʌn/ | 核心 | v | 跑 | run / runs / ran / ran / running | to run |
| sit | /ˈsɪt/ | 核心 | v | 坐 | sit / sits / sat / sat / sitting | to sit |
| stand | /ˈstænd/ | 核心 | v | 站 | stand / stands / stood / stood / standing | to stand |
| eat | /ˈiːt/ | 核心 | v | 吃 | eat / eats / ate / eaten / eating | eat rice |
| drink | /ˈdɹɪŋk/ | 核心 | v/n | 喝；飲料 | drink / drinks / drank / drunk / drinking | drink water |
| sleep | /ˈsliːp/ | 核心 | v | 睡 | sleep / sleeps / slept / slept / sleeping | sleep at night |
| wake | /ˈweɪk/ | 核心 | v | 醒來 | wake / wakes / woke / woken / waking | to wake |
| read | /ɹiːd/ | 核心 | v | 讀 | read / reads / read / read / reading | read a book |
| write | /ˈɹaɪt/ | 核心 | v | 寫 | write / writes / wrote / written / writing | write a letter |
| speak | /ˈspiːk/ | 核心 | v | 說（某種語言） | speak / speaks / spoke / spoken / speaking | to speak |
| say | /ˈseɪ/ | 核心 | v | 說 | say / says / said / said / saying | say hello |
| tell | /ˈtɛl/ | 核心 | v | 告訴 | tell / tells / told / told / telling | tell me |
| ask | /ˈæsk/ | 核心 | v | 問 | ask / asks / asked / asked / asking | ask a question |
| answer | /ˈænsɚ/ | 核心 | v/n | 回答；答案 | answer / answers / answered / answered / answering | the answer |
| look | /ˈlʊk/ | 核心 | v | 看 | look / looks / looked / looked / looking | look at the map |
| see | /ˈsiː/ | 核心 | v | 看見 | see / sees / seed / seed / seeing | see a doctor |
| watch | /ˈwɑtʃ/ | 核心 | v/n | 看；觀看；手錶 | watch / watches / watched / watched / watching | watch a movie |
| hear | /ˈhiːɹ/ | 核心 | v | 聽見 | hear / hears / heard / heard / hearing | hear music |
| listen | /ˈlɪsən/ | 核心 | v | 聽 | listen / listens / listened / listened / listening | to listen |
| give | /ˈɡɪv/ | 核心 | v | 給 | give / gives / gave / given / giving | give me the key |
| take | /ˈteɪk/ | 核心 | v | 拿；花費；搭乘 | take / takes / took / taken / taking | take a bus |
| get | /ˈɡɛt/ | 核心 | v | 得到；到 | get / gets / got / got / getting | get a coffee |
| put | /ˈpʊt/ | 核心 | v | 放 | put / puts / put / put / putting | put it on the table |
| make | /ˈmeɪk/ | 核心 | v | 做；使得 | make / makes / made / made / making | make dinner |
| buy | /ˈbaɪ/ | 核心 | v | 買 | buy / buys / bought / bought / buying | buy food |
| sell | /ˈsɛl/ | 核心 | v | 賣 | sell / sells / sold / sold / selling | sell fruit |
| pay | /ˈpeɪ/ | 核心 | v | 付錢 | pay / pays / paid / paid / paying | pay the bill |
| cost | /ˈkɑst/ | 核心 | v | 花費 | cost / costs / cost / cost / costing | to cost |
| open | /ˈoʊpən/ | 核心 | v | 開 | open / opens / opened / opened / opening | open the door |
| close | /kloʊs/ | 核心 | v | 關 | close / closes / closed / closed / closing | close the window |
| start | /ˈstɑɹt/ | 核心 | v | 開始 | start / starts / started / started / starting | start work |
| stop | /ˈstɑp/ | 核心 | v | 停止 | stop / stops / stopped / stopped / stopping | stop the car |
| wait | /ˈweɪt/ | 核心 | v | 等待 | wait / waits / waited / waited / waiting | wait for the bus |
| work | /ˈwɝk/ | 核心 | v/n | 工作 | work / works / worked / worked / working | work at home |
| play | /ˈpleɪ/ | 核心 | v | 玩；比賽 | play / plays / played / played / playing | play with a child |
| study | /ˈstʌdi/ | 核心 | v | 學習 | study / studies / studied / studied / studying | study English |
| learn | /ˈlɝn/ | 核心 | v | 學會 | learn / learns / learned / learned / learning | learn a new word |
| teach | /ˈtiːtʃ/ | 核心 | v | 教 | teach / teaches / taught / taught / teaching | teach students |
| help | /ˈhɛlp/ | 核心 | v | 幫助 | help / helps / helped / helped / helping | help my friend |
| use | /juːz/ | 核心 | v | 使用 | use / uses / used / used / using | use a computer |
| find | /ˈfaɪnd/ | 核心 | v | 找到 | find / finds / found / found / finding | find my keys |
| lose | /ˈluːz/ | 核心 | v | 失去 | lose / loses / lost / lost / losing | lose my phone |
| keep | /ˈkiːp/ | 核心 | v | 保持 | keep / keeps / kept / kept / keeping | keep the book |
| send | /ˈsɛnd/ | 核心 | v | 寄；送 | send / sends / sent / sent / sending | send an email |
| bring | /ˈbɹɪŋ/ | 核心 | v | 帶來 | bring / brings / brought / brought / bringing | bring water |
| carry | /ˈkæɹi/ | 核心 | v | 搬；帶 | carry / carries / carried / carried / carrying | to carry |
| move | /ˈmuːv/ | 核心 | v | 移動 | move / moves / moved / moved / moving | move to a new city |
| turn | /ˈtɝn/ | 核心 | v | 轉；變成 | turn / turns / turned / turned / turning | to turn |
| change | /ˈtʃeɪndʒ/ | 核心 | v | 改變 | change / changes / changed / changed / changing | change my job |
| grow | /ˈɡɹoʊ/ | 核心 | v | 生長 | grow / grows / grew / grown / growing | grow flowers |
| live | /lɪv/ | 核心 | v | 住；生活 | live / lives / lived / lived / living | live in a big city |
| die | /ˈdaɪ/ | 核心 | v | 死 | die / dies / died / died / dying | die young |
| meet | /ˈmiːt/ | 核心 | v | 遇見 | meet / meets / met / met / meeting | meet my friend |
| visit | /ˈvɪzɪt/ | 核心 | v | 拜訪 | visit / visits / visited / visited / visiting | visit my parents |
| drive | /ˈdɹaɪv/ | 核心 | v | 開車 | drive / drives / drove / driven / driving | drive to work |
| ride | /ˈɹaɪd/ | 核心 | v | 騎 | ride / rides / rode / ridden / riding | ride a bike |
| fly | /ˈflaɪ/ | 核心 | v | 飛 | fly / flies / flew / flown / flying | fly to another country |
| cook | /ˈkʊk/ | 核心 | v | 煮飯 | cook / cooks / cooked / cooked / cooking | cook dinner |
| wash | /ˈwɑʃ/ | 核心 | v | 洗 | wash / washes / washed / washed / washing | wash my hands |
| clean | /ˈkliːn/ | 核心 | v/adj | 洗乾淨；乾淨的 | clean / cleans / cleaned / cleaned / cleaning | clean the room |
| cut | /ˈkʌt/ | 核心 | v | 切；剪 | cut / cuts / cut / cut / cutting | cut the bread |
| break | /ˈbɹeɪk/ | 核心 | v | 打破；休息 | break / breaks / broke / broken / breaking | to break |
| fix | /ˈfɪks/ | 核心 | v | 修理 | fix / fixes / fixed / fixed / fixing | to fix |
| wear | /ˈwɛɹ/ | 核心 | v | 穿 | wear / wears / wore / worn / wearing | wear a coat |
| feel | /ˈfiːl/ | 核心 | v | 感覺 | feel / feels / felt / felt / feeling | feel happy |
| hurt | /ˈhɝt/ | 核心 | v | 痛；受傷 | hurt / hurts / hurted / hurted / hurting | hurt my back |
| want | /ˈwɑnt/ | 核心 | v | 想要 | want / wants / wanted / wanted / wanting | want water |
| try | /ˈtɹaɪ/ | 核心 | v | 嘗試 | try / tries / tried / tried / trying | try again |
| love | /ˈlʌv/ | 核心 | v | 愛 | love / loves / loved / loved / loving | love my family |
| hate | /ˈheɪt/ | 核心 | v | 討厭 | hate / hates / hated / hated / hating | hate cold weather |
| begin | /bɪˈɡɪn/ | 核心 | v | 開始 | begin / begins / began / begun / beginning | begin a new job |
| finish | /ˈfɪnɪʃ/ | 核心 | v | 完成 | finish / finishes / finished / finished / finishing | finish my work |
| choose | /ˈtʃuːz/ | 核心 | v | 選擇 | choose / chooses / chose / chosen / choosing | choose a chair |
| decide | /ˌdɪˈsaɪd/ | 核心 | v | 決定 | decide / decides / decided / decided / deciding | decide to go |
| hope | /ˈhoʊp/ | 核心 | v | 希望 | hope / hopes / hoped / hoped / hoping | I hope so |
| wish | /ˈwɪʃ/ | 核心 | v | 希望；祝願 | wish / wishes / wished / wished / wishing | wish you a good day |
| remember | /ɹɪˈmɛmbɚ/ | 核心 | v | 記得 | remember / remembers / remembered / remembered / remembering | remember her name |
| forget | /fɚˈɡɛt/ | 核心 | v | 忘記 | forget / forgets / forgot / forgotten / forgetting | forget the time |
| know | /ˈnoʊ/ | 核心 | v | 知道 | know / knows / knew / known / knowing | know the answer |
| think | /ˈθɪŋk/ | 核心 | v | 認為 | think / thinks / thought / thought / thinking | I think so |
| mean | /ˈmiːn/ | 核心 | v | 意思是 | mean / means / meant / meant / meaning | to mean |
| happen | /ˈhæpən/ | 核心 | v | 發生 | happen / happens / happened / happened / happening | what happened? |
| become | /bɪˈkʌm/ | 核心 | v | 變成 | become / becomes / became / became / becoming | become a teacher |
| stay | /ˈsteɪ/ | 核心 | v | 停留 | stay / stays / stayed / stayed / staying | stay at home |
| leave | /ˈliːv/ | 核心 | v | 離開 | leave / leaves / left / left / leaving | leave the room |
| arrive | /ɚˈaɪv/ | 核心 | v | 抵達 | arrive / arrives / arrived / arrived / arriving | arrive on time |
| return | /ɹɪˈtɝn/ | 核心 | v | 回來 | return / returns / returned / returned / returning | return home |
| call | /ˈkɔl/ | 核心 | v | 打電話；叫 | call / calls / called / called / calling | call a friend |
| sing | /ˈsɪŋ/ | 核心 | v | 唱歌 | sing / sings / sang / sang / singing | sing a song |
| dance | /ˈdæns/ | 核心 | v | 跳舞 | dance / dances / danced / danced / dancing | dance with music |
| swim | /ˈswɪm/ | 擴充 | v | 游泳 | swim / swims / swam / swam / swimming | swim in the sea |
| jump | /ˈdʒʌmp/ | 核心 | v | 跳 | jump / jumps / jumped / jumped / jumping | jump high |
| climb | /ˈklaɪm/ | 擴充 | v | 爬 | climb / climbs / climbed / climbed / climbing | climb the mountain |
| fall | /ˈfɔl/ | 核心 | v | 跌倒 | fall / falls / fell / fallen / falling | fall down |
| push | /ˈpʊʃ/ | 核心 | v | 推 | push / pushes / pushed / pushed / pushing | push the door |
| pull | /ˈpʊl/ | 核心 | v | 拉 | pull / pulls / pulled / pulled / pulling | pull the door |
| throw | /ˈθɹoʊ/ | 核心 | v | 丟 | throw / throws / threw / thrown / throwing | throw the ball |
| catch | /ˈkætʃ/ | 核心 | v | 抓住 | catch / catches / caught / caught / catching | catch the ball |
| win | /ˈwɪn/ | 核心 | v | 贏 | win / wins / won / won / winning | win the game |
| dream | /ˈdɹiːm/ | 擴充 | v | 夢 | dream / dreams / dreamed / dreamed / dreaming | have a dream |
| rest | /ˈɹɛst/ | 核心 | v/n | 休息 | rest / rests / rested / rested / resting | rest a little |
| marry | /ˈmɛɹi/ | 擴充 | v | 結婚 | marry / marries / married / married / marrying | marry a friend |
| raise | /ˈɹeɪz/ | 核心 | v | 養育；提高 | raise / raises / raised / raised / raising | raise your hand |
| count | /ˈkaʊnt/ | 擴充 | v | 數；計算 | count / counts / counted / counted / counting | count the money |
| taste | /ˈteɪst/ | 擴充 | v | 嘗 | taste / tastes / tasted / tasted / tasting | taste the food |
| smell | /ˈsmɛl/ | 擴充 | v | 聞；發出味道 | smell / smells / smelled / smelled / smelling | smell the coffee |
| touch | /ˈtʌtʃ/ | 擴充 | v | 觸碰 | touch / touches / touched / touched / touching | touch the wall |
| share | /ˈʃɛɹ/ | 核心 | v | 分享 | share / shares / shared / shared / sharing | share the food |
| join | /ˈdʒɔɪn/ | 擴充 | v | 加入 | join / joins / joined / joined / joining | join the game |
| follow | /ˈfɑloʊ/ | 核心 | v | 跟隨 | follow / follows / followed / followed / following | follow me |
| lead | /liːd/ | 核心 | v | 領導 | lead / leads / led / led / leading | lead the group |
| hit | /ˈhɪt/ | 核心 | v | 打；撞到 | hit / hits / hit / hit / hiting | hit the ball |
| enter | /ˈɛntɚ/ | 核心 | v | 進入 | enter / enters / entered / entered / entering | enter the room |
| pass | /ˈpæs/ | 核心 | v | 通過；傳遞 | pass / passes / passed / passed / passing | pass the salt |
| paint | /ˈpeɪnt/ | 擴充 | v | 畫；油漆 | paint / paints / painted / painted / painting | paint the wall |
| draw | /ˈdɹɔ/ | 擴充 | v | 畫 | draw / draws / drawed / drawed / drawing | draw a picture |
| feed | /ˈfiːd/ | 擴充 | v | 餵 | feed / feeds / feeded / feeded / feeding | feed the child |
| hang | /ˈhæŋ/ | 擴充 | v | 掛 | hang / hangs / hung / hung / hanging | hang the coat |
| spread | /ˈspɹɛd/ | 擴充 | v | 傳播；攤開 | spread / spreads / spreaded / spreaded / spreading | spread the map |
| cover | /ˈkʌvɚ/ | 擴充 | v | 蓋住；覆蓋 | cover / covers / covered / covered / covering | cover the table |
| fill | /ˈfɪl/ | 擴充 | v | 裝滿 | fill / fills / filled / filled / filling | fill the cup |
| empty | /ˈɛmpti/ | 核心 | v/adj | 倒空；空的 | empty / empties / emptied / emptied / emptying | empty the box |
| lock | /ˈlɑk/ | 擴充 | v | 鎖上 | lock / locks / locked / locked / locking | lock the door |
| knock | /ˈnɑk/ | 擴充 | v | 敲 | knock / knocks / knocked / knocked / knocking | knock at the door |
| ring | /ˈɹɪŋ/ | 核心 | v | 響；打電話 | ring / rings / rang / rung / ringing | the phone rings |
| wave | /ˈweɪv/ | 擴充 | v | 揮手；波浪 | wave / waves / waved / waved / waving | wave goodbye |
| point | /ˈpɔɪnt/ | 擴充 | v/n | 指；點；看法 | point / points / pointed / pointed / pointing | point to the door |
| smile | /ˈsmaɪl/ | 擴充 | v | 微笑 | smile / smiles / smiled / smiled / smiling | smile at me |
| laugh | /ˈlæf/ | 擴充 | v | 笑 | laugh / laughs / laughed / laughed / laughing | laugh together |
| cry | /ˈkɹaɪ/ | 擴充 | v | 哭 | cry / cries / cried / cried / crying | cry a little |
| shout | /ˈʃaʊt/ | 擴充 | v | 喊 | shout / shouts / shouted / shouted / shouting | shout for help |
| print | /ˈpɹɪnt/ | 擴充 | v | 印 | print / prints / printed / printed / printing | print a photo |
| copy | /ˈkɑpi/ | 擴充 | v | 複印 | copy / copies / copied / copied / copying | copy the message |
| save | /ˈseɪv/ | 擴充 | v | 儲存；救 | save / saves / saved / saved / saving | save money |
| spend | /ˈspɛnd/ | 核心 | v | 花費 | spend / spends / spent / spent / spending | spend money |
| add | /ˈæd/ | 擴充 | v | 增加；加 | add / adds / added / added / adding | add some water |
| allow | /əˈlaʊ/ | 核心 | v | 允許 | allow / allows / allowed / allowed / allowing | allow me to go |
| include | /ˌɪˈnkluːd/ | 核心 | v | 包含 | include / includes / included / included / including | include the price |
| show | /ˈʃoʊ/ | 擴充 | v | 顯示；給…看 | show / shows / showed / shown / showing | show me |
| cause | /ˈkɑz/ | 擴充 | v/n | 造成；原因 | cause / causes / caused / caused / causing | cause a problem |
| prepare | /pɹiˈpɛɹ/ | 擴充 | v | 準備 | prepare / prepares / prepared / prepared / preparing | prepare dinner |
| continue | /kəˈntɪnju/ | 擴充 | v | 繼續 | continue / continues / continued / continued / continuing | continue to work |
| notice | /ˈnoʊtəs/ | 擴充 | v | 注意到 | notice / notices / noticed / noticed / noticing | I notice a noise |
| believe | /bɪˈliːv/ | 核心 | v | 相信 | believe / believes / believed / believed / believing | believe me |
| expect | /ɪˈkspɛkt/ | 擴充 | v | 預期 | expect / expects / expected / expected / expecting | I expect rain |
| explain | /ɪˈkspleɪn/ | 核心 | v | 解釋 | explain / explains / explained / explained / explaining | explain it again |
| describe | /dɪˈskɹaɪb/ | 核心 | v | 描述 | describe / describes / described / described / describing | describe the room |
| agree | /əˈɡɹiː/ | 擴充 | v | 同意 | agree / agrees / agreed / agreed / agreeing | I agree |
| check | /ˈtʃɛk/ | 擴充 | v | 檢查 | check / checks / checked / checked / checking | check the time |
| travel | /ˈtɹævəl/ | 擴充 | v | 旅行 | travel / travels / traveled / traveled / traveling | travel by train |
| translate | /tɹæˈnzleɪt/ | 擴充 | v | 翻譯 | translate / translates / translated / translated / translating | translate the words |
| behave | /bɪˈheɪv/ | 擴充 | v | 表現 | behave / behaves / behaved / behaved / behaving | behave well |
| heal | /ˈhiːl/ | 擴充 | v | 癒合 | heal / heals / healed / healed / healing | heal fast |
| borrow | /ˈbɑˌɹoʊ/ | 擴充 | v | 借入 | borrow / borrows / borrowed / borrowed / borrowing | borrow a book |
| lend | /ˈlɛnd/ | 擴充 | v | 借出 | lend / lends / lent / lent / lending | lend me money |
| rent | /ˈɹɛnt/ | 擴充 | v | 租 | rent / rents / rented / rented / renting | rent a room |
| order | /ˈɔɹdɚ/ | 擴充 | v | 訂購 | order / orders / ordered / ordered / ordering | order the food |
| deliver | /dɪˈlɪvɚ/ | 擴充 | v | 送遞 | deliver / delivers / delivered / delivered / delivering | deliver the food |
| offer | /ˈɔfɚ/ | 擴充 | v | 提供 | offer / offers / offered / offered / offering | offer help |
| support | /səˈpɔɹt/ | 核心 | v/n | 支持 | support / supports / supported / supported / supporting | support a friend |
| affect | /əˈfɛkt/ | 擴充 | v | 影響 | affect / affects / affected / affected / affecting | affect the price |
| increase | /ˌɪˈnkɹiːs/ | 擴充 | v | 增加 | increase / increases / increased / increased / increasing | increase the price |
| decrease | /dɪˈkɹiːs/ | 擴充 | v | 減少 | decrease / decreases / decreased / decreased / decreasing | decrease the price |
| complete | /kəˈmpliːt/ | 擴充 | v | 完成 | complete / completes / completed / completed / completing | complete the work |
| compare | /kəˈmpɛɹ/ | 擴充 | v | 比較 | compare / compares / compared / compared / comparing | compare the 2 |
| discuss | /dɪˈskʌs/ | 擴充 | v | 討論 | discuss / discusses / discussed / discussed / discussing | discuss the plan |
| refuse | /ɹəˈfjuːz/ | 擴充 | v | 拒絕 | refuse / refuses / refused / refused / refusing | refuse the offer |
| avoid | /əˈvɔɪd/ | 擴充 | v | 避免 | avoid / avoids / avoided / avoided / avoiding | avoid the busy road |
| prevent | /pɹɪˈvɛnt/ | 擴充 | v | 防止 | prevent / prevents / prevented / prevented / preventing | prevent a fire |
| improve | /ˌɪˈmpɹuːv/ | 擴充 | v | 改善 | improve / improves / improved / improved / improving | improve the quality |
| develop | /dɪˈvɛləp/ | 擴充 | v | 發展 | develop / develops / developed / developed / developing | develop a plan |
| produce | /pɹəˈduːs/ | 擴充 | v | 生產 | produce / produces / produced / produced / producing | produce food |
| create | /kɹiˈeɪt/ | 擴充 | v | 創造 | create / creates / created / created / creating | create a story |
| build | /ˈbɪld/ | 核心 | v | 建造 | build / builds / built / built / building | build a house |
| destroy | /dɪˈstɹɔɪ/ | 擴充 | v | 破壞 | destroy / destroys / destroyed / destroyed / destroying | destroy the old house |
| protect | /pɹəˈtɛkt/ | 核心 | v | 保護 | protect / protects / protected / protected / protecting | protect your family |
| manage | /ˈmænədʒ/ | 擴充 | v | 管理 | manage / manages / managed / managed / managing | manage a group |
| depend | /dɪˈpɛnd/ | 擴充 | v | 取決於 | depend / depends / depended / depended / depending | depend on the weather |
| seem | /ˈsiːm/ | 核心 | v | 似乎 | seem / seems / seemed / seemed / seeming | seem easy |
| appear | /əˈpɪɹ/ | 核心 | v | 出現；似乎 | appear / appears / appeared / appeared / appearing | appear at the door |
| exist | /ɪˈɡzɪst/ | 核心 | v | 存在 | exist / exists / existed / existed / existing | does it exist? |
| remain | /ɹɪˈmeɪn/ | 擴充 | v | 保持 | remain / remains / remained / remained / remaining | remain at home |
| contain | /kəˈnteɪn/ | 擴充 | v | 包含 | contain / contains / contained / contained / containing | contain water |
| require | /ˌɹiːˈkwaɪɚ/ | 擴充 | v | 需要；要求 | require / requires / required / required / requiring | require much time |
| provide | /pɹəˈvaɪd/ | 核心 | v | 提供 | provide / provides / provided / provided / providing | provide food |
| receive | /ɹəˈsiːv/ | 核心 | v | 收到 | receive / receives / received / received / receiving | receive a letter |
| accept | /æˈksɛpt/ | 核心 | v | 接受 | accept / accepts / accepted / accepted / accepting | accept the food |
| serve | /ˈsɝv/ | 擴充 | v | 服務；上菜 | serve / serves / served / served / serving | serve food |
| press | /ˈpɹɛs/ | 擴充 | v | 按；壓 | press / presses / pressed / pressed / pressing | press the light |
| pour | /ˈpɔɹ/ | 擴充 | v | 倒 | pour / pours / poured / poured / pouring | pour the water |
| boil | /ˈbɔɪl/ | 擴充 | v | 煮沸 | boil / boils / boiled / boiled / boiling | boil the water |
| matter | /ˈmætɚ/ | 擴充 | v | 要緊 | matter / matters / mattered / mattered / mattering | it does not matter |
| sound | /ˈsaʊnd/ | 擴充 | v/n | 聽起來；聲音 | sound / sounds / sounded / sounded / sounding | sound good |
| cross | /ˈkɹɔs/ | 擴充 | v | 穿過 | cross / crosses / crossed / crossed / crossing | cross the road |
| understand | /ˌʌndɚˈstænd/ | 核心 | v | 理解 | understand / understands / understood / understood / understanding | I understand |
| talk | /ˈtɔk/ | 核心 | v | 說話；談 | talk / talks / talked / talked / talking | talk to a friend |
| reach | /ˈɹiːtʃ/ | 核心 | v | 到達；伸手拿 | reach / reaches / reached / reached / reaching | reach the shop |
| act | /ˈækt/ | 擴充 | v | 行動；表演 | act / acts / acted / acted / acting | to act |
| bend | /ˈbɛnd/ | 擴充 | v | 彎曲 | bend / bends / bended / bended / bending | to bend |
| breathe | /ˈbɹiːð/ | 擴充 | v | 呼吸 | breathe / breathes / breathed / breathed / breathing | to breathe |
| burn | /ˈbɝn/ | 擴充 | v | 燒 | burn / burns / burned / burned / burning | to burn |
| disappear | /ˌdɪsəˈpɪɹ/ | 擴充 | v | 消失 | disappear / disappears / disappeared / disappeared / disappearing | to disappear |
| drop | /ˈdɹɑp/ | 擴充 | v | 掉落；讓掉落 | drop / drops / dropped / dropped / dropping | to drop |
| enjoy | /ˌɛˈndʒɔɪ/ | 擴充 | v | 喜歡 | enjoy / enjoys / enjoyed / enjoyed / enjoying | to enjoy |
| flow | /ˈfloʊ/ | 擴充 | v | 流動 | flow / flows / flowed / flowed / flowing | to flow |
| hide | /ˈhaɪd/ | 擴充 | v | 藏 | hide / hides / hided / hided / hiding | to hide |
| kill | /ˈkɪl/ | 擴充 | v | 殺 | kill / kills / killed / killed / killing | to kill |
| mix | /ˈmɪks/ | 擴充 | v | 混合 | mix / mixes / mixed / mixed / mixing | to mix |
| pray | /ˈpɹeɪ/ | 擴充 | v | 祈禱 | pray / prays / prayed / prayed / praying | to pray |
| repeat | /ɹɪˈpiːt/ | 擴充 | v | 重複 | repeat / repeats / repeated / repeated / repeating | repeat the word |
| respect | /ɹɪˈspɛkt/ | 擴充 | v | 尊重 | respect / respects / respected / respected / respecting | to respect |
| search | /ˈsɝtʃ/ | 擴充 | v | 尋找 | search / searches / searched / searched / searching | to search |
| sew | /ˈsoʊ/ | 擴充 | v | 縫 | sew / sews / sewed / sewed / sewing | to sew |
| shake | /ˈʃeɪk/ | 擴充 | v | 搖 | shake / shakes / shaked / shaked / shaking | to shake |
| shoot | /ˈʃuːt/ | 擴充 | v | 射 | shoot / shoots / shooted / shooted / shooting | to shoot |
| step | /ˈstɛp/ | 擴充 | v | 踏 | step / steps / stepped / stepped / stepping | to step |
| twist | /ˈtwɪst/ | 擴充 | v | 扭轉 | twist / twists / twisted / twisted / twisting | to twist |
| zip | /ˈzɪp/ | 擴充 | v | 拉鍊 | zip / zips / ziped / ziped / ziping | to zip |
| fight | /ˈfaɪt/ | 擴充 | v | 打鬥 | fight / fights / fighted / fighted / fighting | to fight |
| fit | /ˈfɪt/ | 擴充 | v | 合身 | fit / fits / fitted / fitted / fitting | it fits me |
| force | /ˈfɔɹs/ | 擴充 | v | 用力 | force / forces / forced / forced / forcing | to force |
| measure | /ˈmɛʒɚ/ | 擴充 | v | 量 | measure / measures / measured / measured / measuring | to measure |
| tie | /ˈtaɪ/ | 擴充 | v | 綁 | tie / ties / tied / tied / tying | to tie |
| trust | /ˈtɹʌst/ | 擴充 | v | 信任 | trust / trusts / trusted / trusted / trusting | to trust |
| vote | /ˈvoʊt/ | 擴充 | v | 投票 | vote / votes / voted / voted / voting | to vote |
| match | /ˈmætʃ/ | 擴充 | v/n | 比；比賽 | match / matches / matched / matched / matching | to match |
| announce | /əˈnaʊns/ | 擴充 | v | 宣布 | announce / announces / announced / announced / announcing | to announce |
| hold | /ˈhoʊld/ | 擴充 | v | 拿著；容納 | hold / holds / held / held / holding | to hold |

### 2.8 性質（核心 74 ＋ 擴充 80 ＝ 154）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| good | /ˈɡʊd/ | 核心 | adj | 好 | good / better / best | a good day |
| bad | /ˈbæd/ | 核心 | adj | 壞 | bad / worse / worst | a bad day |
| big | /ˈbɪɡ/ | 核心 | adj | 大 | big / bigger / biggest | a big house |
| small | /ˈsmɔl/ | 核心 | adj | 小 | small / smaller / smallest | a small room |
| long | /ˈlɔŋ/ | 核心 | adj | 長 | long / longer / longest | a long road |
| short | /ˈʃɔɹt/ | 核心 | adj | 短 | short / shorter / shortest | a short story |
| tall | /ˈtɔl/ | 核心 | adj | 高（人或樹） | tall / taller / tallest | a tall man |
| high | /ˈhaɪ/ | 核心 | adj | 高 | high / higher / highest | a high price |
| low | /ˈloʊ/ | 核心 | adj | 低 | low / lower / lowest | a low price |
| old | /ˈoʊld/ | 核心 | adj | 老；舊 | old / older / oldest | an old man |
| new | /nuː/ | 核心 | adj | 新 | new / newer / newest | a new job |
| young | /ˈjʌŋ/ | 核心 | adj | 年輕 | young / younger / youngest | a young woman |
| hot | /ˈhɑt/ | 核心 | adj | 熱 | hot / hotter / hottest | hot water |
| cold | /ˈkoʊld/ | 核心 | adj | 冷 | cold / colder / coldest | cold weather |
| warm | /ˈwɔɹm/ | 核心 | adj | 溫暖 | warm / warmer / warmest | a warm room |
| cool | /ˈkuːl/ | 核心 | adj | 涼爽 | cool / cooler / coolest | cool water |
| wet | /ˈwɛt/ | 核心 | adj | 濕 | wet / wetter / wettest | wet clothes |
| dry | /ˈdɹaɪ/ | 核心 | adj | 乾 | dry / drier / driest | dry air |
| easy | /ˈiːzi/ | 核心 | adj | 容易 | easy / easier / easiest | an easy question |
| hard | /ˈhɑɹd/ | 核心 | adj | 難；硬的 | hard / harder / hardest | a hard question |
| difficult | /ˈdɪfəkəlt/ | 核心 | adj | 困難 | difficult / more difficult / most difficult | a difficult question |
| simple | /ˈsɪmpəl/ | 核心 | adj | 簡單 | simple / simpler / simplest | a simple answer |
| important | /ˌɪˈmpɔɹtənt/ | 核心 | adj | 重要 | important / more important / most important | an important thing |
| different | /ˈdɪfɚənt/ | 核心 | adj | 不同 | different / more different / most different | different from me |
| wrong | /ˈɹɔŋ/ | 核心 | adj | 錯 | wrong / wronger / wrongest | the wrong answer |
| true | /ˈtɹuː/ | 核心 | adj | 真 | true / truer / truest | a true story |
| false | /ˈfɔls/ | 核心 | adj | 假 | false / falser / falsest | a false story |
| real | /ˈɹiːl/ | 核心 | adj | 真實 | real / realer / realest | a real story |
| nice | /ˈnaɪs/ | 核心 | adj | 好；友善 | nice / nicer / nicest | a nice day |
| fine | /ˈfaɪn/ | 核心 | adj | 細的；很好 | fine / finer / finest | fine, thanks |
| free | /ˈfɹiː/ | 核心 | adj | 免費；自由 | free / freer / freest | free food |
| busy | /ˈbɪzi/ | 核心 | adj | 忙 | busy / busier / busiest | a busy day |
| happy | /ˈhæpi/ | 核心 | adj | 快樂 | happy / happier / happiest | a happy child |
| sad | /ˈsæd/ | 核心 | adj | 悲傷 | sad / sadder / saddest | a sad story |
| angry | /ˈæŋɡɹi/ | 擴充 | adj | 生氣 | angry / angrier / angriest | an angry man |
| tired | /ˈtaɪɚd/ | 核心 | adj | 疲累 | tired / tireder / tiredest | very tired |
| hungry | /ˈhʌŋɡɹi/ | 擴充 | adj | 餓 | hungry / hungrier / hungriest | I am hungry |
| sick | /ˈsɪk/ | 核心 | adj | 生病 | sick / sicker / sickest | a sick child |
| healthy | /ˈhɛlθi/ | 核心 | adj | 健康 | healthy / more healthy / most healthy | a healthy body |
| strong | /ˈstɹɔŋ/ | 核心 | adj | 強壯 | strong / stronger / strongest | a strong man |
| weak | /ˈwiːk/ | 核心 | adj | 弱 | weak / weaker / weakest | a weak man |
| heavy | /ˈhɛvi/ | 核心 | adj | 重 | heavy / heavier / heaviest | a heavy bag |
| fast | /ˈfæst/ | 核心 | adj/adv | 快 | fast / faster / fastest | a fast car |
| slow | /ˈsloʊ/ | 核心 | adj/adv | 慢 | slow / slower / slowest | a slow bus |
| beautiful | /ˈbjuːtɪfəl/ | 核心 | adj | 美麗 | beautiful / more beautiful / most beautiful | a beautiful day |
| ugly | /ˈʌɡli/ | 擴充 | adj | 醜 | ugly / uglier / ugliest | very ugly |
| afraid | /əˈfɹeɪd/ | 核心 | adj | 害怕 | afraid / afraider / afraidest | afraid at night |
| fun | /ˈfʌn/ | 核心 | adj/adv | 有趣 | fun / funer / funest | a fun game |
| interesting | /ˈɪntɹəstɪŋ/ | 核心 | adj | 有趣 | interesting / more interesting / most interesting | an interesting story |
| boring | /ˈbɔɹɪŋ/ | 擴充 | adj | 無聊 | boring / more boring / most boring | very boring |
| possible | /ˈpɑsəbəl/ | 核心 | adj | 可能 | possible / more possible / most possible | it is possible |
| clear | /ˈklɪɹ/ | 核心 | adj | 清楚 | clear / clearer / clearest | a clear answer |
| ready | /ˈɹɛdi/ | 核心 | adj | 準備好 | ready / readier / readiest | I am ready |
| sure | /ˈʃʊɹ/ | 核心 | adj | 確定 | sure / surer / surest | I am sure |
| funny | /ˈfʌni/ | 擴充 | adj | 好笑 | funny / funnier / funniest | very funny |
| strange | /ˈstɹeɪndʒ/ | 擴充 | adj | 奇怪 | strange / more strange / most strange | very strange |
| quiet | /ˈkwaɪət/ | 擴充 | adj | 安靜 | quiet / quieter / quietest | very quiet |
| noisy | /ˈnɔɪzi/ | 擴充 | adj | 吵 | noisy / noisier / noisiest | very noisy |
| rich | /ˈɹɪtʃ/ | 核心 | adj | 有錢；豐富 | rich / richer / richest | a rich family |
| poor | /ˈpuːɹ/ | 核心 | adj | 窮；可憐 | poor / poorer / poorest | a poor family |
| sweet | /ˈswiːt/ | 核心 | adj | 甜 | sweet / sweeter / sweetest | sweet tea |
| sour | /ˈsaʊɚ/ | 擴充 | adj | 酸 | sour / sourer / sourest | very sour |
| bitter | /ˈbɪtɚ/ | 擴充 | adj | 苦 | bitter / bitterer / bitterest | very bitter |
| soft | /ˈsɑft/ | 核心 | adj | 軟 | soft / softer / softest | a soft bed |
| sharp | /ˈʃɑɹp/ | 擴充 | adj | 尖銳 | sharp / sharper / sharpest | very sharp |
| smooth | /ˈsmuːð/ | 擴充 | adj | 平滑 | smooth / smoother / smoothest | very smooth |
| rough | /ˈɹʌf/ | 擴充 | adj | 粗糙 | rough / rougher / roughest | very rough |
| thin | /ˈθɪn/ | 擴充 | adj | 薄 | thin / thinner / thinnest | very thin |
| wide | /ˈwaɪd/ | 核心 | adj | 寬 | wide / wider / widest | a wide road |
| narrow | /ˈnɛɹoʊ/ | 擴充 | adj | 窄 | narrow / narrower / narrowest | very narrow |
| deep | /ˈdiːp/ | 核心 | adj | 深 | deep / deeper / deepest | a deep river |
| full | /ˈfʊl/ | 核心 | adj | 滿 | full / fuller / fullest | a full cup |
| round | /ˈɹaʊnd/ | 擴充 | adj | 圓 | round / rounder / roundest | very round |
| straight | /ˈstɹeɪt/ | 擴充 | adj/adv | 直 | straight / more straight / most straight | very straight |
| brown | /ˈbɹaʊn/ | 核心 | adj | 棕色 | brown / browner / brownest | brown bread |
| black | /ˈblæk/ | 核心 | adj | 黑色 | black / blacker / blackest | a black cat |
| white | /ˈwaɪt/ | 核心 | adj | 白色 | white / whiter / whitest | a white shirt |
| red | /ˈɹɛd/ | 核心 | adj | 紅色 | red / reder / redest | a red apple |
| blue | /ˈbluː/ | 核心 | adj | 藍色 | blue / bluer / bluest | a blue sky |
| green | /ˈɡɹiːn/ | 核心 | adj | 綠色 | green / greener / greenest | green tea |
| yellow | /ˈjɛloʊ/ | 核心 | adj | 黃色 | yellow / yellower / yellowest | a yellow flower |
| orange | /ˈɔɹəndʒ/ | 核心 | adj | 橘色 | orange / oranger / orangest | an orange cat |
| pink | /ˈpɪŋk/ | 核心 | adj | 粉紅色 | pink / pinker / pinkest | a pink flower |
| purple | /ˈpɝpəl/ | 擴充 | adj | 紫色 | purple / purpler / purplest | very purple |
| gray | /ˈɡɹeɪ/ | 擴充 | adj | 灰色 | gray / grayer / grayest | very gray |
| special | /ˈspɛʃəl/ | 核心 | adj | 特別的 | special / more special / most special | a special day |
| safe | /ˈseɪf/ | 核心 | adj | 安全的 | safe / safer / safest | a safe place |
| dangerous | /ˈdeɪndʒɚəs/ | 擴充 | adj | 危險的 | dangerous / more dangerous / most dangerous | very dangerous |
| careful | /ˈkɛɹfəl/ | 核心 | adj | 小心的 | careful / more careful / most careful | be careful |
| friendly | /ˈfɹɛndli/ | 擴充 | adj | 友善的 | friendly / more friendly / most friendly | very friendly |
| kind | /ˈkaɪnd/ | 核心 | adj/n | 善良的；種類 | kind / kinds | a kind man |
| polite | /pəˈlaɪt/ | 擴充 | adj | 有禮貌的 | polite / politer / politest | very polite |
| honest | /ˈɑnəst/ | 擴充 | adj | 誠實的 | honest / honester / honestest | very honest |
| brave | /ˈbɹeɪv/ | 擴充 | adj | 勇敢的 | brave / braver / bravest | very brave |
| lazy | /ˈleɪzi/ | 擴充 | adj | 懶惰的 | lazy / lazier / laziest | very lazy |
| clever | /ˈklɛvɚ/ | 擴充 | adj | 聰明的 | clever / cleverer / cleverest | very clever |
| stupid | /ˈstuːpəd/ | 擴充 | adj | 笨的 | stupid / stupider / stupidest | very stupid |
| crazy | /ˈkɹeɪzi/ | 擴充 | adj | 瘋狂的 | crazy / crazier / craziest | very crazy |
| serious | /ˈsɪɹiəs/ | 擴充 | adj | 嚴肅的 | serious / more serious / most serious | very serious |
| nervous | /ˈnɝvəs/ | 擴充 | adj | 緊張的 | nervous / more nervous / most nervous | very nervous |
| calm | /ˈkɑm/ | 擴充 | adj | 平靜的 | calm / calmer / calmest | very calm |
| comfortable | /ˈkʌmfɚtəbəl/ | 擴充 | adj | 舒服的 | comfortable / more comfortable / most comfortable | very comfortable |
| popular | /ˈpɑpjəlɚ/ | 擴充 | adj | 受歡迎的 | popular / more popular / most popular | very popular |
| correct | /kɚˈɛkt/ | 核心 | adj | 正確的 | correct / more correct / most correct | the correct answer |
| necessary | /ˈnɛsəˌsɛɹi/ | 擴充 | adj | 必要的 | necessary / more necessary / most necessary | very necessary |
| likely | /ˈlaɪkli/ | 擴充 | adj | 可能的 | likely / likelier / likeliest | very likely |
| certain | /ˈsɝtən/ | 核心 | adj | 確定的 | certain / more certain / most certain | a certain fact |
| quick | /ˈkwɪk/ | 擴充 | adj | 快的 | quick / quicker / quickest | very quick |
| sudden | /ˈsʌdən/ | 擴充 | adj | 突然的 | sudden / suddener / suddenest | very sudden |
| terrible | /ˈtɛɹəbəl/ | 擴充 | adj | 糟糕的 | terrible / more terrible / most terrible | very terrible |
| wonderful | /ˈwʌndɚfəl/ | 擴充 | adj | 極好的 | wonderful / more wonderful / most wonderful | very wonderful |
| pretty | /ˈpɹɪti/ | 擴充 | adj | 漂亮的 | pretty / prettier / prettiest | very pretty |
| alone | /əˈloʊn/ | 擴充 | adj | 獨自的 | alone / aloner / alonest | very alone |
| dirty | /ˈdɝti/ | 核心 | adj | 髒 | dirty / dirtier / dirtiest | dirty clothes |
| glad | /ˈɡlæd/ | 擴充 | adj | 高興的 | glad / glader / gladest | very glad |
| proud | /ˈpɹaʊd/ | 擴充 | adj | 驕傲的 | proud / prouder / proudest | very proud |
| lonely | /ˈloʊnli/ | 擴充 | adj | 孤單的 | lonely / lonelier / loneliest | very lonely |
| bored | /ˈbɔɹd/ | 擴充 | adj | 無聊的 | bored / boreder / boredest | very bored |
| worried | /ˈwɝid/ | 擴充 | adj | 擔心的 | worried / more worried / most worried | very worried |
| excited | /ɪˈksaɪtəd/ | 擴充 | adj | 興奮的 | excited / more excited / most excited | very excited |
| surprised | /sɚˈpɹaɪzd/ | 擴充 | adj | 驚訝的 | surprised / more surprised / most surprised | very surprised |
| upset | /əˈpsɛt/ | 擴充 | adj | 難過的；生氣的 | upset / upseter / upsetest | very upset |
| shy | /ˈʃaɪ/ | 擴充 | adj | 害羞的 | shy / shier / shiest | very shy |
| color | /ˈkʌlɚ/ | 核心 | n | 顏色 | color / colors | the color |
| alive | /əˈlaɪv/ | 擴充 | adj | 活著的 | alive / aliver / alivest | very alive |
| available | /əˈveɪləbəl/ | 擴充 | adj | 可以拿到的 | available / more available / most available | very available |
| bright | /ˈbɹaɪt/ | 擴充 | adj | 明亮 | bright / brighter / brightest | very bright |
| cheap | /ˈtʃiːp/ | 擴充 | adj | 便宜 | cheap / cheaper / cheapest | very cheap |
| dark | /ˈdɑɹk/ | 擴充 | adj | 黑暗的 | dark / darker / darkest | very dark |
| dead | /ˈdɛd/ | 擴充 | adj | 死的 | dead / deader / deadest | very dead |
| equal | /ˈiːkwəl/ | 擴充 | adj | 相同的 | equal / equaler / equalest | very equal |
| exact | /ɪˈɡzækt/ | 擴充 | adj | 完全正確的 | exact / exacter / exactest | very exact |
| fair | /ˈfɛɹ/ | 擴充 | adj | 公平的 | fair / fairer / fairest | very fair |
| fat | /ˈfæt/ | 擴充 | adj | 胖的 | fat / fatter / fattest | very fat |
| frozen | /ˈfɹoʊzən/ | 擴充 | adj | 結冰的 | frozen / frozener / frozenest | very frozen |
| ill | /ˈɪl/ | 擴充 | adj | 生病的 | ill / iller / illest | very ill |
| loud | /ˈlaʊd/ | 擴充 | adj | 大聲的 | loud / louder / loudest | very loud |
| normal | /ˈnɔɹməl/ | 擴充 | adj | 正常的 | normal / normaler / normalest | very normal |
| relaxed | /ɹɪˈlækst/ | 擴充 | adj | 放鬆的 | relaxed / more relaxed / most relaxed | very relaxed |
| religious | /ɹɪˈlɪdʒəs/ | 擴充 | adj | 宗教的 | religious / more religious / most religious | very religious |
| shiny | /ˈʃaɪni/ | 擴充 | adj | 發亮的 | shiny / shinier / shiniest | very shiny |
| smart | /ˈsmɑɹt/ | 擴充 | adj | 聰明的 | smart / smarter / smartest | very smart |
| thick | /ˈθɪk/ | 擴充 | adj | 厚的 | thick / thicker / thickest | very thick |
| tight | /ˈtaɪt/ | 擴充 | adj | 緊的 | tight / tighter / tightest | very tight |
| usual | /ˈjuːʒuəl/ | 擴充 | adj | 一般的 | usual / usualer / usualest | very usual |
| valuable | /ˈvæljəbəl/ | 擴充 | adj | 貴重的 | valuable / more valuable / most valuable | very valuable |
| windy | /ˈwɪndi/ | 擴充 | adj | 有風的 | windy / windier / windiest | very windy |
| flat | /ˈflæt/ | 擴充 | adj | 平的 | flat / flatter / flattest | very flat |
| main | /ˈmeɪn/ | 擴充 | adj | 主要的 | main / mainer / mainest | very main |
| worth | /ˈwɝθ/ | 擴充 | adj | 值得的 | worth / worther / worthest | very worth |
| common | /ˈkɑmən/ | 擴充 | adj | 常見的 | common / commoner / commonest | very common |
| wild | /ˈwaɪld/ | 擴充 | adj | 野生的 | wild / wilder / wildest | very wild |
| awake | /əˈweɪk/ | 擴充 | adj | 醒著的 | awake / awaker / awakest | very awake |
| selfish | /ˈsɛlfɪʃ/ | 擴充 | adj | 自私的 | selfish / more selfish / most selfish | very selfish |

### 2.9 事物（核心 48 ＋ 擴充 133 ＝ 181）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| food | /ˈfuːd/ | 核心 | n | 食物 | food / foods | good food |
| rice | /ˈɹaɪs/ | 核心 | n | 米飯 | rice / rices | eat rice |
| bread | /ˈbɹɛd/ | 擴充 | n | 麵包 | bread / breads | the bread |
| meat | /ˈmiːt/ | 核心 | n | 肉 | meat / meats | meat and rice |
| egg | /ˈɛɡ/ | 擴充 | n | 蛋 | egg / eggs | the egg |
| milk | /ˈmɪlk/ | 核心 | n | 牛奶 | milk / milks | a glass of milk |
| tea | /ˈtiː/ | 核心 | n | 茶 | tea / teas | a cup of tea |
| coffee | /ˈkɑfi/ | 核心 | n | 咖啡 | coffee / coffees | a cup of coffee |
| juice | /ˈdʒuːs/ | 擴充 | n | 果汁 | juice / juices | the juice |
| fruit | /ˈfɹuːt/ | 核心 | n | 水果 | fruit / fruits | a sweet apple |
| apple | /ˈæpəl/ | 核心 | n | 蘋果 | apple / apples | a red apple |
| vegetable | /ˈvɛdʒtəbəl/ | 擴充 | n | 蔬菜 | vegetable / vegetables | the vegetable |
| sugar | /ˈʃʊɡɚ/ | 核心 | n | 糖 | sugar / sugars | too much sugar |
| salt | /ˈsɔlt/ | 核心 | n | 鹽 | salt / salts | a little salt |
| soup | /ˈsuːp/ | 擴充 | n | 湯 | soup / soups | the soup |
| cake | /ˈkeɪk/ | 擴充 | n | 蛋糕 | cake / cakes | the cake |
| potato | /pəˈteɪˌtoʊ/ | 擴充 | n | 馬鈴薯 | potato / potatoes | the potato |
| tomato | /təˈmeɪˌtoʊ/ | 擴充 | n | 番茄 | tomato / tomatoes | the tomato |
| chicken | /ˈtʃɪkən/ | 擴充 | n | 雞；雞肉 | chicken / chickens | the chicken |
| breakfast | /ˈbɹɛkfəst/ | 擴充 | n | 早餐 | breakfast / breakfasts | the breakfast |
| lunch | /ˈlʌntʃ/ | 核心 | n | 午餐 | lunch / lunches | eat lunch |
| dinner | /ˈdɪnɚ/ | 核心 | n | 晚餐 | dinner / dinners | make dinner |
| head | /ˈhɛd/ | 核心 | n | 頭 | head / heads | my head |
| hair | /ˈhɛɹ/ | 擴充 | n | 頭髮 | hair / hairs | long hair |
| eye | /aɪ/ | 核心 | n | 眼睛 | eye / eyes | big eyes |
| ear | /ˈiːɹ/ | 擴充 | n | 耳朵 | ear / ears | 2 ears |
| nose | /ˈnoʊz/ | 核心 | n | 鼻子 | nose / noses | a small nose |
| mouth | /ˈmaʊθ/ | 核心 | n | 嘴巴 | mouth / mouths | open your mouth |
| tooth | /ˈtuːθ/ | 擴充 | n | 牙齒 | tooth / teeth | clean your teeth |
| tongue | /ˈtʌŋ/ | 擴充 | n | 舌頭 | tongue / tongues | the tongue |
| neck | /ˈnɛk/ | 擴充 | n | 脖子 | neck / necks | the neck |
| shoulder | /ˈʃoʊldɚ/ | 擴充 | n | 肩膀 | shoulder / shoulders | the shoulder |
| arm | /ˈɑɹm/ | 擴充 | n | 手臂 | arm / arms | my arm |
| hand | /ˈhænd/ | 核心 | n | 手 | hand / hands | wash your hands |
| finger | /ˈfɪŋɡɚ/ | 擴充 | n | 手指 | finger / fingers | the finger |
| leg | /ˈlɛɡ/ | 擴充 | n | 腿 | leg / legs | my leg |
| foot | /ˈfʊt/ | 核心 | n | 腳 | foot / feet | my foot |
| knee | /ˈniː/ | 擴充 | n | 膝蓋 | knee / knees | the knee |
| heart | /ˈhɑɹt/ | 核心 | n | 心臟 | heart / hearts | my heart |
| stomach | /ˈstʌmək/ | 擴充 | n | 肚子 | stomach / stomaches | the stomach |
| skin | /ˈskɪn/ | 擴充 | n | 皮膚 | skin / skins | the skin |
| bone | /ˈboʊn/ | 擴充 | n | 骨頭 | bone / bones | the bone |
| blood | /ˈblʌd/ | 擴充 | n | 血 | blood / bloods | the blood |
| face | /ˈfeɪs/ | 核心 | n | 臉 | face / faces | wash your face |
| body | /ˈbɑdi/ | 核心 | n | 身體 | body / bodies | a healthy body |
| shirt | /ˈʃɝt/ | 核心 | n | 襯衫 | shirt / shirts | a white shirt |
| pants | /ˈpænts/ | 擴充 | n | 褲子 | pants / pantses | new pants |
| dress | /ˈdɹɛs/ | 擴充 | n | 洋裝；穿（動詞） | dress / dresses | a nice dress |
| coat | /ˈkoʊt/ | 擴充 | n | 外套 | coat / coats | the coat |
| shoes | /ˈʃuːz/ | 擴充 | n | 鞋 | shoes / shoeses | new shoes |
| hat | /ˈhæt/ | 擴充 | n | 帽子 | hat / hats | a big hat |
| socks | /ˈsɑks/ | 擴充 | n | 襪子 | socks / sockses | the socks |
| clothes | /kloʊðz/ | 擴充 | n | 衣服 | clothes / clotheses | the clothes |
| shoe | /ˈʃuː/ | 擴充 | n | 鞋 | shoe / shoes | the shoe |
| glasses | /ˈɡlæsəz/ | 擴充 | n | 眼鏡 | glasses / glasseses | the glasses |
| table | /ˈteɪbəl/ | 核心 | n | 桌子 | table / tables | on the table |
| desk | /ˈdɛsk/ | 擴充 | n | 書桌 | desk / desks | the desk |
| chair | /ˈtʃɛɹ/ | 核心 | n | 椅子 | chair / chairs | a small chair |
| bed | /ˈbɛd/ | 核心 | n | 床 | bed / beds | go to bed |
| sofa | /ˈsoʊfə/ | 擴充 | n | 沙發 | sofa / sofas | the sofa |
| lamp | /ˈlæmp/ | 擴充 | n | 燈 | lamp / lamps | the lamp |
| cup | /ˈkʌp/ | 核心 | n | 杯子 | cup / cups | a cup of tea |
| bowl | /ˈboʊl/ | 擴充 | n | 碗 | bowl / bowls | the bowl |
| plate | /ˈpleɪt/ | 擴充 | n | 盤子 | plate / plates | the plate |
| knife | /ˈnaɪf/ | 核心 | n | 刀 | knife / knives | a sharp knife |
| fork | /ˈfɔɹk/ | 擴充 | n | 叉子 | fork / forks | the fork |
| spoon | /ˈspuːn/ | 擴充 | n | 湯匙 | spoon / spoons | the spoon |
| bottle | /ˈbɑtəl/ | 核心 | n | 瓶子 | bottle / bottles | a water bottle |
| box | /ˈbɑks/ | 核心 | n | 盒子 | box / boxes | a small box |
| bag | /ˈbæɡ/ | 核心 | n | 袋子 | bag / bags | a heavy bag |
| book | /ˈbʊk/ | 核心 | n | 書 | book / books | a good book |
| pen | /ˈpɛn/ | 核心 | n | 筆 | pen / pens | write with a pen |
| pencil | /ˈpɛnsəl/ | 擴充 | n | 鉛筆 | pencil / pencils | the pencil |
| key | /ˈkiː/ | 核心 | n | 鑰匙 | key / keys | the key to the door |
| picture | /ˈpɪktʃɚ/ | 核心 | n | 圖片 | picture / pictures | a nice picture |
| photo | /ˈfoʊˌtoʊ/ | 擴充 | n | 照片 | photo / photos | the photo |
| medicine | /ˈmɛdəsən/ | 核心 | n | 藥 | medicine / medicines | take medicine |
| mirror | /ˈmɪɹɚ/ | 擴充 | n | 鏡子 | mirror / mirrors | the mirror |
| towel | /ˈtaʊəl/ | 擴充 | n | 毛巾 | towel / towels | the towel |
| soap | /ˈsoʊp/ | 擴充 | n | 肥皂 | soap / soaps | the soap |
| umbrella | /əˈmbɹɛlə/ | 擴充 | n | 雨傘 | umbrella / umbrellas | the umbrella |
| radio | /ˈɹeɪdiˌoʊ/ | 擴充 | n | 收音機 | radio / radios | the radio |
| television | /ˈtɛləˌvɪʒən/ | 擴充 | n | 電視 | television / televisions | the television |
| blanket | /ˈblæŋkət/ | 擴充 | n | 毯子 | blanket / blankets | the blanket |
| phone | /ˈfoʊn/ | 核心 | n | 電話 | phone / phones | my phone |
| computer | /kəˈmpjuːtɚ/ | 核心 | n | 電腦 | computer / computers | my computer |
| mouse | /ˈmaʊs/ | 擴充 | n | 滑鼠 | mouse / mice | the mouse |
| screen | /ˈskɹiːn/ | 擴充 | n | 螢幕 | screen / screens | the screen |
| password | /ˈpæˌswɚd/ | 擴充 | n | 密碼 | password / passwords | the password |
| account | /əˈkaʊnt/ | 擴充 | n | 帳戶 | account / accounts | the account |
| website | /ˈwɛˌbsaɪt/ | 擴充 | n | 網站 | website / websites | the website |
| letter | /ˈlɛtɚ/ | 核心 | n | 信；字母 | letter / letters | write a letter |
| email | /iˈmeɪl/ | 擴充 | n | 電子郵件 | email / emails | the email |
| message | /ˈmɛsədʒ/ | 核心 | n | 訊息 | message / messages | a short message |
| meal | /ˈmiːl/ | 擴充 | n | 一餐 | meal / meals | the meal |
| menu | /ˈmɛnju/ | 擴充 | n | 菜單 | menu / menus | the menu |
| bill | /ˈbɪl/ | 核心 | n | 帳單 | bill / bills | pay the bill |
| money | /ˈmʌni/ | 核心 | n | 錢 | money / moneys | much money |
| price | /ˈpɹaɪs/ | 核心 | n | 價格 | price / prices | the price of food |
| cash | /ˈkæʃ/ | 擴充 | n | 現金 | cash / cashes | the cash |
| card | /ˈkɑɹd/ | 核心 | n | 卡片 | card / cards | a bank card |
| kitchen | /ˈkɪtʃən/ | 核心 | n | 廚房 | kitchen / kitchens | the kitchen |
| bedroom | /ˈbɛˌdɹuːm/ | 核心 | n | 臥室 | bedroom / bedrooms | the bedroom |
| classroom | /ˈklæˌsɹuːm/ | 核心 | n | 教室 | classroom / classrooms | the classroom |
| supermarket | /ˈsuːpɚˌmɑɹkɪt/ | 核心 | n | 大超市 | supermarket / supermarkets | the supermarket |
| bookstore | /ˈbʊˌkstɔɹ/ | 核心 | n | 書店 | bookstore / bookstores | the bookstore |
| bath | /ˈbæθ/ | 擴充 | n | 洗澡 | bath / baths | the bath |
| bell | /ˈbɛl/ | 擴充 | n | 鈴 | bell / bells | the bell |
| board | /ˈbɔɹd/ | 擴充 | n | 板子 | board / boards | the board |
| breath | /ˈbɹɛθ/ | 擴充 | n | 呼吸 | breath / breaths | the breath |
| brush | /ˈbɹʌʃ/ | 擴充 | n | 刷子 | brush / brushes | the brush |
| bullet | /ˈbʊlət/ | 擴充 | n | 子彈 | bullet / bullets | the bullet |
| cable | /ˈkeɪbəl/ | 擴充 | n | 纜線 | cable / cables | the cable |
| camera | /ˈkæmɚə/ | 擴充 | n | 攝影機 | camera / cameras | the camera |
| case | /ˈkeɪs/ | 擴充 | n | 箱子；案子 | case / cases | the case |
| chain | /ˈtʃeɪn/ | 擴充 | n | 鏈子 | chain / chains | the chain |
| cheese | /ˈtʃiːz/ | 擴充 | n | 起司 | cheese / cheeses | the cheese |
| cloth | /ˈklɔθ/ | 擴充 | n | 布 | cloth / cloths | the cloth |
| coin | /ˈkɔɪn/ | 擴充 | n | 硬幣 | coin / coins | the coin |
| crowd | /ˈkɹaʊd/ | 擴充 | n | 人群 | crowd / crowds | the crowd |
| flour | /ˈflaʊɚ/ | 擴充 | n | 麵粉 | flour / flours | the flour |
| handle | /ˈhændəl/ | 擴充 | n | 把手 | handle / handles | the handle |
| hole | /ˈhoʊl/ | 擴充 | n | 洞 | hole / holes | the hole |
| hood | /ˈhʊd/ | 擴充 | n | 帽子 | hood / hoods | the hood |
| instrument | /ˈɪnstɹəmənt/ | 擴充 | n | 樂器 | instrument / instruments | the instrument |
| jacket | /ˈdʒækət/ | 擴充 | n | 夾克 | jacket / jackets | the jacket |
| jaw | /ˈdʒɔ/ | 擴充 | n | 顎 | jaw / jaws | the jaw |
| leather | /ˈlɛðɚ/ | 擴充 | n | 皮革 | leather / leathers | the leather |
| lung | /ˈlʌŋ/ | 擴充 | n | 肺 | lung / lungs | the lung |
| muscle | /ˈmʌsəl/ | 擴充 | n | 肌肉 | muscle / muscles | the muscle |
| nail | /ˈneɪl/ | 擴充 | n | 指甲 | nail / nails | the nail |
| needle | /ˈniːdəl/ | 擴充 | n | 針 | needle / needles | the needle |
| newspaper | /ˈnuːˌzpeɪpɚ/ | 擴充 | n | 報紙 | newspaper / newspapers | the newspaper |
| nut | /ˈnʌt/ | 擴充 | n | 堅果 | nut / nuts | the nut |
| oven | /ˈʌvən/ | 擴充 | n | 烤箱 | oven / ovens | the oven |
| page | /ˈpeɪdʒ/ | 擴充 | n | 頁 | page / pages | the page |
| pasta | /ˈpɑstə/ | 擴充 | n | 義大利麵 | pasta / pastas | the pasta |
| pepper | /ˈpɛpɚ/ | 擴充 | n | 胡椒 | pepper / peppers | the pepper |
| poem | /ˈpoʊəm/ | 擴充 | n | 詩 | poem / poems | the poem |
| pot | /ˈpɑt/ | 擴充 | n | 鍋 | pot / pots | the pot |
| powder | /ˈpaʊdɚ/ | 擴充 | n | 粉 | powder / powders | the powder |
| prize | /ˈpɹaɪz/ | 擴充 | n | 獎品 | prize / prizes | the prize |
| rope | /ˈɹoʊp/ | 擴充 | n | 繩子 | rope / ropes | the rope |
| salad | /ˈsæləd/ | 擴充 | n | 沙拉 | salad / salads | the salad |
| sauce | /ˈsɔs/ | 擴充 | n | 醬汁 | sauce / sauces | the sauce |
| saw | /ˈsɔ/ | 擴充 | n | 鋸子 | saw / saws | the saw |
| shell | /ˈʃɛl/ | 擴充 | n | 殼 | shell / shells | the shell |
| soy | /ˈsɔɪ/ | 擴充 | n | 大豆 | soy / soys | the soy |
| spice | /ˈspaɪs/ | 擴充 | n | 香料 | spice / spices | the spice |
| spot | /ˈspɑt/ | 擴充 | n | 斑點 | spot / spots | the spot |
| stick | /ˈstɪk/ | 擴充 | n | 棍子 | stick / sticks | the stick |
| strap | /ˈstɹæp/ | 擴充 | n | 背帶 | strap / straps | the strap |
| string | /ˈstɹɪŋ/ | 擴充 | n | 繩子 | string / strings | the string |
| stuff | /ˈstʌf/ | 擴充 | n | 東西 | stuff / stuffs | the stuff |
| surface | /ˈsɝfəs/ | 擴充 | n | 表面 | surface / surfaces | the surface |
| tube | /ˈtuːb/ | 擴充 | n | 管子 | tube / tubes | the tube |
| video | /ˈvɪdioʊ/ | 擴充 | n | 影片 | video / videos | the video |
| waist | /ˈweɪst/ | 擴充 | n | 腰 | waist / waists | the waist |
| wheel | /ˈwiːl/ | 擴充 | n | 輪子 | wheel / wheels | the wheel |
| wool | /ˈwʊl/ | 擴充 | n | 羊毛 | wool / wools | the wool |
| wound | /ˈwaʊnd/ | 擴充 | n | 傷口 | wound / wounds | the wound |
| belt | /ˈbɛlt/ | 擴充 | n | 皮帶 | belt / belts | the belt |
| bit | /ˈbɪt/ | 擴充 | n | 小塊 | bit / bits | the bit |
| file | /ˈfaɪl/ | 擴充 | n/v | 檔案 | file / files / filed / filed / filing | to file |
| film | /ˈfɪlm/ | 擴充 | n | 影片 | film / films | the film |
| fist | /ˈfɪst/ | 擴充 | n | 拳頭 | fist / fists | the fist |
| form | /ˈfɔɹm/ | 擴充 | n | 形式 | form / forms | the form |
| mark | /ˈmɑɹk/ | 擴充 | n | 分數 | mark / marks | the mark |
| thread | /ˈθɹɛd/ | 擴充 | n | 線 | thread / threads | the thread |
| throat | /ˈθɹoʊt/ | 擴充 | n | 喉嚨 | throat / throats | the throat |
| bubble | /ˈbʌbəl/ | 擴充 | n | 泡泡 | bubble / bubbles | the bubble |
| cough | /ˈkɑf/ | 擴充 | n/v | 咳嗽 | cough / coughs / coughed / coughed / coughing | to cough |
| fever | /ˈfiːvər/ | 擴充 | n | 發燒 | fever / fevers | the fever |
| glue | /ˈɡluː/ | 擴充 | n | 黏膠 | glue / glues | the glue |
| tail | /ˈteɪl/ | 擴充 | n | 尾巴 | tail / tails | the tail |
| horn | /ˈhɔɹn/ | 擴充 | n | 角 | horn / horns | the horn |
| gear | /ˈɡɪɹ/ | 擴充 | n | 齒輪 | gear / gears | the gear |
| bean | /ˈbiːn/ | 擴充 | n | 豆子 | bean / beans | the bean |
| pedal | /ˈpɛdəl/ | 擴充 | n | 踏板 | pedal / pedals | the pedal |
| motor | /ˈmoʊtɚ/ | 擴充 | n | 馬達 | motor / motors | the motor |
| frame | /ˈfɹeɪm/ | 擴充 | n | 車架 | frame / frames | the frame |

### 2.10 社交・人（核心 34 ＋ 擴充 40 ＝ 74）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| hello | /həˈloʊ/ | 核心 | interj | 你好 | hello | say hello |
| hi | /ˈhaɪ/ | 核心 | interj | 嗨 | hi | say hi |
| goodbye | /ˌɡʊˈdbaɪ/ | 擴充 | interj | 再見 | goodbye | say goodbye |
| bye | /ˈbaɪ/ | 擴充 | interj | 再見 | bye | say bye |
| thanks | /ˈθæŋks/ | 核心 | interj | 謝謝 | thanks | say thanks |
| thank | /ˈθæŋk/ | 核心 | v | 感謝 | thank / thanks / thanked / thanked / thanking | thank you |
| please | /ˈpliːz/ | 核心 | adv | 請 | please | please sit down |
| sorry | /ˈsɑɹi/ | 核心 | adj | 抱歉的；難過的 | sorry / sorrier / sorriest | I am sorry |
| welcome | /ˈwɛlkəm/ | 核心 | v/adj | 歡迎 | welcome / welcomes / welcomed / welcomed / welcoming | welcome to my home |
| excuse | /ɪˈkskjuːs/ | 擴充 | v | 寬恕；打斷 | excuse / excuses / excused / excused / excusing | to excuse |
| name | /ˈneɪm/ | 核心 | n | 名字 | name / names | my name |
| friend | /ˈfɹɛnd/ | 核心 | n | 朋友 | friend / friends | a good friend |
| family | /ˈfæməli/ | 核心 | n | 家人 | family / families | my family |
| mother | /ˈmʌðər/ | 核心 | n | 母親 | mother / mothers | my mother |
| father | /ˈfɑːðər/ | 核心 | n | 父親 | father / fathers | my father |
| parent | /ˈpɛɹənt/ | 核心 | n | 父母 | parent / parents | my parents |
| brother | /ˈbrʌðər/ | 核心 | n | 兄弟 | brother / brothers | my brother |
| sister | /ˈsɪstɚ/ | 核心 | n | 姐妹 | sister / sisters | my sister |
| child | /ˈtʃaɪld/ | 核心 | n | 小孩 | child / children | a small child |
| son | /ˈsʌn/ | 核心 | n | 兒子 | son / sons | my son |
| daughter | /ˈdɔtɚ/ | 核心 | n | 女兒 | daughter / daughters | my daughter |
| husband | /ˈhʌzbənd/ | 核心 | n | 丈夫 | husband / husbands | my husband |
| wife | /ˈwaɪf/ | 核心 | n | 妻子 | wife / wives | my wife |
| baby | /ˈbeɪbi/ | 核心 | n | 嬰兒 | baby / babies | a small baby |
| grandmother | /ˈɡɹæˌndmʌðɚ/ | 擴充 | n | 祖母 | grandmother / grandmothers | the grandmother |
| grandfather | /ˈɡɹæˌndfɑðɚ/ | 擴充 | n | 祖父 | grandfather / grandfathers | the grandfather |
| uncle | /ˈʌŋkəl/ | 擴充 | n | 叔伯 | uncle / uncles | the uncle |
| aunt | /ˈænt/ | 擴充 | n | 姑姑阿姨 | aunt / aunts | the aunt |
| cousin | /ˈkʌzən/ | 擴充 | n | 表兄弟姊妹 | cousin / cousins | the cousin |
| teacher | /ˈtiːtʃɚ/ | 核心 | n | 老師 | teacher / teachers | a good teacher |
| student | /ˈstuːdənt/ | 核心 | n | 學生 | student / students | a young student |
| doctor | /ˈdɑktɚ/ | 核心 | n | 醫生 | doctor / doctors | see a doctor |
| nurse | /ˈnɝs/ | 核心 | n | 護士 | nurse / nurses | the nurse is here |
| worker | /ˈwɝkɚ/ | 核心 | n | 工作者 | worker / workers | a hard worker |
| boss | /ˈbɑs/ | 擴充 | n | 老闆 | boss / bosses | the boss |
| customer | /ˈkʌstəmɚ/ | 核心 | n | 客人 | customer / customers | a new customer |
| person | /ˈpɝsən/ | 核心 | n | 人 | person / people | a kind person |
| man | /ˈmæn/ | 核心 | n | 男人 | man / men | a young man |
| woman | /ˈwʊmən/ | 核心 | n | 女人 | woman / women | a young woman |
| lady | /ˈleɪdi/ | 擴充 | n | 女士 | lady / ladies | the lady |
| people | /ˈpiːpəl/ | 核心 | n | 人們 | people / peoples | many people |
| stranger | /ˈstɹeɪndʒɚ/ | 擴充 | n | 陌生人 | stranger / strangers | the stranger |
| guest | /ˈɡɛst/ | 擴充 | n | 客人 | guest / guests | the guest |
| neighbor | /ˈneɪbɚ/ | 擴充 | n | 鄰居 | neighbor / neighbors | the neighbor |
| kid | /ˈkɪd/ | 擴充 | n | 小孩 | kid / kids | the kid |
| partner | /ˈpɑɹtnɚ/ | 擴充 | n | 伴侶；夥伴 | partner / partners | the partner |
| member | /ˈmɛmbɚ/ | 核心 | n | 成員 | member / members | a team member |
| leader | /ˈliːdɚ/ | 擴充 | n | 領袖 | leader / leaders | the leader |
| citizen | /ˈsɪtəzən/ | 擴充 | n | 公民 | citizen / citizens | the citizen |
| couple | /ˈkʌpəl/ | 擴充 | n | 一對 | couple / couples | the couple |
| sir | /ˈsɝ/ | 擴充 | n | 先生 | sir / sirs | the sir |
| soldier | /ˈsoʊldʒɚ/ | 擴充 | n | 士兵 | soldier / soldiers | the soldier |
| officer | /ˈɔfəsɚ/ | 擴充 | n | 官員 | officer / officers | the officer |
| scientist | /ˈsaɪəntɪst/ | 擴充 | n | 科學家 | scientist / scientists | the scientist |
| artist | /ˈɑɹtəst/ | 擴充 | n | 藝術家 | artist / artists | the artist |
| writer | /ˈɹaɪtɚ/ | 擴充 | n | 作家 | writer / writers | the writer |
| engineer | /ˈɛndʒəˈnɪɹ/ | 擴充 | n | 工程師 | engineer / engineers | the engineer |
| lawyer | /ˈlɔjɚ/ | 擴充 | n | 律師 | lawyer / lawyers | the lawyer |
| farmer | /ˈfɑɹmɚ/ | 擴充 | n | 農民 | farmer / farmers | the farmer |
| driver | /ˈdɹaɪvɚ/ | 擴充 | n | 司機 | driver / drivers | the driver |
| English | /ˈɪŋɡlɪʃ/ | 核心 | n | 英語 | English / Englishes | I speak English |
| Chinese | /ˈtʃaɪniːz/ | 核心 | n | 中文 | Chinese / Chineses | I speak Chinese |
| band | /ˈbænd/ | 擴充 | n | 樂團 | band / bands | the band |
| crime | /ˈkɹaɪm/ | 擴充 | n | 犯罪 | crime / crimes | the crime |
| king | /ˈkɪŋ/ | 擴充 | n | 國王 | king / kings | the king |
| queen | /ˈkwiːn/ | 擴充 | n | 女王 | queen / queens | the queen |
| judge | /ˈdʒʌdʒ/ | 擴充 | n | 法官 | judge / judges | the judge |
| lover | /ˈlʌvɚ/ | 擴充 | n | 情人 | lover / lovers | the lover |
| girl | /ˈɡɝl/ | 擴充 | n | 女孩 | girl / girls | the girl |
| boy | /ˈbɔɪ/ | 擴充 | n | 男孩 | boy / boys | the boy |
| mayor | /ˈmeɪɚ/ | 擴充 | n | 市長 | mayor / mayors | the mayor |
| actor | /ˈæktɚ/ | 擴充 | n | 演員 | actor / actors | the actor |
| manager | /ˈmænədʒɚ/ | 擴充 | n | 經理 | manager / managers | the manager |
| kingdom | /ˈkɪŋdəm/ | 擴充 | n | 王國 | kingdom / kingdoms | the kingdom |

### 2.11 抽象概念（核心 29 ＋ 擴充 126 ＝ 155）

| 詞 | IPA | 層 | 詞性 | 中文意思 | 允許的形式 | 例子 |
|---|---|---|---|---|---|---|
| thing | /ˈθɪŋ/ | 核心 | n | 事物 | thing / things | a thing to eat |
| type | /ˈtaɪp/ | 核心 | n | 類型 | type / types | the type |
| sort | /ˈsɔɹt/ | 核心 | n | 種類 | sort / sorts | the sort |
| part | /ˈpɑɹt/ | 擴充 | n | 部分 | part / parts | a part of the work |
| piece | /ˈpiːs/ | 擴充 | n | 片段；一片 | piece / pieces | a piece of bread |
| group | /ˈɡɹuːp/ | 擴充 | n | 群組 | group / groups | a group of people |
| system | /ˈsɪstəm/ | 擴充 | n | 系統 | system / systems | a simple system |
| tool | /ˈtuːl/ | 核心 | n | 工具 | tool / tools | a tool for cutting |
| machine | /məˈʃiːn/ | 擴充 | n | 機器 | machine / machines | a machine that washes clothes |
| material | /məˈtɪɹiəl/ | 擴充 | n | 材料 | material / materials | a material for building |
| voice | /ˈvɔɪs/ | 擴充 | n | 嗓音 | voice / voices | the voice |
| noise | /ˈnɔɪz/ | 擴充 | n | 噪音 | noise / noises | the noise |
| language | /ˈlæŋɡwədʒ/ | 核心 | n | 語言 | language / languages | a language for talking |
| word | /ˈwɝd/ | 核心 | n | 單字 | word / words | a new word |
| shape | /ˈʃeɪp/ | 擴充 | n | 形狀 | shape / shapes | a round shape |
| size | /ˈsaɪz/ | 擴充 | n | 大小 | size / sizes | the size of the room |
| level | /ˈlɛvəl/ | 擴充 | n | 程度；階層 | level / levels | a high level of English |
| degree | /dɪˈɡɹiː/ | 擴充 | n | 程度；度 | degree / degrees | a high degree |
| reason | /ˈɹiːzən/ | 核心 | n | 原因 | reason / reasons | the reason why |
| result | /ɹɪˈzʌlt/ | 核心 | n | 結果 | result / results | the result of the work |
| problem | /ˈpɹɑbləm/ | 核心 | n | 問題 | problem / problems | a big problem |
| question | /ˈkwɛstʃən/ | 核心 | n | 問題 | question / questions | a hard question |
| idea | /aɪˈdiːə/ | 擴充 | n | 想法 | idea / ideas | a good idea |
| plan | /ˈplæn/ | 擴充 | n | 計畫 | plan / plans | a plan for the week |
| method | /ˈmɛθəd/ | 擴充 | n | 方法 | method / methods | the method |
| example | /ɪˈɡzæmpəl/ | 擴充 | n | 例子 | example / examples | an example of it |
| fact | /ˈfækt/ | 擴充 | n | 事實 | fact / facts | a true fact |
| truth | /ˈtɹuːθ/ | 擴充 | n | 真實 | truth / truths | the truth |
| lie | /ˈlaɪ/ | 擴充 | n | 謊話 | lie / lies | the lie |
| information | /ˌɪnfɚˈmeɪʃən/ | 擴充 | n | 資訊 | information / informations | the information |
| knowledge | /ˈnɑlədʒ/ | 擴充 | n | 知識 | knowledge / knowledges | the knowledge |
| skill | /ˈskɪl/ | 擴充 | n | 技能 | skill / skills | the skill |
| ability | /əˈbɪləˌtiː/ | 擴充 | n | 能力 | ability / abilities | the ability |
| chance | /ˈtʃæns/ | 擴充 | n | 機會 | chance / chances | the chance |
| choice | /ˈtʃɔɪs/ | 擴充 | n | 選擇 | choice / choices | the choice |
| decision | /dɪˈsɪʒən/ | 擴充 | n | 決定 | decision / decisions | the decision |
| difference | /ˈdɪfɚəns/ | 擴充 | n | 差異 | difference / differences | the difference |
| effect | /ɪˈfɛkt/ | 擴充 | n | 影響 | effect / effects | the effect |
| event | /ɪˈvɛnt/ | 擴充 | n | 事件 | event / events | the event |
| experience | /ɪˈkspɪɹiəns/ | 擴充 | n | 經驗 | experience / experiences | the experience |
| process | /ˈpɹɑˌsɛs/ | 擴充 | n | 過程 | process / processes | the process |
| progress | /ˈpɹɑˌɡɹɛs/ | 擴充 | n | 進步 | progress / progresses | the progress |
| purpose | /ˈpɝpəs/ | 擴充 | n | 目的 | purpose / purposes | the purpose |
| quality | /ˈkwɑləti/ | 擴充 | n | 品質 | quality / qualities | the quality |
| quantity | /ˈkwɑntəti/ | 擴充 | n | 數量 | quantity / quantities | the quantity |
| value | /ˈvælju/ | 擴充 | n | 價值 | value / values | the value |
| rate | /ˈɹeɪt/ | 擴充 | n | 比率 | rate / rates | the rate |
| power | /ˈpaʊɚ/ | 擴充 | n | 力量；電力 | power / powers | the power |
| control | /kəˈntɹoʊl/ | 擴充 | v/n | 控制 | control / controls / controlled / controlled / controlling | control the price |
| influence | /ˈɪnfluəns/ | 擴充 | n/v | 影響 | influence / influences / influenced / influenced / influencing | to influence |
| service | /ˈsɝvəs/ | 擴充 | n | 服務 | service / services | the service |
| product | /ˈprɑːdəkt/ | 擴充 | n | 產品 | product / products | the product |
| project | /ˈpɹɑdʒɛkt/ | 擴充 | n | 專案 | project / projects | the project |
| research | /ɹiˈsɝtʃ/ | 擴充 | n/v | 研究 | research / researches / researched / researched / researching | to research |
| policy | /ˈpɑləsi/ | 擴充 | n | 政策 | policy / policies | the policy |
| culture | /ˈkʌltʃɚ/ | 擴充 | n | 文化 | culture / cultures | the culture |
| society | /səˈsaɪəti/ | 擴充 | n | 社會 | society / societies | the society |
| community | /kəˈmjuːnəti/ | 擴充 | n | 社群 | community / communities | the community |
| government | /ˈɡʌvɚmənt/ | 擴充 | n | 政府 | government / governments | the government |
| president | /ˈpɹɛzəˌdɛnt/ | 擴充 | n | 總統 | president / presidents | the president |
| minister | /ˈmɪnəstɚ/ | 擴充 | n | 部長 | minister / ministers | the minister |
| party | /ˈpɑɹti/ | 擴充 | n | 政黨；派對 | party / parties | the party |
| war | /ˈwɔɹ/ | 擴充 | n | 戰爭 | war / wars | the war |
| peace | /ˈpiːs/ | 擴充 | n | 和平 | peace / peaces | the peace |
| health | /ˈhɛlθ/ | 核心 | n | 健康 | health / healths | good health |
| disease | /dɪˈziːz/ | 擴充 | n | 疾病 | disease / diseases | the disease |
| pain | /ˈpeɪn/ | 核心 | n | 疼痛 | pain / pains | a little pain |
| treatment | /ˈtɹiːtmənt/ | 擴充 | n | 治療 | treatment / treatments | the treatment |
| science | /ˈsaɪəns/ | 擴充 | n | 科學 | science / sciences | the science |
| technology | /tɛˈknɑlədʒi/ | 擴充 | n | 科技 | technology / technologies | the technology |
| history | /ˈhɪstɚi/ | 擴充 | n | 歷史 | history / histories | the history |
| art | /ˈɑɹt/ | 核心 | n | 藝術 | art / arts | a school for art |
| music | /ˈmjuːzɪk/ | 核心 | n | 音樂 | music / musics | music I like |
| story | /ˈstɔɹi/ | 核心 | n | 故事 | story / stories | a long story |
| news | /ˈnuːz/ | 擴充 | n | 新聞 | news / newses | the news |
| article | /ˈɑɹtəkəl/ | 擴充 | n | 文章 | article / articles | the article |
| report | /ɹiˈpɔɹt/ | 擴充 | v/n | 報告 | report / reports / reported / reported / reporting | to report |
| meeting | /ˈmiːtɪŋ/ | 擴充 | n | 會議 | meeting / meetings | a work meeting |
| job | /ˈdʒɑb/ | 核心 | n | 工作 | job / jobs | a good job |
| rule | /ˈɹuːl/ | 核心 | n | 規則 | rule / rules | a simple rule |
| law | /ˈlɔ/ | 核心 | n | 法律 | law / laws | the law of the country |
| company | /ˈkʌmpəˌniː/ | 核心 | n | 公司 | company / companies | a big company |
| business | /ˈbɪznəs/ | 擴充 | n | 商業 | business / businesses | the business |
| industry | /ˈɪndəstɹi/ | 擴充 | n | 產業 | industry / industries | the industry |
| software | /ˈsɔˌftwɛɹ/ | 擴充 | n | 軟體 | software / softwares | the software |
| program | /ˈpɹoʊˌɡɹæm/ | 核心 | n | 節目；程式 | program / programs | a radio program |
| internet | /ˈɪntɚˌnɛt/ | 擴充 | n | 網際網路 | internet / internets | the internet |
| data | /ˈdeɪtə/ | 擴充 | n | 資料 | data / datas | the data |
| movie | /ˈmuːvi/ | 擴充 | n | 電影 | movie / movies | the movie |
| song | /ˈsɔŋ/ | 擴充 | n | 歌 | song / songs | the song |
| game | /ˈɡeɪm/ | 核心 | n | 遊戲；比賽 | game / games | a fun game |
| sport | /ˈspɔɹt/ | 核心 | n | 運動 | sport / sports | a popular sport |
| ball | /ˈbɔl/ | 核心 | n | 球 | ball / balls | a red ball |
| player | /ˈpleɪɚ/ | 核心 | n | 玩家 | player / players | a good player |
| class | /ˈklæs/ | 核心 | n | 班；課 | class / classes | a class of students |
| lesson | /ˈlɛsən/ | 擴充 | n | 課 | lesson / lessons | the lesson |
| test | /ˈtɛst/ | 擴充 | n/v | 測試 | test / tests / tested / tested / testing | to test |
| mistake | /mɪˈsteɪk/ | 擴充 | n | 錯誤 | mistake / mistakes | the mistake |
| homework | /ˈhoʊˌmwɚk/ | 擴充 | n | 作業 | homework / homeworks | the homework |
| score | /ˈskɔɹ/ | 擴充 | n | 分數 | score / scores | the score |
| title | /ˈtaɪtəl/ | 擴充 | n | 標題 | title / titles | the title |
| list | /ˈlɪst/ | 擴充 | n | 清單 | list / lists | the list |
| record | /ɹəˈkɔɹd/ | 擴充 | n/v | 記錄 | record / records / recorded / recorded / recording | to record |
| note | /ˈnoʊt/ | 擴充 | n/v | 筆記；注意 | note / notes / noted / noted / noting | to note |
| interest | /ˈɪntɹəst/ | 擴充 | n | 興趣 | interest / interests | the interest |
| attention | /əˈtɛnʃən/ | 擴充 | n | 注意力 | attention / attentions | the attention |
| amount | /əˈmaʊnt/ | 擴充 | n | 數量 | amount / amounts | the amount |
| sense | /ˈsɛns/ | 擴充 | n | 意義；感覺 | sense / senses | the sense |
| image | /ˈɪmədʒ/ | 擴充 | n | 影像 | image / images | the image |
| situation | /ˌsɪtʃuˈeɪʃən/ | 擴充 | n | 情況 | situation / situations | the situation |
| condition | /kəˈndɪʃən/ | 擴充 | n | 情況；條件 | condition / conditions | the condition |
| subject | /səˈbdʒɛkt/ | 擴充 | n | 主題；科目 | subject / subjects | the subject |
| end | /ˈɛnd/ | 核心 | n/v | 結束 | end / ends / ended / ended / ending | the end of the day |
| life | /ˈlaɪf/ | 核心 | n | 生活；生命 | life / lives | a good life |
| death | /ˈdɛθ/ | 擴充 | n | 死亡 | death / deaths | the death |
| feeling | /ˈfiːlɪŋ/ | 核心 | n | 感覺；心情 | feeling / feelings | a good feeling |
| team | /ˈtiːm/ | 核心 | n | 團隊 | team / teams | the team |
| angle | /ˈæŋɡəl/ | 擴充 | n | 角度 | angle / angles | the angle |
| competition | /ˌkɑmpəˈtɪʃən/ | 擴充 | n | 比賽 | competition / competitions | the competition |
| illness | /ˈɪlnəs/ | 擴充 | n | 疾病 | illness / illnesses | the illness |
| journey | /ˈdʒɝni/ | 擴充 | n | 旅行 | journey / journeys | the journey |
| length | /ˈlɛŋkθ/ | 擴充 | n | 長度 | length / lengths | the length |
| marriage | /ˈmɛɹɪdʒ/ | 擴充 | n | 婚姻 | marriage / marriages | the marriage |
| math | /ˈmæθ/ | 擴充 | n | 數學 | math / maths | the math |
| mind | /ˈmaɪnd/ | 擴充 | n | 心智 | mind / minds | the mind |
| network | /ˈnɛˌtwɚk/ | 擴充 | n | 網路 | network / networks | the network |
| period | /ˈpɪɹiəd/ | 擴充 | n | 時期 | period / periods | the period |
| pressure | /ˈpɹɛʃɚ/ | 擴充 | n | 壓力 | pressure / pressures | the pressure |
| promise | /ˈpɹɑməs/ | 擴充 | n | 承諾 | promise / promises | the promise |
| reaction | /ɹiˈækʃən/ | 擴充 | n | 反應 | reaction / reactions | the reaction |
| signal | /ˈsɪɡnəl/ | 擴充 | n | 訊號 | signal / signals | the signal |
| web | /ˈwɛb/ | 擴充 | n | 網 | web / webs | the web |
| wedding | /ˈwɛdɪŋ/ | 擴充 | n | 婚禮 | wedding / weddings | the wedding |
| age | /ˈeɪdʒ/ | 擴充 | n | 年紀 | age / ages | the age |
| agreement | /əˈɡɹiːmənt/ | 擴充 | n | 協議 | agreement / agreements | the agreement |
| care | /ˈkɛɹ/ | 擴充 | n | 照顧 | care / cares | the care |
| course | /ˈkɔɹs/ | 擴充 | n | 課 | course / courses | the course |
| danger | /ˈdeɪndʒɚ/ | 擴充 | n | 危險 | danger / dangers | the danger |
| effort | /ˈɛfɚt/ | 擴充 | n | 努力 | effort / efforts | the effort |
| fear | /ˈfɪɹ/ | 擴充 | n | 害怕 | fear / fears | the fear |
| goal | /ˈɡoʊl/ | 擴充 | n | 目標 | goal / goals | the goal |
| trip | /ˈtɹɪp/ | 擴充 | n | 旅行 | trip / trips | the trip |
| habit | /ˈhæbət/ | 擴充 | n | 習慣 | habit / habits | the habit |
| sentence | /ˈsɛntəns/ | 擴充 | n | 句子 | sentence / sentences | the sentence |
| stock | /ˈstɑk/ | 擴充 | n | 股票；存貨 | stock / stocks | the stock |
| opinion | /əˈpɪnjən/ | 擴充 | n | 意見 | opinion / opinions | the opinion |
| model | /ˈmɑdəl/ | 擴充 | n | 模型 | model / models | the model |
| state | /ˈsteɪt/ | 擴充 | n | 州；狀態 | state / states | the state |
| dynasty | /ˈdaɪnəsti/ | 擴充 | n | 王朝 | dynasty / dynasties | the dynasty |
| mechanism | /ˈmɛkəˌnɪzəm/ | 擴充 | n | 機械裝置 | mechanism / mechanisms | the mechanism |
| movement | /ˈmuːvmənt/ | 擴充 | n | 移動 | movement / movements | the movement |
| physics | /ˈfɪzɪks/ | 擴充 | n | 物理 | physics / physicses | the physics |
| chemistry | /ˈkɛməstɹi/ | 擴充 | n | 化學 | chemistry / chemistries | the chemistry |
| element | /ˈɛləmənt/ | 擴充 | n | 元素 | element / elements | the element |
| cycle | /ˈsaɪkəl/ | 擴充 | n | 循環 | cycle / cycles | the cycle |

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

| 類頭 | 中文 |
|---|---|
| thing | 東西 |
| person | 人 |
| place | 地方 |
| kind | 種類 |
| way | 方式 |
| part | 部分 |
| piece | 片；片段 |
| group | 群組 |
| system | 系統 |
| tool | 工具 |
| machine | 機器 |
| material | 材料 |
| food | 食物 |
| drink | 飲料 |
| animal | 動物 |
| plant | 植物 |
| language | 語言 |
| word | 單字 |
| letter | 字母 |
| number | 數字 |
| shape | 形狀 |
| size | 大小 |
| level | 程度 |
| degree | 程度 |
| reason | 原因 |
| result | 結果 |
| problem | 問題 |
| question | 問題 |
| answer | 答案 |
| idea | 想法 |
| plan | 計畫 |
| story | 故事 |
| news | 新聞 |
| article | 文章 |
| report | 報告 |
| study | 學習；研究 |
| work | 工作 |
| job | 工作 |
| rule | 規則 |
| law | 法律 |
| company | 公司 |
| team | 團隊 |
| game | 遊戲 |
| sport | 運動 |
| music | 音樂 |
| art | 藝術 |
| science | 科學 |
| history | 歷史 |
| feeling | 感覺 |
| fact | 事實 |

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

| 字首／字尾 | 類型 | 意思 | 例子 |
|---|---|---|---|
| `un-` | prefix | not（否定） | unhappy, unclear, unsafe |
| `re-` | prefix | again / back | redo, reopen, retell |
| `-er` | suffix | a person who does it（做某事的人） | worker, teacher, driver |
| `-er` | suffix | comparative（比較級） | bigger, taller |
| `-est` | suffix | superlative（最高級） | biggest, tallest |
| `-ly` | suffix | adverb（副詞） | quickly, carefully |
| `-ness` | suffix | the quality of it（性質名詞） | kindness, sadness |

### 4.2 保留的不規則形式

因為 Mini-English 必須是正確英文，這些形式照抄英文本來寫法，算同一個詞，不另外計 n。

| 原形 | 不規則形式 |
|---|---|
| go | went / gone |
| come | came |
| eat | ate / eaten |
| drink | drank / drunk |
| sleep | slept |
| wake | woke / woken |
| write | wrote / written |
| speak | spoke / spoken |
| say | said |
| tell | told |
| give | gave / given |
| take | took / taken |
| get | got |
| make | made |
| buy | bought |
| sell | sold |
| pay | paid |
| find | found |
| lose | lost |
| meet | met |
| leave | left |
| hear | heard |
| keep | kept |
| feel | felt |
| send | sent |
| build | built |
| run | ran |
| swim | swam |
| sing | sang |
| begin | began / begun |
| become | became |
| break | broke / broken |
| choose | chose / chosen |
| forget | forgot / forgotten |
| understand | understood |
| bring | brought |
| catch | caught |
| fall | fell / fallen |
| throw | threw / thrown |
| drive | drove / driven |
| ride | rode / ridden |
| grow | grew / grown |
| fly | flew / flown |
| wear | wore / worn |
| win | won |
| stand | stood |
| sit | sat |
| ring | rang / rung |
| hang | hung |
| show | showed / shown |
| teach | taught |
| think | thought |
| know | knew / known |
| hold | held |
| lead | led |
| mean | meant |
| lend | lent |
| spend | spent |
| child | children |
| man | men |
| woman | women |
| foot | feet |
| tooth | teeth |
| person | people |
| mouse | mice |
| knife | knives |
| wife | wives |
| life | lives |
| half | halves |
| shelf | shelves |
| potato | potatoes |
| tomato | tomatoes |
| city | cities |
| baby | babies |
| story | stories |
| country | countries |
| family | families |
| party | parties |
| lady | ladies |
| cost | cost |
| cut | cut |
| hit | hit |
| put | put |
| read | read |
| good | better / best |
| bad | worse / worst |
| far | farther / farthest |
| many | more / most |
| much | more / most |
| little | less / least |

### 4.3 片語動詞（例外，不計入 n）

片語動詞是初學者最大的記憶負擔（`look for / look after / look at / look out` 意思完全不同），
所以大部分片語動詞都用表內的單一動詞或「動詞＋介系詞」取代
（`give up` → `stop`、`find out` → `know`、`put on` → `wear`、`get up` → `stand up`）。

只有下面 13 個保留，而且只在真的需要時用：

```text
look for
look at
look after
put on
take off
get up
get off
get in
get out
find out
turn off
turn on
come back
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
5. 執行 `python check.py`：詞表不能有重複、表格要與附錄一致、所有例句要通過；`python check.py --lexicon` 檢查詞典。
6. 執行 `python build.py`：會重新產生本文件的第 2 節與所有附錄、`prompts/system.md` 的詞表，以及 `lexicon.tsv`。
7. 執行 `python web/build.py`：重新產生網頁的 `web/data.js`（詞表、詞典、範例、規則）。

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
# 核心層｜代詞・指示
I
me
my
myself
you
your
yourself
he
him
his
she
her
it
its
we
us
our
they
them
their
this
that
these
those
who
whom
whose
what
which
someone
somebody
something
anyone
anybody
anything
everyone
everybody
everything
nobody
nothing
one
other
another
both
either
neither
each
all
some
any
none
many
much
few
several
more
most
such
same
own
# 核心層｜語法（功能詞）
a
an
the
be
am
is
are
was
were
been
being
do
does
did
have
has
had
will
would
can
could
shall
should
may
might
must
need
let
not
no
yes
than
as
if
because
so
and
or
but
when
while
before
after
until
since
therefore
also
too
very
quite
really
just
still
only
even
almost
already
always
never
often
sometimes
usually
again
soon
now
then
yet
here
there
up
down
out
off
over
under
away
back
together
less
least
enough
first
last
next
second
every
of
in
on
at
to
for
with
from
by
about
above
below
across
around
behind
between
into
onto
toward
without
near
like
well
maybe
little
okay
actually
where
why
how
# 核心層｜數量・比例
number
half
whole
double
percent
zero
once
twice
# 核心層｜時間
time
year
month
week
day
hour
minute
morning
afternoon
evening
night
today
tomorrow
yesterday
tonight
weekend
birthday
holiday
date
clock
early
late
ago
Monday
Tuesday
Wednesday
Thursday
Friday
Saturday
Sunday
# 核心層｜方位・地點
place
house
home
room
door
window
floor
wall
road
street
way
corner
side
city
town
country
world
shop
store
station
school
office
bank
park
north
south
east
west
left
right
front
inside
outside
map
bus stop
top
line
ticket
bus
train
plane
car
bike
gym
# 核心層｜自然・天氣
weather
sun
sky
rain
snow
wind
sea
river
tree
flower
plant
animal
dog
cat
bird
fish
earth
fire
wood
oil
gas
air
land
field
farm
light
glass
paper
water
# 核心層｜動作
go
come
walk
run
sit
stand
eat
drink
sleep
wake
read
write
speak
say
tell
ask
answer
look
see
watch
hear
listen
give
take
get
put
make
buy
sell
pay
cost
open
close
start
stop
wait
work
play
study
learn
teach
help
use
find
lose
keep
send
bring
carry
move
turn
change
grow
live
die
meet
visit
drive
ride
fly
cook
wash
clean
cut
break
fix
wear
feel
hurt
want
try
love
hate
begin
finish
choose
decide
hope
wish
remember
forget
know
think
mean
happen
become
stay
leave
arrive
return
call
sing
dance
jump
fall
push
pull
throw
catch
win
rest
raise
share
follow
lead
hit
enter
pass
empty
ring
spend
allow
include
believe
explain
describe
support
build
protect
seem
appear
exist
provide
receive
accept
understand
talk
reach
# 核心層｜性質
good
bad
big
small
long
short
tall
high
low
old
new
young
hot
cold
warm
cool
wet
dry
easy
hard
difficult
simple
important
different
wrong
true
false
real
nice
fine
free
busy
happy
sad
tired
sick
healthy
strong
weak
heavy
fast
slow
beautiful
afraid
fun
interesting
possible
clear
ready
sure
rich
poor
sweet
soft
wide
deep
full
brown
black
white
red
blue
green
yellow
orange
pink
special
safe
careful
kind
correct
certain
dirty
color
# 核心層｜事物
food
rice
meat
milk
tea
coffee
fruit
apple
sugar
salt
lunch
dinner
head
eye
nose
mouth
hand
foot
heart
face
body
shirt
table
chair
bed
cup
knife
bottle
box
bag
book
pen
key
picture
medicine
phone
computer
letter
message
bill
money
price
card
kitchen
bedroom
classroom
supermarket
bookstore
# 核心層｜社交・人
hello
hi
thanks
thank
please
sorry
welcome
name
friend
family
mother
father
parent
brother
sister
child
son
daughter
husband
wife
baby
teacher
student
doctor
nurse
worker
customer
person
man
woman
people
member
English
Chinese
# 核心層｜抽象概念
thing
type
sort
tool
language
word
reason
result
problem
question
health
pain
art
music
story
job
rule
law
company
program
game
sport
ball
player
class
end
life
feeling
team
# 擴充層｜代詞・指示
hers
yours
himself
herself
itself
themselves
ourselves
# 擴充層｜語法（功能詞）
although
however
along
among
through
during
against
beside
whether
unless
instead
completely
easily
especially
forward
anyway
# 擴充層｜數量・比例
hundred
third
# 擴充層｜時間
noon
midnight
season
spring
summer
autumn
winter
calendar
moment
future
past
present
daily
weekly
monthly
yearly
recently
schedule
o'clock
sunrise
sunset
century
# 擴充層｜方位・地點
village
market
restaurant
hotel
airport
hospital
library
museum
cinema
theater
stadium
factory
church
building
area
region
far
sign
subway
block
neighborhood
gate
yard
roof
address
downtown
abroad
capital
continent
space
distance
direction
position
middle
edge
bottom
entrance
exit
platform
queue
counter
mall
clinic
pharmacy
police
boat
ship
taxi
pool
africa
america
australia
bathroom
bridge
center
china
college
court
desert
germany
ground
italy
japan
korea
path
rail
seat
slope
spain
temple
truck
university
vehicle
accident
toilet
lake
playground
garden
bicycle
# 擴充層｜自然・天氣
moon
star
cloud
mountain
hill
grass
leaf
ice
sand
stone
rock
forest
island
beach
heat
storm
temperature
nature
environment
pollution
climate
energy
electricity
metal
plastic
atom
bee
cell
cow
dirt
fuel
fur
grain
hay
horse
insect
iron
liquid
pig
planet
root
seed
sheep
snake
soil
volcano
wing
dust
# 擴充層｜動作
swim
climb
dream
marry
count
taste
smell
touch
join
paint
draw
feed
hang
spread
cover
fill
lock
knock
wave
point
smile
laugh
cry
shout
print
copy
save
add
show
cause
prepare
continue
notice
expect
agree
check
travel
translate
behave
heal
borrow
lend
rent
order
deliver
offer
affect
increase
decrease
complete
compare
discuss
refuse
avoid
prevent
improve
develop
produce
create
destroy
manage
depend
remain
contain
require
serve
press
pour
boil
matter
sound
cross
act
bend
breathe
burn
disappear
drop
enjoy
flow
hide
kill
mix
pray
repeat
respect
search
sew
shake
shoot
step
twist
zip
fight
fit
force
measure
tie
trust
vote
match
announce
hold
# 擴充層｜性質
angry
hungry
ugly
boring
funny
strange
quiet
noisy
sour
bitter
sharp
smooth
rough
thin
narrow
round
straight
purple
gray
dangerous
friendly
polite
honest
brave
lazy
clever
stupid
crazy
serious
nervous
calm
comfortable
popular
necessary
likely
quick
sudden
terrible
wonderful
pretty
alone
glad
proud
lonely
bored
worried
excited
surprised
upset
shy
alive
available
bright
cheap
dark
dead
equal
exact
fair
fat
frozen
ill
loud
normal
relaxed
religious
shiny
smart
thick
tight
usual
valuable
windy
flat
main
worth
common
wild
awake
selfish
# 擴充層｜事物
bread
egg
juice
vegetable
soup
cake
potato
tomato
chicken
breakfast
hair
ear
tooth
tongue
neck
shoulder
arm
finger
leg
knee
stomach
skin
bone
blood
pants
dress
coat
shoes
hat
socks
clothes
shoe
glasses
desk
sofa
lamp
bowl
plate
fork
spoon
pencil
photo
mirror
towel
soap
umbrella
radio
television
blanket
mouse
screen
password
account
website
email
meal
menu
cash
bath
bell
board
breath
brush
bullet
cable
camera
case
chain
cheese
cloth
coin
crowd
flour
handle
hole
hood
instrument
jacket
jaw
leather
lung
muscle
nail
needle
newspaper
nut
oven
page
pasta
pepper
poem
pot
powder
prize
rope
salad
sauce
saw
shell
soy
spice
spot
stick
strap
string
stuff
surface
tube
video
waist
wheel
wool
wound
belt
bit
file
film
fist
form
mark
thread
throat
bubble
cough
fever
glue
tail
horn
gear
bean
pedal
motor
frame
# 擴充層｜社交・人
goodbye
bye
excuse
grandmother
grandfather
uncle
aunt
cousin
boss
lady
stranger
guest
neighbor
kid
partner
leader
citizen
couple
sir
soldier
officer
scientist
artist
writer
engineer
lawyer
farmer
driver
band
crime
king
queen
judge
lover
girl
boy
mayor
actor
manager
kingdom
# 擴充層｜抽象概念
part
piece
group
system
machine
material
voice
noise
shape
size
level
degree
idea
plan
method
example
fact
truth
lie
information
knowledge
skill
ability
chance
choice
decision
difference
effect
event
experience
process
progress
purpose
quality
quantity
value
rate
power
control
influence
service
product
project
research
policy
culture
society
community
government
president
minister
party
war
peace
disease
treatment
science
technology
history
news
article
report
meeting
business
industry
software
internet
data
movie
song
lesson
test
mistake
homework
score
title
list
record
note
interest
attention
amount
sense
image
situation
condition
subject
death
angle
competition
illness
journey
length
marriage
math
mind
network
period
pressure
promise
reaction
signal
web
wedding
age
agreement
care
course
danger
effort
fear
goal
trip
habit
sentence
stock
opinion
model
state
dynasty
mechanism
movement
physics
chemistry
element
cycle
```

## 附錄：允許的字首字尾

| 字首／字尾 | 類型 | 意思 | 例子 |
|---|---|---|---|
| `un-` | prefix | not（否定） | unhappy, unclear, unsafe |
| `re-` | prefix | again / back | redo, reopen, retell |
| `-er` | suffix | a person who does it（做某事的人） | worker, teacher, driver |
| `-er` | suffix | comparative（比較級） | bigger, taller |
| `-est` | suffix | superlative（最高級） | biggest, tallest |
| `-ly` | suffix | adverb（副詞） | quickly, carefully |
| `-ness` | suffix | the quality of it（性質名詞） | kindness, sadness |

## 附錄：保留的不規則形式

| 原形 | 不規則形式 |
|---|---|
| go | went / gone |
| come | came |
| eat | ate / eaten |
| drink | drank / drunk |
| sleep | slept |
| wake | woke / woken |
| write | wrote / written |
| speak | spoke / spoken |
| say | said |
| tell | told |
| give | gave / given |
| take | took / taken |
| get | got |
| make | made |
| buy | bought |
| sell | sold |
| pay | paid |
| find | found |
| lose | lost |
| meet | met |
| leave | left |
| hear | heard |
| keep | kept |
| feel | felt |
| send | sent |
| build | built |
| run | ran |
| swim | swam |
| sing | sang |
| begin | began / begun |
| become | became |
| break | broke / broken |
| choose | chose / chosen |
| forget | forgot / forgotten |
| understand | understood |
| bring | brought |
| catch | caught |
| fall | fell / fallen |
| throw | threw / thrown |
| drive | drove / driven |
| ride | rode / ridden |
| grow | grew / grown |
| fly | flew / flown |
| wear | wore / worn |
| win | won |
| stand | stood |
| sit | sat |
| ring | rang / rung |
| hang | hung |
| show | showed / shown |
| teach | taught |
| think | thought |
| know | knew / known |
| hold | held |
| lead | led |
| mean | meant |
| lend | lent |
| spend | spent |
| child | children |
| man | men |
| woman | women |
| foot | feet |
| tooth | teeth |
| person | people |
| mouse | mice |
| knife | knives |
| wife | wives |
| life | lives |
| half | halves |
| shelf | shelves |
| potato | potatoes |
| tomato | tomatoes |
| city | cities |
| baby | babies |
| story | stories |
| country | countries |
| family | families |
| party | parties |
| lady | ladies |
| cost | cost |
| cut | cut |
| hit | hit |
| put | put |
| read | read |
| good | better / best |
| bad | worse / worst |
| far | farther / farthest |
| many | more / most |
| much | more / most |
| little | less / least |

## 附錄：片語動詞（例外）

```text
look for
look at
look after
put on
take off
get up
get off
get in
get out
find out
turn off
turn on
come back
```

## 附錄：描述用的類頭

| 類頭 | 中文 |
|---|---|
| thing | 東西 |
| person | 人 |
| place | 地方 |
| kind | 種類 |
| way | 方式 |
| part | 部分 |
| piece | 片；片段 |
| group | 群組 |
| system | 系統 |
| tool | 工具 |
| machine | 機器 |
| material | 材料 |
| food | 食物 |
| drink | 飲料 |
| animal | 動物 |
| plant | 植物 |
| language | 語言 |
| word | 單字 |
| letter | 字母 |
| number | 數字 |
| shape | 形狀 |
| size | 大小 |
| level | 程度 |
| degree | 程度 |
| reason | 原因 |
| result | 結果 |
| problem | 問題 |
| question | 問題 |
| answer | 答案 |
| idea | 想法 |
| plan | 計畫 |
| story | 故事 |
| news | 新聞 |
| article | 文章 |
| report | 報告 |
| study | 學習；研究 |
| work | 工作 |
| job | 工作 |
| rule | 規則 |
| law | 法律 |
| company | 公司 |
| team | 團隊 |
| game | 遊戲 |
| sport | 運動 |
| music | 音樂 |
| art | 藝術 |
| science | 科學 |
| history | 歷史 |
| feeling | 感覺 |
| fact | 事實 |

## 附錄：常用但禁止的詞與替代說法

這些詞很常用，但不在 Mini-English 裡。寫的時候用右欄的說法。

| 英文（不在核心層、常用） | Mini-English 說法 |
|---|---|
| a lot of | many |
| lots of | many |
| plenty of | many |
| else | other |
| furthermore | also |
| moreover | also |
| additionally | also |
| in addition | also |
| consequently | so |
| nevertheless | but |
| nonetheless | but |
| meanwhile | at the same time |
| regarding | about |
| concerning | about |
| prior to | before |
| subsequent to | after |
| in order to | to |
| due to | because of |
| despite | although |
| though | but |
| various | many |
| numerous | many |
| assorted | many |
| approximately | about |
| roughly | about |
| utilize | use |
| purchase | buy |
| obtain | get |
| acquire | get |
| assist | help |
| attempt | try |
| determine | decide |
| demonstrate | show |
| indicate | show |
| involve | include |
| maintain | keep |
| achieve | get |
| encounter | meet |
| realize | know |
| recognize | know |
| consider | think about |
| imagine | think |
| perhaps | maybe |
| probably | likely |
| nearly | almost |
| barely | only a little |
| rather | a little |
| extremely | very |
| utterly | very |
| completely | all |
| entirely | all |
| totally | all |
| partially | some |
| mostly | most |
| frequently | often |
| occasionally | sometimes |
| regularly | often |
| currently | now |
| previously | before |
| eventually | later |
| immediately | right away |
| briefly | for a short time |
| gradually | slowly |
| finally | at last |
| actually | in fact（核心層） |
| yeah | yes |
| nope | no |
| gonna | going to |
| wanna | want to |
| gotta | have to |
| gotten | got |
| kids | children |
| guys | people |
| folks | people |
| a bit | a little |
| kind of | a little |
| sort of | a little |
| lots | many |
| once upon a time | long ago |
| whoever | anyone |
| whatever | anything |
| whichever | any one of them |
| whenever | at any time |
| wherever | in any place |
| thus | so |
| somewhat | a little |
| exceedingly | very |
| highly | very |
| truly | really |
| certainly | yes |
| absolutely | very |
| fully | all |
| hardly | almost |
| lately | recently |
| formerly | before |
| alright | okay |
| cheers | thanks |
| great | very good |
| awful | very bad |
| terrible | very bad |
| wonderful | very good |
| excellent | very good |
| horrible | very bad |
| gorgeous | very beautiful |
| awesome | very good |
| delicious | very good |
| tiny | very small |
| huge | very big |
| large | big |
| enormous | very big |
| immense | very big |
| massive | very big |
| broad | wide |
| further | more |
| latest | newest |
| closest | nearest |
| via | by |
| per | for |
| except | but |
