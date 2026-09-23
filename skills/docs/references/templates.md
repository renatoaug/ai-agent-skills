# Templates

One per doc kind. Copy the skeleton, keep the section names, fill with real content. Delete a section only when it would be empty — and then say so in one line ("No alternatives were on the table").

## Decision record (ADR / PDR)

Half a page, immutable. ADR for technical choices, PDR for product direction. Number sequentially per prefix. Reversing a decision = new record + `Superseded by` on the old one.

```markdown
# ADR-NNN: <Title stated as the decision, not the topic>

- **Status**: Accepted | Superseded by ADR-NNN
- **Date**: YYYY-MM
- **Related**: design notes, issues, other records

## Context
What was the situation and the forces at play? (2–5 sentences)

## Decision
What we decided, stated as a rule someone can follow. Bold the rule.
If it is designed and not built, say "This is designed, not built."

## Alternatives considered
- **<Option>** — what it is. Rejected: why, in one sentence.

## Consequences
- What this makes easier.
- What this makes harder, and what to watch.
- Still open: <the questions this record does not answer>.
```

## Design note

As long as it needs; changes over time. Carries the reasoning a record leaves out.

```markdown
# <Topic> — design notes

Updated: YYYY-MM-DD

> One paragraph: which record this feeds, what it fills, what it does not reopen.
> **Updated YYYY-MM-DD:** one line when the status changes (e.g. "a v0 of this runs").

---

## The problem
3–5 sentences. What is missing today and what breaks without it. A bullet list of the questions the note answers.

## What the reference does
If there is a reference project: what it does, precisely. Then a table:
| Idea | Why it fits / why not |

## The shape
The proposal. Code blocks for the contract (manifest, schema, API). A table for each mapping.
Mark anything undecided inline as `[DECIDE]`.

## A contradiction to settle first
Only if one exists between this note and an existing record or note. Name both sides.

## What building it changed
Three-column table: proposal → what we built → why it differs. Fill after implementation.

## `[DECIDE]`
- [ ] open item, with the one-line reason it is open
- [x] closed item → what was built (one line)

## Depends on
Links to records and other notes.
```

## README / author guide

For someone who wants to *do* the thing. Five to eight short sections. The reader should be running something by section 3.

```markdown
# <Thing>

One paragraph: what it is, for whom, what they get.

## O que você precisa
Tools and versions. One line each.

## Em 5 minutos
Numbered steps, one command each, ending in something visible on screen.

## A estrutura
File tree with a one-line note per file.

## <The contract>
The one file/config that matters, with every field explained in a table: field · what it is · required · example.

## Regras
What is refused and why, as short rules. Include the error message the reader will see.

## Verificar
The command that validates, and what its output means.

## O que ainda não dá
Honest list of the limits. This section is why people trust the rest.
```

## Doc-site page

For anyone, in order, with diagrams. Six to nine sections. Each section: an eyebrow (`01 · Problema`), a title, a 2–3 sentence lead in plain words, then the content.

```
Summary block (3–5 lines: what · state · open)

1. Problem          — why this exists; why the obvious alternative fails
2. Anatomy          — what the thing is made of (file tree) and what the platform does for it
3. Contract         — the manifest/config, field by field; the vocabulary (closed lists shown in full)
4. Permissions      — what it may touch and how that is enforced
5. Using it         — terminal block: install / run / talk to it through the agent
6. Building one     — numbered steps + terminal block
7. Lifecycle        — one diagram: load → validate → install → mount → update → remove
8. Reference        — what the reference project does and what we did the same / differently / not
9. Open             — what is not built, one line each, and why
```

Design defaults: hairline borders, one accent color, file icons on filenames, tables for mappings, `Terminal` component with tabs for commands. No decorative diagrams.

## Linear card

The description is the current truth; comments are the log.

```markdown
## O que queremos provar
1. <claim we can verify, with what "verified" looks like>
(3–5 items)

## Perguntas
1. <question> — **resposta:** <answer or "em aberto">
(4–7 items)

## Decidido
- <decision as a rule, with link to the ADR/PDR/note>

## Referências
- <design note>, <repo>, <reference project>
```

Every rewrite of the description gets a comment: what changed and why, in 3–6 lines.

## Code comment

Only the *why* the code cannot say: the failure this prevents, the alternative that was rejected, the boundary being enforced. Prose, in the language of the file. Never restate what the next line does.

```ts
/**
 * <Why this exists: the situation that goes wrong without it, concretely.>
 *
 * <The rule, stated so a reader can apply it to the next case.>
 */
```

Good: "Nome combinado por acaso é frágil: escrever `lms.content_sources` no lugar de `lms.content_source` dá exatamente a mesma tela — o plugin fica esperando — e quem escreveu não tem como saber se errou. Então `lms.` é reservado."

Bad: "Validates the type name."
