---
name: docs
description: Write and revise documentation the way Renato likes it — decision records, design notes, READMEs, author guides, doc-site pages, Linear cards and code comments. Use when the user asks to document, write up, explain on a page, update a card, or "verifica a página toda".
---

# Docs

Documentation the reader can follow **without someone next to them explaining it**. That is the bar for every kind of doc this skill covers. Everything below is how to hit it.

Core beliefs:

- **A doc is for a cold reader.** Someone who was not in the call, did not read the code, and has five minutes. If they need a person to explain a sentence, the sentence failed.
- **Status is content.** For every idea the doc names, the reader must know: built, built differently, or not built. "The reference does X" without "and we did / did not" is the single most common complaint.
- **Short beats complete.** A short doc read to the end beats a complete doc abandoned at section 3.
- **The reasoning outlives the decision.** Record why, and what lost, or the discussion reopens in three months.

## Step 1 — Pick the kind

Each kind has its own shape. Do not blend them: a decision record that explains options at length is a design note; a design note with no `[DECIDE]` is probably done and should be said so.

| Kind | Job | Length | Changes? |
|---|---|---|---|
| **Decision record** (ADR / PDR) | Why it is like this, months later | Half a page | Never. Supersede with a new one |
| **Design note** | Options weighed, numbers measured, vocabulary, build plan, what is open | As long as it needs | Yes, with an `Updated:` date |
| **README / author guide** | Get someone doing the thing in minutes | 5–8 short sections | Yes |
| **Doc-site page** | Explain one topic to anyone, in order, with diagrams | 6–9 sections | Yes |
| **Linear card** | What we want to prove, the questions, the answers so far | One screen | Yes; log rewrites in a comment |
| **Code comment** | The *why* the code cannot say | A paragraph at most | With the code |

Templates for each kind are in `references/templates.md`. Read it before writing the first draft of any of them.

## Step 2 — Gather before writing

1. **Read the source of truth first.** Code, calls (Fireflies), the reference project, the existing docs. Write from what exists, never from what the user probably meant.
2. **Map each claim to its status.** Keep a private three-column list: idea → where it comes from → built / different / not built. This list becomes the "what building it changed" section and the status markers.
3. **Find the contradiction.** Two docs in the same repo usually disagree somewhere (a record says X, a later note assumes not-X). Surface it in the doc under its own heading; do not silently pick a side.
4. **Settle the vocabulary.** One name per thing, used everywhere. If the code says `core` and the reader knows it as "the LMS", the prose says LMS and the code field stays `core`, once, with the mapping stated.

## Step 3 — Write

Language rules (these are what the user pushes back on):

- **Plain words, explained on first use.** Every term of art gets a half-sentence in its first appearance. "Manifest — the file the platform reads before running the plugin." Never assume the reader knows the term from a previous page.
- **Short sentences.** One idea each. Cut every "in order to", "basically", "essentially", "note that".
- **Concrete over abstract.** "The form comes from the manifest; the LMS writes the record" — then *show the form fields and the record*. A sentence with no example is a sentence the reader will ask about.
- **Numbers, not adjectives.** "6 000 stars", "1 run per namespace", "≤ 2 edits". "Fast", "small", "many" say nothing.
- **Say what did not happen.** "Not built", "designed only", "we did it differently: …". A doc that only lists successes reads as marketing and gets distrusted.
- **State decisions as rules.** "A plugin never writes a raw query", not "we discussed avoiding raw queries".
- **Match the repo's language.** Docs in English stay English; a Portuguese doc site stays Portuguese; code comments follow the file they are in. Never mix inside one document.
- **Files look like files.** When the prose names `plugin.json`, `ui/Deck.tsx`, `migrations/001.surql`, use code formatting, and on a page use a file icon or a tree so it is obvious those are files on disk, not concepts.

Structure rules:

- **Problem first, then shape, then detail.** The reader must know *why this exists* before *what it is*. Open with the problem in 3–5 sentences.
- **Order sections the way a newcomer needs them**, not the way the code is organized. Problem → anatomy → contract → permissions → how to use → how to build one → lifecycle → reference/comparison → what is open.
- **One table where the reader compares; one list where the reader follows.** Tables for options and mappings. Numbered lists only for real sequences.
- **A summary block at the top of every page** (3–5 lines: what this is, what it does, what is open). The user asks for it on every page that lacks it.
- **End with what is open.** A titled "Still open" / "Em aberto" / `[DECIDE]` checklist. Check items off in place when they get built, with a one-line note of what was built.

## Step 4 — Diagrams and terminal blocks

Draw a diagram when it shows a *mechanism* the prose would have to assemble: flow of a request, who talks to whom, before/after, the states of a lifecycle. Do not draw a diagram that restates a list.

- Hairline borders, one or two muted colors, one accent for the thing under discussion. The user's words: "muito colorido, bordas muito grossas" is the failure to avoid.
- Label the arrows with the verb (`clona`, `lê`, `escreve`, `instala`).
- Directory structure is a diagram: use a file tree, with a one-line note per file.
- Commands go in a terminal block with tabs when there is more than one path (`INSTALL` / `VALIDATE` / `MCP`). One command per line; the reader copies, not retypes.

Rules for inline SVG, if the page is HTML: `viewBox` sizing, `currentColor` for theming, markers for arrowheads, `<figure>` + `<figcaption>` stating the claim.

## Step 5 — The consistency pass (mandatory)

Before saying it is done, read the whole doc top to bottom as the cold reader and fix, in this order:

1. **Every term used before it is explained** → move the explanation up or add a half-sentence.
2. **Every claim with no status** → mark built / different / not built.
3. **Every section that repeats another** → merge; keep the better sentence.
4. **Every name used two ways** → pick one, replace all.
5. **Every sentence a reader could ask "what does this mean?" about** → rewrite or add the example.
6. **Every dead link, wrong path, stale date** → fix. Update the `Updated:` line and the index row.

Then verify what is actually served or committed — `grep` the deployed HTML for the new headings, `git show` the committed file — before reporting. A deploy that printed "Ready" has shipped the old content more than once.

## Companions

- **Linear cards**: rewrite the description in three blocks (what we want to prove · questions · answers so far), keep it to one screen, and add a comment logging what changed and why. Never delete the old text without the comment.
- **Design note ↔ record**: when a design note settles a `[DECIDE]`, the record gets a line in "Consequences" or a new record supersedes it. Both indexes (`docs/README.md`, `docs/design/README.md`) get their row updated in the same commit.
- **Docs and code in the same commit.** A structural change without its record or note is not done.

## What this skill does not do

- Marketing copy, landing pages, pitch decks — use `showcase` for presentations.
- API reference generation from source — hand-write only the parts a generator cannot (the why, the boundaries, the examples).
