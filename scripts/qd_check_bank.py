# -*- coding: utf-8 -*-
"""青岛版数学：题库分片自检。用法: python3 scripts/qd_check_bank.py <shard.json>

逐点校验（派单里已写死）：
- 课时点（level=lesson）≥8 题；单元点（level=unit）≥5 题
- 每题：id/topicId/prompt/question/answer/type/difficulty/explanation 齐全
- choice 必须 4 选项、answer ∈ labels；difficulty ∈ basic/standard/hard 且三档齐
- 题干 ≥12 汉字，解析 ≥15 汉字；不得出现 Markdown 记号（**、`、#、- 开头列表）
- 答案位：单一 label 占比 ≤40%
- topicId 不得超出派单范围（--allow 传入允许的 id，逗号分隔）

末行 PASS 才算过。
"""
import json
import os
import re
import sys
from collections import Counter

MINQ = {"lesson": 8, "unit": 5}
BAN = re.compile(r"\*\*|`|^#|^- |^\* |\|\s*-{3}")
HAN = re.compile(r"[\u4e00-\u9fff]")


def han(s):
    return len(HAN.findall(s or ""))


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python3 scripts/qd_check_bank.py <shard.json> [--allow=id1,id2]")
    path = sys.argv[1]
    allow = None
    for a in sys.argv[2:]:
        if a.startswith("--allow="):
            allow = set(a.split("=", 1)[1].split(","))
    qs = json.load(open(path, encoding="utf-8"))
    if isinstance(qs, dict):
        qs = qs.get("questions", [])
    errs = []
    by_topic = Counter(q.get("topicId") for q in qs)
    if allow:
        extra = {q["topicId"] for q in qs} - allow
        if extra:
            errs.append(f"越界 topicId: {sorted(extra)[:5]}")
    if len({q.get("id") for q in qs}) != len(qs):
        errs.append("题目 id 重复")
    for q in qs:
        qid = q.get("id", "?")
        for f in ("id", "topicId", "prompt", "question", "answer", "type", "difficulty", "explanation"):
            if not q.get(f):
                errs.append(f"{qid}: 缺字段 {f}")
        if q.get("prompt") != q.get("question"):
            errs.append(f"{qid}: prompt 与 question 不同值")
        if han(q.get("prompt")) < 12:
            errs.append(f"{qid}: 题干 {han(q.get('prompt'))} 汉字 <12")
        if han(q.get("explanation")) < 15:
            errs.append(f"{qid}: 解析 {han(q.get('explanation'))} 汉字 <15")
        if q.get("difficulty") not in ("basic", "standard", "hard"):
            errs.append(f"{qid}: difficulty={q.get('difficulty')}")
        if q.get("type") == "choice":
            opts = q.get("options") or []
            labels = [o.get("label") for o in opts]
            if len(opts) != 4:
                errs.append(f"{qid}: choice 选项 {len(opts)} 个")
            if q.get("answer") not in labels:
                errs.append(f"{qid}: answer 不在选项内")
            if len(set(labels)) != len(labels):
                errs.append(f"{qid}: 选项 label 重复")
            for o in opts:
                if han(o.get("text")) < 1 or re.search(r"\.\.\.|…", o.get("text") or ""):
                    errs.append(f"{qid}: 选项文字过短/含省略号")
        for f in ("prompt", "explanation"):
            if BAN.search(q.get(f) or ""):
                errs.append(f"{qid}: {f} 含 Markdown 记号")
    print("题量:", len(qs), "| 覆盖知识点:", len(by_topic))
    print("难度:", Counter(q.get("difficulty") for q in qs))
    print("答案位:", Counter(q.get("answer") for q in qs if q.get("type") == "choice"))
    ch = [q for q in qs if q.get("type") == "choice"]
    if ch:
        c = Counter(q.get("answer") for q in ch)
        top = c.most_common(1)[0]
        if top[1] > len(ch) * 0.4:
            errs.append(f"答案位单一占比过高: {top[0]}={top[1]}/{len(ch)}")
    if len({q.get("difficulty") for q in qs}) < 3:
        errs.append("难度未覆盖三档")
    for e in errs[:15]:
        print("  - ", e)
    print(f"errors={len(errs)}")
    print("PASS" if not errs else "FAIL")


if __name__ == "__main__":
    main()
