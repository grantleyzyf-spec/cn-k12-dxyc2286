#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普版化学九年级下册 PDF（无文字层，154 页）→ data/chemistry-kepu/_text/九年级下册.txt

复用 ocr_bucket_books.ocr_image（macOS Vision，accurate，zh-Hans）。可续跑：已有页文件跳过。
用法：/usr/bin/python3 scripts/ocr_chem_kepu_xia.py [--dpi 220] [--procs 8]
"""
import argparse
import glob
import os
import sys
from multiprocessing import Pool

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
from ocr_bucket_books import ocr_image  # noqa: E402

PDF = os.path.expanduser("~/Desktop/中小学教材/中小学教材/化学/初中/科普版/义务教育教科书•化学_九年级_下册_科学普及出版社_1754968747754.pdf")
OUT_DIR = os.path.join(REPO, "data", "chemistry-kepu", "_text", "_ocr_xia")
TMP = "/tmp/chem_kepu_ocr"


def job(args):
    pdf, pno, dpi = args
    out = os.path.join(OUT_DIR, "p%03d.txt" % (pno + 1))
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return pno, True
    import fitz
    doc = fitz.open(pdf)
    pm = doc[pno].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    os.makedirs(TMP, exist_ok=True)
    tmp = os.path.join(TMP, "p%04d.png" % (pno + 1))
    pm.save(tmp)
    try:
        txt = ocr_image(tmp)
    except Exception as e:  # noqa: BLE001
        with open(os.path.join(OUT_DIR, "_errors.log"), "a", encoding="utf-8") as f:
            f.write("p%03d\t%s\t%s\n" % (pno + 1, type(e).__name__, e))
        return pno, False
    open(out, "w", encoding="utf-8").write(txt)
    try:
        os.remove(tmp)
    except OSError:
        pass
    return pno, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=220)
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    import fitz
    os.makedirs(OUT_DIR, exist_ok=True)
    n = fitz.open(PDF).page_count
    print("下册 %d 页，OCR 开始（dpi %d，%d 进程）" % (n, a.dpi, a.procs), flush=True)
    with Pool(a.procs) as p:
        res = p.map(job, [(PDF, i, a.dpi) for i in range(n)], chunksize=2)
    ok = sum(1 for _, s in res if s)
    parts = []
    for i in range(n):
        fp = os.path.join(OUT_DIR, "p%03d.txt" % (i + 1))
        if os.path.exists(fp):
            parts.append(open(fp, encoding="utf-8").read())
    dst = os.path.join(REPO, "data", "chemistry-kepu", "_text", "九年级下册.txt")
    open(dst, "w", encoding="utf-8").write("\n".join(parts))
    import re
    txt = open(dst, encoding="utf-8").read()
    print("完成 %d/%d 页｜非空白字符 %d｜→ %s" % (ok, n, len(re.sub(r"\s", "", txt)), dst))


if __name__ == "__main__":
    main()
