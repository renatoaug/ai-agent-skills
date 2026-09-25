// Helpers to drive the ttyd terminal from a take. The xterm buffer is readable, so waits are exact, not guessed.
import { sleep } from '../rec.mjs';
export function term(p) {
  const buf = () => p.evaluate(() => { const b = window.term.buffer.active; let s = ''; for (let i = 0; i < b.length; i++) s += b.getLine(i).translateToString(true) + '\n'; return s; });
  const until = async (re, ms = 90000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (re.test(await buf())) return true; await sleep(250); } throw new Error('timeout ' + re); };
  const type = async (s, d = 45) => { await p.keyboard.type(s, { delay: d }); await sleep(300); await p.keyboard.press('Enter'); };
  // wait for Claude Code to finish a turn, approving tool prompts on the way. The end of a turn is the
  // "✻ <Verb> for 12s · done 2:14 PM" line — "esc to interrupt" is not always shown, so do not rely on it.
  const turnsDone = b => (b.match(/✻ [^\n]* for \d+[^\n]*· done/g) || []).length;
  const answered = async (answers = []) => {
    const base = turnsDone(await buf()); const t0 = Date.now(); const done = new Set();
    while (Date.now() - t0 < 900000) {
      const b = await buf(); const tl = b.slice(-3000);
      const a = answers.find(x => !done.has(x.key) && x.when.test(tl));   // skill questions: { key, when: /text/, act: async () => {} }
      if (a) { await sleep(2000); await a.act(); done.add(a.key); await sleep(900); continue; }
      if (/Do you want to proceed|Do you want to make this edit|Do you want to create/i.test(tl)) { await sleep(1200); await p.keyboard.press('Enter'); await sleep(1200); continue; }
      if (turnsDone(b) > base) { await sleep(1500); return; }
      await sleep(400);
    }
    throw new Error('turn did not finish');
  };
  // a URL the CLI printed wrapped across lines (lines are space-padded: trim before joining)
  const url = async re => (await buf()).split('\n').map(l => l.trim()).join('').match(re)?.[0];
  return { buf, until, type, answered, url };
}
