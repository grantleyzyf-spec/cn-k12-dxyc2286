# -*- coding: utf-8 -*-
"""生成 math-bj 试卷讲解分片（每片 5–6 卷，含卷面路径与题号概览）。

用法: python3 make_lecture_shards.py [--only 册名...]
输出: data/math-bj/_build/lecture_shards/T01.json …
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EX = os.path.join(ROOT, "exams")
OUT = os.path.join(HERE, "lecture_shards")
BOOKS = ["一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
         "四年级上册", "五年级上册", "六年级上册", "七年级上册", "七年级下册",
         "八年级上册", "八年级下册", "九年级上册"]
MAX = 5


def main():
    only = sys.argv[2:] if "--only" in sys.argv else None
    os.makedirs(OUT, exist_ok=True)
    rows, papers = [], []
    for book in BOOKS:
        d = os.path.join(EX, book)
        if not os.path.isdir(d):
            continue
        if only and book not in only:
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json"):
                continue
            ex = json.load(open(os.path.join(d, f), encoding="utf-8"))
            items = [it for s in ex.get("sections") or [] for it in s.get("items") or []]
            papers.append(dict(book=book, paper=ex["paper"], kind=ex.get("kind"),
                               examId=ex.get("examId"), path=os.path.join(d, f),
                               n=len(items), fullScore=ex.get("fullScore"),
                               duration=ex.get("duration"), scope=ex.get("scope"),
                               stage=ex.get("stage")))
    n = 0
    for i in range(0, len(papers), MAX):
        n += 1
        sid = f"T{n:02d}"
        chunk = papers[i:i + MAX]
        json.dump(dict(shard=sid, subject="math-bj", papers=chunk),
                  open(os.path.join(OUT, f"{sid}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        rows.append(dict(shard=sid, books=sorted({c["book"] for c in chunk}), n=len(chunk)))
    json.dump(rows, open(os.path.join(OUT, "_index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for r in rows:
        print(f"  {r['shard']} {r['n']} 卷  {'、'.join(r['books'])}")
    print("分片", len(rows), "| 卷数合计", sum(r["n"] for r in rows))


if __name__ == "__main__":
    main()
