# Decepcionaram production standard

## Scope and evidence

Baseline: the owner-reviewed `Jogos-Que-Decepcionaram-PREVIA.mp4`, inspected alongside `render_decepcionaram.py`, `montar_clipes.py`, corrected word timestamps, narration, QA notes, research notes and the separate final cover on 2026-11-15. This reference replaces the older generic layout suggestions. Use it for narrated gaming videos unless the owner requests a departure. Memes/photo posts keep their own approved format.

These are measured renderer settings, not claims about TikTok's universal requirements. The source video is 49.03 s; a new story may be shorter or longer. Do not reproduce private paths, account data, credentials, licensed fonts or source media in this repository. Acquire authorized media/fonts separately. The style is reusable; the original script and assets are not bundled.

## Canvas, footage and export

- **1080 × 1350, 4:5, 30 fps**, square pixels. Do not silently convert to 1080 × 1920.
- Reference footage processing: centered `crop=ih*4/5:ih`, scale to canvas, `setsar=1`, contrast 1.04, saturation 1.06. Reframe individual clips when a centered crop cuts the important subject; never stretch footage.
- Hard cuts, with a fast opening montage. Reference first four shots last 1.50, 1.25, 1.25 and 1.16 seconds (5.16 s total). Later shots vary roughly 2–7 s to follow the point. Use these as pacing evidence, not a mandatory cut grid.
- Show actual matching gameplay/action, not long model rotations or unrelated floating images. For costumes, combat must show the named costume. Trailers can illustrate a game but do not prove a specific bug or claim; label provenance and verify reuse rights.
- H.264, CRF 19, preset fast, AAC 192 kb/s, `+faststart`. Preserve 30 fps. Confirm compatible pixel format in the export rather than assuming it from codec alone.
- Finish on the spoken payoff/question. The reference renderer has a last-frame padding fallback; do not intentionally add a frozen/silent tail. Verify the real last frame and last spoken word.

## Typography and exact subtitle layout

Use **DIN Condensed Bold** for BOTH titles and subtitles. The source script contains an unused Arial Black variable: that is not the selected font. Do not bundle the system font. If unavailable or unlicensed for the intended workflow, stop the exact-match claim and show an alternative sample for approval.

All coordinates below refer to the 1080 × 1350 canvas. Scale the entire layout uniformly if an explicitly approved alternate export size is needed; do not change aspect ratio or independently shrink the titles.

| Property | Reference value |
| --- | --- |
| Subtitle font | DIN Condensed Bold, 86 px, uppercase |
| Inactive / active color | white / `#FFF176` |
| Outline | 4 px black, alpha 230/255 |
| Line horizontal placement | centered at x=540 |
| Word-tile vertical center | y=884 |
| Group size | max 4 words; split earlier if joined text width exceeds 900 px |
| Group punctuation break | `.`, `?`, `:` |
| Group trailing hold | final word end + 0.12 s |
| Natural spaces | font's measured space advance, NOT manually padded gaps |

Use corrected per-word start/end timestamps, not uniform estimated timing. Preserve accents, punctuation and Unicode. Validate pronunciation and alignment after any narration edit.

For each word, let `age = time - word_start`. While active (`word_start <= time < max(word_end, word_start + 0.04)`), apply:

```text
height_scale = 1 + 0.13 * sin(pi * clamp(age / 0.20, 0, 1))
width_scale = 1
```

Otherwise use scale 1. Keep the same measured horizontal advances during the pulse. Grow vertically around y=884, not from the baseline; highlight only the active word. Do not bounce the whole line, widen tiles, alter tracking, or leave artificial spaces as words grow.

Render each word into a padded transparent tile: 18 px padding, full font ascent + descent height, baseline anchor, and stroke-aware horizontal bounds. Never size glyph buffers from capital letters alone. Accents such as Ã, É, Í, Ó and Ç must remain intact at maximum pulse. Center the tile over the word's fixed advance; retain padding even when the glyph has a negative bearing. A single word wider than the line budget needs explicit layout handling and preview, not silent clipping.

## Left red ribbon titles

- Same DIN Condensed Bold, **68 px**, uppercase white. Ratio to subtitle font is **68/86 ≈ 0.79**, not the old suggested 0.85–0.95.
- Nominal top-left **x=90, y=184**. Left aligned; do not center the ribbon or stick it to the screen's top edge.
- Break intentional title lines with a 72 px line advance. Width = longest measured line + 48 px; height = line count × 72 + 20 px. Text inset 24 px horizontally, 10 px vertically, adjusted for font bounds.
- Red `#E20011` ribbon polygon `(0,0), (width,0), (width-6,height), (0,height)`.
- Hard black shadow alpha 225/255: polygon `(12,12), (width+12,12), (width+6,height+12), (6,height+12)`; allow extra tile bounds for shadow and rotation.
- Entrance lasts **0.22 s**. With `u=clamp(age/0.22,0,1)`, ease `e=1-(1-u)^3`; slide from 20 px left to nominal x, opacity `u`.
- Sustained subtle motion: rotation `0.55*sin(age*2.1)` degrees and vertical displacement `2*sin(age*1.7)` px. Rotate bicubically with expanded bounds and compensate size around the tile center. No aggressive bounce or exaggerated rotation.
- Reference top scrim covers y=0..499 with black alpha `95*sin(pi*y/500)^2` to aid contrast.
- First title is a two-line hook, then a short game name per section. Align changes with the script/word timings, not the reference's fixed timestamps. Keep the ribbon inside the frame even for longer names.

The coordinates are the approved composition, not guaranteed TikTok-safe coordinates for every device. Check the actual mobile upload preview, controls, description overlap and profile crop; seek approval if a different placement/aspect ratio is needed. Do not add an unrelated bottom label.

## Narration, music and page-turn sound

- Approved voice: **Sandro Dutra**, ElevenLabs **Multilingual v2**. Reuse the confirmed voice identifier and generation settings from the authorized project/account. No stability, similarity or speed values were established by the inspected render, so do not invent defaults under the guise of matching it.
- Write and correct the narration before spending generation credits. Preserve the human PT-BR cadence and pronounce each game name naturally. Listen where supported; automatic transcription alone cannot establish a good performance.
- Narration filter: `loudnorm=I=-16:TP=-1.5:LRA=8`.
- Reference original music bed looped at **volume 0.12**. This is a gain for that bed, not a universal loudness guarantee for any song. Use original/licensed music and match its perceived supporting level; speech must stay clear.
- Source footage audio removed in this format. Mix narration + music + page-turn SFX with `amix=inputs=3:duration=first:normalize=0`, then limiter **0.95**, automatic level gain disabled. Encode AAC 192 kb/s.
- Page-turn/rustle occurs at **section/title changes**, not every cut or word. The reference uses an original synthesized 0.32 s burst at 48 kHz, peak-normalized to 0.13, stereo with right channel ×0.94. Reuse an authorized original effect or synthesize one; do not package an unidentified downloaded sound.
- For close procedural reproduction: noise minus its 17-sample moving average; envelope `sin(pi*min(1,t/0.32))^1.5`; flutter `0.5+0.5*sin(2*pi*(34*t+70*t*t))^2`; light impulses at 0.065/0.140/0.205 s (width 0.004 s, gain 0.4). Normalize the combined burst once, not each component. Match by listening, not only peak values.
- The checked reference measured peak -1.19 dBFS and RMS -17.36 dBFS. These are observations, not LUFS targets or proof that any different mix sounds right.
- Use the exact separate description credit `Narração com IA: elevenlabs.io` when applicable. Provider credit, usage licensing and platform AI disclosure are separate checks; the skill never authorizes silently changing a reviewed disclosure setting.

## Editorial formula and research

1. Open immediately with the premise and tension. The reference contrasts high expectations with disappointment, without a generic channel introduction.
2. Give each entry an expectation, then a specific reason the experience fell short. Avoid vague lists of names, unsupported superlatives, and pretending every player agrees.
3. Research before narration. Save claim/source/date notes; distinguish launch reviews from the current patched state. Check primary sources for factual game details and credible reviews for attributed criticism. Qualify opinion and divided reception.
4. Choose visuals that support the narration's subject. Do not show a polished trailer as evidence of a technical failure. Do not equate an illustrative clip with self-recorded gameplay or a reuse license.
5. End with one natural question tied to the premise. Let it finish audibly; no lengthy branded outro or forced engagement speech.
6. A shorter version gets fewer points and a narrower promise, not simply accelerated speech. Keep this typography/motion identity across topics.

## A dedicated cover for each video

The final reference cover is a separate composition, not the auto-extracted one-second preview: prominent character face, supporting game montage, strong contrast, short white headline, red emphasis block. Use that hierarchy, not an identical recycled face/layout for every topic. Covers may use larger display text than in-video titles.

Design a new subject-specific cover with readable thumbnail text, inspect full view and the actual profile-grid crop, and deliver it separately. Do not overwrite an approved cover when adjusting subtitles. During upload verify the final cover was selected; a good file on disk is not proof it was applied. No channel logo unless requested.

## Required QA and handoff

- Compare a new preview side-by-side with the approved reference: actual font, title size/ribbon/left offset, subtitle size/baseline, active color, pulse, natural spacing, framing, audio balance and section rustle.
- Inspect first frame, every title/scene boundary, longest title/word, accented glyphs at peak pulse, and final seconds. Titles must not clip during rotation; subtitles must not jump horizontally.
- Decode the entire export; verify dimensions, frame rate, video/audio streams, duration, audio peaks and unexpected silence. Corrected timestamps must cover the final spoken word.
- Watch the entire export with sound when possible. Static images do not validate animation, waveform checks do not validate pronunciation, and hashes do not validate quality. Report any playback/listening limitation explicitly and mark the result as a preview until checked.
- Keep video, cover, source manifest, research notes, corrected timings and renderer/settings versioned together. Do not share private source assets or secrets in public repositories.
- Show the complete final description (line breaks, credits and hashtags) to Renato, identify the export/cover, and wait for explicit approval before posting. Material changes require review again. Verify final account, visibility, disclosure and published status; uncertain submission is not permission to repost.
