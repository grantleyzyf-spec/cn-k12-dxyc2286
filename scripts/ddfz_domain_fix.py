#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""义教 politics 的 domain 重挂（把占位值「道德教育」按所引课标主题改过来）。

背景：旧盘点的 242 个义教点里 186 个（77%）一律写「道德教育」，属占位值——任何闸门都不报。
本脚本按每点**自己引用的课标条目所属学习主题**定板块，幂等：
  RX 入学教育 / DD 道德教育 / SM 生命安全与健康教育 → 道德教育
  FZ 法治教育 → 法治教育
  CT 中华优秀传统文化（与革命传统）教育 / GC 革命传统教育 / GQ 国情教育 → 政治认同
高中点不动（已按册/单元人工定标）。

用法: python3 scripts/ddfz_domain_fix.py [--write]
"""
import json
import os
import sys
from collections import Counter

SUB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "politics")
MAP = {"RX": "道德教育", "DD": "道德教育", "SM": "道德教育",
       "FZ": "法治教育", "CT": "政治认同", "GC": "政治认同", "GQ": "政治认同"}


def code_of(sid):
    return sid.split(":")[1].split(".")[1] if sid.startswith("ddf") else ""


def main():
    write = "--write" in sys.argv
    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    changed = []
    for t in topics:
        if t["grade"] > 9 or not t.get("standards"):
            continue
        new = MAP.get(code_of(t["standards"][0]["id"]))
        if new and new != t["domain"]:
            changed.append((t["id"], t["domain"], new))
            t["domain"] = new
            t["tags"] = [new]
    print("需要改动 %d 个点（义教 %d 点）" % (len(changed), sum(1 for x in topics if x["grade"] <= 9)))
    print("改后义教分布:", dict(Counter(x["domain"] for x in topics if x["grade"] <= 9)))
    print("改后全科分布:", dict(Counter(x["domain"] for x in topics)))
    if write:
        json.dump(topics, open(os.path.join(SUB, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写回 data/politics/topics.json")
    else:
        print("（dry-run，加 --write 落盘）")


if __name__ == "__main__":
    main()
