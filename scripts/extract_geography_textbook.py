#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽人教版地理教材 PDF 文字层 → data/geography/_text/<册>.txt（学层引文回表源）。

只做「去空白/去页码噪声」的规范化：每行保留原页文本，字符间空格全部去掉，
这样 check_geo_learn.py 用 qnorm（去空白）即可被子串命中。
"""
import os, re, subprocess, sys

TEXTBOOK = os.path.expanduser("~/Desktop/中小学教材/中小学教材/地理")
OUT = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/geography/_text")
os.makedirs(OUT, exist_ok=True)

SRC = {
    "七年级上册": f"{TEXTBOOK}/初中/人教版/义务教育教科书 地理 七年级 上册_1756191689035.pdf",
    "七年级下册": f"{TEXTBOOK}/初中/人教版/义务教育教科书 地理 七年级 下册_1756191689035.pdf",
    "八年级上册": f"{TEXTBOOK}/初中/人教版/义务教育教科书 地理 八年级 上册_1756191689873.pdf",
    "八年级下册": f"{TEXTBOOK}/初中/人教版/义务教育教科书 地理 八年级 下册_1756191689873.pdf",
    "必修第一册": f"{TEXTBOOK}/高中/人教版/9787107338755_普通高中教科书·地理_高一年级_必修第一册_人民教育出版社_1787020862164.pdf",
    "必修第二册": f"{TEXTBOOK}/高中/人教版/9787107338748_普通高中教科书·地理_高一年级_必修第二册_人民教育出版社_1787020863017.pdf",
    "选择性必修1": f"{TEXTBOOK}/高中/人教版/9787107347207_普通高中教科书·地理_高二年级_选择性必修1自然地理基础_人民教育出版社_1787020863205.pdf",
    "选择性必修2": f"{TEXTBOOK}/高中/人教版/9787107345708_普通高中教科书·地理_高二年级_选择性必修2区域发展_人民教育出版社_1787020865243.pdf",
    "选择性必修3": f"{TEXTBOOK}/高中/人教版/9787107349157_普通高中教科书·地理_高二年级_选择性必修3资源、环境与国家安全_人民教育出版社_1787020864012.pdf",
}

for book, pdf in SRC.items():
    if not os.path.exists(pdf):
        print(f"缺件 {book}: {pdf}")
        continue
    txt = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"],
                         capture_output=True, text=True).stdout
    pages = txt.split("\f")
    out_lines = []
    for i, pg in enumerate(pages, 1):
        pg = pg.replace("\u3000", "")
        lines = []
        for ln in pg.split("\n"):
            ln = re.sub(r"[ \t]+", "", ln).strip()
            if not ln:
                continue
            if re.fullmatch(r"[\d\-—·\.]{1,4}", ln):   # 页码行
                continue
            lines.append(ln)
        if lines:
            out_lines.append(f"@@PAGE {i}@@")
            out_lines.extend(lines)
    dst = os.path.join(OUT, f"{book}.txt")
    open(dst, "w", encoding="utf-8").write("\n".join(out_lines) + "\n")
    han = len(re.findall(r"[\u4e00-\u9fa5]", "\n".join(out_lines)))
    print(f"{book}: {len(pages)} 页 / {han} 汉字 → {dst}")
