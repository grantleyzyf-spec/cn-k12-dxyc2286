#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 _skeleton 切出可发布的 topics/dependencies 切片（按册）。

用法：python3 scripts/make_bsd_slice.py --skeleton data/math-bsd/_skeleton_小学.json \
        --books 一年级上册 [一年级下册 …]            # 不给 --books 就全切
产出：data/math-bsd/topics.json + dependencies.json（只含这些册）
附带：data/math-bsd/_shards/<册>_第<N>单元.json（派单 spec：该单元的点清单）
"""
import argparse, json, os, re

ap = argparse.ArgumentParser()
ap.add_argument("--skeleton", required=True)
ap.add_argument("--books", nargs="*")
ap.add_argument("--root", default="data/math-bsd")
a = ap.parse_args()

sk = json.load(open(a.skeleton, encoding="utf-8"))
topics = sk["topics"]
if a.books:
    topics = [t for t in topics if t["chapter"].split(" ")[0] in set(a.books)]
ids = {t["id"] for t in topics}
deps = [d for d in sk["deps"] if d["from"] in ids and d["to"] in ids]

os.makedirs(a.root, exist_ok=True)
json.dump(topics, open(f"{a.root}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(f"{a.root}/topics.json", "a", encoding="utf-8").write("\n")
json.dump(deps, open(f"{a.root}/dependencies.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(f"{a.root}/dependencies.json", "a", encoding="utf-8").write("\n")

# 派单 spec（按册+单元）
shard_dir = os.path.join(a.root, "_shards")
os.makedirs(shard_dir, exist_ok=True)
groups = {}
for t in topics:
    book = t["chapter"].split(" ")[0]
    m = re.search(r"第([一二三四五六七八九十\d]+)(?:单元|章)\s*(.*)$", t["chapter"])
    key = (book, m.group(1) if m else "?", (m.group(2) if m else "").strip())
    groups.setdefault(key, []).append(
        {"id": t["id"], "name": t["name"], "domain": t["domain"],
         "grade": t["grade"], "book": book, "unit": key[2], "chapter": t["chapter"]})
n = 0
for (book, uno, uname), items in sorted(groups.items()):
    fn = os.path.join(shard_dir, f"{book}_第{uno}单元.json")
    json.dump({"book": book, "unit_no": uno, "unit_name": uname, "topics": items},
              open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n += 1
print(f"topics {len(topics)} | deps {len(deps)} | 派单 spec {n} 份 → {shard_dir}")
