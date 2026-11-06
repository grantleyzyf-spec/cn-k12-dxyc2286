#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 physics-hkjy 160 个点挂高中物理课标（phy-2017:*）。

章 → 课标条目为人工核定表（沪科教版 31 章 ↔ 2017 版 2025 修订 高中物理课标条目）；
节点在该章的候选条目里按「名称+描述」与原文的汉字二元组重合度取最贴合的一条。
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
HAN = re.compile(r"[\u4e00-\u9fa5]")

CH = {
    "phk_u001": ["phy-2017:1.1.1.1", "phy-2017:1.1.1.2", "phy-2017:1.1.1.3"],
    "phk_u002": ["phy-2017:1.1.1.3", "phy-2017:1.1.1.4"],
    "phk_u003": ["phy-2017:1.1.2.1", "phy-2017:1.1.2.2"],
    "phk_u004": ["phy-2017:1.1.2.3", "phy-2017:1.1.2.4"],
    "phk_u005": ["phy-2017:2.2.1.1", "phy-2017:2.2.1.2", "phy-2017:2.2.1.3", "phy-2017:2.2.1.4"],
    "phk_u006": ["phy-2017:2.2.2.1", "phy-2017:2.2.2.2"],
    "phk_u007": ["phy-2017:2.2.2.3"],
    "phk_u008": ["phy-2017:2.2.2.4", "phy-2017:2.2.2.5"],
    "phk_u009": ["phy-2017:2.2.3.1", "phy-2017:2.2.3.3"],
    "phk_u010": ["phy-2017:3.3.1.1", "phy-2017:3.3.1.2"],
    "phk_u011": ["phy-2017:3.3.1.3", "phy-2017:3.3.1.5", "phy-2017:3.3.1.6"],
    "phk_u012": ["phy-2017:3.3.2.1", "phy-2017:3.3.2.2", "phy-2017:3.3.2.3"],
    "phk_u013": ["phy-2017:3.3.2.4", "phy-2017:3.3.2.6"],
    "phk_u014": ["phy-2017:3.3.3.1", "phy-2017:3.3.3.2", "phy-2017:3.3.3.3",
                 "phy-2017:3.3.3.4", "phy-2017:3.3.3.5"],
    "phk_u015": ["phy-2017:3.3.4.1", "phy-2017:3.3.4.2", "phy-2017:3.3.4.3"],
    "phk_u016": ["phy-2017:4.1.1.1", "phy-2017:4.1.1.2", "phy-2017:4.1.1.3"],
    "phk_u017": ["phy-2017:4.1.2.1", "phy-2017:4.1.2.2", "phy-2017:4.1.2.3"],
    "phk_u018": ["phy-2017:4.1.2.4", "phy-2017:4.1.2.5", "phy-2017:4.1.2.6"],
    "phk_u019": ["phy-2017:4.1.3.1", "phy-2017:4.1.3.2", "phy-2017:4.1.3.3", "phy-2017:4.1.3.4"],
    "phk_u020": ["phy-2017:5.2.1.1", "phy-2017:5.2.1.2", "phy-2017:5.2.1.3"],
    "phk_u021": ["phy-2017:5.2.2.1", "phy-2017:5.2.2.2", "phy-2017:5.2.2.3"],
    "phk_u022": ["phy-2017:5.2.2.4", "phy-2017:5.2.2.5"],
    "phk_u023": ["phy-2017:5.2.3.1", "phy-2017:5.2.3.2", "phy-2017:5.2.3.3", "phy-2017:5.2.3.4"],
    "phk_u024": ["phy-2017:5.2.4.2", "phy-2017:5.2.4.3"],
    "phk_u025": ["phy-2017:6.3.1.1", "phy-2017:6.3.1.2"],
    "phk_u026": ["phy-2017:6.3.1.6"],
    "phk_u027": ["phy-2017:6.3.1.3", "phy-2017:6.3.1.4", "phy-2017:6.3.1.5"],
    "phk_u028": ["phy-2017:6.3.2.1", "phy-2017:6.3.2.2", "phy-2017:6.3.2.3"],
    "phk_u029": ["phy-2017:6.3.3.1"],
    "phk_u030": ["phy-2017:6.3.4.1"],
    "phk_u031": ["phy-2017:6.3.3.2", "phy-2017:6.3.3.3", "phy-2017:6.3.3.4"],
}


def bigrams(s):
    ch = "".join(HAN.findall(s or ""))
    return {ch[i:i + 2] for i in range(len(ch) - 1)}


def load_pool():
    pool = {}
    for p in glob.glob(os.path.join(ROOT, "data", "physics*/topics.json")):
        try:
            T = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for t in T:
            for s in t.get("standards") or []:
                i = s.get("id") or ""
                if i.startswith("phy-2017") and s.get("quote"):
                    pool.setdefault(i, s["quote"])
    return pool


def main():
    pool = load_pool()
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    unit_of = {t["id"]: t["id"] for t in topics if t["level"] == "unit"}
    for t in topics:
        if t["level"] == "lesson":
            unit_of[t["id"]] = t["chapter"].split(" · ")[0].strip()
            # 章名 → 章点 id
    name2unit = {t["chapter"]: t["id"] for t in topics if t["level"] == "unit"}

    miss = []
    for t in topics:
        if t["level"] == "unit":
            uid = t["id"]
        else:
            uid = name2unit.get(t["chapter"].split(" · ")[0])
        ids = CH.get(uid) or []
        if not ids:
            miss.append(t["id"])
            continue
        # 课时点与章点同挂本章课标条目：章≈课标主题，课时是该主题下的具体内容
        picked = ids
        t["standards"] = [{"id": i, "quote": pool[i], "confidence": "inferred"}
                          for i in picked if i in pool]
    json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(1 for t in topics if t.get("standards"))
    print("点 %d ｜ 有课标 %d（%.0f%%）｜ 无章映射 %d" % (len(topics), ok, 100 * ok / len(topics), len(miss)))
    for tid in ["phk_j001", "phk_j002", "phk_j005", "phk_j040", "phk_j047", "phk_j062", "phk_j105", "phk_j129"]:
        t = [x for x in topics if x["id"] == tid][0]
        print(" ", tid, t["name"], "→", [(s["id"], s["quote"][:26]) for s in t["standards"]])


if __name__ == "__main__":
    main()
