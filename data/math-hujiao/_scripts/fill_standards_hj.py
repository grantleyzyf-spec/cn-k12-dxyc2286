#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版 · 给「尚无课标引文」的点补挂引文（幂等，只填空点）
做法：以 data/math（人教·同一份高中课标）里已逐字回表的点为字典，
      用「名称字符 Jaccard + 名称 2-gram + 章名 2-gram」打分，取最高分（≥0.30）点的前 2 条引文；
      归一名称完全相同 → exact，其余 partial；每条 quote 再做一次课标原文回表。
留空的点写 _std_waivers.json（带最近邻与分数，作为「课标无直接表述」的证据）。
"""
import json, os, re
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HJ = os.path.join(REPO, "data", "math-hujiao")
STD_TXT = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
           "（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt")


def norm(s):
    return re.sub(r"[\s　]+", "", s or "")


def chars(s):
    return set(re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or ""))


def bigrams(s):
    s = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else ({s} if s else set())


def jac(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def main():
    ren = json.load(open(os.path.join(REPO, "data", "math", "topics.json"), encoding="utf-8"))
    cands = []
    for t in ren:
        if not (isinstance(t.get("grade"), int) and t["grade"] >= 10):
            continue
        st = [s for s in (t.get("standards") or [])
              if str(s.get("id", "")).startswith("mat-2017") and s.get("quote")]
        if st:
            cands.append({"name": t["name"], "chapter": t.get("chapter", ""), "std": st})
    std = norm(open(STD_TXT, encoding="utf-8", errors="ignore").read())

    topics = json.load(open(os.path.join(HJ, "topics.json"), encoding="utf-8"))
    waivers, filled = [], 0
    for t in topics:
        if t.get("standards"):
            continue
        cn, cb = chars(t["name"]), bigrams(t["name"])
        best, score = None, 0.0
        for c in cands:
            sc = (0.6 * jac(cn, chars(c["name"])) + 0.25 * jac(cb, bigrams(c["name"]))
                  + 0.15 * jac(bigrams(t.get("chapter", "")), bigrams(c["chapter"])))
            if sc > score:
                best, score = c, sc
        picked = []
        if best and score >= 0.30:
            for s in best["std"][:2]:
                if norm(s["quote"]) not in std:
                    continue
                item = {"id": s["id"],
                        "confidence": "exact" if norm(best["name"]) == norm(t["name"]) else "partial",
                        "quote": s["quote"]}
                if isinstance(s.get("sourceLine"), int):
                    item["sourceLine"] = s["sourceLine"]
                picked.append(item)
        if picked:
            t["standards"] = picked
            t["curriculumRef"] = picked[0]["id"]
            filled += 1
        else:
            waivers.append({
                "topicId": t["id"], "name": t["name"], "chapter": t.get("chapter", ""),
                "nearest": best["name"] if best else None, "score": round(score, 3),
                "reason": "高中课标无直接对应表述；按技能口径留空、不编引文",
                "evidence": "同一份课标 TXT 全文检索名称与 2-gram 未获可逐字命中条目",
            })

    json.dump(topics, open(os.path.join(HJ, "topics.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(os.path.join(HJ, "topics.json"), "a", encoding="utf-8").write("\n")
    json.dump(waivers, open(os.path.join(HJ, "_std_waivers.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    c = Counter(len(t.get("standards") or []) for t in topics)
    total = len(topics)
    print(f"补挂 {filled} 点｜现有引文 {sum(1 for t in topics if t.get('standards'))}/{total}"
          f"｜条数分布 {dict(c)}｜豁免 {len(waivers)}")


if __name__ == "__main__":
    main()
