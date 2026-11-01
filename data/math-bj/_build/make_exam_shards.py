# -*- coding: utf-8 -*-
"""生成 math-bj 试卷分片（每片一册，单元卷 ≤6 份；单元名/课时点/题库索引一并给出）。

用法: python3 make_exam_shards.py
输出: data/math-bj/_build/exam_shards/E01.json …
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
CODE = {f"{c}{s}": f"g{CN.index(c) + 1}{s}" for c in CN for s in ("上", "下")}
STAGE = {"小学": dict(dur_lo=40, dur_hi=60, full=100), "初中": dict(dur_lo=90, dur_hi=90, full=120)}


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

    os.makedirs(OUT, exist_ok=True)
    idx, n = [], 0
    for book, pts in by_book.items():
        units = [p for p in pts if p["level"] == "unit"]
        # 只对「正式单元」出卷：排除 数学百花园 / 总复习（综合与实践板块）
        formal = [u for u in units if not re.search(r"数学百花园|总复习", u["name"])]
        g = pts[0]["grade"]
        stage = "小学" if g <= 6 else "初中"
        dur = 40 if g <= 2 else 60 if g <= 6 else 90
        k = max(1, -(-len(formal) // 6))          # 册内片数（≤6 卷/片）
        size = -(-len(formal) // k)               # 均衡
        for i in range(0, len(formal), size):
            chunk = formal[i:i + size]
            n += 1
            sid = f"E{n:02d}"
            payload = dict(
                shard=sid, subject="math-bj", book=book, book_code=CODE[book],
                grade=g, stage=stage, semester=pts[0]["semester"],
                duration=dur, fullScore=100 if stage == "小学" else 120,
                units=[dict(no=u["chapter"].split("第")[1].split("单元")[0].split("章")[0],
                            name=u["name"], unit_topic_id=u["id"],
                            label=u["chapter"].split(" ")[1] + " " + u["name"],
                            lessons=[dict(id=p["id"], name=p["name"]) for p in pts
                                     if p["level"] == "lesson" and p.get("chapter", "").startswith(
                                         u["chapter"])]) for u in chunk],
                topics_all=[dict(id=p["id"], name=p["name"], level=p["level"]) for p in pts],
                bank_index={p["id"]: bank.get(p["id"], [])[:3] for p in pts if p["level"] == "lesson"},
            )
            # 章节号：小学「第一单元」、初中「第一章」
            json.dump(payload, open(os.path.join(OUT, f"{sid}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            idx.append(dict(shard=sid, book=book, units=len(chunk),
                            names=[u["name"] for u in chunk]))
    json.dump(idx, open(os.path.join(OUT, "_index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for r in idx:
        print(f"  {r['shard']} {r['book']}  单元卷 {r['units']}：{ '、'.join(r['names'])[:60] }")
    print("分片", len(idx), "| 单元卷合计", sum(r["units"] for r in idx))


if __name__ == "__main__":
    main()
