#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普版地理：75 卷分片（39 单元卷 ＋ 36 期中期末），每片 2 卷、同册不跨片。"""
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-kepu")
SD = os.path.join(D, "_exam_shards")
os.makedirs(SD, exist_ok=True)

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册",
         "必修第一册", "必修第二册", "选择性必修1", "选择性必修2", "选择性必修3"]
CODE = {"七年级上册": "g7a", "七年级下册": "g7b", "八年级上册": "g8a", "八年级下册": "g8b",
        "必修第一册": "bx1", "必修第二册": "bx2", "选择性必修1": "xx1", "选择性必修2": "xx2",
        "选择性必修3": "xx3"}
SPEC = {
    "初中": {"duration": 120, "fullScore": 120,
             "sections": [{"title": "一、选择题（每小题 3 分，共 54 分）", "rule": "每小题 3 分，共 54 分",
                           "type": "choice", "n": 18, "each": 3},
                          {"title": "二、综合题（每小题 11 分，共 66 分）", "rule": "每小题 11 分，共 66 分",
                           "type": "short", "n": 6, "each": 11}]},
    "高中": {"duration": 150, "fullScore": 150,
             "sections": [{"title": "一、选择题（每小题 3 分，共 54 分）", "rule": "每小题 3 分，共 54 分",
                           "type": "choice", "n": 18, "each": 3},
                          {"title": "二、综合题（每小题 16 分，共 96 分）", "rule": "每小题 16 分，共 96 分",
                           "type": "short", "n": 6, "each": 16}]},
}

SEM = {"七年级上册": "上", "七年级下册": "下", "八年级上册": "上", "八年级下册": "下",
       "必修第一册": "上", "必修第二册": "下", "选择性必修1": "上", "选择性必修2": "下", "选择性必修3": "上"}


def t_sem(book):
    return SEM[book]


by_book = {}
for t in topics:
    book = t["chapter"].split(" ")[0]
    by_book.setdefault(book, []).append(t)

papers = []
for book in BOOKS:
    pts = by_book.get(book, [])
    stage = "初中" if book.startswith(("七", "八")) else "高中"
    chapters = []
    for t in pts:
        if t["level"] == "unit":
            chapters.append(t["chapter"])
    if not chapters:
        continue
    for idx, ch in enumerate(chapters, 1):
        title = ch.split(" ", 1)[1]
        papers.append({"paper": f"{title} 测试卷", "kind": "unit", "book": book, "stage": stage,
                       "term": t_sem(book), "scope": [ch], "examId": f"gkp_exam_{CODE[book]}_u{idx:02d}"})
    half = max(1, len(chapters) // 2)
    for tag in ("A", "B"):
        papers.append({"paper": f"期中测试卷{tag}", "kind": "mid", "book": book, "stage": stage,
                       "term": t_sem(book), "scope": chapters[:half],
                       "examId": f"gkp_exam_{CODE[book]}_mid_{tag.lower()}"})
    for tag in ("A", "B"):
        papers.append({"paper": f"期末测试卷{tag}", "kind": "fin", "book": book, "stage": stage,
                       "term": t_sem(book), "scope": chapters,
                       "examId": f"gkp_exam_{CODE[book]}_final_{tag.lower()}"})


for p in papers:
    p["points"] = [{"id": t["id"], "name": t["name"], "level": t["level"],
                    "chapter": t["chapter"], "description": t.get("description", ""),
                    "mastery_criteria": t.get("mastery_criteria", [])}
                   for t in by_book[p["book"]]
                   if t["chapter"] in p["scope"] or any(t["chapter"].startswith(s + " · ") for s in p["scope"])]

shards, cur = [], []
for p in papers:
    if cur and (p["book"] != cur[0]["book"] or len(cur) >= 2):
        shards.append(cur)
        cur = []
    cur.append(p)
if cur:
    shards.append(cur)

index = []
for i, grp in enumerate(shards, 1):
    tag = f"GKP_E{i:02d}"
    payload = {"shard": tag, "subject": "geography-kepu", "edition": "科普版",
               "book": grp[0]["book"], "stage": grp[0]["stage"], "spec": SPEC[grp[0]["stage"]],
               "papers": grp, "out": f"data/geography-kepu/exams/<册>/<卷>.json"}
    json.dump(payload, open(os.path.join(SD, f"{tag}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    index.append({"shard": tag, "book": grp[0]["book"], "papers": [x["paper"] for x in grp],
                  "points": sum(len(x["points"]) for x in grp)})
json.dump(index, open(os.path.join(SD, "_INDEX.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"卷 {len(papers)} / 分片 {len(shards)}")
for x in index[:6]:
    print(" ", x["shard"], x["book"], x["papers"], x["points"])
