#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题型改造分片自检。用法: python3 scripts/ddfz_check_type.py <shard.json> --shard=T01"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")
AI = ("总之", "综上所述", "赋能", "抓手", "闭环", "维度", "值得注意")
TPL = re.compile(r"^关于「.*」，下列说法正确的是")


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def main():
    path = sys.argv[1]
    tag = next((a.split("=")[1] for a in sys.argv if a.startswith("--shard=")), None)
    wm = open(os.path.join(SUB, "_batch", "type", tag, "WORKER.md"), encoding="utf-8").read()
    rows = re.findall(r"\| (pol_p\d+) \| [^|]+ \| [^|]+ \| (polq_\w+) \| (polq_\w+) \|", wm)
    want = {}
    for pid, fid, sid in rows:
        want[fid] = ("fill", pid)
        want[sid] = ("short-answer", pid)
    items = json.load(open(path, encoding="utf-8"))
    got = {x.get("id"): x for x in items}
    fails = []
    if set(got) != set(want):
        fails.append("id 不齐：缺 %s，多 %s" % (sorted(set(want) - set(got))[:4],
                                              sorted(set(got) - set(want))[:4]))
    for qid, (typ, pid) in want.items():
        q = got.get(qid)
        if not q:
            continue
        if q.get("type") != typ:
            fails.append("%s 类型应为 %s，实为 %s" % (qid, typ, q.get("type")))
        if q.get("topicId") != pid:
            fails.append("%s topicId 应为 %s" % (qid, pid))
        if q.get("options") != []:
            fails.append("%s 非选择题 options 必须为 []" % qid)
        if not isinstance(q.get("answer"), str) or not q["answer"].strip():
            fails.append("%s answer 必须是非空字符串" % qid)
        if han(q.get("prompt")) < 12:
            fails.append("%s 题干不足 12 汉字" % qid)
        if q.get("prompt") != q.get("question"):
            fails.append("%s prompt 与 question 不一致" % qid)
        if TPL.match(q.get("prompt", "")):
            fails.append("%s 用了模板题干" % qid)
        if han(q.get("explanation")) < 15:
            fails.append("%s 解析不足 15 汉字" % qid)
        if typ == "fill":
            if "____" not in q.get("prompt", ""):
                fails.append("%s 填空题干缺 ____ 空位" % qid)
            if re.search(r"[ABCD][\.．、]", q.get("prompt", "")):
                fails.append("%s 填空题干里出现了选项字母" % qid)
        else:
            kp = q.get("keypoints") or []
            if not (2 <= len(kp) <= 4):
                fails.append("%s keypoints %d 条（要 2–4）" % (qid, len(kp)))
            for k in kp:
                if han(k) < 4:
                    fails.append("%s 要点过短：%s" % (qid, k))
        for w in AI:
            if w in q.get("prompt", "") or w in q.get("explanation", ""):
                fails.append("%s 含 AI 腔词「%s」" % (qid, w))
    print("分片 %s：%d/%d 题" % (tag, len(got), len(want)))
    if fails:
        for f in fails[:25]:
            print("  ❌", f)
        print("FAILED %d" % len(fails))
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
