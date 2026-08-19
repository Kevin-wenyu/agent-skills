---
name: publish
description: |
  公众号发布前校验与发布技能。当 `write-article`/`newsletter-digest` 写完一篇文章需要校验格式或推送草稿时使用，也可以直接触发："校验一下这篇""可以发布了吗""推草稿箱"。产出校验报告 + （确认后）推送到微信公众号草稿箱。这个 skill 不会替你点"发布"——真正发布永远需要你自己去公众号后台手动确认。
---

# 公众号发布校验与推送

## 这个 skill 做什么

`write-article`/`newsletter-digest` 写完稿子后调用这个 skill 做两件事：格式/事实校验（`check.py`），确认无误后推送到微信公众号草稿箱（`publish.py`）。两步分开执行，不校验通过不进入推送步骤。

## 前置准备（首次使用）

1. **安装 Python 依赖**：`requests`、`pyyaml`、`browser_cookie3`（`stats.py` 用）、`playwright`（`qa_svg.py` 用，装完还要 `playwright install chromium`）。建议用虚拟环境。
2. **配置微信凭证**：把 `scripts/wechat.yaml.example` 复制成 `scripts/wechat.yaml`，填入你自己公众号后台"开发者中心"里的 `app_id`/`app_secret`。**这个文件不要提交到任何公开仓库**——它就是你公众号的密钥。
3. **（可选）本地 Postgres**：如果你的文章里会写 SQL 代码块并想校验语法，`check.py` 需要能连上本机的 `psql`；不需要这项检查就忽略相关警告，不影响其他校验项。

## 脚本一览

| 脚本 | 作用 |
|------|------|
| `check.py` | 发布前校验：SVG引用/尺寸、SQL块语法（可选）、系列课引用（可选）、编译类文章frontmatter、小节链接完整性 |
| `publish.py` | 把 Markdown 文章转换并推送到微信公众号草稿箱（`--clear` 参数可以先清空草稿箱） |
| `publish_html.py` | 直接推送一个 HTML 文件到草稿箱，自动处理内嵌图片上传 |
| `qa_svg.py` | 把 SVG 渲染成 PNG 供人工目检，看完自己删（`--clean` 批量清理） |
| `make_cover.py` | 生成封面图（色块+标题风格，分类配色可在脚本里自定义） |
| `stats.py` | 通过读取本机 Chrome 的登录态 cookie，拉取公众号后台的文章阅读数据 |

**`stats.py` 需要特别注意**：它直接读取你本机 Chrome 浏览器里 `mp.weixin.qq.com` 的登录 cookie 来发请求，不是走官方 API。这意味着：只在你自己的电脑、自己已登录公众号后台的 Chrome 上才能跑通；不需要这个数据回流功能可以完全不用这个脚本，不影响 `check.py`/`publish.py`。

## 执行步骤

### 1. 校验

```bash
cd skills/publish/scripts
python check.py <文章路径.md>
```

0 error 才能进入下一步；warning 需要人工确认是否可以接受。校验报告里每一条都要给出具体位置和原因，不能只说"有问题"。

### 2. 推送草稿（需要用户明确同意才执行）

校验通过后，向用户确认"校验通过了，要推送到草稿箱吗"，得到明确同意再执行：

```bash
python publish.py <文章路径.md>
# 想先清空草稿箱再推：加 --clear
```

推送成功只是把内容放进了公众号后台的草稿箱。

## 边界

- **绝不自动执行真正的"发布"操作**——`publish.py`/`publish_html.py` 做的是"推草稿"，草稿箱之后还需要用户自己登录公众号后台，人工检查排版、手动点发布。这一步任何情况下都不能被这个 skill 跳过或替用户确认，是硬性边界，不因为校验全部通过就自动执行。
- 校验没过（有 error）不推送，直接反馈给用户具体错哪了。
- `wechat.yaml` 里是真实密钥，不读环境变量以外的地方获取，不要把内容打印到日志或对话里。

## 参考资料

- `references/fact-checking.md` — 事实核查规范：权威信息源清单、核查流程、事实审计报告格式
- `references/vault-specs.md` — 参考实现（Kevin自己的）目录映射和配色规范，换成你自己的写作素材库结构
