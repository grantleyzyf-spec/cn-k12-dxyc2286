# -*- coding: utf-8 -*-
"""把 chemistry-bj 的 topics/questions 修到 schema 口径（幂等、原子落盘）。

1) 每个点补 `diagnostic_question: {question, answer}`（取该点首题题干/答案；无题时用掌握标准自拟）
2) 所有题的 `answer` 统一转字符串（数值题原本存成 number，撞 schema `must be string`）
用法：python3 scripts/fix_chem_bj_schema.py [--write]
"""
import json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-bj")


def atomic_write(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    write = "--write" in sys.argv
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    questions = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))

    by_topic = {}
    for q in questions:
        by_topic.setdefault(q["topicId"], []).append(q)

    n_dq = 0
    for t in topics:
        dq = t.get("diagnostic_question")
        if isinstance(dq, dict) and dq.get("question") and isinstance(dq.get("answer"), str):
            continue
        qs = by_topic.get(t["id"], [])
        if qs:
            q0 = qs[0]
            question = q0["prompt"] if len(q0["prompt"]) <= 60 else q0["prompt"][:58] + "……"
            answer = str(q0["answer"])
        else:                                   # 无题兜底：用第一条掌握标准反问
            mc = (t.get("mastery_criteria") or ["本课核心内容"])[0]
            question = f"你能做到「{mc}」吗？"
            answer = "能"
        t["diagnostic_question"] = {"question": question, "answer": answer}
        n_dq += 1

    n_ans = 0
    for q in questions:
        if not isinstance(q.get("answer"), str):
            q["answer"] = str(q["answer"])
            n_ans += 1

    print(f"补 diagnostic_question {n_dq} 个；answer 转字符串 {n_ans} 处")
    if write:
        atomic_write(os.path.join(D, "topics.json"), topics)
        atomic_write(os.path.join(D, "questions.json"), questions)
        print("已写入")
    else:
        print("(dry-run，加 --write 落盘)")


if __name__ == "__main__":
    main()
