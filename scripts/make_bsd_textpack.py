#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版数学教材 textpack 落盘（永久目录）：<TXT_ROOT>/<tag>/{整册全文.txt, ocr/pNNN.txt}

判文字层：pdftotext 前 20 页汉字 > 500 ⇒ 文字层，逐页 pdftotext；
否则 tesseract chi_sim OCR（pdftoppm -r 200 → png → txt）。

用法：
  python3 scripts/make_bsd_textpack.py --books 九年级上册 必修第一册            # 只做文字层
  python3 scripts/make_bsd_textpack.py --books 七年级上册 --ocr --jobs 6        # 强制 OCR
"""
import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import tempfile

PDF_ROOT = {
    "小学": os.path.expanduser("~/Desktop/中小学教材/中小学教材/数学/小学/北师大版"),
    "初中": os.path.expanduser("~/Desktop/中小学教材/中小学教材/数学/初中/北师大版"),
    "高中": os.path.expanduser("~/Desktop/中小学教材/中小学教材/数学/高中/北师大版"),
}
TXT_ROOT = os.path.expanduser("~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/数学/北师大版")
TAGS = {
    "一年级上册": "mbsd1a", "一年级下册": "mbsd1b", "二年级上册": "mbsd2a", "二年级下册": "mbsd2b",
    "三年级上册": "mbsd3a", "三年级下册": "mbsd3b", "四年级上册": "mbsd4a", "四年级下册": "mbsd4b",
    "五年级上册": "mbsd5a", "五年级下册": "mbsd5b", "六年级上册": "mbsd6a", "六年级下册": "mbsd6b",
    "七年级上册": "mbsd7a", "七年级下册": "mbsd7b", "八年级上册": "mbsd8a", "八年级下册": "mbsd8b",
    "九年级上册": "mbsd9a", "九年级下册": "mbsd9b",
    "必修第一册": "mbsdbx1", "必修第二册": "mbsdbx2",
    "选择性必修第一册": "mbsdxb1", "选择性必修第二册": "mbsdxb2",
}
STAGE = {"一年级上册": "小学", "一年级下册": "小学", "二年级上册": "小学", "二年级下册": "小学",
         "三年级上册": "小学", "三年级下册": "小学", "四年级上册": "小学", "四年级下册": "小学",
         "五年级上册": "小学", "五年级下册": "小学", "六年级上册": "小学", "六年级下册": "小学",
         "七年级上册": "初中", "七年级下册": "初中", "八年级上册": "初中", "八年级下册": "初中",
         "九年级上册": "初中", "九年级下册": "初中",
         "必修第一册": "高中", "必修第二册": "高中",
         "选择性必修第一册": "高中", "选择性必修第二册": "高中"}


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def find_pdf(book):
    d = PDF_ROOT[STAGE[book]]
    if not os.path.isdir(d):
        return None
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".pdf"):
            continue
        if book in f.replace(" ", ""):
            return os.path.join(d, f)
        # 「选择性必修第一册」形如 选择性必修第一册
        if book.startswith("选择性必修") and book in f:
            return os.path.join(d, f)
    # 兜底：七年级上册 ← 「七年级 上册」
    g, sem = book[:3], book[3:]
    for f in sorted(os.listdir(d)):
        if f.lower().endswith(".pdf") and g in f and sem in f:
            return os.path.join(d, f)
    return None


def npages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return int(m.group(1)) if m else 0


def page_text(pdf, p):
    r = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", "-f", str(p), "-l", str(p), pdf, "-"],
                       capture_output=True, text=True)
    return r.stdout


def page_ocr(pdf, p, tmpdir):
    png = os.path.join(tmpdir, f"p{p:03d}.png")
    subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", "200", "-png", "-singlefile", pdf, png[:-4]],
                   capture_output=True)
    r = subprocess.run(["tesseract", png, "stdout", "-l", "chi_sim", "--psm", "6"],
                       capture_output=True, text=True)
    return r.stdout


def do_book(book, force_ocr=False, jobs=6):
    tag = TAGS[book]
    pdf = find_pdf(book)
    if not pdf:
        print(f"!! {book} 无教材 PDF", flush=True)
        return book, "nopdf", 0, 0
    n = npages(pdf)
    probe = sum(hanzi(page_text(pdf, p)) for p in range(2, min(21, n + 1)))
    ocr = force_ocr or probe < 500
    outdir = os.path.join(TXT_ROOT, STAGE[book], book)
    os.makedirs(os.path.join(outdir, "ocr"), exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix=f"bsd_{tag}_")
    pages = list(range(1, n + 1))

    def one(p):
        t = page_ocr(pdf, p, tmpdir) if ocr else page_text(pdf, p)
        with open(os.path.join(outdir, "ocr", f"p{p:03d}.txt"), "w", encoding="utf-8") as fh:
            fh.write(t)
        return t

    texts = [None] * n
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        for i, t in enumerate(ex.map(one, pages)):
            texts[i] = t
    full = "\n".join(t or "" for t in texts)
    with open(os.path.join(outdir, "整册全文.txt"), "w", encoding="utf-8") as fh:
        fh.write(full)
    mode = "OCR" if ocr else "文字层"
    print(f"✅ {book} [{tag}] {mode} {n} 页 汉字{hanzi(full)} → {outdir}", flush=True)
    return book, mode, n, hanzi(full)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", nargs="*", required=True)
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    for b in a.books:
        do_book(b, a.ocr, a.jobs)


if __name__ == "__main__":
    main()
