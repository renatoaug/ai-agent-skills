# ai-agent-skills

Personal collection of [Claude Code](https://claude.com/claude-code) agent skills.

## Install

Each skill is a directory under `skills/`. To use one, link (or copy) it into your local skills directory:

```bash
git clone git@github.com:renatoaug/ai-agent-skills.git
ln -s "$(pwd)/ai-agent-skills/skills/showcase" ~/.claude/skills/showcase
```

Claude Code picks it up on the next session; invoke it with `/showcase` or just describe the task.

## Skills

| Skill | What it does |
| ----- | ------------ |
| [`showcase`](skills/showcase/SKILL.md) | Generates a presentation of software you built — a client delivery, a release, an open-source project — as a narrated video tour, a live-demo script, or a slide deck. |
