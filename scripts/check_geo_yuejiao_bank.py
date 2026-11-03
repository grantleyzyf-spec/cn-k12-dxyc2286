#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""粤教粤人版地理题库分片检查器。

用法：python3 scripts/check_geo_yuejiao_bank.py data/geography-yuejiao/_bank/GYJ_B01.json
"""
import json
import os
import re
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-yuejiao")
SHARDS = os.path.join(D, "_bank_shards")

BAN = ["首先", "其次", "综上所述", "总而言之", "由此可见", "赋能", "抓手", "闭环", "值得注意的是"]


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    d = json.load(open(path, encoding="utf-8"))
    spec_path = os.path.join(SHARDS, f"{d.get('shard')}.json")
    if not os.path.exists(spec_path):
        print(f"ERR 找不到分片规格 {spec_path}")
        return 1
    spec = json.load(open(spec_path, encoding="utf-8"))
    want = {}
    meta = {}
    for it in spec["items"]:
        meta[it["topicId"]] = it
        for s in it["slots"]:
            want[s["id"]] = (it["topicId"], s["type"], s["difficulty"])
    qs = d.get("questions") or []
    errs = []
    got = {q.get("id") for q in qs}
    if set(want) - got:
        errs.append(f"缺槽 {sorted(set(want)-got)[:5]}")
    if got - set(want):
        errs.append(f"多出未授权 id {sorted(got-set(want))[:5]}")
    # —— 点位内容（items）——
    items = {it.get("topicId"): it for it in (d.get("items") or [])}
    if set(meta) - set(items):
        errs.append(f"items 缺点位 {sorted(set(meta)-set(items))[:5]}")
    for tid, m in meta.items():
        it = items.get(tid) or {}
        if han(it.get("description")) < 25:
            errs.append(f"{tid} description 不足 25 汉字")
        if len(it.get("mastery_criteria") or []) < 2:
            errs.append(f"{tid} mastery_criteria 不足 2 条")
        if not (it.get("diagnostic_question") or {}).get("question"):
            errs.append(f"{tid} 缺 diagnostic_question")
        if it.get("name") and it["name"] != m["name"]:
            errs.append(f"{tid} name 与骨架不一致")
    for q in qs:
        qid = q.get("id")
        if qid not in want:
            continue
        tids, tp, diff = want[qid]
        if q.get("topicId") != tids:
            errs.append(f"{qid} topicId 应为 {tids}")
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
        if re.search(r"\*\*|##|\|", stem):
            errs.append(f"{qid} 题干含 Markdown")
        if tp == "choice":
            opts = q.get("options") or []
            if len(opts) != 4:
                errs.append(f"{qid} 选择题须 4 选项")
            labels = [o.get("label") for o in opts]
            if labels != ["A", "B", "C", "D"]:
                errs.append(f"{qid} label 应为 A–D")
            texts = [o.get("text", "") for o in opts]
            if len(set(texts)) != len(texts):
                errs.append(f"{qid} 选项文本重复")
            if q.get("answer") not in labels:
                errs.append(f"{qid} answer 不在选项内")
            if q.get("choices") != opts:
                errs.append(f"{qid} choices 与 options 不一致")
            if any(x in t for t in texts for x in ("以上都不对", "以上都对", "以上都可以", "无法确定")):
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
            except Exception as e:
                errs.append(f"{qid} verify 无法复算（{e}）")
            if re.search(r"[^0-9+\-*/(). ]", str(v or "")):
                errs.append(f"{qid} verify 只能含数字与 + - * / ** ( )")
        elif tp == "short-answer":
            ans = str(q.get("answer") or "")
            if han(ans) < 15:
                errs.append(f"{qid} 简答答案过短")
            if "；" not in ans:
                errs.append(f"{qid} 简答应为 2–3 条要点（用；分隔）")
        for b in BAN:
            if b in (q.get("explanation") or "") or b in stem:
                errs.append(f"{qid} 禁用套话「{b}」")
    seen = {}
    for q in qs:
        k = re.sub(r"\s+", "", q.get("prompt") or "")
        if k in seen:
            errs.append(f"题干重复：{seen[k]} / {q.get('id')}")
        seen[k] = q.get("id")
    ch = [q for q in qs if q.get("type") == "choice"]
    if ch:
        c = Counter(q.get("answer") for q in ch)
        thin = {k: round(c.get(k, 0) / len(ch) * 100, 1) for k in "ABCD" if c.get(k, 0) / len(ch) < 0.15}
        if thin:
            print(f"WARN 答案位偏低 {thin}")
    if errs:
        print(f"❌ {os.path.basename(path)}：{len(errs)} 条")
        for e in errs[:20]:
            print("  -", e)
        print("RESULT: FAIL")
        return 1
    print(f"✅ {os.path.basename(path)}：{len(qs)} 题 / 点 {len({q['topicId'] for q in qs})}")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
