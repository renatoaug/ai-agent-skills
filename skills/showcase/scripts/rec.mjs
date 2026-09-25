// Recording harness: CDP screencast (high-quality JPEG frames with timestamps) + beat log.
import { chromium } from 'playwright';
import fs from 'node:fs';
export const S = process.env.S;
export const N = JSON.parse(fs.readFileSync(`${S}/narration.json`, 'utf8'));
const dur = id => { const o = JSON.parse(fs.readFileSync(`${S}/durations.json`, 'utf8')); return o[id]; };
export const PAD = 0.8;
export const beatLen = id => dur(id) + PAD;
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function take(name, fn, { auth = true, profile = false, cdp = false } = {}) {
  const dir = `${S}/takes/${name}`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  let browser, ctx;
  let cdpPage = null;
  if (cdp) {
    browser = await chromium.connectOverCDP('http://127.0.0.1:9333'); ctx = browser.contexts()[0];
    cdpPage = await ctx.newPage(); await cdpPage.setViewportSize({ width: 1920, height: 1080 }); await cdpPage.addInitScript({ path: `${S}/fx.js` });
  } else if (profile) {
    ctx = await chromium.launchPersistentContext(`${S}/profile`, { headless: true, viewport: { width: 1920, height: 1080 } });
  } else {
    browser = await chromium.launch();
    ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, storageState: auth ? `${S}/state.json` : undefined });
  }
  if (!cdp) await ctx.addInitScript({ path: `${S}/fx.js` });
  const page = cdpPage ?? ctx.pages()[0] ?? await ctx.newPage();
  const frames = []; let rec = false;
  let cdpS;
  const attach = async () => {
    cdpS = await ctx.newCDPSession(page);
    cdpS.on('Page.screencastFrame', async f => {
      if (rec) { const i = frames.length; fs.writeFileSync(`${dir}/${String(i).padStart(6, '0')}.jpg`, Buffer.from(f.data, 'base64')); frames.push(f.metadata.timestamp); }
      cdpS.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
    });
    await cdpS.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  };
  const log = [];
  const api = {
    page,
    fx: (fnName, ...args) => page.evaluate(([n, a]) => window.__fx[n](...a), [fnName, args]),
    async start() { await attach(); rec = true; await sleep(300); },
    beat(id) { log.push({ id, t: Date.now() / 1000 }); return beatLen(id) * 1000; },
    mark(label) { log.push({ id: '#' + label, t: Date.now() / 1000 }); },
    async rect(loc) { return loc.evaluate(el => window.__fx.docRect(el)); },
    async union(...locs) { const rs = await Promise.all(locs.map(l => api.rect(l))); const x = Math.min(...rs.map(r => r.x)), y = Math.min(...rs.map(r => r.y)); return { x, y, w: Math.max(...rs.map(r => r.x + r.w)) - x, h: Math.max(...rs.map(r => r.y + r.h)) - y }; },
    async vrect(loc) { const b = await loc.boundingBox(); return { x: b.x, y: b.y, w: b.width, h: b.height }; },
    async clickOn(loc) {
      const b = await loc.boundingBox();
      await api.fx('cursor', b.x + b.width / 2, b.y + b.height / 2); await sleep(950);
      await api.fx('click'); await sleep(150); await loc.click(); },
  };
  try { await fn(api); } finally {
    log.push({ id: '#end', t: Date.now() / 1000 });
    rec = false; await sleep(200);
    fs.writeFileSync(`${dir}/meta.json`, JSON.stringify({ frames, log }));
    if (cdp) { await page.goto('about:blank').catch(() => {}); } else { await ctx.close(); if (browser) await browser.close(); }
    console.log(name, 'frames', frames.length, 'secs', (frames.at(-1) - frames[0]).toFixed(1));
  }
}
