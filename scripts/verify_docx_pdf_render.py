#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 14 链：合订本「渲染面」核验 —— 真转 PDF，查页码 / 空白页 / 页数下限 / 字体内嵌。

为什么需要（2026-11-15 12:00 段）：第 11/12/13 链的 `docxfp.doc_sig` 是**属性级**指纹，
它证明「交付件的 XML 属性 == 现役渲染器会写出什么」，但证明不了三件事：

  1) **页码域每页真的排出来了**。指纹只看得见「footer1.xml 里有 1 个 PAGE 域」；
     若某节 `titlePg` 换了页脚、后续节引用了没域的 footer、或页脚距底边过大把数字挤出页面，
     属性面全绿而读者手里没有页码。
  2) **版面没排出空白页**。11-07 曾出现 260 本合订本空白页的真缺陷，属性上看是「段落数正常」。
  3) **每卷/每课时各占新页**（页数 ≥ 分页符数 + 1）。分页符在册 ≠ 分页真的发生。

判据（逐本）：
  P1 页码：每一页都必须出现**独占一行**的十进制页号，且等于该页页序（1 起）。
  P2 空白页：去掉空白字符后不足 `--min-chars`（默认 20）字符的页 —— 只有页号也算空白页。
  P3 页数下限：pages ≥ pageBreakBefore 数 + 显式分页符（w:br type=page）数 + 1。
  P4 字体内嵌：PDF 里每个字体都必须 emb=yes，且不得是 Fallback / LastResort 类兜底字体。

**渲染器是 LibreOffice，不是 Word**（本机 26.8）。本机缺 Times New Roman / 宋体 / 黑体，
LO 会做等宽度替换（LiberationSerif / Songti SC / ArialUnicodeMS），故本链证的是
「同一引擎下版面自洽、页码连续、无空白页」，**不证 Word 的分页落点**（见文末限度）。

用法：
  python3 scripts/verify_docx_pdf_render.py                 # 全 12 版 520 本合订本
  python3 scripts/verify_docx_pdf_render.py --limit 4       # 每族取 4 本（冒烟）
  python3 scripts/verify_docx_pdf_render.py --selftest      # 4 个夹具（含 3 类注入）
  python3 scripts/verify_docx_pdf_render.py --jobs 3 --quiet
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

SOFFICE = os.environ.get("SOFFICE") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
HOME = os.path.expanduser("~")
FAMILIES = (
    ("试卷合订本", os.path.join(HOME, "Desktop/学科图谱相关资料/学科图谱原创试卷/数学")),
    ("讲解合订本", os.path.join(HOME, "Desktop/学科图谱相关资料/试卷讲解/数学")),
    ("学层合订本", os.path.join(HOME, "Desktop/学科图谱相关资料/学层精讲/数学")),
)
PAT = "**/_合订本/*.docx"
PAGE_LINE = re.compile(r"^第?\s*(\d{1,4})\s*页?$")
_print_lock = threading.Lock()


def log(*a):
    with _print_lock:
        print(*a, flush=True)


# ---------- 收集 ----------
def collect(limit=0, family=None):
    out = []
    for fam, root in FAMILIES:
        if family and family not in fam:
            continue
        fs = sorted(glob.glob(os.path.join(root, PAT), recursive=True))
        fs = [f for f in fs if not os.path.basename(f).startswith((".~", "~$"))]
        if limit:
            fs = fs[:: max(1, len(fs) // limit)][:limit]
        out += [(fam, f) for f in fs]
    return out


# ---------- 渲染 ----------
def stage(files, root):
    """平铺成 f0001.docx：交付目录里同名（不同版同册名）会互相覆盖，故不能按原名转。"""
    src = os.path.join(root, "src")
    os.makedirs(src, exist_ok=True)
    staged = []
    for i, p in enumerate(files):
        q = os.path.join(src, "f%04d.docx" % i)
        try:
            os.link(p, q)
        except OSError:
            shutil.copy2(p, q)
        staged.append((q, p))
    return staged


def _convert_chunk(paths, outdir, profile, tag):
    os.makedirs(profile, exist_ok=True)
    done = set()
    for k in range(0, len(paths), 20):
        part = paths[k:k + 20]
        cmd = [SOFFICE, "-env:UserInstallation=file://" + profile, "--headless", "--norestore",
               "--convert-to", "pdf", "--outdir", outdir] + part
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
        except subprocess.TimeoutExpired:
            log("  ! %s 批次转换超时（%d 份），继续" % (tag, len(part)))
        for q in part:
            if os.path.exists(os.path.join(outdir, os.path.splitext(os.path.basename(q))[0] + ".pdf")):
                done.add(q)
    return done


def render(staged, root, jobs):
    outdir = os.path.join(root, "pdf")
    os.makedirs(outdir, exist_ok=True)
    paths = [q for q, _ in staged]
    buckets = [paths[i::jobs] for i in range(jobs)]
    res = {}
    err = []

    def work(i, bucket):
        try:
            res[i] = _convert_chunk(bucket, outdir, os.path.join(root, "prof%d" % i), "w%d" % i)
        except Exception as e:  # noqa: BLE001
            err.append("%s: %s" % (i, e))

    ths = [threading.Thread(target=work, args=(i, b)) for i, b in enumerate(buckets)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    if err:
        log("  ! 渲染线程异常：" + "; ".join(err))
    ok = set().union(*res.values()) if res else set()
    return outdir, ok


# ---------- 判据 ----------
def docx_breaks(p):
    with zipfile.ZipFile(p) as z:
        x = z.read("word/document.xml").decode("utf-8", "ignore")
    return x.count("<w:pageBreakBefore"), x.count('w:type="page"')


def pdf_pages(pdf):
    r = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True)
    m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.M)
    n = int(m.group(1)) if m else 0
    t = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    pages = t.split("\f")
    while pages and not pages[-1].strip():
        pages.pop()
    return n, pages


def pdf_fonts(pdf):
    r = subprocess.run(["pdffonts", pdf], capture_output=True, text=True)
    bad, names = [], []
    for ln in r.stdout.splitlines()[2:]:
        cols = ln.split()
        if len(cols) < 4:
            continue
        names.append(cols[0].split("+")[-1])
        emb = cols[-4]
        if emb not in ("yes",):
            bad.append((cols[0], emb))
        if re.search(r"(?i)fallback|lastresort", cols[0]):
            bad.append((cols[0], "fallback"))
    return names, bad


def check_one(p, pdf, min_chars=20):
    """返回 (问题列表[(代码, 说明)], 信息 dict)。"""
    probs = []
    n, pages = pdf_pages(pdf)
    if not n or not pages:
        return [("P0", "PDF 页数读不出")], {"pages": 0}
    pbb, brp = docx_breaks(p)
    lo = pbb + brp + 1
    if n < lo:
        probs.append(("P3", "页数 %d < 分页符+1=%d（pbb %d / br %d）" % (n, lo, pbb, brp)))
    miss, wrong, blank, thin = [], [], [], []
    seen = []
    for i, pg in enumerate(pages, 1):
        lines = [l.strip() for l in pg.split("\n") if l.strip()]
        nums = []
        for l in lines:
            m = PAGE_LINE.match(l)
            if m:
                nums.append(int(m.group(1)))
        seen.append(nums[-1] if nums else None)
        if not nums:
            miss.append(i)
        elif nums[-1] != i:
            wrong.append((i, nums[-1]))
        body = re.sub(r"\s", "", "".join(l for l in lines if not PAGE_LINE.match(l)))
        if not body:
            blank.append(i)          # 整页只有页号 ⇒ 真空白页
        elif len(body) < min_chars:
            thin.append(i)           # 有字但几乎空（如目录只溢出 2 行）⇒ 记为警告
    if miss:
        probs.append(("P1", "缺页号 %d 页（首 %s）" % (len(miss), miss[:5])))
    if wrong:
        probs.append(("P1", "页号≠页序 %d 页（首 %s）" % (len(wrong), wrong[:5])))
    if blank:
        probs.append(("P2", "空白页 %d 页（首 %s）" % (len(blank), blank[:5])))
    warn = [("P2w", "近空白页 %d 页（首 %s）" % (len(thin), thin[:5]))] if thin else []
    names, badf = pdf_fonts(pdf)
    if badf:
        probs.append(("P4", "字体未内嵌/兜底 %s" % badf[:3]))
    return probs, {"pages": n, "fonts": sorted(set(names)), "lo": lo, "warn": warn}


# ---------- 自检 ----------
def _rewrite(src, dst, edit):
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            data = edit(it.filename, data)
            zo.writestr(it, data)


def _ins_blank_page(name, data):
    """插一个「只带段前分页的空段」：分页符在册 + 一切属性正常，却排出一整页空白。
    这是 11-07 那次 260 本空白页的形态（属性指纹完全看不出）。"""
    if name != "word/document.xml":
        return data
    x = data.decode("utf-8")
    idxs = [m.start() for m in re.finditer(r"<w:pageBreakBefore", x)]
    if not idxs:
        return data
    k = idxs[min(2, len(idxs) - 1)]
    st = max(x.rfind("<w:p>", 0, k), x.rfind("<w:p ", 0, k))
    if st < 0:
        return data
    ins = "<w:p><w:pPr><w:pageBreakBefore/></w:pPr></w:p>"
    return (x[:st] + ins + x[st:]).encode("utf-8")


def _drop_page_field(name, data):
    if name != "word/footer1.xml":
        return data
    x = data.decode("utf-8")
    return re.sub(r'<w:fldSimple[^>]*w:instr="PAGE"[^>]*/>', "", x).encode("utf-8")


def _pin_page_number(name, data):
    if name != "word/footer1.xml":
        return data
    x = data.decode("utf-8")
    return re.sub(r'<w:fldSimple[^>]*w:instr="PAGE"[^>]*/>',
                  '<w:r><w:t>1</w:t></w:r>', x).encode("utf-8")


def selftest(min_chars=20):
    src = sorted(glob.glob(os.path.join(FAMILIES[0][1], "苏科版/*/_合订本/*试卷合订本.docx")))[0]
    root = tempfile.mkdtemp(prefix="pdfsel_")
    cases = [
        ("现役合订本原样（不该报）", lambda n, d: d, None),
        ("页码域被删（整页无页码）", _drop_page_field, "P1"),
        ("页码写死成 1（第 2 页起错号）", _pin_page_number, "P1"),
        ("末尾多一个空页（只余页号）", _ins_blank_page, "P2"),
    ]
    files = []
    for i, (name, fn, _want) in enumerate(cases):
        q = os.path.join(root, "c%d.docx" % i)
        _rewrite(src, q, fn)
        files.append(q)
    staged = [(q, c[0]) for q, c in zip(files, cases)]
    outdir, ok = render(staged, root, jobs=2)
    bad = 0
    want_of = {q: c[2] for q, c in zip(files, cases)}
    for q, name in staged:
        want = want_of[q]
        pdf = os.path.join(outdir, os.path.splitext(os.path.basename(q))[0] + ".pdf")
        if not os.path.exists(pdf):
            log("✗ %-34s 渲染失败" % name)
            bad += 1
            continue
        probs, _info = check_one(q, pdf, min_chars)
        codes = sorted({c for c, _ in probs})
        okk = (codes == []) if want is None else (want in codes)
        log("%s %-34s 期望 %-4s 实得 %s" % ("✓" if okk else "✗", name, want or "无", codes or "无"))
        if not okk:
            bad += 1
    shutil.rmtree(root, ignore_errors=True)
    log("== 自检 %d/%d" % (len(cases) - bad, len(cases)))
    return 0 if bad == 0 else 1


# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="每族取样本数（0=全部）")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--min-chars", type=int, default=20)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--family", default="", help="只核某一族（试卷/讲解/学层）")
    ap.add_argument("--keep", action="store_true", help="保留 tmp（PDF 供人眼复核）")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.min_chars)
    if not os.access(SOFFICE, os.X_OK):
        log("✗ 找不到 LibreOffice：%s" % SOFFICE)
        return 1
    t0 = time.time()
    items = collect(a.limit, a.family or None)
    if not items:
        log("✗ 没有合订本可核（检查交付根）")
        return 1
    root = tempfile.mkdtemp(prefix="pdfgate_")
    try:
        staged = stage([p for _f, p in items], root)
        outdir, ok = render(staged, root, a.jobs)
        per_fam = {}
        probs_all, pages_all, warn_all = [], [], []
        for (fam, p), (q, _p) in zip(items, staged):
            pdf = os.path.join(outdir, os.path.splitext(os.path.basename(q))[0] + ".pdf")
            d = per_fam.setdefault(fam, {"n": 0, "bad": 0, "pages": 0})
            d["n"] += 1
            if pdf not in ok and not os.path.exists(pdf):
                probs_all.append((p, [("P0", "未生成 PDF")]))
                d["bad"] += 1
                continue
            probs, info = check_one(p, pdf, a.min_chars)
            d["pages"] += info["pages"]
            if info.get("warn"):
                warn_all.append((p, info["warn"]))
            pages_all.append(info["pages"])
            if probs:
                probs_all.append((p, probs))
                d["bad"] += 1
        for fam, d in per_fam.items():
            log("%-6s 本 %3d｜页 %5d｜问题 %d" % (fam, d["n"], d["pages"], d["bad"]))
        if probs_all:
            for p, pr in probs_all[:40]:
                log("  ✗ %s" % os.path.relpath(p, HOME))
                for c, m in pr:
                    log("      [%s] %s" % (c, m))
            if len(probs_all) > 40:
                log("  … 另 %d 本（省略）" % (len(probs_all) - 40))
        for p, w in warn_all[:20]:
            log("  ⚠ %s" % os.path.relpath(p, HOME))
            for c, m in w:
                log("      [%s] %s" % (c, m))
        log("== 合计 本 %d｜页 %d｜问题 %d｜近空白 %d｜%s" % (
            len(items), sum(pages_all), len(probs_all), len(warn_all),
            "%.1f 分" % ((time.time() - t0) / 60)))
        if a.keep:
            log("PDF 留存：%s" % outdir)
        return 0 if not probs_all else 1
    finally:
        if not a.keep:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
