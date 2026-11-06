#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中物理 描述自检：点名校对 / 字数 / 禁 Markdown。

用法：python3 scripts/check_phys_sk_desc.py data/physics-sk/_desc/八年级上册.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
HAN = re.compile(r"[\u4e00-\u9fa5]")
BAD = re.compile(r"\*\*|##|\||\$|\\frac")


def han(s):
    return len(HAN.findall(str(s)))


def main():
    if len(sys.argv) < 2:
        print("用法：check_phys_sk_desc.py <desc.json>")
        return 2
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    book = d.get("book")
    sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
    want = {t["id"]: t["name"] for t in sk
            if t["level"] == "lesson" and t["chapter"].startswith(book + " ")}
    got = {x.get("id"): x for x in (d.get("lessons") or [])}
    errs = []
    if set(got) != set(want):
        errs.append("点集合不符：缺 %s / 多 %s" % (sorted(set(want) - set(got))[:4], sorted(set(got) - set(want))[:4]))
    for tid, name in want.items():
        x = got.get(tid) or {}
        if x.get("name") and x["name"] != name:
            errs.append("%s 名称不符（%s ≠ %s）" % (tid, x["name"], name))
        n = han(x.get("description"))
        if not 40 <= n <= 120:
            errs.append("%s description %d 汉字（需 40–120）" % (name, n))
        for k in ("c1", "c2"):
            if han(x.get(k)) < 10:
                errs.append("%s %s 不足 10 汉字" % (name, k))
        for k in ("description", "c1", "c2"):
            if BAD.search(str(x.get(k) or "")):
                errs.append("%s %s 含 Markdown" % (name, k))
    if errs:
        print("❌ %d 处不合格：" % len(errs))
        for e in errs[:20]:
            print("  -", e)
        return 1
    print("✅ %s：%d 课时 · RESULT: PASS" % (book, len(want)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
