#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）地理：把 _exam_out/E*.json 合并为 exams/<册>/<卷名>.json。

派单形状：`{"shard":"E01","book":…,"papers":[{examId,kind,paper,scope,topicIds,sections}]}`
工位产物：同名文件，papers 里每卷补齐 `sections[].items` 与 `book/grade/term/stage/duration/fullScore`。

幂等：全部卷先校验再原子落盘；旧卷不删（只覆盖同名）。
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")


def atomic_dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main() -> int:
    files = sorted(glob.glob(os.path.join(D, "_exam_out", "E*.json")))
    if not files:
        print("❌ _exam_out 下没有 E*.json")
        return 1
    papers, bad = [], []
    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        book = d.get("book")
        for paper in d.get("papers") or []:
            paper = dict(paper)
            paper.setdefault("book", book)
            paper.setdefault("grade", d.get("grade"))
            paper.setdefault("term", d.get("term"))
            paper.setdefault("stage", d.get("stage", "初中"))
            paper.setdefault("duration", d.get("duration", 120))
            paper.setdefault("fullScore", d.get("fullScore", 120))
            for k in ("examId", "kind", "paper", "scope", "sections"):
                if not paper.get(k):
                    bad.append(f"{os.path.basename(p)} 缺字段 {k}")
            papers.append(paper)
    if bad:
        print("❌ 结构不全：", bad[:5])
        return 1
    ids = [x["examId"] for x in papers]
    if len(set(ids)) != len(ids):
        dup = [k for k in set(ids) if ids.count(k) > 1]
        print(f"❌ examId 撞号 {dup[:5]}")
        return 1
    n_items = sum(len(s.get("items") or []) for x in papers for s in x["sections"])
    if n_items == 0:
        print("❌ 所有卷 sections 都是空的（工位没写题）")
        return 1
    for x in papers:
        dst = os.path.join(D, "exams", x["book"], f"{x['paper']}.json")
        atomic_dump(dst, x)
    print(f"合并 {len(papers)} 卷 / {n_items} 题 → {os.path.join(D, 'exams')}")
    from collections import Counter
    print("按册", dict(Counter(x["book"] for x in papers)),
          "按类型", dict(Counter(x["kind"] for x in papers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
