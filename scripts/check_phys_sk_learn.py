#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中物理（physics-sk）学层精讲校验器。

用法：
  python3 scripts/check_phys_sk_learn.py data/physics-sk/learn/_parts/T01.json
  python3 scripts/check_phys_sk_learn.py data/physics-sk/learn/七年级上册.json
  python3 scripts/check_phys_sk_learn.py --dir data/physics-sk/learn/_parts

七段固定（标题逐字）：一、开场 / 二、课本原文 / 三、费曼翻译 / 四、例题精讲 / 五、易错点拨 / 六、五步学习法 / 七、自查清单
判据：全篇 1200–2600 汉字；五步节 350–700；五条固定序逐字；课本原文 `> ` 引文 ≥2 处且**逐字回表**到该册 textpack；
      自查 `- [ ]` ≥3；例题含 ❌ 与 ✅；禁 `** ## | $ \\`；禁元话语（扫描件/OCR/抽取/切片/文字层/残片）。
回表源：data/physics-sk/_text/<册>.txt（本桶教材全文，含 [[pN]] 页标）；缺失时回落到旧 TXT_ROOT。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
TXT_ROOT = os.path.expanduser(
    "~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/苏科版/初中")
SEC = ["开场", "课本原文", "费曼翻译", "例题精讲", "易错点拨", "五步学习法", "自查清单"]
STEPS = ["每天锻炼一个", "扎实掌握第一个知识点", "能积微者速成", "对标思维", "杠铃法则"]
BAD = re.compile(r"\*\*|\||\\frac|\$")
META = re.compile(r"扫描件|OCR|抽取|切片|文字层|残片")


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", str(s)))


def qnorm(s):
    return re.sub(r"[\s\u3000，。、；：“”‘’（）()《》！？—…·]", "", str(s))


_cache = {}


def book_src(book):
    if book in _cache:
        return _cache[book]
    parts = []
    local = os.path.join(D, "_text", "%s.txt" % book)
    if os.path.exists(local):
        parts.append(open(local, encoding="utf-8", errors="ignore").read())
    else:
        base = os.path.join(TXT_ROOT, book)
        full = os.path.join(base, "整册全文.txt")
        if os.path.exists(full):
            parts.append(open(full, encoding="utf-8", errors="ignore").read())
        else:
            for p in sorted(glob.glob(os.path.join(base, "ocr", "p*.txt"))):
                parts.append(open(p, encoding="utf-8", errors="ignore").read())
    _cache[book] = qnorm("".join(parts))
    return _cache[book]


def check_lesson(les, out):
    md = les.get("markdown") or ""
    book = les.get("book") or ""
    tid = les.get("topicId") or "?"
    w = han(md)
    if not (1200 <= w <= 2600):
        out.append(f"{tid} 字数 {w} ∉1200–2600")
    if les.get("words") is not None and abs((les.get("words") or 0) - w) > 5:
        out.append(f"{tid} words 标注 {les.get('words')} ≠ 实测 {w}")
    for s in SEC:
        if s not in md:
            out.append(f"{tid} 缺段「{s}」")
    pos = [md.find(s) for s in SEC]
    if all(p >= 0 for p in pos) and pos != sorted(pos):
        out.append(f"{tid} 七段顺序错")
    tail = md.split("五步学习法", 1)[-1] if "五步学习法" in md else ""
    for st in STEPS:
        if st not in tail:
            out.append(f"{tid} 五步缺「{st}」")
    wstep = han(tail.split("七、")[0]) if tail else 0
    if not (350 <= wstep <= 700):
        out.append(f"{tid} 五步节 {wstep} ∉350–700")
    if md.count("- [ ]") < 3:
        out.append(f"{tid} 自查勾选 <3")
    if "❌" not in md or "✅" not in md:
        out.append(f"{tid} 例题缺 ❌/✅")
    if BAD.search(md):
        out.append(f"{tid} 含 Markdown/LaTeX 字符")
    if META.search(md):
        out.append(f"{tid} 含元话语（扫描件/OCR/切片…）")
    quotes = re.findall(r"^>\s*(.+)$", md, re.M)
    if len(quotes) < 2:
        out.append(f"{tid} 课本原文引文 <2 处")
    src = book_src(book) if book else ""
    if src:
        for q in quotes:
            body = q.strip()
            if body.startswith("【"):
                body = body.lstrip("【").split("】", 1)[-1]
            if qnorm(body) and qnorm(body) not in src:
                out.append(f"{tid} 引文未逐字回表：{body[:18]}")


def load_lessons(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, list):
        return d
    if "lessons" in d:
        return d["lessons"]
    return [d]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    if sys.argv[1] == "--dir":
        files = sorted(glob.glob(os.path.join(sys.argv[2], "*.json")))
    else:
        files = [sys.argv[1]]
    errs, n = [], 0
    for p in files:
        for les in load_lessons(p):
            n += 1
            check_lesson(les, errs)
    if errs:
        print(f"❌ {n} 篇 · 不合格 {len(errs)} 条")
        for e in errs[:25]:
            print("  -", e)
        print("RESULT: FAIL")
        return 1
    print(f"✅ {n} 篇 · 不合格 0")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
