#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中物理：_skeleton.json（已含描述）＋ _bank/T*.json → topics/questions/dependencies。

不依赖 _points 点内容分片（本桶描述已在建骨架时回填）。
"""
import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")


def main(write=False):
    sk = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    T = {t["id"]: t for t in sk}
    qs, bad = [], []
    for p in sorted(glob.glob(os.path.join(D, "_bank", "T*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        qs.extend(d.get("questions") or [])
    by = Counter(q["topicId"] for q in qs)
    for t in sk:
        need = 5 if t["level"] == "unit" else 8
        if by.get(t["id"], 0) != need:
            bad.append("%s(%s) %d/%d" % (t["name"], t["id"], by.get(t["id"], 0), need))
    if bad:
        print("❌ 题量不符 %d 点：%s" % (len(bad), bad[:6]))
        return 1  # 拒绝半成品
    # 补齐题面字段一致性 + 派生依赖
    for q in qs:
        q.setdefault("subject", "physics-sk")
        q["question"] = q.get("question") or q.get("prompt")
        q["prompt"] = q.get("prompt") or q.get("question")
    topics = []
    for t in sk:
        x = dict(t)
        x.setdefault("type", "conceptual")
        x["tags"] = [x["domain"], x["name"]]
        topics.append(x)
    deps = []
    for t in topics:
        if t["level"] == "lesson":
            for pre in (t.get("prerequisites") or []):
                deps.append({"from": pre, "to": t["id"], "type": "hard"})
    print("点 %d（单元 %d / 课时 %d）· 题 %d · 边 %d" % (
        len(topics), sum(1 for t in topics if t["level"] == "unit"),
        sum(1 for t in topics if t["level"] == "lesson"), len(qs), len(deps)))
    if write:
        for name, obj in (("topics.json", topics), ("questions.json", qs), ("dependencies.json", deps)):
            json.dump(obj, open(os.path.join(D, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写入 topics/questions/dependencies")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
