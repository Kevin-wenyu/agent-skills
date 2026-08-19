#!/usr/bin/env python3
"""
Obsidian → 微信公众号 自动发布脚本
用法: python publish.py <文章路径.md>
"""

import sys
import os
import re
import subprocess
import yaml
import json
import time
import requests
import markdown
import css_inline
from pathlib import Path

VAULT = Path(__file__).parent.parent
CONFIG_FILE = Path(__file__).parent / "wechat.yaml"

# ─── 微信 CSS（全部内联，微信会过滤 <style> 标签）────────────────
WECHAT_CSS = """
<style>
  body    { font-family: 'PingFang SC', -apple-system, sans-serif; font-size: 15px; line-height: 1.75; color: #333; }
  h2      { font-size: 16px; font-weight: bold; color: #fff; background: #FF9966; padding: 8px 14px; margin: 22px 0 10px; line-height: 1.5; border-radius: 4px; }
  h3      { font-size: 15px; font-weight: bold; color: #FF9966; border-left: 3px solid #FF9966; padding-left: 8px; margin: 16px 0 6px; line-height: 1.5; }
  p       { margin: 6px 0; padding: 0; font-size: 15px; line-height: 1.75; color: #333; }
  blockquote { background: #FFF6F2; border-left: 4px solid #FF9966; margin: 12px 0; padding: 8px 14px; color: #555; font-size: 14px; line-height: 1.7; }
  blockquote p { margin: 0; padding: 0; font-size: 14px; color: #555; }
  code    { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'Menlo', 'Courier New', monospace; font-size: 13px; color: #c0392b; }
  pre     { background: #f6f8fa; color: #333; border: 1px solid #e1e4e8; border-radius: 6px; padding: 12px 14px; margin: 12px 0; line-height: 1.6; }
  pre code { background: none; color: inherit; padding: 0; font-size: 11px; }
  table   { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; overflow-wrap: break-word; table-layout: fixed; }
  th      { background: #FF9966; color: #fff; padding: 6px 6px; text-align: left; font-weight: bold; font-size: 13px; }
  td      { padding: 5px 6px; border-bottom: 1px solid #f0e8e8; font-size: 13px; overflow-wrap: break-word; }
  tr:nth-child(even) td { background: #FFF8F5; }
  img     { width: 100%; max-width: 100%; display: block; margin: 14px auto; border-radius: 6px; }
  hr      { border: none; border-top: 1px solid #e8e8e8; margin: 16px 0; }
  strong  { font-weight: bold; color: #FF9966; }
  em      { font-style: italic; color: #555; }
  .footnote { margin-top: 24px; }
  .footnote hr { margin: 20px 0 12px; }
  .footnote ol { padding-left: 20px; margin: 0; }
  .footnote li { margin: 4px 0; line-height: 1.6; }
  .footnote li p { font-size: 13px; color: #888; margin: 0; }
  .footnote-ref { color: #FF9966; text-decoration: none; font-size: 12px; }
  .footnote-backref { color: #FF9966; text-decoration: none; }
</style>
"""


def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def get_access_token(cfg):
    url = "https://api.weixin.qq.com/cgi-bin/token"
    r = requests.get(url, params={
        "grant_type": "client_credential",
        "appid": cfg["app_id"],
        "secret": cfg["app_secret"],
    })
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"获取 token 失败: {data}")
    return data["access_token"]


def svg_to_png(svg_path: Path) -> Path:
    """用 rsvg-convert 渲染 SVG 为 PNG，2x 分辨率。无浏览器依赖，比 Playwright 更轻量。"""
    png_path = svg_path.with_suffix(".png")
    result = subprocess.run(
        ["rsvg-convert", "--zoom", "2", str(svg_path), "-o", str(png_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"rsvg-convert 失败: {svg_path.name}\n{result.stderr}")
    return png_path


def upload_image(token: str, image_path: Path) -> str:
    """上传图片到微信（临时素材），返回可直接用于 content 的 URL"""
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    with open(image_path, "rb") as f:
        r = requests.post(url, files={"media": (image_path.name, f, "image/png")})
    data = r.json()
    if "url" not in data:
        raise RuntimeError(f"上传图片失败: {data}")
    return data["url"]


def upload_thumb(token: str, image_path: Path) -> str:
    """上传永久封面素材，返回 media_id（草稿 thumb_media_id 必须用这个）"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    with open(image_path, "rb") as f:
        r = requests.post(url, files={"media": (image_path.name, f, "image/png")})
    data = r.json()
    if "media_id" not in data:
        raise RuntimeError(f"上传封面失败: {data}")
    return data["media_id"]


def parse_article(md_path: Path):
    text = md_path.read_text(encoding="utf-8")

    # 去掉 frontmatter，提取 title
    title = md_path.stem
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if fm_match:
        fm_body = fm_match.group(1)
        text = text[fm_match.end():]
        # 优先从 frontmatter 的 title 字段取标题
        title_match = re.search('^title:\\s*["\']([^"\']+)["\']\\s*$', fm_body, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

    # 提取 H1 作为标题，并从正文中删除（微信已显示文章标题，不重复）
    h1_match = re.search(r"^# (.+)\n?", text, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()
        text = text[:h1_match.start()] + text[h1_match.end():]

    return title, text


def embed_svg_inline(svg_path: Path) -> str:
    """读取 SVG，注入 viewBox + 响应式宽度，直接内联到 HTML（保持矢量质量）"""
    content = svg_path.read_text(encoding="utf-8")
    # 补 viewBox（没有 viewBox 时 width=100% 无法等比缩放）
    if 'viewBox' not in content:
        w = re.search(r'<svg\b[^>]+\bwidth=["\'](\d+)["\']', content)
        h = re.search(r'<svg\b[^>]+\bheight=["\'](\d+)["\']', content)
        if w and h:
            content = content.replace('<svg ', f'<svg viewBox="0 0 {w.group(1)} {h.group(1)}" ', 1)
    # 响应式宽度
    content = re.sub(r'(<svg\b[^>]+)\bwidth="[^"]*"', r'\1 width="100%"', content)
    content = re.sub(r'(<svg\b[^>]+)\bheight="[^"]*"', r'\1 height="auto"', content)
    return f'<section style="margin:14px 0;line-height:0;">{content}</section>'


def process_images(md_text: str, article_dir: Path, token: str):
    """找出文中所有 ![[xxx.svg]]：
    - 第一张（封面）转 PNG 上传，获取 thumb_media_id（微信 API 要求）
    - 其余图片直接内联 SVG，保持矢量清晰度
    返回 (处理后的 md_text, 第一张图的 thumb_media_id)
    """
    pattern = re.compile(r"!\[\[([^\]]+\.svg)\]\]")
    first_thumb_id = None

    def replace(m):
        nonlocal first_thumb_id
        svg_name = m.group(1)
        svg_path = VAULT / "assets" / "svg" / svg_name
        if not svg_path.exists():
            svg_path = article_dir / svg_name
        if not svg_path.exists():
            svg_path = article_dir.parent / "attachments" / svg_name
        if not svg_path.exists():
            print(f"  [跳过] 找不到图片: {svg_name}")
            return ""
        # 第一张图：转 PNG 上传作为封面素材
        if first_thumb_id is None:
            print(f"  [封面] 转 PNG 上传: {svg_name}")
            png_path = svg_to_png(svg_path)
            first_thumb_id = upload_thumb(token, png_path)
            png_path.unlink()
            return ""   # 封面图不在正文中显示
        # 正文图：转 PNG 上传，支持微信点击放大
        print(f"  [正文图] 转 PNG 上传: {svg_name}")
        png_path = svg_to_png(svg_path)
        img_url = upload_image(token, png_path)
        png_path.unlink()
        return f'<img src="{img_url}" style="width:100%;max-width:100%;display:block;margin:14px auto;border-radius:6px;" />'

    new_text = pattern.sub(replace, md_text)
    return new_text, first_thumb_id


def _lists_to_p(html: str) -> str:
    """把 <ul>/<ol> 转成 <p> + 字符 bullet，微信渲染最稳定"""
    from html.parser import HTMLParser

    class ListConverter(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.out = []
            self.in_ul = False
            self.in_ol = False
            self.ol_counter = 0
            self.in_li = False
            self.li_buf = []

        def handle_starttag(self, tag, attrs):
            attr_str = "".join(f' {k}="{v}"' for k, v in attrs)
            if tag == "ul":
                self.in_ul = True
            elif tag == "ol":
                self.in_ol = True
                self.ol_counter = 0
            elif tag == "li" and (self.in_ul or self.in_ol):
                self.in_li = True
                self.li_buf = []
                if self.in_ol:
                    self.ol_counter += 1
            else:
                raw = f"<{tag}{attr_str}>"
                if self.in_li:
                    self.li_buf.append(raw)
                else:
                    self.out.append(raw)

        def handle_endtag(self, tag):
            if tag == "ul":
                self.in_ul = False
            elif tag == "ol":
                self.in_ol = False
            elif tag == "li" and (self.in_ul or self.in_ol):
                self.in_li = False
                content = "".join(self.li_buf).strip()
                # footnotes 扩展会把 <li> 内容包一层 <p>（"loose list"），
                # 这里再套一层 <p> 会形成 <p><p>...</p></p> 嵌套，微信解析会截断，
                # 数字/圆点跟内容错位——先拆掉这层内层 <p>，避免嵌套
                inner_p = re.match(r"^<p[^>]*>(.*)</p>$", content, re.DOTALL)
                if inner_p:
                    content = inner_p.group(1)
                li_style = (
                    "margin:6px 0;line-height:1.75;font-size:15px;color:#333;"
                    "padding-left:0;"
                )
                if self.in_ol:
                    bullet = f"{self.ol_counter}."
                else:
                    bullet = "•"
                self.out.append(
                    f'<p style="{li_style}">'
                    f'<span style="margin-right:6px;">{bullet}</span>{content}</p>'
                )
            else:
                raw = f"</{tag}>"
                if self.in_li:
                    self.li_buf.append(raw)
                else:
                    self.out.append(raw)

        def handle_data(self, data):
            if self.in_li:
                self.li_buf.append(data)
            else:
                self.out.append(data)

        def handle_entityref(self, name):
            ref = f"&{name};"
            (self.li_buf if self.in_li else self.out).append(ref)

        def handle_charref(self, name):
            ref = f"&#{name};"
            (self.li_buf if self.in_li else self.out).append(ref)

    parser = ListConverter()
    parser.feed(html)
    return "".join(parser.out)


def _fix_pre_blocks(html: str) -> str:
    """把 <pre> 包在横向可滚动容器里，超长行左右拖动查看"""
    # 仿 mdnice 结构：overflow-x:auto + display:-webkit-box 加在 code 元素上
    # 这是微信 WebKit 引擎实际支持的横向滚动组合
    pre_style = (
        "border-radius:5px;"
        "box-shadow:rgba(0,0,0,0.45) 0px 4px 14px;"
        "border:1px solid #3a3f4b;"
        "margin:14px 0;"
        "padding:0;"
        "text-align:left;"
        "overflow:hidden;"
    )
    header_style = (
        "display:block;"
        "height:32px;"
        "width:100%;"
        "background-color:#1e2227;"
        "border-radius:5px 5px 0 0;"
        "padding:10px 12px;"
        "box-sizing:border-box;"
        "line-height:12px;"
    )
    dot_red    = "color:#ff5f57;font-size:16px;line-height:1;margin-right:6px;"
    dot_yellow = "color:#ffbd2e;font-size:16px;line-height:1;margin-right:6px;"
    dot_green  = "color:#28ca41;font-size:16px;line-height:1;"
    code_style = (
        "overflow-x:auto;"
        "padding:16px;"
        "color:#abb2bf;"
        "background:#282c34;"
        "display:-webkit-box;"
        "font-family:'Menlo','Courier New',monospace;"
        "font-size:12px;"
        "line-height:1.6;"
    )

    def replace_pre(m):
        inner = m.group(1)
        lines = inner.split("\n")
        converted = []
        for line in lines:
            n = len(line) - len(line.lstrip(" "))
            converted.append("&nbsp;" * n + line[n:])
        inner = "<br>".join(converted)
        return (
            f'<pre style="{pre_style}">'
            f'<span style="{header_style}">'
            f'<span style="{dot_red}">●</span>'
            f'<span style="{dot_yellow}">●</span>'
            f'<span style="{dot_green}">●</span>'
            f'</span>'
            f'<code style="{code_style}">{inner}</code>'
            f'</pre>'
        )

    html = re.sub(
        r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
        replace_pre,
        html,
        flags=re.DOTALL,
    )
    return html


def _strip_footnote_anchors(html: str) -> str:
    """去掉脚注的页内跳转锚点（id="fnref:N" / href="#fn:N" 这类），
    微信草稿接口会把这种结构判定成非法内容（errcode 45166），
    而且微信文章阅读也用不上"点数字跳文末、点↩跳回来"这种网页交互，
    只保留视觉效果：上标数字 + 文末编号列表。"""
    # 正文里的引用角标：<sup id="fnref:1"><a class="footnote-ref" href="#fn:1">1</a></sup>
    html = re.sub(
        r'<sup id="fnref\d*:\w+"><a class="footnote-ref" href="#fn:\w+">(\d+)</a></sup>',
        r'<sup class="footnote-ref">\1</sup>',
        html,
    )
    # 文末列表项：<li id="fn:1"> → <li>
    html = re.sub(r'<li id="fn:\w+">', '<li>', html)
    # 跳回箭头：<a class="footnote-backref" ...>↩</a>——同一条脚注被多次引用时会连续重复几个，
    # 只有第一个前面带 &#160; 分隔符，后面几个是直接紧贴的，要能都删掉
    html = re.sub(r'<a class="footnote-backref"[^>]*>(?:&#8617;|↩)</a>', '', html)
    html = re.sub(r'&#160;(?=</p>)', '', html)  # 删完箭头后清理落单的分隔符
    return html


def md_to_html(md_text: str) -> str:
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "footnotes"],
    )
    body_html = _strip_footnote_anchors(body_html)
    full_html = f"<html><head>{WECHAT_CSS}</head><body>{body_html}</body></html>"
    inliner = css_inline.CSSInliner()
    inlined = inliner.inline(full_html)
    body_match = re.search(r"<body[^>]*>(.*?)</body>", inlined, re.DOTALL)
    content = body_match.group(1).strip() if body_match else inlined
    content = _lists_to_p(content)
    content = _fix_pre_blocks(content)
    return content


def create_draft(token: str, title: str, html: str, thumb_media_id: str = None):
    """创建草稿，含原创声明、留言、创作来源"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    if len(title) > 64:
        title = title[:64]

    article = {
        "title":                title,
        "content":              html,
        "author":               "DB小匠",
        "thumb_media_id":       thumb_media_id or "",
        "need_open_comment":    1,   # 开启留言
        "only_fans_can_comment": 0,  # 所有人可留言
    }

    payload = {"articles": [article]}
    r = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                      headers={"Content-Type": "application/json; charset=utf-8"})
    data = r.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"创建草稿失败: {data}")
    return data.get("media_id")



def delete_draft_by_title(token: str, title: str):
    """删除草稿箱中与 title 同名的草稿（可能有多篇）"""
    list_url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    del_url  = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"
    offset, deleted = 0, 0
    while True:
        r = requests.post(list_url, json={"offset": offset, "count": 20, "no_content": 1})
        data = r.json()
        items = data.get("item", [])
        if not items:
            break
        for item in items:
            draft_title = item.get("content", {}).get("news_item", [{}])[0].get("title", "")
            if draft_title == title:
                mid = item["media_id"]
                dr = requests.post(del_url, json={"media_id": mid})
                if dr.json().get("errcode", 0) == 0:
                    deleted += 1
                    print(f"  [删除旧草稿] {draft_title} ({mid[:16]}...)")
        if len(items) < 20:
            break
        offset += 20
    if deleted == 0:
        print(f"  [草稿箱] 无同名草稿，直接创建")


def clear_drafts(token: str):
    """清空草稿箱（分批获取并逐一删除）"""
    list_url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    del_url  = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"
    deleted = 0
    while True:
        r = requests.post(list_url, json={"offset": 0, "count": 20, "no_content": 1})
        data = r.json()
        items = data.get("item", [])
        if not items:
            break
        for item in items:
            mid = item["media_id"]
            dr = requests.post(del_url, json={"media_id": mid})
            dr_data = dr.json()
            if dr_data.get("errcode", 0) == 0:
                deleted += 1
                print(f"  [删除] {mid}")
            else:
                print(f"  [失败] {mid}: {dr_data}")
    print(f"  共删除 {deleted} 篇草稿")


def update_frontmatter_status(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    # 只替换 frontmatter 块（第一个 --- 和第二个 --- 之间）
    fm_match = re.match(r"^(---\n)(.*?)(\n---\n)", text, re.DOTALL)
    if not fm_match:
        return
    fm = fm_match.group(2)
    new_fm = re.sub(r"(^status:\s*)draft", r"\1published", fm, flags=re.MULTILINE)
    if new_fm != fm:
        updated = text[:fm_match.start(2)] + new_fm + text[fm_match.end(2):]
        md_path.write_text(updated, encoding="utf-8")
        print(f"  [状态] status 已更新为 published")


def main():
    args = sys.argv[1:]
    clear = "--clear" in args
    args = [a for a in args if a != "--clear"]

    if not args:
        print("用法: python publish.py [--clear] <文章路径.md>")
        sys.exit(1)

    md_path = Path(args[0])
    if not md_path.is_absolute():
        md_path = VAULT / md_path
    if not md_path.exists():
        print(f"文件不存在: {md_path}")
        sys.exit(1)

    print(f"\n发布文章: {md_path.name}")
    print("─" * 40)

    cfg = load_config()
    print("[1/4] 获取 access_token...")
    token = get_access_token(cfg)

    if clear:
        print("[0/4] 清空草稿箱...")
        clear_drafts(token)

    print("[2/4] 解析文章...")
    title, md_text = parse_article(md_path)
    print(f"  标题: {title}")

    print("[3/4] 处理图片...")
    md_text, thumb_id = process_images(md_text, md_path.parent, token)

    print("[4/4] 创建草稿...")
    delete_draft_by_title(token, title)
    print(f"  thumb_media_id: {thumb_id}")
    html = md_to_html(md_text)
    draft_id = create_draft(token, title, html, thumb_media_id=thumb_id)
    print(f"  草稿 media_id: {draft_id}")

    update_frontmatter_status(md_path)

    print("\n✓ 完成！请到公众号后台「草稿箱」确认后发布。")
    print(f"  https://mp.weixin.qq.com\n")


if __name__ == "__main__":
    main()
