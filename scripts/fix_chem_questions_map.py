#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：把题库里挂了旧 id 的题重挂到新 topics 上；无主的题存档。

用法：python3 scripts/fix_chem_questions_map.py [--write]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    Q = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
    legacy = json.load(open(os.path.join(D, "_legacy_topics.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(D, "_legacy_topics.json")) else []
    ids = {t["id"] for t in T}
    by_name = {}
    for t in T:
        by_name.setdefault(norm(t["name"]), t["id"])
    lmap = {l["id"]: by_name[norm(l["name"])] for l in legacy if norm(l["name"]) in by_name}
    moved = orphan = 0
    keep = []
    for q in Q:
        tid = q["topicId"]
        if tid in ids:
            keep.append(q)
            continue
        if tid in lmap:
            q["topicId"] = lmap[tid]
            moved += 1
            keep.append(q)
        else:
            orphan += 1
    print(f"题 {len(Q)} → 保留 {len(keep)}（重挂 {moved}，孤儿 {orphan}）")
    if orphan:
        orph = [q for q in Q if q["topicId"] not in ids and q["topicId"] not in lmap]
        with open(os.path.join(D, "_orphan_questions.json"), "w", encoding="utf-8") as f:
            json.dump(orph, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("  孤儿已存 data/chemistry/_orphan_questions.json")
    if "--write" in sys.argv:
        with open(os.path.join(D, "questions.json"), "w", encoding="utf-8") as f:
            json.dump(keep, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("→ data/chemistry/questions.json")


if __name__ == "__main__":
    main()
