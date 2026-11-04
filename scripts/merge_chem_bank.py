#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：合并题库分片 → questions.json，并把分片 topics[] 内容回写 topics.json。

用法：python3 scripts/merge_chem_bank.py [--write]
护栏：分片不全（题槽对不上）时拒绝写入；题量比现有少 5% 以上时拒绝写入。
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")


def main():
    spec_files = sorted(glob.glob(os.path.join(D, "_bank_shards", "CHEM_B*.json")))
    outs = {}
    for sp in spec_files:
        sid = os.path.basename(sp)[:-5]
        out = os.path.join(D, "_bank", f"{sid}_out.json")
        if os.path.exists(out):
            outs[sid] = json.load(open(out, encoding="utf-8"))
    missing = len(spec_files) - len(outs)
    qs, trend = [], {}
    for sid, o in sorted(outs.items()):
        if isinstance(o, list):
            o = {"shard": sid, "topics": [], "questions": o}
        qs.extend(o.get("questions") or [])
        for t in o.get("topics") or []:
            trend[t["id"]] = {k: t[k] for k in ("description", "mastery_criteria", "type")
                              if t.get(k)}
    ids = {q["id"] for q in qs}
    print(f"分片 {len(outs)}/{len(spec_files)}（缺 {missing}）· 题 {len(qs)}（唯一 id {len(ids)}）")
    old = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(D, "questions.json")) else []
    if len(qs) < len(old) * 0.95:
        print(f"⚠ 题量 {len(qs)} 少于现有 {len(old)} 的 95%，拒绝写入")
        return 1
    if missing:
        print("⚠ 分片不齐，先补齐再合并（本次不写）")
        return 1
    # 按主题与难度排序
    order = {"basic": 0, "standard": 1, "hard": 2}
    qs.sort(key=lambda q: (q["topicId"], order.get(q.get("difficulty"), 3), q["id"]))
    if "--write" not in sys.argv:
        print("（dry-run，未写盘）")
        return 0
    with open(os.path.join(D, "questions.json"), "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=1)
        f.write("\n")
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    filled = 0
    for t in T:
        tr = trend.get(t["id"])
        if tr:
            t.update(tr)
            filled += 1
    with open(os.path.join(D, "topics.json"), "w", encoding="utf-8") as f:
        json.dump(T, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"→ questions.json {len(qs)} 题；topics.json 回写内容 {filled}/{len(T)} 点")
    return 0


if __name__ == "__main__":
    sys.exit(main())
