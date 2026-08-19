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
│   ├── write-article/
│   ├── newsletter-digest/
│   ├── fireworks-tech-graph/
│   ├── architecture-diagram/
│   └── excalidraw-diagram-generator/
├── kevin-wechat-skill/         # 上面公众号相关几个 skill 泛化打包后的可分发版本
├── publishing-pipeline/        # write-article / newsletter-digest 共用的发布脚本（check.py / publish.py 等）
└── Agent-Skills-Complete-Guide-zh-v260411.pdf   # 设计原则和分类法的来源
```

## 两类 skill：自己写的 vs 镜像的

仓库里的 skill 分两种，命名和维护方式不一样：

- **自研（`kevin-` 前缀）**：从零设计的，比如 `kevin-book-research-planning`、`kevin-wechat-topic-gen`。同一条流水线的 skill 再共享一个二级前缀（`kevin-book-*`、`kevin-wechat-*`），方便在 `skills/` 平铺目录里一眼认出属于哪条流水线。
- **镜像（保留原名）**：`write-article`、`newsletter-digest` 等是从 `~/.claude/skills/` 同步过来的、已经在实际生产使用的真实 skill。放进这个仓库只是为了拿到 git 版本历史（`~/.claude/skills` 本身不带版本控制），不是在这里重新设计它们——改动应该先发生在源头，再手动同步过来。

## 设计原则

出自 `Agent-Skills-Complete-Guide-zh-v260411.pdf`，每个自研 skill 都要过一遍这五条：

1. **先确认再动手**——有真实决策成本的地方，让 skill 先给方案、等用户拍板，别自己埋头跑出两千字才发现方向错了。
2. **边做边存**——长流程（调研、多步生成）每完成一个阶段就落盘，别攒到最后一次性写，防止中途断掉丢东西。
3. **模块化可组合**——一个 skill 只做一件事。不要把整条流水线塞进一个 SKILL.md，拆开才能像 Unix 管道一样单独用或串起来用。
4. **给选择不给答案**——优先给 3 个左右的方案而不是一个"成品"，让用户的判断留在输出里，也是避免"AI 味"的关键手段。
5. **放大你，而不是替代你**——skill 提议、人决定、再执行、再确认，不是输入直接产出没人看过的结果。

维护上的补充：skill 会随实际使用反复改，用 git 记录每次修订，方便回滚到没有回归的版本；SKILL.md 超过约 3000 字就该拆成两个——长而全面反而会降低执行准确率，短而聚焦更好。

## 当前 skill 索引

| Skill | 所属流水线 | 类型 | 状态 |
|---|---|---|---|
| `kevin-book-research-planning` | 写书 | 自研 | 已建，未验证，未注册为可调用 skill |
| `kevin-wechat-topic-gen` | 公众号 | 自研 | 已建，未验证 |
| `kevin-wechat-research` | 公众号 | 自研 | 已建，未验证 |
| `write-article` | 公众号 | 镜像 | **生产在用** |
| `newsletter-digest` | 公众号 | 镜像 | **生产在用** |
| `fireworks-tech-graph` | 公众号（配图） | 镜像，不完整 | 生产在用（`scripts/`、`references/` 未同步） |
| `architecture-diagram` | 公众号（配图） | 镜像，完整 | 生产在用 |
| `excalidraw-diagram-generator` | 公众号（配图） | 镜像，不完整 | 生产在用（`references/`、`templates/`、`scripts/` 未同步） |

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
- [x] 写作 → 审校 → 配图 → 发布 → `write-article` / `newsletter-digest` / 3 个配图 skill

**公众号流水线打包分享**（独立分支，目标是发布成通用包）：

- [x] 打包 `kevin-wechat-skill/`：泛化后的 topic-gen / research / write-article / newsletter-digest + 新增的 publish 子 skill
- [ ] 端到端跑通全链路（topic-gen → research → write-article → publish）
- [ ] 验证跨工具安装（Codex / Gemini CLI，不只 Claude）
- [ ] 决定独立开仓库还是留在这个仓库下，然后正式发布

## 怎么加一个新 skill

用 `skill-creator` skill 起草，别手写——它定义好了 SKILL.md 结构、eval/test 流程、description 优化方法。新 skill 放在 `skills/<name>/`，kebab-case，跟 frontmatter 里的 `name` 对齐。自研的一律 `kevin-` 前缀；同一条流水线的再共享二级前缀。SKILL.md 控制在 500 行以内，大参考材料放 `references/`，可执行脚本放 `scripts/`。

镜像 skill 走另一条路：源头（`~/.claude/skills/<name>`）改完之后，手动 `cp -r` 过来再提交，没有自动检测漂移的机制，靠人工重新对比。

## License

MIT
