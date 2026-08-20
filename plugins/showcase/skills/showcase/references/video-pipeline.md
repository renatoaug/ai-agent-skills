# Video pipeline — mechanics

Everything here was learned by shipping real release videos. Read fully before writing recording code.

## Workspace layout

Keep the whole production in one directory (a scratchpad dir, never inside the user's repo):

```
video/
  narration.json      # the script: single source of truth
  record.mjs          # Playwright takes
  assemble.py         # trim + concat + audio mix (drives ffmpeg)
  regen_tts.py        # (re)generate narration clips for changed beats only
  clips/              # one audio file per beat: <beat_id>.mp3
  takes/              # raw screen recordings: <take_id>.webm
  out/                # assembled versions: v1.mp4, v2.mp4, ...
```

## narration.json schema

```json
{
  "beats": [
    {
      "id": "a1_open",
      "section": "Opening",
      "take": "A_dashboard",
      "text": "This is the spoken line for this beat.",
      "note": "what is on screen / what to highlight"
    }
  ]
}
```

- `id` is stable across versions — clips and markers key off it. Renaming an id forces a TTS regen and a re-record; don't.
- `take` maps the beat to the continuous recording it lives in.

## Recording (Playwright)

**Continuous takes, not per-beat clips.** Record one long take per app area, then cut at assembly. Per-beat recordings multiply seams and make transitions jumpy.

**Marker frames for trimming.** At every beat boundary, flash a full-screen solid-color overlay for ~3 frames (e.g. pure magenta `#ff00ff`). At assembly, scan the take for those frames to get exact cut points. Never trim by wall-clock timestamps — page loads vary run to run.

**Recorder settings.** Viewport 1920×1080. If the source video comes out larger (retina capture), `scale` to width 1920 and `pad` to 1080 — cropping cuts off content at the edges.

**Helpers that must exist:**

- `overlay(page, text)` — draws the on-screen callout. It MUST `await page.waitForFunction(() => !!document.body)` before injecting; right after a navigation `document.body` can be null and the injection crashes the take.
- `marker(page)` — the trim flash described above.
- Retry wrappers around any click that triggers server-side generation — one flaky response should not kill a 3-minute take.

**Navigation realism:**

- Use fresh `page.goto(url)` instead of `page.goBack()`. `goBack()` can restore a bfcache snapshot from *before* your mutations — the audience sees a list without the item you just created.
- Follow the app's own flow. If an action redirects to a detail page, film the detail page there; never navigate away and back to fit an outline.

**Dead time.** Record generation waits in full (so real progress UI stays visible), then speed those windows 8× at assembly with `setpts`. Mark the window boundaries with marker frames too.

## Narration (TTS)

- Provider, model, and voice come from env vars — never hardcoded. Regenerating with a different voice must be a config change, not a code change.
- One clip per beat, named by beat id. Regenerate only beats whose text changed (hash the text if needed).
- **Verify every clip, every time:**
  1. Transcribe with a word-timestamp-capable model (e.g. Whisper `verbose_json`).
  2. Normalize (case, punctuation) and diff transcript vs. script — a missing phrase is a dropout.
  3. `ffmpeg -af silencedetect` on the clip; longest internal gap must stay under ~0.55s.
- TTS reliably mangles: colon constructions ("autonomy: how much of…"), bare numbers, dense acronym runs. When a phrase fails twice, **rephrase it** (e.g. "the autonomy index, which measures how much of…"). Retrying the same text is a coin flip.

## Sync

- On-screen highlight timing (flashing a metric, underlining a value) comes from the **word timestamps of the actual clip**, not from guessed offsets. If the narration says "context, groundedness, answer relevance", each highlight fires at that word's timestamp.
- Each beat's video segment must be at least the clip duration plus 0.4–0.8s of breathing room. Never let the cut land mid-sentence.

## Assembly (ffmpeg)

1. Locate marker frames in each take → cut list per beat.
2. Trim segments; apply `setpts` speed-ups to the flagged wait windows.
3. Concat with the concat demuxer (same codec/params across segments, or re-encode).
4. Place each narration clip with `adelay` at its beat's start; `amix` over the (usually silent) video track.
5. Write `out/v<N>.mp4` — never overwrite the previous version; the user compares rounds.

## QA per round

- Extract one frame per beat boundary (`ffmpeg -ss <t> -frames:v 1`) and inspect all of them.
- Transcribe the **final mixed audio** and diff against the full script.
- Check A/V sync specifically at section transitions — that's where drift accumulates.
- Watch the video end to end.

Only after all four pass does the round go to the user.
