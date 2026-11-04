#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏教版高中化学 知识点描述自检：点名校对 / 字数 / domain 枚举 / 禁 Markdown。

用法：python3 scripts/check_sujiao_desc.py data/chemistry-sujiao/_desc/必修第一册.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-sujiao")
HAM = re.compile(r"[\u4e00-\u9fa5]")
DOMAINS = {"物质的组成与结构", "物质的化学变化", "物质的性质与应用",
           "科学探究与化学实验", "化学与社会·跨学科实践"}
BAD = re.compile(r"\*\*|##|\||\$|\\frac|\\ce\{")


def han(s):
    return len(HAM.findall(str(s)))


def main():
    if len(sys.argv) < 2:
        print("用法：check_sujiao_desc.py <desc.json>")
        return 2
    p = sys.argv[1]
    d = json.load(open(p, encoding="utf-8"))
    book = d.get("book")
    struct = json.load(open(os.path.join(D, "_structure.json"), encoding="utf-8"))
    # 册名两种写法并存：_structure.json 用「选择性必修2」，_text/ 与派单用「选择性必修第二册」。
    _alias = {"选择性必修第一册": "选择性必修1", "选择性必修第二册": "选择性必修2",
              "选择性必修第三册": "选择性必修3"}
    key = book if book in struct else _alias.get(book, book)
    if key not in struct:
        print("❌ book 不在 _structure.json：%r" % book)
        return 1
    errs = []
    want = struct[key]
    got = d.get("units") or []
    if len(got) != len(want):
        errs.append("专题数 %d ≠ 表定 %d" % (len(got), len(want)))
    for w, g in zip(want, got):
        if g.get("no") != w["no"] or g.get("name") != w["name"]:
            errs.append("专题错位：期望 %s %s，得到 %s %s" % (w["no"], w["name"], g.get("no"), g.get("name")))
            continue
        if g.get("domain") not in DOMAINS:
            errs.append("%s domain 非法：%r" % (w["name"], g.get("domain")))
        gl = g.get("lessons") or []
        if len(gl) != len(w["lessons"]):
            errs.append("%s 课时数 %d ≠ 表定 %d" % (w["name"], len(gl), len(w["lessons"])))
        for wn, gg in zip(w["lessons"], gl):
            if gg.get("name") != wn:
                errs.append("%s 课时错位：期望 %s，得到 %s" % (w["name"], wn, gg.get("name")))
                continue
            desc = gg.get("description") or ""
            n = han(desc)
            if not 40 <= n <= 120:
                errs.append("%s description %d 汉字（需 40–120）" % (wn, n))
            if BAD.search(desc):
                errs.append("%s description 含 Markdown/LaTeX" % wn)
            for k in ("c1", "c2"):
                if han(gg.get(k)) < 10:
                    errs.append("%s %s 不足 10 汉字" % (wn, k))
                if BAD.search(str(gg.get(k) or "")):
                    errs.append("%s %s 含 Markdown/LaTeX" % (wn, k))
    if errs:
        print("❌ %d 处不合格：" % len(errs))
        for e in errs[:20]:
            print("  -", e)
        return 1
    nl = sum(len(u["lessons"]) for u in got)
    print("✅ %s：%d 专题 / %d 课时 · RESULT: PASS" % (book, len(got), nl))
    return 0


if __name__ == "__main__":
    sys.exit(main())
