# Vault 规范参考

## 目录映射

| 内容类型 | 目标路径 |
|----------|----------|
| MySQL | `01_数据库产品/MySQL/` |
| Oracle | `01_数据库产品/Oracle/` |
| PostgreSQL | `01_数据库产品/PostgreSQL/` |
| Redis | `01_数据库产品/Redis/` |
| MongoDB | `01_数据库产品/MongoDB/` |
| ClickHouse | `01_数据库产品/ClickHouse/` |
| Kingbase / 信创 | `01_数据库产品/Kingbase/` |
| TiDB / OceanBase / Greenplum | `01_数据库产品/分布式数据库/` |
| 跨产品对比 / 架构 / 选型 | `02_行业知识/` |
| Linux / 运维 | `03_工程实践/Linux/` |
| Python | `03_工程实践/Python/` |
| 存储相关 | `03_工程实践/存储管理/` |
| MQ 消息队列 | `03_工程实践/MQ消息队列/` |
| macOS / 效率工具 | `04_Mac效率工具/` |
| LLM / AI / Claude | `05_AI/` |
| 个人成长 / 管理 / 学习 | `06_个人管理/` |
| SVG 图表 | 与文章同目录 |

## Frontmatter 模板

```yaml
---
tags: []
created: YYYY-MM-DD
status: draft
---
```

**tags 词表（不随意扩展）**

- 产品：`mysql` `oracle` `postgresql` `redis` `mongodb` `clickhouse` `tidb` `kingbase`
- 话题：`高可用` `备份恢复` `性能优化` `故障处理` `架构设计` `数据迁移` `监控` `安全`
- 来源：`原创` `整理` `收藏`

**status**：`draft` / `published`

## 画图规范

| 元素 | 规格 |
|------|------|
| 标题栏 | 背景 `#26215C`，白色文字 |
| 容器 | 白底，边框 `#D3D1C7`，圆角 8px |
| 紫（旧版本/存储层） | 填充 `#EEEDFE`，边框 `#AFA9EC` |
| 绿（新版本/当前状态） | 填充 `#E1F5EE`，边框 `#5DCAA5` |
| 琥珀（流转/机制） | 填充 `#FAEEDA`，边框 `#EF9F27` |
| 珊瑚（风险/告警） | 填充 `#FAECE7`，边框 `#F0997B` |
| 灰（中性/监控） | 填充 `#F1EFE8`，边框 `#D3D1C7` |
