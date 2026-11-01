#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把某数学版本的教材 PDF（扫描件/无文字层）逐页 OCR 成 /tmp/<root>/<tag>/ocr/pNNN.txt。

用途：学层精讲要引用教材原文，而 `data/<bucket>/_skeleton.json` 的 volumes 里有 PDF 路径与 tag，
本脚本按 volumes 批量渲染 + macOS Vision 识别（比 tesseract chi_sim 更准），产物与
check_math_<bucket>_learn.py 的 TXT 映射一致（`/tmp/<root>/<tag>/ocr/`）。

用法：
  python3 scripts/ocr_bucket_books.py math-suke --root msk
  python3 scripts/ocr_bucket_books.py math-xiangjiao --root mxj --dpi 250
  python3 scripts/ocr_bucket_books.py math-suke --root msk --tag k7a      # 单册
可续跑：已存在的非空页文件跳过。
"""
import argparse
import glob
import json
import os
import sys
import time
from multiprocessing import Pool

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ocr_image(path):
    import Quartz
    import Vision
    from Foundation import NSURL

    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(0)                    # 0 = accurate
    req.setRecognitionLanguages_(["zh-Hans", "en-US"])
    req.setUsesLanguageCorrection_(True)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    handler.performRequests_error_([req], None)
    lines = []
    for r in req.results() or []:
        c = r.topCandidates_(1)
        if c and len(c):
            lines.append(c[0].string())
    return "\n".join(lines)


def page_job(args):
    pdf, pno, out_dir, dpi, tmp_dir, tag = args
    out = os.path.join(out_dir, f"p{pno + 1:03d}.txt")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return pno, True
    import fitz
    doc = fitz.open(pdf)
    pm = doc[pno].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    tmp = os.path.join(tmp_dir, f"{tag}_{pno + 1:04d}.png")
    pm.save(tmp)
    try:
        txt = ocr_image(tmp)
    except Exception as e:                                    # noqa: BLE001
        with open(os.path.join(out_dir, "_errors.log"), "a", encoding="utf-8") as f:
            f.write(f"p{pno + 1:03d}\t{type(e).__name__}\t{e}\n")
        return pno, False
    with open(out, "w", encoding="utf-8") as f:
        f.write(txt)
    try:
        os.remove(tmp)
    except OSError:
        pass
    return pno, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("--root", required=True, help="输出根名，产物 /tmp/<root>/<tag>/ocr/")
    ap.add_argument("--tag", action="append", help="只跑这些 tag（可多次）")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    sk = os.path.join(REPO, "data", a.subject, "_skeleton.json")
    vols = json.load(open(sk, encoding="utf-8"))["volumes"]
    if a.tag:
        vols = [v for v in vols if v["tag"] in a.tag]
    root = f"/tmp/{a.root}"
    print(f"{a.subject}: {len(vols)} 册 → {root}/<tag>/ocr/  dpi={a.dpi}")

    for v in vols:
        pdf = v.get("pdf") or ""
        if not os.path.isfile(pdf):
            print(f"  !! {v['tag']} PDF 不存在：{pdf}")
            continue
        out_dir = os.path.join(root, v["tag"], "ocr")
        tmp_dir = os.path.join(root, "_tmp")
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(tmp_dir, exist_ok=True)
        # 页数：优先骨架，其次 PDF 实际
        n = int(v.get("pages") or 0)
        if not n:
            import fitz
            n = len(fitz.open(pdf))
        done = len(glob.glob(os.path.join(out_dir, "p*.txt")))
        todo = [p for p in range(n) if not os.path.exists(os.path.join(out_dir, f"p{p + 1:03d}.txt"))]
        print(f"  {v['tag']} {v['book']}  {n} 页  已有 {done}  待跑 {len(todo)}", flush=True)
        if not todo:
            continue
        t0 = time.time()
        fails = 0
        with Pool(a.workers) as pool:
            for i, (pno, ok) in enumerate(pool.imap_unordered(
                    page_job, [(pdf, p, out_dir, a.dpi, tmp_dir, v["tag"]) for p in todo]), 1):
                if not ok:
                    fails += 1
                if i % 20 == 0 or i == len(todo):
                    print(f"    {v['tag']} {i}/{len(todo)} 页  失败 {fails}  {time.time() - t0:.0f}s", flush=True)
    print("完成")


if __name__ == "__main__":
    sys.exit(main())
