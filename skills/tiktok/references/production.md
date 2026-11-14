# Production notes

Read for render implementation and visual QA. These are adjustable production starting points, not measured values from a recovered template or universal TikTok requirements.

## Reusable project, not a hard-coded one-off

Keep a small manifest beside editable sources:

- Reference and approved export paths/version.
- Canvas, FPS, font files/license, title/subtitle styles, positions, and maximum animated bounds.
- Source clip provenance, cut ranges, which outfit/action each clip depicts, and any caveats.
- Script, narration voice/settings, final audio, word timestamps, scene order, and durations.
- Cover asset/frame, description text, and the export/text version approved for publishing.

Do not store credentials, session tokens, private conversations, or unrelated personal details in the project or skill.

## Layout calibration

A practical new-video starting canvas is 1080 × 1920 (9:16). Preserve source motion appropriately rather than upscaling a low-resolution clip and calling it higher quality. Pick FPS/export settings for the source and current upload support; do not change them merely to sound “professional”.

Build one representative sample before a full render: a long subtitle line, its largest word, a title, moving footage, and the cover. Compare it at phone size against the latest approved reference.

Use a shared subtitle base size `S` and a slightly smaller title style; around `0.85–0.95 × S` is an **initial tuning range**, not a locked brand ratio. Test rendered cap height, line wrapping, stroke, and peak animation size. A numeric font size alone does not produce visual consistency across typefaces.

Inspect top navigation, right-hand buttons, bottom description, and profile-grid crop in the current app/upload preview. Place essential text within the unobstructed area and move the visual subject as needed. Do not “solve” a crop by adding large empty space below everything.

## Spoken-word animation

Generate or align word timestamps to the **final narration audio**. Do not divide sentence duration evenly among words. A workable first pass is:

1. Group a small number of words into readable phrase chunks, with deliberate breaks.
2. Keep the chunk's position stable; reserve space for the largest word state.
3. On the spoken word's onset, reveal/highlight it and briefly scale it up, then ease it back to the base size before the next emphasized word.
4. Use a restrained elastic overshoot (for example, a 1.10–1.18 peak) as a preview starting point. Tune against the reference: the desired effect is a soft swell/ripple, not rubbery distortion or a bouncing paragraph.
5. Check punctuation, short function words, proper nouns, word collisions, baseline jumps, and the final word of each chunk.

These values are suggested implementation choices. Prefer recovered parameters from the latest approved project. Keep timing and typography configurable so one correction updates all titles/subtitles consistently.

## Memes and compositing

For a background change, preserve the original clip's frame rate, timing, subjects, and audio unless the request says otherwise. Inspect masks during movement, not only still frames: ears, paws, motion blur, holes, halos, flicker, and edges crossing the text band.

Make the requested object recognizable in the actual composition. In the PS5 example, a small console hidden behind the cats did not communicate the joke; a larger console and box improved legibility. That is a compositional lesson, not a requirement to put a PS5 box behind every meme.

Do not remove third-party attribution/watermarks to pass a source clip off as original. Distinguish the owner's optional channel branding from source attribution, and use authorized material. Adapting a caption does not establish reuse rights.

## Technical checks supplement viewing

Use installed tools such as ffprobe/ffmpeg where suitable, without assuming a fixed runtime or downloading arbitrary helpers. Probe container/video/audio durations, dimensions, FPS and channel layout; decode the final file and inspect unexpected freezes/silence. For narration, compare final transcript/alignment with the script, then listen through the joins. For memes, a stream hash can confirm that the requested original audio survived.

Technical validation cannot judge the joke, animation feel, music balance, pronunciation, or whether the mask looks convincing. Report each verification honestly and keep the previous approved version recoverable.
