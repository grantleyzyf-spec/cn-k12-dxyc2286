#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从《义务教育化学课程标准（2022年版2025年修订）》TXT 抽取【内容要求】条目池。

产物：data/_chem2022_items.json —— [{id, theme, code, title, quote, sourceLine}]
· id      = "che-2022:<code>"（code 为课标原文编号，如 2.2.1）
· quote   = 该条目正文（**已去除全部空白并拼接**，与门禁的归一化口径一致，可逐字回表）
· sourceLine = 编号行在 TXT 中的行号（1-based）
"""
import json
import os
import re

SRC = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "_chem2022_items.json")
HEAD = re.compile(r"^(\d+(?:\.\d+)+)\s*(\S.*)$")
STOP = ("【学业要求】", "【教学提示】", "【内容要求】")


def norm(s):
    return re.sub(r"[\s\u3000]+", "", s)


def main():
    lines = open(SRC, encoding="utf-8").read().splitlines()
    items, cur, in_block = [], None, False
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s.startswith("【内容要求】"):
            in_block, cur = True, None
            continue
        if in_block and any(s.startswith(x) for x in STOP[0:2]):
            if cur:
                items.append(cur)
            in_block, cur = False, None
            continue
        if not in_block:
            continue
        m = HEAD.match(s)
        if m and len(s) < 60:
            if cur:
                items.append(cur)
            code, title = m.group(1), m.group(2).strip()
            cur = {"id": "che-2022:" + code, "code": code, "theme": int(code.split(".")[0]),
                   "title": title, "body": [s], "sourceLine": i + 1}
        elif cur and s:
            cur["body"].append(s)
    if cur:
        items.append(cur)

    out = []
    for it in items:
        q = norm("".join(it["body"]))
        # 去掉开头编号与标题（保留纯正文，更贴「引文」口径）
        q = re.sub(r"^" + re.escape(it["code"]), "", q)
        q = q.replace(norm(it["title"]), "", 1)
        if len(q) < 12:
            continue
        out.append({"id": it["id"], "theme": it["theme"], "code": it["code"],
                    "title": it["title"], "quote": q, "sourceLine": it["sourceLine"]})

    whole = norm("\n".join(lines))
    bad = [x["id"] for x in out if x["quote"] not in whole]
    print("抽出条目 %d ｜ 可回表 %d ｜ 不可回表 %d %s" % (len(out), len(out) - len(bad), len(bad), bad[:5]))
    from collections import Counter
    print("按主题", dict(sorted(Counter(x["theme"] for x in out).items())))
    for x in out[:4]:
        print("  ", x["id"], x["title"][:22], "|", x["quote"][:44])
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已写入", OUT)


if __name__ == "__main__":
    main()
