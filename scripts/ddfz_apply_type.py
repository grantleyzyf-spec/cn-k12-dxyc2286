#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把题型改造成果写回题库分片（_bank/S*.json），并重跑合并。

题 id 形如 polq_qS010007 ⇒ 属于分片 S01。只替换同 id 的题，不动同片其它题。
用法: python3 scripts/ddfz_apply_type.py [--no-merge]
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")
BANK = os.path.join(SUB, "_bank")
TYPE = os.path.join(SUB, "_batch", "type")


def main():
    files = sorted(glob.glob(os.path.join(TYPE, "T*.json")))
    if not files:
        sys.exit("没有题型分片产出")
    patched = 0
    for f in files:
        for q in json.load(open(f, encoding="utf-8")):
            m = re.match(r"polq_q(S\d{2})", q["id"])
            if not m:
                print("!! id 无法定位分片:", q["id"])
                continue
            bp = os.path.join(BANK, m.group(1) + ".json")
            items = json.load(open(bp, encoding="utf-8"))
            for i, old in enumerate(items):
                if old["id"] == q["id"]:
                    q.setdefault("options", [])
                    q["choices"] = q["options"]
                    items[i] = q
                    patched += 1
                    break
            else:
                print("!! 分片里找不到", q["id"])
                continue
            json.dump(items, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("已替换 %d 题" % patched)
    if "--no-merge" not in sys.argv:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "ddfz_merge_bank.py")],
                           capture_output=True, text=True)
        print(r.stdout.strip().split("\n")[-1] if r.stdout else r.stderr[-300:])


if __name__ == "__main__":
    main()
