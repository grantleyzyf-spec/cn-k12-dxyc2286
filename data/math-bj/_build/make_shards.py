# -*- coding: utf-8 -*-
"""生成北京版数学题库分片（每片 ≤25 点、不跨册）＋ WORKER.md 契约 ＋ check_bank.py。

用法: python3 make_shards.py
输出: data/math-bj/_shards/S01.json … SWORKER.md check_bank.py  _shards/_index.json
"""
import json
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # data/math-bj
SH = os.path.join(ROOT, "_shards")
MAX_POINTS = 25

BOOKS = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "五上", "六上",
         "七上", "七下", "八上", "八下", "九上"]


def main():
    sk = json.load(open(os.path.join(HERE, "_skeleton.json"), encoding="utf-8"))
    topics = sk["topics"]
    cands = json.load(open(os.path.join(HERE, "_std_candidates.json"), encoding="utf-8"))
    by_book = OrderedDict((b, []) for b in BOOKS)
    for t in topics:
        by_book[t["book"]].append(t)

    os.makedirs(SH, exist_ok=True)
    idx, n = [], 0
    for book, pts in by_book.items():
        k = max(1, -(-len(pts) // MAX_POINTS))          # 册内片数
        size = -(-len(pts) // k)                        # 均衡每片点数
        for i in range(0, len(pts), size):
            chunk = pts[i:i + size]
            n += 1
            sid = f"S{n:02d}"
            payload = dict(
                shard=sid, subject="math-bj", book=book, seg=chunk[0]["seg"],
                grade=chunk[0]["grade"], semester=chunk[0]["semester"],
                std_candidates=cands[str(1 if chunk[0]["grade"] <= 2 else 2 if chunk[0]["grade"] <= 4
                                         else 3 if chunk[0]["grade"] <= 6 else 4)],
                points=[dict(
                    id=p["id"], name=p["name"], chapter=p["chapter"], level=p["level"],
                    type=p["type"], domain=p["domain"], grade=p["grade"],
                    unit_no=p["unit_no"],
                    std_id=(p["standards"][0]["id"] if p.get("standards") else None),
                    std_quote=(p["standards"][0]["quote"] if p.get("standards") else None),
                ) for p in chunk],
            )
            json.dump(payload, open(os.path.join(SH, f"{sid}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            idx.append(dict(shard=sid, book=book, points=len(chunk),
                            units=sum(1 for p in chunk if p["level"] == "unit")))
    json.dump(idx, open(os.path.join(SH, "_index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for r in idx:
        print(f"  {r['shard']} {r['book']}  点 {r['points']:2d}（单元 {r['units']}）")
    print("分片总数", len(idx), "| 点", sum(r["points"] for r in idx))


if __name__ == "__main__":
    main()
