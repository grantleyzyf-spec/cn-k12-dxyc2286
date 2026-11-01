# -*- coding: utf-8 -*-
"""合并题库分片 → data/math-qd/questions.json，并回写 topics.diagnostic_question。

用法: python3 scripts/qd_merge_bank.py [/tmp/qd_bank]   # 默认 data/math-qd/_bank
分片格式：顶层题目数组（或 {"questions": [...]}）。
合并后按 topicId、id 排序；每个知识点的首个题目写回 diagnostic_question。
"""
import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QD = os.path.join(ROOT, "data", "math-qd")

FIELDS = ("id", "topicId", "prompt", "question", "options", "answer", "type", "difficulty", "explanation", "verify")


def main():
    bank = sys.argv[1] if len(sys.argv) > 1 else os.path.join(QD, "_bank")
    files = sorted(glob.glob(os.path.join(bank, "*.json")))
    if not files:
        sys.exit(f"没有分片：{bank}")
    all_q = {}
    for f in files:
        data = json.load(open(f, encoding="utf-8"))
        items = data.get("questions", []) if isinstance(data, dict) else data
        for q in items:
            q = {k: q[k] for k in FIELDS if k in q}
            if q.get("id") in all_q:
                print("!! 重复题 id:", q["id"], "来自", os.path.basename(f))
                continue
            all_q[q["id"]] = q
    qs = sorted(all_q.values(), key=lambda q: (q["topicId"], q["id"]))

    topics = json.load(open(os.path.join(QD, "topics.json"), encoding="utf-8"))
    first = {}
    for q in qs:
        first.setdefault(q["topicId"], q)
    n_fill = 0
    for t in topics:
        q = first.get(t["id"])
        if q:
            dq = {"question": q["prompt"], "answer": q["answer"]}
            if t.get("diagnostic_question") != dq:
                t["diagnostic_question"] = dq
                n_fill += 1

    by_topic = Counter(q["topicId"] for q in qs)
    need = {"lesson": 8, "unit": 5}
    short = [(t["id"], t["level"], by_topic.get(t["id"], 0)) for t in topics
             if by_topic.get(t["id"], 0) < need[t["level"]]]
    print(f"分片 {len(files)} 个 | 题 {len(qs)} | 覆盖知识点 {len(by_topic)}/{len(topics)}")
    print("难度:", Counter(q["difficulty"] for q in qs))
    print("答案位:", Counter(q["answer"] for q in qs if q["type"] == "choice"))
    print("回写 diagnostic_question:", n_fill)
    print("题量不足的知识点:", len(short), short[:6])
    json.dump(qs, open(os.path.join(QD, "questions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(topics, open(os.path.join(QD, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WRITTEN", os.path.join(QD, "questions.json"))


if __name__ == "__main__":
    main()
