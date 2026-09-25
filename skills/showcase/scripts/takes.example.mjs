// Example takes: one per scene type used in the WorkOS identity video. Copy, rename, adapt.
// Run: S=$PWD node takes.mjs DOC,APP,TERM   → then: python3 render_take.py <Take> ... ; python3 assemble.py out/v1.mp4
import { take, sleep } from './rec.mjs';
import { beat, svgBox, open } from './lib.mjs';
import { term } from './adapters/terminal.mjs';

const which = (process.argv[2] ?? 'DOC,APP,TERM').split(',');
const goSec = async (t, id) => { await t.page.evaluate(id => scrollTo(0, document.getElementById(id).offsetTop - 80), id); await sleep(900); };

// 1. A doc page with a diagram: chapter caption, camera zoom, spotlight/ring synced to spoken words.
if (which.includes('DOC')) await take('A_doc', async t => {
  const p = t.page; await open(t, '/docs'); await goSec(t, 'overview');
  await t.start();                                   // recording starts here: nothing before is in the video
  const svg = p.locator('#overview svg').first();
  await beat(t, 'u1', [                              // cues: [seconds | 'word' | ['word', nth], action]
    [0, async () => { await t.fx('caption', '02', 'How it works'); await t.fx('zoom', await t.rect(svg), { max: 1.4, fill: .95, ms: 1300 }); }],
    ['admin', async () => t.fx('ring', await svgBox(t, svg, 'admin, on the Users screen')(), 5)],   // box found by the text inside it
    [['provedor', 1], async () => t.fx('spot', await svgBox(t, svg, 'login provider')(), 6)],
  ]);
  await t.fx('unspot'); await t.fx('unring');
}, { auth: false });

// 2. A real app flow: fake cursor clicks, typing, a modal, then the page the app lands on.
if (which.includes('APP')) await take('B_app', async t => {
  const p = t.page; await open(t, '/dashboard');       // storageState (state.json) keeps the operator logged in (state.json)
  await t.start();
  await beat(t, 'c1', [
    [0.2, () => t.fx('caption', '03', 'Creating an organization')],
    ['novo', async () => t.clickOn(p.getByRole('button', { name: 'New organization' }))],
    ['nome', async () => { const i = p.getByPlaceholder('Acme School'); await i.click(); await i.pressSequentially('Acme', { delay: 90 }); }],
  ]);
  // Real work that may outlast the line: mark the wait so fit_take.py can speed it up.
  t.beat('c2'); await p.getByRole('button', { name: 'Create' }).click();
  t.mark('w+'); await p.getByRole('link', { name: 'Open' }).waitFor({ timeout: 240000 }); t.mark('w-');
  await sleep(2000);
});

// 3. A real terminal (ttyd, started with adapters/terminal.sh) running Claude Code against an MCP server.
if (which.includes('TERM')) await take('C_term', async t => {
  const p = t.page; await p.goto('http://localhost:7681/', { waitUntil: 'networkidle' }); await sleep(1500);
  const tm = term(p);
  await t.start();
  await p.evaluate(() => { window.__capTop = true; }); await t.fx('caption', 'MCP', 'Claude Code');  // caption top-right: the prompt line is at the bottom
  t.beat('m1');
  await tm.type('claude', 80); t.mark('w+'); await tm.until(/effort/); t.mark('w-'); await sleep(1500);
  t.beat('m2');
  await tm.type('Who am I in this organization?', 55);
  t.mark('w+'); await tm.answered(); t.mark('w-');   // model latency gets compressed by fit_take.py
  await sleep(4500);                                 // hold the answer on screen while the narration talks about it
}, { auth: false });

// 4. A logged-in third-party dashboard (database studio, identity provider dashboard): attach to the user's Chrome (adapters/chrome-cdp.sh).
//    take(name, fn, { cdp: true }) — the page is emulated at 1920×1080 inside the user's window; the user sees it
//    shifted, the recording does not. Frame zooms by the full row/table width or the right side gets cut.

process.exit(0);
