# -*- coding: utf-8 -*-
"""生成 math-bj 期中 / 期末卷分片（每册一片，4 份卷：期中A·B + 期末A·B）。

用法: python3 make_exam_shards2.py
输出: data/math-bj/_build/exam_shards/M01.json …
"""
import json
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "exam_shards")
BOOKS = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "五上", "六上",
         "七上", "七下", "八上", "八下", "九上"]
CN = "一二三四五六七八九"


def main():
    topics = json.load(open(os.path.join(ROOT, "topics.json"), encoding="utf-8"))
    qs = json.load(open(os.path.join(ROOT, "questions.json"), encoding="utf-8"))
    bank = {}
    for q in qs:
        bank.setdefault(q["topicId"], []).append({"qid": q["id"], "difficulty": q.get("difficulty")})
    by_book = OrderedDict((b, []) for b in BOOKS)
    for t in topics:
        m = re.match(r"([一二三四五六七八九])年级([上下])册", t["chapter"])
        if m:
            by_book[f"{m.group(1)}{m.group(2)}"].append(t)

    idx, n = [], 0
    for book, pts in by_book.items():
        units = [u for u in pts if u["level"] == "unit"]
        formal = [u for u in units if not re.search(r"数学百花园|总复习", u["name"])]
        g = pts[0]["grade"]
        stage = "小学" if g <= 6 else "初中"
        dur = 40 if g <= 2 else 60 if g <= 6 else 90
        half = max(1, len(formal) // 2)
        n += 1
        sid = f"M{n:02d}"
        payload = dict(
            shard=sid, subject="math-bj", book=f"{book[0]}年级{book[1]}册", book_code=f"g{g}{'a' if book[1] == '上' else 'b'}",
            grade=g, stage=stage, semester=book[1], duration=dur,
            fullScore=100 if stage == "小学" else 120,
            mid_scope=[u["chapter"] for u in formal[:half]],
            fin_scope=[u["chapter"] for u in formal],
            units=[dict(label=u["chapter"].split(" ")[1] + " " + u["name"], name=u["name"],
                        lessons=[dict(id=p["id"], name=p["name"]) for p in pts
                                 if p["level"] == "lesson" and p.get("chapter", "").startswith(u["chapter"])])
                   for u in formal],
            topics_all=[dict(id=p["id"], name=p["name"], level=p["level"]) for p in pts],
            bank_index={p["id"]: bank.get(p["id"], [])[:3] for p in pts if p["level"] == "lesson"},
        )
        json.dump(payload, open(os.path.join(OUT, f"{sid}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        idx.append(dict(shard=sid, book=payload["book"], units=len(formal), mid=len(formal[:half])))
    json.dump(idx, open(os.path.join(OUT, "_index_midfin.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for r in idx:
        print(f"  {r['shard']} {r['book']}  单元 {r['units']}（期中覆盖 {r['mid']}）")
    print("分片", len(idx), "| 卷数 4×", len(idx), "=", 4 * len(idx))


if __name__ == "__main__":
    main()
