# Motion videos — the composition pipeline

A product video built as a [HyperFrames](https://hyperframes.dev) composition: HTML scenes animated with GSAP, the product's own clips and screenshots laid in, rendered frame by frame to mp4. This is where the motion lives — captions that come up line by line, tiles that rise and take the light in turn, callouts that draw a line to what they point at, a lineup where each piece lands big in the middle and glides into its slot. Learned on the Clauddy README video (100 s, music only, two languages) and the Tank layout walkthrough (screenshots with highlight boxes).

Narration is optional and plugs into the same composition: with beats, each scene lasts as long as its lines and every highlight fires on the line that names it; without, each scene has a fixed `dur`. Music is optional too.

## Workspace

```
video/                       # in the scratchpad, or tools/<name>/ in the repo when the user wants to re-render it as the product changes
  video.json                 # the spec: scenes, beats (optional), music (optional), theme overrides
  assets/                    # clips (.webm with alpha), screenshots (.png), music
  frames/<clip>/0000.png...  # raw frames, before clips.sh encodes them
  clips/<beat>.mp3           # narration, one clip per beat (voice.py, or a cloned voice)
  index.html                 # written by build.py — never edit it by hand
```

Copy `../scripts/composition/` into it. The loop:

```sh
python3 voice.py                                       # only with narration; regenerates changed lines only
python3 build.py [--lang en]                           # video.json -> index.html, prints every scene's start and length
npx hyperframes@<pinned> lint                          # 0 errors; "nested_structure_needs_subcomposition" warnings are fine
npx hyperframes@<pinned> snapshot --at 1,4.5,12 --no-end -o snap   # look at the contact sheet
npx hyperframes@<pinned> render -f 30 -q high -o render.mp4
./export.sh render.mp4 ~/Downloads/<name>-vN.mp4       # under 10 MB for GitHub, with a cover
```

Pin the HyperFrames version (`@0.8.164` rendered Clauddy, `@0.8.209` the Tank walkthrough) so a re-render months later behaves the same.

## Scene kinds (`build.py`)

| Kind | What moves | Use for |
|---|---|---|
| `card` | Nothing on the opening (whole from frame 1, so a player's preview and the file's thumbnail show it); on the outro, the name, line and command build up | Opening and closing: name, one line, the install command |
| `hook` | A big number counts up, turns hot and shakes; the media lands beside it; headline and subline follow | The problem in one number (100% mid-task) |
| `feature` | Caption lines stagger in on one side; the media slides in from the other; callouts pop and draw a dotted line to a point of the media | One screen and the 2–3 things on it worth naming |
| `row` | Caption, then 2–4 tiles rise in with labels; each tile takes the light (scale + glow) in turn | States side by side: moods, sizes, holidays |
| `lineup` | Each item lands big in the middle while what is already placed blurs, says what it is, then glides into its slot in the row | The product's shapes, one at a time, ending in an overview |
| `shot` | A screenshot in a framed window with a slow push-in; highlight boxes pop and dim everything else; a numbered caption below | Walking through a static UI (layout reviews, proposals) |
| `scroll` | A tall media slides up inside a masked window | A long panel: details, history, settings |
| `checklist` | A heading, then one line at a time | What to do next, what to validate |

Scene changes are all the same and it is what makes the video feel like one piece: the new scene settles up 24 px into place over 0.6 s, the old one fades out over its last 0.45 s. The last scene fades its content out instead of cutting.

Timing per item: `"at": 2.5` (seconds into the scene), or `"beat": "b3"` to fire when that narrated line starts. Without either, callouts come every 1.2 s from 2.5 s, highlights every 2 s from 0.8 s, spotlights spread over the scene.

Text fields take a string or `{"pt": "...", "en": "..."}`; `--lang` picks one, so one spec renders both cuts. `<b>` and `<em>` inside a title or line get the accent styles. Colors and fonts come from `theme.json`; override any token in `video.json` → `"theme"` to match the product (Clauddy's warm dark, Tank's light paper).

## Getting the clips

The composition never records a screen: it lays in clips made beforehand, at 30 fps on a transparent background, so the product floats on the scene.

- **Web app**: `frames.mjs` drives Playwright with a fake clock and every CSS/WAAPI animation paused and seeked by hand, so each screenshot lands exactly 1/30 s after the last however long the screenshot takes (`omitBackground: true` keeps the alpha). Load the real UI with fixture data (stub the API or the preload bridge) so no real account shows. `record(page, dir, ms, { clip, at })`: `clip` is the element's box plus room for its shadow, `at` maps a frame index to an action fired mid-clip (a hover, a data push).
- **Native app**: render frames with the app's own drawing code, the way its snapshot tests do, moving the app's animation clock 1/30 s per frame (Clauddy: an ignored Rust test on egui_kittest, ~13 ms a frame).
- **Screenshots** (`shot`): capture at the size the frame shows them; read highlight boxes from the DOM (`locator.boundingBox()` into a JSON) rather than guessing coordinates.
- `clips.sh` encodes `frames/<name>/` into `assets/<name>.webm` (VP9, `yuva420p`).

Each clip must last at least as long as its scene, from the scene's start; a clip shown in several scenes (the pet in the opening and the outro) is one file used twice. When a scene is timed to things inside a clip (a value ticks up at frame 60, a remark at frame 105), write those frame numbers next to the scene and convert them to `at` seconds.

## Narration

Off by default for a README or landing-page video (music only, or silence); on for a delivery, a walkthrough, anything that explains. Three sources write the same `clips/<id>.mp3`, so `build.py` does not care which:

- **AI voice**: `voice.py`, edge-tts, `en-US-AndrewNeural` or `pt-BR-AntonioNeural` at `+10%`.
- **The user's cloned voice**: ElevenLabs per beat, calibrated with the owner first (see `narration.md`).
- **The user live**: no clips; deliver the script (Format B) and a silent render with each scene's `dur` set to their rehearsed timing.

Each scene lasts its beats' clips plus 0.8 s each, from a 0.6 s lead-in; the voice starts 0.25 s after the picture moves. Music under narration drops to 0.25 volume. A beat's text follows `narration.md` (write for the ear, one idea per line).

## Traps that cost real time

| Symptom | Cause | Fix |
|---|---|---|
| A clip plays frozen on its first frame | `<video>` without an `id` | `build.py` gives every one an id; `lint` catches it in hand-written scenes |
| A clip squashed or shifted in the render, fine in `snapshot` | The renderer letterboxes each video into its element's box; a box of another aspect shifts it, and `snapshot` doesn't show it | Always both width and height, in the clip's aspect: `build.py` reads every media's size with ffprobe |
| Part of a scene never appears (a number, a kicker), the rest does | Inline JS in the timeline that reads the DOM or computed styles at build time (an IIFE, `getComputedStyle`) breaks under the renderer | Keep logic in the template's helpers (`count`, `spot`, `lineup`) and pass plain values; colors from the theme, not from CSS at runtime |
| Callout line points next to the row it names | Coordinates guessed | Targets are fractions of the media; measure them on a rendered frame (`snapshot` the scene, read the pixel row) and correct |
| edge-tts `NoAudioReceived` on the same line every time | A colon construction in the text (and some symbols) | Rephrase ("It follows the session. It works…"); intermittent failures are the service, retried by `voice.py` |
| The opening shows a black or half-built frame as the thumbnail | Opening scene animates in | `card` as the first scene is whole from frame 1 |
| The render is 20 MB and GitHub refuses it | Default render quality | `export.sh`: x264 crf 26, ~5 MB for 100 s at 1080p |
| A detached background job (render, encode) silently never ran | `( cmd & )` inside a tool call dies with the call | Run it in the foreground, or as a proper background task, and check its log |

## QA per round

1. `lint`: no errors.
2. `snapshot` at a moment inside every scene, after its entrances (the contact sheet): wrong media, a caption off-screen, a callout off target, a tile missing.
3. After `render`: duration as `build.py` printed; one frame per scene from the mp4 tiled into a sheet and looked at; and clips really play — pick two frames ~0.5 s apart inside a clip and diff the region (beware of loops whose period matches the gap).
4. With narration: `silencedetect` shows speech starting at each beat's start; transcribe and diff against the beats (`verify.py`/`check_audio.py`) before delivering.
5. Both languages when the spec has both: every visible line in the right one.
