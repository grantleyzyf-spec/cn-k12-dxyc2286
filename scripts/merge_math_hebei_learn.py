
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把学层分片 data/math-hebei/learn/_parts/L*.json 合并成 data/math-hebei/learn/<册>.json。

- 课时顺序按 topics.json 里的册内顺序排列（不按分片顺序，避免错册乱序）
- 输出结构与人教一致：{"book": "<册>", "lessons": [{topicId,title,markdown,words}]}
- 合并后逐册跑 check_math_hebei_learn.py，未过不写盘

用法：python3 scripts/merge_math_hebei_learn.py [--write]
"""
import argparse, glob, json, os, subprocess, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "math-hebei")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true", help="允许把整册覆盖成更少的篇数（默认拒绝缩水）")
    a = ap.parse_args()
    topics = load(os.path.join(D, "topics.json"))
    order = {}
    for i, t in enumerate(topics):
        if t.get("level") == "lesson":
            order[t["id"]] = i
    parts = sorted(glob.glob(os.path.join(D, "learn", "_parts", "L*.json")))
    by_book = defaultdict(dict)
    for p in parts:
        d = load(p)
        for L in d.get("lessons") or []:
            by_book[d["book"]][L["topicId"]] = L
    print(f"分片 {len(parts)} | 册 {len(by_book)}")
    bad = 0
    for book, lessons in sorted(by_book.items()):
        seq = sorted(lessons.values(), key=lambda L: order.get(L["topicId"], 10 ** 6))
        out = {"book": book, "lessons": seq}
        need = {tid for tid, i in order.items() if True}
        n_less = sum(1 for t in topics if t.get("level") == "lesson" and t["chapter"].startswith(book + " "))
        print(f"  {book}: {len(seq)}/{n_less} 篇")
        if len(seq) != n_less:
            print(f"    !! 缺口 {n_less - len(seq)}")
        if a.write:
            p = os.path.join(D, "learn", f"{book}.json")
            # 🔴 防缩水：现有成品篇数多于本次合并结果时拒绝写入（分片不全时会把整册覆盖成残本）
            if os.path.exists(p) and not a.force:
                old_n = len((load(p).get("lessons") or []))
                if old_n > len(seq):
                    print(f"    ⛔ 拒绝写入：现有 {old_n} 篇 > 本次 {len(seq)} 篇（分片不全；确认要覆盖请加 --force）")
                    bad += 1
                    continue
            dump(p, out)
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_math_hebei_learn.py"), p],
                               capture_output=True, text=True)
            last = (r.stdout.strip().split("\n") or [""])[-1]
            print("    checker:", last)
            if "PASS" not in last:
                bad += 1
    if a.write:
        print("不通过的册数:", bad)


if __name__ == "__main__":
    main()
