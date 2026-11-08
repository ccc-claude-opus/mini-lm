// Mini-English 引擎：一般英文 ⇄ Mini-English，以及詞表檢查。
// 規則來自 mini-english/mini-english.md，資料來自 data.js（由 web/build.py 產生）。
// 網頁和 Node 測試共用這個檔案。

(function (root) {
  'use strict';

  const TOKEN = /[A-Za-z]+(?:['’][A-Za-z]+)*(?:-[A-Za-z]+)*|\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?|[\u4e00-\u9fff\u3400-\u4dbf]+/g;
  const HAN = /[\u4e00-\u9fff\u3400-\u4dbf]/;
  const WORD = /[A-Za-z]+(?:['’][A-Za-z]+)*/;
  const NOT_STEMS = { wo: 'will', ca: 'can', sha: 'shall', mu: 'must', ne: 'need',
    ai: 'is', ar: 'are', we: 'were', ha: 'has', do: 'does' };
  const PROPER = new Set(['paris', 'china', 'japan', 'korea', 'taiwan', 'india', 'england', 'scotland',
    'wales', 'ireland', 'france', 'germany', 'italy', 'spain', 'russia', 'canada', 'australia',
    'brazil', 'mexico', 'london', 'tokyo', 'beijing', 'shanghai', 'hong', 'kong', 'taipei', 'seoul',
    'new', 'york', 'los', 'angeles', 'osaka', 'kyoto', 'europe', 'asia', 'africa', 'america',
    'european', 'asian', 'african', 'american', 'chinese', 'japanese', 'korean', 'english',
    'french', 'german', 'spanish', 'italian', 'russian', 'british', 'covid', 'instagram', 'google',
    'apple', 'microsoft', 'amazon', 'toyota', 'samsung', 'wifi', 'internet', 'email', 'iphone',
    'youtube', 'facebook', 'twitter']);

  function create(DATA) {
    const forms = new Set(DATA.forms);
    const words = new Set(DATA.words.map((w) => w[0].toLowerCase()));
    const posOf = new Map(DATA.words.map((w) => [w[0].toLowerCase(), w[3]]));
    const infoOf = new Map(DATA.words.map((w) => [w[0].toLowerCase(), w]));
    const forbidden = DATA.forbidden || {};

    // ==========================================
    // 1. 檢查（對應 check.py 的規則）
    // ==========================================
    const contractionOk = (token) => {
      const t = token.toLowerCase().replace(/’/g, "'");
      if (forms.has(t)) return true;
      if (t === 'cannot') return true;
      if (t.endsWith("n't")) {
        let stem = t.slice(0, -3);
        stem = NOT_STEMS[stem] || stem;
        return forms.has(stem);
      }
      if (t.endsWith("'s")) return forms.has(t.slice(0, -2));
      for (const [suf, repl] of [["'ll", 'will'], ["'ve", 'have'], ["'re", 'are'], ["'m", 'am']]) {
        if (t.endsWith(suf)) return forms.has(t.slice(0, -t.length + suf.length) === '' ? '' : t.slice(0, t.length - suf.length));
      }
      if (t.endsWith("'d")) return forms.has(t.slice(0, -2));
      return false;
    };

    const derivable = (w) => {
      for (const p of DATA.affixes.prefixes) {
        if (w.startsWith(p) && w.length > p.length) {
          const stem = w.slice(p.length);
          if (forms.has(stem)) {
            const kinds = (posOf.get(stem) || '').split('/');
            if (p === 'un' && kinds.includes('adj')) return true;
            if (p === 're' && kinds.includes('v')) return true;
          }
        }
      }
      for (const s of DATA.affixes.suffixes) {
        if (w.endsWith(s) && w.length > s.length) {
          const stem = w.slice(0, -s.length);
          if (forms.has(stem)) {
            const kinds = (posOf.get(stem) || '').split('/');
            if (s === 'er' && (kinds.includes('v') || kinds.includes('adj'))) return true;
            if (s === 'est' && kinds.includes('adj')) return true;
            if (s === 'ly' && kinds.includes('adj')) return true;
            if (s === 'ness' && kinds.includes('adj')) return true;
          }
        }
      }
      return false;
    };

    const sentenceStart = (text, pos) => {
      for (let i = pos - 1; i >= 0; i--) {
        const c = text[i];
        if ('.!?\n'.includes(c)) return true;
        if (/[A-Za-z0-9一-鿿]/.test(c)) return false;
      }
      return true;
    };

    // 回傳 [{type:'外來詞'|'未知詞'|'禁用詞', msg, token, index}]
    function check(text) {
      const errors = [];
      const defined = new Set();
      // 多字禁用詞（a lot of、in order to…）先抓，抓到後整段跳過
      const phraseSpans = [];
      const phrases = Object.keys(forbidden).filter((p) => p.includes(' ')).sort((a, b) => b.length - a.length);
      for (const phrase of phrases) {
        const re = new RegExp('(?<![A-Za-z])' + phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![A-Za-z])', 'gi');
        let pm;
        while ((pm = re.exec(text)) !== null) {
          errors.push({ type: '禁用詞', msg: `「${pm[0]}」是禁用詞，改用「${forbidden[phrase]}」`, token: pm[0], index: pm.index });
          phraseSpans.push([pm.index, pm.index + pm[0].length]);
        }
      }
      // 括號說明往前認專有名詞（The Great Wall of China (…)、Li Ming (…)）
      const re = /([A-Z][A-Za-z]*(?:\s+[A-Za-z]+)*)\s*\(/g;
      let m;
      while ((m = re.exec(text)) !== null) {
        for (const w of m[1].split(/\s+/)) if (/^[A-Z]/.test(w)) defined.add(w);
      }
      const parenSpans = [];
      const pre = /(\(([^()]*)\))/g;
      while ((m = pre.exec(text)) !== null) parenSpans.push([m.index, m.index + m[0].length]);

      const inParen = (pos) => parenSpans.some(([a, b]) => a <= pos && pos < b);
      TOKEN.lastIndex = 0;
      while ((m = TOKEN.exec(text)) !== null) {
        const tok = m[0];
        const pos = m.index;
        if (phraseSpans.some(([a, b]) => a <= pos && pos < b)) continue;
        const par = inParen(pos);
        if (/^\d/.test(tok)) continue;
        if (HAN.test(tok)) {
          if (par) continue;
          const nxt = text.slice(m.index + tok.length).replace(/^\s+/, '');
          if (nxt.startsWith('(')) { defined.add(tok); continue; }
          if (defined.has(tok)) continue;
          errors.push({ type: '外來詞', msg: `中文外來詞「${tok}」第一次出現時必須有括號說明`, token: tok, index: pos });
          continue;
        }
        if (tok.includes('-')) {
          for (const part of tok.split('-').filter(Boolean)) {
            const p = part.toLowerCase();
            if (!forms.has(p) && !contractionOk(part)) errors.push({ type: '未知詞', msg: `「${part}」不在詞表內`, token: part, index: pos });
          }
          continue;
        }
        const low = tok.toLowerCase();
        if (forms.has(low)) continue;
        if (contractionOk(tok)) continue;
        const nxt = text.slice(m.index + tok.length).replace(/^\s+/, '');
        if (!par && nxt.startsWith('(')) { defined.add(tok); continue; }
        if (defined.has(tok) || defined.has(low)) continue;
        if (derivable(low)) continue;
        if (forbidden[low] && !/^[A-Z]/.test(tok)) {
          errors.push({ type: '禁用詞', msg: `「${tok}」是禁用詞，改用「${forbidden[low]}」`, token: tok, index: pos });
          continue;
        }
        if (/^[A-Z]/.test(tok)) {
          if (par) continue;
          if (PROPER.has(low) || !sentenceStart(text, pos)) {
            errors.push({ type: '外來詞', msg: `「${tok}」是外來詞，第一次出現時必須有括號說明`, token: tok, index: pos });
            continue;
          }
        }
        errors.push({ type: '未知詞', msg: `「${tok}」不在詞表內（用描述或外來詞）`, token: tok, index: pos });
      }
      return errors;
    }

    // ==========================================
    // 2. 一般英文 → Mini-English
    // ==========================================
    // 詞典裡的「描述／外來詞」條目：英文詞 → Mini-English
    const forward = new Map();
    for (const [eng, mini, way, note] of DATA.lexicon) {
      if (way === '本詞' || !mini) continue;
      if (way !== '外來詞' && mini === eng) continue;   // 外來詞保留原詞是正常的
      const key = eng.toLowerCase();
      if (forms.has(key)) continue;                    // 已經在詞表內的詞直接用，不用描述
      if (!forward.has(key)) forward.set(key, { mini, way, note });
    }
    // 多字條目（bus stop）也要能換
    const multi = [...forward.keys()].filter((k) => k.includes(' ')).sort((a, b) => b.length - a.length);
    const forwardMax = Math.max(...[...forward.keys()].map((k) => k.length));

    const singular = (w) => {
      if (w.endsWith('ies') && w.length > 3) return w.slice(0, -3) + 'y';
      if (w.endsWith('es') && w.length > 2) return w.slice(0, -2);
      if (w.endsWith('s') && w.length > 1) return w.slice(0, -1);
      return null;
    };

    // 回傳 tokens：{type, text, from?, info?, loan?, note?}
    //   plain：照抄；sub：詞典換掉的詞；loan：外來詞（說明放在 note）；hint：要依句子改寫；bad：詞表外、詞典沒有
    function toMini(input) {
      const tokens = [];
      const seenLoan = new Set();
      let i = 0;
      const text = input;
      while (i < text.length) {
        // 先找多字條目
        let matched = null;
        const lower = text.slice(i, i + forwardMax).toLowerCase();
        for (const key of multi) {
          if (lower.startsWith(key)) {
            const after = text.slice(i + key.length);
            if (/[A-Za-z]/.test(after[0] || '')) continue;
            matched = { len: key.length, entry: forward.get(key) };
            break;
          }
        }
        if (!matched) {
          const m2 = /^[A-Za-z]+(?:['’][A-Za-z]+)*/.exec(text.slice(i));
          if (m2) {
            const w = m2[0];
            const key = w.toLowerCase();
            if (forward.has(key)) matched = { len: w.length, entry: forward.get(key) };
            else {
              const s = singular(key);
              if (s && forward.has(s)) {
                matched = { len: w.length, entry: forward.get(s), plural: true };
              }
            }
          }
        }
        if (matched) {
          const e = matched.entry;
          const original = text.slice(i, i + matched.len);
          if (matched.plural) {
            tokens.push({ type: 'hint', text: e.mini, from: original, info: '複數要依句子改寫，建議：' + e.mini });
          } else if (e.way === '外來詞') {
            const first = !seenLoan.has(e.mini);
            seenLoan.add(e.mini);
            tokens.push({ type: 'sub', text: e.mini, from: original, loan: true, note: e.note, first });
          } else {
            tokens.push({ type: 'sub', text: e.mini, from: original });
          }
          i += matched.len;
          continue;
        }
        // 其他文字照抄
        const m3 = /^[A-Za-z]+(?:['’][A-Za-z]+)*/.exec(text.slice(i));
        if (m3) {
          const w = m3[0];
          const low = w.toLowerCase();
          if (!forms.has(low) && !contractionOk(w)) {
            const e = forward.get(low);
            tokens.push({ type: 'bad', text: w, info: '詞表外，詞典也沒有' });
          } else {
            tokens.push({ type: 'plain', text: w });
          }
          i += w.length;
          continue;
        }
        const ch = text[i];
        tokens.push({ type: 'plain', text: ch });
        i += 1;
      }
      return tokens;
    }

    // ==========================================
    // 3. Mini-English → 一般英文
    // ==========================================
    const backward = new Map();
    for (const [eng, mini, way] of DATA.lexicon) {
      if (way === '本詞' || !mini || mini === eng) continue;
      const key = mini.toLowerCase();
      if (!backward.has(key)) backward.set(key, eng);
    }
    for (const [mini, eng] of Object.entries(DATA.reverse || {})) {
      backward.set(mini.toLowerCase(), eng);
    }
    const backKeys = [...backward.keys()].sort((a, b) => b.length - a.length);

    function toEnglish(input) {
      const tokens = [];
      let i = 0;
      const low = input.toLowerCase();
      while (i < input.length) {
        let hit = null;
        for (const key of backKeys) {
          if (low.startsWith(key, i)) {
            const after = input.slice(i + key.length);
            if (/[A-Za-z]/.test(after[0] || '')) continue;
            hit = { len: key.length, eng: backward.get(key) };
            break;
          }
        }
        if (hit) {
          tokens.push({ type: 'sub', text: hit.eng, from: input.slice(i, i + hit.len) });
          i += hit.len;
          continue;
        }
        const m = /^[A-Za-z]+(?:['’][A-Za-z]+)*/.exec(input.slice(i));
        if (m) {
          tokens.push({ type: 'plain', text: m[0] });
          i += m[0].length;
          continue;
        }
        tokens.push({ type: 'plain', text: input[i] });
        i += 1;
      }
      return tokens;
    }

    // ==========================================
    // 4. 詞表查詢
    // ==========================================
    function wordInfo(word) {
      return infoOf.get(String(word).toLowerCase()) || null;
    }

    function search(q) {
      const s = String(q || '').trim().toLowerCase();
      if (!s) return DATA.words;
      return DATA.words.filter((w) => w[0].toLowerCase().includes(s) || w[4].includes(s));
    }

    return { check, toMini, toEnglish, wordInfo, search, forms, words, posOf };
  }

  const api = { create };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof root !== 'undefined') root.MiniEnglish = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
