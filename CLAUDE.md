# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

For what this repo is, its layout, the current skill index, and pipeline progress, see [README.md](README.md) — don't duplicate that here; keep this file to conventions and constraints for actually doing the work.

## Directory conventions

- Every skill lives at `skills/<name>/` (kebab-case, matching the `name` in its `SKILL.md` frontmatter), following the standard anatomy: `SKILL.md` + optional `scripts/`, `references/`, `assets/`. Never create a skill directory at the repo root.
- Keep `SKILL.md` under ~500 lines (roughly 3000 Chinese characters). Past that, split into two skills — long SKILL.md files measurably hurt execution accuracy. Push large reference material into `references/`, executable helpers into `scripts/`.
- **Self-authored skills** get a `kevin-` prefix (e.g. `kevin-book-research-planning`), so they're recognizable at a glance against mirrored/third-party skills. Skills belonging to the same pipeline additionally share a secondary prefix so they sort together in the flat `skills/` folder: `kevin-book-*`, `kevin-wechat-*`. A new, unrelated project gets its own secondary prefix the same way rather than overloading an existing one.
- **Mirrored skills keep their real name, no `kevin-` prefix** — `write-article/`, `newsletter-digest/`, `architecture-diagram/` must match their canonical directory name exactly, or the mental link back to the real copy breaks.
- **Don't vendor a third-party skill that depends on files fetched at install time** (scripts/references pulled dynamically via `npx skills add`, not present even at the canonical source). Reference it as an external dependency instead — see how `kevin-wechat-skill/README.md` handles `fireworks-tech-graph` / `excalidraw-diagram-generator`. Only mirror a skill if what's at the source is actually complete.

## Language

Every skill's output content (SKILL.md prose, generated articles/briefs/notes, user-facing messages) is Chinese by default. Switch to English, or mix in English terms, only when there's a functional reason to: code, commands, file paths, API/library names, proper nouns without a natural Chinese term, or a direct quote from an English source. Don't default to English scaffolding (headers, explanations, boilerplate) just because it's faster to draft — that's not a functional reason.

## Syncing a mirrored skill

Canonical homes: `~/.claude/skills/<name>` for skills, `~/Documents/Kevin-Brain/raw/publishing-pipeline` for the shared publish scripts. Both are readable directly from this environment — confirm with `ls`/`Read` before assuming a mirror is stale or incomplete. To update a mirror, diff the two copies manually and re-copy changed files; there's no automated drift detection, and the scripts in `publishing-pipeline/` still only actually run from the canonical vault (hardcoded relative paths to its `articles/`, `assets/`, `.venv`) — the copy here is for version history, not independent execution.

When mirroring, deliberately exclude: real credentials (`wechat.yaml` — only `wechat.yaml.example` is tracked, real file is gitignored), generated/local artifacts (`stats.json`, `_output/`, `.venv/`), and content that's personal-but-unrelated to the skill's actual purpose (e.g. a PostgreSQL-course reading list found inside `publishing-pipeline/` — out of scope for publish mechanics, removed).

## Design principles

Every self-authored skill should hold to these 5 (source: an external Chinese-language Agent Skills guide — not vendored in this repo, third-party copyrighted content):

1. **先确认再动手 (confirm before acting)** — for anything with real decision or redo cost, present options and get sign-off before the expensive step. Don't let a skill pick a direction and run pages deep before the user can object.
2. **边做边存 (save as you go)** — long-running skills (research, multi-step generation) write results to disk incrementally per stage, not all at once at the end. Sessions get cut off; incremental saves mean nothing is lost.
3. **模块化可组合 (modular and composable)** — one skill does one thing. Don't bundle a whole pipeline into one SKILL.md; split into small skills that chain Unix-pipe style.
4. **给选择不给答案 (offer choices, not answers)** — present ~3 options rather than one finished answer, so the output carries the user's judgment, not just the AI's. This is also the main lever against generic "AI-flavored" output.
5. **放大你，而不是替代你 (amplify, don't replace)** — flag issues / propose edits, let the user decide. Shape is input → proposal → human decision → execution → human confirmation, not input → output with no human in the loop.

Self-authored skills should also hold to the concreteness bar the mirrored production skills demonstrate: real positive **and** negative examples (not abstract templates), hard constraints stated as rules rather than preferences, and anti-rationalization tables that name a specific shortcut and rebut it (e.g. `write-article`'s voice rules, `fireworks-tech-graph`'s 反合理化 table).

## Building a new skill

Use the `skill-creator` skill rather than authoring freehand — it defines the SKILL.md structure, eval/test workflow, and description-optimization process this project follows. Apply the 5 principles above while drafting. If `skill-creator` is genuinely unavailable, draft freehand against the same anatomy (frontmatter with `name`/`description`, numbered steps, explicit boundaries section) and principles instead of skipping structure.

## Open follow-ups

- `kevin-wechat-skill/`'s genericization judgment calls haven't been reviewed by the user yet: didn't vendor the 3 diagram skills as peer-dependencies instead, consolidated shared scripts into a new `publish` sub-skill that didn't exist in the original system, softened `newsletter-digest`'s specific incident citations into general language, wrote the "首次使用前必做" callouts from scratch. Worth a skim to confirm nothing Kevin-specific leaked through and nothing important got over-genericized.
- `kevin-book-research-planning` has never been registered as an invokable skill after being drafted — still just a file on disk.
- `kevin-wechat-proofreading` (new: AI-flavor + detail pass, deliberately not re-checking facts) was added to run after `write-article` drafts. `write-article`'s own SKILL.md — mirrored, real production skill, canonical source is `~/.claude/skills/write-article` — doesn't reference it yet. Deliberately not edited here per the mirroring convention above; decide with the user whether the real source should point to it, and if so make that change at the source, not in the mirror.
