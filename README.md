# ai-agent-skills

Personal collection of [Claude Code](https://claude.com/claude-code) agent skills.

## Install

Each skill is a directory under `skills/`. To use one, link (or copy) it into your local skills directory:

```bash
git clone git@github.com:renatoaug/ai-agent-skills.git
ln -s "$(pwd)/ai-agent-skills/skills/showcase" ~/.claude/skills/showcase
```

Claude Code picks it up on the next session; invoke it with `/showcase` or just describe the task.

### Plugins

Skills under `plugins/` ship as Claude Code plugins from this repo's marketplace. Install one from inside Claude Code:

```
/plugin marketplace add renatoaug/ai-agent-skills
/plugin install i-dont-take-coffee-breaks@ai-agent-skills
```

`i-dont-take-coffee-breaks` loads its rules at the start of every session through a `SessionStart` hook, so they apply even when nothing in the conversation would trigger the skill. See [its README](plugins/i-dont-take-coffee-breaks/README.md) for a before/after demo.

## Skills

| Skill | What it does |
| ----- | ------------ |
| [`docs`](skills/docs/SKILL.md) | Writes and revises documentation for a cold reader — decision records, design notes, READMEs, author guides, doc-site pages, Linear cards and code comments — with a status on every claim and a mandatory consistency pass. |
| [`i-dont-take-coffee-breaks`](plugins/i-dont-take-coffee-breaks/skills/i-dont-take-coffee-breaks/SKILL.md) (plugin) | Sizes time estimates by how fast a coding agent actually works — a range in minutes for the agent, with the user's part (testing, decisions, external waits) named apart — instead of a human team's "1–2 weeks". |
| [`showcase`](skills/showcase/SKILL.md) | Generates a presentation of software you built — a client delivery, a release, an open-source project — as a narrated video tour, a live-demo script, or a slide deck. |
