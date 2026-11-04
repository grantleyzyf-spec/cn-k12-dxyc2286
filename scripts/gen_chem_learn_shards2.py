#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：学层分片 v2——每篇自带教材节选（excerpt），工人不必再 grep/sed 整册（实测每篇光找文就要 2–4 分钟）。

用法：python3 scripts/gen_chem_learn_shards2.py
产物：data/chemistry/_learn_shards/CHEM_Lnn.json（覆盖写，带 excerpt/text_file）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")
SD = os.path.join(D, "_learn_shards")
PER_SHARD = 4
EX_LEN = 3800


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    lessons = [t for t in T if t.get("level") == "lesson"]
    by_book = {}
    for t in lessons:
        by_book.setdefault(t["chapter"].split(" ")[0], []).append(t)
    out = []
    n = 0
    for book, pts in sorted(by_book.items(), key=lambda kv: list(by_book).index(kv[0])):
        tp = os.path.join(D, "_text", f"{book}.txt")
        raw = open(tp, encoding="utf-8", errors="ignore").read() if os.path.exists(tp) else ""
        flat = norm(raw)
        for i in range(0, len(pts), PER_SHARD):
            grp = pts[i:i + PER_SHARD]
            n += 1
            tag = f"CHEM_L{n:02d}"
            items = []
            for k, t in enumerate(grp):
                key = norm(t["name"].split("——")[0])[:12]
                pos = flat.find(key) if key else -1
                if pos < 0:
                    excerpt = ""
                else:
                    # 取本节起点到下一节起点（或 EX_LEN）
                    nxt = nth_next(grp, k, flat)
                    end = pos + EX_LEN
                    if nxt and nxt > pos:
                        end = min(end, nxt)
                    excerpt = flat[pos:pos + (end - pos)]
                items.append({"topicId": t["id"], "title": t["name"], "chapter": t["chapter"],
                              "description": t.get("description", ""),
                              "mastery_criteria": t.get("mastery_criteria", []),
                              "standards": [s.get("quote") for s in (t.get("standards") or [])],
                              "excerpt": excerpt[:EX_LEN]})
            payload = {"shard": tag, "subject": "chemistry", "book": book,
                       "text_file": f"data/chemistry/_text/{book}.txt",
                       "out": f"data/chemistry/learn/_parts/{book}/",
                       "lessons": items}
            with open(os.path.join(SD, f"{tag}.json"), "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            out.append({"shard": tag, "book": book, "n": len(grp),
                        "topics": [t["id"] for t in grp],
                        "missing_excerpt": [t["title"] for t in items if not t["excerpt"]]})
    with open(os.path.join(SD, "_INDEX.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    miss = sum(len(x["missing_excerpt"]) for x in out)
    print(f"学层分片 {len(out)} / 篇 {sum(x['n'] for x in out)}；节选缺失 {miss}")
    for x in out:
        if x["missing_excerpt"]:
            print("  缺节选", x["shard"], x["missing_excerpt"])


def nth_next(grp, k, flat):
    """下一个课时在本册全文中的位置（用于裁短节选）。"""
    for j in range(k + 1, len(grp)):
        key = norm(grp[j]["name"].split("——")[0])[:12]
        p = flat.find(key)
        if p > 0:
            return p
    return None


if __name__ == "__main__":
    main()
