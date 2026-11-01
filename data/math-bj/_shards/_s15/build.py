# -*- coding: utf-8 -*-
"""把 data_a/b/c.py 组装成 _bank/S15.json 并自检。"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SHARDS = "/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj/_shards"
BANK = os.path.join(os.path.dirname(SHARDS), "_bank")
sys.path.insert(0, HERE)

import data_a
import data_b
import data_c

LABELS = "ABCD"
src = json.load(open(os.path.join(SHARDS, "S15.json"), encoding="utf-8"))
cands = {}
for c in src["std_candidates"]:
    cands[c["id"]] = c["quote"]  # 同 id 后出现者覆盖，与 check_bank 一致

raw = data_a.POINTS + data_b.POINTS + data_c.POINTS
pts_meta = {p["id"]: p for p in src["points"]}

errs = []
if set(p["topicId"] for p in raw) != set(pts_meta):
    errs.append("知识点集合与 S15.json 不一致")

out_points = []
ci = 0
for rd in raw:
    tid = rd["topicId"]
    meta = pts_meta[tid]
    need = 5 if meta["level"] == "unit" else 8
    if len(rd["questions"]) != need:
        errs.append(f"{tid} 题量 {len(rd['questions'])} 应 {need}")
    sid = rd["std_id"]
    if sid is not None and sid not in cands:
        errs.append(f"{tid} std_id 不在候选集 {sid}")
    std = {"id": sid, "quote": cands[sid]} if sid else None
    desc = rd["description"]
    if not (40 <= len(desc) <= 160):
        errs.append(f"{tid} description 长度 {len(desc)}")
    if not (60 <= len(desc) <= 140):
        print(f"[warn] {tid} description {len(desc)} 字（建议 60–140）")
    if not (1 <= len(rd["mastery_criteria"]) <= 3):
        errs.append(f"{tid} mastery 条数")
    for m in rd["mastery_criteria"]:
        if len(m) > 60:
            errs.append(f"{tid} mastery 超 60：{m[:14]}")
        elif len(m) > 50:
            print(f"[warn] {tid} mastery {len(m)} 字：{m}")
    if not (2 <= len(rd["misconceptions"]) <= 3):
        errs.append(f"{tid} misconceptions 条数")
    for m in rd["misconceptions"]:
        if len(m) > 50:
            errs.append(f"{tid} misconception 超 50：{m[:14]}")
        elif len(m) > 40:
            print(f"[warn] {tid} misconception {len(m)} 字：{m}")

    qs = []
    prompts = set()
    for i, q in enumerate(rd["questions"], 1):
        pr = q["prompt"]
        if len(pr) < 12:
            errs.append(f"{tid}_q{i} 题干 <12 字")
        if pr in prompts:
            errs.append(f"{tid}_q{i} 题干重复")
        prompts.add(pr)
        if len(q["explanation"]) < 20:
            errs.append(f"{tid}_q{i} explanation <20")
        t = q["type"]
        item = {"id": f"{tid}_q{i}", "topicId": tid, "prompt": pr, "question": pr,
                "type": t, "difficulty": q["difficulty"]}
        if t == "choice":
            correct = q["_correct"]
            ds = q["_distractors"]
            if len(ds) != 3:
                errs.append(f"{tid}_q{i} 干扰项不是 3 个")
            pos = ci % 4
            ci += 1
            opts = ds[:pos] + [correct] + ds[pos:]
            item["options"] = [{"label": LABELS[k], "text": v} for k, v in enumerate(opts)]
            item["answer"] = LABELS[pos]
        else:
            item["answer"] = str(q["answer"])
        if t == "numeric":
            item["verify"] = q["verify"]
            if abs(float(eval(q["verify"])) - float(q["answer"])) > 1e-6:
                errs.append(f"{tid}_q{i} verify 与 answer 不等")
        if t == "short-answer" and len(str(q["answer"])) < 30:
            errs.append(f"{tid}_q{i} 参考答案 <30")
        item["explanation"] = q["explanation"]
        item["subject"] = "math-bj"
        qs.append(item)
    diffs = Counter(x["difficulty"] for x in qs)
    if set(diffs) != {"basic", "standard", "hard"}:
        errs.append(f"{tid} 难度三档不齐 {dict(diffs)}")
    out_points.append({"topicId": tid, "description": desc,
                       "mastery_criteria": rd["mastery_criteria"],
                       "misconceptions": rd["misconceptions"],
                       "std": std, "questions": qs})

bank = {"shard": "S15", "subject": "math-bj", "book": "三下", "grade": 3,
        "segment": 2, "points": out_points}

allq = [q for p in out_points for q in p["questions"]]
print("points=%d q=%d type=%s diff=%s" % (
    len(out_points), len(allq),
    dict(Counter(q["type"] for q in allq)),
    dict(Counter(q["difficulty"] for q in allq))))
print("choice label 分布:", dict(Counter(q["answer"] for q in allq if q["type"] == "choice")))
print("std 已挂:", sum(1 for p in out_points if p["std"]), "/", len(out_points))

if errs:
    print("SELF-CHECK FAIL:", len(errs))
    for e in errs:
        print("  -", e)
    sys.exit(1)

os.makedirs(BANK, exist_ok=True)
path = os.path.join(BANK, "S15.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(bank, f, ensure_ascii=False, indent=1)
print("written:", path)
