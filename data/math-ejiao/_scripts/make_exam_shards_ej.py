# -*- coding: utf-8 -*-
"""鄂教版数学：生成试卷派单分片（单元卷 + 期中A/B + 期末A/B）。

结构（高中 150 分 / 120 分钟）：
  单元卷  20 章各 1 卷（scope = 该章 chapter 首段）
  期中卷  每册 A/B（scope = 前半册各章）
  期末卷  每册 A/B（scope = 全册各章）

产出：data/math-ejiao/_exam_shards/<shard>.json（每片 ≤6 卷，单册不跨片）
用法：python3 _scripts/make_exam_shards_ej.py [--write]
"""
import collections
import math
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
OUT = os.path.join(D, "_exam_shards")
BOOK_CODE = {"必修第一册": "b1", "必修第二册": "b2", "必修第三册": "b3", "必修第四册": "b4",
             "选择性必修第一册": "x1", "选择性必修第二册": "x2", "选择性必修第三册": "x3"}


def main():
    write = "--write" in sys.argv
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    books = collections.OrderedDict()
    for t in topics:
        parts = t["chapter"].split(" ")
        book = parts[0]
        chap = " ".join(parts[:2])
        b = books.setdefault(book, {"grade": t["grade"], "chapters": [], "points": {}})
        b["grade"] = t["grade"]
        if chap not in b["chapters"]:
            b["chapters"].append(chap)
        b["points"].setdefault(chap, []).append(t["id"])

    papers = []
    for book, info in books.items():
        code = next((v for k, v in sorted(BOOK_CODE.items(), key=lambda kv: -len(kv[0])) if k in book), "b0")
        chs = info["chapters"]
        g = info["grade"]
        for i, ch in enumerate(chs, 1):
            papers.append({"book": book, "kind": "unit", "paper": f"第{i}章 单元测试卷",
                           "scope": [ch], "topicIds": info["points"][ch], "grade": g,
                           "examId": f"mej_exam_{code}_u{i:02d}"})
        half = chs[: max(1, len(chs) // 2)]
        for kind, tag, label, sc in (("mid", "mid_a", "期中测试卷A", half), ("mid", "mid_b", "期中测试卷B", half),
                                     ("fin", "fin_a", "期末测试卷A", chs), ("fin", "fin_b", "期末测试卷B", chs)):
            tids = [tid for ch in sc for tid in info["points"][ch]]
            papers.append({"book": book, "kind": kind, "paper": label, "scope": sc,
                           "topicIds": tids, "grade": g, "examId": f"mej_exam_{code}_{tag}"})

    # 分片：单册不跨片、每片 ≤6 卷，且按册均衡切（不留 1 卷碎片、不产空片）
    shards, idx = [], 0
    by_book = collections.OrderedDict()
    for p in papers:
        by_book.setdefault(p["book"], []).append(p)
    for book, rows in by_book.items():
        k = max(1, math.ceil(len(rows) / 6))
        size = math.ceil(len(rows) / k)
        for i in range(0, len(rows), size):
            idx += 1
            shards.append((f"E{idx:02d}", rows[i:i + size]))

    print(f"卷 {len(papers)} 份（单元 {sum(1 for p in papers if p['kind']=='unit')} · "
          f"期中 {sum(1 for p in papers if p['kind']=='mid')} · 期末 {sum(1 for p in papers if p['kind']=='fin')}）"
          f" | 分片 {len(shards)}")
    for name, rows in shards:
        print(f"  {name}: {len(rows)} 卷 " + "、".join(r["paper"] for r in rows))
        if write:
            os.makedirs(OUT, exist_ok=True)
            json.dump({"shard": name, "papers": rows},
                      open(os.path.join(OUT, f"{name}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    if write:
        print("已写", OUT)


if __name__ == "__main__":
    main()
