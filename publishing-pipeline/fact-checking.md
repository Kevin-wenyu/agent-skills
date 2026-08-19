# 事实核查规范

## 核心原则

**禁止使用训练数据印象作为文章事实来源。**

凡涉及技术架构细节、数据指标、发布时间、算法描述、API 接口等具体事实，必须在写作前通过以下来源之一完成核实，并在写作过程中注明来源。

---

## 权威来源清单

### 开源项目与代码
| 来源 | 适用内容 |
|------|----------|
| GitHub 官方 repo README | 项目架构、功能描述、安装方式 |
| GitHub Releases / CHANGELOG | 版本号、发布时间、功能变更 |
| GitHub Issues / Discussions | 已知问题、设计决策背景 |
| 源代码本身 | 算法实现、数据结构、配置项 |

重点仓库（AI 工程方向）：
- `anthropics/claude-code`
- `All-Hands-AI/OpenHands`
- `modelcontextprotocol/specification`
- `openai/codex`
- `microsoft/autogen`
- `langchain-ai/langchain`

### 官方文档与博客
| 来源 | 适用内容 |
|------|----------|
| `docs.anthropic.com` | Claude API、Claude Code、MCP |
| `platform.openai.com/docs` | OpenAI API、Codex、GPT 系列 |
| `anthropic.com/news` | 发布公告、产品发布时间 |
| `openai.com/blog` | OpenAI 产品发布与研究 |
| `deepmind.google/research` | Google DeepMind 研究成果 |
| `ai.meta.com` | Meta AI 研究与产品 |
| `mistral.ai/news` | Mistral 模型发布 |

### 学术论文
| 来源 | 适用内容 |
|------|----------|
| `arxiv.org` | 预印本论文，核实摘要与核心数据 |
| ACL Anthology (`aclanthology.org`) | NLP 方向会议论文 |
| OpenReview (`openreview.net`) | ICLR / NeurIPS / ICML 审稿与论文 |
| Semantic Scholar (`semanticscholar.org`) | 论文引用与摘要查询 |

### 数据库专项
| 来源 | 适用内容 |
|------|----------|
| `postgresql.org/docs` | PostgreSQL 官方文档，版本锁定 |
| `dev.mysql.com/doc` | MySQL 官方文档 |
| `docs.oracle.com` | Oracle 官方文档 |
| `pganalyze.com/blog` | PG 性能分析，社区高质量内容 |
| `use-the-index-luke.com` | 索引设计，标注「社区来源」 |

### 行业数据与报告
| 来源 | 适用内容 |
|------|----------|
| Stack Overflow Developer Survey | 技术使用率、开发者偏好 |
| DB-Engines Ranking (`db-engines.com`) | 数据库流行度排名 |
| ThoughtWorks Technology Radar | 技术成熟度 |
| CNCF Survey | 云原生技术采用 |

---

## 执行流程

```
写文章前
  ↓
列出文章中所有"具体事实"（数字、时间、架构细节、算法名称）
  ↓
逐条 WebFetch 对应权威来源
  ↓
找到来源 → 写入文章，末尾或脚注标注「来源：XXX」
找不到来源 → 降级处理（见下）
```

### 降级处理规则

| 情况 | 处理方式 |
|------|----------|
| 找到官方文档/论文 | 直接引用，标注来源 |
| 只找到社区博客/二手来源 | 标注「来源：XXX（社区，建议验证）」 |
| 找不到任何来源 | 改为「据我的理解」「从架构角度推断」，不以确定句式写出 |
| 数字类数据无法核实 | 删除数字，改为定性描述 |

---

## 违规示例

```
❌ TAOR 循环是 Claude Code 的核心执行架构（训练数据印象，未核实）
❌ 33K vs 188K token 完成相同任务（数字来源不明）
❌ Hermes 用 FTS5 内存搜索替代向量数据库（未查原始代码）

✅ 根据 claude-code GitHub README（2026-04-24），其执行模型包含…
✅ 据 OpenHands ICLR 2025 论文（arXiv:XXXX.XXXXX），在 SWE-bench 上成功率为 X%
✅ 从其架构设计推断，这类 Agent 倾向于使用本地搜索替代向量检索（未找到官方说明，待验证）
```

---

## 适用范围

所有对外发布的公众号文章，包括独立选题和系列文章。内部笔记不强制要求，但建议养成习惯。

---

## 事实审计报告（写完后、发布前必做）

⛔ **每篇文章写完正文后，必须在进入 Kevin 审核前，输出一份事实审计报告。**

### 报告格式

```
## 事实审计报告

### 可验证事实（数字、日期、API名、版本号、命令）
| # | 声明 | 来源 1 | 来源 2 | 状态 |
|---|------|--------|--------|------|
| 1 | Claude Code 使用 1M token 上下文窗口 | code.claude.com/docs (2026-05-23) | Anthropic 官方博客 (2026-05-15) | ✅ 双重验证 |
| 2 | shared_buffers 默认值 128MB | postgresql.org/docs/16 (2026-05-23) | — | ⚠️ 单源 |
| 3 | DeepSeek V4 输出 $0.28/MTok | 需核实 | — | ❌ 待验证 |

### 架构声明（系统如何工作）
| # | 声明 | 来源 | 可信度 |
|---|------|------|--------|
| 1 | Claude Code Agent 拥有独立上下文窗口 | code.claude.com/docs | 高（官方文档） |
| 2 | pg_stat_statements 通过共享内存通信 | interdb.jp/pg (2026-05-23) | 高（社区权威来源） |

### 个人判断（不标注为外部事实）
| # | 判断 |
|---|------|
| 1 | "work_mem = 256MB 是大多数 OLTP 场景的安全上限" — 来自 Kevin 生产经验 |
| 2 | "SDD 更适合多人协作场景" — Kevin 的判断 |

### 需降级或删除的声明
| # | 声明 | 处理 |
|---|------|------|
| 1 | "Context Rot 约在 300K tokens 开始" | 降级为"据社区经验分享"，加"未经官方确认" |
```

### 审计规则

1. **所有可验证事实必须至少有 1 个来源**。0 来源 = 删除或降级为个人推断。
2. **核心论点依赖的事实必须至少有 2 个独立来源**。单源 = 标注 ⚠️，由 Kevin 决定是否保留。
3. **所有来源必须标注 fetch 日期**，方便 Kevin 判断时效性。
4. **架构声明必须有官方文档或源码级验证**，不接受社区博客作为唯一来源。
5. **个人判断必须在报告中与外部事实分开列出**，确保读者（和 Kevin）不会把观点当事实。
6. **待验证项 = 阻塞项**。有 ❌ 状态的事实，必须先核实再发给 Kevin，不得以"先让 Kevin 看"心态放过。
