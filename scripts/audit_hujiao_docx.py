#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版 Word 交付件终审（只读、轻负载）：卷头/结构/字数/串版/占位符

用法：python3 scripts/audit_hujiao_docx.py
判定口径来自仓库既有约定：
- 试卷：22 题、满分 150、时长 120；答案卷须有「评分标准」
- 讲解：六段（考什么/考点地图/逐题精讲/整卷复盘/五步学习法/自查）
- 学层：七段（生活场景/课本原文/费曼翻译/例题/易错/五步/自查），1200–2600 汉字
- 合订本：有「目　录」，篇数与 learn JSON 课时数一致
"""
import glob
import json
import os
import re
import sys
from docx import Document

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料")
ED = "沪教版"
PLACEHOLDER = re.compile(r"TODO|XXX|待补|占位|\{\{|\}\}|undefined|NaN")
HAN = re.compile(r"[\u4e00-\u9fa5]")

fails = []


def docx_text(p):
    d = Document(p)
    return [x.text.strip() for x in d.paragraphs if x.text.strip()]


def chk(cond, msg):
    if not cond:
        fails.append(msg)


def main():
    # ---- 试卷 ----
    papers = [f for f in glob.glob(f"{ROOT}/学科图谱原创试卷/数学/{ED}/{ED}*/**/*.docx", recursive=True)
              if not os.path.basename(f).startswith(".~")]
    sheets = [f for f in papers if "_试卷.docx" in f]
    answers = [f for f in papers if "参考答案与评分标准" in f]
    print(f"试卷 {len(sheets)} 份 / 答案卷 {len(answers)} 份")
    chk(len(sheets) == len(answers) == 41, f"试卷/答案卷数量不配对：{len(sheets)}/{len(answers)}")
    for p in sheets:
        ps = docx_text(p)
        head = ps[0] if ps else ""
        chk("（沪教版）" in head and "人教版" not in head, f"卷头版本错：{os.path.basename(p)} → {head[:40]}")
        chk("150 分" in " ".join(ps[:3]) and "120 分钟" in " ".join(ps[:3]), f"卷头分值/时长缺：{os.path.basename(p)}")
        nums = {int(m.group(1)) for x in ps for m in [re.match(r"^(\d{1,2})．", x)] if m}
        chk(len(nums) == 22 and max(nums or {0}) == 22, f"题号不齐：{os.path.basename(p)} 共 {len(nums)} 题")
        chk(not PLACEHOLDER.search(" ".join(ps)), f"占位符残留：{os.path.basename(p)}")
    for p in answers:
        ps = docx_text(p)
        chk("评分标准" in " ".join(ps), f"答案卷无评分标准：{os.path.basename(p)}")
        chk("解析" in " ".join(ps), f"答案卷无解析：{os.path.basename(p)}")

    # ---- 讲解 ----
    lecs = [f for f in glob.glob(f"{ROOT}/试卷讲解/数学/{ED}/{ED}*/**/*.docx", recursive=True)
            if not os.path.basename(f).startswith(".~")]
    print(f"讲解 {len(lecs)} 份")
    chk(len(lecs) == 41, f"讲解数量 {len(lecs)}≠41")
    need = ["考什么", "考点地图", "逐题精讲", "复盘", "五步学习法", "自查"]
    for p in lecs:
        ps = docx_text(p)
        body = " ".join(ps)
        chk("（沪教版）" in ps[0], f"讲解卷头版本错：{os.path.basename(p)}")
        miss = [k for k in need if k not in body]
        chk(not miss, f"讲解缺段 {miss}：{os.path.basename(p)}")
        chk(len(HAN.findall(body)) >= 4500, f"讲解字数不足 {len(HAN.findall(body))}：{os.path.basename(p)}")
        chk(not PLACEHOLDER.search(body), f"讲解占位符：{os.path.basename(p)}")

    # ---- 学层 ----
    learns = [f for f in glob.glob(f"{ROOT}/学层精讲/数学/{ED}/{ED}*/**/*.docx", recursive=True)
              if not os.path.basename(f).startswith(".~") and "_合订本" not in f]
    print(f"学层 {len(learns)} 篇")
    chk(len(learns) == 80, f"学层数量 {len(learns)}≠80")
    # 第一节标题各册措辞不同（「先说生活里的一件事」/「开场：…」），按同义集合判
    need7 = [("生活", "开场", "先说"), ("课本原文",), ("费曼",), ("例题",),
             ("易错",), ("五步学习法",), ("自查",)]
    for p in learns:
        ps = docx_text(p)
        body = " ".join(ps)
        chk("（沪教版）" in ps[0], f"学层卷头版本错：{os.path.basename(p)}")
        miss = [k[0] for k in need7 if not any(w in body for w in k)]
        chk(not miss, f"学层缺段 {miss}：{os.path.basename(p)}")
        n = len(HAN.findall(body))
        # docx 比 md 多卷头/副标题/小节标题（约 30 字），带宽放宽到 2680
        chk(1200 <= n <= 2680, f"学层字数出带 {n}：{os.path.basename(p)}")

    # ---- 合订本 ----
    books = sorted(glob.glob(f"{ROOT}/学层精讲/数学/{ED}/{ED}*/_合订本/*.docx"))
    print(f"合订本 {len(books)} 本")
    chk(len(books) == 5, f"合订本数量 {len(books)}≠5")
    for b in books:
        ps = docx_text(b)
        body = " ".join(ps)
        chk("目" in body[:200] and "录" in body[:200], f"合订本无目录：{os.path.basename(b)}")
        chk("（沪教版）" in ps[1] if len(ps) > 1 else False, f"合订本副标题版本错：{os.path.basename(b)}")
        book = os.path.basename(b).replace("_学层精讲合订本.docx", "")
        lf = f"{REPO}/data/math-hujiao/learn/{book}.json"
        want = len(json.load(open(lf, encoding="utf-8"))["lessons"]) if os.path.isfile(lf) else None
        got = len([x for x in ps if re.match(r"^\d+\.\s*\d+\.\d+", x)])
        chk(want is None or got == want, f"合订本篇数 {got}≠{want}：{book}")

    print("\n== 终审：", ("全部通过" if not fails else f"{len(fails)} 项不通过"), "==")
    for f in fails[:25]:
        print("  ❌", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
