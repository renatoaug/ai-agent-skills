---
name: showcase
description: Generate a presentation of software you built — a client delivery, a release, an open-source project, or a whole product — as a narrated video tour, a live-demo script, or a slide deck. Use when the user wants to show their work to an audience.
---

# Showcase

Turn working software into a presentation an audience actually follows. The subject can be anything shippable: one sprint's delivery, a release, an open-source repo, an entire product. The output can be a narrated video tour (the flagship format), a numbered script for the user to present live, or a slide deck — the user's request decides.

This skill encodes a production-tested pipeline. Its core belief: **a presentation is a product**, so it gets the same treatment — a spec (the beat script), an implementation (recording/deck), and verification (you inspect the actual output before the user ever sees it).

## Step 1 — Scope

Resolve these before producing anything. Infer what you can from context; ask only what you cannot infer.

- **Subject** — what exactly is being shown: a delivery, a release, a repo, the whole product. Scope creep in presentations reads as rambling; pick one story.
- **Audience** — client stakeholders, dev team, open-source users, a conference. This sets language, tone, and depth. Present what the audience can *do* with the thing, not how you built it — architecture only appears if the audience is engineers who will operate it.
- **Format** — video tour / live-demo script / slide deck (see formats below).
- **Duration** — default 2–4 minutes for video, 10–15 slides for a deck. Shorter than the user fears is almost always right.
- **Voice** — synthesized narration (TTS), the user's own **cloned voice** (see the cloned-voices section of `references/narration.md` — calibration samples, accent fixes, per-clip validation), or the user's live voice. If the user narrates live, the deliverable shifts: a numbered script plus a silent recording plan, not an assembled video.

## Step 2 — Build the narrative before touching tools

1. **Use the product first.** Click through every flow you intend to show, taking screenshots. You will find rough edges — a confusing label, an empty state, stale test data. Each one either gets fixed before recording or gets addressed in the narration. Never let the audience find it first.
2. **Script as beats.** Structure the story as sections → beats. A beat is one idea, one visual moment, and 1–3 spoken sentences. Keep the script in a single JSON file (`narration.json`) — it is the single source of truth for text, order, and timing; recording and assembly both read from it.
3. **Write like a person.** Section titles and narration must sound like a colleague walking you through their work, not generated copy. See `references/narration.md` for the concrete rules — this is the note users push back on most ("sounds like AI").
4. **Follow the real flow.** The camera goes where a real user would go. If creating an item lands on its detail page, present the detail *there*, then move on — never bounce between screens because your outline listed them in a different order.
5. **Open with the outcome.** The first beat says what the audience is about to get out of watching. No throat-clearing, no "in this video we will".

## Format A — Narrated video tour

The flagship. Read `references/video-pipeline.md` **before writing any recording code** — it carries the mechanics that cost real debugging time (marker-based trimming, bfcache traps, TTS verification).

Pipeline summary:

1. Continuous Playwright takes per app area, with visual marker frames at beat boundaries.
2. One TTS clip per beat, provider/model/voice driven by env vars — never hardcoded.
3. Every clip verified by transcription: full-transcript match plus a max-silence-gap check.
4. Highlight/overlay timing aligned to word-level timestamps — never eyeballed.
5. ffmpeg assembly: trim by markers, speed up dead waits, mix narration, verify frame-by-frame.

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
- Measure the longest silence inside each clip; above ~0.55s means the TTS swallowed something.
- When TTS consistently mangles a phrase, **rephrase the script** — do not fight the engine with retries.
- Watch the assembled video end to end at least once per delivery round.

## Iterating with the user

Presentations converge by rounds, not by one-shot perfection. Deliver a complete v1 fast, collect the user's feedback as a numbered list, apply the whole list in one round, then **re-verify everything** — not just what changed; assembly-stage edits shift timing globally. Keep each round's output as a new version so the user can compare.
