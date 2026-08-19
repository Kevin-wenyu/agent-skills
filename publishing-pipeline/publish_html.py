#!/usr/bin/env python3
"""
直接发布 HTML 文件到微信公众号草稿箱
- 自动提取 base64 图片上传到微信素材库
- 替换为微信图片 URL
- 第一张图作为封面
用法: python publish_html.py <html文件路径>
"""

import sys
import os
import re
import json
import base64
import tempfile
import requests
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VAULT = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "wechat.yaml"


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


def extract_title(html):
    """从 HTML 中提取标题"""
    # 先找 h1
    m = re.search(r'<h1[^>]*>(.+?)</h1>', html, re.DOTALL)
    if m:
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        title = re.sub(r'\s+', ' ', title)
        return title
    m = re.search(r'<title[^>]*>(.+?)</title>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    return "未命名文章"


def upload_content_image(token, image_bytes, fmt="png"):
    """上传图片到微信内容素材库，返回微信 URL"""
    ext = "jpg" if fmt in ("jpeg", "jpg") else "png"
    mime = f"image/{ext}"
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as f:
        f.write(image_bytes)
        tmp_path = f.name

    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    try:
        with open(tmp_path, "rb") as f:
            r = requests.post(url, files={"media": (f"img.{ext}", f, mime)})
        data = r.json()
        if "url" not in data:
            raise RuntimeError(f"上传图片失败: {data}")
        return data["url"]
    finally:
        os.unlink(tmp_path)


def upload_thumb(token, image_bytes, fmt="png"):
    """上传永久封面素材，返回 media_id"""
    ext = "jpg" if fmt in ("jpeg", "jpg") else "png"
    mime = f"image/{ext}"
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as f:
        f.write(image_bytes)
        tmp_path = f.name

    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    try:
        with open(tmp_path, "rb") as f:
            r = requests.post(url, files={"media": (f"cover.{ext}", f, mime)})
        data = r.json()
        if "media_id" not in data:
            raise RuntimeError(f"上传封面失败: {data}")
        return data["media_id"]
    finally:
        os.unlink(tmp_path)


def replace_base64_images(html, token):
    """提取并上传所有 base64 图片，替换为微信 URL。返回 (新HTML, thumb_media_id)"""
    pattern = re.compile(r'data:image/(png|jpeg|jpg);base64,([^"]+)')
    matches = list(pattern.finditer(html))
    print(f"  找到 {len(matches)} 张 base64 图片")

    if not matches:
        return html, None

    thumb_id = None
    result_parts = []
    last_end = 0

    for i, m in enumerate(matches):
        fmt = m.group(1)
        b64 = m.group(2)
        image_bytes = base64.b64decode(b64)
        size_kb = len(image_bytes) / 1024

        # 内容图片上传
        print(f"  [图片 {i+1}/{len(matches)}] {size_kb:.0f}KB ...", end=" ", flush=True)
        wx_url = upload_content_image(token, image_bytes, fmt)
        print(f"OK")

        # 第一张图同时作为封面
        if thumb_id is None:
            thumb_id = upload_thumb(token, image_bytes, fmt)
            print(f"  [封面] thumb_media_id: {thumb_id}")

        # 拼接替换后的内容
        result_parts.append(html[last_end:m.start()])
        result_parts.append(wx_url)
        last_end = m.end()

    result_parts.append(html[last_end:])
    return "".join(result_parts), thumb_id


def delete_draft_by_title(token, title):
    """删除草稿箱中同名草稿"""
    list_url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    del_url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"
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
        print(f"  [草稿箱] 无同名草稿")


def create_draft(token, title, html_content, thumb_media_id=None):
    """创建草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    if len(title) > 64:
        title = title[:64]

    article = {
        "title": title,
        "content": html_content,
        "author": "DB小匠",
        "thumb_media_id": thumb_media_id or "",
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }

    payload = {"articles": [article]}
    r = requests.post(url,
                      data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                      headers={"Content-Type": "application/json; charset=utf-8"})
    data = r.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"创建草稿失败: {data}")
    return data.get("media_id")


def extract_body(html):
    """提取 HTML 中 body 内容或全部内容"""
    m = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    # No body tag, check if it's a full HTML doc
    if '<html' in html.lower():
        # strip doctype, head, html tags
        html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.I)
        html = re.sub(r'</?html[^>]*>', '', html, flags=re.I)
        html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.I | re.DOTALL)
        html = re.sub(r'</?body[^>]*>', '', html, flags=re.I)
    return html.strip()


def main():
    if len(sys.argv) < 2:
        print("用法: python publish_html.py <html文件路径>")
        sys.exit(1)

    html_path = Path(sys.argv[1])
    if not html_path.is_absolute():
        html_path = Path.cwd() / html_path
    if not html_path.exists():
        print(f"文件不存在: {html_path}")
        sys.exit(1)

    print(f"\n发布 HTML: {html_path.name}")
    print("─" * 40)

    html = html_path.read_text(encoding="utf-8")
    title = extract_title(html)
    print(f"  标题: {title}")

    cfg = load_config()
    print("[1/4] 获取 access_token...")
    token = get_access_token(cfg)

    print("[2/4] 上传图片并替换 base64...")
    html, thumb_id = replace_base64_images(html, token)

    print("[3/4] 提取内容...")
    content = extract_body(html)
    print(f"  内容长度: {len(content)} 字符")

    print("[4/4] 创建草稿...")
    delete_draft_by_title(token, title)

    draft_id = create_draft(token, title, content, thumb_media_id=thumb_id)
    print(f"  草稿 media_id: {draft_id}")

    print("\n✓ 完成！请到公众号后台「草稿箱」确认后发布。")
    print(f"  https://mp.weixin.qq.com\n")


if __name__ == "__main__":
    main()
