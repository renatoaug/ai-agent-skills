---
name: showcase
description: Generate a presentation of software you built — a client delivery, a release, an open-source project, or a whole product — as a video (motion graphics over the product's own clips, or a recorded walkthrough; narrated by an AI voice, the user's voice, or music only), a live-demo script, or a slide deck. Use when the user wants to show their work to an audience.
---

# Showcase

Turn working software into a presentation an audience actually follows. The subject can be anything shippable: one sprint's delivery, a release, an open-source repo, an entire product. The output can be a video (the flagship format), a numbered script for the user to present live, or a slide deck — the user's request decides.

This skill encodes a production-tested pipeline. Its core belief: **a presentation is a product**, so it gets the same treatment — a spec (the beat script), an implementation (recording/deck), and verification (you inspect the actual output before the user ever sees it).

## Step 1 — Scope

Resolve these before producing anything. Infer what you can from context; ask only what you cannot infer.

- **Subject** — what exactly is being shown: a delivery, a release, a repo, the whole product. Scope creep in presentations reads as rambling; pick one story.
- **Audience** — client stakeholders, dev team, open-source users, a conference. This sets language, tone, and depth. Present what the audience can *do* with the thing, not how you built it — architecture only appears if the audience is engineers who will operate it.
- **Format** — video / live-demo script / slide deck (see formats below). For a video, two more choices: the **look** (motion graphics or a recorded walkthrough, Format A) and the **sound** (AI voice, the user's voice, music only, or silence).
- **Duration** — default 2–4 minutes for a product tour, 10–15 slides for a deck. An explainer that must convince (architecture, PoC results, a decision) runs as long as its explanations need — the identity video landed at 9:41 and the user asked for more detail, not less.
- **Voice** — none (a README or landing-page video reads better with music only and short captions), synthesized narration (TTS; default `pt-BR-AntonioNeural` or `en-US-AndrewNeural` at `+10%` via edge-tts), the user's own **cloned voice** (see the cloned-voices section of `references/narration.md` — calibration samples, accent fixes, per-clip validation), or the user's live voice. If the user narrates live, the deliverable shifts: a numbered script plus a silent recording plan, not an assembled video.

## Step 2 — Build the narrative before touching tools

1. **Use the product first.** Click through every flow you intend to show, taking screenshots. You will find rough edges — a confusing label, an empty state, stale test data. Each one either gets fixed before recording or gets addressed in the narration. Never let the audience find it first.
2. **Script as beats.** Structure the story as sections → beats. A beat is one idea, one visual moment, and 1–3 spoken sentences. Keep the script in a single JSON file (`video.json` for motion, `narration.json` for a walkthrough) — it is the single source of truth for text, order, and timing; everything downstream reads from it. A video with no voice still gets beats: the on-screen line of each scene.
3. **Write like a person.** Section titles and narration must sound like a colleague walking you through their work, not generated copy. See `references/narration.md` for the concrete rules — this is the note users push back on most ("sounds like AI").
4. **Follow the real flow.** The camera goes where a real user would go. If creating an item lands on its detail page, present the detail *there*, then move on — never bounce between screens because your outline listed them in a different order.
5. **Open with the outcome.** The first beat says what the audience is about to get out of watching. No throat-clearing, no "in this video we will".

## Format A — Video

The flagship. Two looks, and either takes any sound:

| Look | What it is | Pick it when |
|---|---|---|
| **Motion** (default) | A HyperFrames composition: animated scenes (captions, tiles, callouts, lineups, highlighted screenshots) over clips of the product rendered frame by frame on a transparent background. `references/motion.md`, `scripts/composition/` | A product video, a README, a release, a layout review: anything that should look made, not recorded |
| **Walkthrough** | A continuous recording of the real product with a camera that zooms and spotlights, cut into scenes with transitions | Real work must be seen happening: a model answering, a deploy, a terminal session, logged-in dashboards |

The two combine: a walkthrough take is an mp4 the motion composition can lay in like any other clip.

| Sound | How |
|---|---|
| None, or music only | Each scene has a fixed `dur`; music is a file in the spec (chiptune or any track the user supplies) |
| AI voice | One edge-tts clip per beat; scenes last as long as their lines, highlights fire on the line that names them |
| The user's cloned voice | Same clips, from ElevenLabs, calibrated with the owner (`references/narration.md`) |
| The user live | Format B: the script, plus a silent render timed to their rehearsal |

### Motion

Read `references/motion.md` **before building anything**: scene kinds, timing by beats, getting the clips, the traps and the QA per round. Copy `scripts/composition/` into the workspace and write only `video.json` (start from `video.example.json`); `build.py` writes the composition, so every scene gets the same entrances and the same scene change.

| Script | Job |
|---|---|
| `build.py` + `template.html` + `theme.json` | `video.json` → `index.html`: scenes, timing (from narration when there is one), media laid out in their own aspect, the GSAP vocabulary |
| `voice.py` | One edge-tts clip per beat, cached by text + voice + rate |
| `frames.mjs` | Frame-exact capture of a web UI (fake clock, animations seeked by hand), transparent background |
| `clips.sh` | Frames → VP9 webm with alpha |
| `export.sh` | Render → under 10 MB for GitHub, with a cover frame |

### Walkthrough

Read `references/video-pipeline.md` **before writing any recording code**: defaults, workspace, the per-round loop, framing rules and the traps that cost real time. The working code is in `scripts/` — copy it into the workspace and write only the scenes (`takes.mjs`, starting from `scripts/takes.example.mjs`).

| Script | Job |
|---|---|
| `fx.js` | Camera and overlays injected into every page: rAF zoom/pan, spotlight, ring, chapter caption, fake cursor |
| `rec.mjs` | `take()`: CDP screencast recorder (Chromium, persistent profile, or the user's Chrome over CDP) + beat log |
| `lib.mjs` | `beat()` with cues on spoken words, `svgBox()` to highlight diagram boxes by their label |
| `tts.py` / `verify.py` / `durations.sh` | One clip per beat (edge-tts), transcript diff + word timestamps (mlx-whisper), durations |
| `render_take.py` / `fit_take.py` | Frames → CFR mp4; compress marked waits so a beat fits its line |
| `assemble.py` / `check_audio.py` | Scenes from `narration.json`, xfade transitions, narration mix; final transcript diff |
| `adapters/` | `terminal.sh/.mjs` (real Claude Code in ttyd), `chrome-cdp.sh` (logged-in dashboards), `surreal-studio.mjs` |

Pipeline summary:

1. Continuous take per scene; each beat waits exactly its clip length, and overlays fire on the words the voice says (Whisper timestamps).
2. One TTS clip per beat; only changed lines regenerate. Every clip transcribed and diffed.
3. Real waits (provisioning, model answers) are recorded in full and compressed at render time — the audience sees real progress, not a cut.
4. Assembly overlaps scenes with a 0.6 s transition, mixes, normalizes loudness; `timeline.json` drives frame QA.
5. Deliver `vN.mp4` to `~/Downloads`; every round is a new version.

## Format B — Live-demo script

For when the user presents live or records their own voice.

- Numbered beats; each beat has a **bold action cue** (what to click/type) and the spoken line under it.
- A "reset state" preamble: every fixture, login, and browser tab needed so the demo is repeatable from zero.
- Rehearsal timings per section so the user knows where the time budget goes.
- Mark the two or three beats that tolerate improvisation, and the ones that don't (anything involving generation latency or irreversible actions).

## Format C — Slide deck

A single self-contained HTML file (no external dependencies), or the platform's artifact equivalent.

- Structure: cold open with the outcome → the tour → what's next. One idea per slide.
- Screenshots beat bullet points. Capture them yourself with Playwright at `deviceScaleFactor: 2` so they're crisp; crop to the region that matters.
- The speaker notes carry the narration beats — the slides carry only what the audience should read while listening.

## Verification discipline (non-negotiable)

Never tell the user a video or deck is ready without having inspected the actual output:

- Extract one frame per beat boundary and look at every one: dead frames, wrong screen, cut-off UI, overlays on top of the wrong element.
- Transcribe the final audio and diff it against the script. Any missing phrase is a dropout, not a rounding error.
- Measure the longest silence inside each clip; above ~0.9 s *mid-sentence* means the TTS swallowed something (sentence-boundary pauses of 0.6–0.9 s are normal for neural voices).
- For every side effect the narration claims (a row in the database, an account at the provider), check it through an API or dashboard **before** recording the scene that shows it.
- When TTS consistently mangles a phrase, **rephrase the script** — do not fight the engine with retries.
- Watch the assembled video end to end at least once per delivery round.

## Iterating with the user

Presentations converge by rounds, not by one-shot perfection. Deliver a complete v1 fast, collect the user's feedback as a numbered list, apply the whole list in one round, then **re-verify everything** — not just what changed; assembly-stage edits shift timing globally. Keep each round's output as a new version so the user can compare.
