#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 15 链：**单份**交付件的渲染面核验（P1 页码 / P2 空白页 / P3 页数下限 / P4 字体）。

为什么第 14 链不够（2026-11-15 18:00 段）：
第 14 链只核 520 本**合订本**。单份 docx 是教师实际打开的东西，而合订本的拼接方式会**掩盖**
单份的尾部空白页 —— 上一份的最后一张空白页后面紧接着下一份的「段前分页 + 标题」，
在合订本里那一页被标题占了，读起来不空。于是「合订本 0 问题」不能推出「单份 0 问题」。
实测：12 份随机样本就抓到 1 份单份试卷有尾部空白页。

判据与第 14 链同源（`verify_docx_pdf_render.check_one`），族根换成单份目录：
  讲解单份 1312 ｜ 学层单份 4367 ｜ 试卷单份 2608。

用法：
  python3 scripts/verify_single_docx_render.py --limit 4      # 每族 4 份冒烟
  python3 scripts/verify_single_docx_render.py --jobs 6       # 全量（约 40–60 分钟）
  python3 scripts/verify_single_docx_render.py --family 试卷   # 只核一族
  python3 scripts/verify_single_docx_render.py --list         # 只列清单不渲染
"""
import argparse
import concurrent.futures as cf
import json
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_docx_pdf_render as V  # noqa: E402

HOME = os.path.expanduser("~")
SINGLES = (
    ("讲解单份", os.path.join(HOME, "Desktop/学科图谱相关资料/试卷讲解/数学")),
    ("学层单份", os.path.join(HOME, "Desktop/学科图谱相关资料/学层精讲/数学")),
    ("试卷单份", os.path.join(HOME, "Desktop/学科图谱相关资料/学科图谱原创试卷/数学")),
)


def collect(root):
    fs = []
    for dp, dns, fns in os.walk(root):
        if "_合订本" in dp:
            continue
        dns[:] = sorted(d for d in dns if d != "_合订本")
        for f in sorted(fns):
            if f.endswith(".docx") and not f.startswith((".~", "~$")):
                fs.append(os.path.join(dp, f))
    return fs


# ---------- 自检（判据同第 14 链，但夹具必须取自**单份**交付件） ----------
def _append_blank_page(name, data):
    """在正文末尾、sectPr 之前插一个「段前分页的空段」⇒ 末页只剩页码。"""
    if name != "word/document.xml":
        return data
    x = data.decode("utf-8")
    k = x.rfind("<w:sectPr")
    if k < 0:
        return data
    ins = "<w:p><w:pPr><w:pageBreakBefore/></w:pPr></w:p>"
    return (x[:k] + ins + x[k:]).encode("utf-8")


def selftest(min_chars=20):
    import zipfile
    src = sorted(collect(SINGLES[2][1]))[0]     # 一份现役单份试卷
    cases = [
        ("现役单份原样（不该报）", lambda n, d: d, None),
        ("末页只余页号（插入段前分页空段）", _append_blank_page, "P2"),
        ("页码域被删（整页无页码）", V._drop_page_field, "P1"),
    ]
    root = tempfile.mkdtemp(prefix="singlesel_")
    files = []
    for i, (name, fn, _w) in enumerate(cases):
        q = os.path.join(root, "c%d.docx" % i)
        V._rewrite(src, q, fn)
        files.append(q)
    shutil.copy2(src, os.path.join(root, "c0.docx"))
    staged = V.stage(files, root)
    outdir, _ok = V.render(staged, root, jobs=2)
    bad = 0
    for (q, _o), (name, _fn, want) in zip(staged, cases):
        pdf = os.path.join(outdir, os.path.splitext(os.path.basename(q))[0] + ".pdf")
        if not os.path.exists(pdf):
            print("✗ %-34s 渲染失败" % name)
            bad += 1
            continue
        probs, _info = V.check_one(q, pdf, min_chars)
        codes = sorted({c for c, _ in probs})
        okk = (codes == []) if want is None else (want in codes)
        print("%s %-34s 期望 %-4s 实得 %s" % ("✓" if okk else "✗", name, want or "无", codes or "无"))
        if not okk:
            bad += 1
    shutil.rmtree(root, ignore_errors=True)
    print("== 自检 %d/%d" % (len(cases) - bad, len(cases)))
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="每族取前 N 份（0=全部）")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--min-chars", type=int, default=20)
    ap.add_argument("--family", default="")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--json", default="", help="把问题清单写成 json")
    ap.add_argument("--selftest", action="store_true", help="3 个夹具（含 2 类注入）")
    a = ap.parse_args()

    if a.selftest:
        return selftest(a.min_chars)
    items = []
    for fam, root in SINGLES:
        if a.family and a.family not in fam:
            continue
        fs = collect(root)
        if a.limit:
            fs = fs[:: max(1, len(fs) // a.limit)][:a.limit]
        print("%-6s %d 份" % (fam, len(fs)), flush=True)
        items += [(fam, p) for p in fs]
    if not items:
        print("✗ 没有单份 docx 可核")
        return 1
    if a.list:
        return 0
    if not os.access(V.SOFFICE, os.X_OK):
        print("✗ 找不到 LibreOffice：%s" % V.SOFFICE)
        return 1

    t0 = time.time()
    root = tempfile.mkdtemp(prefix="singlegate_")
    try:
        staged = V.stage([p for _f, p in items], root)
        outdir, ok = V.render(staged, root, a.jobs)

        # 判据阶段并行：每份要起 pdfinfo / pdftotext / pdffonts 三个子进程，
        # 8287 份串行实测 30+ 分钟（渲染本身才 10 分钟）⇒ 12 线程放量，判据一字不改。
        def _one(pair):
            (fam, p), (q, _o) = pair
            pdf = os.path.join(outdir, os.path.splitext(os.path.basename(q))[0] + ".pdf")
            if not os.path.exists(pdf):
                return fam, p, [("P0", "未生成 PDF")], 0, []
            probs, info = V.check_one(p, pdf, a.min_chars)
            return fam, p, probs, info["pages"], info.get("warn") or []

        rows = []
        with cf.ThreadPoolExecutor(max_workers=12) as ex:
            for r in ex.map(_one, list(zip(items, staged))):
                rows.append(r)
        per, bad, warns = {}, [], []
        pages_all = 0
        for fam, p, probs, npages, warn in rows:
            d = per.setdefault(fam, {"n": 0, "bad": 0, "pages": 0})
            d["n"] += 1
            d["pages"] += npages
            pages_all += npages
            if warn:
                warns.append((fam, p, warn))
            if probs:
                d["bad"] += 1
                bad.append((fam, p, probs))
        for fam, d in per.items():
            print("%-6s 份 %4d｜页 %6d｜问题 %d" % (fam, d["n"], d["pages"], d["bad"]), flush=True)
        for fam, p, pr in bad[:60]:
            print("  ✗ [%s] %s" % (fam, os.path.relpath(p, HOME)))
            for c, m in pr:
                print("      [%s] %s" % (c, m))
        if len(bad) > 60:
            print("  … 另 %d 份（见 --json）" % (len(bad) - 60))
        for fam, p, w in warns[:20]:
            print("  ⚠ [%s] %s" % (fam, os.path.relpath(p, HOME)))
            for c, m in w:
                print("      [%s] %s" % (c, m))
        if len(warns) > 20:
            print("  … 另 %d 处近空白（见 --json）" % (len(warns) - 20))
        print("== 合计 份 %d｜页 %d｜问题 %d｜近空白 %d｜%.1f 分"
              % (len(items), pages_all, len(bad), len(warns), (time.time() - t0) / 60))
        if a.json:
            with open(a.json, "w", encoding="utf-8") as f:
                json.dump({"bad": [{"family": f, "path": p, "probs": pr} for f, p, pr in bad],
                           "warn": [{"family": f, "path": p, "warn": w} for f, p, w in warns]},
                          f, ensure_ascii=False, indent=1)
            print("清单：%s" % a.json)
        if a.keep:
            print("PDF 留存：%s" % outdir)
        return 0 if not bad else 1
    finally:
        if not a.keep:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
