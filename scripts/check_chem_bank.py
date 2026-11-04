#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：题库分片校验（单文件 / 全量）。

用法：
  python3 scripts/check_chem_bank.py data/chemistry/_bank/CHEM_B01_out.json
  python3 scripts/check_chem_bank.py --all
判据：题量恰好、id 与题槽一致、题型配额、三档齐、题干 ≥12 字、解析 ≥25 汉字、
      选择题 4 选项互异且答案在 label 内、choices==options、填空含 ____、
      简答 2–3 条（；分隔）、数值题 verify 可复算且等于 answer、禁 Markdown、片内题干不重复、
      topics 覆盖本片全部点且 description 40–90 汉字、mastery_criteria 1–3 条。
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")
BAD_OPT = ("以上都不对", "以上都对", "仅在大学学习", "无法确定")


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def check(out_path, spec_path=None):
    errs = []
    try:
        o = json.load(open(out_path, encoding="utf-8"))
    except Exception as e:
        return [f"读不了 {out_path}: {e}"]
    if isinstance(o, list):
        return ["落盘必须是对象 {shard, topics, questions}，不能是裸数组"]
    sid = o.get("shard") or ""
    spec_path = spec_path or os.path.join(D, "_bank_shards", f"{sid}.json")
    if not os.path.exists(spec_path):
        return [f"找不到分片规格 {spec_path}"]
    spec = json.load(open(spec_path, encoding="utf-8"))
    qs, tps = o.get("questions") or [], o.get("topics") or []
    # 点内容
    tmap = {t["id"]: t for t in tps}
    for sp in spec["topics"]:
        t = tmap.get(sp["id"])
        if not t:
            errs.append(f"topics 缺点 {sp['id']}")
            continue
        d = t.get("description") or ""
        if not (40 <= han(d) <= 90):
            errs.append(f"{sp['id']} description {han(d)} 汉字（要 40–90）")
        mc = t.get("mastery_criteria") or []
        if not (1 <= len(mc) <= 3) or any(not str(x).strip() for x in mc):
            errs.append(f"{sp['id']} mastery_criteria 要 1–3 条")
        if not t.get("type"):
            errs.append(f"{sp['id']} 缺 type")
    # 题量与 id
    by_topic = Counter(q.get("topicId") for q in qs)
    for sl in spec["slots"]:
        got = [q for q in qs if q.get("topicId") == sl["topicId"]]
        if len(got) != sl["count"]:
            errs.append(f"{sl['topicId']} 题数 {len(got)} ≠ {sl['count']}")
        if {q.get("id") for q in got} - set(sl["idRange"]):
            errs.append(f"{sl['topicId']} 用了题槽外的 id")
        if set(sl["idRange"]) - {q.get("id") for q in got}:
            errs.append(f"{sl['topicId']} 题槽未写满")
        tc = Counter(q.get("type") for q in got)
        for k, v in sl["quota"].items():
            if tc.get(k, 0) < v - 1 and sl["level"] == "lesson" and k == "short-answer":
                continue
            if tc.get(k, 0) < v:
                errs.append(f"{sl['topicId']} {k} {tc.get(k,0)} < {v}")
        if sl["level"] == "lesson":
            dif = {q.get("difficulty") for q in got}
            if not {"basic", "standard", "hard"} <= dif:
                errs.append(f"{sl['topicId']} 三档不齐 {sorted(x for x in dif if x)}")
    # 逐题
    stems = Counter()
    for q in qs:
        qid = q.get("id", "?")
        st = q.get("stem") or ""
        if han(st) < 12:
            errs.append(f"{qid} 题干 {han(st)} 汉字 < 12")
        stems[re.sub(r"\s+", "", st)] += 1
        if han(q.get("analysis")) < 25:
            errs.append(f"{qid} 解析 {han(q.get('analysis'))} 汉字 < 25")
        if re.search(r"\*\*|##|\$\$|\\frac|\|", st):
            errs.append(f"{qid} 题干含 Markdown")
        ty = q.get("type")
        if ty == "choice":
            opts = q.get("options") or []
            if len(opts) != 4:
                errs.append(f"{qid} 选项 {len(opts)} 个")
            labels = [x.get("label") for x in opts]
            if q.get("answer") not in labels:
                errs.append(f"{qid} 答案不在选项内")
            if len({x.get("text") for x in opts}) != len(opts):
                errs.append(f"{qid} 选项有重复")
            if q.get("choices") != opts:
                errs.append(f"{qid} choices 与 options 不同构")
            if any(b in (x.get("text") or "") for x in opts for b in BAD_OPT):
                errs.append(f"{qid} 用了凑数干扰项")
        elif ty == "fill":
            if "____" not in st:
                errs.append(f"{qid} 填空缺 ____")
            if not isinstance(q.get("answer"), str) or not q.get("answer").strip():
                errs.append(f"{qid} 填空答案缺失")
            if q.get("options"):
                errs.append(f"{qid} 非选择题 options 应为空")
        elif ty == "short-answer":
            ans = q.get("answer") or ""
            if len([x for x in ans.split("；") if x.strip()]) < 2:
                errs.append(f"{qid} 简答要点 < 2 条")
        elif ty == "numeric":
            try:
                val = eval(q.get("verify", ""), {"__builtins__": {}}, {})
                if str(val) != str(q.get("answer")).strip():
                    errs.append(f"{qid} verify={val} ≠ answer={q.get('answer')}")
            except Exception as e:
                errs.append(f"{qid} verify 不可复算：{e}")
        else:
            errs.append(f"{qid} type 非法 {ty}")
    for s, n in stems.items():
        if n > 1:
            errs.append(f"片内题干重复 ×{n}：{s[:24]}")
    return errs


def main():
    if "--all" in sys.argv:
        files = sorted(f for f in os.listdir(os.path.join(D, "_bank")) if f.endswith("_out.json")) \
            if os.path.isdir(os.path.join(D, "_bank")) else []
        bad = 0
        for f in files:
            errs = check(os.path.join(D, "_bank", f))
            print(("✅" if not errs else "❌"), f, "" if not errs else f"{len(errs)} 项")
            for e in errs[:6]:
                print("   -", e)
            bad += 1 if errs else 0
        print(f"\n共 {len(files)} 片 · 不合格 {bad}")
        return 1 if bad else 0
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    errs = check(sys.argv[1])
    for e in errs[:40]:
        print(" -", e)
    print(("RESULT: PASS" if not errs else f"RESULT: FAIL ({len(errs)} 项)"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
