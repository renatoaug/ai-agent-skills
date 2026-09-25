import fs from 'node:fs';
import { S, sleep, beatLen } from './rec.mjs';
const W = JSON.parse(fs.readFileSync(`${S}/words.json`, 'utf8'));
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
export const LEAD = 0.25; // audio starts this long after the beat cut
export function at(id, word, nth = 1) {
  const w = norm(word); let k = 0;
  for (const x of W[id]) if (norm(x.w).startsWith(w) && ++k === nth) return x.s + LEAD;
  throw new Error(`word ${word} not in ${id}`);
}
// Run a beat: cues = [[seconds|word|[word,nth], async fn], ...]; waits for the full beat length.
export async function beat(t, id, cues = []) {
  const t0 = Date.now(); const total = t.beat(id);
  const jobs = cues.map(([when, fn]) => (async () => {
    const s = typeof when === 'number' ? when : Array.isArray(when) ? at(id, ...when) : at(id, when);
    const wait = t0 + s * 1000 - Date.now(); if (wait > 0) await sleep(wait);
    await fn();
  })());
  const rest = t0 + total - Date.now(); if (rest > 0) await sleep(rest);
  await Promise.all(jobs);
}
export function svgPart(t, svg, vb, r) {
  return async () => { const b = await t.rect(svg); const k = b.w / vb[0]; return { x: b.x + r[0] * k, y: b.y + r[1] * k, w: r[2] * k, h: r[3] * k }; };
}
export const BASE = process.env.BASE_URL ?? 'http://localhost:3000';  // the app under recording
export async function open(t, path) {
  await t.page.goto(BASE + path, { waitUntil: 'networkidle' });
  await t.page.waitForFunction(() => !!window.__fx && !!document.getElementById('fx-cap'));
  await sleep(1200);
}
// Smallest <rect> of the svg whose on-screen box contains the <text> that starts with `label`.
export function svgBox(t, svg, label) {
  return () => svg.evaluate((s, label) => {
    const inside = (a, b) => a.left >= b.left - 1 && a.top >= b.top - 1 && a.right <= b.right + 1 && a.bottom <= b.bottom + 1;
    const all = [...s.querySelectorAll('text')]; const txt = all.find(x => x.textContent.trim() === label) ?? all.find(x => x.textContent.trim().startsWith(label));
    if (!txt) throw new Error('no text ' + label);
    const tr = txt.getBoundingClientRect();
    const rects = [...s.querySelectorAll('rect')].map(r => [r, r.getBoundingClientRect()]).filter(([, b]) => b.width > 40 && inside(tr, b)).sort((a, b) => a[1].width * a[1].height - b[1].width * b[1].height);
    if (!rects.length) throw new Error('no rect for ' + label);
    return window.__fx.docRect(rects[0][0]);
  }, label);
}
// rect of lines inside a code block (<pre>): the line containing `needle`, `count` lines
export const codeLines = (t, pre, needle, count = 1) => () => pre.evaluate((el, [n, c]) => window.__fx.codeLines(el, n, c), [needle, count]);
