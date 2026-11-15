"""More tutorial scenes (imported by shots.py). Each is the body of an async function run in the app,
with the helpers from shots.js as H; SKETCH is the shared board drawing."""


def scenes(SKETCH):
    return {
        # ---- Pen and colours
        'pen-dash': SKETCH + r'''
  H.stroke([[470, 470], [700, 470]], { color: '#007aff', width: 5, smooth: false, dash: 'dashed' });
  H.stroke([[470, 510], [700, 510]], { color: '#ff3b30', width: 5, smooth: false, dash: 'dotted' });
  H.redraw();
  H.$('#btn-dash').click(); await H.sleep(350);
  H.ring('#dash-menu', 8, 18);
  const r = H.rect('#dash-menu');
  H.arrow([r.x + r.w + 170, r.y + r.h + 50], '#dash-menu', 0.25);
''',
        'pen-mixer': SKETCH + r'''
  H.$('#btn-custom').click(); await H.sleep(450);
  H.ring('#picker', 8, 19);
  const r = H.rect('#picker');
  H.arrow([r.x - 170, r.y + 60], '#picker', -0.25);
''',
        'pen-pressure': r'''
  const press = (n) => Array.from({ length: n }, (_, i) => Math.sin((i / (n - 1)) * Math.PI) * 0.95 + 0.05);
  for (let k = 0; k < 3; k++) {
    const pts = []; for (let i = 0; i <= 40; i++) pts.push([120 + i * 18, 190 + k * 110 + Math.sin(i / 4) * 30]);
    H.stroke(pts, { width: 18, color: ['#111111', '#007aff', '#ff3b30'][k] === '#111111' ? H.ink() : ['#111111', '#007aff', '#ff3b30'][k] });
    H.A().doc.strokes[H.A().doc.strokes.length - 1].press = press(41);
  }
  H.redraw();
  await H.menu('settings'); await H.sleep(300);
  const row = H.$('#lbl-pressure').closest('.row'); row.scrollIntoView({ block: 'center' }); await H.sleep(300);
  H.ring(row, 6, 20);
  const r = H.rect(row);
  H.arrow([r.x - 150, r.y - 90], row, 0.25);
''',
        # ---- Highlighter, eraser, laser
        'hl-highlight': r'''
  H.text(140, 120, 'Photosynthesis', { size: 50 });
  H.text(150, 210, 'light + water + CO₂', { size: 34 });
  H.text(150, 270, '→ sugar + oxygen', { size: 34 });
  H.text(150, 330, 'happens in the leaves', { size: 34 });
  H.redraw(); await H.sleep(100);
  const z = H.A().view.zoom;
  H.A().doc.strokes.unshift({ tool: 'pen', hl: true, color: '#ffee00', width: 34, opacity: 0.5, smooth: false, closed: false, points: [140, 236, 450, 236] });
  H.A().doc.strokes.unshift({ tool: 'pen', hl: true, color: '#2bff88', width: 34, opacity: 0.5, smooth: false, closed: false, points: [140, 296, 420, 296] });
  H.redraw();
  H.$('.tool[data-tool="highlighter"]').click(); await H.sleep(300);
  H.ring('.tool[data-tool="highlighter"]', 9, 21);
  H.ring('#swatches', 8, 22);
  const p = H.centre('.tool[data-tool="highlighter"]');
  H.arrow([p[0] - 130, p[1] - 170], '.tool[data-tool="highlighter"]', 0.2);
''',
        'hl-eraser': SKETCH + r'''
  H.A().doc.strokes.push({ tool: 'eraser', width: 34, opacity: 1, smooth: true, closed: false, points: [590, 160, 640, 220, 700, 250, 780, 260] });
  H.redraw();
  H.$('.tool[data-tool="eraser"]').click(); await H.sleep(300);
  H.ring('.tool[data-tool="eraser"]', 9, 23);
  H.ring('#sl-size', 8, 24);
  const p = H.centre('.tool[data-tool="eraser"]');
  H.arrow([p[0] + 150, p[1] - 160], '.tool[data-tool="eraser"]', -0.25);
''',
        'hl-laser': SKETCH + r'''
  H.$('.tool[data-tool="laser"]').click(); await H.sleep(200);
  let t = 0;
  window.__laser = setInterval(() => {
    t += 0.09;
    const x = 520 + Math.cos(t) * 150, y = 330 + Math.sin(2 * t) * 70;
    H.$('#canvas').dispatchEvent(new PointerEvent('pointermove', { bubbles: true, clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse', buttons: 0, isPrimary: true }));
  }, 16);
  await H.sleep(900);
  H.ring('.tool[data-tool="laser"]', 9, 25);
  const p = H.centre('.tool[data-tool="laser"]');
  H.arrow([p[0] + 160, p[1] - 150], '.tool[data-tool="laser"]', -0.25);
''',
        # ---- Shapes: recolour
        'shapes-recolour': r'''
  H.stroke([[160, 260], [380, 200], [600, 280], [820, 210]], { color: '#007aff', width: 8, dash: 'dashed' });
  H.text(170, 120, 'Route', { size: 46 });
  H.redraw(); await H.sleep(200);
  const sw = document.querySelectorAll('#swatches .swatch')[2];
  const b = H.$('#drop-blob'); b.style.setProperty('--c', sw.dataset.color);
  b.style.transform = 'translate3d(600px, 278px, 0)'; b.classList.add('on'); await H.sleep(350);
  H.ring(sw, 9, 26);
  const s = H.centre(sw);
  H.arrow([s[0] + 20, s[1] - 26], [596, 306], -0.3);
''',
        # ---- Selecting
        'sel-lasso': SKETCH + r'''
  H.$('.tool[data-tool="select"]').click(); await H.sleep(150);
  const pts = []; for (let i = 0; i <= 40; i++) { const a = (i / 40) * Math.PI * 1.9 + 0.3; pts.push([290 + Math.cos(a) * 225, 200 + Math.sin(a) * 140]); }
  H.pointer('pointerdown', pts[0][0], pts[0][1]);
  for (const [x, y] of pts.slice(1)) { await H.sleep(8); H.pointer('pointermove', x, y); }
  await H.sleep(200);
  H.ring('.tool[data-tool="select"]', 9, 27);
  const p = H.centre('.tool[data-tool="select"]');
  H.arrow([p[0] + 170, p[1] - 160], '.tool[data-tool="select"]', -0.25);
''',
        'sel-handles': r'''
  H.circle(470, 290, 110, { color: '#ff9500', width: 7 });
  H.redraw(); await H.sleep(150);
  H.$('.tool[data-tool="select"]').click(); await H.sleep(100);
  await H.tap(580, 290); await H.sleep(500);
  const b = WB.boundsOf([...H.A().selection][0]), v = H.A().view, z = v.zoom;
  const x0 = v.x + b.x0 * z, y0 = v.y + b.y0 * z, x1 = v.x + b.x1 * z, y1 = v.y + b.y1 * z;
  H.ring([(x0 + x1) / 2 - 14, y0 - 54, 28, 28], 10, 28);
  H.ring([x1 - 6, y1 - 6, 20, 20], 10, 29);
  H.arrow([x1 + 170, y0 - 40], [(x0 + x1) / 2 + 30, y0 - 42], 0.2);
''',
        'sel-bar': SKETCH + r'''
  H.$('.tool[data-tool="select"]').click(); await H.sleep(100);
  await H.tap(788, 210); await H.sleep(500);
  H.ring('#sel-bar', 8, 30);
  const r = H.rect('#sel-bar');
  H.arrow([r.x + r.w + 120, r.y + r.h + 120], '#sel-bar', -0.25);
''',
        # ---- Scratch out and undo
        'scratch-out': r'''
  H.text(160, 130, 'Shopping list', { size: 46 });
  H.text(170, 220, '• bread', { size: 34 });
  H.text(170, 280, '• milk', { size: 34 });
  H.text(170, 340, '• tomatos', { size: 34 });
  const z = []; for (let i = 0; i <= 14; i++) z.push([182 + i * 12, 360 + (i % 2 ? -26 : 22)]);
  H.stroke(z, { color: '#ff3b30', width: 4, smooth: false });
  H.redraw(); H.toast('Scratched out', 'Undo'); await H.sleep(300);
  H.ring([175, 325, 175, 70], 8, 31);
  H.ring('#toast', 8, 32);
  const r = H.rect('#toast');
  H.arrow([r.x + r.w + 150, r.y - 120], '#toast', -0.25);
''',
        'undo': SKETCH + r'''
  H.pointer('pointerdown', 470, 520); for (let i = 1; i < 8; i++) { await H.sleep(10); H.pointer('pointermove', 470 + i * 25, 520 + Math.sin(i) * 10); } H.pointer('pointerup', 645, 520);
  await H.sleep(400);
  H.ring('#btn-undo', 6, 33); H.ring('#btn-redo', 6, 34);
  const r = H.rect('#btn-undo');
  H.arrow([r.x - 170, r.y + 140], '#btn-undo', 0.25);
''',
        # ---- Text and handwriting
        'text-type': SKETCH + r'''
  H.$('.tool[data-tool="text"]').click(); await H.sleep(150);
  await H.tap(470, 470); await H.sleep(300);
  const ta = H.$('#text-edit'); ta.value = 'Meeting at 3 pm'; ta.dispatchEvent(new Event('input', { bubbles: true })); await H.sleep(300);
  H.ring('#text-bar', 8, 35);
  const r = H.rect('#text-bar');
  H.arrow([r.x + r.w + 150, r.y - 80], '#text-bar', -0.25);
''',
        'text-ink': SKETCH + r'''
  await H.menu('settings'); await H.sleep(300);
  const row = H.$('#lbl-ink').closest('.row'); row.scrollIntoView({ block: 'center' }); await H.sleep(300);
  H.ring(row, 6, 36);
  const r = H.rect(row);
  H.arrow([r.x - 150, r.y + r.h + 100], row, -0.25);
''',
        # ---- Pictures and stickers
        'pic-import': SKETCH + r'''
  await H.menu();
  H.ring('[data-act="import"]', 6, 37);
  const r = H.rect('[data-act="import"]');
  H.arrow([r.x + r.w + 190, r.y + 40], '[data-act="import"]', 0.25);
''',
        'pic-edit': r'''
  const cv = document.createElement('canvas'); cv.width = 840; cv.height = 560; const g = cv.getContext('2d');
  let gr = g.createLinearGradient(0, 0, 0, 560); gr.addColorStop(0, '#7ec8ff'); gr.addColorStop(1, '#d8f0ff'); g.fillStyle = gr; g.fillRect(0, 0, 840, 560);
  g.fillStyle = '#ffd34d'; g.beginPath(); g.arc(640, 150, 70, 0, 7); g.fill();
  g.fillStyle = '#5fbf5f'; g.beginPath(); g.moveTo(0, 420); g.quadraticCurveTo(220, 300, 460, 410); g.quadraticCurveTo(650, 330, 840, 400); g.lineTo(840, 560); g.lineTo(0, 560); g.fill();
  g.fillStyle = '#3c9a46'; g.beginPath(); g.moveTo(0, 480); g.quadraticCurveTo(300, 400, 840, 500); g.lineTo(840, 560); g.lineTo(0, 560); g.fill();
  const src = cv.toDataURL('image/jpeg', 0.9);
  H.A().doc.strokes.push({ tool: 'image', x: 280, y: 150, w: 420, h: 280, rot: 0.08, opacity: 1, src, width: 0 });
  await WB.loadImages(H.A().doc.strokes); H.redraw(); await H.sleep(200);
  H.$('.tool[data-tool="select"]').click(); await H.sleep(100);
  await H.tap(490, 290); await H.sleep(500);
  H.ring([260, 100, 460, 370], 16, 38);
  H.arrow([840, 140], [720, 200], 0.2);
''',
        'sticker': SKETCH + r'''
  H.$('.tool[data-tool="select"]').click(); await H.sleep(100);
  await H.tap(788, 210); await H.sleep(500);
  H.ring('#sel-sticker', 6, 39);
  H.ring('#btn-sticker', 8, 40);
  const r = H.rect('#sel-sticker');
  H.arrow([r.x + r.w + 140, r.y + 150], '#sel-sticker', 0.25);
''',
        # ---- PDFs and sheets: pages
        'pdf-pages': r'''
  const A = H.A();
  A.doc.pages = [{ x: 0, y: -896, w: 559.37, h: 793.7 }, { x: 0, y: 0, w: 559.37, h: 793.7 }];
  const z = 0.6; A.view.zoom = z; A.view.x = 512 - 280 * z; A.view.y = 340 + 499 * z; A.invalidate(); await H.sleep(400);
  H.text(...[A.view.x + 40 * A.view.zoom, A.view.y + 40 * A.view.zoom], 'Notes', { size: 60 * A.view.zoom });
  H.redraw(); await H.sleep(400);
  H.ring('#page-add-top', 5, 41); H.ring('#page-del-top', 5, 42);
  const p = H.centre('#page-del-top');
  H.arrow([p[0] + 190, p[1] + 60], '#page-del-top', -0.25);
''',
        # ---- Gallery and files
        'save-file': SKETCH + r'''
  await H.menu();
  H.ring('[data-act="save-to"]', 6, 43);
  H.ring('[data-act="open"]', 6, 44);
  const r = H.rect('[data-act="save-to"]');
  H.arrow([r.x + r.w + 190, r.y + 20], '[data-act="save-to"]', 0.2);
''',
        # ---- Export and share
        'export-pattern': SKETCH + r'''
  await H.menu('export'); await H.sleep(300);
  H.$('#exp-pattern').click(); await H.sleep(200);
  H.ring('#exp-pattern-block', 6, 45);
  const r = H.rect('#exp-pattern-block');
  H.arrow([r.x + r.w + 110, r.y - 80], '#exp-pattern-block', -0.3);
''',
        'open-link': SKETCH + r'''
  await H.menu('open-link'); await H.sleep(400);
  const i = H.$('#open-link-input'); i.value = 'https://citromoseper.github.io/Whiteboard/#b=Y-T1SU0uKS1K…';
  H.ring(i, 6, 46);
  H.ring('#open-link-go', 6, 47);
  const r = H.rect('#open-link-go');
  H.arrow([r.x + r.w + 110, r.y + 110], '#open-link-go', 0.25);
''',
        # ---- Settings
        'set-theme': SKETCH + r'''
  await H.menu('settings'); await H.sleep(300);
  H.ring('[data-seg="theme"]', 6, 48);
  H.ring('[data-seg="canvas"]', 6, 49);
  const r = H.rect('[data-seg="canvas"]');
  H.arrow([r.x - 130, r.y + 150], '[data-seg="canvas"]', -0.25);
''',
        'set-pattern': SKETCH + r'''
  H.$('#board').dataset.grid = 'ruled';
  await H.menu('settings'); await H.sleep(300);
  H.$('[data-seg="grid"] [data-value="ruled"]').click();
  const seg = H.$('[data-seg="grid"]'); seg.scrollIntoView({ block: 'center' }); await H.sleep(300);
  H.ring(seg, 6, 50);
  const r = H.rect(seg);
  H.arrow([r.x - 140, r.y - 110], seg, 0.25);
''',
        'set-lang': SKETCH + r'''
  await H.menu('settings'); await H.sleep(300);
  H.$('#lang-btn').click(); await H.sleep(350);
  H.ring('#lang-menu', 6, 51);
  const r = H.rect('#lang-menu');
  H.arrow([r.x - 150, r.y + 60], '#lang-menu', -0.25);
''',
    }
