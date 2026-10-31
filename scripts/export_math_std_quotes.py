# -*- coding: utf-8 -*-
"""导出「本册单元点已用课标引用」参考表（docs/math-std-quotes.md）。

用途：课时级建点时，`standards` 不许自拟 —— 只能从本册单元点已回表逐字命中的条目里挑，
quote 原样照抄（含 sourceLine）。这样 quote 回表 100% 命中由构造保证。
"""
import json
import os
from collections import OrderedDict

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
LINES = f"{REPO}/docs/math-std-lines.json"   # backfill_math_std_lines.py 产出：被截断/缺行号的条目订正
TS = f"{REPO}/data/math/topics.json"
OUT = f"{REPO}/docs/math-std-quotes.md"
ORDER = ["一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
         "四年级上册", "四年级下册", "五年级上册", "五年级下册", "六年级上册", "六年级下册",
         "七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册", "九年级下册",
         "必修第1册", "必修第2册", "选必第1册", "选必第2册", "选必第3册"]


def book_of(chapter):
    return (chapter or "").split(" ")[0]


def main():
    fix = json.load(open(LINES, encoding="utf-8")) if os.path.exists(LINES) else {}
    topics = json.load(open(TS, encoding="utf-8"))
    books = OrderedDict()
    for t in topics:
        b = book_of(t.get("chapter"))
        bucket = books.setdefault(b, OrderedDict())
        for s in (t.get("standards") or []):
            sid, q, ln = s.get("id"), s.get("quote"), s.get("sourceLine")
            if not (sid and q):
                continue
            bf = fix.get(f"{sid}||{q}")
            if bf:                      # 有回填则以回填为准（含整句订正）
                q = bf.get("quote") or q
                ln = bf["line"]
            key = (sid, q)
            if key not in bucket:
                bucket[key] = ln
    lines = ["# 数学：本册单元点已用课标引用（课时级建点的唯一取材来源）", "",
             "规则：课时点的 `standards` 只能从**本册**下面的条目里挑，`quote` 与 `sourceLine` 原样照抄，",
             "不许改字、不许拼接、不许自拟。挑不到贴切的条目就沿用同单元那一条（导学段也允许沿用）。", ""]
    for b in ORDER + [k for k in books if k not in ORDER]:
        if b not in books:
            continue
        lines.append(f"## {b}")
        lines.append("")
        for (sid, q), ln in books[b].items():
            lines.append(f"- `{sid}` · sourceLine {ln}")
            lines.append(f"  > {q}")
        lines.append("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"✅ {OUT}：{len(books)} 册 / {sum(len(v) for v in books.values())} 条引用")


if __name__ == "__main__":
    main()
