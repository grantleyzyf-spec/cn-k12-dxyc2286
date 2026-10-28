# -*- coding: utf-8 -*-
"""人教 A 版高中数学 5 册（974 页）无文字层 PDF → OCR 文本。

为什么需要：这 5 个 PDF 整页是图，pdftotext 只出空白，导致只能做「章级」核对；
要核到小节级（3.1 函数的概念）必须先有可搜索的文本层。

做法：PyMuPDF 渲染页面（默认 300 DPI、灰度）→ macOS Vision（VNRecognizeTextRequest，
accurate + zh-Hans + 语言纠正）识别 → 按行拼接。Vision 对中文排版准确率高、速度快
（约 0.2–0.6 s/页），比 tesseract chi_sim 更适合教材正文。

产物（可续跑，每页一个缓存文件）：
  <OUT>/pages/<book>/pNNNN.txt    单页文本
  <OUT>/<book>.txt                合并文本，页间插 `=====PAGE n=====`

用法：
  python3 ocr_highschool.py                 # 全部 5 册
  python3 ocr_highschool.py --book 选必第2册 # 单册
  python3 ocr_highschool.py --dpi 250 --workers 8
"""
import argparse
import glob
import os
import sys
import time
from multiprocessing import Pool

import fitz

BASE = "/Users/a627692/Desktop/中小学教材/高中教材/高中数学/人教版（A版）"
OUT = "/Users/a627692/Desktop/qbank-upgrade/math/ocr_hs"
BOOKS = ["必修第1册", "必修第2册", "选必第1册", "选必第2册", "选必第3册"]

_DOCS = {}


def _ocr_image(path):
    import Quartz
    import Vision
    from Foundation import NSURL

    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(0)                      # 0 = accurate
    req.setRecognitionLanguages_(["zh-Hans", "en-US"])
    req.setUsesLanguageCorrection_(True)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)
    lines = []
    for r in req.results() or []:
        cands = r.topCandidates_(1)
        if cands and len(cands):
            lines.append(cands[0].string())
    return "\n".join(lines)


def _page(args):
    book, pno, dpi = args
    cache = os.path.join(OUT, "pages", book, f"p{pno + 1:04d}.txt")
    if os.path.exists(cache) and os.path.getsize(cache) > 0:
        return pno, open(cache, encoding="utf-8").read(), True
    pdf = os.path.join(BASE, f"A版 {book}.pdf")
    doc = _DOCS.get(pdf)
    if doc is None:
        doc = _DOCS[pdf] = fitz.open(pdf)
    page = doc[pno]
    pm = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    tmp = os.path.join(OUT, "tmp", f"{book}_{pno + 1:04d}.png")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    pm.save(tmp)
    try:
        txt = _ocr_image(tmp)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    with open(cache, "w", encoding="utf-8") as f:
        f.write(txt)
    return pno, txt, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", action="append", default=None)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    books = a.book or BOOKS
    os.makedirs(OUT, exist_ok=True)
    total_t0 = time.time()
    grand = 0
    for book in books:
        pdf = os.path.join(BASE, f"A版 {book}.pdf")
        if not os.path.exists(pdf):
            print(f"跳过（缺文件）{pdf}")
            continue
        n = fitz.open(pdf).page_count
        grand += n
        t0 = time.time()
        print(f"\n=== {book}（{n} 页，dpi={a.dpi}，workers={a.workers}）")
        results = {}
        cached = 0
        with Pool(a.workers) as pool:
            for i, (pno, txt, was_cached) in enumerate(
                    pool.imap_unordered(_page, [(book, p, a.dpi) for p in range(n)]), 1):
                results[pno] = txt
                cached += 1 if was_cached else 0
                if i % 25 == 0 or i == n:
                    el = time.time() - t0
                    print(f"   {i}/{n} 页  用时 {el:.0f}s  缓存命中 {cached}", flush=True)
        merged = []
        for p in range(n):
            merged.append(f"=====PAGE {p + 1}=====")
            merged.append(results.get(p, ""))
        out_path = os.path.join(OUT, f"{book}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(merged) + "\n")
        chars = sum(len(x) for x in results.values())
        print(f"   → {out_path}  {chars} 字符  {time.time() - t0:.0f}s")
    print(f"\n全部完成：{grand} 页，总用时 {time.time() - total_t0:.0f}s")


if __name__ == "__main__":
    main()
