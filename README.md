# ai-agent-skills

Personal collection of [Claude Code](https://claude.com/claude-code) agent skills, packaged as a plugin marketplace.

## Install

```
/plugin marketplace add renatoaug/ai-agent-skills
/plugin install <plugin>@ai-agent-skills
```

## Skills

| Plugin | Skill | What it does |
| ------ | ----- | ------------ |
| `showcase` | `showcase` | Generates a presentation of software you built — a client delivery, a release, an open-source project — as a narrated video tour, a live-demo script, or a slide deck. |

## Layout

Each plugin lives under `plugins/<name>/` with its own `.claude-plugin/plugin.json` and `skills/` directory. The marketplace manifest is `.claude-plugin/marketplace.json`.
