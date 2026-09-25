# Video pipeline — mechanics

Everything here was learned shipping real videos (the WorkOS identity tour: 9:41, 44 lines, 18 scenes, 9 feedback rounds). The scripts live in `../scripts/`. Copy them into the workspace; do not rewrite them.

## Defaults

| Thing | Default | Why |
|---|---|---|
| Voice | `pt-BR-AntonioNeural`, rate `+10%`, via `edge-tts` | Natural, free, no key. +10% keeps a 9-minute script under 10 |
| English voice | `en-US-AndrewNeural` | Same engine |
| Transcriber | `mlx-whisper`, `mlx-community/whisper-large-v3-turbo`, word timestamps | Local on Apple Silicon, fast, gives the cue times |
| Canvas | 1920×1080, 30 fps, x264 crf 18, AAC 192k, loudnorm −16 LUFS | |
| Capture | CDP `Page.startScreencast`, JPEG q92, frames timestamped | Playwright `recordVideo` is blurry VP8 |
| Pad after each line | 0.8 s (beats), 1.2 s (fitted takes) | Breathing room; the cut never lands mid-word |
| Audio lead | 0.25 s after the beat cut | Picture moves first, voice follows |
| Transition between scenes | 0.6 s `xfade`, rotating `smoothleft`, `circleopen`, `fade`, `smoothup`, `zoomin`; last one `fadeblack` | Varied, never flashy; set per scene in `narration.json` → `"transitions"` |
| Video start / end | 0.6 s fade-in, 1.0 s fade-out | |
| Length | Whatever the content needs. The user prefers complete (≈9 min) over short when it convinces | Ask once; do not cut explanations to hit a number |

Setup, once per workspace:

```sh
python3 -m venv .venv && .venv/bin/pip install edge-tts mlx-whisper
npm init -y && npm i playwright            # uses the installed Chromium
brew install ttyd                          # only for terminal scenes
```

## Workspace layout

```
video/                      # in the scratchpad, never in the user's repo
  narration.json            # the script: single source of truth (voice, rate, lang, beats, transitions)
  fx.js rec.mjs lib.mjs     # camera + recorder + beat/cue helpers (from ../scripts)
  takes.mjs                 # the scenes of THIS video (start from takes.example.mjs)
  tts.py verify.py durations.sh render_take.py fit_take.py assemble.py check_audio.py
  adapters/                 # terminal.sh/.mjs, chrome-cdp.sh, surreal-studio.mjs
  clips/<beat>.mp3          # one narration clip per beat (+ .hash so unchanged lines are not regenerated)
  words.json                # word timestamps per beat (written by verify.py)
  takes/<Take>/             # raw frames + meta.json (frame times + beat log)
  takes/<Take>.mp4          # rendered take; <Take>.beats.json = beat offsets inside it
  out/vN.mp4                # every round is a new version; the deliverable is copied to ~/Downloads
```

## narration.json

```json
{
  "voice": "pt-BR-AntonioNeural", "rate": "+10%", "lang": "pt",
  "transitions": { "L_local": "circleopen", "I_close": "fadeblack" },
  "beats": [
    { "id": "a1", "take": "A_home", "text": "Esse vídeo mostra o resultado da PoC..." }
  ]
}
```

- `id` is stable across rounds; clips, words and cues key off it. New line between two others → new id (`u3b`), never renumber.
- Beat order = video order. Consecutive beats with the same `take` form one scene.

## The loop, per round

```sh
.venv/bin/python tts.py [ids…]        # only changed lines regenerate (text+voice+rate hash)
.venv/bin/python verify.py [ids…]     # transcript diff + longest gap; writes words.json
./durations.sh
S=$PWD node takes.mjs A,B             # record only the scenes that changed
python3 render_take.py A_home B_x     # frames → CFR mp4 starting at the first beat
python3 fit_take.py M_mcp             # only for takes with w+/w- wait marks
python3 assemble.py out/v2.mp4
.venv/bin/python check_audio.py out/v2.mp4
cp out/v2.mp4 ~/Downloads/<name>-v2.mp4
```

## Recording

`take(name, fn, opts)` in `rec.mjs` opens a context, injects `fx.js` into every page, and records only after `t.start()`. `opts`: `{ auth: false }` (no storageState), `{ cdp: true }` (attach to the user's Chrome), `{ profile: true }` (persistent Chromium profile).

- **Beats drive time.** `await beat(t, 'id', cues)` logs the beat start and waits exactly clip + pad. Cues fire at seconds or at a spoken word: `['admin', fn]`, `[['provedor', 2], fn]` (2nd occurrence). Words match the **Whisper** transcript (accent-folded prefix), so check `words.json` when a cue throws "word not in".
- **Unbounded real work** (provisioning, model answers, installs): call `t.beat(id)` yourself, wrap the wait in `t.mark('w+')` / `t.mark('w-')`, and run `fit_take.py`: it speeds only those windows (≤16×) so the beat fits its line.
- **Logins:** save `state.json` once (headed login script) and reuse it as storageState. Google SSO blocks automated Chromium → use `adapters/chrome-cdp.sh` (real Chrome, user logs in, **keeps the window open**; session-only cookies die on close).
- **Terminal scenes:** `adapters/terminal.sh <dir> <label>` then record `http://localhost:7681`. Read the xterm buffer to wait for real output; never sleep-and-hope. Claude Code runs with only the demo MCP (`.mcp-demo.json`), so personal servers never appear in `/mcp`. OAuth logins the CLI prints can be completed off-camera by opening the printed URL in a context with `state.json` and clicking the consent button.
- **Destructive setup** (remove a row, delete a test org) happens outside `t.start()`, and gets restored afterwards so the product state matches the story.

## Camera and overlays (`fx.js`)

| Call | Effect |
|---|---|
| `zoom(rect, {max, fill, ms})` | Pan+zoom so `rect` fills `fill` of the screen, capped at `max`, never below 1×. Driven by rAF |
| `unzoom(ms)` | Back to 1× |
| `spot(rect, pad)` / `unspot()` | Dims everything else, cyan glowing border. The main "look here" |
| `ring(rect, pad)` / `unring()` | Amber ring, for the one element inside a spotlit area the voice names |
| `caption(tag, text)` | Chapter label bottom-left (`window.__capTop = true` → top-right, for terminals) |
| `cursor(x, y)` / `click()` via `t.clickOn(locator)` | Fake cursor glides to the element, pulse on click |

Rects: `t.rect(locator)`, `t.union(...locators)`, `svgBox(t, svg, 'text in the box')` (smallest `<rect>` that contains that text). Coordinates are document space and account for the current zoom.

Framing rules the user checks:

1. **Zoom on the thing the sentence is about**, then move the spot/ring as the sentence moves. One idea per beat → one framing.
2. **Anchor highlights to the DOM, never to guessed coordinates.** Diagrams: `svgBox` by the label inside the box. Guessed viewBox coordinates drifted by 20–50 px and the user flagged every one.
3. **Rings on a card = the card element** (title's parent), not the union of texts inside it (falls short of the edges).
4. **Tables: frame the full row width** (include the last column header) or the zoom centers left and cuts the right side.
5. Cue a zoom on a word *before* the last word of the line; a zoom fired on the last word lands after the voice ends.
6. Modals live in the browser top layer: body transforms and spot/ring do not reach them. Scale the `<dialog>` itself and highlight its rows with inline outline styles (see the creation step list in the WorkOS video).

## Assembly (`assemble.py`)

Scenes come from `narration.json`; per take it cuts [first beat → `#end`/`#nav`], overlaps scenes by 0.6 s with the scene's transition, places each clip at scene start + beat offset + 0.25 s, mixes, normalizes loudness, fades in/out. If a rewritten line now outlasts its old take, it freezes the last frame (`tpad`) instead of cutting the voice, and prints `WARN overlap` when a line would run into the next one. `out/vN.mp4.timeline.json` has every beat's time in the final video, for frame QA.

## QA per round (all four, every round)

1. `check_audio.py`: ratio ≥ 0.97 and no missing run that is not an acronym or a number spelled out ("o i d c", "noventa e nove" are fine).
2. One frame per beat at 60% of its line (from `timeline.json`), tiled 3×5, and **looked at**: wrong screen, zoom not applied, highlight off-target, caption stale.
3. Frames at every scene boundary (transition midpoints).
4. For each fix the user asked for, a frame proving it.

## Traps that cost real time

| Symptom | Cause | Fix |
|---|---|---|
| Zoom "jumps", frozen frames for 5 s | CSS `transition` between two non-identity transforms emits **no screencast frames** in Chrome | Camera animated by `requestAnimationFrame` (current `fx.js`) |
| Highlight lands in the wrong place while zoomed | Element rect read from the screen during/after a transform | `fx.docRect()` inverts the live transform matrix |
| Zoom did nothing | Target taller than the screen → scale < 1 | `max(1, …)`; frame a sub-part (top of a tall diagram) |
| Google "este navegador pode não ser seguro" | Automated Chromium | `chrome-cdp.sh` real Chrome, no automation flags |
| Logged out after closing the browser | Session cookies | Keep the CDP Chrome open for the whole production |
| MCP tool "worked" but nothing downstream | App fired a webhook in `after()` inside a streaming MCP response; it never ran | Found in the receiver's logs; fixed in the app. **Verify side effects you narrate** (DB row, provider account) with an API call before recording the "look, it's there" scene |
| TTS reads "SaaS" as S-A-A-S, merges "No Thanos" | Engine quirks | Rephrase ("na nossa hospedagem"); acronyms the viewer must hear letter by letter: `O.I.D.C.`, `S.C.I.M.` |
| Transcript shows "Tenon .org", "alta zero", "Cloud" | Whisper bias on names | Not a voice problem; accept if the ratio holds |
| Page looks shifted right in the user's Chrome during CDP takes | The tab is emulated at 1920×1080 inside a bigger window | Expected; the recording is correct. Close leftover `about:blank` tabs after takes |
| Product bugs found mid-production (broken deploy, missing side effect) | The product was already broken | Report with evidence (logs), fix on a branch, the user pushes and deploys (production deploys are theirs) |
