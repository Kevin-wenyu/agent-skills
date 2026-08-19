#!/usr/bin/env python3
"""
封面图生成器（B 风格：左色块 + 右标题）
用法:
  python make_cover.py "标题文字" output.svg
  python make_cover.py "标题文字" output.svg --sub "副标题" --cat pg --tags "实战踩坑,性能调优"
"""

import sys
import re
import argparse
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# ─── 分类配置 ────────────────────────────────────────────────────────────────

CATEGORIES = {
    "pg":         ("PG",    "POSTGRESQL"),
    "postgresql": ("PG",    "POSTGRESQL"),
    "mysql":      ("My",    "MYSQL"),
    "oracle":     ("ORA",   "ORACLE"),
    "ai":         ("AI",    "A  I"),
    "dba":        ("DBA",   "D B A"),
    "ops":        ("OPS",   "运  维"),
    "infra":      ("INF",   "INFRA"),
    "xinchuang":  ("信创",  "国产化"),
}

# 每个分类的左栏配色：(left_bg, accent, label_text, brand_text, brand_sub)
CAT_STYLES = {
    "pg":         ("#26215C", "#FF9966", "#BBAAFF", "#8888CC", "#555588"),
    "postgresql": ("#26215C", "#FF9966", "#BBAAFF", "#8888CC", "#555588"),
    "mysql":      ("#0D3D2B", "#3DAF85", "#88DDBB", "#559977", "#2D6644"),
    "oracle":     ("#2A1A00", "#D4860A", "#EFC97A", "#AA7733", "#775522"),
    "ai":         ("#7B1E3C", "#FF6688", "#FFAABB", "#CC8899", "#885566"),
    "dba":        ("#1A2E3D", "#5B9FD4", "#AACCEE", "#6688AA", "#445566"),
    "ops":        ("#1C2B1C", "#5DC87A", "#99DD99", "#558855", "#334433"),
    "infra":      ("#1A1A2E", "#8888FF", "#BBBBFF", "#6666AA", "#444466"),
    "xinchuang":  ("#2E1A00", "#CC6600", "#FFBB77", "#AA7744", "#664422"),
}

TAG_COLORS = [
    ("#FFF0E8", "#FF9966", "#FF9966"),   # 橙
    ("#EEEDFE", "#AFA9EC", "#6B65C4"),   # 紫
    ("#E1F5EE", "#5DCAA5", "#1A7A55"),   # 绿
    ("#FAEEDA", "#EF9F27", "#B07000"),   # 琥珀
]

# ─── 文字换行 ────────────────────────────────────────────────────────────────

def split_title(title: str, max_chars: int = 13) -> list[str]:
    """
    把标题按 max_chars 字符数分行（中文=1，ASCII=0.5）
    优先在标点/空格处断行
    """
    lines, cur, cur_w = [], "", 0
    breaks = set("，。：；—— ·")
    for ch in title:
        w = 0.5 if ch.isascii() else 1
        if cur_w + w > max_chars:
            # 尝试找最近的断点往后退
            for i in range(len(cur) - 1, max(len(cur) - 4, -1), -1):
                if cur[i] in breaks or cur[i] == " ":
                    lines.append(cur[:i + 1].rstrip())
                    cur, cur_w = cur[i + 1:], sum(0.5 if c.isascii() else 1 for c in cur[i + 1:])
                    break
            else:
                lines.append(cur)
                cur, cur_w = "", 0
        cur += ch
        cur_w += w
    if cur:
        lines.append(cur)
    return lines[:3]   # 最多 3 行


# ─── SVG 生成 ────────────────────────────────────────────────────────────────

def make_cover_svg(
    title: str,
    subtitle: str = "",
    category: str = "pg",
    tags: list[str] = None,
) -> str:
    W, H = 900, 383
    LEFT_W = 280
    RIGHT_X = LEFT_W + 40
    RIGHT_W = W - RIGHT_X - 50

    cat_key  = category.lower().strip()
    cat_abbr, cat_label = CATEGORIES.get(cat_key, ("DB", "DATABASE"))
    left_bg, accent, label_clr, brand_clr, brand_sub_clr = CAT_STYLES.get(
        cat_key, ("#26215C", "#FF9966", "#BBAAFF", "#8888CC", "#555588")
    )
    tags = tags or []

    # 标题换行
    title_lines = split_title(title, max_chars=13)
    n_lines = len(title_lines)

    # 标题块垂直居中（副标题存在时上移）
    title_font = 36 if n_lines <= 2 else 30
    line_h     = title_font * 1.35
    sub_h      = 30 if subtitle else 0
    tag_h      = 38 if tags else 0
    content_h  = n_lines * line_h + (16 if subtitle else 0) + sub_h + (12 if tags else 0) + tag_h
    title_y0   = (H - content_h) / 2 + title_font   # baseline of first line

    lines_svg = ""
    for i, line in enumerate(title_lines):
        y = title_y0 + i * line_h
        lines_svg += (
            f'  <text x="{RIGHT_X}" y="{y:.0f}" font-size="{title_font}" '
            f'font-weight="bold" fill="#26215C">{xml_escape(line)}</text>\n'
        )

    sub_svg = ""
    if subtitle:
        sub_y = title_y0 + n_lines * line_h + 16
        sub_svg = (
            f'  <text x="{RIGHT_X}" y="{sub_y:.0f}" font-size="16" fill="#666">'
            f'{xml_escape(subtitle)}</text>\n'
        )

    tags_svg = ""
    if tags:
        tag_y_rect = title_y0 + n_lines * line_h + (16 + sub_h + 12 if subtitle else 12)
        tag_x = RIGHT_X
        for i, tag in enumerate(tags[:3]):
            bg, border, fg = TAG_COLORS[i % len(TAG_COLORS)]
            tag_w = len(tag) * 13 + 24
            tags_svg += (
                f'  <rect x="{tag_x}" y="{tag_y_rect:.0f}" width="{tag_w}" height="26" '
                f'fill="{bg}" stroke="{border}" stroke-width="1" rx="4"/>\n'
                f'  <text x="{tag_x + tag_w / 2:.0f}" y="{tag_y_rect + 17:.0f}" '
                f'font-size="13" fill="{fg}" text-anchor="middle" font-weight="bold">'
                f'{xml_escape(tag)}</text>\n'
            )
            tag_x += tag_w + 10

    # 左侧色块的大字垂直居中
    abbr_len   = len(cat_abbr)
    abbr_font  = 48 if abbr_len <= 2 else (38 if abbr_len == 3 else 30)

    svg = f"""<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" font-family="PingFang SC, -apple-system, sans-serif">

  <!-- White background -->
  <rect width="{W}" height="{H}" fill="#FAFAFA"/>

  <!-- Left color block -->
  <rect width="{LEFT_W}" height="{H}" fill="{left_bg}"/>

  <!-- Decorative dots -->
  <circle cx="46" cy="46" r="4" fill="{accent}" opacity="0.6"/>
  <circle cx="72" cy="46" r="4" fill="{accent}" opacity="0.3"/>
  <circle cx="98" cy="46" r="4" fill="{accent}" opacity="0.15"/>
  <circle cx="46" cy="72" r="4" fill="{accent}" opacity="0.3"/>
  <circle cx="72" cy="72" r="4" fill="{accent}" opacity="0.15"/>
  <circle cx="46" cy="98" r="4" fill="{accent}" opacity="0.15"/>

  <!-- Left: category label -->
  <text x="{LEFT_W // 2}" y="158" font-size="13" fill="{label_clr}" text-anchor="middle" letter-spacing="3">{xml_escape(cat_label)}</text>
  <line x1="36" y1="174" x2="{LEFT_W - 36}" y2="174" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
  <text x="{LEFT_W // 2}" y="{174 + abbr_font * 0.85:.0f}" font-size="{abbr_font}" font-weight="bold" fill="white" text-anchor="middle">{xml_escape(cat_abbr)}</text>
  <line x1="36" y1="{174 + abbr_font * 1.6:.0f}" x2="{LEFT_W - 36}" y2="{174 + abbr_font * 1.6:.0f}" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>

  <!-- Left: branding -->
  <text x="{LEFT_W // 2}" y="328" font-size="13" fill="{brand_clr}" text-anchor="middle">DB小匠</text>
  <text x="{LEFT_W // 2}" y="348" font-size="11" fill="{brand_sub_clr}" text-anchor="middle">数据库·AI·工程实践</text>

  <!-- Right: top accent -->
  <rect x="{RIGHT_X}" y="52" width="72" height="5" fill="{accent}" rx="2"/>

  <!-- Right: title lines -->
{lines_svg}
  <!-- Right: subtitle -->
{sub_svg}
  <!-- Right: tags -->
{tags_svg}
</svg>"""
    return svg


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="生成微信文章封面 SVG")
    parser.add_argument("title",  help="文章标题")
    parser.add_argument("output", help="输出 SVG 路径")
    parser.add_argument("--sub",  default="", help="副标题（可选）")
    parser.add_argument("--cat",  default="pg", help="分类: pg/mysql/ai/dba/ops/xinchuang/...")
    parser.add_argument("--tags", default="", help="标签，逗号分隔，最多3个")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    svg  = make_cover_svg(args.title, args.sub, args.cat, tags)

    out = Path(args.output)
    out.write_text(svg, encoding="utf-8")
    print(f"封面已生成: {out}")


if __name__ == "__main__":
    main()
