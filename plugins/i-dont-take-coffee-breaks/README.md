# I don't take coffee breaks ☕

> "Next step: phase 3, the real widget, which takes about 1–2 weeks."
>
> *— Claude, thirty minutes before finishing phase 3*

Coding agents estimate time like a human team: sprints, working days, "about two weeks". They learned it from tickets and blog posts written by people who type, sit in meetings, wait on review and switch context. The agent does none of that, so the number is off by an order of magnitude, and sometimes it becomes the agent's excuse to stop or split work that fits in one session.

This plugin makes Claude estimate in **agent time**: a range in minutes for what it will do itself, and, on a line of its own, **your part**, the things only you can do (testing, deciding, waiting on CI or review).

![Same question, without and with the plugin](demo.gif)

Same prompt, two real answers: without the plugin, "4–5 working days"; with it, "60–100 min of my time", with checkpoints and your part named apart.

## Install

Inside Claude Code:

```
/plugin install i-dont-take-coffee-breaks --marketplace renatoaug/ai-agent-skills
```

Or in two steps on older versions:

```
/plugin marketplace add renatoaug/ai-agent-skills
/plugin install i-dont-take-coffee-breaks@ai-agent-skills
```

Start a new session. That's it.

## How it works

A skill alone only loads when the model decides it applies, and a time estimate usually shows up in the middle of some other answer, where nothing triggers it. So the plugin ships two pieces:

| Piece | What it does |
|---|---|
| [`SKILL.md`](skills/i-dont-take-coffee-breaks/SKILL.md) | The rules: how to size the work, what counts as your part, the format, what not to do. |
| [`hooks/session-start.mjs`](hooks/session-start.mjs) | A `SessionStart` hook that loads those rules at the start of every session (startup, resume, clear, compact), so they apply to every duration Claude writes. |

The hook only reads the skill file and prints it. It makes no network calls and never blocks the session: on any error it exits quietly.

## The rules, in short

- **Agent time, as a range.** Minutes or hours for the work Claude does itself. Never days or weeks, unless the work is blocked on something external (a store review, a vendor, data that doesn't exist yet).
- **Size the work, not the keywords.** "Auth" can be a one-line fix. Claude reads enough code to know the scope, then places it on a scale:

  | Category | Looks like | Agent time |
  |---|---|---|
  | Trivial | typo, constant, config value | 2–6 min |
  | Simple | bug with a known cause, one function | 5–12 min |
  | Medium | feature touching 3–8 files, an endpoint | 10–25 min |
  | Complex | UI + data + wiring, a new module with tests | 25–60 min |
  | Major | codebase-wide migration, a rewrite | 1–3 h |

- **Measure, don't guess.** If the last phase took 25 minutes in this session, a similar one takes about 25 minutes. Git timestamps beat any table.
- **Name your part.** That's usually the real schedule: testing on a device, decisions, CI, review, long-running jobs.
- **No excuses.** A big estimate is not a reason to stop, defer, or ask permission to keep going.

## Turn it off

For a moment: `/plugin` → disable `i-dont-take-coffee-breaks`. For good: `/plugin uninstall i-dont-take-coffee-breaks@ai-agent-skills`.

## Recording the demo

The GIF replays real `claude -p` answers, cut down to the estimate. The full prompt described phase 3 (live data, session and week bars, a status dot, a background reader thread, an expanded size, a pet-only mode and a tray icon) and asked for the "Next step" line of a status update. The answers were captured beforehand and replayed with VHS so the GIF skips the wait. The run without the plugin passed `--settings` with `"enabledPlugins": {"i-dont-take-coffee-breaks@ai-agent-skills": false}`. Answers vary between runs: three runs without the plugin gave "2 working days", "3–4 days" and "4–5 working days"; two runs with it gave "45–90 min" and "60–100 min".
