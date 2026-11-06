#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鲁科版高中物理（physics-luke）单卷自检器。只读，不写仓库。

用法：
    python3 scripts/check_geo_xiangjiao_exam.py data/physics-luke/exams/九年级上册/第1单元 走进化学世界 测试卷.json
    python3 scripts/check_geo_xiangjiao_exam.py --book 九年级上册          # 只核某册
    python3 scripts/check_geo_xiangjiao_exam.py --all                      # 全库

检查项（任一不过即 exit 1）：
 1 结构：book/kind/term/grade/stage/paper/duration/fullScore/scope/sections/examId 齐全
 2 学段口径：初中 120 分 120 分钟 / 高中 150 分 150 分钟；题数 20–26（初中）/18–24（高中）
 3 分值：各段 items 的 score 之和 = rule 里写的分值；全卷合计 = fullScore
 4 题号：全卷连续 1..N，无跳号重号
 5 知识点：每题 topicIds 非空且都是**本册**点；**单元卷必须覆盖本章全部点各 ≥1 次**
 6 题目质量：stem ≥12 字；analysis ≥20 汉字；choice 四选项、label A–D、文本互异、answer ∈ labels；
   short/solve 必须有 scoreRule 且各步之和 = 该题分；fill/numeric 答案非空
 7 原创性：与题库 data/physics-luke/questions.json 题干相似度 <0.85
 8 答案位：A–D 各 ≥15%（防「一律选 B」套利）
 9 章名口径：unit 卷 paper 必须以「第N单元/第N章 <章名> 测试卷」结尾，且与 scope[0] 逐字一致
"""
import difflib
import glob
import json
import os
import re
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "physics-luke")
SPEC = {"初中": (120, 120, 20, 26), "高中": (150, 150, 18, 24)}
KIND_OK = {"unit", "mid", "fin", "midterm", "final"}
errs = []


def E(m):
    errs.append(m)


def hanzi(s):
    return re.findall(r"[\u4e00-\u9fa5]", s or "")


def qnorm(s):
    return re.sub(r"\s+", "", s or "")


def book_of(chapter):
    return re.split(r"\s*第[一二三四五六七八九十\d]+(?:章|单元)", chapter or "")[0].strip()


def chap_name(chapter):
    """章名（去册次前缀）：'七年级上册 第一章 地球和地图' → '第一章 地球和地图'"""
    m = re.search(r"第[一二三四五六七八九十\d]+(?:章|单元).*$", chapter or "")
    return (m.group(0) if m else (chapter or "")).strip()


def book_pts_of(topics, book):
    return {t["id"]: t for t in topics if book_of(t.get("chapter")) == book}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    if args[0] == "--book":
        files = sorted(glob.glob(os.path.join(D, "exams", args[1], "*.json")))
    elif args[0] == "--all":
        files = sorted(glob.glob(os.path.join(D, "exams", "*", "*.json")))
    else:
        files = [args[0]]
    if not files:
        print("没有匹配到试卷文件")
        return 1
    bank = [qnorm(q.get("stem") or q.get("prompt") or q.get("question")) for q in
            json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))]
    idx = {}
    for bi, b in enumerate(bank):
        for i in range(len(b) - 3):
            idx.setdefault(b[i:i + 3], set()).add(bi)
    bad = 0
    for path in files:
        try:
            if check_one(path, topics, bank, idx):
                bad += 1
        except Exception as e:
            print(f"\n❌ {os.path.basename(path)}：检查器异常 {type(e).__name__}: {e}")
            bad += 1
    print(f"\n共 {len(files)} 卷 · 不合格 {bad}")
    return 1 if bad else 0


def check_one(path, topics, bank, idx):
    errs.clear()
    d = json.load(open(path, encoding="utf-8"))
    paper = os.path.basename(path)[:-5]
    for k in ("book", "kind", "term", "grade", "stage", "paper", "duration",
              "fullScore", "scope", "sections", "examId"):
        if k not in d:
            E(f"缺字段 {k}")
    if errs:
        return report(path)
    if d["paper"] != paper:
        E(f"paper「{d['paper']}」与文件名「{paper}」不一致")
    if d["kind"] not in KIND_OK:
        E(f"kind「{d['kind']}」非法（unit/mid/fin）")
    stage = d.get("stage")
    if stage not in SPEC:
        E(f"stage「{stage}」非法（初中/高中）")
        return report(path)
    dur, full, lo, hi = SPEC[stage]
    if d["duration"] != dur:
        E(f"{stage} 时长应为 {dur} 分钟，现 {d['duration']}")
    if d["fullScore"] != full:
        E(f"{stage} 满分应为 {full}，现 {d['fullScore']}")
    if not isinstance(d["scope"], list) or not d["scope"]:
        E("scope 必须是非空数组（覆盖的教材章标题）")

    book_pts = book_pts_of(topics, d["book"])
    if not book_pts:
        E(f"本册「{d['book']}」在 topics.json 里没有知识点")

    total, nos, n_choice, covered = 0, [], 0, set()
    for sec in d["sections"]:
        for k in ("title", "rule", "items"):
            if k not in sec:
                E(f"sections 缺 {k}")
        ssum = sum(it.get("score", 0) for it in sec.get("items") or [])
        nums = [int(x) for x in re.findall(r"\d+", sec.get("rule", ""))]
        if nums and nums[-1] != ssum:
            E(f"「{sec.get('title')}」rule 写 {nums[-1]} 分，实际 items 合计 {ssum} 分")
        for it in sec.get("items") or []:
            total += it.get("score", 0)
            nos.append(it.get("no"))
            no, tp = it.get("no"), it.get("type")
            stem = it.get("stem") or ""
            if len(stem) < 12:
                E(f"第 {no} 题题干不足 12 字（{len(stem)}）")
            if len(hanzi(it.get("analysis"))) < 20:
                E(f"第 {no} 题解析不足 20 汉字")
            tids = it.get("topicIds") or []
            if any(isinstance(x, list) for x in tids):
                E(f"第 {no} 题 topicIds 嵌套数组：{tids}")
                tids = [y for x in tids for y in (x if isinstance(x, list) else [x])]
            if not tids:
                E(f"第 {no} 题缺 topicIds")
            for tid in tids:
                if tid not in book_pts:
                    E(f"第 {no} 题 topicId {tid} 不是本册知识点")
                covered.add(tid)
            if tp == "choice":
                n_choice += 1
                opts = it.get("options") or []
                if len(opts) != 4:
                    E(f"第 {no} 题选择题须 4 个选项（现 {len(opts)}）")
                labels = [o.get("label") for o in opts]
                texts = [(o.get("text") or "").strip() for o in opts]
                if labels != ["A", "B", "C", "D"]:
                    E(f"第 {no} 题选项 label 应为 A–D，现 {labels}")
                if len(set(texts)) != len(texts):
                    E(f"第 {no} 题选项文本有重复")
                if it.get("answer") not in labels:
                    E(f"第 {no} 题 answer 不在选项 label 内")
                if any(x in t for t in texts for x in ("以上都不对", "以上都对", "以上都可以")):
                    E(f"第 {no} 题出现「以上都不对」类凑数选项")
            elif tp in ("short", "solve", "writing"):
                sr = it.get("scoreRule") or []
                if not sr:
                    E(f"第 {no} 题（{tp}）缺 scoreRule")
                else:
                    s = 0
                    for line in sr:
                        m = re.search(r"(\d+)\s*分", line)
                        s += int(m.group(1)) if m else 0
                    if s != it.get("score", 0):
                        E(f"第 {no} 题 scoreRule 合计 {s} 分 ≠ 题目分值 {it.get('score')}")
                if not str(it.get("answer") or "").strip():
                    E(f"第 {no} 题缺参考答案")
            elif tp in ("fill", "numeric"):
                if not str(it.get("answer", "")).strip():
                    E(f"第 {no} 题缺答案")
            else:
                E(f"第 {no} 题 type「{tp}」非法（choice/fill/short/solve/writing/numeric）")
            s = qnorm(stem)
            cand = set()
            for i in range(len(s) - 3):
                cand |= idx.get(s[i:i + 3], set())
            hi_sim = 0.0
            for bi in cand:
                b = bank[bi]
                if 2 * min(len(s), len(b)) / max(len(s) + len(b), 1) <= 0.85:
                    continue
                hi_sim = max(hi_sim, difflib.SequenceMatcher(None, s, b).ratio())
            if hi_sim >= 0.85:
                E(f"第 {no} 题与题库相似度 {hi_sim:.2f} ≥0.85（卷面须原创）")

    # 单元卷：必须覆盖本章全部点；卷名与 scope 章名一致
    if d["kind"] == "unit":
        scope0 = d["scope"][0]
        want = chap_name(scope0)
        if not d["paper"].startswith(want):
            E(f"单元卷卷名应以「{want}」开头，现「{d['paper']}」")
        same = {tid for tid, t in book_pts.items()
                if t["chapter"] == scope0 or t["chapter"].startswith(scope0 + " · ")}
        if not same:
            E(f"本册没有章「{want}」的知识点（scope 写错册次/章名）")
        miss = sorted(same - covered)
        if miss:
            names = [book_pts[m].get("name") for m in miss[:4]]
            E(f"单元卷未覆盖本章 {len(miss)} 个点（例：{names}）")

    if nos != list(range(1, len(nos) + 1)):
        E(f"题号不连续：{nos[:8]}…（应 1..{len(nos)}）")
    if total != full:
        E(f"全卷分值合计 {total} ≠ fullScore {full}")
    if not (lo <= len(nos) <= hi):
        E(f"题数 {len(nos)} 不在 {lo}–{hi} 之间")
    if n_choice < 6:
        E(f"选择题只有 {n_choice} 道（应 ≥6）")
    chs = [it for sec in d["sections"] for it in sec.get("items") or [] if it.get("type") == "choice"]
    if n_choice:
        raw = Counter(it.get("answer") for it in chs)
        labels = ("A", "B", "C", "D")
        dist = {k: raw.get(k, 0) for k in labels}
        thin = {k: round(v / n_choice * 100, 1) for k, v in dist.items() if v / n_choice < 0.15}
        if thin:
            E(f"答案位偏斜：{thin} 低于 15%")
    print(f"卷：{d['book']} · {paper} · {stage} · {len(d['sections'])} 大题 / {len(nos)} 题 / {total} 分 / "
          f"{d['duration']} 分钟 · 选择 {n_choice} · 覆盖 {len(covered)}/{len(book_pts)} 点")
    return report(path)


def report(path):
    if errs:
        print(f"\n❌ {os.path.basename(path)}：{len(errs)} 条问题")
        for e in errs[:25]:
            print("  -", e)
        if len(errs) > 25:
            print(f"  …另有 {len(errs)-25} 条")
        return 1
    print("  ✅ PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
