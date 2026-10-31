# -*- coding: utf-8 -*-
"""数学「课时级」建点合并器（幂等）。

输入：data/math/ke_json/<册>.json —— 每册一份，形如
{
  "book": "一年级上册",
  "keshi": [
    {"name": "1～5的认识", "unit": "第一单元", "unit_name": "5以内数的认识和加、减法",
     "page": 14, "domain": "数与代数", "type": "conceptual",
     "tags": ["数与代数", "教材课时", "数与运算"],
     "description": "...", "mastery_criteria": ["..."],
     "standards": [{"id": "mat-2022:1.XY.01", "confidence": "exact",
                    "quote": "...", "sourceLine": 732}],
     "questions": [ {"type":"choice", ...}, ... 5 条 ]}
  ]
}

本器负责：分配 id、拼 chapter、连先修边、镜像 prerequisites、写回
data/math/{topics,questions,dependencies}.json。题目内容一律由 ke_json 提供，本器不改写。

id 规则：1–9 年级用 mat_p（从 1000 起，避开既有 1–963），10–14 年级（高中）用 mat_h（从 300 起）。
chapter 规则：`<册> <单元> <单元名> · <课时名>`（与单元级点 `… <单元名>` 并存，便于按册按单元聚合）。
先修：单元级点 → 课时点（hard）；同一单元内上一课时 → 本课时（soft）。

用法：python3 scripts/build_math_ke_points.py [--book 一年级上册] [--dry-run]
"""
import argparse
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math"
KE = f"{D}/ke_json"

META = {
 "一年级上册": (1, "上"), "一年级下册": (1, "下"),
 "二年级上册": (2, "上"), "二年级下册": (2, "下"),
 "三年级上册": (3, "上"), "三年级下册": (3, "下"),
 "四年级上册": (4, "上"), "四年级下册": (4, "下"),
 "五年级上册": (5, "上"), "五年级下册": (5, "下"),
 "六年级上册": (6, "上"), "六年级下册": (6, "下"),
 "七年级上册": (7, "上"), "七年级下册": (7, "下"),
 "八年级上册": (8, "上"), "八年级下册": (8, "下"),
 "九年级上册": (9, "上"), "九年级下册": (9, "下"),
 "必修第一册": (10, "上"), "必修第二册": (11, "上"),
 "选择性必修第一册": (12, "上"), "选择性必修第二册": (13, "上"),
 "选择性必修第三册": (14, "上"),
}
KE_TAG = "教材课时"


def load(name):
    return json.load(open(f"{D}/{name}.json", encoding="utf-8"))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def next_id(prefix, used, start):
    n = start
    while f"{prefix}{n:03d}" in used:
        n += 1
    used.add(f"{prefix}{n:03d}")
    return f"{prefix}{n:03d}"


def build_book(path, topics, questions, deps, used_p, used_h, dry):
    spec = json.load(open(path, encoding="utf-8"))
    book = spec["book"]
    grade, semester = META[book]
    prefix = "mat_" + ("h" if grade >= 10 else "p")
    start = 300 if grade >= 10 else 1000
    unit_index = {}
    for t in topics:
        ch = t.get("chapter") or ""
        if ch.startswith(book + " ") and KE_TAG not in (t.get("tags") or []):
            unit_index[ch] = t["id"]
    added = skipped = 0
    prev_in_unit = {}
    for ke in spec["keshi"]:
        unit, uname = ke["unit"], ke["unit_name"]
        chapter = f"{book} {unit} {uname} · {ke['name']}"
        exists = next((t for t in topics if t.get("chapter") == chapter), None)
        if exists:
            skipped += 1
            prev_in_unit.setdefault(unit, exists["id"])
            continue
        pid = next_id(prefix, used_p if prefix == "mat_p" else used_h, start)
        prereq, edge_types = [], {}
        up = next((tid for ch, tid in unit_index.items() if ch == f"{book} {unit} {uname}"), None)
        if up:
            prereq.append(up)
            edge_types[up] = "hard"
        pv = prev_in_unit.get(unit)
        if pv:
            prereq.append(pv)
            edge_types[pv] = "soft"
        topic = {
            "id": pid,
            "name": ke["name"],
            "subject": "math",
            "domain": ke["domain"],
            "grade": grade,
            "semester": semester,
            "chapter": chapter,
            "type": ke.get("type") or "conceptual",
            "description": ke["description"],
            "mastery_criteria": ke["mastery_criteria"][:3],
            "diagnostic_question": {"question": "", "answer": ""},
            "external": False,
            "standards": ke.get("standards") or [],
            "tags": ke["tags"],
            "prerequisites": prereq,
            "curriculumRef": (ke.get("standards") or [{}])[0].get("id", ""),
            "verified": False,
            "page": ke.get("page"),
        }
        qs = []
        for i, q in enumerate(ke["questions"], 1):
            item = dict(q)
            item["id"] = f"{pid}_q{i}"
            item["topicId"] = pid
            item["subject"] = "math"
            item.setdefault("question", item.get("prompt", ""))
            if item.get("type") == "choice":
                item["choices"] = item.get("options") or []
            else:
                item.setdefault("choices", [])
                item.setdefault("options", [])
            qs.append(item)
        first = next((q for q in qs if q.get("type") == "choice"), None)
        if first:
            topic["diagnostic_question"] = {"question": first["prompt"], "answer": first["answer"]}
        if not prereq:
            topic["root_reason"] = f"起始知识点：{book} {unit} {ke['name']} 为本图谱内无前置的起始课时"
        topics.append(topic)
        questions.extend(qs)
        for p, ty in edge_types.items():
            deps.append({"from": p, "to": pid, "type": ty})
        prev_in_unit[unit] = pid
        added += 1
    return book, added, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    files = sorted(glob.glob(f"{KE}/*.json"))
    if a.book:
        files = [f for f in files if os.path.basename(f)[:-5] == a.book]
    if not files:
        print("ke_json 下没有匹配文件")
        return
    topics, questions, deps = load("topics"), load("questions"), load("dependencies")
    used_p = {t["id"] for t in topics}
    used_h = set(used_p)
    total = 0
    for f in files:
        book, add, skip = build_book(f, topics, questions, deps, used_p, used_h, a.dry_run)
        total += add
        print(f"{book}: 新增 {add} 课时点 / {add*5} 题（已存在跳过 {skip}）")
    print(f"合计新增 {total} 点 / {total*5} 题；期末口径 topics {len(topics)} / questions {len(questions)} / deps {len(deps)}")
    if a.dry_run or total == 0:
        return
    for name, obj in (("topics", topics), ("questions", questions), ("dependencies", deps)):
        with open(f"{D}/{name}.json", "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    print("✅ 已写回 topics/questions/dependencies")


if __name__ == "__main__":
    main()
