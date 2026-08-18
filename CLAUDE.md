# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

This repository's goal is to create Claude Skills for ongoing/long-term use (per the user: "创建使用的skill，长期维护" — create skills for actual use, maintained long-term). It is a skills workspace: each skill should live in its own directory following the standard Skill anatomy (`SKILL.md` + optional `scripts/`, `references/`, `assets/`), built and iterated using the `skill-creator` skill's draft → test → review → improve loop.

Current contents:

- `Agent-Skills-Complete-Guide-zh-v260411.pdf` — a Chinese-language reference guide on Agent Skills (花叔's 橙皮书). Source of the 5 design principles below and of a 6-pattern taxonomy (检查清单型/Checklist, 多方案选择型/Options, 多阶段流水线型/Pipeline, 外部API集成型/Integration, 多Agent协作型/Swarm, 思维蒸馏型/Distillation) used to classify new skills before drafting them.
- `kevin-book-research-planning/` — first skill. Stage 1 of a planned 5-stage book-writing pipeline (Pipeline pattern): 调研与规划 → 内容写作 → 构建与组装 → 版本管理 → 多格式输出. Turns a book idea into a confirmed `PROJECT.md` (chapter structure, status per chapter) plus per-chapter research notes under `research/`, ready for a future "内容写作" skill to consume. Only stage 1 has been built so far — build order is deliberately one-at-a-time: use each stage in anger before designing the next, rather than scaffolding all 5 up front.
- `kevin-wechat-topic-gen/` — second skill, first stage of a planned WeChat-article publishing workflow (separate from the book pipeline): 选题生成 → 深度调研 → 三遍审校 → 配图 (Options, then save-as-you-go research, then Checklist, then Options+Integration+Checklist combo — modeled on the 花叔 huashu-* examples in the guide, chapter 1 and chapter 9). Options pattern: given a rough topic, produces 3-4 genuinely different directions with title/angle/outline/effort estimate/honest pros-and-cons, and waits for the user to pick rather than choosing itself. Same one-at-a-time build order as the book pipeline — only this first stage exists; 个人素材匹配 and 跨平台分发 were considered but deferred until the core 4 are validated in use.
- `.serena/` — Serena MCP project configuration (gitignored).
- `.claude/` — Claude Code local settings (gitignored).

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
- Each skill gets its own top-level directory (kebab-case, matching its `name` in SKILL.md frontmatter). Keep SKILL.md under ~500 lines; push large reference material into `references/` and executable helpers into `scripts/`.
- **Naming convention:** every self-authored skill in this repo is prefixed `kevin-` (e.g. `kevin-book-research-planning`), matching the guide's own advice to give personally-authored skills a consistent personal prefix (花叔 uses `huashu-`) — this makes them recognizable at a glance and distinct from official/third-party skills (`docx`, `pdf`, `pptx`, etc.) once the skill list grows. Skills belonging to the same pipeline additionally share a secondary prefix so that pipeline's stages sort and scan together, independent of unrelated pipelines: `kevin-book-*` for the book-writing pipeline (`kevin-book-research-planning`, and future `kevin-book-writing`, `kevin-book-assembly`, `kevin-book-versioning`, `kevin-book-publish`), `kevin-wechat-*` for the WeChat-article pipeline (`kevin-wechat-topic-gen`, and future `kevin-wechat-research`, `kevin-wechat-proofreading`, `kevin-wechat-image`).
- Put this repo under git once the first skill is added, and commit as skills iterate — the guide's maintenance advice above depends on having history to look back through.
- Once the first skill(s) land, update this CLAUDE.md with the actual directory layout and any repo-wide conventions that emerge (e.g., shared script libraries, a common test/eval runner) — don't leave this section describing an empty repo once it isn't one.
