---
name: i-dont-take-coffee-breaks
description: Size time estimates by how fast a coding agent actually works, not how long a human team would take. Use BEFORE writing any duration — "next step takes X", phase plans, roadmaps, "this is a big job", effort sizing, or deciding a task is too large to start now. Prevents "1-2 weeks" for work that ends in half an hour.
---

# I don't take coffee breaks

Your instinct for durations comes from human estimates: tickets, sprint plans, blog posts by people who type, sit in meetings, wait on review and switch context. You do none of that. Quoting those numbers misleads the user and, worse, hands you an excuse to stop or split work that fits in this session.

## The rule

Estimate in **agent time**: wall-clock minutes for you to do it here, as a range. Then, on its own line, the **user's part**: what only they can do and roughly how long.

Never write days or weeks for work you will do yourself, unless it is blocked on something external (an app store review, a vendor, a waiting period, data that does not exist yet).

## Sizing

Read enough of the code to know the scope, then pick the category by the work, not by keywords in the request ("auth" can be a one-line fix):

| Category | Looks like | Agent time |
|---|---|---|
| Trivial | typo, constant, config value, rename in one place | 2–6 min |
| Simple | a bug with a known cause, one function, one test | 5–12 min |
| Medium | a feature touching 3–8 files, an endpoint, a small refactor | 10–25 min |
| Complex | UI + data + wiring, cross-cutting change, a new module with tests | 25–60 min |
| Major | a migration across the codebase, a rewrite, several features at once | 1–3 h |

Add on top, only when present:

- **Unknown failure to debug**: +10–40 min. This is the one line that is honestly hard to predict; say so.
- **Slow feedback loop**: count the measured runtime of the build, test suite or pipeline per iteration.
- **Risky ground** (prod data, migrations, auth, payments): time for a backup, a dry run, or a check against real data.

Better than any table: **your own measurements from this session.** If the last phase took 25 minutes, a phase of similar size takes about 25 minutes. Check `git log --format='%ad %s'`, file mtimes or `date` instead of guessing.

Past ~3 hours of agent time the honest framing is "a few sessions", not "weeks".

## The user's part

This is usually the real schedule. Name it:

- Testing on a real device or in the running app
- Decisions only they can make
- External waits: CI, deploy, PR review, approval, third-party accounts
- Long-running jobs, at their measured runtime

## Format

Bad: "Next: phase 3, the real widget, which takes about 1–2 weeks."

Good: "Next: phase 3, the real widget. 30–50 min for me: compact size on real data first, then expanded, pet-only and tray. Your part: run it and check the look, ~10 min."

For anything Complex or bigger, show where the time goes (understand, build, test, verify) and propose checkpoints: a commit or a look from the user between phases.

## Don't

- Don't take a human estimate and divide it by some factor. Size the actual work.
- Don't use a big estimate as a reason to stop, defer, or ask permission to keep going. If it fits in the session and the user asked for it, do it.
- Don't pad to look safe, and don't give a single point. A range, plus the one thing that drives it: "20 min, or an hour if the API needs auth work".
