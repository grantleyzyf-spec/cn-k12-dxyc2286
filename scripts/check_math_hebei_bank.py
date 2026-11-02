#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冀教版数学（math-hebei）题库分片自检 / 合并前门禁。

用法：
    python3 scripts/check_math_hebei_bank.py <分片.json> [<分片2.json> ...]
    python3 scripts/check_math_hebei_bank.py data/math-hebei/_bank/S22.json

判据（与 test_math_hebei.py 的全桶口径一致，只是作用在分片上）：
    1 结构：顶层 {shard, topics[], questions[]}
    2 内容层：每个 topic 的 description ≥120 汉字、mastery_criteria 2–3 条、
      misconceptions ≥2 条、diagnostic_question 含 question/answer、domain 四类、type 枚举、
      standards 每条带 id+quote（quote 去空白后须与仓库同 id 原文逐字一致）
    3 题量：level=unit 的点 5 题、level=lesson 的点 8 题（按派单 qPerPoint 覆盖，可多不可少）
    4 题目：id 唯一且形如 mhb_qNN####、topicId 必须在本片、题型 choice/fill/numeric、
      难度 basic/standard/hard、题干 ≥12 字、解析 ≥20 汉字
    5 选择题：4 个选项、label A–D 互异、answer 在选项内、选项文本互异、
      同一片内答案位分布每挡 ≤60%
    6 数值题：answer 必须是字符串
退出码：0 全绿；1 有不合格。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "math-hebei")
HAN = re.compile(r"[\u4e00-\u9fa5]")
DOMAINS = {"数与代数", "图形与几何", "统计与概率", "综合与实践"}
QTYPES = {"choice", "fill", "numeric", "short-answer"}
DIFFS = {"basic", "standard", "hard"}


def han(s):
    return len(HAN.findall(s or ""))


def clen(s):
    """与 test_math_hebei.py 同口径：字符数（不是汉字数）。"""
    return len(s or "")


def qnorm(s):
    """去空白 + 去 ASCII 字母与标点，用于课标原文比对。"""
    s = re.sub(r"\s+", "", s or "")
    return re.sub(r"[A-Za-z0-9:;,.，。；：、（）()《》“”\"'·—\-~～]", "", s)


def levels_from_skeleton():
    p = os.path.join(D, "_skeleton.json")
    try:
        sk = json.load(open(p, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return {x["id"]: x.get("level") for x in sk.get("points") or []}


def std_pool():
    """仓库里同 id 课标原文池（所有 topics.json 里出现过的 quote）。"""
    pool = {}
    for p in glob.glob(os.path.join(ROOT, "data", "*", "topics.json")):
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        topics = data["topics"] if isinstance(data, dict) else data
        for t in topics:
            for s in t.get("standards") or []:
                sid, q = s.get("id"), s.get("quote")
                if sid and q:
                    pool.setdefault(sid, set()).add(qnorm(q))
    return pool


def check_topic(t, pool, errs, warn):
    tid = t.get("id", "?")
    if not re.match(r"^mhb_p\d{3}$", tid or ""):
        errs.append(f"{tid}: id 非法（应 mhb_p###）")
    if clen(t.get("description")) < 40:
        errs.append(f"{tid}: description {clen(t.get('description'))} 字 < 40")
    elif han(t.get("description")) < 100:
        warn.append(f"{tid}: description 汉字仅 {han(t.get('description'))}（建议 ≥100，低年级也够说明）")
    mc = t.get("mastery_criteria") or []
    if not (2 <= len(mc) <= 3):
        errs.append(f"{tid}: mastery_criteria {len(mc)} 条（应 2–3）")
    ms = t.get("misconceptions") or []
    if len(ms) < 2:
        errs.append(f"{tid}: misconceptions {len(ms)} 条（应 ≥2）")
    dq = t.get("diagnostic_question") or {}
    if not (dq.get("question") and dq.get("answer")):
        errs.append(f"{tid}: diagnostic_question 缺 question/answer")
    if t.get("domain") not in DOMAINS:
        errs.append(f"{tid}: domain 非法 {t.get('domain')}")
    if not t.get("type"):
        errs.append(f"{tid}: 缺 type")
    stds = t.get("standards") or []
    if not stds:
        errs.append(f"{tid}: 缺 standards（至少 1 条课标引用）")
    for s in stds:
        sid, q = s.get("id"), s.get("quote")
        if not (sid and q):
            errs.append(f"{tid}: standards 条目缺 id/quote")
            continue
        if sid in pool and qnorm(q) not in pool[sid]:
            errs.append(f"{tid}: 课标 {sid} 的 quote 与仓库同 id 原文不一致")


def check_question(q, point_ids, errs, seen):
    qid = q.get("id", "?")
    if not re.match(r"^mhb_q\d{6}$", qid or ""):
        errs.append(f"{qid}: id 非法（应 mhb_qNN####）")
    if qid in seen:
        errs.append(f"{qid}: id 重复")
    seen.add(qid)
    if q.get("topicId") not in point_ids:
        errs.append(f"{qid}: topicId {q.get('topicId')} 不在本片")
    if q.get("type") not in QTYPES:
        errs.append(f"{qid}: type 非法 {q.get('type')}")
    if q.get("difficulty") not in DIFFS:
        errs.append(f"{qid}: difficulty 非法 {q.get('difficulty')}")
    if clen(q.get("prompt")) < 12:
        errs.append(f"{qid}: 题干 {clen(q.get('prompt'))} 字 < 12")
    if clen(q.get("explanation")) < 20:
        errs.append(f"{qid}: 解析 {clen(q.get('explanation'))} 字 < 20")
    ans = q.get("answer")
    if not isinstance(ans, str):
        errs.append(f"{qid}: answer 必须是字符串（当前 {type(ans).__name__}）")
    if q.get("type") == "choice":
        opts = q.get("options") or []
        labels = [o.get("label") for o in opts]
        texts = [(o.get("text") or "").strip() for o in opts]
        if len(opts) != 4:
            errs.append(f"{qid}: 选择题选项 {len(opts)} 个（应 4）")
        if sorted(labels) != ["A", "B", "C", "D"]:
            errs.append(f"{qid}: 选项 label 应 A–D，实为 {labels}")
        if len(set(texts)) != len(texts):
            errs.append(f"{qid}: 选项文本有重复")
        if ans not in labels:
            errs.append(f"{qid}: answer {ans} 不在选项内")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    pool = std_pool()
    bad_total = 0
    for path in sys.argv[1:]:
        if not os.path.exists(path):
            print(f"❌ 文件不存在：{path}")
            bad_total += 1
            continue
        d = json.load(open(path, encoding="utf-8"))
        topics = d.get("topics") or []
        questions = d.get("questions") or []
        errs, warn = [], []
        if not d.get("shard"):
            errs.append("缺 shard 字段")
        point_ids = {t.get("id") for t in topics}
        sk_levels = levels_from_skeleton()
        levels = {t.get("id"): (t.get("level") or sk_levels.get(t.get("id"))) for t in topics}
        seen = set()
        for t in topics:
            check_topic(t, pool, errs, warn)
        for q in questions:
            check_question(q, point_ids, errs, seen)

        # 题量：单元点 5、课时点 8
        from collections import Counter
        cnt = Counter(q.get("topicId") for q in questions)
        for tid in point_ids:
            need = 5 if levels.get(tid) == "unit" else 8
            if cnt.get(tid, 0) != need:
                errs.append(f"{tid}: 题量 {cnt.get(tid, 0)}，应恰好 {need}（{levels.get(tid) or '未知层级'}）")

        # 答案位分布（仅同片内参考）
        pos = Counter(q.get("answer") for q in questions if q.get("type") == "choice")
        tot = sum(pos.values()) or 1
        for k, v in pos.items():
            if v / tot > 0.6:
                errs.append(f"答案位偏置：{k} 占 {v}/{tot} > 60%")

        name = os.path.basename(path)
        if errs:
            bad_total += 1
            print(f"❌ {name}：点 {len(topics)} · 题 {len(questions)} · 不合格 {len(errs)}")
            for e in errs[:25]:
                print("   -", e)
            if len(errs) > 25:
                print(f"   … 其余 {len(errs) - 25} 条略")
        else:
            print(f"✅ {name}：点 {len(topics)} · 题 {len(questions)} · 不合格 0")
            for w in warn[:6]:
                print("   ~", w)
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())
