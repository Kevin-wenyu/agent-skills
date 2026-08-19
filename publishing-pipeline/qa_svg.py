#!/usr/bin/env python3
"""SVG 质量预览：Playwright 渲染 SVG → PNG，供目检后删除。

用法（从 _specs/ 执行）：
    .venv/bin/python qa_svg.py assets/svg/foo.svg [assets/svg/bar.svg ...]

输出：每个 SVG 旁边生成 <name>_qa.png，打印路径供 Claude Read 目检。
清理：目检完成后运行 .venv/bin/python qa_svg.py --clean 删除所有 _qa.png。
"""

import sys
from pathlib import Path

VAULT = Path(__file__).parent.parent
SVG_DIR = VAULT / "assets" / "svg"


def svg_to_preview(svg_path: Path) -> Path:
    from playwright.sync_api import sync_playwright
    out_path = svg_path.with_name(svg_path.stem + "_qa.png")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-device-scale-factor=2"])
        ctx = browser.new_context(device_scale_factor=2)
        page = ctx.new_page()
        page.goto(svg_path.as_uri(), wait_until="domcontentloaded")
        size = page.evaluate("""() => {
            const svg = document.querySelector('svg');
            const wAttr = svg.getAttribute('width');
            const hAttr = svg.getAttribute('height');
            if (wAttr && hAttr && !wAttr.includes('%')) {
                return { width: parseFloat(wAttr), height: parseFloat(hAttr) };
            }
            const vb = svg.viewBox.baseVal;
            if (vb && vb.width) return { width: vb.width, height: vb.height };
            return { width: svg.width.baseVal.value, height: svg.height.baseVal.value };
        }""")
        w, h = int(size["width"]), int(size["height"])
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(500)
        page.screenshot(path=str(out_path), timeout=60000)
        browser.close()
    return out_path


def clean_qa_files():
    removed = list(SVG_DIR.glob("*_qa.png"))
    for f in removed:
        f.unlink()
    print(f"已删除 {len(removed)} 个 QA 预览文件")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--clean":
        clean_qa_files()
        sys.exit(0)

    errors = 0
    for arg in args:
        p = Path(arg)
        if not p.is_absolute():
            p = VAULT / p
        if not p.exists():
            # 也尝试 assets/svg/ 前缀
            p2 = SVG_DIR / Path(arg).name
            if p2.exists():
                p = p2
            else:
                print(f"❌ 找不到文件: {arg}")
                errors += 1
                continue
        try:
            out = svg_to_preview(p)
            print(f"✅ {p.name} → {out}")
        except Exception as e:
            print(f"❌ 渲染失败 {p.name}: {e}")
            errors += 1

    sys.exit(errors)
