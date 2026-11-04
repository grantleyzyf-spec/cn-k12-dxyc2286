#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 chemistry-yuejiao 的 43 个知识点挂义教化学课标引文（逐字回表）。

做法：
- 从课标 TXT 抽「内容要求」区的句子（去分页标记、去换行），按 2-gram 相似度给点名+描述匹配；
- 只接受能在课标 TXT 中逐字找到的句子，信度一律 partial；
- 单元点若自身没匹到，继承本单元第一个已挂标课时点的引文。

用法：python3 scripts/assign_chem_yuejiao_std.py [--write]
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = "/Users/a627692/Desktop/cn-k12-dxyc2286"
D = os.path.join(ROOT, "data", "chemistry-yuejiao")
STD = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
       "8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt")

HAN = re.compile(r"[^\u4e00-\u9fa5]+")


def norm(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def load_sentences():
    raw = open(STD, encoding="utf-8", errors="ignore").read()
    raw = re.sub(r"={5,}\s*page\s*\d+\s*/\s*\d+\s*={5,}", "\n", raw)
    raw = re.sub(r"\n\d{1,3}\n", "\n", raw)
    # 只取「内容要求」段：从第一个【内容要求】到【学业要求】
    blocks = re.findall(r"【内容要求】(.*?)(?=【学业要求】|【教学提示】)", raw, re.S)
    text = "\n".join(blocks)
    text = re.sub(r"\n+", "", text)
    segs = [s.strip() for s in re.split(r"[。；]", text) if len(norm(s)) >= 12]
    return segs, norm(raw)


def grams(s):
    s = HAN.sub("", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def main():
    segs, full = load_sentences()
    print("课标句池", len(segs))
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    seg_grams = [(s, grams(s)) for s in segs]
    df = Counter()
    for _, g in seg_grams:
        df.update(g)
    unit_std = {}
    hit = 0
    for t in topics:
        q = t["name"] + " " + (t.get("description") or "")
        qg = grams(q)
        best, best_score = None, 0.0
        for s, g in seg_grams:
            shared = qg & g
            if not shared:
                continue
            # 稀有词权重高，避免「物质」「化学」这类泛词独占
            score = sum(1.0 / (1 + df[w] / 10.0) for w in shared) / (len(qg) ** 0.5 + 1)
            if score > best_score:
                best, best_score = s, score
        if best and best_score >= 0.55 and norm(best) in full:
            t["standards"] = [{"id": "che-2022:yue", "confidence": "partial", "quote": best}]
            t["curriculumRef"] = "che-2022:yue"
            hit += 1
            if t["level"] == "lesson":
                unit_std.setdefault(t["chapter"].split(" · ")[0], best)
        elif t["level"] == "unit":
            u = unit_std.get(t["chapter"])
            if u:
                t["standards"] = [{"id": "che-2022:yue", "confidence": "partial", "quote": u}]
                t["curriculumRef"] = "che-2022:yue"
                hit += 1
    # 二遍：单元点在课时点之后统一继承（上面按顺序遍历时单元点还拿不到 unit_std）
    for u in [x for x in topics if x["level"] == "unit"]:
        if u.get("standards"):
            continue
        kids = [x for x in topics if x["level"] == "lesson" and x["chapter"].split(" · ")[0] == u["chapter"]]
        q = next((k["standards"][0]["quote"] for k in kids if k.get("standards")), None)
        if q:
            u["standards"] = [{"id": "che-2022:yue", "confidence": "partial", "quote": q}]
            u["curriculumRef"] = "che-2022:yue"
            hit += 1
    print(f"挂标 {hit}/{len(topics)}")
    if "--write" in sys.argv:
        tmp = os.path.join(D, "topics.json.tmp")
        json.dump(topics, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.replace(tmp, os.path.join(D, "topics.json"))
        print("已写入 topics.json")
    for t in topics[:3]:
        print(t["id"], t["name"], "|", (t.get("standards") or [{}])[0].get("quote", "")[:40])


if __name__ == "__main__":
    main()
