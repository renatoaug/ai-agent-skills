// Injected into every page: camera (zoom/scroll), spotlight, captions, fake cursor.
(() => {
  if (window.__fx) return;
  const ease = t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t+2, 3)/2;
  const css = `
  #fx-spot{position:absolute;z-index:2147483600;pointer-events:none;border-radius:14px;opacity:0;
    box-shadow:0 0 0 2px rgba(120,230,255,.95),0 0 38px 6px rgba(80,200,255,.45),0 0 0 200vmax rgba(3,4,10,.62);
    transition:all 800ms cubic-bezier(.65,0,.35,1)}
  #fx-ring{position:absolute;z-index:2147483601;pointer-events:none;border-radius:10px;opacity:0;
    border:3px solid #ffd166;box-shadow:0 0 24px rgba(255,209,102,.6);transition:all 600ms cubic-bezier(.65,0,.35,1)}
  #fx-cap{position:fixed;left:56px;bottom:56px;z-index:2147483646;pointer-events:none;display:flex;align-items:center;gap:14px;
    font:600 26px/1.1 Inter,ui-sans-serif,system-ui;color:#fff;padding:16px 26px 16px 18px;border-radius:14px;
    background:rgba(10,12,24,.82);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.14);
    box-shadow:0 12px 40px rgba(0,0,0,.5);transform:translateY(30px);opacity:0;transition:all 600ms cubic-bezier(.2,.8,.2,1)}
  #fx-cap b{font:600 15px/1 ui-monospace,Menlo,monospace;color:#0b0d18;background:linear-gradient(90deg,#7df9ff,#b69cff);padding:7px 10px;border-radius:8px}
  #fx-cur{position:fixed;z-index:2147483647;width:30px;height:30px;left:0;top:0;pointer-events:none;
    transition:transform 900ms cubic-bezier(.65,0,.35,1);filter:drop-shadow(0 3px 6px rgba(0,0,0,.6))}
  #fx-cur.click::after{content:"";position:absolute;left:-16px;top:-16px;width:34px;height:34px;border-radius:50%;
    border:3px solid #7df9ff;animation:fxp 500ms ease-out forwards}
  @keyframes fxp{from{transform:scale(.3);opacity:1}to{transform:scale(1.6);opacity:0}}
  #fx-cap.top{bottom:auto;top:28px;left:auto;right:40px}
  #fx-flash{position:fixed;inset:0;z-index:2147483647;pointer-events:none;background:#000;opacity:0;transition:opacity 350ms}
  `;
  const ready = () => document.body && document.head;
  function mount() {
    if (!ready()) return requestAnimationFrame(mount);
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    for (const id of ['fx-spot','fx-ring','fx-cap','fx-flash']) {
      const d = document.createElement('div'); d.id = id;
      (id === 'fx-cap' || id === 'fx-flash' ? document.documentElement : document.documentElement).appendChild(d);
    }
    const c = document.createElement('div'); c.id = 'fx-cur';
    c.innerHTML = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M4 2l16 9.5-7 1.6L9.6 20z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    c.style.transform = 'translate(1500px,900px)'; c.style.opacity = '0';
    document.documentElement.appendChild(c);
  }
  mount();
  let cam3 = { s: 1, tx: 0, ty: 0 };
  const fx = window.__fx = {
    scrollTo(y, ms = 1400) {
      return new Promise(res => {
        const y0 = scrollY, t0 = performance.now();
        const step = now => { const t = Math.min(1, (now - t0) / ms); scrollTo(0, y0 + (y - y0) * ease(t)); t < 1 ? requestAnimationFrame(step) : res(); };
        requestAnimationFrame(step);
      });
    },
    // rect in document coords {x,y,w,h}
    // camera driven by rAF (CSS transitions between two transforms emit no screencast frames)
    animCam(to, ms) {
      const b = document.body; b.style.transformOrigin = '0 0';
      const from = { ...cam3 }; const t0 = performance.now();
      return new Promise(res => {
        const step = now => {
          const k = ease(Math.min(1, (now - t0) / ms));
          cam3 = { s: from.s + (to.s - from.s) * k, tx: from.tx + (to.tx - from.tx) * k, ty: from.ty + (to.ty - from.ty) * k };
          b.style.transform = (cam3.s === 1 && cam3.tx === 0 && cam3.ty === 0) ? '' : `translate(${cam3.tx}px,${cam3.ty}px) scale(${cam3.s})`;
          k < 1 ? requestAnimationFrame(step) : res();
        };
        requestAnimationFrame(step);
      });
    },
    async zoom(r, { max = 2.2, fill = .86, ms = 1200 } = {}) {
      const s = Math.max(1, Math.min(max, innerWidth * fill / r.w, innerHeight * fill / r.h));
      const cy = r.y + r.h / 2, cx = r.x + r.w / 2;
      if (cam3.s === 1 && cam3.tx === 0 && cam3.ty === 0) {
        const target = Math.max(0, cy - innerHeight / 2);
        if (Math.abs(target - scrollY) > 4) await fx.scrollTo(target, 900);
      }
      await fx.animCam({ s, tx: innerWidth / 2 - s * cx, ty: innerHeight / 2 + scrollY - s * cy }, ms);
    },
    async unzoom(ms = 1000) { await fx.animCam({ s: 1, tx: 0, ty: 0 }, ms); },
    spot(r, pad = 14) { // r in document coords (unzoomed) - only use when not zoomed
      const e = document.getElementById('fx-spot');
      Object.assign(e.style, { left: r.x - pad + 'px', top: r.y - pad + 'px', width: r.w + pad*2 + 'px', height: r.h + pad*2 + 'px', opacity: 1 });
      if (!e.parentElement || e.parentElement !== document.body) document.body.appendChild(e);
    },
    unspot() { const e = document.getElementById('fx-spot'); if (e) e.style.opacity = 0; },
    ring(r, pad = 8) {
      const e = document.getElementById('fx-ring'); if (e.parentElement !== document.body) document.body.appendChild(e);
      Object.assign(e.style, { left: r.x - pad + 'px', top: r.y - pad + 'px', width: r.w + pad*2 + 'px', height: r.h + pad*2 + 'px', opacity: 1 });
    },
    unring() { const e = document.getElementById('fx-ring'); if (e) e.style.opacity = 0; },
    caption(n, text) {
      const e = document.getElementById('fx-cap');
      if (!text) { e.style.opacity = 0; e.style.transform = 'translateY(30px)'; return; }
      e.innerHTML = `<b>${n}</b><span>${text}</span>`; e.classList.toggle('top', !!window.__capTop); e.style.opacity = 1; e.style.transform = 'none';
    },
    docRect(el) { // element rect in untransformed document coords, using the live (mid-transition) transform
      const r = el.getBoundingClientRect();
      const t = getComputedStyle(document.body).transform;
      const M = new DOMMatrix(t === 'none' ? undefined : t).inverse();
      const [ox, oy] = getComputedStyle(document.body).transformOrigin.split(' ').map(parseFloat);
      const inv = (vx, vy) => { const q = M.transformPoint(new DOMPoint(vx - ox, vy + scrollY - oy)); return [q.x + ox, q.y + oy]; };
      const [x1, y1] = inv(r.left, r.top), [x2, y2] = inv(r.right, r.bottom);
      return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
    },
    cursor(x, y, show = true) { const c = document.getElementById('fx-cur'); c.style.opacity = show ? 1 : 0; c.style.transform = `translate(${x}px,${y}px)`; },
    click() { const c = document.getElementById('fx-cur'); c.classList.remove('click'); void c.offsetWidth; c.classList.add('click'); },
  };
})();
