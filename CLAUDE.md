# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

This repository's goal is to create Claude Skills for ongoing/long-term use (per the user: "创建使用的skill，长期维护" — create skills for actual use, maintained long-term). It is a skills workspace: every skill lives under `skills/<name>/` following the standard Skill anatomy (`SKILL.md` + optional `scripts/`, `references/`, `assets/`), built and iterated using the `skill-creator` skill's draft → test → review → improve loop. Directory layout follows the reference project [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills): all skills nested one level under `skills/`, flat (no category subfolders — categorize via the index table below and via naming prefix), with repo-level material (this file, the design-principles PDF) staying at the root instead of mixed in with skill directories.

Current contents:

- `Agent-Skills-Complete-Guide-zh-v260411.pdf` — a Chinese-language reference guide on Agent Skills (花叔's 橙皮书). Source of the 5 design principles below and of a 6-pattern taxonomy (检查清单型/Checklist, 多方案选择型/Options, 多阶段流水线型/Pipeline, 外部API集成型/Integration, 多Agent协作型/Swarm, 思维蒸馏型/Distillation) used to classify new skills before drafting them.
- `skills/kevin-book-research-planning/` — first skill. Stage 1 of a planned 5-stage book-writing pipeline (Pipeline pattern): 调研与规划 → 内容写作 → 构建与组装 → 版本管理 → 多格式输出. Turns a book idea into a confirmed `PROJECT.md` (chapter structure, status per chapter) plus per-chapter research notes under `research/`, ready for a future "内容写作" skill to consume. Only stage 1 has been built so far — build order is deliberately one-at-a-time: use each stage in anger before designing the next, rather than scaffolding all 5 up front.
- `skills/kevin-wechat-topic-gen/`, `skills/kevin-wechat-research/` — the two upstream stages of a WeChat-article workflow that are genuinely missing from the user's real system (see `write-article/` below): 选题生成 (Options pattern) and 深度调研 (save-as-you-go). Their output (a chosen topic direction, a research brief) is meant to feed into `write-article`, which takes over from drafting onward. Not yet validated against a real article.
- `skills/write-article/` — **mirrored copy of the user's real, already-in-production article-writing skill**, whose canonical home is `~/.claude/skills/write-article` (a protected path this repo/session cannot mount directly — see "Working here" for the sync process). This is not something authored in this repo; it's git-tracked here so the user gets version history that `~/.claude/skills` itself doesn't have. Defines Kevin's actual voice rules, 3 article-structure branches, hook patterns, fact-checking hard-line, and a real publish pipeline (`check.py`/`publish.py` under `~/Documents/Kevin-Brain/raw/publishing-pipeline`, outside this repo).
- `skills/newsletter-digest/` — mirrored. Handles compiled/digest articles (tech newsletters, link roundups) — explicitly **out of scope** for `write-article`, which only covers Kevin's original writing. 5-stage internal pipeline (extract → independent-subagent fact-recheck → fixed layout → diagrams → automated check.py retry loop). The independent-subagent recheck step is a strong real-world example of the "amplify don't replace" + verification principles: it exists because same-model self-review was proven (PG Weekly #656) to miss real errors that a fresh, source-blind subagent catches.
- `skills/fireworks-tech-graph/` — mirrored, **incomplete**: only `SKILL.md` copied, the `scripts/` and `references/style-N.md` files it references weren't present at `~/.claude/skills/fireworks-tech-graph` (likely resolved via its own `npx skills add` install path rather than vendored locally). Default diagram tool referenced by `write-article`. Notably has an explicit 反合理化 (anti-rationalization) table at the top — "语法验证通过就行" → 反驳: 语法正确≠逻辑正确, etc. — worth reusing as a pattern in future self-authored skills.
- `skills/architecture-diagram/` — mirrored, complete (`resources/template.html` included). Dark-themed HTML+SVG architecture diagrams, used for more complex system/infra diagrams than `fireworks-tech-graph`'s default style handles.
- `skills/excalidraw-diagram-generator/` — mirrored, **incomplete**: only `SKILL.md` copied, the `references/`, `templates/`, and `scripts/` it references weren't present in the source either. Generates `.excalidraw` JSON files for hand-drawn-style diagrams.
- `.serena/` — Serena MCP project configuration (gitignored).
- `.claude/` — Claude Code local settings (gitignored).

**Retired:** `kevin-wechat-proofreading`, `kevin-wechat-image`, `kevin-wechat-publish-check` were scaffolded early in this repo's life as a generic, from-scratch WeChat pipeline, before discovering that `write-article` already covers the same ground far more specifically (real voice rules instead of generic AI-tone checklist; local SVG + `rsvg-convert` instead of generic image-API-and-host; a real Python check/publish pipeline instead of a generic checklist). Removed via `git rm` rather than left to rot as a parallel, conflicting system — still recoverable from git history (see the "Retire generic proofreading/image/publish-check skills..." commit) if ever needed.

### Skills index (quick scan)

| Skill | Category | Type | Status |
|---|---|---|---|
| `kevin-book-research-planning` | Book pipeline | self-authored | built, unvalidated |
| `kevin-wechat-topic-gen` | WeChat pipeline | self-authored | built, unvalidated |
| `kevin-wechat-research` | WeChat pipeline | self-authored | built, unvalidated |
| `write-article` | WeChat pipeline | mirrored | real, in production |
| `newsletter-digest` | WeChat pipeline | mirrored | real, in production |
| `fireworks-tech-graph` | WeChat pipeline (diagrams) | mirrored, incomplete | real, in production |
| `architecture-diagram` | WeChat pipeline (diagrams) | mirrored, complete | real, in production |
| `excalidraw-diagram-generator` | WeChat pipeline (diagrams) | mirrored, incomplete | real, in production |

All paths are `skills/<name>/`.

### Future scope

The user has more projects beyond book-writing and WeChat that will eventually need skills or plugins here — this repo isn't scoped to just these two pipelines long-term. When a new unrelated project starts, give it its own secondary prefix the same way (`kevin-<project>-*`) rather than overloading `kevin-book-*` or `kevin-wechat-*`.

**Why this repo restarted from scratch on skills instead of reusing whatever existed before:** per the user, past attempts had two failure modes — the AI didn't reliably follow the skill (compliance), and even when followed, output quality was poor. The mirrored real skills above (especially `write-article`'s hard constraints/反例/anchor-articles and `fireworks-tech-graph`'s 反合理化 table) are evidence of what actually works: concrete positive AND negative examples, hard constraints stated as rules not preferences, and anti-rationalization tables that name the specific shortcut and rebut it — not generic "write good content" advice. Self-authored skills in this repo should hold to that same concreteness bar, not just the lighter anatomy used so far.

Git was initialized once the first skill landed (see "Working here" below); history starts from the `book-research-planning` commit.

**Note on tooling:** the `skill-creator` skill referenced below is a Claude Code concept and was not available as an invocable tool when `book-research-planning` was authored (in a Cowork session). It was drafted directly against the anatomy and 5 principles from the guide instead. If `skill-creator` becomes available in a given session, prefer it per the instruction below; otherwise draft freehand but hold to the same structure (frontmatter with `name`/`description`, numbered steps, explicit boundaries section) and principles.

## Design principles (from `Agent-Skills-Complete-Guide-zh-v260411.pdf`)

Every skill authored in this repo should follow these 5 principles (source: guide's "5个设计原则" section):

1. **Confirm before acting (先确认再动手)** — For anything with real decisions or cost to redo, have the skill present options and get user sign-off before doing the expensive step. Don't let it pick a direction and run 2000 words deep before the user can object — that work is wasted and pollutes context once it's wrong.
2. **Save as you go (边做边存)** — In long-running skills (research, multi-step generation), write results to disk incrementally as each stage/batch completes, not all at once at the end. Sessions can be cut off (network, token limits, closed tab); incremental saves mean nothing is lost.
3. **Modular and composable (模块化可组合)** — One skill does one thing. Don't bundle a whole pipeline (e.g. "topic selection + research + draft + review + images") into a single SKILL.md — it bloats context and kills flexibility. Split into small skills that can be run independently or chained, Unix-pipe style.
4. **Offer choices, not answers (给选择不给答案)** — Prefer presenting ~3 options over handing back one finished answer. This keeps the user making the real decisions, so the output carries their judgment, not just the AI's — and it's also the main lever for avoiding generic "AI-flavored" output. The skill is an advisor, not the decision-maker.
5. **Amplify, don't replace (放大你，而不是替代你)** — A skill should flag issues / propose edits and let the user decide what to accept, rather than auto-applying changes. The shape is input → proposal → human decision → execution → human confirmation, not input → output with no human in the loop. That's what distinguishes a skill from a plain automation script.

**Maintenance guidance from the same guide:**
- Skills evolve with use — expect to revise a skill's steps/checklist many times after real usage surfaces gaps. Track skill changes with git so you can see how a skill matured and roll back a version that regresses.
- If a skill's SKILL.md grows past ~3000 Chinese characters (roughly analogous to the ~500-line guidance below), split it into two — long skills measurably hurt the AI's execution accuracy. Short and focused beats long and comprehensive.

## Working here

- When asked to build a new skill, use the `skill-creator` skill rather than freehand authoring — it defines the SKILL.md structure, eval/test workflow, and description-optimization process this project should follow, and apply the 5 principles above while drafting.
- Each skill gets its own directory under `skills/` (kebab-case, matching its `name` in SKILL.md frontmatter) — e.g. `skills/kevin-book-research-planning/SKILL.md`. Don't create skill directories at the repo root; that was the layout before this repo adopted the addyosmani/agent-skills convention, and any repo-root skill folder found from before that point should be moved under `skills/` rather than left where it was. Keep SKILL.md under ~500 lines; push large reference material into `references/` and executable helpers into `scripts/`.
- **Naming convention:** this only applies to skills *authored in this repo*. Every self-authored skill is prefixed `kevin-` (e.g. `kevin-book-research-planning`), matching the guide's own advice to give personally-authored skills a consistent personal prefix (花叔 uses `huashu-`) — this makes them recognizable at a glance and distinct from official/third-party skills (`docx`, `pdf`, `pptx`, etc.) once the skill list grows. Skills belonging to the same pipeline additionally share a secondary prefix so that pipeline's stages sort and scan together, independent of unrelated pipelines: `kevin-book-*` for the book-writing pipeline, `kevin-wechat-*` for the WeChat-article pipeline (currently just `kevin-wechat-topic-gen` and `kevin-wechat-research` — see "Retired" above for why it's not the full 5 stages).
- **Mirrored skills keep their real name, no `kevin-` prefix.** `write-article/` (and any future mirror of a skill living in `~/.claude/skills/`) must match its directory name exactly — renaming the mirror would break the mental link back to the canonical copy the user actually invokes day to day. Don't "clean up" a mirrored skill's name to fit the convention above.
- **Syncing a mirrored skill:** `~/.claude/skills/` is a protected host path — no tool in a Cowork session can mount or read it directly, permission dialogs don't apply, this is a hard block. To bring a real skill under version control here, ask the user to run `cp -r ~/.claude/skills/<name> ~/Documents/GitHub/skills_creator_project/skills/<name>` themselves (note the `skills/` in the destination), then read/commit it from this side. There's no automated way to detect drift between the mirror and the canonical copy — re-copy and diff manually when the user has edited the real one.
- Put this repo under git once the first skill is added, and commit as skills iterate — the guide's maintenance advice above depends on having history to look back through.
- Once the first skill(s) land, update this CLAUDE.md with the actual directory layout and any repo-wide conventions that emerge (e.g., shared script libraries, a common test/eval runner) — don't leave this section describing an empty repo once it isn't one.
