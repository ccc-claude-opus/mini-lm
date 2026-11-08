// Mini-English 翻譯器的介面。規則在 minienglish.js，資料在 data.js（由 web/build.py 產生）。
(function () {
  'use strict';
  const ME = MiniEnglish.create(DATA);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const LANG = { en: 'English', mini: 'Mini-English' };
  const PLACEHOLDER = {
    en: '在這裡輸入或貼上 English 的文章',
    mini: '在這裡輸入或貼上 Mini-English 的文章',
  };

  const state = { src: 'en', dst: 'mini' };
  try {
    const saved = JSON.parse(localStorage.getItem('mini-english') || '{}');
    if (saved.src && saved.dst) Object.assign(state, saved);
  } catch (e) { /* 沒有儲存空間也能用 */ }
  const save = () => {
    try { localStorage.setItem('mini-english', JSON.stringify(state)); } catch (e) { /* 忽略 */ }
  };

  // ---------- 畫出結果 ----------
  function render(tokens) {
    return tokens.map((t) => {
      const body = esc(t.text);
      if (t.type === 'plain') return body;
      if (t.loan) {
        const tip = [t.note ? `（${t.note}）` : '', t.from ? `原文：${t.from}` : ''].filter(Boolean).join('\n');
        return `<span class="sub loan" tabindex="0" title="${esc(tip)}">${body}</span>`;
      }
      if (t.type === 'hint') {
        const tip = [t.from ? `原文：${t.from}` : '', t.info || ''].filter(Boolean).join('\n');
        return `<span class="hint" tabindex="0" title="${esc(tip)}">${body}</span>`;
      }
      const tip = [t.from ? `原文：${t.from}` : '', t.info || ''].filter(Boolean).join('\n');
      return `<span class="${t.type}" tabindex="0" title="${esc(tip)}">${body}</span>`;
    }).join('');
  }

  const plainText = (tokens) => tokens.map((t) => {
    if (t.loan && t.first && t.note) return `${t.text}（${t.note}）`;
    return t.text;
  }).join('');

  // ---------- 翻譯 ----------
  function translate() {
    const text = $('input').value;
    const src = state.src, dst = state.dst;
    $('in-label').textContent = LANG[src];
    $('out-label').textContent = LANG[dst];
    $('input').placeholder = PLACEHOLDER[src];
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    $('in-count').textContent = words ? `${words} 詞` : '';
    if (!text.trim()) {
      $('output').textContent = '';
      $('stats').textContent = '';
      $('notes').innerHTML = '';
      return;
    }
    const tokens = src === 'en' ? ME.toMini(text) : ME.toEnglish(text);
    $('output').innerHTML = render(tokens);

    // 統計
    const changed = tokens.filter((t) => t.type === 'sub' || t.type === 'hint').length;
    const bad = tokens.filter((t) => t.type === 'bad').length;
    const loans = tokens.filter((t) => t.loan).length;
    const direct = src === 'en' ? words - changed - bad : words;
    $('stats').innerHTML = [
      `輸入 <b>${words}</b> 詞`,
      `直接可用 <b>${Math.max(direct, 0)}</b> 詞`,
      `換掉 <b>${changed}</b> 個`,
      loans ? `外來詞 <b>${loans}</b> 個` : '',
      bad ? `<b style="color:var(--bad-line)">表外的詞 ${bad} 個</b>` : '',
    ].filter(Boolean).join(' · ');

    // 換詞清單
    const notes = [];
    tokens.forEach((t) => {
      if (t.loan) notes.push(`<li class="loan">外來詞 <code>${esc(t.text)}</code>${t.note ? `：${esc(t.note)}` : ''}${t.from ? `　原文：${esc(t.from)}` : ''}</li>`);
      else if (t.type === 'sub') notes.push(`<li>${esc(t.from)} → <code>${esc(t.text)}</code></li>`);
      else if (t.type === 'hint') notes.push(`<li class="forbid">${esc(t.from)}：${esc(t.info || '')}</li>`);
      else if (t.type === 'bad') notes.push(`<li class="bad">表外：<code>${esc(t.text)}</code>（${esc(t.info || '')}）</li>`);
    });
    $('notes').innerHTML = notes.join('');
    save();
  }

  // ---------- 檢查 ----------
  function runCheck() {
    const text = $('input').value.trim();
    if (!text) { $('checklist').innerHTML = '<li>先在上面輸入一段文字。</li>'; return; }
    const errors = ME.check(text);
    if (!errors.length) {
      $('checklist').innerHTML = '<li>✅ 全部在詞表內。</li>';
      return;
    }
    $('checklist').innerHTML = errors.map((e) => {
      const cls = e.type === '禁用詞' ? 'forbid' : (e.type === '外來詞' ? 'loan' : 'bad');
      return `<li class="${cls}">${esc(e.msg)}</li>`;
    }).join('');
  }

  // ---------- 詞表 ----------
  function renderWords() {
    const q = $('q').value;
    const onlyCore = $('coreonly').checked;
    let list = ME.search(q);
    if (onlyCore) list = list.filter((w) => w[2] === '核心');
    $('wordcount').textContent = DATA.words.length;
    if (!list.length) { $('wordlist').innerHTML = '<p class="tagline">沒有找到。</p>'; return; }
    const groups = new Map();
    for (const w of list) {
      const key = w[7] || '其他';
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(w);
    }
    let html = '';
    for (const [name, ws] of groups) {
      html += `<h3>${esc(name)}（${ws.length}）</h3><table class="wordtable"><tr><th>詞</th><th>IPA</th><th>層</th><th>詞性</th><th>中文</th><th>例子</th></tr>`;
      for (const w of ws) {
        const badge = w[2] === '核心' ? '<span class="badge core">核心</span>' : '<span class="badge ext">擴充</span>';
        html += `<tr><td>${esc(w[0])}</td><td class="ipa">/${esc(w[1])}/</td><td>${badge}</td><td>${esc(w[3])}</td><td>${esc(w[4])}</td><td>${esc(w[6])}</td></tr>`;
      }
      html += '</table>';
    }
    $('wordlist').innerHTML = html;
  }

  // ---------- 規則與範例 ----------
  function renderRules() {
    $('rules').innerHTML = DATA.rules.map(([title, ex]) =>
      `<div class="card"><h4>${esc(title)}</h4><p class="mono">${esc(ex)}</p></div>`).join('');
  }

  function renderExamples() {
    $('examples-list').innerHTML = DATA.examples.map(([title, dir, text]) =>
      `<div class="card"><h4>${esc(title)}</h4><p class="mono">${esc(text.slice(0, 220))}${text.length > 220 ? '…' : ''}</p>
       <button class="ghost small" data-dir="${esc(dir)}" data-text="${esc(text)}">放進輸入框</button></div>`).join('');
    $('examples-list').addEventListener('click', (ev) => {
      const btn = ev.target.closest('button[data-text]');
      if (!btn) return;
      $('input').value = btn.getAttribute('data-text');
      state.src = btn.getAttribute('data-dir') === 'to-mini' ? 'en' : 'mini';
      state.dst = state.src === 'en' ? 'mini' : 'en';
      $('src').value = state.src; $('dst').value = state.dst;
      translate();
    });
  }

  function fillExampleSelect() {
    const sel = $('examples');
    sel.innerHTML = '<option value="">— 選一個範例 —</option>' +
      DATA.examples.map(([title, dir, text], i) =>
        `<option value="${i}">${esc(title)}</option>`).join('');
    sel.addEventListener('change', () => {
      const e = DATA.examples[sel.value];
      if (!e) return;
      $('input').value = e[2];
      state.src = e[1] === 'to-mini' ? 'en' : 'mini';
      state.dst = state.src === 'en' ? 'mini' : 'en';
      $('src').value = state.src; $('dst').value = state.dst;
      translate();
    });
  }

  // ---------- 啟動 ----------
  function init() {
    $('src').value = state.src; $('dst').value = state.dst;
    $('src').addEventListener('change', () => { state.src = $('src').value; if (state.src === state.dst) state.dst = state.src === 'en' ? 'mini' : 'en'; $('dst').value = state.dst; translate(); });
    $('dst').addEventListener('change', () => { state.dst = $('dst').value; if (state.src === state.dst) state.src = state.dst === 'en' ? 'mini' : 'en'; $('src').value = state.src; translate(); });
    $('swap').addEventListener('click', () => {
      const text = plainText(state.src === 'en' ? ME.toMini($('input').value) : ME.toEnglish($('input').value));
      const s = state.src; state.src = state.dst; state.dst = s;
      $('src').value = state.src; $('dst').value = state.dst;
      $('input').value = text;
      translate();
    });
    $('input').addEventListener('input', translate);
    $('check').addEventListener('click', runCheck);
    $('copy').addEventListener('click', () => {
      const text = $('output').innerText;
      navigator.clipboard.writeText(text).then(() => { $('copy').textContent = '已複製'; setTimeout(() => { $('copy').textContent = '複製'; }, 1200); });
    });
    $('q').addEventListener('input', renderWords);
    $('coreonly').addEventListener('change', renderWords);
    fillExampleSelect();
    renderWords();
    renderRules();
    renderExamples();
    translate();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
