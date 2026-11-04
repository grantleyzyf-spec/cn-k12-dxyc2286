#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科技版高中化学 5 册 PDF → data/chemistry-hukeji/_text/<册>.txt（每页前加 [[pN]]）"""
import glob
import os
import re

import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-hukeji", "_text")
SRC = os.path.expanduser("~/Desktop/中小学教材/中小学教材/化学/高中/沪科技版")
BOOKS = {
    "必修第一册": "必修第一册",
    "必修第二册": "必修第二册",
    "选择性必修第一册": "选择性必修第一册",
    "选择性必修第二册": "选择性必修2",
    "选择性必修第三册": "选择性必修3",
}
os.makedirs(D, exist_ok=True)
for book, key in BOOKS.items():
    cand = [f for f in glob.glob(os.path.join(SRC, "*.pdf")) if key in os.path.basename(f)]
    if book == "必修第一册":
        cand = [f for f in cand if "选择性必修" not in os.path.basename(f)]
    assert len(cand) == 1, (book, cand)
    doc = fitz.open(cand[0])
    parts = []
    for i, page in enumerate(doc, 1):
        txt = page.get_text()
        txt = re.sub(r"[ \t\u3000]+", "", txt)
        parts.append(f"[[p{i}]]\n{txt}")
    out = os.path.join(D, f"{book}.txt")
    open(out, "w", encoding="utf-8").write("\n".join(parts))
    han = len(re.findall(r"[\u4e00-\u9fa5]", "\n".join(parts)))
    print(f"{book}: {len(doc)} 页 / {han} 汉字 → {out}")
