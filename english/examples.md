# Mini-English 翻譯範例

這裡的每一段都是「一般英文 → Mini-English」的完整改寫。**改寫後的文字必須是正確、自然的英文**，
而且每個詞都在 [mini-english.md](mini-english.md) 的詞表內（`python check.py --file examples.md` 會檢查）。

三層表達法在這裡都可以看到：

- **本詞**：`park`, `people`, `children`, `minutes`…
- **描述**：`a green place with trees where people walk and play`（表外的概念，用表內的詞說清楚）
- **外來詞**：`Riverdale (a small city in the north of the country)`（說不出是哪一個的名字，第一次出現時說明，之後直接用）

> **長度怎麼算**：以「詞」為單位（中文的標點與空白不算）。Mini-English 的長度比較是這個設計最重要的代價：
> 描述越多，文章越長。下面的數字是實測。

---

## 範例一：新聞

**一般英文**

```text
The city of Riverdale opened a new park on Saturday. The park has a large green area, a small lake, and a playground for children. More than three hundred people came on the first day. The mayor said the park was built because the old park was too small and there were not enough places for children to play. Families in the city can now walk to the park in ten minutes. The city plans to build two more parks before the end of 2027.
```

**Mini-English**

```en
On Saturday the city of Riverdale (a small city in the north of the country) opened a new park.
The park has a big green area, a small lake and a playground (a place with games for children).
More than 300 people came on the first day.
The mayor (the person who leads a city) said the park was made because the old park was too small and there were not enough places for children to play.
Now families in the city can walk to the park in 10 minutes.
The city plans to build 2 more parks before the end of 2027.
```

**長度比較**：一般英文 85 詞 → Mini-English 103 詞（+18 詞，+21%）

---

## 範例二：說明文（怎麼煮好一杯茶）

**一般英文**

```text
Good tea is easy to make, but you need to follow four steps. First, heat the water until it just starts to make small bubbles. Second, put the tea in your cup and wait for one minute. Third, pour the hot water into the cup. Do not pour all the water, because the tea will become too strong. Last, wait one more minute and drink. You can add more water if the tea is too strong for you. Many people like to add milk or sugar, but good tea does not need them.
```

**Mini-English**

```en
Good tea is easy to make, but you must follow 4 steps.
First, heat the water until it starts to make small bubbles.
Second, put the tea in your cup and wait for 1 minute.
Third, pour the hot water into the cup. Do not pour all the water, because then the tea will be too strong.
Last, wait 1 more minute and drink.
You can add more water if the tea is too strong for you.
Many people like to add milk or sugar, but good tea does not need them.
```

**長度比較**：一般英文 93 詞 → Mini-English 92 詞（-1 詞，-1%）

---

## 範例三：故事

**一般英文**

```text
Long ago, a small dog lived in a small village near the sea. Every day he looked for food, but the village was poor and there was little to eat. One winter day, the dog was very hungry and very cold. He found a fishing boat near the water. The people on the boat gave him fish every day. After one year, the dog was big and strong. He never went back to the village. He slept on the boat and he ate every day, and in the evening he looked at the sea with his old friend.
```

**Mini-English**

```en
Long ago, a small dog lived in a small village (a small town in the country) near the sea.
Every day he looked for food, but the village was poor and there was little to eat.
1 winter day, the dog was very hungry and very cold.
He found a fishing boat (a big boat that people use to catch fish) near the land.
The people on the boat gave him fish every day.
After 1 year, the dog was big and strong.
He never went back to the village. He slept on the boat and he ate every day, and in the evening he looked at the sea with his old friend.
```

**長度比較**：一般英文 98 詞 → Mini-English 113 詞（+15 詞，+15%）

---

## 範例四：對話（在醫院）

**一般英文**

```text
A: Good morning. What is wrong?
B: I have had a bad cough since Monday, and I feel very tired.
A: Do you have a fever?
B: A little. I also have a pain in my throat when I drink cold water.
A: Let me look at your throat. Your throat is not very bad, but your nose is stopped. You have a common cold. You must rest at home for two days and drink a lot of water.
B: Do I need to take medicine?
A: Yes, take this twice a day after you eat. Come back in three days if you do not get better.
B: Thank you, doctor. I will rest.
```

**Mini-English**

```en
A: Good morning. What is wrong?
B: I have a bad cough since Monday, and I feel very tired.
A: Do you have a fever?
B: A little. I also have a pain in my throat when I drink cold water.
A: Let me look at your throat. Your throat is not very bad, but you cannot breathe well through your nose. You have a common cold. You must rest at home for 2 days and drink much water.
B: Do I need to take medicine?
A: Yes, take this 2 times a day after you eat. Come back in 3 days if you do not get better.
B: Thank you, doctor. I will rest.
```

**長度比較**：一般英文 114 詞 → Mini-English 112 詞（-2 詞，-2%）

---

## 範例五：科普（天空為什麼是藍的）

**一般英文**

```text
The sky looks blue because the air is full of small things that we cannot see. When white light from the sun comes into the air, these small things send the blue light in all directions much more than the other colors. This is the same reason that the sky is red at sunrise and sunset. At that time the light must travel through much more air, so most of the blue light is scattered away before it reaches your eyes. The light that reaches you is most of all red and orange. Scientists have studied this for 100 years, and today we can measure it with machines.
```

**Mini-English**

```en
The sky looks blue because the air is full of very small things that we cannot see.
When white light from the sun comes into the air, these small things send the blue light in all directions much more than the other colors.
This is the same reason that the sky is red at sunrise and sunset.
At that time the light must go through much more air, so most of the blue light goes away before it reaches your eyes.
The light that reaches you is most of all red and orange.
Scientists (people who study how the world works) have studied this for 100 years, and today we can measure it with machines.
```

**長度比較**：一般英文 105 詞 → Mini-English 113 詞（+8 詞，+8%）

---

## 範例六：生活（一天的習慣）

**一般英文**

```text
I have four good habits that changed my life. First, I get up at seven every morning, even on Sunday. Second, I read for twenty minutes before I look at my phone. Third, I walk home instead of taking the bus, which takes about thirty minutes. Last, I go to bed at eleven and I do not look at my phone after ten. These small things are not hard, but you need to do them every day for two or three months before you see a real change. A friend told me that the hardest part is not the first week, but the hundredth day.
```

**Mini-English**

```en
I have 4 good habits (things you do again and again) that changed my life.
First, I get up at 7 every morning, even on Sunday.
Second, I read for 20 minutes before I look at my phone.
Third, I walk home instead of taking the bus. It takes about 30 minutes.
Last, I go to bed at 11 and I do not look at my phone after 10.
These small things are not hard, but you must do them every day for 2 or 3 months before you see a real change.
A friend told me that the hardest part is not the first week, but the 100th day.
```

**長度比較**：一般英文 105 詞 → Mini-English 110 詞（+5 詞，+5%）

---

## 反向翻譯一：Mini-English → 一般英文

**Mini-English**

```en
Last week I went to the city with my friend Anna (a woman who works with me).
We saw a very old building with big windows and a small garden in front of it.
Anna said it was a museum (a place where people look at old things) of old machines.
There were many people there, and we waited 20 minutes for the door.
In the end we did not go in, because we were too tired.
We went back home and made some food.
It was not a very good day, but it was fun.
```

**一般英文**

```text
Last week I went to the city with my friend Anna. We saw a very old building with big windows and a small garden in front of it. Anna said it was a museum of old machines. There were many people there, and we waited twenty minutes for the door. In the end we did not go in, because we were too tired. We went back home and made some food. It was not a very good day, but it was fun.
```

**長度比較**：Mini-English 96 詞 → 一般英文 82 詞（-14 詞，-15%）

---

## 反向翻譯二：Mini-English → 一般英文

**Mini-English**

```en
If you want to learn English fast, do 3 things.
First, learn 10 new words every day and use them in a sentence.
Second, listen to English for 30 minutes every day. Do not just read.
Third, speak with a person every week, even if you are afraid.
Many people want to learn a language, but few people keep doing it for 6 months.
The people who can speak a new language are not the smart people. They are the people who go on.
```

**一般英文**

```text
If you want to learn English fast, do three things. First, learn ten new words every day and use them in a sentence. Second, listen to English for thirty minutes every day. Do not just read. Third, speak with a person every week, even if you are afraid. Many people want to learn a language, but few people keep doing it for six months. The people who can speak a new language are not the smart people. They are the people who go on.
```

**長度比較**：Mini-English 84 詞 → 一般英文 84 詞（+0 詞，+0%）

---

## 從這些範例可以看到的規則

1. **數字一律用阿拉伯數字**：`ten` → `10`，`three hundred` → `300`，`twenty minutes` → `20 minutes`。
2. **能省的字就省**：英文的冠詞在中文裡不需要的地方不要硬加；`the city plans to build` 保留（自然英文需要）。
3. **描述要短**：本篇的描述平均 8–10 個詞，超過就改用外來詞。
4. **同一篇文章裡，外來詞只要說明一次**：`Riverdale` 說明過之後就直接用。
5. **不要為了省詞而寫出不自然的英文**：例如 `a place where people look at old things` 可以，但 `a thing for looking old things` 不行。
