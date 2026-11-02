#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 math-bsd 全部试卷，找出与题库相似度 ≥ 阈值的题（默认 0.85）。

为什么不用逐卷跑 check_math_bsd_exam.py：那个每卷都要重新解析 10k 题的 questions.json，
219 卷要二十分钟以上。这里一次载入题库，先用 difflib 的 quick_ratio（相似度上界）筛候选，
再对候选算真 ratio，结果与 checker 同口径但快两个数量级。

用法：python3 scripts/scan_bsd_exam_dupes.py [--min 0.85] [--json /tmp/out.json]
"""
import argparse
import glob
import json
import os
import re
import sys
from difflib import SequenceMatcher

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "math-bsd")


def norm(s: str) -> str:
    s = (s or "").replace("\u3000", " ")
    return re.sub(r"\s+", "", s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=0.85)
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    th = a.min

    bank = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
    stems = [(q["id"], norm(q.get("prompt", ""))) for q in bank]
    print(f"题库 {len(stems)} 题")

    hits = []
    files = sorted(glob.glob(os.path.join(D, "exams", "*", "*.json")))
    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        for sec in d.get("sections") or []:
            for it in sec.get("items") or []:
                s = norm(it.get("stem", ""))
                if not s:
                    continue
                sm = SequenceMatcher(None, s, "")
                best_r, best_id = 0.0, ""
                for qid, qs in stems:
                    sm.set_seq2(qs)
                    if sm.real_quick_ratio() < th or sm.quick_ratio() < th:
                        continue
                    r = sm.ratio()
                    if r > best_r:
                        best_r, best_id = r, qid
                if best_r >= th:
                    hits.append(dict(file=os.path.relpath(p, REPO), book=d.get("book"),
                                     paper=d.get("paper"), no=it.get("no"),
                                     itemId=it.get("itemId"), qid=best_id, ratio=round(best_r, 3),
                                     stem=it.get("stem", "")[:80]))
        print(f"  {os.path.basename(p)} 累计命中 {len(hits)}", flush=True)

    print(f"\n共 {len(files)} 卷 · 相似度 ≥{th} 的题 {len(hits)} 处")
    for h in sorted(hits, key=lambda x: -x["ratio"]):
        print(f"  {h['ratio']:.2f} {h['book']} / {h['paper']} 第{h['no']}题 ({h['itemId']}) ↔ {h['qid']}")
    if a.json:
        json.dump(hits, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
