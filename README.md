# agent-skills

我自己长期维护的 Claude Skills 仓库——不是写着玩的示例，是实际会用、会迭代、会踩坑修正的工作流。

## 这是什么

目标很直接：**创建使用的 skill，长期维护**。每个 skill 按标准 Skill 结构（`SKILL.md` + 可选的 `scripts/`、`references/`、`assets/`）组织，用 draft → test → review → improve 的循环打磨，而不是写一次就扔在那不管。

目录布局参照 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)：所有 skill 平铺在 `skills/` 下一层，不分类别子目录，靠命名前缀和下面的索引表分类。

```
agent-skills/
├── skills/                    # 每个 skill 一个目录
│   ├── kevin-book-research-planning/
│   ├── kevin-wechat-topic-gen/
│   ├── kevin-wechat-research/
│   ├── kevin-wechat-proofreading/
│   ├── kevin-wechat-write-article/       # 调用名仍是 write-article，见下方说明
│   ├── kevin-wechat-newsletter-digest/   # 调用名仍是 newsletter-digest
│   └── kevin-wechat-architecture-diagram/ # 调用名仍是 architecture-diagram
├── kevin-wechat-skill/         # 公众号几个 skill 泛化打包后的可分发版本，这个仓库自己拥有、自己改
└── publishing-pipeline/        # write-article / newsletter-digest 共用的发布脚本（check.py / publish.py 等），跟着 write-article 一起从源头同步
```

设计原则和分类法参考了花叔的《Agent Skills 使用手册》（未收录进本仓库——第三方版权内容，不适合放公开仓库）。

`skills/` 下所有公众号相关 skill 目录都带 `kevin-wechat-` 前缀，包括跟着源头同步的那 3 个——这样整条流水线在目录里排在一起，不用只靠索引表分辨。但这 3 个内部的 SKILL.md 文件本身（frontmatter 的 `name` 字段、脚本调用等）**不改**，仍然是 `write-article`/`newsletter-digest`/`architecture-diagram`，因为这才是它们的真实调用名，改了就跟源头对不上、也没法触发。也就是说：**目录名管排序和归类，SKILL.md 里的 `name` 管实际调用**，这两件事是分开的，别搞混。

## 设计原则

每个自研 skill 都要过一遍这五条：

1. **先确认再动手**——有真实决策成本的地方，让 skill 先给方案、等用户拍板，别自己埋头跑出两千字才发现方向错了。
2. **边做边存**——长流程（调研、多步生成）每完成一个阶段就落盘，别攒到最后一次性写，防止中途断掉丢东西。
3. **模块化可组合**——一个 skill 只做一件事。不要把整条流水线塞进一个 SKILL.md，拆开才能像 Unix 管道一样单独用或串起来用。
4. **给选择不给答案**——优先给 3 个左右的方案而不是一个"成品"，让用户的判断留在输出里，也是避免"AI 味"的关键手段。
5. **放大你，而不是替代你**——skill 提议、人决定、再执行、再确认，不是输入直接产出没人看过的结果。

维护上的补充：skill 会随实际使用反复改，用 git 记录每次修订，方便回滚到没有回归的版本；SKILL.md 超过约 3000 字就该拆成两个——长而全面反而会降低执行准确率，短而聚焦更好。

## 当前 skill 索引

| 目录名 | 调用名 | 干什么用的 | 状态 | 改哪里 |
|---|---|---|---|---|
| `kevin-book-research-planning` | 同左 | 写书流水线第1阶段：把模糊的书想法整理成确认过的章节结构 + 逐章调研笔记 | 已建，未验证，未注册为可调用 skill | 这个仓库里直接改 |
| `kevin-wechat-topic-gen` | 同左 | 公众号选题生成：给一个话题，产出3-4个真正有差异的方向，带优劣分析，交用户选 | 已建，未验证 | 这个仓库里直接改 |
| `kevin-wechat-research` | 同左 | 公众号深度调研：选题定了之后按信息源优先级搜索，边搜边存，产出结构化简报 | 已建，未验证 | 这个仓库里直接改 |
| `kevin-wechat-proofreading` | 同左 | 初稿写完后的AI味+细节审校，不查事实（write-article已管），独立子agent跑 | 已建，未验证 | 这个仓库里直接改 |
| `kevin-wechat-write-article` | `write-article` | Kevin原创文章写作：声音规则 + 3种结构分支 + 发布前检查清单 | **生产在用** | 源头 `~/.claude/skills/write-article` 改，改完手动同步过来 |
| `kevin-wechat-newsletter-digest` | `newsletter-digest` | 编译/汇总类文章（技术周刊、链接合集）处理，独立子agent核实取代同模型自查 | **生产在用** | 同上，源头改 |
| `kevin-wechat-architecture-diagram` | `architecture-diagram` | 复杂系统架构图，暗色风格 HTML+SVG | 生产在用，第三方（Cocoon AI） | 不改，`npx skills add` 装最新版 |

`write-article` 默认还会用到两个配图 skill——`fireworks-tech-graph`、`excalidraw-diagram-generator`。这两个本身是通过 `npx skills add` 从外部仓库安装的第三方包（脚本和参考资料在安装时动态拉取，源头本地也不存在完整文件），不适合在这个仓库里放"半个镜像"，所以不 vendor，需要时自己装：

```bash
npx skills add yizhiyanhua-ai/fireworks-tech-graph
# excalidraw-diagram-generator 按你实际用的安装源装
```

## 流水线进度

**写书流水线**（自研，未验证）—— 5 个阶段，1 个建好：

- [x] 调研与规划 → `kevin-book-research-planning`
- [ ] 内容写作
- [ ] 构建与组装
- [ ] 版本管理
- [ ] 多格式输出

**公众号流水线**——上游自研，下游就是已经在跑的真实生产系统，不需要重建：

- [x] 选题生成 → `kevin-wechat-topic-gen`
- [x] 深度调研 → `kevin-wechat-research`
- [x] 写作 → `write-article`
- [x] AI味+细节审校 → `kevin-wechat-proofreading`（只管AI味和细节，事实核查是`write-article`自己的事，独立子agent跑）
- [x] 配图 → 发布 → 3 个配图 skill / `newsletter-digest`（编译类走这个而不是`write-article`）

**公众号流水线打包分享**（独立分支，目标是发布成通用包）：

- [x] 打包 `kevin-wechat-skill/`：泛化后的 topic-gen / research / write-article / newsletter-digest + 新增的 publish 子 skill
- [ ] 端到端跑通全链路（topic-gen → research → write-article → publish）
- [ ] 验证跨工具安装（Codex / Gemini CLI，不只 Claude）
- [ ] 决定独立开仓库还是留在这个仓库下，然后正式发布

## 怎么改一个 skill

**新建**：用 `skill-creator` skill 起草，别手写——它定义好了 SKILL.md 结构、eval/test 流程、description 优化方法。新 skill 放在 `skills/<name>/`，kebab-case，跟 frontmatter 里的 `name` 对齐。自己在这个仓库里从零写的一律 `kevin-` 前缀；同一条流水线的再共享二级前缀。SKILL.md 控制在 500 行以内，大参考材料放 `references/`，可执行脚本放 `scripts/`。

**改一个跟着源头同步的 skill**（`write-article`、`newsletter-digest`、`architecture-diagram`）：先去源头（`~/.claude/skills/<name>`）改，改完手动 `cp -r` 过来这个仓库对应的 `skills/kevin-wechat-<name>/` 目录再提交——**目录名要重新套一层 `kevin-wechat-` 前缀，但 `cp` 过来的 SKILL.md 内容本身（包括 frontmatter 的 `name` 字段）原样不动，不要跟着改名**。不能反过来在这个仓库里单方面改——那边才是天天在用的权威版本，这边的副本改了不会生效，还会造成两边不一致。没有自动检测漂移的机制，靠人工重新对比。

## License

MIT
