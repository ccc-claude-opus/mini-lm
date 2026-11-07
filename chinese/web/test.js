// 翻譯引擎的測試：node web/test.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, 'data.js'), 'utf8') + ';this.DATA = DATA;', ctx);
const ML = require(path.join(__dirname, 'minilang.js')).create(ctx.DATA);

const text = (tokens) => tokens.map((t) => t.text).join('');
const pinyin = (s) => ML.readings(s).filter(Boolean).map(ML.toneMark).join(' ');

const cases = [
  // 數字（和 mini-lang/to_digits.py 相同）
  ['數字', ML.toDigits('他二十二歲，星期六要去三百公里外的地方。'), '他22歲，週6要去300公里外的地方。'],
  ['概數', ML.toDigits('兩三天就好了'), '2到3天就好了'],
  ['固定說法不動', ML.toDigits('我們一起去，兩個人一樣高'), '我們一起去，兩個人一樣高'],
  // 中文 → Mini-Lang
  ['量詞與外來語（畫面上不含說明）', text(ML.toMini('我家有一隻狗，狗很可愛。')), '我家有一個 dog，dog 很可愛。'],
  ['複製的文字：第一次出現時附上說明', ML.plainText(ML.toMini('我家有一隻狗，狗很可愛。')),
    '我家有一個 dog（會看家、會叫的小東西），dog 很可愛。'],
  ['反向的外來語說明', ML.loanTokens('一個 dog（會看家的東西）和 apple').filter((t) => t.loan).map((t) => `${t.text}:${t.note}`).join(' '),
    'dog:會看家的東西 apple:紅色的、比手小一點的水果'],
  ['描述', text(ML.toMini('我去醫院')), '我去看病的地方'],
  ['要改寫的詞只標出來', ML.toMini('雖然下雨').find((t) => t.type === 'hint').text, '雖然'],
  // Mini-Lang → 中文
  ['反譯', text(ML.toZh('我家有一個 dog（會看家、會叫的小東西）。我天天和 dog 出去走走，看見很多 apple。')),
    '我家有一個狗。我天天和狗出去走走，看見很多蘋果。'],
  ['反譯：外來語要整個詞相符', text(ML.toZh('我有很多 apples')), '我有很多 apples'],
  // 第 3 版：被刪的字要換掉，新加的字直接用
  ['被刪的字', text(ML.toMini('如果你跟我去，事情就很容易。')), '要是你和我去，事就不難。'],
  ['新加的字直接用', text(ML.toMini('樹上有鳥，河裡有魚。')), '樹上有鳥，河裡有魚。'],
  ['新字的拼音', pinyin('音樂很好聽，有空來玩'), 'yīn yuè hěn hǎo tīng yǒu kòng lái wán'],
  // 拼音
  ['一、不變調', pinyin('一個人不是一起去'), 'yí gè rén bú shì yì qǐ qù'],
  ['多音字與輕聲', pinyin('我覺得他睡覺了'), 'wǒ jué de tā shuì jiào le'],
  ['很快地', pinyin('他很快地長大了'), 'tā hěn kuài de zhǎng dà le'],
];

let failed = 0;
for (const [name, got, want] of cases) {
  const ok = got === want;
  if (!ok) failed++;
  console.log(`${ok ? '✅' : '❌'} ${name}${ok ? '' : `\n   得到：${got}\n   應為：${want}`}`);
}
console.log(failed ? `❌ ${failed} 個失敗` : `✅ ${cases.length} 個全部通過`);
process.exit(failed ? 1 : 0);
