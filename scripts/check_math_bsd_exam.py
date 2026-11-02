
# -*- coding: utf-8 -*-
"""北师大版数学单卷自检（单元卷 / 期中A·B / 期末A·B）。只读。

用法：python3 scripts/check_math_bsd_exam.py data/math-bsd/exams/七年级上册/第一章 有理数 测试卷.json

断言：
 1 结构 book/kind/paper/stage/grade/duration/fullScore/scope/sections/examId
 2 学段模板：小学1-2 40' 100分；小学3-6 60' 100分；初中 90' 120分（段题数×分值固定）
 3 题号连续 1..N；section 分值和 = fullScore
 4 topicIds 必须是本册点；unit 卷必须覆盖 scope 章的全部点各 ≥1 次
 5 题目质量：stem ≥12 字、analysis ≥20 字、choice 4 选项 A–D 文本互异、answer 合法、solve 有 scoreRule 且分值和 = score
 6 原创性：与 data/math-bsd/questions.json 题干相似度 <0.85
"""
import difflib, json, os, re, sys
from collections import Counter

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math-bsd"
STAGE = {1: ("小学1-2", 40, 100), 2: ("小学1-2", 40, 100), 3: ("小学3-6", 60, 100), 4: ("小学3-6", 60, 100),
         5: ("小学3-6", 60, 100), 6: ("小学3-6", 60, 100), 7: ("初中", 90, 120), 8: ("初中", 90, 120), 9: ("初中", 90, 120),
         10: ("高中", 120, 150), 11: ("高中", 120, 150), 12: ("高中", 120, 150)}
TEMPLATES = {
 "小学1-2": [("直接写得数", 10, 2), ("填空", 10, 2), ("选择", 8, 2), ("操作", 4, 4), ("解决问题", 4, 7)],
 "小学3-6": [("计算", 6, 4), ("填空", 10, 2), ("选择", 8, 2), ("操作", 3, 4), ("解决问题", 4, 7)],
 "初中": [("选择", 10, 3), ("填空", 6, 4), ("解答", 8, None)],
 "高中": [("单选题", 8, 5), ("多选题", 4, 5), ("填空题", 4, 5), ("解答题", 6, None)],
}
CLUSTER = {"初中": [6, 6, 8, 8, 9, 9, 10, 10], "高中": [10, 12, 12, 12, 12, 12]}
errs = []


def E(m): errs.append(m)
def norm(s): return re.sub(r"\s+", "", s or "")


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("用法：python3 scripts/check_math_bsd_exam.py <卷.json>"); sys.exit(1)
    p = sys.argv[1]
    ex = json.load(open(p, encoding="utf-8"))
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    T = {t["id"]: t for t in topics}
    bank = json.load(open(f"{D}/questions.json", encoding="utf-8"))
    book = ex.get("book")
    for k in ("book", "kind", "paper", "stage", "grade", "duration", "fullScore", "scope", "sections", "examId"):
        if not ex.get(k): E(f"缺字段 {k}")
    if ex.get("kind") not in ("unit", "mid", "fin"): E(f"kind 非法：{ex.get('kind')}")
    g = int(ex.get("grade") or 0)
    if g not in STAGE: E(f"grade 非法 {g}"); print("RESULT: FAIL"); sys.exit(1)
    sk, dur, full = STAGE[g]
    if int(ex.get("duration") or 0) != dur: E(f"时长应 {dur}，实为 {ex.get('duration')}")
    if int(ex.get("fullScore") or 0) != full: E(f"满分应 {full}，实为 {ex.get('fullScore')}")
    secs = ex.get("sections") or []
    tmpl = TEMPLATES[sk]
    if len(secs) != len(tmpl): E(f"大题数 {len(secs)} != {len(tmpl)}")
    total, nos = 0, []
    for i, (kw, n, per) in enumerate(tmpl):
        if i >= len(secs): break
        s = secs[i]
        items = s.get("items") or []
        if len(items) != n: E(f"第{i+1}大题题数 {len(items)} != {n}")
        if kw not in (s.get("title") or ""): E(f"第{i+1}大题标题应含「{kw}」")
        for j, it in enumerate(items):
            no = it.get("no")
            nos.append(no)
            score = it.get("score")
            total += score or 0
            stem = it.get("stem") or it.get("prompt") or ""
            if len(stem) < 12: E(f"第{no}题 stem <12 字")
            ana = it.get("analysis") or it.get("explanation") or ""
            if len(ana) < 20: E(f"第{no}题 analysis <20 字")
            ty = it.get("type")
            if ty == "choice":
                opts = it.get("options") or []
                labs = [o.get("label") for o in opts]
                if len(opts) != 4 or sorted(labs) != ["A", "B", "C", "D"]: E(f"第{no}题 选项不合规")
                texts = [norm(o.get("text")) for o in opts]
                if len(set(texts)) != 4 or any(not t for t in texts): E(f"第{no}题 选项重复或空")
                if it.get("answer") not in labs: E(f"第{no}题 answer 不在选项内")
            if ty == "solve":
                sr = it.get("scoreRule") or []
                if len(sr) < 2: E(f"第{no}题 scoreRule <2 步")
                nums = [int(x.get("score") or 0) for x in sr if isinstance(x, dict)]
                if nums and sum(nums) != (score or 0): E(f"第{no}题 scoreRule 分值和 {sum(nums)} != {score}")
            # topicIds
            tids = it.get("topicIds") or ([it["topicId"]] if it.get("topicId") else [])
            if not tids: E(f"第{no}题 缺 topicIds")
            for tid in tids:
                if tid not in T: E(f"第{no}题 topicId {tid} 不存在"); continue
                if not T[tid]["chapter"].startswith(book): E(f"第{no}题 topicId {tid} 不属本册")
            # 原创性
            for q in bank:
                r = difflib.SequenceMatcher(None, norm(stem), norm(q.get("prompt"))).ratio()
                if r >= 0.85:
                    E(f"第{no}题 与题库 {q['id']} 雷同 {r:.2f}"); break
    if nos != list(range(1, len(nos) + 1)): E(f"题号不连续：{nos[:12]}")
    if total != full: E(f"分值和 {total} != 满分 {full}")
    # unit 卷覆盖
    if ex.get("kind") == "unit":
        scope = ex.get("scope") or []
        need = {t["id"] for t in topics if t["chapter"] in scope}
        got = {tid for s in secs for it in (s.get("items") or [])
               for tid in (it.get("topicIds") or ([it["topicId"]] if it.get("topicId") else []))}
        miss = need - got
        if miss: E(f"unit 卷未覆盖知识点：{sorted(miss)[:6]}（共 {len(miss)}）")
    print(f"== {ex.get('book')} / {ex.get('paper')}（{ex.get('kind')}）: 题 {len(nos)} 分 {total}")
    for e in errs[:25]: print("  ERR", e)
    print(f"RESULT: {'PASS' if not errs else 'FAIL'} errors={len(errs)}")
    sys.exit(0 if not errs else 1)


if __name__ == "__main__":
    main()
