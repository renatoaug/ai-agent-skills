// Helpers to drive the ttyd terminal from a take. The xterm buffer is readable, so waits are exact, not guessed.
import { sleep } from '../rec.mjs';
export function term(p) {
  const buf = () => p.evaluate(() => { const b = window.term.buffer.active; let s = ''; for (let i = 0; i < b.length; i++) s += b.getLine(i).translateToString(true) + '\n'; return s; });
  const until = async (re, ms = 90000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (re.test(await buf())) return true; await sleep(250); } throw new Error('timeout ' + re); };
  const type = async (s, d = 45) => { await p.keyboard.type(s, { delay: d }); await sleep(300); await p.keyboard.press('Enter'); };
  // wait for Claude Code to finish a turn, approving tool prompts on the way
  const answered = async () => { await until(/esc to interrupt/i, 30000).catch(() => {}); const t0 = Date.now(); while (Date.now() - t0 < 180000) { const b = (await buf()).slice(-2500); if (/Do you want to proceed/.test(b)) { await sleep(1200); await p.keyboard.press('Enter'); } if (!/esc to interrupt/i.test(b)) return; await sleep(400); } };
  // a URL the CLI printed wrapped across lines (lines are space-padded: trim before joining)
  const url = async re => (await buf()).split('\n').map(l => l.trim()).join('').match(re)?.[0];
  return { buf, until, type, answered, url };
}
