#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把文案分片产出合并回 topics.json（description / mastery_criteria）。

用法: python3 scripts/ddfz_apply_copy.py [--write]
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")
WEN = os.path.join(SUB, "_batch", "wen")


def main():
    write = "--write" in sys.argv
    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    T = {t["id"]: t for t in topics}
    files = sorted(glob.glob(os.path.join(WEN, "W*.json")))
    if not files:
        sys.exit("没有文案分片产出：%s" % WEN)
    done, changed = [], 0
    for f in files:
        for x in json.load(open(f, encoding="utf-8")):
            t = T.get(x["id"])
            if not t:
                continue
            done.append(x["id"])
            if t["description"] != x["description"] or t["mastery_criteria"] != x["mastery_criteria"]:
                t["description"] = x["description"]
                t["mastery_criteria"] = x["mastery_criteria"]
                changed += 1
    print("分片 %d 个 | 覆盖点 %d/%d | 实际改动 %d" % (len(files), len(set(done)), len(topics), changed))
    left = [t["id"] for t in topics if t["description"] == t["name"]]
    print("仍是占位的点：%d %s" % (len(left), left[:6]))
    if write:
        json.dump(topics, open(os.path.join(SUB, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写回 data/politics/topics.json")
    else:
        print("（dry-run，加 --write 落盘）")


if __name__ == "__main__":
    main()
