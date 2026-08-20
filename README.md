# agent-skills

我自己长期维护的 Claude Skills 仓库——不是写着玩的示例，是实际会用、会迭代、会踩坑修正的工作流。

## 这是什么

目标很直接：**创建使用的 skill，长期维护**。每个 skill 按标准 Skill 结构（`SKILL.md` + 可选的 `scripts/`、`references/`、`assets/`）组织，用 draft → test → review → improve 的循环打磨，而不是写一次就扔在那不管。

每条流水线一个独立的顶层文件夹，文件夹内平铺各阶段的 skill，不再靠命名前缀分组——2026-08-20之前所有流水线挤在一个 `skills/` 平铺目录里（参照 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的布局），靠 `wechat-`/`book-` 这类前缀区分归属；两条流水线规模都起来之后这个平铺结构反而让人分不清"这堆东西都是干嘛的"，于是拆开：一条流水线一个顶层文件夹，文件夹名本身就是流水线名，内部不用再重复前缀。

```
agent-skills/
├── wechat/                    # 公众号流水线，每个 skill 一个目录
│   ├── topic-gen/
│   ├── research/
│   ├── deepen/
│   ├── proofreading/
│   ├── proofreading-workspace/  # proofreading 的 eval 测试记录，不是 skill 本身
│   ├── write-article/         # 调用名仍是 write-article，见下方说明
│   ├── newsletter-digest/     # 调用名仍是 newsletter-digest
│   └── architecture-diagram/  # 调用名仍是 architecture-diagram
├── book/                      # 写书流水线，同样每个 skill 一个目录
│   └── research-planning/
└── publishing-pipeline/       # write-article / newsletter-digest 共用的发布脚本（check.py / publish.py 等），跟着 write-article 一起从源头同步
```

设计原则和分类法参考了花叔的《Agent Skills 使用手册》（未收录进本仓库——第三方版权内容，不适合放公开仓库）。

3 个跟着源头同步的 skill（`write-article`/`newsletter-digest`/`architecture-diagram`，都在 `wechat/` 下）目录名就是它们的真实调用名，SKILL.md 文件本身（frontmatter 的 `name` 字段、脚本调用等）**不改**，因为改了就跟源头对不上、也没法触发。自研的 skill 目录名和 frontmatter `name` 现在也是同一个值（比如 `wechat/proofreading/SKILL.md` 里 `name: proofreading`），不用再额外套一层流水线前缀——流水线归属已经由它所在的顶层文件夹（`wechat/`、`book/`）表达了。

新开一条不相关的流水线，同样开一个新的顶层文件夹，不要塞进 `wechat/` 或 `book/` 里。

## 设计原则

每个自研 skill 都要过一遍这五条：

1. **先确认再动手**——有真实决策成本的地方，让 skill 先给方案、等用户拍板，别自己埋头跑出两千字才发现方向错了。
2. **边做边存**——长流程（调研、多步生成）每完成一个阶段就落盘，别攒到最后一次性写，防止中途断掉丢东西。
3. **模块化可组合**——一个 skill 只做一件事。不要把整条流水线塞进一个 SKILL.md，拆开才能像 Unix 管道一样单独用或串起来用。
4. **给选择不给答案**——优先给 3 个左右的方案而不是一个"成品"，让用户的判断留在输出里，也是避免"AI 味"的关键手段。
5. **放大你，而不是替代你**——skill 提议、人决定、再执行、再确认，不是输入直接产出没人看过的结果。

维护上的补充：skill 会随实际使用反复改，用 git 记录每次修订，方便回滚到没有回归的版本；SKILL.md 超过约 3000 字就该拆成两个——长而全面反而会降低执行准确率，短而聚焦更好。

## 当前 skill 索引

| 路径 | 调用名 | 干什么用的 | 状态 | 改哪里 |
|---|---|---|---|---|
| `book/research-planning` | `research-planning` | 写书流水线第1阶段：把模糊的书想法整理成确认过的章节结构 + 逐章调研笔记 | 已建，未验证，未注册为可调用 skill | 这个仓库里直接改 |
| `wechat/topic-gen` | `topic-gen` | 公众号选题生成：给一个话题，产出3-4个真正有差异的方向，带优劣分析，交用户选 | 已建，未验证，未注册为可调用 skill | 这个仓库里直接改 |
| `wechat/research` | `research` | 公众号深度调研：选题定了之后按信息源优先级搜索，边搜边存，产出结构化简报 | 已建，未验证，未注册为可调用 skill | 这个仓库里直接改 |
| `wechat/deepen` | `deepen` | 拔高：检查文章核心判断有没有Kevin自己的专业经验支撑，没有就问本人要，不编造，不是扩写/堆案例 | 已建，未验证，未注册为可调用 skill | 这个仓库里直接改 |
| `wechat/proofreading` | `proofreading` | 初稿写完后的AI味+细节审校，不查事实（write-article已管），独立子agent跑 | 已建，用skill-creator Eval模式验证过一轮（2026-08-19，`evals/`目录），未注册为可调用skill——Kevin决定先不装，等在真实公众号文章上跑过验证再说 | 这个仓库里直接改 |
| `wechat/write-article` | `write-article` | Kevin原创文章写作：声音规则 + 3种结构分支 + 发布前检查清单 | **生产在用** | 源头 `~/.claude/skills/write-article` 改，改完手动同步过来 |
| `wechat/newsletter-digest` | `newsletter-digest` | 编译/汇总类文章（技术周刊、链接合集）处理，独立子agent核实取代同模型自查 | **生产在用** | 同上，源头改 |
| `wechat/architecture-diagram` | `architecture-diagram` | 复杂系统架构图，暗色风格 HTML+SVG | 生产在用，第三方（Cocoon AI） | 不改，`npx skills add` 装最新版 |

`write-article` 默认还会用到两个配图 skill——`fireworks-tech-graph`、`excalidraw-diagram-generator`。这两个本身是通过 `npx skills add` 从外部仓库安装的第三方包（脚本和参考资料在安装时动态拉取，源头本地也不存在完整文件），不适合在这个仓库里放"半个镜像"，所以不 vendor，需要时自己装：

```bash
npx skills add yizhiyanhua-ai/fireworks-tech-graph
# excalidraw-diagram-generator 按你实际用的安装源装
```

## 流水线进度

**注**：下面的 ✅ 表示"skill 文件写完了、按设计应该能跑"，不代表"已经装到 Claude Code 能自动触发的位置"——这个仓库里的自研 skill 默认只是源文件，装没装看每条后面的括号说明，装的方法见下方"怎么装一个 skill"。

**写书流水线**（自研，未验证）—— 5 个阶段，1 个建好：

- [x] 调研与规划 → `book/research-planning`（已建，未装）
- [ ] 内容写作
- [ ] 构建与组装
- [ ] 版本管理
- [ ] 多格式输出

**公众号流水线**——上游自研，下游就是已经在跑的真实生产系统，不需要重建：

- [x] 选题生成 → `wechat/topic-gen`（已建，未装）
- [x] 深度调研 → `wechat/research`（已建，未装）
- [x] 写作 → `wechat/write-article`（生产在用）
- [x] 拔高（可选） → `wechat/deepen`（已建，未装。判断句有没有Kevin自己的经验支撑，没有就问本人，不编）
- [x] AI味+细节审校 → `wechat/proofreading`（已建，未装，Kevin决定先不装等真实文章验证。只管AI味和细节，事实核查是`write-article`自己的事，独立子agent跑）
- [x] 配图 → 发布 → 3 个配图 skill / `wechat/newsletter-digest`（编译类走这个而不是`write-article`，生产在用）

（曾经有一个泛化打包分享的独立分支`kevin-wechat-skill/`，2026-08-20决定不做通用分发，已删除——这个仓库现在只服务 Kevin 自己的流水线，不维护对外分发的版本。git 历史里还能找到，commit `57cdb35`。）

## 怎么改一个 skill

**新建**：用 `skill-creator` skill 起草，别手写——它定义好了 SKILL.md 结构、eval/test 流程、description 优化方法。新 skill 放在对应流水线的顶层文件夹下（`wechat/<name>/`、`book/<name>/`），kebab-case，跟 frontmatter 里的 `name` 对齐——两者现在是同一个值，不用再套流水线前缀。

**改一个跟着源头同步的 skill**（`write-article`、`newsletter-digest`、`architecture-diagram`）：先去源头（`~/.claude/skills/<name>`）改，改完手动 `cp -r` 过来这个仓库对应的 `wechat/<name>/` 目录再提交——**`cp` 过来的 SKILL.md 内容本身（包括 frontmatter 的 `name` 字段）原样不动，不要跟着改名**。不能反过来在这个仓库里单方面改——那边才是天天在用的权威版本，这边的副本改了不会生效，还会造成两边不一致。没有自动检测漂移的机制，靠人工重新对比。

## 怎么装一个 skill

这个仓库里的自研 skill 默认只是源文件——写完不会自动被 Claude Code 发现或触发，得手动装到下面两个位置之一：

- **个人级，所有项目都能用**：`~/.claude/skills/<skill-name>/`
- **项目级，只在某个项目里能用**：`<那个项目>/.claude/skills/<skill-name>/`

推荐软链接而不是复制：

```bash
ln -s ~/Documents/GitHub/skills_creator_project/wechat/proofreading ~/.claude/skills/proofreading
```

软链接的好处：这个仓库里的文件改了，装的那份立刻生效，不用每次手动重新复制，也不会出现"装的版本"和"仓库里的版本"两份内容各自漂移的问题。

**注意软链接要指向仓库的主目录**（`~/Documents/GitHub/skills_creator_project`），不要指向某次会话临时开的 git worktree（`.claude/worktrees/...`）——worktree 用完可能会被清掉，软链接会变成死链接。

装完想验证有没有真的生效：开一个新的 Claude Code 会话，说一句会触发这个 skill 描述里"什么时候用"条件的话，看它会不会自己去读这个 SKILL.md。

## License

MIT
