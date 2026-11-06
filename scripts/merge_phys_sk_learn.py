#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版地理：learn/_parts/LNN*.json → learn/<册>.json。

分片形状：`{"shard":"L01","book":"七年级上册","lessons":[<篇>, …]}`
篇字段：topicId / title / book / markdown / words

护栏（照 SKILL §5.7）：
- 目标文件已存在且现有篇数 > 本次合并篇数 ⇒ 拒绝写入（防分片不全把整册覆盖成残本）
- 篇数与 `topics.json` 的课时点数逐册对表；缺一篇就报出来
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
PARTS = os.path.join(D, "learn", "_parts")
OUT = os.path.join(D, "learn")


def atomic_dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main() -> int:
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    order = {t["id"]: i for i, t in enumerate(topics)}
    need = collections.Counter(t["chapter"].split(" ")[0] for t in topics if t["level"] == "lesson")

    by_book = collections.defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(PARTS, "*.json"))):
        obj = json.load(open(f, encoding="utf-8"))
        book = obj.get("book") or ""
        batch = obj.get("lessons") if isinstance(obj, dict) else obj
        for les in batch or []:
            tid = les.get("topicId")
            if not tid:
                continue
            les = dict(les)
            les.setdefault("book", book)
            by_book[book][tid] = les

    bad = 0
    total = 0
    for book in ["八年级上册", "八年级下册", "九年级上册", "九年级下册"]:
        lessons = by_book.get(book, {})
        items = [lessons[k] for k in sorted(lessons, key=lambda x: order.get(x, 9999))]
        dst = os.path.join(OUT, f"{book}.json")
        if os.path.exists(dst):
            old = len((json.load(open(dst, encoding="utf-8")).get("lessons") or []))
            if old > len(items):
                print(f"❌ {book}：现有 {old} 篇 > 本次 {len(items)} 篇 ⇒ 拒绝覆盖（分片不全？）")
                bad += 1
                continue
        if len(items) != need[book]:
            print(f"⚠️ {book}：{len(items)}/{need[book]} 篇（缺口 {need[book] - len(items)}）")
            bad += 1
        atomic_dump(dst, {"book": book, "lessons": items})
        total += len(items)
        print(f"{book}: {len(items)} 篇 → {dst}")
    print(f"合计 {total} 篇；异常 {bad} 册")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
