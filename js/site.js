/* Whiteboard site: language choice, light/dark theme, and the tutorials.
   The pages themselves are built by tools/build.py, one per language. */
(function () {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} },
  };
  const lang = document.documentElement.lang;

  /* ---- Language: each language is its own page (so search engines can read them all) ----
     The first visit to an English page goes to the version in the browser's language, when there
     is one; a language picked in the menu is remembered and always wins. */
  const links = {};                                 // language -> this page in that language (relative link)
  document.querySelectorAll('#lang-list a[data-lang]').forEach((a) => { links[a.dataset.lang] = a.href; });
  const chosen = store.get('site.lang');
  const wanted = (() => {
    if (chosen && links[chosen]) return chosen;
    for (const l of navigator.languages || [navigator.language || 'en']) {
      const code = String(l).toLowerCase().split('-')[0];
      if (links[code]) return code;
    }
    return 'en';
  })();
  if (wanted !== lang && (chosen || lang === 'en')) { location.replace(links[wanted] + location.hash); return; }

  const list = $('#lang-list'), btn = $('#lang-btn');
  list.addEventListener('click', (e) => { const a = e.target.closest('a[data-lang]'); if (a) store.set('site.lang', a.dataset.lang); });
  const closeLang = () => { list.hidden = true; btn.setAttribute('aria-expanded', 'false'); };
  btn.addEventListener('click', () => {
    const open = list.hidden;
    list.hidden = !open; btn.setAttribute('aria-expanded', String(open));
    if (open) (list.querySelector('[aria-current="true"]') || list.querySelector('a')).focus();
  });
  list.addEventListener('keydown', (e) => {
    const items = [...list.querySelectorAll('a')], i = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
    else if (e.key === 'Escape') { closeLang(); btn.focus(); }
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.lang')) closeLang(); });

  /* ---- Theme: follows the system until the switch is used; the switch shows what is in effect ---- */
  const sys = matchMedia('(prefers-color-scheme: dark)');
  const sw = $('#theme-switch');
  const isDark = () => (document.documentElement.dataset.theme ? document.documentElement.dataset.theme === 'dark' : sys.matches);
  // Screenshots come in a light and a dark version (img[data-shot] and the tutorial picture).
  function syncTheme() {
    sw.setAttribute('aria-checked', String(isDark()));
    const v = isDark() ? 'dark' : 'light';
    document.querySelectorAll('img[data-shot]').forEach((i) => { i.src = i.src.replace(/[^/]*$/, `${i.dataset.shot}-${v}.webp`); });
    if (tut) renderShot();
  }
  sw.addEventListener('click', () => {
    const next = isDark() ? 'light' : 'dark';
    // Back to following the system when the choice matches it again.
    if ((next === 'dark') === sys.matches) { delete document.documentElement.dataset.theme; store.set('site.theme', null); }
    else { document.documentElement.dataset.theme = next; store.set('site.theme', next); }
    syncTheme();
  });
  sys.addEventListener('change', syncTheme);

  /* ---- Tutorials (the tutorials page): a tab per topic, numbered steps, a screenshot for each ---- */
  const dataEl = $('#tut-data');
  const tut = dataEl ? JSON.parse(dataEl.textContent).tutorials : null;
  let cur = 0, step = 0;
  const tabs = $('#tut-tabs'), steps = $('#tut-steps'), img = $('#tut-img');
  function renderTutorial() {
    [...tabs.children].forEach((b, i) => { b.setAttribute('aria-selected', String(i === cur)); b.tabIndex = i === cur ? 0 : -1; });
    $('#tut-panel').setAttribute('aria-labelledby', 'tab-' + cur);
    // On phones the tabs scroll sideways: keep the chosen one in view (without scrolling the page).
    const sel = tabs.children[cur];
    if (sel && tabs.scrollWidth > tabs.clientWidth) {
      const l = sel.offsetLeft - tabs.offsetLeft, r = l + sel.offsetWidth;
      if (l < tabs.scrollLeft || r > tabs.scrollLeft + tabs.clientWidth) tabs.scrollLeft = l - 16;
    }
    steps.textContent = '';
    tut[cur].steps.forEach((s, i) => {
      const li = document.createElement('li'), b = document.createElement('button');
      if (i === step) b.setAttribute('aria-current', 'step');
      b.innerHTML = '<span class="num"></span><b></b><span class="t"></span>';
      b.children[0].textContent = i + 1; b.children[1].textContent = s.t; b.children[2].textContent = s.p;
      b.addEventListener('click', () => { step = i; renderTutorial(); });
      li.appendChild(b); steps.appendChild(li);
    });
    renderShot();
  }
  function renderShot() {
    const s = tut[cur].steps[step], v = isDark() ? 'dark' : 'light';
    const src = img.src.replace(/[^/]*$/, `${s.shot}-${v}.webp`);
    if (img.src !== src) { img.classList.add('loading'); img.onload = () => img.classList.remove('loading'); img.src = src; }
    img.alt = s.t + ': ' + s.p;
    $('#tut-prev').disabled = step === 0;
    $('#tut-next').disabled = step === tut[cur].steps.length - 1;
    for (const o of tut[cur].steps) if (o !== s) { const p = new Image(); p.src = img.src.replace(/[^/]*$/, `${o.shot}-${v}.webp`); }
  }
  function openTopic(key) {
    const i = tut.findIndex((t) => t.key === key);
    if (i >= 0) { cur = i; step = 0; renderTutorial(); }
  }
  if (tut) {
    [...tabs.children].forEach((b, i) => b.addEventListener('click', () => {
      cur = i; step = 0; renderTutorial();
      history.replaceState(null, '', '#' + tut[i].key);
    }));
    $('#tut-prev').addEventListener('click', () => { if (step > 0) { step--; renderTutorial(); } });
    $('#tut-next').addEventListener('click', () => { if (step < tut[cur].steps.length - 1) { step++; renderTutorial(); } });
    tabs.addEventListener('keydown', (e) => {
      const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!d) return;
      const dir = document.documentElement.dir === 'rtl' ? -d : d;
      cur = (cur + dir + tut.length) % tut.length; step = 0;
      renderTutorial(); tabs.children[cur].focus();
    });
    // A link to a topic (from the features page or the home page) opens that tab.
    window.addEventListener('hashchange', () => openTopic(location.hash.slice(1)));
    if (location.hash) openTopic(location.hash.slice(1)); else renderTutorial();
  }
  syncTheme();
})();
