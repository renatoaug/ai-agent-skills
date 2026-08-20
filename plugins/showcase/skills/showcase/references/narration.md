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

## When the user narrates

Deliver a script, not prose:

- Numbered beats, each with a **bold action cue** line (what to click/type) and the spoken line beneath it.
- A timing column with the rehearsed duration per section.
- A pre-flight checklist: window size, tabs open, fixtures loaded, notifications off.
- Flag lines that must be verbatim (names, numbers, legal-ish claims); everything else is a suggestion the user can say their own way.
