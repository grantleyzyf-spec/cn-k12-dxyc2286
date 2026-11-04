#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_geo_lujiao_exam.py —— 鲁教版高中地理单卷自检器（只读）。

用法：
  /usr/bin/python3 scripts/check_geo_lujiao_exam.py <卷.json>
  /usr/bin/python3 scripts/check_geo_lujiao_exam.py --book 必修第一册
  /usr/bin/python3 scripts/check_geo_lujiao_exam.py --all
检查项（任一不过 exit 1）：结构 / 学段口径 / 分值 / 题号 / 知识点归属与覆盖 /
题目质量 / 原创性(<0.85) / 答案位(≥15%) / 卷名口径（单元卷用「单元」）。
"""
import difflib, glob, json, os, re, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-lujiao")
TOPICS = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
QS = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
SK = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
T = {t["id"]: t for t in TOPICS}
UCH = {u["chapter"] for u in SK["units"]}
PROMPTS = [q["prompt"] for q in QS]


def cjk(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def check(path):
    errs = []
    d = json.load(open(path, encoding="utf-8"))
    for k in ("book", "kind", "term", "grade", "stage", "paper", "duration", "fullScore", "examId", "scope", "sections"):
        if k not in d:
            errs.append("缺字段 %s" % k)
    if errs:
        return errs
    # 学段口径
    if (d["fullScore"], d["duration"]) != (150, 150):
        errs.append("分值/时长应 150/150，实为 %s/%s" % (d["fullScore"], d["duration"]))
    sec = d["sections"]
    if len(sec) != 2:
        errs.append("应为两段，实为 %d" % len(sec))
        return errs
    cnt = [len(s["items"]) for s in sec]
    if cnt != [18, 6]:
        errs.append("题数应 [18,6]，实为 %s" % cnt)
    # 分段分值
    for s in sec:
        m = re.search(r"共\s*(\d+)\s*分", s.get("rule", ""))
        tot = sum(i["score"] for i in s["items"])
        if m and int(m.group(1)) != tot:
            errs.append("段「%s」rule=%s 与 items 合计 %d 不等" % (s["title"][:12], m.group(1), tot))
        if abs(tot - (54 if s is sec[0] else 96)) > 0:
            errs.append("段分值应 54/96，实为 %d" % tot)
    items = [i for s in sec for i in s["items"]]
    if sum(i["score"] for i in items) != 150:
        errs.append("全卷合计 %d != 150" % sum(i["score"] for i in items))
    if [i["no"] for i in items] != list(range(1, len(items) + 1)):
        errs.append("题号不连续")
    # 知识点
    scope = set(d["scope"])

    def in_scope_ch(ch):
        return any(ch == sc or ch.startswith(sc + " · ") for sc in scope)

    in_scope = {t["id"] for t in TOPICS if in_scope_ch(t["chapter"])}
    for i in items:
        if not i.get("topicIds"):
            errs.append("题 %s 无 topicIds" % i["no"])
        else:
            bad = [x for x in i["topicIds"] if x not in in_scope]
            if bad:
                errs.append("题 %s 引用了 scope 外的点 %s" % (i["no"], bad))
    covered = {x for i in items for x in i.get("topicIds", [])}
    if d["kind"] == "unit":
        lesson_pts = {t["id"] for t in TOPICS if in_scope_ch(t["chapter"]) and t["level"] == "lesson"}
        miss = lesson_pts - covered
        if miss:
            errs.append("单元卷未覆盖全部课时点：缺 %s" % sorted(miss)[:5])
    else:
        for ch in scope:
            u = next(t for t in TOPICS if t["chapter"] == ch and t["level"] == "unit")
            n = sum(1 for i in items if u["id"] in i.get("topicIds", []) or
                    any(in_scope_ch(T[x]["chapter"]) and T[x]["chapter"].startswith(ch) for x in i.get("topicIds", [])))
            if n < 2:
                errs.append("单元「%s」仅 %d 题（应 ≥2）" % (ch[-10:], n))
        cov_rate = len({x for x in covered if T[x]["level"] == "lesson"}) / max(1, len([t for t in TOPICS if in_scope_ch(t["chapter"]) and t["level"] == "lesson"]))
        if cov_rate < 0.8:
            errs.append("课时点覆盖率 %.0f%% < 80%%" % (cov_rate * 100))
    # 题目质量
    for i in items:
        if len(i.get("stem", "")) < 12:
            errs.append("题 %s 题干 <12 字" % i["no"])
        if cjk(i.get("analysis", "")) < 40:
            errs.append("题 %s 解析 <40 汉字" % i["no"])
        if i.get("type") == "choice":
            labs = [o["label"] for o in i.get("options") or []]
            if labs != ["A", "B", "C", "D"] or i.get("answer") not in labs:
                errs.append("题 %s 选项/答案不合规" % i["no"])
            if len({o["text"] for o in i["options"]}) != 4:
                errs.append("题 %s 选项文本重复" % i["no"])
        if i.get("type") == "short":
            if sum(x["score"] for x in i.get("scoreRule") or []) != i["score"]:
                errs.append("题 %s scoreRule 之和 != 题分" % i["no"])
        # 原创性
        for p in PROMPTS:
            if difflib.SequenceMatcher(None, i["stem"], p).ratio() >= 0.85:
                errs.append("题 %s 与题库重复（相似度≥0.85）" % i["no"]); break
    # 答案位
    a = Counter(i["answer"] for i in sec[0]["items"])
    if len(a) != 4 or min(a.values()) / 18 < 0.15:
        errs.append("答案位失衡 %s" % dict(a))
    # 难度三档
    if {i["difficulty"] for i in items} != {"basic", "standard", "hard"}:
        errs.append("难度三档不齐")
    # 卷名口径
    if d["kind"] == "unit":
        if not re.search(r"第[一二三四五六七八九十]+单元 .+ 测试卷$", d["paper"]):
            errs.append("单元卷名应「第N单元 <名> 测试卷」，实为「%s」" % d["paper"])
        if d["paper"] != d["scope"][0] + " 测试卷":
            errs.append("单元卷名与 scope 不一致")
        if d["scope"][0] not in UCH:
            errs.append("scope 章名不在骨架 19 单元内")
    return errs


def main():
    args = sys.argv[1:]
    files = []
    if not args or args[0] == "--all":
        files = sorted(glob.glob(os.path.join(D, "exams", "*", "*.json")))
    elif args[0] == "--book":
        files = sorted(glob.glob(os.path.join(D, "exams", args[1], "*.json")))
    else:
        files = [args[0]]
    bad = 0
    for f in files:
        e = check(f)
        if e:
            bad += 1
            print("❌ %s" % os.path.basename(f))
            for x in e[:6]:
                print("     - %s" % x)
    print("\n合计 %d 卷｜不合格 %d 卷" % (len(files), bad))
    if bad:
        sys.exit(1)
    print("LUJIAO EXAMS PASSED")


if __name__ == "__main__":
    main()
