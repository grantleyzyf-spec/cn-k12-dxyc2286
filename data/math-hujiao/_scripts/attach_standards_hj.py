#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版 · 课标挂载（复用同一份课标已逐字回表的引文）
做法：从 data/math（人教）里收集全部 mat-2017 的 (id, quote, sourceLine)；
对沪教版每个知识点，用「名称+章名」2-gram 重合度挑选最匹配的 1–2 条引文挂上，
confidence: 人教有同名点→exact，否则 partial。
最后逐条校验 quote 去空白后必须在高中课标 TXT 里子串命中（不命中则丢弃并计数）。
"""
import json, os, re, sys
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HJ = os.path.join(REPO, "data", "math-hujiao")
STD_TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt"


def norm(s):
    return re.sub(r"\s+", "", s or "")


def bigrams(s):
    s = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def main():
    ren = json.load(open(os.path.join(REPO, "data", "math", "topics.json"), encoding="utf-8"))
    bank = []  # (id, quote, sourceLine, name)
    for t in ren:
        for s in t.get("standards") or []:
            if str(s.get("id", "")).startswith("mat-2017") and s.get("quote"):
                bank.append((s["id"], s["quote"], s.get("sourceLine"), t.get("name", "")))
    print(f"人教 mat-2017 引文库：{len(bank)} 条（去重 {len({b[1] for b in bank})} 句）")

    std = open(STD_TXT, encoding="utf-8", errors="ignore").read()
    stdn = norm(std)
    topics_p = os.path.join(HJ, "topics.json")
    topics = json.load(open(topics_p, encoding="utf-8"))
    same_name = {}
    for t in ren:
        same_name.setdefault(norm(t.get("name")), t.get("name"))

    hit = partial = 0
    dropped = []
    for t in topics:
        key = bigrams(t.get("name", "") + t.get("chapter", ""))
        scored = []
        for sid, q, sl, rname in bank:
            qb = bigrams(q)
            if not qb:
                continue
            score = len(key & qb) / max(1, len(qb))
            scored.append((score, sid, q, sl, rname))
        scored.sort(reverse=True)
        picked = []
        for score, sid, q, sl, rname in scored[:12]:
            if score < 0.18:
                break
            if any(x["id"] == sid for x in picked):
                continue
            if norm(q) not in stdn:
                dropped.append((t["id"], sid, q[:20]))
                continue
            picked.append({"id": sid, "confidence": "exact" if norm(t["name"]) == norm(rname) else "partial",
                           "quote": q, **({"sourceLine": sl} if isinstance(sl, int) else {})})
            if len(picked) >= 2:
                break
        t["standards"] = picked
        if picked:
            t["curriculumRef"] = picked[0]["id"]
            hit += 1
            if picked[0]["confidence"] == "partial":
                partial += 1

    json.dump(topics, open(topics_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = Counter(len(t.get("standards") or []) for t in topics)
    print(f"挂载：{hit}/{len(topics)} 点有引文；条数分布 {dict(c)}；partial 首条 {partial}；丢弃不可回表 {len(dropped)}")
    for d in dropped[:5]:
        print("  丢弃", d)


if __name__ == "__main__":
    main()
