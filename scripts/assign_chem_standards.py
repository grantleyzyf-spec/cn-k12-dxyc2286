#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：给所有知识点挂课标引文（优先原 id 恢复，其次同单元/邻单元借标，逐字回表）。

用法：python3 scripts/assign_chem_standards.py [--write]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")
STD = ["/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
       "8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt",
       "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
       "（9）普通高中化学课程标准日常修订版（2017年版2025年修订）.txt"]
OLD = "/tmp/chem_topics_before.json"


def qnorm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    old = json.load(open(OLD, encoding="utf-8")) if os.path.exists(OLD) else []
    src = "\n".join(qnorm(open(p, encoding="utf-8", errors="ignore").read()) for p in STD if os.path.exists(p))
    old_std = {t["id"]: t["standards"] for t in old if t.get("standards")}
    # 单元 → 该单元可用引文
    def unit_of(ch):
        return ch.split(" · ")[0]

    by_unit = {}
    for t in T:
        if t["id"] in old_std:
            by_unit.setdefault(unit_of(t["chapter"]), []).extend(old_std[t["id"]])
    restored = borrowed = 0
    units = [t for t in T if t.get("level") == "unit"]
    unit_ids = [u["id"] for u in units]
    for i, u in enumerate(units):
        ch = u["chapter"]
        pool = by_unit.get(ch) or []
        if not pool:  # 邻单元借
            for j in list(range(i - 1, -1, -1)) + list(range(i + 1, len(units))):
                p = by_unit.get(units[j]["chapter"])
                if p:
                    pool = p
                    break
        if pool:
            u["standards"] = [dict(pool[0], confidence="partial")]
            borrowed += 1
    for t in T:
        if t.get("level") == "unit":
            continue
        if t["id"] in old_std:
            t["standards"] = old_std[t["id"]]
            restored += 1
            continue
        ch = unit_of(t["chapter"])
        pool = by_unit.get(ch)
        if not pool:
            for j, u in enumerate(units):
                if u["chapter"] == ch:
                    for k in list(range(j - 1, -1, -1)) + list(range(j + 1, len(units))):
                        p = by_unit.get(units[k]["chapter"])
                        if p:
                            pool = p
                            break
                    break
        if pool:
            t["standards"] = [dict(pool[0], confidence="partial")]
            borrowed += 1
    miss = []
    for t in T:
        if not t.get("standards"):
            miss.append(t["id"])
            continue
        if not any(qnorm(s["quote"]) in src for s in t["standards"]):
            miss.append(t["id"] + "（回表失败）")
        elif not t.get("curriculumRef"):
            t["curriculumRef"] = t["standards"][0]["id"]
    print(f"恢复 {restored}（原 id）＋借标 {borrowed}；未挂/失配 {len(miss)}")
    if miss:
        print("  例子", miss[:8])
    if "--write" in sys.argv:
        with open(os.path.join(D, "topics.json"), "w", encoding="utf-8") as f:
            json.dump(T, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("→ topics.json 已写")


if __name__ == "__main__":
    main()
