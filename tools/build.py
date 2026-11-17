"""Build the site: every page in every language, as plain HTML that search engines can read.

  python tools/build.py

Reads content/strings.json (the site's text in 14 languages), content/strings-pages.json (text of
the separate pages) and content/site.json (languages, tutorials and their screenshots), and writes:

  index.html, features/, tutorials/, support/          English, at the top
  <lang>/index.html, <lang>/features/, ...             the other 13 languages
  sitemap.xml                                          every page, with its language versions

Each page links its other language versions (hreflang), carries a canonical address, a title and
description of its own, and structured data (the app itself on the home page, breadcrumbs on the
others), which is what Google uses to understand the site and may show as sitelinks.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://citromoseper.github.io/Whiteboard-site/'
APP = 'https://citromoseper.github.io/Whiteboard/'
REPO = 'https://github.com/CITROMOSEPER/Whiteboard'

TEXT = json.loads((ROOT / 'content' / 'strings.json').read_text(encoding='utf-8'))
for lang, extra in json.loads((ROOT / 'content' / 'strings-pages.json').read_text(encoding='utf-8')).items():
    TEXT[lang].update(extra)
SITE = json.loads((ROOT / 'content' / 'site.json').read_text(encoding='utf-8'))
LANGS = SITE['langs']                       # [code, own name, English name]
PAGES = ['', 'features/', 'tutorials/', 'support/']

e = lambda s: html.escape(s, quote=True)


def prefix(lang):
    return '' if lang == 'en' else lang + '/'


def url(lang, page):
    return BASE + prefix(lang) + page


def page_html(lang, page, body, title, desc, jsonld):
    T = lambda k: e(TEXT[lang].get(k) or TEXT['en'][k])
    depth = (0 if lang == 'en' else 1) + (1 if page else 0)
    root = '../' * depth                              # to the site's top folder
    here = root + prefix(lang)                        # to this language's home
    rtl = lang == 'ar'
    alternates = ''.join(f'<link rel="alternate" hreflang="{l}" href="{url(l, page)}">\n' for l, _, _ in LANGS)
    alternates += f'<link rel="alternate" hreflang="x-default" href="{url("en", page)}">\n'
    langs = ''.join(
        f'<li><a href="{root + prefix(l) + page}" hreflang="{l}" lang="{l}" data-lang="{l}"'
        f'{" aria-current=\"true\"" if l == lang else ""}><span>{e(own)}</span><small>{"" if l == "en" else e(en)}</small></a></li>'
        for l, own, en in LANGS)
    own_name = next(o for l, o, _ in LANGS if l == lang)
    cur = lambda p: ' aria-current="page"' if p == page else ''
    return f'''<!doctype html>
<html lang="{lang}" dir="{'rtl' if rtl else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#fbfbfa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#161618" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{url(lang, page)}">
{alternates}<meta property="og:type" content="website">
<meta property="og:site_name" content="Whiteboard">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url(lang, page)}">
<meta property="og:image" content="{BASE}img/og.png">
<meta property="og:locale" content="{lang}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}img/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}img/icon-180.png">
<link rel="preload" href="{root}fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}fonts/bricolage-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}css/site.css">
<script>
  // The theme before the first paint, so nothing flashes.
  (function () {{ try {{ var t = localStorage.getItem('site.theme'); if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; }} catch (e) {{}} }})();
</script>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body data-root="{root}">
<a class="skip" href="#main">{T('skip')}</a>

<header class="top">
  <nav class="wrap" aria-label="Main">
    <a class="brand" href="{here}">
      <img src="{root}img/icon.svg" alt="" width="34" height="34">
      <span>Whiteboard</span>
    </a>
    <div class="nav-links">
      <a class="opt" href="{here}features/"{cur('features/')}>{T('navFeatures')}</a>
      <a class="opt" href="{here}tutorials/"{cur('tutorials/')}>{T('navTutorials')}</a>
      <a class="opt" href="{here}support/"{cur('support/')}>{T('navSupport')}</a>
      <a class="opt" href="{REPO}">GitHub</a>
      <div class="tools">
        <div class="lang">
          <button id="lang-btn" aria-haspopup="true" aria-expanded="false" aria-label="{T('language')}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9c-2.6-2.6-3.8-5.6-3.8-9S9.4 5.6 12 3z"/></svg>
            <span id="lang-name">{e(own_name)}</span>
          </button>
          <ul id="lang-list" hidden>{langs}</ul>
        </div>
        <button class="theme-switch" id="theme-switch" role="switch" aria-checked="false" aria-label="{T('darkMode')}" title="{T('darkMode')}">
          <span class="knob">
            <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="#ff9500" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>
            <svg class="moon" viewBox="0 0 24 24" fill="#ffe14d" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>
          </span>
        </button>
      </div>
      <a class="btn-pill" href="{APP}">{T('openApp')}</a>
    </div>
  </nav>
</header>

<main id="main">
{body}
</main>

<footer class="bottom">
  <div class="wrap">
    <div class="who">
      <img src="{root}img/icon.svg" alt="" width="24" height="24">
      <span>Nemes Dániel © 2026-now</span>
    </div>
    <nav class="links" aria-label="Footer">
      <a href="{APP}">{T('openApp')}</a>
      <a href="{here}features/">{T('navFeatures')}</a>
      <a href="{here}tutorials/">{T('navTutorials')}</a>
      <a href="{here}support/">{T('navSupport')}</a>
      <a href="{REPO}">{T('footSource')}</a>
      <a href="{REPO}/blob/main/LICENSE">{T('footLicense')}</a>
      <a href="{REPO}/blob/main/THIRD-PARTY-NOTICES.md">{T('footNotices')}</a>
    </nav>
  </div>
</footer>

<script src="{root}js/site.js"></script>
</body>
</html>
'''


# ---- Page bodies ------------------------------------------------------------------------
ARROW = '<svg class="fwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

CARD_ICONS = [
    '<path class="faint" d="M8 30c4-12 8-18 14-14s4 12 12 4" stroke-width="3" stroke-dasharray="1 6"/><circle cx="26" cy="24" r="14" stroke="#1a6bff" stroke-width="3.5"/>',
    '<rect x="6" y="14" width="26" height="26" rx="4" fill="#ff9500" fill-opacity="0.22" stroke="#ff9500" stroke-width="3.5"/><circle cx="38" cy="10" r="6" fill="#ff9500"/><path class="ink" d="M34 15l-8 9" stroke-width="3"/>',
    '<path class="ink" d="M8 34l6-20 6 20 6-20 6 20 6-20" stroke-width="3.5"/>',
    '<path d="M6 30h36" stroke="#ffe14d" stroke-width="12" stroke-linecap="butt"/><path class="ink" d="M10 32c3-10 6-14 8-10s2 8 6 2 6-8 8-2" stroke-width="3.5"/>',
    '<rect class="ink" x="10" y="6" width="28" height="36" rx="4" stroke-width="3.5"/><path d="M17 17h14M17 24h14M17 31h8" stroke="#1a6bff" stroke-width="3.5"/>',
    '<path class="ink" d="M8 36c4-8 8-22 12-22s2 14 6 14 4-10 8-10" stroke-width="3.5"/><path d="M30 38h12" stroke="#1a6bff" stroke-width="3.5"/>',
    # AI for handwriting: a sparkle over a written x²
    '<path d="M33 5l2.6 6.4L42 14l-6.4 2.6L33 23l-2.6-6.4L24 14l6.4-2.6z" fill="#af52de" fill-opacity="0.22" stroke="#af52de" stroke-width="3"/><path class="ink" d="M7 28l12 13M19 28L7 41" stroke-width="3.5"/><path class="ink" d="M23 26c1-3 6-3 6 0s-6 6-6 7h6" stroke-width="3"/>',
    # The key stays on the device: a closed padlock
    '<rect x="9" y="21" width="30" height="21" rx="5" fill="#34c759" fill-opacity="0.18" stroke="#34c759" stroke-width="3.5"/><path class="ink" d="M16 21v-6a8 8 0 0 1 16 0v6" stroke-width="3.5"/><circle class="ink" cx="24" cy="30" r="3" stroke-width="3"/><path class="ink" d="M24 33v4" stroke-width="3"/>',
    # Drawing together, live: two people's lines and their laser pointers (red and green)
    '<path class="ink" d="M5 40c5-7 9-7 13-2s8 4 11-3" stroke-width="3.5"/><path d="M20 22c4-6 8-6 11-1s6 3 9-4" stroke="#34c759" stroke-width="3.5"/><circle cx="31" cy="35" r="8" fill="#ff3b30" fill-opacity="0.2"/><circle cx="31" cy="35" r="3.5" fill="#ff3b30"/><circle cx="40" cy="17" r="8" fill="#34c759" fill-opacity="0.2"/><circle cx="40" cy="17" r="3.5" fill="#34c759"/>',
]


def cards(T, level='h3'):
    return '<div class="cards">' + ''.join(
        f'<article class="card{" wide" if i == 9 else ""}"><svg viewBox="0 0 48 48" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{icon}</svg>'
        f'<{level} class="display">{T(f"f{i}t")}</{level}><p>{T(f"f{i}p")}</p></article>'
        for i, icon in enumerate(CARD_ICONS, 1)) + '</div>'


def support_box(T, heading='h2'):
    return f'''<div class="support">
        <div class="text">
          <p class="hand">{T('supHand')}</p>
          <{heading} class="display">{T('supTitle')}</{heading}>
          <p class="lead">{T('supLead')}</p>
        </div>
        <div class="actions">
          <span class="soon" aria-disabled="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 10h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M8 3v2M12 3v2"/></svg>
            <span>{T('supCoffee')}</span> <small>{T('supSoon')}</small>
          </span>
          <a class="sponsor" href="https://github.com/sponsors/CITROMOSEPER">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>
            <span>{T('supSponsor')}</span>
          </a>
          <a class="star" href="{REPO}">{T('supStar')}</a>
        </div>
      </div>'''


def home_body(lang, T, here):
    teasers = ''.join(
        f'<a class="teaser" href="{here}tutorials/#{tu["key"]}"><img data-shot="{tu["steps"][0][1]}" src="{{ROOT}}img/shots/{tu["steps"][0][1]}-light.webp" alt="" width="1536" height="960" loading="lazy"><span>{T(tu["key"])}</span></a>'
        for tu in SITE['tutorials'][:3])
    return f'''<section class="hero" id="top">
    <div class="wrap">
      <div class="hero-text">
        <p class="hand">{T('heroHand')}</p>
        <h1 class="display"><span>{T('heroTitleA')}</span> <mark>{T('heroTitleB')}</mark></h1>
        <p class="lead">{T('heroLead')}</p>
        <div class="ctas">
          <a class="btn btn-primary" href="{APP}"><span>{T('ctaStart')}</span> {ARROW}</a>
          <a class="btn btn-ghost" href="{here}tutorials/">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16v11H4z"/><path d="M9 20h6M12 16v4"/><path d="M8 11l3 2 5-5" stroke="#ff3b30"/></svg>
            <span>{T('ctaTour')}</span>
          </a>
        </div>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="board-card">
          <svg class="art" viewBox="0 0 480 360" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M60 210 L196 196" stroke="#ffe14d" stroke-opacity="0.85" stroke-width="22" stroke-linecap="butt"/>
            <path class="ink" d="M62 150 C70 196 80 222 92 222 C106 222 112 176 124 176 C136 176 142 222 156 222 C168 222 178 196 186 150" stroke-width="7"/>
            <circle cx="186" cy="150" r="7" fill="#ff9500"/>
            <circle cx="340" cy="120" r="58" fill="#1a6bff" fill-opacity="0.16" stroke="#1a6bff" stroke-width="6"/>
            <rect x="262" y="210" width="124" height="80" rx="4" fill="#ff9500" fill-opacity="0.18" stroke="#ff9500" stroke-width="6"/>
            <path class="ink" d="M402 236 L444 300 L360 300 Z" stroke-width="6"/>
            <path d="M70 290 C110 270 150 310 200 284" stroke="#1a6bff" stroke-width="6" stroke-dasharray="2 14"/>
          </svg>
          <div class="dock">
            <i class="on" style="background: var(--ink)"></i><i style="background: #1a6bff"></i><i style="background: #ff9500"></i>
            <i style="background: #34c759"></i><i style="background: #ff3b30"></i><i class="sep"></i>
            <i style="background: conic-gradient(#ff3b30, #ff9500, #ffe14d, #34c759, #1a6bff, #af52de, #ff3b30)"></i>
          </div>
        </div>
        <p class="note hand">{T('heroNote')}</p>
      </div>
    </div>
  </section>

  <section class="strip" aria-label="Whiteboard">
    <div class="wrap">
      <span>{T('fact1')}</span><span>{T('fact2')}</span><span>{T('fact3')}</span><span>{T('fact4')}</span><span>{T('fact5')}</span>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="section-head">
        <h2 class="display">{T('featTitle')}</h2>
        <p>{T('featLead')}</p>
      </div>
      {cards(T)}
      <a class="more" href="{here}features/">{T('seeAll')} {ARROW}</a>
    </div>
  </section>

  <section class="block">
    <div class="wrap">
      <div class="section-head">
        <h2 class="display">{T('tutTitle')}</h2>
        <p>{T('tutLead')}</p>
      </div>
      <div class="teasers">{teasers}</div>
      <a class="more" href="{here}tutorials/">{T('openTutorials')} {ARROW}</a>
    </div>
  </section>

  <section class="block last">
    <div class="wrap">{support_box(T)}</div>
  </section>'''


def features_body(lang, T, here):
    topics = ''.join(
        f'''<section class="topic" id="{tu['key']}">
          <h2 class="display">{T(tu['key'])}</h2>
          <ul>{''.join(f"<li><b>{T(k + 'T')}</b><span>{T(k + 'P')}</span></li>" for k, _ in tu['steps'])}</ul>
          <a class="more" href="{here}tutorials/#{tu['key']}">{T('toTutorial')} {ARROW}</a>
        </section>''' for tu in SITE['tutorials'])
    return f'''<section class="block first">
    <div class="wrap">
      <div class="section-head">
        <h1 class="display">{T('allTitle')}</h1>
        <p>{T('allLead')}</p>
      </div>
      {cards(T, 'h2')}
      <div class="topics">{topics}</div>
      <a class="btn btn-primary cta-end" href="{APP}"><span>{T('ctaStart')}</span> {ARROW}</a>
    </div>
  </section>'''


def tutorials_body(lang, T, here):
    data = {
        'tutorials': [{'key': tu['key'], 'name': TEXT[lang].get(tu['key']) or TEXT['en'][tu['key']],
                       'steps': [{'shot': shot, 't': TEXT[lang].get(k + 'T') or TEXT['en'][k + 'T'], 'p': TEXT[lang].get(k + 'P') or TEXT['en'][k + 'P']}
                                 for k, shot in tu['steps']]} for tu in SITE['tutorials']],
    }
    first = data['tutorials'][0]
    # The first tutorial is written into the page too, so it reads without scripts.
    steps = ''.join(f'<li><button{" aria-current=\"step\"" if i == 0 else ""}><span class="num">{i + 1}</span><b>{e(s["t"])}</b><span class="t">{e(s["p"])}</span></button></li>'
                    for i, s in enumerate(first['steps']))
    tabs = ''.join(f'<button role="tab" id="tab-{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{e(tu["name"])}</button>'
                   for i, tu in enumerate(data['tutorials']))
    return f'''<section class="block first" id="tutorials">
    <div class="wrap">
      <div class="tut-head">
        <div class="section-head">
          <h1 class="display">{T('tutTitle')}</h1>
          <p>{T('tutLead')}</p>
        </div>
        <a href="{REPO}#readme">{T('tutGuide')}</a>
      </div>
      <div class="tabs" role="tablist" id="tut-tabs">{tabs}</div>
      <div class="tutorial" role="tabpanel" id="tut-panel" aria-labelledby="tab-0">
        <figure class="shot">
          <img id="tut-img" src="{{ROOT}}img/shots/{first['steps'][0]['shot']}-light.webp" alt="{e(first['steps'][0]['t'])}" width="1536" height="960">
          <button class="nav-btn prev" id="tut-prev" aria-label="{T('prev')}" disabled><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
          <button class="nav-btn next" id="tut-next" aria-label="{T('next')}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
        </figure>
        <ol class="steps" id="tut-steps">{steps}</ol>
      </div>
      <script type="application/json" id="tut-data">{json.dumps(data, ensure_ascii=False).replace('</', '<\\/')}</script>
    </div>
  </section>'''


def support_body(lang, T, here):
    return f'''<section class="block first">
    <div class="wrap">
      {support_box(T, 'h1')}
      <div class="issues">
        <h2 class="display">{T('issuesT')}</h2>
        <p>{T('issuesP')}</p>
        <a class="btn btn-ghost" href="{REPO}/issues/new">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.5v.01"/></svg>
          <span>{T('issuesLink')}</span>
        </a>
      </div>
    </div>
  </section>'''


BODIES = {'': home_body, 'features/': features_body, 'tutorials/': tutorials_body, 'support/': support_body}
NAV_KEY = {'features/': 'navFeatures', 'tutorials/': 'navTutorials', 'support/': 'navSupport'}


def main():
    sitemap = []
    for lang, _, _ in LANGS:
        L = TEXT[lang]
        T = lambda k, L=L: e(L.get(k) or TEXT['en'][k])
        raw = lambda k, L=L: L.get(k) or TEXT['en'][k]
        for page in PAGES:
            depth = (0 if lang == 'en' else 1) + (1 if page else 0)
            root = '../' * depth
            here = root + prefix(lang)
            body = BODIES[page](lang, T, here).replace('{ROOT}', root)
            if page == '':
                title, desc = raw('pageTitle'), raw('pageDesc')
                jsonld = {'@context': 'https://schema.org', '@graph': [
                    {'@type': 'WebSite', 'name': 'Whiteboard', 'url': url(lang, ''), 'inLanguage': lang},
                    {'@type': 'WebApplication', 'name': 'Whiteboard', 'url': APP, 'applicationCategory': 'DesignApplication',
                     'operatingSystem': 'Any (runs in a web browser)', 'browserRequirements': 'A modern web browser',
                     'description': desc, 'image': BASE + 'img/og.png', 'inLanguage': [l for l, _, _ in LANGS],
                     'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
                     'author': {'@type': 'Person', 'name': 'Nemes Dániel', 'url': 'https://github.com/CITROMOSEPER'},
                     'sameAs': [REPO], 'softwareHelp': url(lang, 'tutorials/')},
                ]}
            else:
                name = raw(NAV_KEY[page])
                title = f'{name} – Whiteboard'
                desc = {'features/': raw('allLead'), 'tutorials/': raw('tutLead'), 'support/': raw('supLead')}[page]
                desc = raw('heroLead') + ' ' + desc if page != 'support/' else desc
                jsonld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': raw('home'), 'item': url(lang, '')},
                    {'@type': 'ListItem', 'position': 2, 'name': name, 'item': url(lang, page)}]}
            out = ROOT / prefix(lang) / page / 'index.html'
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page_html(lang, page, body, title, desc, jsonld), encoding='utf-8', newline='\n')
            sitemap.append((lang, page))
    # Sitemap: every page once, each listing all its language versions.
    rows = []
    for lang, page in sitemap:
        alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{url(l, page)}"/>' for l, _, _ in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url("en", page)}"/>'
        rows.append(f'  <url>\n    <loc>{url(lang, page)}</loc>{alts}\n  </url>')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                                      + '\n'.join(rows) + '\n</urlset>\n', encoding='utf-8', newline='\n')
    print(f'{len(sitemap)} pages in {len(LANGS)} languages, and sitemap.xml')


if __name__ == '__main__':
    main()
