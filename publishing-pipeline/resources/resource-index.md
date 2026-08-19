# PostgreSQL 优化 20 讲 · 外部资源索引

> 使用原则：这些资源用于**补充角度和验证事实**，不是抄内容。
> 写每讲前 WebFetch / pdf skill 读对应章节，提取"他们有但你没讲的角度"，再结合你的实战经验写。
> **外部讲原理（WHY），Kevin 补案例（HOW）**——这个叠加是文章被转发的根因。

---

## 第一梯队：原理级权威来源（覆盖 WHY）

| 资源 | 定位 | 覆盖讲次 |
|------|------|---------|
| **[The Internals of PostgreSQL](https://www.interdb.jp/pg/)** | Hironobu Suzuki 著，免费在线，覆盖内部机制最全面。每章对应一个子系统，是理解"为什么"的权威来源 | 几乎覆盖全部20讲 |
| **[PostgreSQL 14 Internals PDF](https://edu.postgrespro.com/postgresql_internals-14_en.pdf)** | Postgres Pro 出品，Egor Rogov 著。比 interdb 更深，覆盖 MVCC 细节、Buffer Manager、统计信息内部实现。用 pdf skill 读对应章节 | 第04/05/07/11讲重点 |

**interdb.jp 章节映射：**
- Ch3 查询处理 → 第03讲（EXPLAIN cost 计算）、第04讲（rows 估算机制）、第06讲（work_mem 与 Sort/Hash）
- Ch5 并发控制 → 第11讲（锁与 MVCC）
- Ch6 VACUUM → 第09讲（autovacuum）
- Ch7 HOT + Index Only Scan → 第05讲（索引设计，visibility map 前提）
- Ch8 Buffer Manager → 第07讲（shared_buffers）
- Ch9 WAL/Checkpoint → 第08讲
- Ch11 流复制 → 第15讲（主从延迟）

---

## 第二梯队：专项深度来源（覆盖 HOW）

| 资源 | 定位 | 最适合 |
|------|------|--------|
| [pgpedia.info](https://pgpedia.info) | PostgreSQL 对象百科，每个系统视图/函数独立词条 | 查系统视图字段含义、参数行为 |
| [pgmustard.com/blog](https://www.pgmustard.com/blog) | EXPLAIN 深度分析，index 效率，pg_stat_statements | 第03/04/05讲 |
| [depesz.com](https://www.depesz.com) | Hubert Lubaczewski，PG 核心贡献者博客，极深 | 各讲技术细节验证 |
| [postgresqlco.nf](https://postgresqlco.nf) | 所有配置参数说明 + 推荐值 | 第06/07/08讲参数 |
| [pganalyze.com/blog](https://pganalyze.com/blog) | autovacuum、统计信息、连接池深度文章 | 第04/09/10讲 |
| [explain.dalibo.com](https://explain.dalibo.com) | EXPLAIN 可视化工具，附带分析说明 | 第03讲配图参考 |
| [postgreslocksexplained.com](https://postgreslocksexplained.com/) | 锁类型可视化，冲突矩阵图 | 第11讲 |
| [crunchydata.com/blog](https://www.crunchydata.com/blog) | Crunchy Data 工程博客。PG 核心贡献者撰稿，内容 DBA 向：EXPLAIN 分析、pg_stat_statements、Postgres 内部机制、全文搜索。✅ 已验证质量 | 第13/15/16/17讲 |
| [brandur.org/articles](https://brandur.org/articles) | 独立工程师深度博客。覆盖 MVCC 原子性、WAL、连接管理、事务并发，机制类内容（2015-2021）不过时。✅ 已验证质量 | 第11/15讲补充理论 |
| [percona.com/blog](https://www.percona.com/blog/category/postgresql/) | Percona PG 博客。DBA 运维向，监控、复制、索引维护方向。⚠️ 具体文章 URL 不稳定，写讲时现搜 | 第14/15讲参考 |

---

## 各讲对应资源

### 第 04 讲：统计信息偏差（原第05讲，调整后）
- [pganalyze: Understanding Postgres Statistics](https://pganalyze.com/blog/postgres-statistics) — statistics collector 工作机制，default_statistics_target 影响
- [pgpedia: pg_statistic](https://pgpedia.info/p/pg_statistic.html) — 统计信息存储结构
- [depesz: Statistics in PostgreSQL](https://www.depesz.com/tag/statistics/) — 实际案例分析

### 第 05 讲：索引设计（原第04讲，调整后）
- [use-the-index-luke.com](https://use-the-index-luke.com) — 索引设计圣经，B-tree 原理到实战，免费在线书
- [pgmustard: Index Scans](https://www.pgmustard.com/blog) — Index Scan vs Index Only Scan 误区
- [pgpedia: pg_indexes](https://pgpedia.info/p/pg_indexes.html) — 索引元数据查询

### 第 06 讲：work_mem
- [postgresqlco.nf: work_mem](https://postgresqlco.nf/doc/en/param/work_mem/) — 参数详细说明和推荐值逻辑
- [pganalyze: Tune work_mem](https://pganalyze.com/blog/5mins-postgres-work-mem) — 实际调优方法
- [depesz: work_mem](https://www.depesz.com/tag/work_mem/) — spill 案例

### 第 07 讲：shared_buffers 与缓存命中
- [postgresqlco.nf: shared_buffers](https://postgresqlco.nf/doc/en/param/shared_buffers/) — 参数说明
- [pgpedia: pg_buffercache](https://pgpedia.info/p/pg_buffercache.html) — 缓存内容查看
- [pganalyze: Buffer Cache](https://pganalyze.com/blog/buffer-cache) — 命中率分析方法

### 第 08 讲：checkpoint 与 WAL
- [postgresqlco.nf: checkpoint_completion_target](https://postgresqlco.nf/doc/en/param/checkpoint_completion_target/) — 参数说明
- [pgpedia: pg_stat_bgwriter](https://pgpedia.info/p/pg_stat_bgwriter.html) — checkpoint 监控视图
- [depesz: checkpoint](https://www.depesz.com/tag/checkpoint/) — 调优实践

### 第 09 讲：autovacuum 调优
- [pganalyze: Autovacuum Guide](https://pganalyze.com/blog/autovacuum-not-running-postgres) — autovacuum 不工作的排查
- [pgpedia: pg_stat_user_tables](https://pgpedia.info/p/pg_stat_user_tables.html) — 监控死元组
- [depesz: autovacuum](https://www.depesz.com/tag/autovacuum/) — 实战经验

### 第 10 讲：连接池设计
- [pgbouncer 官方文档](https://www.pgbouncer.org/config.html) — 配置参数权威来源
- [pganalyze: Connection Pooling](https://pganalyze.com/blog/postgres-connection-pooling) — 三种模式对比
- [pgpedia: pg_stat_activity](https://pgpedia.info/p/pg_stat_activity.html) — 连接监控

### 第 11 讲：锁冲突排查
- [postgreslocksexplained.com](https://postgreslocksexplained.com/) — 锁类型可视化，冲突矩阵，质量极高
- [pgpedia: pg_locks](https://pgpedia.info/p/pg_locks.html) — pg_locks 字段详解
- [pgpedia: lock modes](https://pgpedia.info/l/lock-modes.html) — 8种锁模式说明

### 第 12 讲：JOIN 策略优化
- [pgmustard: Join Strategies](https://www.pgmustard.com/blog) — Hash/Nested Loop/Merge 选择逻辑
- [depesz: join](https://www.depesz.com/tag/join/) — 实际案例

### 第 13 讲：分区表决策
- [pgpedia: partitioning](https://pgpedia.info/p/partitioning.html) — PG 分区类型说明
- [pganalyze: Partitioning](https://pganalyze.com/blog/postgres-partitioning) — 何时用分区的判断框架

### 第 14 讲：僵尸索引治理
- [pgpedia: pg_stat_user_indexes](https://pgpedia.info/p/pg_stat_user_indexes.html) — 索引使用统计
- pgmustard 博客有专文讨论未使用索引的识别

### 第 15 讲：主从延迟诊断
- [pgpedia: pg_stat_replication](https://pgpedia.info/p/pg_stat_replication.html) — 复制监控视图
- [pganalyze: Replication Lag](https://pganalyze.com/blog/postgres-replication-lag) — 延迟定位方法

### 第 16 讲：并行查询
- [postgresqlco.nf: max_parallel_workers](https://postgresqlco.nf/doc/en/param/max_parallel_workers/) — 参数说明
- [pgmustard: Parallel Query](https://www.pgmustard.com/blog) — 并行计划解读

### 第 13 讲：分区表决策
- [pgpedia: partitioning](https://pgpedia.info/p/partitioning.html) — PG 分区类型说明
- [pganalyze: Partitioning](https://pganalyze.com/blog/postgres-partitioning) — 何时用分区的判断框架
- [crunchydata.com/blog](https://www.crunchydata.com/blog) — 搜索 "partitioning"，有分区剪枝（partition pruning）和声明式分区深度文章

### 第 14 讲：僵尸索引治理
- [pgpedia: pg_stat_user_indexes](https://pgpedia.info/p/pg_stat_user_indexes.html) — 索引使用统计
- [pgmustard.com/blog](https://www.pgmustard.com/blog) — 搜索 "unused indexes"，有识别和清理方法
- [percona.com/blog](https://www.percona.com/blog/category/postgresql/) — 搜索 "bloat index"，有索引膨胀诊断内容

### 第 15 讲：主从延迟诊断
- [pgpedia: pg_stat_replication](https://pgpedia.info/p/pg_stat_replication.html) — 复制监控视图字段详解
- [interdb.jp Ch11](https://www.interdb.jp/pg/pgsql11.html) — 流复制内部机制（WAL sender/receiver 模型）
- [brandur.org/articles](https://brandur.org/articles) — 搜索 "replication"，有复制一致性与延迟机制深度文章
- [crunchydata.com/blog](https://www.crunchydata.com/blog) — 搜索 "replication lag"

### 第 16 讲：并行查询评估
- [postgresqlco.nf: max_parallel_workers](https://postgresqlco.nf/doc/en/param/max_parallel_workers/) — 参数说明
- [postgresqlco.nf: max_parallel_workers_per_gather](https://postgresqlco.nf/doc/en/param/max_parallel_workers_per_gather/) — 单查询并行度参数
- [pgmustard.com/blog](https://www.pgmustard.com/blog) — 搜索 "parallel query"，有并行计划解读
- [crunchydata.com/blog](https://www.crunchydata.com/blog) — 搜索 "parallel"，有并行查询工作原理文章

### 第 17 讲：全文搜索优化
- [pgpedia: pg_trgm](https://pgpedia.info/p/pg_trgm.html) — trigram 索引
- [pgpedia: tsvector](https://pgpedia.info/t/tsvector.html) — 全文搜索数据类型
- [crunchydata.com/blog/postgres-full-text-search-a-search-engine-in-a-database](https://www.crunchydata.com/blog/postgres-full-text-search-a-search-engine-in-a-database) — ✅ 已验证：tsvector/tsquery/GIN/加权排序完整覆盖，适合作为基础原理参考

### 第 18 讲：JSONB 查询优化
- [pgpedia: jsonb](https://pgpedia.info/j/jsonb.html) — JSONB 内部结构
- [pgpedia: GIN index](https://pgpedia.info/g/gin-index.html) — GIN 索引机制
- [crunchydata.com/blog](https://www.crunchydata.com/blog) — 搜索 "jsonb"，有 GIN 索引查询模式深度文章

### 第 19 讲：金融场景实战
- 主要来源：Kevin 实际交付案例（一手经验，无需外部资源）
- 补充：pganalyze 的高并发写入案例作对照
- [percona.com/blog](https://www.percona.com/blog/category/postgresql/) — 搜索 "high concurrency" / "financial"，有高并发写入场景参考

### 第 20 讲：自动化巡检体系
- 前 19 讲所有 SQL 片段汇总
- [pganalyze](https://pganalyze.com) 作为商业化参照，说明自研巡检的差异点
- [github.com/darold/pgbadger](https://github.com/darold/pgbadger) — ✅ 日志分析工具，巡检体系的日志维度参考
- [github.com/ankane/pghero](https://github.com/ankane/pghero) — 索引和查询 dashboard，自研巡检的功能对标参考

---

## 写文章前的资源使用流程

```
1. 确定本讲主题
2. WebFetch 本讲对应的 2-3 个资源
3. 提取"外部有但 Kevin 没讲的角度"
4. 在提纲里标注：[外部角度] 这个点参考 X，建议结合你的 Y 案例
5. Kevin 确认提纲后正式写作
```

---

## AI 工具与提示词资源

| 资源 | 定位 | 用途 |
|------|------|------|
| [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | Claude 官方提示词工程指南 | 每讲 AI prompt 模板优化参考 |
| [Claude API Docs](https://docs.anthropic.com/en/api/) | Claude API 能力边界 | AI 辅助诊断章节的技术准确性 |
| [Text2SQL 论文与工具](https://github.com/eosphoros-ai/Awesome-Text2SQL) | GitHub 精选，NL→SQL 方向 | 第20讲自动化巡检体系 |
| [pgvector](https://github.com/pgvector/pgvector) | PostgreSQL 向量扩展 | AI+PG 融合场景，系列后期可单独成讲 |
| [LLM 辅助 DBA 工作实践](https://www.pgmustard.com/blog) | pgmustard 有涉及 AI 辅助 EXPLAIN 分析 | 各讲 AI 协作部分的具体 prompt 设计 |

> AI 资源的使用原则：每讲的"给 AI 的 prompt 模板"是差异化内容，别的地方没有，要认真设计。
> 不只是"把 SQL 丢给 AI"，而是"给什么上下文，AI 才不会给出错误建议"——这是这个系列的核心价值主张。

---

## GitHub 项目（待补充）

写到相关讲次前再精确搜索，避免过度收集。
已知方向：
- `pg_activity` — 实时活动监控
- `pgbadger` — 日志分析
- `postgres_exporter` — Prometheus 指标导出
- `pgaudit` — 审计日志（金融场景相关）
