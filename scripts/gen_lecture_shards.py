#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「试卷讲解」派单分片：data/<subject>/_exam_shards/_lecture_shards/K*.json

每片只装同一册的若干卷（不跨册），片内含卷面路径与考点名，写手据此写讲解。

用法：
  python3 scripts/gen_lecture_shards.py math-hujiao --per-shard 2
"""
import argparse, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--per-shard", type=int, default=2)
    a = ap.parse_args()
    D = os.path.join(ROOT, "data", a.subject)
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    tname = {t["id"]: t["name"] for t in topics}

    papers = []
    for p in sorted(glob.glob(os.path.join(D, "exams", "*", "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        if not d.get("examId"):
            continue
        ids = set()
        for sec in d.get("sections") or []:
            for it in sec.get("items") or []:
                ids.update(it.get("topicIds") or [])
        papers.append({
            "book": d.get("book") or os.path.basename(os.path.dirname(p)),
            "paper": d.get("paper") or os.path.splitext(os.path.basename(p))[0],
            "kind": d.get("kind"),
            "examId": d["examId"],
            "stage": d.get("stage") or "",
            "grade": d.get("grade") or "",
            "path": p,
            "topicNames": sorted({tname[i] for i in ids if i in tname}),
        })

    by_book = {}
    for x in papers:
        by_book.setdefault(x["book"], []).append(x)

    out_dir = os.path.join(D, "_exam_shards", "_lecture_shards")
    os.makedirs(out_dir, exist_ok=True)
    for f in glob.glob(os.path.join(out_dir, "K*.json")):
        os.remove(f)

    n = 0
    books = 0
    for book in sorted(by_book):
        xs = by_book[book]
        books += 1
        for i in range(0, len(xs), a.per_shard):
            n += 1
            chunk = xs[i:i + a.per_shard]
            d = {
                "shard": f"K{n:02d}",
                "book": book,
                "stage": chunk[0]["stage"],
                "grade": chunk[0]["grade"],
                "out_dir": os.path.join(D, "exam_lectures", book),
                "exams": chunk,
            }
            with open(os.path.join(out_dir, f"K{n:02d}.json"), "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
                f.write("\n")
    print(f"{a.subject}: 册 {books} · 卷 {len(papers)} · 分片 {n} → {out_dir}")


if __name__ == "__main__":
    main()
