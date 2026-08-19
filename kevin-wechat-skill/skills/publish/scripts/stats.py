#!/usr/bin/env python3
"""
微信公众号文章数据回流（Chrome Cookie 方式）
用法:
  python stats.py             # 拉最近 20 篇
  python stats.py --count 50  # 拉最近 50 篇
"""

import sys
import json
import re
import requests
import browser_cookie3
from pathlib import Path
from datetime import datetime

SPECS      = Path(__file__).parent
STATS_FILE = SPECS / "stats.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://mp.weixin.qq.com/",
}


# ─── Cookie & Token ──────────────────────────────────────────────────────────

def get_cookies():
    """从 Chrome 读取 mp.weixin.qq.com 的 Cookie"""
    try:
        cj = browser_cookie3.chrome(domain_name="mp.weixin.qq.com")
        return cj
    except Exception as e:
        raise RuntimeError(f"读取 Chrome Cookie 失败: {e}\n请确保 Chrome 已登录 mp.weixin.qq.com")


def get_token(session: requests.Session) -> str:
    """访问后台主页，从跳转 URL 里提取 token"""
    r = session.get("https://mp.weixin.qq.com/", headers=HEADERS, allow_redirects=True)
    token_match = re.search(r"[?&]token=(\d+)", r.url)
    if token_match:
        return token_match.group(1)
    # 也可能在页面内容里
    content_match = re.search(r'"token"\s*:\s*"?(\d+)"?', r.text)
    if content_match:
        return content_match.group(1)
    raise RuntimeError(
        "无法获取 token，请确认 Chrome 已登录 mp.weixin.qq.com 且 Cookie 未过期"
    )


# ─── 文章列表 ────────────────────────────────────────────────────────────────

def fetch_article_list(session: requests.Session, token: str, count: int = 20) -> list[dict]:
    """
    拉取已发布文章列表，含阅读数/点赞数等字段
    接口: /cgi-bin/appmsgpublish
    """
    url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
    articles = []
    begin = 0
    batch = min(count, 20)

    while len(articles) < count:
        params = {
            "sub":    "list",
            "begin":  begin,
            "count":  batch,
            "token":  token,
            "lang":   "zh_CN",
            "f":      "json",
        }
        r = session.get(url, params=params, headers=HEADERS)
        data = r.json()

        if data.get("base_resp", {}).get("ret") != 0:
            err = data.get("base_resp", {})
            raise RuntimeError(f"拉取文章列表失败: {err}")

        # publish_page 是双重编码的 JSON 字符串，需要二次解析
        publish_page = data.get("publish_page", {})
        if isinstance(publish_page, str):
            publish_page = json.loads(publish_page)
        publish_list = publish_page.get("publish_list", [])
        if not publish_list:
            break

        for item in publish_list:
            # publish_info 也是双重编码字符串
            pub_info = item.get("publish_info", {})
            if isinstance(pub_info, str):
                pub_info = json.loads(pub_info)
            appmsg_list = pub_info.get("appmsg_info", [])
            # appmsgex 是带统计数据的扩展字段（如果有）
            appmsgex = item.get("appmsgex", appmsg_list)
            for article in appmsgex:
                articles.append({
                    "title":      article.get("title", ""),
                    "read_num":   article.get("read_num", 0),
                    "like_num":   article.get("like_num", 0),      # 旧版点赞
                    "old_like_num": article.get("old_like_num", 0), # 在看数
                    "comment_num": article.get("comment_num", 0),
                    "share_num":  article.get("share_num", 0),
                    "cover":      article.get("cover", ""),
                    "create_time": article.get("create_time", 0),
                    "appmsgid":   article.get("appmsgid", ""),
                    "idx":        article.get("idx", 0),
                })
                if len(articles) >= count:
                    break
            if len(articles) >= count:
                break

        begin += len(publish_list)
        if len(publish_list) < batch:
            break   # 已到末尾

    return articles


# ─── 存储 ────────────────────────────────────────────────────────────────────

def load_stats() -> dict:
    if STATS_FILE.exists():
        return json.loads(STATS_FILE.read_text(encoding="utf-8"))
    return {}


def save_stats(data: dict):
    STATS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def merge_stats(existing: dict, articles: list[dict]) -> dict:
    merged = dict(existing)
    for a in articles:
        key = a["appmsgid"] or a["title"]
        ts  = a.get("create_time", 0)
        merged[key] = {
            "title":       a["title"],
            "read_num":    a["read_num"],
            "like_num":    a["like_num"] + a["old_like_num"],
            "comment_num": a["comment_num"],
            "share_num":   a["share_num"],
            "date":        datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "",
            "appmsgid":    a["appmsgid"],
            "updated_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    return merged


# ─── 展示 ────────────────────────────────────────────────────────────────────

def print_table(stats: dict):
    rows = sorted(stats.values(), key=lambda x: x["read_num"], reverse=True)
    if not rows:
        print("  暂无数据")
        return

    def trunc(s, n=28):
        return s if len(s) <= n else s[:n - 1] + "…"

    header = f"{'标题':<30} {'阅读':>6} {'点赞':>5} {'分享':>5} {'评论':>5}  {'发布日期'}"
    print()
    print(header)
    print("─" * len(header))
    for r in rows:
        print(
            f"{trunc(r['title']):<30} "
            f"{r['read_num']:>6} "
            f"{r['like_num']:>5} "
            f"{r['share_num']:>5} "
            f"{r['comment_num']:>5}  "
            f"{r['date']}"
        )


# ─── 主流程 ──────────────────────────────────────────────────────────────────

def main():
    args  = sys.argv[1:]
    count = 20
    if "--count" in args:
        idx = args.index("--count")
        try:
            count = int(args[idx + 1])
        except (IndexError, ValueError):
            print("用法: python stats.py --count <篇数>")
            sys.exit(1)

    print(f"\n微信文章数据回流（最近 {count} 篇）")
    print("─" * 40)

    print("[1/3] 读取 Chrome Cookie...")
    cookies = get_cookies()
    session = requests.Session()
    session.cookies.update(cookies)

    print("[2/3] 获取后台 session token...")
    token = get_token(session)
    print(f"  token: {token[:6]}...")

    print(f"[3/3] 拉取文章列表...")
    articles = fetch_article_list(session, token, count)
    print(f"  共拉取 {len(articles)} 篇")

    existing = load_stats()
    merged   = merge_stats(existing, articles)
    save_stats(merged)
    print(f"  stats.json 已更新")

    print_table(merged)
    print()


if __name__ == "__main__":
    main()
