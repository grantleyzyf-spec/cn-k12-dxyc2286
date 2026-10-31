# -*- coding: utf-8 -*-
"""单卷自检器（单元卷 / 期中卷 / 期末卷）。只读，不写仓库。

用法：
    python3 scripts/check_math_exam_json.py data/math/exams/七年级上册/第一单元测试卷.json

检查项（任一不过即 exit 1）：
  1 结构：book/kind/paper/stage/grade/duration/fullScore/scope/sections 齐全
  2 分值与题量：各大题题数×分值 = 该段说明；全卷分值合计 = fullScore；
    卷面结构与 docs/math-exam-spec.md 的学段表逐项一致
  3 题号：全卷连续 1..N，无跳号重号
  4 知识点：每题 topicIds 必须都是**本册课时级点**（chapter 含「 · 」且以本册名开头）；
    单元卷须覆盖本单元全部课时点各 ≥1 次
  5 题目质量：stem ≥12 字；analysis ≥20 字；choice/multi 选项 4 个、label A–D、文本互异、answer 合法；
     solve 必须有 scoreRule 且分值和 = score；numeric 若给 verify 则须 eval==answer
  6 原创性：与题库 questions.json 的题干相似度 <0.85（去空白后 SequenceMatcher）
"""
import difflib
import json
import os
import re
import sys
from collections import Counter

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math"
STAGE_RULES = {
 "小学": {1: ("小学1-2", 40, 100), 2: ("小学1-2", 40, 100),
          3: ("小学3-6", 60, 100), 4: ("小学3-6", 60, 100),
          5: ("小学3-6", 60, 100), 6: ("小学3-6", 60, 100),
          7: ("初中", 90, 120), 8: ("初中", 90, 120), 9: ("初中", 90, 120),
          10: ("高中", 120, 150), 11: ("高中", 120, 150), 12: ("高中", 120, 150),
          13: ("高中", 120, 150), 14: ("高中", 120, 150)},
}
# 学段卷面模板：(段标题关键字, 题数, 每题分值)
TEMPLATES = {
 "小学1-2": [("直接写得数", 10, 2), ("填空", 10, 2), ("选择", 8, 2), ("操作", 4, 4), ("解决问题", 4, 7)],
 "小学3-6": [("计算", 6, 4), ("填空", 10, 2), ("选择", 8, 2), ("操作", 3, 4), ("解决问题", 4, 7)],
 "初中": [("选择", 10, 3), ("填空", 6, 4), ("解答", 8, None)],
 "高中": [("单选", 8, 5), ("多选", 4, 5), ("填空", 4, 5), ("解答", 6, None)],
}
CLUSTER_SCORES = {"初中": [6, 6, 8, 8, 9, 9, 10, 10], "高中": [10, 12, 12, 12, 12, 12]}
errs = []


def E(m):
    errs.append(m)


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("用法：python3 scripts/check_math_exam_json.py <卷.json>")
        sys.exit(1)
    p = sys.argv[1]
    ex = json.load(open(p, encoding="utf-8"))
    book = ex.get("book")
    for k in ("book", "kind", "paper", "stage", "grade", "duration", "fullScore", "scope", "sections"):
        if not ex.get(k):
            E(f"缺字段 {k}")
    if ex.get("kind") not in ("unit", "midterm", "final"):
        E(f"kind 非法：{ex.get('kind')}")
    grade = int(ex.get("grade") or 0)
    rule = STAGE_RULES["小学"].get(grade)
    if not rule:
        E(f"grade 非法：{grade}")
        rule = ("初中", ex.get("duration"), ex.get("fullScore"))
    stage_key, dur, full = rule
    if int(ex.get("duration") or 0) != dur:
        E(f"时长应为 {dur} 分钟（{stage_key}），实为 {ex.get('duration')}")
    if int(ex.get("fullScore") or 0) != full:
        E(f"满分应为 {full}（{stage_key}），实为 {ex.get('fullScore')}")

    # 本册课时点
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    ke = [t for t in topics if " · " in (t.get("chapter") or "") and (t.get("chapter") or "").startswith(f"{book} ")]
    ke_ids = {t["id"] for t in ke}
    if not ke:
        E(f"本册没有课时级点（book={book}）")

    secs = ex.get("sections") or []
    tmpl = TEMPLATES.get(stage_key) or []
    if len(secs) != len(tmpl):
        E(f"{stage_key} 应有 {len(tmpl)} 个大题，实为 {len(secs)}")
    for i, (kw, n, each) in enumerate(tmpl):
        if i >= len(secs):
            break
        s = secs[i]
        if kw not in (s.get("title") or ""):
            E(f"第 {i+1} 大题标题应含「{kw}」，实为「{s.get('title')}」")
        items = s.get("items") or []
        if len(items) != n:
            E(f"「{s.get('title')}」题数应为 {n}，实为 {len(items)}")
        if each:
            bad = [it.get("score") for it in items if it.get("score") != each]
            if bad:
                E(f"「{s.get('title')}」每题应为 {each} 分，异常：{bad}")
        else:
            want = CLUSTER_SCORES.get(stage_key, [])
            got = [it.get("score") for it in items]
            if len(want) == len(got) and got != want:
                E(f"「{s.get('title')}」分值序列应为 {want}，实为 {got}")

    total = sum((it.get("score") or 0) for s in secs for it in (s.get("items") or []))
    if total != full:
        E(f"全卷分值合计 {total} ≠ 满分 {full}")

    # 题号连续
    nos = [it.get("no") for s in secs for it in (s.get("items") or [])]
    if nos != list(range(1, len(nos) + 1)):
        E(f"题号不连续：{nos}")

    # 题库题干（原创性）
    bank = [norm(q.get("prompt")) for q in json.load(open(f"{D}/questions.json", encoding="utf-8"))]

    used = Counter()
    for s in secs:
        for it in s.get("items") or []:
            no = it.get("no")
            stem = it.get("stem") or ""
            if len(stem) < 12:
                E(f"第 {no} 题题干 <12 字")
            if len(it.get("analysis") or "") < 20:
                E(f"第 {no} 题解析 <20 字")
            if not it.get("answer"):
                E(f"第 {no} 题缺 answer")
            tids = it.get("topicIds") or []
            if not tids:
                E(f"第 {no} 题缺 topicIds")
            for t in tids:
                if t not in ke_ids:
                    E(f"第 {no} 题 topicIds 不在本册课时点内：{t}")
                used[t] += 1
            if it.get("difficulty") not in ("basic", "standard", "hard"):
                E(f"第 {no} 题 difficulty 非法")
            typ = it.get("type")
            if typ in ("choice", "multi"):
                opts = it.get("options") or []
                labs = [o.get("label") for o in opts]
                texts = [norm(o.get("text")) for o in opts]
                if len(opts) != 4 or labs != ["A", "B", "C", "D"]:
                    E(f"第 {no} 题选项必须 4 个且 label 为 A–D")
                if len(set(texts)) != len(texts) or any(not t for t in texts):
                    E(f"第 {no} 题选项文本有重复或为空")
                a = it.get("answer") or ""
                if typ == "choice":
                    if a not in labs:
                        E(f"第 {no} 题 answer 不在选项内")
                else:
                    if not (len(a) >= 2 and all(c in "ABCD" for c in a) and len(set(a)) == len(a)):
                        E(f"第 {no} 题多选 answer 应为 ≥2 个互异选项字母，如 ABD")
                    if len(it.get("scoreRule") or []) < 2:
                        E(f"第 {no} 题多选要给分档说明（scoreRule ≥2 条）")
            if typ == "solve":
                sr = it.get("scoreRule") or []
                if len(sr) < 2:
                    E(f"第 {no} 题解答题 scoreRule 至少 2 步")
                # 只认「N 分」（给分），排除「1 分米」「12 分钟」「3 分之二」——否则分值被虚增
                nums = [int(m.group(1)) for x in sr
                        for m in re.finditer(r"(\d+)\s*分(?!米|钟|数|之)", x)]
                if sum(nums) != (it.get("score") or 0):
                    E(f"第 {no} 题 scoreRule 分值和 {sum(nums)} ≠ 题目分值 {it.get('score')}")
            v = it.get("verify")
            if v:
                try:
                    if abs(eval(str(v)) - float(it.get("answer"))) > 1e-6:
                        E(f"第 {no} 题 verify={v} 与 answer={it.get('answer')} 不符")
                except Exception as _err:
                    # 注意别写成 `as ex`：ex 是本卷对象，except 结束后 Python 会 del 掉它，
                    # 后面任何 ex.get(...) 都会抛 UnboundLocalError（写手已被这个坑误导过一次）
                    E(f"第 {no} 题 verify 不可求值：{_err}")
            ns = norm(stem)
            for b in bank:
                if b and difflib.SequenceMatcher(None, ns, b).ratio() > 0.85:
                    E(f"第 {no} 题与题库题干相似度过高（>0.85）")
                    break

    # 单元卷覆盖检验
    if ex.get("kind") == "unit" and len(ex.get("scope") or []) == 1:
        unit = ex["scope"][0]
        need = {t["id"] for t in ke if unit in (t.get("chapter") or "")}
        miss = sorted(need - set(used))
        if miss:
            names = {t["id"]: t["name"] for t in ke}
            E(f"单元卷未覆盖 {len(miss)} 个课时点：" + "、".join(names.get(i, i) for i in miss[:6]))

    print(f"卷：{ex.get('paper')}（{book} / {stage_key} / {full} 分 / {dur} 分钟 / {len(nos)} 题）")
    print(f"覆盖课时点 {len(used)} 个 · 难度 {dict(Counter(it.get('difficulty') for s in secs for it in (s.get('items') or [])))}")
    if errs:
        print(f"\n❌ {len(errs)} 条问题：")
        for e in errs[:40]:
            print("  -", e)
        if len(errs) > 40:
            print(f"  …另有 {len(errs)-40} 条")
        sys.exit(1)
    print("✅ 自检通过")


if __name__ == "__main__":
    main()
