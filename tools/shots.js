/* Runs inside the Whiteboard app (see shots.py): builds each tutorial scene with the app's own
   objects and windows, then draws red circles and arrows over what to tap. */
window.H = (() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const $ = (s) => document.querySelector(s);
  const A = () => WB.app;
  const dark = () => document.documentElement.dataset.theme === 'dark';
  const ink = () => (dark() ? '#ffffff' : '#111111');

  function rect(t) {
    if (Array.isArray(t)) return { x: t[0], y: t[1], w: t[2] || 0, h: t[3] || 0 };
    const e = typeof t === 'string' ? $(t) : t;
    const r = e.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  }
  const byText = (sel, text) => [...document.querySelectorAll(sel)].find((e) => e.textContent.trim() === text);

  /* Board objects, in screen coordinates (the view starts at 100 %, at 0, 0). */
  const toWorld = (x, y) => { const v = A().view; return [(x - v.x) / v.zoom, (y - v.y) / v.zoom]; };
  function stroke(pts, o = {}) {
    const p = []; for (const [x, y] of pts) p.push(...toWorld(x, y));
    const z = A().view.zoom;
    A().doc.strokes.push(Object.assign({ tool: 'pen', color: ink(), width: 5 / z, opacity: 1, smooth: true, closed: false, points: p }, o, o.width ? { width: o.width / z } : {}));
  }
  function text(x, y, t, o = {}) {
    const [wx, wy] = toWorld(x, y), z = A().view.zoom;
    A().doc.strokes.push(Object.assign({ tool: 'text', x: wx, y: wy, rot: 0, text: t, font: 'hand', size: (o.size || 30) / z, color: o.color || ink(), opacity: 1, width: 0 }, o.font ? { font: o.font } : {}));
  }
  function circle(cx, cy, r, o = {}) {
    const pts = []; for (let i = 0; i < 96; i++) { const a = (i / 96) * Math.PI * 2; pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r * (o.ry || 1)]); }
    stroke(pts, Object.assign({ closed: true, shape: 'circle' }, o));
  }
  /* A hand-drawn wiggle, like a quick scribble of a word. */
  function scribble(x, y, w, h, o = {}) {
    const pts = [], n = Math.max(8, Math.round(w / 9));
    for (let i = 0; i <= n; i++) pts.push([x + (w * i) / n, y + Math.sin(i * 1.9) * h * 0.5 + (i % 2 ? h * 0.18 : -h * 0.12)]);
    stroke(pts, o);
  }
  const redraw = () => { A().invalidate(); $('#hint').classList.add('gone'); };

  function pointer(type, x, y, o = {}) {
    $('#canvas').dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse', button: type === 'pointermove' ? -1 : 0, buttons: type === 'pointerup' ? 0 : 1, isPrimary: true, ...o }));
  }
  async function tap(x, y) { pointer('pointerdown', x, y); await sleep(20); pointer('pointerup', x, y); await sleep(60); }
  const menu = async (act) => { $('#btn-menu').click(); await sleep(250); if (act) { $(`[data-act="${act}"]`).click(); await sleep(450); } };
  function toast(t, action) { $('#toast-text').textContent = t; const b = $('#toast-action'); b.hidden = !action; b.textContent = action || ''; $('#toast').classList.add('on'); }

  /* ---- Marks ---------------------------------------------------------------- */
  const RED = '#ff3b30';
  let svg = null;
  function layer() {
    if (svg) return svg;
    svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('style', 'position:fixed;inset:0;width:100vw;height:100vh;z-index:9999;pointer-events:none;overflow:visible');
    document.body.appendChild(svg);
    return svg;
  }
  function path(d, w) {
    layer();
    const halo = document.createElementNS(svg.namespaceURI, 'path');
    halo.setAttribute('d', d); halo.setAttribute('fill', 'none'); halo.setAttribute('stroke', dark() ? 'rgba(0,0,0,0.45)' : 'rgba(255,255,255,0.75)');
    halo.setAttribute('stroke-width', w + 4); halo.setAttribute('stroke-linecap', 'round'); halo.setAttribute('stroke-linejoin', 'round');
    const p = document.createElementNS(svg.namespaceURI, 'path');
    p.setAttribute('d', d); p.setAttribute('fill', 'none'); p.setAttribute('stroke', RED);
    p.setAttribute('stroke-width', w); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-linejoin', 'round');
    layer().append(halo, p);
  }
  /* A loose loop around a target, drawn like a marker: a little more than once round, slightly uneven. */
  function ring(t, pad = 10, seed = 1) {
    const r = rect(t), cx = r.x + r.w / 2, cy = r.y + r.h / 2, rx = r.w / 2 + pad, ry = r.h / 2 + pad;
    let d = '', a0 = -2.2 + seed * 0.3;
    for (let i = 0; i <= 64; i++) {
      const a = a0 + (i / 64) * Math.PI * 2.18, k = 1 + 0.045 * Math.sin(a * 3 + seed) + 0.03 * (i / 64);
      d += (i ? 'L' : 'M') + (cx + Math.cos(a) * rx * k).toFixed(1) + ' ' + (cy + Math.sin(a) * ry * k).toFixed(1);
    }
    path(d, 4);
    return { cx, cy, rx: rx * 1.03, ry: ry * 1.03 };
  }
  /* A curved arrow from a point to the edge of a target (or a point). */
  function arrow(from, to, bend = 0.25) {
    let tx, ty;
    if (Array.isArray(to) && to.length === 2) [tx, ty] = to;
    else {
      const r = rect(to), cx = r.x + r.w / 2, cy = r.y + r.h / 2, dx = from[0] - cx, dy = from[1] - cy;
      const rx = r.w / 2 + 18, ry = r.h / 2 + 18, k = 1 / Math.sqrt((dx * dx) / (rx * rx) + (dy * dy) / (ry * ry));
      tx = cx + dx * k; ty = cy + dy * k;
    }
    const [fx, fy] = from, mx = (fx + tx) / 2, my = (fy + ty) / 2, nx = -(ty - fy) * bend, ny = (tx - fx) * bend;
    const qx = mx + nx, qy = my + ny;
    path(`M${fx} ${fy} Q${qx} ${qy} ${tx} ${ty}`, 4.5);
    const ang = Math.atan2(ty - qy, tx - qx), L = 16;
    path(`M${tx - L * Math.cos(ang - 0.45)} ${ty - L * Math.sin(ang - 0.45)} L${tx} ${ty} L${tx - L * Math.cos(ang + 0.45)} ${ty - L * Math.sin(ang + 0.45)}`, 4.5);
  }
  const centre = (t) => { const r = rect(t); return [r.x + r.w / 2, r.y + r.h / 2]; };
  return { sleep, $, A, ink, dark, rect, byText, stroke, text, circle, scribble, redraw, pointer, tap, menu, toast, ring, arrow, centre };
})();
