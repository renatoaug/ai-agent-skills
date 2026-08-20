# Writing narration

The script is read aloud (by TTS or by the user), so write for the ear, not the page.

## Voice and tone

- Write like a colleague walking someone through their work — first person plural is fine ("here we ask…"), marketing voice is not.
- Short sentences. One idea per sentence. If a sentence needs a comma splice to fit, it's two beats.
- Match the audience's language (a client deck in their language, an open-source video in English) and keep product names exactly as the product spells them.
- Contractions are good; they're how people talk.

## Humanizing (the most common rejection)

Users reject narration that "sounds like AI". The tells, and their fixes:

| AI tell | Human fix |
| ------- | --------- |
| "In this video, we will explore…" | Start inside the subject: "This is the evaluation screen." |
| Title-case listicle headers ("Key Features Overview") | Say what the section actually shows: "Where the answers come from" |
| Symmetric triads ("fast, reliable, and scalable") | Pick the one claim that matters and give its evidence |
| Closing with "…and much more!" | Close with what the audience should do next |
| Narrating the UI literally ("now I click the blue button") | Narrate the intent ("we promote this question to the golden set") |

Test: read the line aloud. If you wouldn't say it to a coworker at their desk, rewrite it.

## Explaining a screen

1. Name what the viewer is looking at ("this is the run history").
2. Point at the one element that matters for this beat.
3. Say what it means for the audience — the consequence, not the mechanism.

Never explain more than one concept per beat; add a beat instead.

## TTS-safe writing

- Avoid colon constructions ("autonomy: how much of the volume…") — engines pause wrong or drop the second half. Fold the definition into the sentence ("the autonomy index, which measures how much of the volume…").
- Spell out what must be spoken precisely: "R$ 4 million" → "four million reais" if the engine misreads currency.
- Acronyms: if it must be read letter by letter, dot it ("C.T.X.") or rewrite to the full term.
- If an engine mangles the same phrase twice, rephrase — don't retry.

## Cloned voices (ElevenLabs and similar)

Narrating with the user's own cloned voice is a big upgrade for authenticity — and a distinct workflow. Everything stays env-driven: API key, voice id, model id, and voice settings are configuration, never constants in code.

**Calibrate with the owner, not by yourself.** Similarity ("does it sound like me?") and naturalness are attributes only the voice's owner can judge. Pick one representative passage (~30s) and generate a small matrix of variants — model × settings — named so the user can refer to them ("A-expressive", "B-neutral"). Send the files, let them pick, then iterate on the winner. Converge on the passage before spending credits on the full script.

**The knobs, and what they trade:**

- `stability` — lower is more expressive, higher is more consistent/faithful. Newer models may only accept discrete modes (creative/natural/robust).
- `similarity_boost` — how hard to pull toward the voice sample; raise it when the user says "doesn't sound like me".
- `style` — expressiveness on older models; often unavailable on newer ones.
- `speed` — native pacing control; prefer it over post-processing (`atempo` shifts formants and sounds processed).
- Model quirks differ: e.g. ElevenLabs `eleven_v3` is markedly more natural but rejects `previous_text`/`next_text` (per-beat prosodic continuity), which `multilingual_v2` supports. Verify per model; expect HTTP 400s to tell you.

**The clone inherits its training sample — fix problems at the source.** Accent drift (a dragged R, a foreign vowel) means the sample didn't anchor that sound: have the user re-record reading sentences dense in the sounds the model gets wrong. Never mix captures — two samples from different mics/rooms average into a voice that is neither; delete the old sample when a better one lands. More material from the *same* capture helps; more captures hurt.

**Expressive models are stochastic — validate every clip, re-roll failures.** Product names and rare words come out differently per generation ("Nord" → "Norde", "set" → "sete"). For each beat with risky words, transcribe the clip and check against an accept/reject word list; regenerate until it passes (cap at ~4 attempts, then rephrase the script instead). Distinguish transcription artifacts from real mispronunciations: the transcriber mishearing a foreign name consistently (e.g. "Claude" → "Cloud") is usually its bias, not the voice's — reject only renderings that reflect actual wrong speech.

**Re-calibrate your QA thresholds per voice.** Human-like voices pause longer at sentence boundaries than robotic ones, so a silence-gap threshold tuned for one engine false-alarms on another. A gap is a dropout only if the transcript lost content or the gap falls mid-phrase.

**A voice swap changes every duration.** Faster/slower speech shifts all beat durations and word offsets: re-measure word timestamps, re-check that each recorded scene still outlasts its narration, and re-record only the takes with baked-in highlights synced to specific words. The beats file plus per-beat clips make this cheap — that's why the pipeline keys everything off beat ids.

## When the user narrates

Deliver a script, not prose:

- Numbered beats, each with a **bold action cue** line (what to click/type) and the spoken line beneath it.
- A timing column with the rehearsed duration per section.
- A pre-flight checklist: window size, tabs open, fixtures loaded, notifications off.
- Flag lines that must be verbatim (names, numbers, legal-ish claims); everything else is a suggestion the user can say their own way.
