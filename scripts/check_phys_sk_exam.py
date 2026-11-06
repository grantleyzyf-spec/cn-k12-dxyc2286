#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中地理（physics-sk）单卷自检器。

用法：
  python3 scripts/check_phys_sk_exam.py data/physics-sk/exams/七年级上册/xxx.json
  python3 scripts/check_phys_sk_exam.py --book 七年级上册
  python3 scripts/check_phys_sk_exam.py --all

检查项（任一不过 exit 1）：
 1 结构：book/kind/term/grade/stage/paper/duration/fullScore/scope/sections/examId 齐全
 2 学段口径：初中 120 分 120 分钟；题数 20–26
 3 分值：每段 items 的 score 合计 = 该段 rule 里的分值；全卷合计 = fullScore
 4 题号：全卷连续 1..N
 5 知识点：每题 topicIds 非空且都是**本册**点；单元卷必须覆盖 scope 下全部课时点各 ≥1 次
   （scope 匹配：`chapter == sc` 或 `chapter.startswith(sc + " · ")`——课时点的 chapter 在单元串后面
     还带「 · 第N课时 … 」，等值比较只会命中单元点，覆盖审计当场变假齐）
 6 质量：stem ≥12 字；analysis ≥20 汉字；choice 四选项 label A–D、文本互异、answer ∈ label；
   short-answer/solve 必须有 scoreRule 且各步之和 = 该题分；fill/numeric 答案非空
 7 原创性：与题库 data/physics-sk/questions.json 题干相似度 <0.85
 8 答案位：A–D 各 ≥15%
 9 卷名：单元卷 paper 以「主题X <主题名> 测试卷」结尾且与 scope[0] 逐字一致
"""
import difflib
import glob
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
SPEC = {"初中": (120, 120, 20, 26)}
KIND_OK = {"unit", "mid", "fin"}
HAN = re.compile(r"[\u4e00-\u9fa5]")
errs = []


def E(m):
    errs.append(m)


def norm(s):
    return re.sub(r"\s+", "", s or "")


def check(path):
    errs.clear()
    d = json.load(open(path, encoding="utf-8"))
    for k in ("book", "kind", "term", "grade", "stage", "paper", "duration", "fullScore", "scope", "sections", "examId"):
        if k not in d:
            E(f"缺字段 {k}")
    if errs:
        return
    if d["kind"] not in KIND_OK:
        E(f"kind 非法 {d['kind']}")
    stage = d.get("stage") or "初中"
    if stage not in SPEC:
        E(f"stage 非法 {stage}")
        return
    full, dur, nmin, nmax = SPEC[stage]
    if d["fullScore"] != full:
        E(f"满分 {d['fullScore']} ≠ {full}")
    if d["duration"] != dur:
        E(f"时长 {d['duration']} ≠ {dur}")

    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    T = {t["id"]: t for t in topics}
    bank = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
    book = d["book"]
    book_ids = {t["id"] for t in topics if t["chapter"].split(" ")[0] == book}
    scope = d.get("scope") or []
    if not scope:
        E("scope 为空")

    # 覆盖：scope 下全部课时点
    def cover(ids):
        return {t["id"] for t in topics
                if any(t["chapter"] == sc or t["chapter"].startswith(sc + " · ") for sc in ids)}

    nos, total, ans, used_tids = [], 0, [], set()
    for si, sec in enumerate(d.get("sections") or [], start=1):
        items = sec.get("items") or []
        ssum = sum(it.get("score") or 0 for it in items)
        rule = sec.get("rule") or ""
        nums = [int(x) for x in re.findall(r"\d+", rule)]
        if nums and ssum != nums[-1] and ssum not in nums:
            E(f"第{si}段分值和 {ssum} 与 rule「{rule}」不符")
        total += ssum
        for it in items:
            no = it.get("no")
            nos.append(no)
            stem = it.get("stem") or ""
            if not it.get("itemId"):
                E(f"第{no}题缺 itemId")
            if len(stem) < 12:
                E(f"第{no}题题干不足 12 字")
            if len(HAN.findall(it.get("analysis") or "")) < 20:
                E(f"第{no}题解析不足 20 汉字")
            tids = it.get("topicIds") or []
            used_tids.update(tids)
            if not tids:
                E(f"第{no}题缺 topicIds")
            for tid in tids:
                if tid not in T:
                    E(f"第{no}题 topicId {tid} 不存在")
                elif tid not in book_ids:
                    E(f"第{no}题 topicId {tid} 不属本册")
            tp = it.get("type")
            if tp == "choice":
                opts = it.get("options") or []
                labels = [o.get("label") for o in opts]
                if len(opts) != 4 or labels != ["A", "B", "C", "D"]:
                    E(f"第{no}题选择题须 4 选项且 label A–D")
                texts = [o.get("text", "") for o in opts]
                if len(set(texts)) != len(texts):
                    E(f"第{no}题选项文本重复")
                if it.get("answer") not in labels:
                    E(f"第{no}题 answer 不在选项内")
                if any(x in t for t in texts for x in ("以上都不对", "以上都对", "无法确定")):
                    E(f"第{no}题出现凑数选项")
                ans.append(it.get("answer"))
            elif tp in ("short", "short-answer", "solve"):
                sr = it.get("scoreRule") or []
                if not sr:
                    E(f"第{no}题（{tp}）缺 scoreRule")
                else:
                    tot = 0
                    for x in sr:
                        if isinstance(x, dict):
                            tot += int(x.get("score") or 0)
                        else:
                            m = re.findall(r"(\d+)\s*分", str(x))
                            tot += int(m[-1]) if m else 0
                    if tot != (it.get("score") or 0):
                        E(f"第{no}题 scoreRule 合计 {tot} ≠ 题分 {it.get('score')}")
            elif tp in ("fill", "numeric"):
                if not str(it.get("answer") or "").strip():
                    E(f"第{no}题缺答案")
            # 原创性
            for q in bank:
                r = difflib.SequenceMatcher(None, norm(stem), norm(q.get("prompt"))).ratio()
                if r >= 0.85:
                    E(f"第{no}题 与题库 {q['id']} 雷同 {r:.2f}")
                    break

    if nos != list(range(1, len(nos) + 1)):
        E(f"题号不连续 {nos[:12]}")
    if not (nmin <= len(nos) <= nmax):
        E(f"题数 {len(nos)} 不在 {nmin}–{nmax}")
    if total != full:
        E(f"分值和 {total} ≠ 满分 {full}")

    if d["kind"] == "unit":
        need = cover(scope)
        miss = need - used_tids
        if miss:
            E(f"单元卷未覆盖 {len(miss)} 个课时点：{sorted(miss)[:5]}")
        # 卷名判据：去空白后比，允许「…认识地球 测试卷」与「…认识地球测试卷」两种写法
        _pape = re.sub(r"\s+", "", d["paper"])
        _scop = re.sub(r"\s+", "", scope[0]) if scope else ""
        if scope and not _pape.rstrip("测试卷").endswith(_scop):
            E(f"卷名应与 scope[0]「{scope[0]}」一致（现「{d['paper']}」）")
    # 期中卷 scope 必须是本册正式单元的**连续前缀**：中文序数按字符排是「一<三<二<五<四」，
    # 生成器若按字符串排序，scope 会变成「第一章＋第三章」，整册第二章一道没考，而覆盖率审计只审
    # 单元卷 ⇒ 静默放行。锚点：章号解析后必须是 1..len(scope) 的连续序列。
    if d["kind"] == "mid":
        _CN = {c: i for i, c in enumerate("一二三四五六七八九十", 1)}

        def _no(ch):
            m = re.search(r"第([一二三四五六七八九十\d]+)章", ch)
            if not m:
                return None
            v = m.group(1)
            return int(v) if v.isdigit() else _CN.get(v)

        book_units = sorted(
            [(t["chapter"], _no(t["chapter"])) for t in topics
             if t["level"] == "unit" and t["chapter"].split(" ")[0] == book
             and "绪论" not in t["chapter"]],
            key=lambda x: (x[1] is None, x[1]))
        order = {ch: i for i, (ch, _) in enumerate(book_units)}
        idx = [order.get(sc) for sc in scope]
        if any(i is None for i in idx):
            E(f"期中卷 scope 含非本册正式单元：{[sc for sc, i in zip(scope, idx) if i is None]}")
        elif sorted(idx) != list(range(len(idx))):
            want = [ch for ch, _ in book_units[: len(scope)]]
            E(f"期中卷 scope 应为本册前 {len(scope)} 个单元（{want}），现为 {scope}")

    if ans:
        c = Counter(ans)
        dist = {k: round(c.get(k, 0) / len(ans) * 100, 1) for k in "ABCD"}
        thin = {k: v for k, v in dist.items() if v < 15}
        if thin:
            E(f"答案位偏低 {thin}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "--all":
        files = sorted(glob.glob(os.path.join(D, "exams", "*", "*.json")))
    elif args[0] == "--book":
        files = sorted(glob.glob(os.path.join(D, "exams", args[1], "*.json")))
    else:
        files = [args[0]]
    bad = 0
    for p in files:
        if not os.path.exists(p):
            print(f"❌ 缺件 {p}")
            bad += 1
            continue
        check(p)
        head = json.load(open(p, encoding="utf-8"))
        tag = f"{head.get('book')} / {head.get('paper')}（{head.get('kind')}）"
        if errs:
            bad += 1
            print(f"❌ {tag}：{len(errs)} 条")
            for e in errs[:10]:
                print("  ERR", e)
            print("RESULT: FAIL")
        else:
            n = sum(len(s.get("items") or []) for s in head.get("sections") or [])
            print(f"== {tag}: 题 {n} 分 {head.get('fullScore')}")
            print("RESULT: PASS")
    if len(files) > 1:
        print(f"\n共 {len(files)} 卷 · 不合格 {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
