#!/usr/bin/env python3
"""按仓库实际页面生成 sitemap.xml（正式域名），novel 章节另见 sitemap-novel.xml。

用法：python3 scripts/build_sitemap.py [--write]
口径：
- 顶层页面（含 index.html 的一级目录）全部收录；
- teacher/ 下的详情页逐篇收录（254 篇左右，nested 目录也算）；
- novel/ 只收书架与书目，章节走 sitemap-novel.xml（避免两份重复）；
- 排除 dist/、.git/、tests/、webapp/、screenshots/。
"""
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://xueketupu.com"
SKIP_TOP = {"dist", ".git", "tests", "webapp", "screenshots", "scripts", "docs", "deploy", "data", "assets"}
PRIORITY = {"/": "1.0", "/explore/": "0.9", "/diagnose/": "0.9", "/learn/": "0.9",
            "/learn/exam/": "0.85", "/teacher/": "0.85", "/novel/": "0.7", "/children/": "0.6",
            "/contact/": "0.5"}


def pages():
    out = []
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if not os.path.isdir(p) or name in SKIP_TOP or name.startswith("."):
            continue
        if name == "novel":
            out.append("/novel/")
            if os.path.exists(os.path.join(p, "xueshen", "index.html")):
                out.append("/novel/xueshen/")
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            if "index.html" not in filenames:
                continue
            rel = "/" + os.path.relpath(dirpath, ROOT).replace(os.sep, "/") + "/"
            # 教师详情页藏在多层中文目录里，一并收录；其它深层目录（如 learn/data）不收录
            if name != "teacher" and rel.count("/") > 2:
                continue
            out.append(rel)
    # 顶层单页
    for f in ("index.html",):
        if os.path.exists(os.path.join(ROOT, f)):
            out.insert(0, "/")
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def main():
    urls = pages()
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pr = PRIORITY.get(u, "0.5" if u.startswith("/teacher/") else "0.6")
        lines += ["  <url>", f"    <loc>{SITE}{u}</loc>",
                  f"    <lastmod>{today}</lastmod>",
                  "    <changefreq>weekly</changefreq>",
                  f"    <priority>{pr}</priority>", "  </url>"]
    lines.append("</urlset>")
    xml = "\n".join(lines) + "\n"
    if "--write" in sys.argv:
        with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
            fh.write(xml)
        print(f"写入 sitemap.xml：{len(urls)} 个 URL")
    else:
        print(f"将输出 {len(urls)} 个 URL（--write 落盘）")
        for u in urls[:12]:
            print("  ", u)


if __name__ == "__main__":
    main()
