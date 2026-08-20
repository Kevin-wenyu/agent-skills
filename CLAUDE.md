# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

For what this repo is, its layout, the current skill index, and pipeline progress, see [README.md](README.md) — don't duplicate that here; keep this file to conventions and constraints for actually doing the work.

## Directory conventions

- Every pipeline gets its own top-level folder (`wechat/`, `book/`), and every skill lives at `<pipeline>/<dir-name>/` (kebab-case) inside it, following the standard anatomy: `SKILL.md` + optional `scripts/`, `references/`, `assets/`. Never create a skill directory at the repo root, and never create a new skill outside a pipeline folder.
- Keep `SKILL.md` under ~500 lines (roughly 3000 Chinese characters). Past that, split into two skills — long SKILL.md files measurably hurt execution accuracy. Push large reference material into `references/`, executable helpers into `scripts/`.
- **Directory name and SKILL.md frontmatter `name` are the same value for every skill** — e.g. `wechat/proofreading/SKILL.md` has `name: proofreading`. This repo used to prefix every directory with its pipeline name (`wechat-proofreading`) to keep a flat `skills/` folder sorted; on 2026-08-20 the flat folder was split into one top-level folder per pipeline (see below), which made the prefix redundant — the containing folder now says which pipeline a skill belongs to, so the name inside it doesn't need to repeat that. (Earlier history, in case a similar problem resurfaces: before the per-pipeline-folder split, the prefix itself went through a "only self-authored skills get it" → "every pipeline member gets it" → "drop the `kevin-` ownership layer, keep only the pipeline-functional part" evolution, each step fixing a real grouping/sorting problem in the old flat layout. That whole prefix mechanism no longer applies now that pipelines are physically separated into their own folders.)
- **For skills synced from a real source (`write-article`, `newsletter-digest`, `architecture-diagram`, all under `wechat/`), the directory name happens to equal the SKILL.md frontmatter `name`** — but treat that as coincidental, not guaranteed: the frontmatter `name` is the real invocation name and must match the canonical source verbatim (`~/.claude/skills/<name>`) or it breaks, while the directory name is free to be whatever fits this repo's layout. If a future pipeline reorganization would require renaming one of these directories in a way that no longer matches its frontmatter `name`, that's fine — rename the directory, never the frontmatter `name` of a mirrored skill.
- **Don't vendor a third-party skill that depends on files fetched at install time** (scripts/references pulled dynamically via `npx skills add`, not present even at the canonical source). Reference it as an external dependency instead — see how README's skill-index section handles `fireworks-tech-graph` / `excalidraw-diagram-generator`. Only mirror a skill if what's at the source is actually complete.
- **A skill file existing in this repo does not mean Claude Code can discover or trigger it.** Self-authored skills here are source files only — nothing in this repo auto-installs them to `.claude/skills/` (project) or `~/.claude/skills/` (personal), the two places Claude Code actually scans. Confirmed 2026-08-20: none of the self-authored skills were installed anywhere. Don't assume a skill is "live" just because its SKILL.md exists and looks finished — check the README's skill index status column, and see README's "怎么装一个 skill" for the install step (symlink, not copy, and point at the main checkout, not a worktree).

## Language

Every skill's output content (SKILL.md prose, generated articles/briefs/notes, user-facing messages) is Chinese by default. Switch to English, or mix in English terms, only when there's a functional reason to: code, commands, file paths, API/library names, proper nouns without a natural Chinese term, or a direct quote from an English source. Don't default to English scaffolding (headers, explanations, boilerplate) just because it's faster to draft — that's not a functional reason.

## Syncing a mirrored skill

Canonical homes: `~/.claude/skills/<name>` for skills, `~/Documents/Kevin-Brain/raw/publishing-pipeline` for the shared publish scripts. Both are readable directly from this environment — confirm with `ls`/`Read` before assuming a mirror is stale or incomplete. To update a mirror, diff the two copies manually and re-copy changed files into `wechat/<name>/` (see "Directory conventions" above), leaving the copied SKILL.md content itself, including its frontmatter `name`, untouched. There's no automated drift detection, and the scripts in `publishing-pipeline/` still only actually run from the canonical vault (hardcoded relative paths to its `articles/`, `assets/`, `.venv`) — the copy here is for version history, not independent execution.

When mirroring, deliberately exclude: real credentials (`wechat.yaml` — only `wechat.yaml.example` is tracked, real file is gitignored), generated/local artifacts (`stats.json`, `_output/`, `.venv/`), and content that's personal-but-unrelated to the skill's actual purpose (e.g. a PostgreSQL-course reading list found inside `publishing-pipeline/` — out of scope for publish mechanics, removed).

## Design principles

Every self-authored skill should hold to these 5 (source: an external Chinese-language Agent Skills guide — not vendored in this repo, third-party copyrighted content):

1. **先确认再动手 (confirm before acting)** — for anything with real decision or redo cost, present options and get sign-off before the expensive step. Don't let a skill pick a direction and run pages deep before the user can object.
2. **边做边存 (save as you go)** — long-running skills (research, multi-step generation) write results to disk incrementally per stage, not all at once at the end. Sessions get cut off; incremental saves mean nothing is lost.
3. **模块化可组合 (modular and composable)** — one skill does one thing. Don't bundle a whole pipeline into one SKILL.md; split into small skills that chain Unix-pipe style.
4. **给选择不给答案 (offer choices, not answers)** — present ~3 options rather than one finished answer, so the output carries the user's judgment, not just the AI's. This is also the main lever against generic "AI-flavored" output.
5. **放大你，而不是替代你 (amplify, don't replace)** — flag issues / propose edits, let the user decide. Shape is input → proposal → human decision → execution → human confirmation, not input → output with no human in the loop.

Self-authored skills should also hold to the concreteness bar the mirrored production skills demonstrate: real positive **and** negative examples (not abstract templates), hard constraints stated as rules rather than preferences, and anti-rationalization tables that name a specific shortcut and rebut it (e.g. `write-article`'s voice rules, `fireworks-tech-graph`'s 反合理化 table).

## Verification: default to independent review, but verify the reviewer too

For anything independently verifiable — mechanical checks (counting a pattern, checking a paragraph length), or checking a quoted claim against its source — default to spinning up an independent subagent to review, without waiting to be asked. Proven twice in one session (`wechat/proofreading` catching a referential-clarity bug; an ad hoc review agent catching a real footnote-precision issue) to reliably catch what the same context that produced the content can't see in itself.

This is not a full solution, and don't treat it as one. The same session also had the independent reviewer fabricate a finding — claim a source said something it didn't — that only got caught because it was re-verified against the primary source directly. Two distinct failure modes, both need guarding against separately: the *author* context misses its own errors (independent review fixes this), and the *reviewer* context can also misreport what it read (only re-verification against the primary source fixes this — a second AI opinion isn't ground truth just because it's independent). For judgments that depend on the user's own domain authority (is this analogy actually accurate, is this deep enough), no amount of independent review substitutes for asking the user directly — an independent agent has the same blind spot the original author does there.

## Building a new skill

Use the `skill-creator` skill rather than authoring freehand — it defines the SKILL.md structure, eval/test workflow, and description-optimization process this project follows. Apply the 5 principles above while drafting. If `skill-creator` is genuinely unavailable, draft freehand against the same anatomy (frontmatter with `name`/`description`, numbered steps, explicit boundaries section) and principles instead of skipping structure.

## Open follow-ups

- None of the self-authored skills (`book/research-planning`, `wechat/topic-gen`, `wechat/research`, `wechat/deepen`, `wechat/proofreading`) are installed anywhere Claude Code discovers them — see the Directory Conventions bullet above. Kevin explicitly decided (2026-08-20) not to install `wechat/proofreading` yet, wanting real-article validation first; treat the others the same way unless told otherwise.
- `wechat/proofreading` (AI-flavor + detail pass, deliberately not re-checking facts) was added to run after `write-article` drafts. `write-article`'s own SKILL.md — mirrored, real production skill, canonical source is `~/.claude/skills/write-article` — doesn't reference it yet. Deliberately not edited here per the mirroring convention above; decide with the user whether the real source should point to it, and if so make that change at the source, not in the mirror.
