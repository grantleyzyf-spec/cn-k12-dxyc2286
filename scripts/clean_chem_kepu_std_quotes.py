#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清洗课标条目池里的 PDF 页码垃圾（`====page16/83====`），并把 topics 里的引文同步替换。

为什么不能直接删标记：门禁要「逐字回表」——引文必须是课标 TXT 归一化后的**连续子串**。
页码标记本身也是 TXT 里的连续字符，所以做法是「按标记切段，取最长的一段」：每段都是
原 TXT 的连续片段，既干净又能回表。
"""
import json
import re

SRC = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt"
POOL = "data/_chem2022_items.json"
TOPICS = "data/chemistry-kepu/topics.json"
MARK = re.compile(r"=+\s*page\d+/\d+\s*=+")
MINLEN = 24


def clean_quote(q):
    """按页码标记切段，返回最长且 >= MINLEN 的连续段（无则原样返回）。"""
    if not MARK.search(q):
        return q, 0
    segs = [s for s in MARK.split(q) if len(s) >= MINLEN]
    if not segs:
        return q, 0
    return max(segs, key=len), 1


def main():
    txt = re.sub(r"[\s\u3000]+", "", open(SRC, encoding="utf-8").read())
    pool = json.load(open(POOL, encoding="utf-8"))
    changed = {}
    for it in pool:
        q, hit = clean_quote(it["quote"])
        if hit:
            it["quote"] = q
            changed[it["id"]] = q
    json.dump(pool, open(POOL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    topics = json.load(open(TOPICS, encoding="utf-8"))
    n = 0
    for t in topics:
        for s in t.get("standards", []):
            if MARK.search(s.get("quote", "")):
                new = changed.get(s["id"]) or clean_quote(s["quote"])[0]
                s["quote"] = new
                n += 1
    json.dump(topics, open(TOPICS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    bad = [s for t in topics for s in t.get("standards", []) if s["quote"] not in txt]
    left = [s for t in topics for s in t.get("standards", []) if MARK.search(s["quote"])]
    print("池内清洗 %d 条 ｜ topics 替换 %d 处 ｜ 现残留页码 %d ｜ 不可回表 %d"
          % (len(changed), n, len(left), len(bad)))
    for s in bad[:3]:
        print("  不可回表:", s["quote"][:40])


if __name__ == "__main__":
    main()
