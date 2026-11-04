#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）化学（chemistry-hujiao）题库分片检查器。

用法：python3 scripts/check_geo_ztu_bank.py data/chemistry-hujiao/_bank/T01.json
     python3 scripts/check_geo_ztu_bank.py --all          # 逐片跑，末尾给总表

口径与全库门禁一致（字段名照 data/geography/questions.json 实测）：
  id / topicId / prompt / question / answer / type / difficulty / explanation / options / choices
  · question 必须与 prompt 完全相同（前端两处读不同字段）
  · choice：4 选项、label 恰为 A–D、文本互异、answer ∈ label、choices == options、禁凑数项
  · fill：题干含 ____ 或 ＿＿、answer 非空、options 为空
  · numeric：answer 非空、verify 只含数字与 + - * / ** ( ) 且复算等于 answer
  · short-answer：answer ≥15 汉字且含「；」分条
  · 题干 ≥12 字、解析 ≥25 汉字、禁 Markdown、片内题干不重复
"""
import glob
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-hujiao")
SPEC = os.path.join(D, "_bank_spec")

HAN = re.compile(r"[\u4e00-\u9fa5]")
MD = re.compile(r"\*\*|##|\$|\\frac|\btable\b")


def han(s):
    return len(HAN.findall(s or ""))


def check_one(path):
    errs = []
    d = json.load(open(path, encoding="utf-8"))
    spec_path = os.path.join(SPEC, f"{d.get('shard', '')}.json")
    if not os.path.exists(spec_path):
        return [f"找不到分片规格 {spec_path}"], 0, 0
    spec = json.load(open(spec_path, encoding="utf-8"))
    want = {}
    for it in spec["items"]:
        for s in it["slots"]:
            want[s["id"]] = (it["topicId"], s["type"], s["difficulty"], s.get("label"))
    qs = d.get("questions") or []
    got = {q.get("id") for q in qs}
    if set(want) - got:
        errs.append(f"缺槽 {sorted(set(want) - got)[:5]}")
    if got - set(want):
        errs.append(f"多出未授权 id {sorted(got - set(want))[:5]}")

    for q in qs:
        qid = q.get("id")
        if qid not in want:
            continue
        tid, tp, diff, lab = want[qid]
        if q.get("topicId") != tid:
            errs.append(f"{qid} topicId 应为 {tid}")
        if q.get("type") != tp:
            errs.append(f"{qid} type 应为 {tp}（现 {q.get('type')}）")
        if q.get("difficulty") != diff:
            errs.append(f"{qid} difficulty 应为 {diff}")
        stem = q.get("prompt") or ""
        if q.get("question") != stem:
            errs.append(f"{qid} question 应与 prompt 相同")
        if len(stem) < 12:
            errs.append(f"{qid} 题干不足 12 字")
        if han(q.get("explanation")) < 25:
            errs.append(f"{qid} 解析不足 25 汉字")
        if MD.search(stem) or MD.search(q.get("explanation") or ""):
            errs.append(f"{qid} 含 Markdown/LaTeX")
        if tp == "choice":
            opts = q.get("options") or []
            labels = [o.get("label") for o in opts]
            if len(opts) != 4 or labels != ["A", "B", "C", "D"]:
                errs.append(f"{qid} 选择题须 4 选项且 label 为 A–D（现 {labels}）")
            texts = [o.get("text", "") for o in opts]
            if len(set(texts)) != len(texts):
                errs.append(f"{qid} 选项文本重复")
            if q.get("answer") not in labels:
                errs.append(f"{qid} answer 不在选项内")
            if lab and q.get("answer") != lab:
                errs.append(f"{qid} 答案位应为预分配的 {lab}（现 {q.get('answer')}）")
            if q.get("choices") != opts:
                errs.append(f"{qid} choices 与 options 不一致")
            if any(x in t for t in texts for x in ("以上都不对", "以上都对", "以上都可以", "仅在大学学习")):
                errs.append(f"{qid} 出现凑数选项")
        elif tp == "fill":
            if "____" not in stem and "＿＿" not in stem:
                errs.append(f"{qid} 填空题干缺 ____")
            if not str(q.get("answer") or "").strip():
                errs.append(f"{qid} 缺答案")
            if q.get("options"):
                errs.append(f"{qid} 非选择题 options 应为空")
        elif tp == "numeric":
            if not str(q.get("answer") or "").strip():
                errs.append(f"{qid} 缺答案")
            v = q.get("verify")
            try:
                if abs(eval(str(v), {"__builtins__": {}}, {}) - float(q["answer"])) > 1e-6:
                    errs.append(f"{qid} verify 复算与 answer 不等")
            except Exception as e:                                  # noqa: BLE001
                errs.append(f"{qid} verify 无法复算（{e}）")
            if re.search(r"[^0-9+\-*/(). ]", str(v or "")):
                errs.append(f"{qid} verify 只能含数字与 + - * / ** ( )")
        elif tp == "short-answer":
            ans = str(q.get("answer") or "")
            if han(ans) < 15:
                errs.append(f"{qid} 简答答案过短")
            if "；" not in ans:
                errs.append(f"{qid} 简答应为 2–3 条要点（用；分隔）")

    seen = {}
    for q in qs:
        k = re.sub(r"\s+", "", q.get("prompt") or "")
        if k in seen:
            errs.append(f"题干重复：{seen[k]} / {q.get('id')}")
        seen[k] = q.get("id")

    ch = [q for q in qs if q.get("type") == "choice"]
    warn = ""
    if ch:
        c = Counter(q.get("answer") for q in ch)
        thin = {k: round(c.get(k, 0) / len(ch) * 100, 1) for k in "ABCD" if c.get(k, 0) / len(ch) < 0.15}
        if thin:
            warn = f"WARN 答案位偏低 {thin}"
    return errs, len(qs), len({q.get("topicId") for q in qs}), warn


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    targets = (sorted(glob.glob(os.path.join(D, "_bank", "T*.json")))
               if sys.argv[1] == "--all" else [sys.argv[1]])
    bad = 0
    total_q = 0
    for p in targets:
        if not os.path.exists(p):
            print(f"❌ 缺件 {p}")
            bad += 1
            continue
        r = check_one(p)
        errs, nq, npt = r[0], r[1], r[2]
        total_q += nq
        if errs:
            bad += 1
            print(f"❌ {os.path.basename(p)}：{len(errs)} 条")
            for e in errs[:20]:
                print("  -", e)
            print("RESULT: FAIL")
        else:
            print(f"✅ {os.path.basename(p)}：{nq} 题 / 点 {npt}" + (f"  {r[3]}" if r[3] else ""))
            print("RESULT: PASS")
    if sys.argv[1] == "--all":
        print(f"\n共 {len(targets)} 片 · 题 {total_q} · 不合格片 {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
