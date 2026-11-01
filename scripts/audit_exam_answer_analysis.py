#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卷面「答案与解析自相矛盾」审计：只读，扫各版本桶的整卷。

为什么需要：answer 与 analysis 打架的题能过四道机器闸门（题数/分值/原创性/覆盖率），
只有讲解工位逐题读卷面时才偶尔报出来。实测沪教版抓到 4 处（必修三期中A 题2、
选必二第6章 题4/题8 属「解析算出正确值、answer 却标了错项」）。

判据（只报高置信）：
1. analysis 里出现「选 X」「答案为 X」「故…X」「答案是 X」等结论式表述，且 X ≠ answer；
2. （已废弃）「解析没提 answer 选项文本」这条判据噪声太大：教学解析逐项讲干扰项是常态，
   实测在 math 桶上全是假阳性，故只保留结论式表述这一条高置信判据。

用法：
  python3 scripts/audit_exam_answer_analysis.py                 # 扫全部桶
  python3 scripts/audit_exam_answer_analysis.py math-hujiao     # 扫某桶
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# 「错选 D」「误选 D」「会选 D」是在讲干扰项，不是结论，必须先排除
# 只认「结论式」表述；裸「选 X」噪声太大（解析检查常写「选 A 的同学把…」），不再当结论
LETTER = re.compile(r"(?<![错误会易])(?:答案为|答案是|故选|应选|答案选|所以选|因此选|正确选项(?:是|为)?)\s*([ABCD])")
LABELS = "ABCD"


def audit_item(it):
    out = []
    ans = str(it.get("answer") or "").strip()
    ana = it.get("analysis") or ""
    if not ana or not ans:
        return out
    if it.get("type") in ("choice", "multi"):
        if it.get("type") == "multi":
            picked = set(re.findall(r"[ABCD]", ans))
        else:
            picked = {ans} if ans in LABELS else set()
        for m in LETTER.finditer(ana):
            got = m.group(1)
            if picked and got not in picked:
                out.append(f"解析结论「{m.group(0)}」与 answer={ans} 不一致")
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    buckets = [only] if only else sorted(
        d for d in os.listdir(DATA) if os.path.isdir(os.path.join(DATA, d)))
    total = flagged = 0
    for b in buckets:
        files = sorted(glob.glob(os.path.join(DATA, b, "exams", "*", "*.json")))
        if not files:
            continue
        nb = 0
        for p in files:
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            for sec in d.get("sections") or []:
                for it in sec.get("items") or []:
                    total += 1
                    bad = audit_item(it)
                    if bad:
                        nb += 1
                        flagged += 1
                        print(f"{os.path.relpath(p, ROOT)} 第 {it.get('no')} 题：{'；'.join(bad)}")
        if nb:
            print(f"  ↑ {b}: {nb} 处")
    print(f"\n扫描 {total} 题 | 可疑 {flagged} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
