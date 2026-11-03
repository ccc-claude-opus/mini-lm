// Mini-Lang 翻譯器的介面。翻譯邏輯在 minilang.js。
(function () {
  'use strict';
  const ML = MiniLang.create(DATA);
  const $ = (id) => document.getElementById(id);
  const HAN = /[一-鿿]/;

  const state = { dir: 'to-mini', pinyin: false, text: '' };
  try {
    Object.assign(state, JSON.parse(localStorage.getItem('minilang') || '{}'));
  } catch (e) { /* 沒有儲存空間也能用 */ }
  const save = () => {
    try { localStorage.setItem('minilang', JSON.stringify(state)); } catch (e) { /* 忽略 */ }
  };

  // ---------- 畫出結果：tokens → HTML，需要時加上拼音 ----------
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function render(tokens, withPinyin) {
    const full = tokens.map((t) => t.text).join('');
    const py = withPinyin ? ML.readings(full) : null;
    let pos = 0;
    return tokens.map((t) => {
      const chars = [...t.text];
      const body = chars.map((c, k) => {
        const r = py && py[pos + k];
        return r && HAN.test(c) ? `<ruby>${esc(c)}<rt>${ML.toneMark(r)}</rt></ruby>` : esc(c);
      }).join('');
      pos += chars.length;
      if (t.type === 'plain') return body;
      const tip = [t.from ? `原文：${t.from}` : '', t.info || ''].filter(Boolean).join('\n');
      return `<span class="${t.type}" title="${esc(tip)}">${body}</span>`;
    }).join('');
  }

  // ---------- 翻譯並更新畫面 ----------
  function update() {
    const toMini = state.dir === 'to-mini';
    const text = state.text;
    $('dir-to-mini').classList.toggle('on', toMini);
    $('dir-to-zh').classList.toggle('on', !toMini);
    $('in-label').textContent = toMini ? '一般中文' : 'Mini-Lang';
    $('out-label').textContent = toMini ? 'Mini-Lang' : '一般中文';
    $('input').placeholder = toMini ? '在這裡輸入或貼上一般中文的文章' : '在這裡輸入或貼上 Mini-Lang 的文章';
    $('in-count').textContent = text ? `${[...text].filter((c) => HAN.test(c)).length} 字` : '';
    $('pinyin').checked = state.pinyin;

    const tokens = toMini ? ML.toMini(text) : ML.toZh(text);
    const out = $('output');
    out.innerHTML = render(tokens, toMini && state.pinyin);
    out.classList.toggle('pinyin', toMini && state.pinyin);

    // Mini-Lang → 中文時，拼音標在輸入的 Mini-Lang 上
    const showPreview = !toMini && state.pinyin && text.trim() !== '';
    $('preview-wrap').hidden = !showPreview;
    if (showPreview) {
      const unknown = new Set(ML.unknownChars(text));
      const parts = [...text].map((c) => unknown.has(c)
        ? { type: 'bad', text: c, info: '字表外的字' } : { type: 'plain', text: c });
      $('preview').innerHTML = render(parts, true);
      $('preview').classList.add('pinyin');
    }

    // 統計與注意事項
    const count = (type) => tokens.filter((t) => t.type === type).length;
    const stats = [];
    const notes = [];
    if (!text.trim()) {
      $('stats').innerHTML = '';
      $('notes').innerHTML = '';
      return;
    }
    if (toMini) {
      const result = tokens.map((t) => t.text).join('');
      const left = ML.unknownChars(result);
      stats.push(`詞典換了 <b>${count('sub') + count('alt')}</b> 個詞`);
      stats.push(left.length ? `還有 <b>${left.length}</b> 個字表外的字要改寫`
        : '<span class="ok">✓ 全部只用字表內的字</span>');
      for (const t of tokens) {
        if (t.type === 'hint') notes.push(`「${t.text}」${t.info}`);
        if (t.type === 'alt') notes.push(`「${t.from}」換成「${t.text}」，${t.info}`);
      }
      const bad = [...new Set(tokens.filter((t) => t.type === 'bad').map((t) => t.text))];
      if (bad.length) notes.push(`這些字詞典沒有，要換個說法：${bad.join('、')}`);
    } else {
      const unknown = ML.unknownChars(text);
      stats.push(`還原了 <b>${count('sub')}</b> 個詞`);
      stats.push(unknown.length ? `輸入有 <b>${unknown.length}</b> 個字表外的字：${unknown.join('')}`
        : '<span class="ok">✓ 輸入只用字表內的字</span>');
      notes.push('還原只查詞典：量詞（一個大衣 → 一件大衣）和語氣要自己改。');
    }
    $('stats').innerHTML = stats.join('　·　');
    $('notes').innerHTML = [...new Set(notes)].map((n) => `<li>${esc(n)}</li>`).join('');
  }

  // ---------- 事件 ----------
  let timer;
  $('input').addEventListener('input', (e) => {
    state.text = e.target.value;
    clearTimeout(timer);
    timer = setTimeout(() => { update(); save(); }, 120);
  });
  for (const id of ['dir-to-mini', 'dir-to-zh']) {
    $(id).addEventListener('click', (e) => { state.dir = e.target.dataset.dir; update(); save(); });
  }
  $('swap').addEventListener('click', () => {
    state.text = $('output').textContent;
    state.dir = state.dir === 'to-mini' ? 'to-zh' : 'to-mini';
    $('input').value = state.text;
    update(); save();
  });
  $('pinyin').addEventListener('change', (e) => { state.pinyin = e.target.checked; update(); save(); });
  $('copy').addEventListener('click', async () => {
    // 複製純文字（不含拼音）
    const clone = $('output').cloneNode(true);
    clone.querySelectorAll('rt').forEach((rt) => rt.remove());
    try {
      await navigator.clipboard.writeText(clone.textContent);
      $('copy').textContent = '已複製';
      setTimeout(() => { $('copy').textContent = '複製'; }, 1200);
    } catch (e) {
      $('copy').textContent = '無法複製';
    }
  });

  const sel = $('examples');
  DATA.examples.forEach((ex, i) => {
    const o = document.createElement('option');
    o.value = i;
    o.textContent = `${ex.dir === 'to-mini' ? '中文' : 'Mini-Lang'}：${ex.title}`;
    sel.appendChild(o);
  });
  sel.addEventListener('change', () => {
    const ex = DATA.examples[sel.value];
    if (!ex) return;
    state.text = ex.text;
    state.dir = ex.dir;
    $('input').value = ex.text;
    sel.value = '';
    update(); save();
  });

  // ---------- 字表 ----------
  $('charset').innerHTML = DATA.groups.map(([name, chars]) => {
    const body = [...chars].map((c) => `<ruby>${c}<rt>${ML.toneMark(DATA.pinyin[c])}</rt></ruby>`).join('');
    return `<div class="group"><h3>${esc(name)}（${[...chars].length}）</h3><div class="chars">${body}</div></div>`;
  }).join('');

  if (!state.text) state.text = DATA.examples[0] ? DATA.examples[0].text : '';
  $('input').value = state.text;
  update();
})();
