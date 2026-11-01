#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把心理健康学科的单元素养测评卷（data/mental-health/exams/<册>.json）转成
「整卷测试」前端可用的卷面格式（data/mental-health/exams/web/<册>.json）。

原卷是教研向数据（no/type/topicId/unit/explain/rubric），前端 exam.js 需要的是
（itemId/type/score/stem/options/answer/analysis/topicIds/scoreRule），两者字段不同，
故单独生成一份派生物，原卷保持不动（check_exam.py 的口径与交付文档都按原卷）。

用法：python3 scripts/build_mh_exam_web.py
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "mental-health", "exams")
OUT = os.path.join(SRC, "web")

BOOK_CODE = {
    "一年级上册": "g1a", "一年级下册": "g1b", "二年级上册": "g2a", "二年级下册": "g2b",
    "三年级上册": "g3a", "三年级下册": "g3b", "四年级上册": "g4a", "四年级下册": "g4b",
    "五年级上册": "g5a", "五年级下册": "g5b", "六年级上册": "g6a", "六年级下册": "g6b",
    "七年级全一册": "g7", "八年级全一册": "g8", "九年级全一册": "g9",
    "高中一年级全一册": "g10", "高中二年级": "g11", "高中三年级": "g12",
}
JUDGE_OPTS = [{"label": "A", "text": "正确"}, {"label": "B", "text": "错误"}]


def convert_item(it, code, sec_type=None):
    """原卷题 → 前端题。判断题渲染成两个选项（正确/错误），简答渲染成解答题。"""
    no = it["no"]
    base = {"itemId": f"mh_{code}_q{no:02d}", "no": no, "stem": it["stem"],
            "score": it.get("score", 0), "topicIds": [it["topicId"]],
            "analysis": it.get("explain", "")}
    t = it.get("type") or sec_type          # 部分卷把题型写在 section 上，题内无 type
    if t == "choice":
        base["type"] = "choice"
        base["options"] = it.get("options", [])
        base["answer"] = it.get("answer", "")
    elif t == "judge":
        base["type"] = "choice"
        base["options"] = JUDGE_OPTS
        base["answer"] = "A" if it.get("answer", "√") in ("√", "对", "正确", "A") else "B"
    elif t == "short":
        base["type"] = "solve"
        base["answer"] = it.get("answer", "")
        base["scoreRule"] = it.get("rubric", [])
    else:                                     # 兜底：按填空处理
        base["type"] = "fill"
        base["answer"] = it.get("answer", "")
    return base


def convert(paper):
    book = paper["book"]
    code = BOOK_CODE.get(book) or ("g" + re.sub(r"\D", "", book))
    title = paper.get("title", "")
    short = title[len(book):].strip() if title.startswith(book) else title
    sections = []
    for sec in paper.get("sections", []):
        sections.append({
            "title": sec.get("name") or "试题",
            "rule": "",
            "items": [convert_item(it, code, sec.get("type")) for it in sec.get("items", [])],
        })
    units = []
    for bp in paper.get("blueprint") or []:
        u = bp.get("unit")
        if u and u not in units:
            units.append(u)
    if not units:
        for sec in paper.get("sections", []):
            for it in sec.get("items", []):
                u = it.get("unit")
                if u and u not in units:
                    units.append(u)
    return {
        "examId": f"mh_exam_{code}_unit",
        "subject": "mental-health",
        "edition": "北师大版",
        "book": book,
        "paper": short or "素养测评卷",
        "kind": "unit",
        "grade": paper.get("grade"),
        "stage": ("小学" if paper.get("grade", 0) <= 6 else ("初中" if paper.get("grade", 0) <= 9 else "高中")),
        "duration": paper.get("duration", 40),
        "fullScore": paper.get("fullScore", 100),
        "scope": units,
        "itemCount": sum(len(s["items"]) for s in sections),
        "sections": sections,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(p for p in glob.glob(os.path.join(SRC, "*.json")))
    n = 0
    for p in files:
        paper = json.load(open(p, encoding="utf-8"))
        if paper.get("subject") != "mental-health" or "sections" not in paper:
            continue
        page = convert(paper)
        dst = os.path.join(OUT, os.path.basename(p))
        json.dump(page, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(dst, "a", encoding="utf-8").write("\n")
        n += 1
    print(f"已生成 {n} 份前端卷面 → {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
