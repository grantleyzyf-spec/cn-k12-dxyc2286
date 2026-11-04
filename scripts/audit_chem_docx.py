#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学 docx 交付件自检（基准版本，卷头本就含「人教版」，不套用版本桶判据）。

用法：python3 scripts/audit_chem_docx.py [--root ~/Desktop/学科图谱相关资料]
"""
import argparse
import glob
import json
import os
import re
import zipfile

import docx

HAN = re.compile(r"[\u4e00-\u9fa5]")
SEC7 = [("开场",), ("课本原文",), ("费曼翻译",), ("例题",), ("易错",), ("五步学习法",), ("自查",)]
SEC6 = ["这份卷在考什么", "考点地图", "逐题精讲", "整卷复盘", "五步学习法", "自查清单"]
PLACE = re.compile(r"占位符|TODO|XXX|待补|\{\{|\}\}|undefined|NaN")


def text(p):
    ps = [x.text.strip() for x in docx.Document(p).paragraphs if x.text.strip()]
    return ps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/Desktop/学科图谱相关资料"))
    a = ap.parse_args()
    D = "data/chemistry"
    T = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    ex = glob.glob(f"{D}/exams/*/*.json")
    le = glob.glob(f"{D}/exam_lectures/*/*.json")
    lessons = [t for t in T if t.get("level") == "lesson"]
    bad = []
    paper_dir = f"{a.root}/学科图谱原创试卷/化学/人教版"
    n_p = n_a = 0
    for p in glob.glob(f"{paper_dir}/*/*.docx"):
        b = os.path.basename(p)
        ps = text(p)
        head = ps[0] if ps else ""
        body = " ".join(ps)
        if b.endswith("_试卷.docx"):
            n_p += 1
            if "化学（人教版）" not in head:
                bad.append(f"卷头缺版本：{b} → {head[:30]}")
            nos = []
            for para in ps:
                m = re.match(r"^(\d{1,2})[．.、]", para.strip())
                if m:
                    nos.append(int(m.group(1)))
            if len(nos) < 20 or max(nos) < 24:
                bad.append(f"题号异常：{b}（识别 {len(nos)} 个，最大 {max(nos) if nos else 0}）")
            if PLACE.search(body):
                bad.append(f"占位符：{b}")
        elif "参考答案" in b:
            n_a += 1
    learn_dir = f"{a.root}/学层精讲/化学/人教版"
    n_l = 0
    for p in glob.glob(f"{learn_dir}/*/*.docx"):
        if "_合订本" in p:
            continue
        n_l += 1
        ps = text(p)
        head, body = (ps[0] if ps else ""), " ".join(ps)
        if "化学（人教版）" not in head:
            bad.append(f"学层卷头缺版本：{os.path.basename(p)}")
        miss = [k[0] for k in SEC7 if not any(w in body for w in k)]
        if miss:
            bad.append(f"学层缺段 {miss}：{os.path.basename(p)}")
        n = len(HAN.findall(body))
        if not (1150 <= n <= 2750):
            bad.append(f"学层字数出带 {n}：{os.path.basename(p)}")
    books = glob.glob(f"{learn_dir}/*/_合订本/*.docx")
    lec_dir = f"{a.root}/试卷讲解/化学/人教版"
    n_lec = len(glob.glob(f"{lec_dir}/*/*.docx"))
    badlec = []
    for p in glob.glob(f"{lec_dir}/*/*.docx"):
        if "_合订本" in p:
            continue
        ps = text(p)
        head, body = (ps[0] if ps else ""), " ".join(ps)
        if "化学（人教版）" not in head:
            badlec.append(f"讲解卷头：{os.path.basename(p)}")
        miss = [k for k in SEC6 if k not in body]
        if miss:
            badlec.append(f"讲解缺段 {miss}：{os.path.basename(p)}")
        if len(HAN.findall(body)) < 3800:
            badlec.append(f"讲解字数不足：{os.path.basename(p)}")
    print(f"试卷 {n_p}/{len(ex)}　答案 {n_a}/{len(ex)}　学层 {n_l}/{len(lessons)}　"
          f"学层合订 {len(books)}　讲解 {n_lec}/{len(le)}")
    for x in (bad + badlec)[:20]:
        print("  ❌", x)
    print(f"\n不通过 {len(bad)+len(badlec)} 项")
    return 1 if (bad or badlec) else 0


if __name__ == "__main__":
    raise SystemExit(main())
