#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）地理：知识点内容分片检查器（_points/TNN.json）。

用法：python3 scripts/check_geo_ztu_points.py data/geography-zhongtu-cz/_points/T01.json

判据（与 test_geo_ztu.py 同口径）：
- 点数与 id 集合必须与 _bank_spec/TNN.json 的 items 完全一致（9 点：8 课时 ＋ 1 单元）
- 每点：name 非空且与 spec 一致；type ∈ {conceptual, procedural, reasoning, modeling, application}
- description 汉字 40–120；mastery_criteria 2–3 条（每条 ≥8 汉字、互不重复）
- diagnostic_question：question ≥10 字、answer 非空
- 禁 Markdown（** ## | $ 反斜杠）、禁元话语（扫描件/OCR/抽取/切片/文字层/残片）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")
SPEC = os.path.join(D, "_bank_spec")

TYPES = {"conceptual", "procedural", "reasoning", "modeling", "application"}
HAN = re.compile(r"[\u4e00-\u9fa5]")
BAD = re.compile(r"\*\*|##|\||\$|\\")
META = re.compile(r"扫描件|OCR|抽取|切片|文字层|残片|待补|TODO|XXX")


def han(s):
    return len(HAN.findall(s or ""))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    d = json.load(open(path, encoding="utf-8"))
    tag = d.get("shard") or os.path.basename(path)[:-5]
    spec_path = os.path.join(SPEC, f"{tag}.json")
    if not os.path.exists(spec_path):
        print(f"❌ 找不到规格 {spec_path}")
        return 1
    spec = json.load(open(spec_path, encoding="utf-8"))
    need = {it["topicId"]: it for it in spec["items"]}
    pts = d.get("points") or []
    errs = []
    got = {p.get("id") for p in pts}
    if set(need) - got:
        errs.append(f"缺点 {sorted(set(need) - got)[:5]}")
    if got - set(need):
        errs.append(f"多出未授权 id {sorted(got - set(need))[:5]}")
    for p in pts:
        pid = p.get("id")
        if pid not in need:
            continue
        if p.get("name") != need[pid]["name"]:
            errs.append(f"{pid} name 应逐字等于 spec（{need[pid]['name']}）")
        if p.get("type") not in TYPES:
            errs.append(f"{pid} type 非法（{p.get('type')}）")
        desc = p.get("description") or ""
        if not (40 <= han(desc) <= 120):
            errs.append(f"{pid} description 汉字 {han(desc)}（须 40–120）")
        mc = p.get("mastery_criteria") or []
        if not (2 <= len(mc) <= 3):
            errs.append(f"{pid} mastery_criteria {len(mc)} 条（须 2–3）")
        for x in mc:
            if han(x) < 8:
                errs.append(f"{pid} mastery_criteria 条目过短：{x[:12]}")
        if len({re.sub(r'\s+', '', x) for x in mc}) != len(mc):
            errs.append(f"{pid} mastery_criteria 有重复条目")
        dq = p.get("diagnostic_question") or {}
        if len(str(dq.get("question") or "")) < 10:
            errs.append(f"{pid} diagnostic_question.question 不足 10 字")
        if not str(dq.get("answer") or "").strip():
            errs.append(f"{pid} diagnostic_question.answer 为空")
        blob = json.dumps(p, ensure_ascii=False)
        if BAD.search(desc) or BAD.search(" ".join(mc)):
            errs.append(f"{pid} 含 Markdown/LaTeX 字符")
        if META.search(blob):
            errs.append(f"{pid} 含元话语或占位符")
    if errs:
        print(f"❌ {os.path.basename(path)}：{len(errs)} 条")
        for e in errs[:20]:
            print("  -", e)
        print("RESULT: FAIL")
        return 1
    print(f"✅ {os.path.basename(path)}：{len(pts)} 点（{sum(1 for p in pts if need[p['id']]['kind'] == 'unit')} 单元 / "
          f"{sum(1 for p in pts if need[p['id']]['kind'] == 'lesson')} 课时）")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
