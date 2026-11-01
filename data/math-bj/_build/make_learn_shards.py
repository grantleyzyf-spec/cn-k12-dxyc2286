# -*- coding: utf-8 -*-
"""生成 math-bj 学层精讲分片（每片 ≤15 篇课时，产物落 learn/_parts，父代合并）。

用法: python3 make_learn_shards.py
输出: data/math-bj/_build/learn_shards/L01.json …
"""
import json
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "learn_shards")
TXTROOT = os.path.expanduser("~/Desktop/中小学教材/精准提取各学科教材TXT文档/数学/北京版")
BOOKS = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "五上", "六上",
         "七上", "七下", "八上", "八下", "九上"]
MAX = 15


def main():
    topics = json.load(open(os.path.join(ROOT, "topics.json"), encoding="utf-8"))
    qs = json.load(open(os.path.join(ROOT, "questions.json"), encoding="utf-8"))
    bank = {}
    for q in qs:
        bank.setdefault(q["topicId"], []).append(q["id"])
    by_book = OrderedDict((b, []) for b in BOOKS)
    for t in topics:
        m = re.match(r"([一二三四五六七八九])年级([上下])册", t["chapter"])
        if m:
            by_book[f"{m.group(1)}{m.group(2)}"].append(t)

    os.makedirs(OUT, exist_ok=True)
    idx, n = [], 0
    for short, pts in by_book.items():
        lessons = [p for p in pts if p["level"] == "lesson"]
        book = f"{short[0]}年级{short[1]}册"
        stage = "小学" if pts[0]["grade"] <= 6 else "初中"
        txt = os.path.join(TXTROOT, stage, f"北京版数学{short}.txt")
        k = max(1, -(-len(lessons) // MAX))
        size = -(-len(lessons) // k)
        for i in range(0, len(lessons), size):
            chunk = lessons[i:i + size]
            n += 1
            sid = f"L{n:02d}"
            payload = dict(
                shard=sid, subject="math-bj", book=book, book_short=short, stage=stage,
                grade=pts[0]["grade"], semester=pts[0]["semester"],
                textbook_txt=txt if os.path.exists(txt) else None,
                out_parts=f"/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj/learn/_parts/{book}__{sid}.json",
                points=[dict(
                    id=p["id"], name=p["name"], chapter=p["chapter"],
                    unit=p["chapter"].split(" ")[1] + " " +
                         (p["chapter"].split(" ")[2] if len(p["chapter"].split(" ")) > 2 else ""),
                    description=p.get("description"),
                    mastery_criteria=p.get("mastery_criteria"),
                    misconceptions=p.get("misconceptions"),
                    std_quote=(p["standards"][0]["quote"] if p.get("standards") else None),
                    bank_ids=bank.get(p["id"], [])[:3],
                ) for p in chunk],
            )
            json.dump(payload, open(os.path.join(OUT, f"{sid}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            idx.append(dict(shard=sid, book=book, lessons=len(chunk),
                            txt=bool(payload["textbook_txt"])))
    json.dump(idx, open(os.path.join(OUT, "_index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for r in idx:
        print(f"  {r['shard']} {r['book']:8s} {r['lessons']:2d} 篇  教材TXT={'有' if r['txt'] else '缺'}")
    print("分片", len(idx), "| 篇数合计", sum(r["lessons"] for r in idx),
          "| 缺教材TXT的片:", [r["shard"] for r in idx if not r["txt"]])


if __name__ == "__main__":
    main()
