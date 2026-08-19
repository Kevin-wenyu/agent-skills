#!/usr/bin/env python3
"""
发布前校验脚本
用法: python check.py <文章路径.md>

检查项：
  1. SQL 块语法验证（BEGIN...ROLLBACK，不产生副作用）
  2. 讲次引用校验（"第N讲"对照大纲映射）
  另外还包含：SVG 引用/尺寸校验、编译类文章 frontmatter 校验（仅对 digest 文章生效）、小节链接完整性校验
"""

import sys
import re
import subprocess
import tempfile
from pathlib import Path

VAULT = Path(__file__).parent.parent

# ── 讲次/系列大纲映射（可选功能）───────────────────────────────
# 如果你的公众号内容是系列课/连载，写文章时会互相引用"第N讲"这种编号，
# 把编号 → 标题关键词填进这个字典，check_episode_refs 就会校验引用是否在大纲范围内。
# 留空（默认）则完全跳过这项检查，不影响其他校验项。
# 示例（原作者 Kevin 的 PostgreSQL 系列课大纲，仅供参考格式，替换成你自己的）：
#   EPISODE_MAP = {1: "Roadmap", 2: "慢查询", 3: "EXPLAIN", ...}
EPISODE_MAP = {}

# SQL 块校验是可选功能：文章里如果有 ```sql 代码块，会拼进一个 BEGIN...ROLLBACK
# 事务丢给本地 Postgres 验证语法（不产生副作用，跑完自动回滚）。
# 需要本机装了 psql 并能连接下面这个数据库；连不上会导致该项报错，
# 如果你不需要这项检查，把 validate_all_sql 的调用去掉，或者忽略这条报错即可。
PSQL = "/opt/homebrew/bin/psql"  # 换成你自己的 psql 路径，比如 `which psql` 的结果
PG_DB = "postgres"  # 换成你用来做语法校验的本地数据库名


def extract_sql_blocks(text: str) -> list[tuple[int, str]]:
    """返回 [(起始行号, sql内容), ...]"""
    blocks = []
    lines = text.split("\n")
    in_block = False
    current = []
    start_line = 0
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```sql") and not in_block:
            in_block = True
            current = []
            start_line = i
        elif line.strip() == "```" and in_block:
            in_block = False
            blocks.append((start_line, "\n".join(current)))
            current = []
        elif in_block:
            current.append(line)
    return blocks


def validate_all_sql(blocks: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """把所有 SQL 块顺序拼入一个 BEGIN...ROLLBACK 事务执行。
    返回有错误的块列表：[(起始行号, 错误信息), ...]
    """
    if not blocks:
        return []

    # 拼合：每个块之间加分隔注释，方便定位
    parts = ["BEGIN;"]
    for start_line, sql in blocks:
        stripped = "\n".join(
            l for l in sql.splitlines() if not l.strip().startswith("--")
        ).strip()
        if not stripped:
            continue
        # 跳过含占位符或不完整的示例块
        if re.search(r"\.\.\.|<[^>]+>|\[在这里|粘贴", sql):
            continue
        # 跳过只有 WHERE/ORDER BY/HAVING 子句的片段
        if re.match(r"\s*(WHERE|ORDER\s+BY|HAVING|LIMIT|GROUP\s+BY)\b", stripped, re.IGNORECASE):
            continue
        # 跳过引用业务表的操作命令（本地无对应表）
        first_kw = stripped.split()[0].upper() if stripped.split() else ""
        if first_kw in ("ANALYZE", "VACUUM", "REINDEX", "CLUSTER"):
            continue
        # DDL 引用业务表，跳过（ALTER TABLE / CREATE INDEX / CREATE STATISTICS）
        if re.match(r"(ALTER\s+TABLE|CREATE\s+(UNIQUE\s+)?INDEX|CREATE\s+STATISTICS)\b", stripped, re.IGNORECASE):
            continue
        parts.append(f"-- [block:{start_line}]")
        parts.append(sql)
        parts.append(";")
    parts.append("ROLLBACK;")

    combined = "\n".join(parts)
    with tempfile.NamedTemporaryFile(suffix=".sql", mode="w", delete=False) as f:
        f.write(combined)
        tmpfile = f.name

    try:
        result = subprocess.run(
            [PSQL, "-d", PG_DB, "-f", tmpfile, "-v", "ON_ERROR_STOP=1"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        Path(tmpfile).unlink()
        print(f"  ⊘ 跳过 SQL 校验（找不到 psql: {PSQL}，如果你不需要本地验证SQL语法，忽略这条即可）")
        return []
    Path(tmpfile).unlink()

    if result.returncode == 0:
        return []

    # 从错误信息里提取出错位置
    errors = []
    err_text = result.stderr.strip() or result.stdout.strip()

    # 从错误信息里找是哪个 block 出错：取错误行号，反查最近的 [block:N]
    err_lineno = None
    m = re.search(r"\.sql:(\d+):", err_text)
    if m:
        err_lineno = int(m.group(1))

    # 重建 combined 的行映射：找到出错行对应的 block
    failed_block_line = blocks[0][0]
    if err_lineno:
        combined_lines = combined.splitlines()
        current_block = blocks[0][0]
        for i, line in enumerate(combined_lines, 1):
            bm = re.match(r"-- \[block:(\d+)\]", line)
            if bm:
                current_block = int(bm.group(1))
            if i >= err_lineno:
                failed_block_line = current_block
                break

    first_err = next(
        (l for l in err_text.splitlines() if "ERROR" in l),
        err_text.splitlines()[0] if err_text else "未知错误"
    )
    errors.append((failed_block_line, first_err))
    return errors


def check_svg_refs(text: str) -> list[str]:
    """检查文章中所有 ![[xxx.svg]] 引用的文件是否存在"""
    issues = []
    svg_dir = VAULT / "assets" / "svg"
    for m in re.finditer(r"!\[\[([^\]]+\.svg)\]\]", text):
        fname = m.group(1)
        if not (svg_dir / fname).exists():
            issues.append(f"  缺少 SVG 文件: assets/svg/{fname}")
    return issues


def check_cover_title_sync(text: str) -> list[str]:
    """检查封面 SVG（首个 SVG 引用）里的文字是否还带着标题的关键词，
    防止标题改了但封面文字没同步（如 655 那次 "编辑整理" 改成 "内容整理" 忘了改封面）"""
    issues = []
    title_m = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    if not title_m:
        return issues
    title = title_m.group(1).strip()
    cjk_runs = re.findall(r"[一-鿿]+", title)
    if not cjk_runs:
        return issues
    suffix = cjk_runs[-1]  # 标题里最后一段连续中文，通常是副标题/关键词

    m = re.search(r"!\[\[([^\]]+\.svg)\]\]", text)
    if not m:
        return issues
    svg_path = VAULT / "assets" / "svg" / m.group(1)
    if not svg_path.exists():
        return issues
    svg_text = svg_path.read_text(encoding="utf-8")
    if suffix not in svg_text:
        issues.append(
            f'  封面 {m.group(1)} 里没有出现标题关键词"{suffix}"，标题可能改了但封面文字没同步'
        )
    return issues


def check_episode_refs(text: str, current_episode: int) -> list[str]:
    """检查文章中所有"第N讲"引用是否在大纲里"""
    issues = []
    pattern = re.compile(r"第\s*(\d+)\s*讲")
    for m in pattern.finditer(text):
        n = int(m.group(1))
        if n == current_episode:
            continue  # 本讲自我引用，跳过
        if n not in EPISODE_MAP:
            issues.append(f'  引用"第{n}讲"，超出大纲范围（1-20）')
    return issues


def is_digest_article(text: str) -> bool:
    """判断是否是编译/汇总类文章（不是 Kevin 原创），只有这类文章才走 digest frontmatter 校验。
    判断标准跟 write-article skill 里的一致：标题/frontmatter 带"编辑整理"/"周刊"/"汇编"这种字样，
    或 tags 里带"整理"。"""
    fm_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    fm = fm_match.group(1) if fm_match else ""
    tags_m = re.search(r"^tags:\s*\[(.*?)\]", fm, re.MULTILINE)
    if tags_m and "整理" in tags_m.group(1):
        return True
    title_m = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
    if title_m and re.search(r"编辑整理|周刊|汇编", title_m.group(1)):
        return True
    h1_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if h1_m and re.search(r"编辑整理|周刊|汇编", h1_m.group(1)):
        return True
    return False


def check_digest_frontmatter(text: str) -> list[str]:
    """检查编译类文章 frontmatter 必备字段，以及 H1 与 title 是否一致"""
    issues = []
    fm_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        issues.append("  缺少 frontmatter（--- ... ---）")
        return issues
    fm = fm_match.group(1)

    required = ["title", "date", "tags"]
    missing = [f for f in required if not re.search(rf"^{f}:", fm, re.MULTILINE)]
    if missing:
        issues.append(f"  frontmatter 缺字段: {', '.join(missing)}")

    status_m = re.search(r"^status:\s*(\S+)", fm, re.MULTILINE)
    if status_m and status_m.group(1) not in ("draft", "published"):
        issues.append(f"  status 应为 draft 或 published，实际是 {status_m.group(1)}")
    elif not status_m:
        issues.append("  frontmatter 缺 status 字段")

    title_m = re.search(r"^title:\s*(.+)$", fm, re.MULTILINE)
    h1_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if title_m and h1_m:
        title = title_m.group(1).strip().strip('"').strip("'")
        h1 = h1_m.group(1).strip()
        if title != h1:
            issues.append(f'  H1 标题 "{h1}" 与 frontmatter title "{title}" 不一致')
    elif not h1_m:
        issues.append("  正文缺少 H1 标题")

    return issues


def check_svg_dimensions(text: str, vault: Path) -> list[str]:
    """检查引用的 SVG 是否有 width/height（缺 width/height 在 Obsidian 会裁切成 300x150）"""
    issues = []
    svg_dir = vault / "assets" / "svg"
    for m in re.finditer(r"!\[\[([^\]]+\.svg)\]\]", text):
        fname = m.group(1)
        svg_path = svg_dir / fname
        if not svg_path.exists():
            continue  # 缺文件已经由 check_svg_refs 报过，这里不重复报
        svg_text = svg_path.read_text(encoding="utf-8")
        root_tag_m = re.search(r"<svg\b[^>]*>", svg_text)
        if not root_tag_m:
            issues.append(f"  {fname}: 找不到 <svg> 根标签")
            continue
        root_tag = root_tag_m.group(0)
        has_width = re.search(r'\bwidth="[\d.]+', root_tag)
        has_height = re.search(r'\bheight="[\d.]+', root_tag)
        if not (has_width and has_height):
            issues.append(
                f"  {fname}: 根 <svg> 标签缺 width/height，"
                f"Obsidian 里会裁切成默认 300x150"
            )
    return issues


def check_section_links(text: str) -> list[str]:
    """检查正文每个 ## 小节内部是否有链接，防止链接被堆到文末统一列表（发布渲染会塌陷成一段）"""
    issues = []
    # 只看第一个 ## 之后的内容，跳过 frontmatter/H1/引言段
    sections = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    # re.split 用捕获组时返回 [before, title1, body1, title2, body2, ...]
    if len(sections) < 3:
        return issues  # 没有二级标题，不适用这个检查
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        body = sections[i + 1] if i + 1 < len(sections) else ""
        has_link = re.search(r"https?://|\[.+?\]\(.+?\)", body)
        if not has_link:
            issues.append(f'  小节"{title}"内没有找到链接（如果这条确实不需要外链可以忽略这条警告）')
    return issues


def get_episode_number(text: str) -> int:
    """从 frontmatter 读 episode 字段"""
    m = re.search(r"^episode:\s*(\d+)", text, re.MULTILINE)
    return int(m.group(1)) if m else 0


def main():
    if len(sys.argv) < 2:
        print("用法: python check.py <文章路径.md>")
        sys.exit(1)

    md_path = VAULT / sys.argv[1]
    if not md_path.exists():
        print(f"文件不存在: {md_path}")
        sys.exit(1)

    text = md_path.read_text(encoding="utf-8")
    episode = get_episode_number(text)

    print(f"\n校验文章: {md_path.name}（第{episode}讲）")
    print("─" * 50)

    errors = []
    warnings = []

    # ── 1. SVG 引用校验 ──────────────────────────────────────────
    print(f"[1/6] SVG 引用校验...")
    svg_issues = check_svg_refs(text)
    if svg_issues:
        for issue in svg_issues:
            errors.append(issue)
            print(f"  ✗ {issue.strip()}")
    else:
        svg_count = len(re.findall(r"!\[\[[^\]]+\.svg\]\]", text))
        print(f"  ✓ {svg_count} 个 SVG 引用均存在")

    # ── 1b. 封面文字 / 标题同步校验 ────────────────────────────
    cover_issues = check_cover_title_sync(text)
    if cover_issues:
        for issue in cover_issues:
            warnings.append(issue)
            print(f"  ⚠ {issue.strip()}")

    # ── 2. SQL 验证 ──────────────────────────────────────────────
    sql_blocks = extract_sql_blocks(text)
    print(f"\n[2/6] SQL 块校验（共 {len(sql_blocks)} 块，顺序合并执行）...")

    sql_errors = validate_all_sql(sql_blocks)
    if not sql_errors:
        for start_line, _ in sql_blocks:
            print(f"  ✓ 第 {start_line} 行")
    else:
        for start_line, _ in sql_blocks:
            matched = [e for e in sql_errors if e[0] == start_line]
            if matched:
                msg = matched[0][1]
                errors.append(f"  ✗ 第 {start_line} 行 SQL 错误: {msg}")
                print(f"  ✗ 第 {start_line} 行 → {msg}")
            else:
                print(f"  ✓ 第 {start_line} 行")

    # ── 3. 讲次引用校验（可选，EPISODE_MAP 为空则跳过）──────────────
    print(f"\n[3/6] 讲次引用校验...")
    if not EPISODE_MAP:
        print("  ⊘ 跳过（EPISODE_MAP 为空，没有配置系列课大纲——如果你不写连载系列，忽略这条即可）")
    else:
        ref_issues = check_episode_refs(text, episode)
        if ref_issues:
            for issue in ref_issues:
                warnings.append(issue)
                print(f"  ⚠ {issue.strip()}")
        else:
            print("  ✓ 所有讲次引用在大纲范围内")

    # ── 4. Frontmatter 校验（编译类文章）──────────────────────────
    print(f"\n[4/6] Frontmatter 校验...")
    if is_digest_article(text):
        fm_issues = check_digest_frontmatter(text)
        if fm_issues:
            for issue in fm_issues:
                errors.append(issue)
                print(f"  ✗ {issue.strip()}")
        else:
            print("  ✓ frontmatter 字段完整，H1 与 title 一致")
    else:
        print("  ⊘ 跳过（非编译类文章，不适用这套 frontmatter 规则）")

    # ── 5. SVG 尺寸校验 ──────────────────────────────────────────
    print(f"\n[5/6] SVG width/height 校验...")
    dim_issues = check_svg_dimensions(text, VAULT)
    if dim_issues:
        for issue in dim_issues:
            errors.append(issue)
            print(f"  ✗ {issue.strip()}")
    else:
        print("  ✓ 所有 SVG 都有 width/height")

    # ── 6. 小节链接完整性校验 ───────────────────────────────────
    print(f"\n[6/6] 小节链接完整性校验...")
    link_issues = check_section_links(text)
    if link_issues:
        for issue in link_issues:
            warnings.append(issue)
            print(f"  ⚠ {issue.strip()}")
    else:
        print("  ✓ 所有小节都带链接")

    # ── 汇总 ─────────────────────────────────────────────────────
    print("\n" + "─" * 50)
    if not errors and not warnings:
        print("✅ 全部通过，可以发布。")
        sys.exit(0)
    else:
        if errors:
            print(f"❌ {len(errors)} 个错误，建议修复后再发布。")
        if warnings:
            print(f"⚠  {len(warnings)} 个警告，请人工确认。")
        sys.exit(1)


if __name__ == "__main__":
    main()
