#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科教版高中物理：把 _points/T*.json（点内容）与 _bank/T*.json（题库）合并进 topics/questions。

- 点内容：只回填 description / mastery_criteria / diagnostic_question，id 与骨架一致
- 题库：按 id 去重，孤儿题（topicId 不在 topics）拒绝写入
- 原子落盘；合并后打印点数/题数/题型/难度
"""
import glob
import json
import os
import sys
import tempfile
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")


def atomic(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    tmap = {t["id"]: t for t in topics}

    filled = 0
    for p in sorted(glob.glob(os.path.join(D, "_points", "T*.json"))):
        rows = json.load(open(p, encoding="utf-8"))
        if isinstance(rows, dict):
            rows = rows.get("points") or rows.get("topics") or []
        for r in rows:
            tid = r.get("topicId") or r.get("id")
            t = tmap.get(tid)
            if not t:
                print("!! 点内容出现无主 topicId:", tid)
                continue
            for k in ("description", "mastery_criteria", "diagnostic_question"):
                if r.get(k):
                    t[k] = r[k]
            filled += 1

    seen, out, dup = set(), [], 0
    for p in sorted(glob.glob(os.path.join(D, "_bank", "T*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        qs = d.get("questions") if isinstance(d, dict) else d
        for q in qs:
            if q["id"] in seen:
                dup += 1
                continue
            if q.get("topicId") not in tmap:
                raise SystemExit("孤儿题 %s（topicId %s 不在 topics）" % (q["id"], q.get("topicId")))
            seen.add(q["id"])
            out.append(q)

    atomic(os.path.join(D, "topics.json"), topics)
    atomic(os.path.join(D, "questions.json"), out)
    print("点 %d（回填 %d）｜题 %d（去重 %d）" % (len(topics), filled, len(out), dup))
    print("题型", dict(Counter(q["type"] for q in out)))
    print("难度", dict(Counter(q["difficulty"] for q in out)))
    print("每点题量", dict(Counter(Counter(q["topicId"] for q in out).values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
