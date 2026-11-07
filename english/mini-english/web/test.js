// Mini-English 引擎的測試：node web/test.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, 'data.js'), 'utf8') + ';this.DATA = DATA;', ctx);
const ME = require(path.join(__dirname, 'minienglish.js')).create(ctx.DATA);

const text = (tokens) => tokens.map((t) => t.text).join('');
const types = (tokens) => tokens.filter((t) => t.type !== 'plain').map((t) => `${t.type}:${t.text}`).join(' ');

const cases = [
  // ── 檢查：合規則的 ──
  ['表內的句子', ME.check('I am a student and she goes to work by bus.').length, 0],
  ['縮寫', ME.check("I don't like it. She's my friend. It's fine.").length, 0],
  ['屈折形式', ME.check('The children went to the shops and he was running.').length, 0],
  ['不規則複數', ME.check('2 children and 3 women with many feet.').length, 0],
  ['數字', ME.check('I have 20 books and 3 pens at 7:30.').length, 0],
  ['字首字尾', ME.check('The worker was quickly unhappy with the taller man.').length, 0],
  ['片語動詞', ME.check('Please look for my book and put on your coat.').length, 0],
  ['外來詞有說明', ME.check('I went to Paris (a big city in France) last year.').length, 0],
  ['外來詞第二次出現不用說明', ME.check('I went to Paris (a big city in France). Paris is nice.').length, 0],
  ['多字專有名詞', ME.check('Marie Curie (a woman from Poland) won a prize.').length, 0],
  ['中文專有名詞有說明', ME.check('我住在上海 (a big city in China)。').length, 0],

  // ── 檢查：抓得到 ──
  ['表外的詞', ME.check('I ate a hamburger.').map((e) => e.type)[0], '未知詞'],
  ['多字禁用詞', ME.check('a lot of books').map((e) => e.type)[0], '禁用詞'],
  ['禁用詞', ME.check('a lot of books').map((e) => e.type)[0], '禁用詞'],
  ['外來詞缺說明', ME.check('I went to Paris last year.').map((e) => e.type)[0], '外來詞'],
  ['句首大寫的表外詞', ME.check('Zebras run.').map((e) => e.type)[0], '未知詞'],
  ['句中的大寫表外詞是外來詞', ME.check('The Zebra runs.').map((e) => e.type)[0], '外來詞'],

  // ── English → Mini-English ──
  ['表內的詞照抄', text(ME.toMini('I am a student.')), 'I am a student.'],
  ['換掉的詞', types(ME.toMini('I ate a hamburger.')), 'sub:bread with meat inside'],
  ['外來詞保留原詞', types(ME.toMini('A panda lives here.')), 'sub:panda'],
  ['複數要改寫', ME.toMini('I ate 2 hamburgers.').filter((t) => t.type === 'hint').length, 1],

  // ── Mini-English → English ──
  ['反譯', text(ME.toEnglish('I went to the place where doctors help sick people.')), 'I went to hospital.'],
  ['反譯：外來詞保留', text(ME.toEnglish('A panda is a black and white animal from China.')), 'A panda is a black and white animal from China.'],

  // ── 詞表 ──
  ['查詞', (ME.wordInfo('go') || [])[4], '去'],
  ['查詞的 IPA', (ME.wordInfo('doctor') || [])[1], ctx.DATA.words.find((w) => w[0] === 'doctor')[1]],
  ['搜尋', ME.search('doctor').length > 0, true],
];

let failed = 0;
for (const [name, got, want] of cases) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) failed++;
  console.log(`${ok ? '✅' : '❌'} ${name}${ok ? '' : `\n   得到：${got}\n   應為：${want}`}`);
}
console.log(failed ? `❌ ${failed} 個失敗` : `✅ ${cases.length} 個全部通過`);
process.exit(failed ? 1 : 0);
