# -*- coding: utf-8 -*-
"""沪科技版高中物理 6 册 PDF → _text/<册>.txt（每页加 [[pN]] 标记）。"""
import os
import re
import fitz

SRC = os.path.expanduser("~/Desktop/中小学教材/中小学教材/物理/高中/沪科技版")
DST = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/physics-hushuke/_text")
os.makedirs(DST, exist_ok=True)

BOOKS = {
    "必修第一册": "必修第一册",
    "必修第二册": "必修第二册",
    "选择性必修第一册": "选择性必修第一册",
    "必修第三册": "必修第三册",
    "选择性必修第二册": "选择性必修第二册",
    "选择性必修第三册": "选择性必修第三册",
}

pdfs = [f for f in os.listdir(SRC) if f.lower().endswith(".pdf")]
for book, key in BOOKS.items():
    cand = [f for f in pdfs if key in f]
    if book == "必修第一册":
        cand = [f for f in cand if "选择性必修" not in f]
    if book == "必修第二册":
        cand = [f for f in cand if "选择性必修" not in f]
    if book == "必修第三册":
        cand = [f for f in cand if "选择性必修" not in f]
    assert len(cand) == 1, (book, cand)
    doc = fitz.open(os.path.join(SRC, cand[0]))
    out = []
    for i, page in enumerate(doc, 1):
        t = page.get_text("text")
        t = re.sub(r"[ \t]+", "", t)
        out.append("[[p%d]]\n%s" % (i, t))
    body = "\n".join(out)
    body = re.sub(r"\n{3,}", "\n\n", body)
    han = len(re.findall(r"[\u4e00-\u9fa5]", body))
    with open(os.path.join(DST, book + ".txt"), "w", encoding="utf-8") as f:
        f.write(body)
    print("%s: %d 页 / %d 汉字 → %s" % (book, len(doc), han, os.path.join(DST, book + ".txt")))
