# kevin-wechat-skill

一套完整的公众号文章生产流水线，打包成可跨工具安装的 Claude Skills：选题 → 调研 → 写作 → 编译类周刊处理 → 校验与发布。

跟着标准 [Agent Skills](https://agentskills.io) 格式写成，理论上可以装进任何支持这个标准的工具（Claude Code、Cursor、Codex、Gemini CLI 等），不锁定某一个产品。

## 这个包能做什么

一篇公众号文章从"我想写点什么"到"推进草稿箱"的完整链路：

1. **`skills/topic-gen`** — 给一个话题，生成3-4个有真实差异的选题方向，你来选
2. **`skills/research`** — 针对选定方向做调研，边搜边存，产出结构化简报
3. **`skills/write-article`** — 写原创文章，带一套真实校准过的声音规则/文章结构/钩子/事实核查标准（首次使用需要换成你自己的，见该 skill 内的说明）
4. **`skills/newsletter-digest`** — 处理编译/汇总类内容（技术周刊、链接合集），跟原创写作走不同规则
5. **`skills/publish`** — 发布前格式校验 + 推送草稿箱（不会替你点最终发布）

各 skill 独立可用，也可以按上面的顺序串联成完整流水线。

## 安装

```bash
npx skills add <your-github-username>/kevin-wechat-skill            # 装全部
npx skills add <your-github-username>/kevin-wechat-skill --skill write-article   # 只装一个
```

（或者直接把 `skills/` 下面的目录复制到你的工具认的 skills 路径下，比如 Claude Code 的 `~/.claude/skills/`。）

## 外部依赖（不随本包分发，需要单独安装）

配图用到下面几个第三方 skill，本包只在文档里引用，不 vendor 副本——它们是各自独立维护的项目，装最新版不容易和这里的拷贝产生版本漂移：

```bash
npx skills add yizhiyanhua-ai/fireworks-tech-graph      # 默认配图工具
# architecture-diagram、excalidraw-diagram-generator 按你实际用到的工具渠道安装
```

不装这几个也能用文字部分（选题、调研、写作、发布），只是文章里不会自动配图。

## 首次使用前必做的事

1. **`write-article`**：把"Kevin 的声音"和"锚点文章"两节换成你自己的写作规则和代表作，见该 skill 文件内的说明——这是让 skill 真正为你服务的关键一步，不换的话你会得到 Kevin 的写作风格，不是你的。
2. **`publish`**：复制 `skills/publish/scripts/wechat.yaml.example` 为 `wechat.yaml`，填入你自己公众号后台的 `app_id`/`app_secret`。这个文件包含真实密钥，**永远不要提交到公开仓库**，已经在 `.gitignore` 里排除。

## 目录结构

```
kevin-wechat-skill/
├── README.md
└── skills/
    ├── topic-gen/SKILL.md
    ├── research/SKILL.md
    ├── write-article/SKILL.md
    ├── newsletter-digest/SKILL.md
    └── publish/
        ├── SKILL.md
        ├── scripts/          # check.py / publish.py / publish_html.py / qa_svg.py / make_cover.py / stats.py
        │   └── wechat.yaml.example
        └── references/       # fact-checking.md / vault-specs.md
```

## 来源与致谢

`write-article`、`newsletter-digest`、`publish` 里的脚本和规则，源自作者本人（Kevin）真实在用的公众号写作流程，经脱敏和泛化后开源——具体的声音规则、锚点文章、发布素材库路径都替换成了占位符或标注为"参考实现"，详见各 skill 内的说明。设计上参考了 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的目录组织方式。
