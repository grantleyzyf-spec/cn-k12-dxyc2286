#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科教版高中物理单卷自检器（150 分 / 90 分钟 / 21 题）。

用法：python3 scripts/check_phys_hkjy_exam.py <卷.json> | --book <册> | --all
检查：字段齐全 · 21 题连续 · 逐段题数与分值 · 段合计＝rule 分值与 fullScore ·
      每题 topicIds 属本册且落在 scope · 章卷覆盖全部课时点 · 题干/解析字数 ·
      选择题四选项 · 解答类 scoreRule 各步和＝题分 · 与题库相似度 <0.85 · 答案位 ≥15%
"""
import difflib
import glob
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
HAN = re.compile(r"[\u4e00-\u9fa5]")
CN = "零一二三四五六七八九十"
STRUCT = [("一、单项选择题", "choice", 10, 3), ("二、多项选择题", "multi", 5, 4),
          ("三、实验题", "experiment", 2, 15), ("四、计算题", "calc", 4, None)]
CALC = [15, 18, 18, 19]
NO_SIM = False  # --no-similarity：CI 跳过与题库的逐题相似度比对（慢）


def han(s):
    return len(HAN.findall(s or ""))


def load():
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    Q = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
    return {t["id"]: t for t in T}, Q


def check(path, tmap, bank):
    E = []
    d = json.load(open(path, encoding="utf-8"))
    for k in ("book", "kind", "paper", "duration", "fullScore", "scope", "sections", "examId"):
        if k not in d:
            E.append("缺字段 %s" % k)
    if E:
        return E
    if d["fullScore"] != 150 or d["duration"] != 90:
        E.append("满分/时长 %s/%s ≠ 150/90" % (d["fullScore"], d["duration"]))
    secs = d["sections"]
    if len(secs) != 4:
        E.append("段数 %d ≠ 4" % len(secs))
    items = [it for s in secs for it in s.get("items") or []]
    if len(items) != 21:
        E.append("题数 %d ≠ 21" % len(items))
    if [it.get("no") for it in items] != list(range(1, len(items) + 1)):
        E.append("题号不连续")
    total = 0
    for i, (title, typ, cnt, each) in enumerate(STRUCT):
        if i >= len(secs):
            break
        s = secs[i]
        its = s.get("items") or []
        want = CALC if each is None else [each] * cnt
        if len(its) != cnt:
            E.append("第%d段题数 %d ≠ %d" % (i + 1, len(its), cnt))
        if [it.get("score") for it in its] != want:
            E.append("第%d段分值序列 %s ≠ %s" % (i + 1, [it.get("score") for it in its], want))
        m = re.search(r"共\s*(\d+)\s*分", s.get("title", ""))
        if m and int(m.group(1)) != sum(want):
            E.append("第%d段 rule 分 %s ≠ %d" % (i + 1, m.group(1), sum(want)))
        total += sum(want)
    if total != 150:
        E.append("全卷合计 %d ≠ 150" % total)
    # 题级
    scope = d.get("scope") or []
    scope_ids = {t for t, o in tmap.items() if any(o["chapter"] == sc or o["chapter"].startswith(sc + " · ") for sc in scope)}
    cover = set()
    for it in items:
        tids = it.get("topicIds") or []
        if not tids:
            E.append("第%s题 topicIds 空" % it.get("no"))
        for t in tids:
            if t not in tmap:
                E.append("第%s题 topicId %s 不存在" % (it.get("no"), t))
            elif t not in scope_ids:
                E.append("第%s题 topicId %s 不在 scope" % (it.get("no"), t))
            cover.add(t)
        if han(it.get("stem")) < 12:
            E.append("第%s题题干 <12 字" % it.get("no"))
        if han(it.get("analysis")) < 25:
            E.append("第%s题解析 <25 汉字" % it.get("no"))
        if it.get("type") in ("choice", "multi"):
            opts = it.get("options") or []
            if len(opts) != 4 or [o.get("label") for o in opts] != list("ABCD"):
                E.append("第%s题选项非 ABCD 四项" % it.get("no"))
            ans = str(it.get("answer") or "")
            if it.get("type") == "multi":
                if not (2 <= len(ans) <= 4 and set(ans) <= set("ABCD")
                        and len(set(ans)) == len(ans) and ans == "".join(sorted(ans))):
                    E.append("第%s题多选答案应为按字母序的 2–4 个 ABCD 组合，现 %s" % (it.get("no"), ans or "空"))
            elif ans not in list("ABCD"):
                E.append("第%s题答案不在 ABCD" % (it.get("no")))
        if it.get("type") in ("calc", "experiment", "short-answer"):
            sr = it.get("scoreRule") or []
            if not sr:
                E.append("第%s题缺 scoreRule" % it.get("no"))
            else:
                sm = sum(float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*分", " ".join(sr) if isinstance(sr[0], str) else json.dumps(sr, ensure_ascii=False)))
                if abs(sm - float(it.get("score", 0))) > 1e-6:
                    E.append("第%s题 scoreRule 合计 %s ≠ %s" % (it.get("no"), sm, it.get("score")))
    if d.get("kind") == "unit":
        need = {t for t in scope_ids if tmap[t]["level"] == "lesson"}
        miss = need - cover
        if miss:
            E.append("章卷未覆盖课时点 %d 个：%s" % (len(miss), "、".join(sorted(miss))[:80]))
    # 原创性
    for it in ([] if NO_SIM else items):
        best = 0.0
        for q in bank:
            r = difflib.SequenceMatcher(None, it.get("stem", ""), q.get("prompt", "")).ratio()
            if r > best:
                best = r
                if best >= 0.85:
                    break
        if best >= 0.85:
            E.append("第%s题与题库相似 %.2f ≥0.85" % (it.get("no"), best))
            break
    ans = Counter(it.get("answer") for it in items if it.get("type") == "choice")
    if ans:
        n = sum(ans.values())
        low = [k for k, v in ans.items() if v / n < 0.15]
        if low:
            E.append("答案位偏低 %s（%s）" % (low, dict(ans)))
    return E


def main():
    global NO_SIM
    tmap, bank = load()
    args = sys.argv[1:]
    if "--no-similarity" in args:
        NO_SIM = True
        args = [a for a in args if a != "--no-similarity"]
    if not args:
        print("用法：check_phys_hkjy_exam.py <卷.json> | --book <册> | --all")
        return 2
    if args[0] == "--all":
        files = sorted(glob.glob(os.path.join(D, "exams", "*", "*.json")))
    elif args[0] == "--book":
        files = sorted(glob.glob(os.path.join(D, "exams", args[1], "*.json")))
    else:
        files = args
    bad = 0
    for f in files:
        E = check(f, tmap, bank)
        name = os.path.basename(f)
        if E:
            bad += 1
            print("❌", name, len(E), "条")
            for e in E[:12]:
                print("   -", e)
        else:
            print("✅", name)
    print("\n共 %d 卷 · 不合格 %d" % (len(files), bad))
    print("RESULT: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
