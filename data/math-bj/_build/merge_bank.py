# -*- coding: utf-8 -*-
"""合并分片产出 → data/math-bj/{topics,questions,dependencies}.json

用法:
  python3 merge_bank.py            # 干跑：打印缺片/点数/题量核对
  python3 merge_bank.py --write    # 落库
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                     # data/math-bj
SH = os.path.join(ROOT, "_shards")
BANK = os.path.join(ROOT, "_bank")
SUBJECT = "math-bj"
BOOKS = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "五上", "六上",
         "七上", "七下", "八上", "八下", "九上"]
SEG_NAME = {1: "小学低年级", 2: "小学中年级", 3: "小学高年级", 4: "初中"}


def seg_of(g):
    return 1 if g <= 2 else 2 if g <= 4 else 3 if g <= 6 else 4


def main():
    write = "--write" in sys.argv
    sk = json.load(open(os.path.join(HERE, "_skeleton.json"), encoding="utf-8"))
    points = {p["id"]: p for p in sk["topics"]}
    edges = sk["edges"]

    bank, missing, extra = {}, [], []
    for f in sorted(os.listdir(SH)):
        if not re.fullmatch(r"S\d{2}\.json", f):
            continue
        sid = f[:-5]
        bp = os.path.join(BANK, f)
        if not os.path.exists(bp):
            missing.append(sid)
            continue
        src = json.load(open(os.path.join(SH, f), encoding="utf-8"))
        cands = {c["id"]: c["quote"] for c in src.get("std_candidates", [])}
        for row in json.load(open(bp, encoding="utf-8")).get("points", []):
            tid = row.get("topicId")
            if tid not in points:
                extra.append(tid)
                continue
            st = row.get("std")
            if st and (st.get("id") not in cands or st.get("quote") != cands[st["id"]]):
                st = None
            row["_std"] = st
            bank[tid] = row

    no_content = [t for t in points if t not in bank]
    print("分片缺产物:", missing)
    print("分片点数:", len(bank), "/", len(points), "| 未知 topicId:", extra[:3])
    if missing or no_content:
        print("未覆盖点:", len(no_content), [(points[t]['book'], points[t]['name']) for t in no_content][:5])
        if not write:
            return
        print("⚠ 有缺片，仍继续（缺片的点将没有题）")

    topics, questions = [], []
    for t in sk["topics"]:
        row = bank.get(t["id"])
        st = (row or {}).get("_std")
        std = [dict(id=st["id"], confidence="partial", quote=st["quote"])] if st else \
              (t.get("standards") or [])
        desc = (row or {}).get("description") or f"{t['name']}（{t['chapter']}）"
        mc = (row or {}).get("mastery_criteria") or [f"能说出{t['name']}的含义并完成相应练习"]
        qs = (row or {}).get("questions") or []
        item = dict(
            id=t["id"], name=t["name"], subject=SUBJECT, domain=t["domain"],
            grade=t["grade"], semester=t["semester"], chapter=t["chapter"],
            type=t["type"], level=t["level"], description=desc,
            mastery_criteria=mc, misconceptions=(row or {}).get("misconceptions") or [],
            diagnostic_question=dict(question=(qs[0]["prompt"] if qs else f"{t['name']}的核心内容是什么？"),
                                     answer=(qs[0]["answer"] if qs else "见教材")),
            external=False, standards=std,
            tags=[t["domain"], t.get("book", "")],
            prerequisites=[e["from"] for e in edges if e["to"] == t["id"]],
            verified=False,
        )
        if std:
            item["curriculumRef"] = std[0]["id"]
        if not item["prerequisites"]:
            seg = SEG_NAME[seg_of(t["grade"])]
            item["root_reason"] = (f"起始知识点：《{t['name']}》（{t['chapter']}）为{seg}"
                                   f"起始内容，图谱内无更早前置（幼儿园与学前经验不单独连边）")
        topics.append(item)
        for q in qs:
            q = dict(q)
            q["subject"] = SUBJECT
            questions.append(q)

    # 册内单元顺次边：前单元末课时 → 后单元单元点（hard，教材章序）
    by_book = OrderedDict((b, []) for b in BOOKS)
    for t in topics:
        by_book[t.get("book") or _book_of(t)].append(t)
    intra = []
    sk_unit_no = {p["id"]: p.get("unit_no") for p in sk["topics"]}
    for b, pts in by_book.items():
        units = [p["id"] for p in pts if p["level"] == "unit"]
        last_lesson = {}
        for p in pts:
            if p["level"] == "lesson":
                last_lesson[sk_unit_no.get(p["id"])] = p["id"]
        for u1, u2 in zip(units, units[1:]):
            src = last_lesson.get(sk_unit_no.get(u1))
            if src:
                intra.append({"from": src, "to": u2, "type": "hard"})
    # 册际 soft 边：前册末课时 → 后册首单元
    prev_last = None
    soft = []
    for b, pts in by_book.items():
        if prev_last and pts:
            soft.append({"from": prev_last, "to": pts[0]["id"], "type": "soft"})
        prev_last = pts[-1]["id"] if pts else prev_last
    all_edges = edges + intra + soft
    # 镜像回填 prerequisites
    for e in intra + soft:
        for t in topics:
            if t["id"] == e["to"] and e["from"] not in t["prerequisites"]:
                t["prerequisites"].append(e["from"])
                t.pop("root_reason", None)

    print("知识点", len(topics), "| 单元点", sum(1 for t in topics if t["level"] == "unit"),
          "| 课时点", sum(1 for t in topics if t["level"] == "lesson"))
    print("题", len(questions), "| 题/点", round(len(questions) / max(1, len(topics)), 2))
    print("题型", dict(Counter(q["type"] for q in questions)))
    print("难度", dict(Counter(q["difficulty"] for q in questions)))
    print("挂标点", sum(1 for t in topics if t["standards"]), "| 边", len(all_edges),
          "| soft", len(soft), "| 根节点", sum(1 for t in topics if not t["prerequisites"]))
    if write:
        json.dump(topics, open(os.path.join(ROOT, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        json.dump(questions, open(os.path.join(ROOT, "questions.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        json.dump(all_edges, open(os.path.join(ROOT, "dependencies.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写 topics.json / questions.json / dependencies.json")


def _book_of(t):
    m = re.match(r"([一二三四五六七八九])年级([上下])册", t["chapter"])
    return f"{m.group(1)}{m.group(2)}" if m else "?"


if __name__ == "__main__":
    main()
