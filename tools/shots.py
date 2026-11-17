"""Make the tutorial screenshots: the real Whiteboard app, each scene built with its own objects
and windows, with red circles and arrows drawn over what to tap. Light and dark versions.

  pip install playwright pillow
  python tools/shots.py [APP_URL]          (default: the published app)

Writes img/shots/<scene>-<light|dark>.webp. Uses the Chrome (or Edge) installed on the computer.
"""
import io
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
APP = sys.argv[1] if len(sys.argv) > 1 else 'https://citromoseper.github.io/Whiteboard/'
OUT = ROOT / 'img' / 'shots'
W, H, SCALE = 1024, 640, 1.5

# A sketch to sit on the board behind most scenes.
SKETCH = r'''
  H.text(120, 96, 'Project ideas', { size: 46 });
  H.text(128, 178, '• sketch the layout', { size: 30 });
  H.text(128, 228, '• pick the colours', { size: 30 });
  H.text(128, 278, '• share with the team', { size: 30 });
  H.stroke([[124, 154], [410, 150]], { width: 4, color: '#007aff' });
  H.circle(700, 210, 88, { color: '#007aff', width: 6 });
  H.stroke([[620, 470], [800, 470], [710, 360], [620, 470]], { color: '#ff9500', width: 6, smooth: false, closed: true, shape: 'triangle' });
  H.stroke([[470, 228], [570, 222]], { width: 5, smooth: false, shape: 'line' });
  H.stroke([[552, 208], [572, 222], [553, 238]], { width: 5, smooth: false });
  H.redraw(); await H.sleep(300);
'''

GALLERY = r'''
  await H.menu('gallery'); await H.sleep(500);
  H.byText('#gallery button', 'Keep it in this browser').click(); await H.sleep(900);
  const mk = (title, draw) => {
    const s = []; draw(s);
    return new File([WB.serialize({ title, created: Date.now(), pages: [], strokes: s }, { x: 0, y: 0, zoom: 1 })], title + '.whtbd');
  };
  const pen = (pts, color, w = 5) => ({ tool: 'pen', color, width: w, opacity: 1, smooth: true, closed: false, points: pts.flat() });
  const ring = (cx, cy, r, color) => { const p = []; for (let i = 0; i < 64; i++) { const a = i / 64 * 6.283; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } return Object.assign(pen(p, color, 6), { closed: true }); };
  const files = [
    mk('Biology notes', (s) => { s.push({ tool: 'text', x: 0, y: 0, rot: 0, text: 'Cell structure', font: 'hand', size: 40, color: H.ink(), opacity: 1, width: 0 }); s.push(ring(160, 200, 90, '#34c759'), ring(150, 210, 30, '#af52de')); }),
    mk('Trip plan', (s) => { s.push(pen([[0, 100], [80, 40], [160, 120], [240, 60], [320, 110]], '#007aff', 7)); s.push({ tool: 'text', x: 0, y: 140, rot: 0, text: 'Day 1 → Day 4', font: 'hand', size: 36, color: H.ink(), opacity: 1, width: 0 }); }),
    mk('Logo ideas', (s) => { s.push(ring(100, 100, 70, '#ff9500'), ring(260, 100, 70, '#ff3b30')); s.push(pen([[40, 220], [320, 220]], H.ink(), 6)); }),
    mk('Maths homework', (s) => { s.push({ tool: 'text', x: 0, y: 0, rot: 0, text: '∫ x² dx = x³/3', font: 'hand', size: 44, color: H.ink(), opacity: 1, width: 0 }); s.push(pen([[0, 90], [300, 90]], '#ff3b30', 4)); }),
  ];
  const dt = new DataTransfer(); files.forEach((f) => dt.items.add(f));
  const inp = H.$('#addboards-input'); inp.files = dt.files; inp.dispatchEvent(new Event('change')); await H.sleep(2200);
  H.$('#toast').classList.remove('on');
'''

SCENES = {
    # ---- Getting started
    'start-tools': SKETCH + r'''
  document.querySelectorAll('#swatches .swatch')[2].click(); await H.sleep(150);
  H.ring('.tool[data-tool="pen"]', 9, 1);
  H.ring(document.querySelectorAll('#swatches .swatch')[2], 9, 2);
  const p = H.centre('.tool[data-tool="pen"]');
  H.arrow([p[0] - 110, p[1] - 170], '.tool[data-tool="pen"]', 0.22);
''',
    'start-brush': SKETCH + r'''
  H.ring('#side', 12, 3);
  const r = H.rect('#side');
  H.arrow([r.x + r.w + 190, r.y + r.h - 20], '#side', -0.25);
''',
    'start-move': SKETCH + r'''
  H.$('#btn-zoom').click(); await H.sleep(350);
  H.ring('[data-act="zoom-fit"]', 8, 4);
  const r = H.rect('#zoom-menu');
  H.arrow([r.x + 60, r.y + r.h + 190], '[data-act="zoom-fit"]', 0.25);
''',
    # ---- Shapes and colour
    'shapes-snap': r'''
  H.circle(470, 290, 120, { color: '#007aff', width: 7 });
  H.text(640, 150, 'hold still…', { size: 34, color: '#007aff' });
  H.redraw(); H.toast('Circle'); await H.sleep(300);
  H.ring([350, 170, 240, 240], 14, 5);
  H.arrow([700, 210], [600, 250], 0.2);
''',
    'shapes-fill': r'''
  H.circle(470, 290, 120, { color: '#007aff', width: 7 });
  H.redraw(); await H.sleep(200);
  const sw = document.querySelectorAll('#swatches .swatch')[4];
  const b = H.$('#drop-blob'); b.style.setProperty('--c', sw.dataset.color);
  b.style.transform = 'translate3d(480px, 300px, 0)'; b.classList.add('on'); await H.sleep(350);
  H.ring(sw, 9, 6);
  const s = H.centre(sw);
  H.arrow([s[0] + 10, s[1] - 26], [505, 335], -0.35);
''',
    'shapes-style': r'''
  H.circle(470, 280, 120, { color: '#007aff', width: 7 });
  const pts = []; for (let i = 0; i < 96; i++) { const a = (i / 96) * Math.PI * 2; pts.push(470 + Math.cos(a) * 120, 280 + Math.sin(a) * 120); }
  H.A().doc.strokes.unshift({ tool: 'fill', color: '#ffcc00', opacity: 1, under: true, rings: [pts], width: 0 });
  H.redraw(); await H.sleep(200);
  H.$('.tool[data-tool="select"]').click(); await H.sleep(100);
  await H.tap(590, 280); await H.sleep(500);
  H.ring('#sel-style', 10, 7);
  const r = H.rect('#sel-style');
  H.arrow([r.x + r.w + 140, r.y - 40], '#sel-style', 0.25);
''',
    # ---- PDFs and sheets
    'pdf-menu': SKETCH + r'''
  await H.menu();
  H.ring('[data-act="sheet"]', 6, 8);
  H.ring('[data-act="open"]', 6, 9);
  const r = H.rect('[data-act="open"]');
  H.arrow([r.x + r.w + 190, r.y + 70], '[data-act="open"]', 0.22);
''',
    'pdf-sizes': SKETCH + r'''
  await H.menu('sheet'); await H.sleep(300);
  const a4 = H.byText('.sz-tile b', 'A4').parentElement;
  H.ring(a4, 8, 10);
  const r = H.rect(a4);
  H.arrow([r.x + r.w + 150, r.y - 70], a4, -0.3);
''',
    'pdf-annotate': r'''
  // A lecture slide, as an opened PDF page.
  const cv = document.createElement('canvas'); cv.width = 1600; cv.height = 900; const g = cv.getContext('2d');
  g.fillStyle = '#ffffff'; g.fillRect(0, 0, 1600, 900);
  g.fillStyle = '#1d2a5c'; g.fillRect(0, 0, 1600, 18);
  g.fillStyle = '#1d1d1f'; g.font = '700 74px Georgia, serif'; g.fillText('Lecture 4: Fourier series', 110, 170);
  g.font = '40px Georgia, serif'; g.fillStyle = '#333';
  ['Any periodic signal is a sum of sines', 'Each term has its own frequency', 'More terms, closer fit'].forEach((t, i) => { g.fillText('•  ' + t, 130, 300 + i * 80); });
  g.strokeStyle = '#1a6bff'; g.lineWidth = 6; g.beginPath();
  for (let x = 0; x <= 520; x += 4) { const t = (x / 520) * Math.PI * 4; const y = 640 + 90 * (Math.sin(t) + Math.sin(3 * t) / 3 + Math.sin(5 * t) / 5); x ? g.lineTo(980 + x, y) : g.moveTo(980, y); }
  g.stroke();
  const A = H.A();
  A.doc.pages = [{ x: 0, y: 0, w: 1200, h: 675, src: cv.toDataURL('image/jpeg', 0.9) }];
  A.fitView(true); await H.sleep(400);
  const v = A.view, S = (x, y) => [v.x + x * 0.75 * v.zoom, v.y + y * 0.75 * v.zoom];   // slide pixels to the screen
  // Highlight the title, underline a point, a note in the margin.
  H.A().doc.strokes.push({ tool: 'pen', hl: true, color: '#ffee00', width: 46, opacity: 0.5, smooth: false, closed: false, points: [100, 110, 830, 110] });
  H.stroke([S(130, 520), S(380, 516), S(640, 522)], { color: '#ff3b30', width: 4 });
  H.text(...S(1000, 450), 'square wave!', { size: 30 * v.zoom * 1.3, color: '#ff3b30' });
  H.redraw();
  H.$('.tool[data-tool="highlighter"]').click(); await H.sleep(500);
  H.ring('.tool[data-tool="highlighter"]', 9, 11);
  H.ring('#page-add-top', 7, 12);
  const p = H.centre('#page-add-top');
  H.arrow([p[0] + 200, p[1] + 30], '#page-add-top', -0.25);
''',
    # ---- Saving and sharing
    'save-gallery': SKETCH + GALLERY + r'''
  const tile = document.querySelector('#g-grid > *');
  H.ring(tile, 6, 13);
  const r = H.rect(tile);
  H.arrow([r.x + r.w + 170, r.y + r.h + 40], tile, -0.25);
''',
    'save-backup': SKETCH + GALLERY + r'''
  const links = [...document.querySelectorAll('#g-foot .g-link')].filter((b) => /^(Back up|Restore|Add boards)/.test(b.textContent));
  for (const [k, l] of links.entries()) H.ring(l, 5, 52 + k);
  const r = H.rect(links[0]);
  H.arrow([r.x + 60, r.y - 170], links[0], 0.25);
''',
    'save-export': SKETCH + r'''
  await H.menu('export'); await H.sleep(300);
  H.ring('[data-seg="format"]', 8, 15);
  H.ring('#btn-export', 8, 16);
  const r = H.rect('#btn-export');
  H.arrow([r.x + r.w + 120, r.y - 90], '#btn-export', -0.3);
''',
    'save-share': SKETCH + r'''
  window.WebSocket = function () { return { readyState: 0, send() {}, close() {} }; };
  await H.menu('share'); await H.sleep(900);
  H.$('#live-state').textContent = WB.t('liveWaiting');
  H.$('#live-box').classList.add('alone');
  { const i = H.$('#share-link'); i.value = i.value.replace(location.origin + location.pathname, 'https://citromoseper.github.io/Whiteboard/'); }
  H.ring('#share-copy', 8, 17);
  const r = H.rect('#share-copy');
  H.arrow([r.x - 110, r.y + r.h + 50], [r.x - 6, r.y + r.h / 2 + 6], 0.3);
''',
}


from scenes_more import scenes as _more
SCENES.update(_more(SKETCH))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    helpers = (ROOT / 'tools' / 'shots.js').read_text(encoding='utf-8')
    only = set(sys.argv[2:])
    with sync_playwright() as p:
        browser = None
        for ch in ('chrome', 'msedge', None):
            try:
                browser = p.chromium.launch(channel=ch) if ch else p.chromium.launch()
                break
            except Exception:
                pass
        for theme in ('light', 'dark'):
            for name, body in SCENES.items():
                if only and name not in only:
                    continue
                ctx = browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=SCALE, color_scheme=theme)
                settings = {'theme': theme, 'lang': 'en', 'grid': 'dots', 'canvas': 'theme'}
                ctx.add_init_script(f"try {{ localStorage.setItem('wb.settings', {json.dumps(json.dumps(settings))}); }} catch (e) {{}}")
                page = ctx.new_page()
                page.goto(APP)
                page.wait_for_function('window.WB && WB.app')
                page.wait_for_timeout(1200)
                page.add_script_tag(content=helpers)
                page.evaluate(f'async () => {{ {body} }}')
                page.wait_for_timeout(350)
                png = page.screenshot()
                Image.open(io.BytesIO(png)).convert('RGB').save(OUT / f'{name}-{theme}.webp', 'WEBP', quality=82, method=6)
                print('made', name, theme)
                ctx.close()
        browser.close()


if __name__ == '__main__':
    main()
