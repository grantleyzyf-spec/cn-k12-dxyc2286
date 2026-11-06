#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中物理：把 _desc/<册>.json 回填进 _skeleton.json，并生成 topics.json。"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")


def main(write=False):
    sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
    desc = {}
    for p in glob.glob(os.path.join(D, "_desc", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for x in d.get("lessons") or []:
            desc[x["id"]] = x
    miss = [t["id"] for t in sk if t["level"] == "lesson" and t["id"] not in desc]
    if miss:
        print("❌ 缺 %d 个课时描述：%s" % (len(miss), miss[:6]))
        return 1
    n = 0
    for t in sk:
        if t["level"] == "lesson":
            d = desc[t["id"]]
            t["description"] = d["description"]
            t["mastery_criteria"] = [d["c1"], d["c2"]]
            n += 1
    print("回填 %d 个课时描述；总点 %d" % (n, len(sk)))
    if write:
        json.dump(sk, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写 topics.json")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
