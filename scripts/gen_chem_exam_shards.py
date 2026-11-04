#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：试卷分片（31 单元卷 ＋ 28 期中期末 = 59 卷），每片 2 卷、同册不跨片。"""
import json
import math
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "chemistry")
SD = os.path.join(D, "_exam_shards")
os.makedirs(SD, exist_ok=True)

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
BOOKS = ["九年级上册", "九年级下册", "必修第一册", "必修第二册",
         "选择性必修第一册", "选择性必修第二册", "选择性必修第三册"]
CODE = {"九年级上册": "c9a", "九年级下册": "c9b", "必修第一册": "cb1", "必修第二册": "cb2",
        "选择性必修第一册": "cx1", "选择性必修第二册": "cx2", "选择性必修第三册": "cx3"}
SEM = {"九年级上册": "上", "九年级下册": "下", "必修第一册": "上", "必修第二册": "下",
       "选择性必修第一册": "上", "选择性必修第二册": "下", "选择性必修第三册": "上"}
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

by_book = {}
for t in topics:
    by_book.setdefault(t["chapter"].split(" ")[0], []).append(t)

papers = []
for book in BOOKS:
    pts = by_book.get(book, [])
    stage = "初中" if book.startswith("九") else "高中"
    chapters = [t["chapter"] for t in pts if t.get("level") == "unit"]
    for idx, ch in enumerate(chapters, 1):
        title = ch.split(" ", 1)[1]
        papers.append({"paper": f"{title} 测试卷", "kind": "unit", "book": book, "stage": stage,
                       "term": SEM[book], "grade": pts[0]["grade"], "scope": [ch],
                       "examId": f"chem_exam_{CODE[book]}_u{idx:02d}"})
    half = max(1, math.ceil(len(chapters) / 2))
    for tag in ("A", "B"):
        papers.append({"paper": f"期中测试卷{tag}", "kind": "mid", "book": book, "stage": stage,
                       "term": SEM[book], "grade": pts[0]["grade"], "scope": chapters[:half],
                       "examId": f"chem_exam_{CODE[book]}_m{tag.lower()}"})
        papers.append({"paper": f"期末测试卷{tag}", "kind": "fin", "book": book, "stage": stage,
                       "term": SEM[book], "grade": pts[0]["grade"], "scope": chapters,
                       "examId": f"chem_exam_{CODE[book]}_f{tag.lower()}"})

# 每片 2 卷、同册不跨片
shards, cur = [], []
for p in papers:
    if cur and (len(cur) >= 2 or cur[0]["book"] != p["book"]):
        shards.append(cur)
        cur = []
    cur.append(p)
if cur:
    shards.append(cur)

for f in os.listdir(SD):
    if f.startswith("CHEM_E"):
        os.remove(os.path.join(SD, f))
for i, sh in enumerate(shards, 1):
    sid = f"CHEM_E{i:02d}"
    avail = {}
    for p in sh:
        pts = [t for t in by_book.get(p["book"], [])
               if any(t["chapter"] == s or t["chapter"].startswith(s + " · ") for s in p["scope"])]
        avail[p["examId"]] = [{"id": t["id"], "name": t["name"], "level": t["level"],
                               "chapter": t["chapter"]} for t in pts]
    data = {"shard": sid, "papers": sh, "spec": SPEC[sh[0]["stage"]],
            "topics": avail,
            "out": os.path.join(D, "exams", "{book}", "{paper}.json")}
    with open(os.path.join(SD, f"{sid}.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
print(f"卷 {len(papers)} → 分片 {len(shards)}")
for i, sh in enumerate(shards, 1):
    print(f"  CHEM_E{i:02d} {sh[0]['book']:10} " + " / ".join(p["paper"][:16] for p in sh))
