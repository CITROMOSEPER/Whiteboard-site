/* Whiteboard landing site: language, light/dark theme, and the tutorials. */
(function () {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const S = window.SITE;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} },
  };

  /* ---- Language: the visitor's choice, else the best match for the browser's languages ---- */
  let lang = 'en';
  const detect = () => {
    for (const l of navigator.languages || [navigator.language || 'en']) {
      const code = String(l).toLowerCase().split('-')[0];
      if (S.text[code]) return code;
    }
    return 'en';
  };
  const t = (k) => (S.text[lang] && S.text[lang][k]) || S.text.en[k] || k;
  function applyLang(code) {
    lang = S.text[code] ? code : 'en';
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-label]').forEach((el) => { el.setAttribute('aria-label', t(el.dataset.i18nLabel)); });
    document.querySelectorAll('[data-i18n-title]').forEach((el) => { el.title = t(el.dataset.i18nTitle); });
    document.title = t('pageTitle');
    const meta = document.querySelector('meta[name="description"]'); if (meta) meta.content = t('pageDesc');
    $('#lang-name').textContent = S.langs.find((l) => l[0] === lang)[1];
    document.querySelectorAll('#lang-list button').forEach((b) => b.setAttribute('aria-current', String(b.dataset.lang === lang)));
    renderTutorial();
  }
  // The menu: every language in its own name, with the English name beside it.
  const list = $('#lang-list'), btn = $('#lang-btn');
  for (const [code, own, en] of S.langs) {
    const li = document.createElement('li'), b = document.createElement('button');
    b.dataset.lang = code; b.setAttribute('role', 'option'); b.lang = code;
    b.innerHTML = `<span></span><small></small>`;
    b.firstChild.textContent = own; b.lastChild.textContent = code === 'en' ? '' : en;
    b.addEventListener('click', () => { store.set('site.lang', code); applyLang(code); closeLang(); btn.focus(); });
    li.appendChild(b); list.appendChild(li);
  }
  const closeLang = () => { list.hidden = true; btn.setAttribute('aria-expanded', 'false'); };
  btn.addEventListener('click', () => {
    const open = list.hidden;
    list.hidden = !open; btn.setAttribute('aria-expanded', String(open));
    if (open) { const cur = list.querySelector('[aria-current="true"]') || list.querySelector('button'); cur.focus(); }
  });
  list.addEventListener('keydown', (e) => {
    const items = [...list.querySelectorAll('button')], i = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
    else if (e.key === 'Escape') { closeLang(); btn.focus(); }
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.lang')) closeLang(); });

  /* ---- Theme: follows the system until the switch is used; the switch shows what is in effect ---- */
  const sys = matchMedia('(prefers-color-scheme: dark)');
  const sw = $('#theme-switch');
  const isDark = () => (document.documentElement.dataset.theme ? document.documentElement.dataset.theme === 'dark' : sys.matches);
  function syncTheme() {
    sw.setAttribute('aria-checked', String(isDark()));
    renderShot();
  }
  sw.addEventListener('click', () => {
    const next = isDark() ? 'light' : 'dark';
    // Back to following the system when the choice matches it again.
    if ((next === 'dark') === sys.matches) { delete document.documentElement.dataset.theme; store.set('site.theme', null); }
    else { document.documentElement.dataset.theme = next; store.set('site.theme', next); }
    syncTheme();
  });
  sys.addEventListener('change', syncTheme);

  /* ---- Tutorials: a tab per tutorial, numbered steps, a screenshot for each (light or dark) ---- */
  let tut = 0, step = 0;
  const tabs = $('#tut-tabs'), steps = $('#tut-steps'), img = $('#tut-img');
  function renderTutorial() {
    tabs.textContent = '';
    S.tutorials.forEach((tu, i) => {
      const b = document.createElement('button');
      b.setAttribute('role', 'tab'); b.id = 'tab-' + i;
      b.setAttribute('aria-selected', String(i === tut)); b.setAttribute('aria-controls', 'tut-panel');
      b.tabIndex = i === tut ? 0 : -1;
      b.textContent = t(tu.key);
      b.addEventListener('click', () => { tut = i; step = 0; renderTutorial(); });
      tabs.appendChild(b);
    });
    $('#tut-panel').setAttribute('aria-labelledby', 'tab-' + tut);
    // On phones the tabs scroll sideways: keep the chosen one in view (without scrolling the page).
    const sel = tabs.children[tut];
    if (sel && tabs.scrollWidth > tabs.clientWidth) {
      const l = sel.offsetLeft - tabs.offsetLeft, r = l + sel.offsetWidth;
      if (l < tabs.scrollLeft || r > tabs.scrollLeft + tabs.clientWidth) tabs.scrollLeft = l - 16;
    }
    steps.textContent = '';
    S.tutorials[tut].steps.forEach((s, i) => {
      const li = document.createElement('li'), b = document.createElement('button');
      if (i === step) b.setAttribute('aria-current', 'step');
      b.innerHTML = '<span class="num"></span><b></b><span class="t"></span>';
      b.children[0].textContent = i + 1;
      b.children[1].textContent = t(s.key + 'T');
      b.children[2].textContent = t(s.key + 'P');
      b.addEventListener('click', () => { step = i; renderTutorial(); });
      li.appendChild(b); steps.appendChild(li);
    });
    renderShot();
  }
  function renderShot() {
    const s = S.tutorials[tut].steps[step], src = `img/shots/${s.shot}-${isDark() ? 'dark' : 'light'}.webp`;
    if (!img.src.endsWith(src)) {
      img.classList.add('loading');
      img.onload = () => img.classList.remove('loading');
      img.src = src;
    }
    img.alt = t(s.key + 'T') + ': ' + t(s.key + 'P');
    $('#tut-prev').disabled = step === 0;
    $('#tut-next').disabled = step === S.tutorials[tut].steps.length - 1;
    // Fetch the other steps' pictures in the background, so stepping through is instant.
    for (const o of S.tutorials[tut].steps) if (o !== s) { const p = new Image(); p.src = `img/shots/${o.shot}-${isDark() ? 'dark' : 'light'}.webp`; }
  }
  $('#tut-prev').addEventListener('click', () => { if (step > 0) { step--; renderTutorial(); } });
  $('#tut-next').addEventListener('click', () => { if (step < S.tutorials[tut].steps.length - 1) { step++; renderTutorial(); } });
  tabs.addEventListener('keydown', (e) => {
    const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
    if (!d) return;
    const dir = document.documentElement.dir === 'rtl' ? -d : d;
    tut = (tut + dir + S.tutorials.length) % S.tutorials.length; step = 0;
    renderTutorial(); tabs.children[tut].focus();
  });

  applyLang(store.get('site.lang') || detect());
  syncTheme();
})();
