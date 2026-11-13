#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讲解 docx ↔ 现役讲解 JSON「同源」核验（交付件 vs 源，逐份）。

为什么要有这一条（2026-11-13 实抓）：
  `verify_math_docx.py` 只核学层与试卷（B1 两份齐 / B2 题干 / B3 解析），**不核讲解 docx**；
  技能库七链里只核「讲解合订本」「讲解题块（markdown）」，单份 `<paper>_讲解.docx` 一直无人校。
  实测后果：苏教版必修第一册 8 份讲解 docx 是 11-02 Q0 重写**之前**的旧稿残留——
  与现役 JSON 的汉字二元字组 Jaccard 仅 0.17–0.22（现役 216 份最低 0.989），
  即学生拿到手的纸质讲解讲的是另一套题干/答案。本链把这类「源已换、成品没重渲」钉死在门禁上。

判据（任一不满足即 FAIL）：
  A 每份现役讲解 JSON 必有对应 `<out>/<book>/<paper>_讲解.docx`；
  B **同源**：docx 与 JSON markdown 的汉字二元字组 Jaccard ≥ 0.90
    （标定：216 份现役 min 0.989 / p1 0.990；旧稿残留 0.169–0.212 ⇒ 阈值居中，两侧各留 4 倍余量）；
  C 汉字数比（docx/源）∈ [0.95, 1.15]（标定：现役 1.003–1.007，仅多页眉页脚固定增量）；
  D 题块头「第 N 题（S 分）」的 (题号, 题分) 多重集合必须与 JSON 完全相等（防漏题/题分错位）；
  E 合订本：`<out>/<book>/_合订本/<book>_试卷讲解合订本.docx` 存在，且每份现役讲解的正文
    40% / 70% 处各 40 字特征串都在合订本内（防「单份重渲了、合订本没重建」）；
    另：`exam_lectures/_stale/**` 里的旧稿特征串**不得**出现在合订本（防旧稿又混回去）；
  F 文件名集合：`<out>/<book>/*_讲解.docx` 的 paper 集合必须等于现役讲解 JSON 的 paper 集合
    （多一份旧名、少一份都算错）。

用法：
    python3 scripts/verify_lecture_docx_samesource.py                    # 默认 苏教版 + 苏科版
    python3 scripts/verify_lecture_docx_samesource.py --bucket math-suke --edition 苏科版
    python3 scripts/verify_lecture_docx_samesource.py --quiet
    python3 scripts/verify_lecture_docx_samesource.py --selftest         # 合成夹具（含杀伤力断言）
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

REPO = os.path.expanduser(os.environ.get("REPO")
                          or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料/试卷讲解/数学")
DEFAULT_PAIRS = (("math-sujiao", "苏教版"), ("math-suke", "苏科版"))
HEAD = re.compile(r"第\s*(\d+)\s*题[（(]\s*(\d+)\s*分[）)]")
HAN = re.compile(r"[\u4e00-\u9fa5]")
JACCARD_MIN = 0.90
RATIO_LO, RATIO_HI = 0.95, 1.15


def doc_text(p):
    """Word 把公式排成 OMML，paragraph.text 读不到 ⇒ 同时取 w:t 与 m:t。"""
    with zipfile.ZipFile(p) as z:
        x = z.read("word/document.xml").decode("utf-8", "ignore")
    return html.unescape("".join(re.findall(r"<(?:w|m):t[^>]*>([^<]*)</(?:w|m):t>", x)))


def han(s):
    return len(HAN.findall(s or ""))


def norm(s):
    return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")


def bigrams(s):
    s = re.sub(r"[^\u4e00-\u9fa5]", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def jaccard(a, b):
    ba, bb = bigrams(a), bigrams(b)
    return len(ba & bb) / max(1, len(ba | bb))


def heads(s):
    out = {}
    ms = list(HEAD.finditer(s or ""))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(s)
        out.setdefault(int(m.group(1)), []).append(int(m.group(2)))
    return {k: sorted(v) for k, v in out.items()}


def lectures(repo, bucket):
    out = []
    for p in sorted(glob.glob(f"{repo}/data/{bucket}/exam_lectures/*/*.json")):
        if "_stale" in p:
            continue
        d = json.load(open(p, encoding="utf-8"))
        out.append((d.get("book"), d.get("paper"), d.get("markdown") or "", p))
    return out


def check(repo, bucket, edition, out_root=OUT_ROOT, strict_stale=True):
    errs = []
    root = f"{out_root}/{edition}"
    lecs = lectures(repo, bucket)
    by_book = {}
    for book, paper, md, _ in lecs:
        by_book.setdefault(book, []).append((paper, md))
    for book in sorted(by_book):
        papers = by_book[book]
        docs = sorted(os.path.basename(x) for x in glob.glob(f"{root}/{book}/*_讲解.docx")
                      if not os.path.basename(x).startswith(".~"))
        have = {x[:-len("_讲解.docx")] for x in docs if x.endswith("_讲解.docx")}
        want = {p for p, _ in papers}
        for p in sorted(want - have):
            errs.append(f"[A] {book}·{p}: 讲解 docx 缺失")
        for p in sorted(have - want):
            errs.append(f"[F] {book}·{p}: 无对应现役讲解的多余 docx（旧名/孤儿）")
        for paper, md in papers:
            f = f"{root}/{book}/{paper}_讲解.docx"
            if not os.path.exists(f):
                continue
            t = doc_text(f)
            j = jaccard(t, md)
            if j < JACCARD_MIN:
                errs.append(f"[B] {book}·{paper}: docx 与源不同源（Jaccard {j:.3f} < {JACCARD_MIN}）")
            ratio = han(t) / max(1, han(md))
            if han(md) and not (RATIO_LO <= ratio <= RATIO_HI):
                errs.append(f"[C] {book}·{paper}: 汉字比 {ratio:.3f} 越界"
                            f"（docx {han(t)} / 源 {han(md)}）")
            if heads(t) != heads(md):
                hm, hd = heads(md), heads(t)
                diff = [k for k in set(hm) | set(hd) if hm.get(k) != hd.get(k)]
                errs.append(f"[D] {book}·{paper}: 题块头不一致（题号 {sorted(diff)[:6]}）")
        # E 合订本
        b = f"{root}/{book}/_合订本/{book}_试卷讲解合订本.docx"
        if not os.path.exists(b):
            errs.append(f"[E] {book}: 讲解合订本缺失")
            continue
        T = norm(doc_text(b))
        for paper, md in papers:
            m = norm(md)
            probes = [m[int(len(m) * f):int(len(m) * f) + 100] for f in (0.4, 0.7)]
            if not all(x and x in T for x in probes):
                errs.append(f"[E] {book}·{paper}: 合订本内找不到本篇正文（合订本未重建）")
        if strict_stale:
            cur_md = [md for _, md in papers]
            for p in glob.glob(f"{repo}/data/{bucket}/exam_lectures/_stale/{book}/*.json"):
                try:
                    d = json.load(open(p, encoding="utf-8"))
                except Exception:
                    continue
                sm = d.get("markdown") or ""
                # 同文改名副本（Q0 归一 book 字段留下的 prefixed 重复件）不算旧稿：Jaccard ≥ 0.95 跳过
                if any(jaccard(sm, cm) >= 0.95 for cm in cur_md):
                    continue
                m = norm(sm)
                probes = [m[int(len(m) * f):int(len(m) * f) + 100] for f in (0.4, 0.7)]
                if all(x and x in T for x in probes):
                    errs.append(f"[E] {book}: 合订本仍含旧稿 {os.path.basename(p)} 的正文（应为现役）")
    return errs, len(lecs)


def build_docx(path, text):
    from docx import Document
    doc = Document()
    for line in text.split("\n"):
        if line.strip():
            doc.add_paragraph(re.sub(r"^#+\s*|\*\*", "", line))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc.save(path)


def selftest():
    tmp = tempfile.mkdtemp(prefix="lecdocx_")
    repo = os.path.join(tmp, "repo")
    out = os.path.join(tmp, "out")
    md = "\n".join([
        "# 苏教版一年级上册 第一单元测试卷 · 讲解",
        "## 一、这份卷在考什么",
        "这份卷只考十以内的加减法，题干短、分值密，失分多在把加法看成减法。" * 3,
        "## 三、逐题精讲",
        "**第 1 题（5 分）**",
        "先数一数，三加二等于五，所以答案是 5。" * 3,
        "**第 2 题（6 分）**",
        "把七个分成两份，一份四个，另一份三个，答案是 3。" * 3,
    ])
    mk = lambda: build_fixture(repo, "math-x", "版X", "版X一年级上册", "第一单元测试卷", md, out)
    ok = True

    def run():
        e, n = check(repo, "math-x", "版X", out_root=out, strict_stale=False)
        return e

    # 1 正常
    mk()
    e = run()
    if e:
        print("✗ 夹具1（正常）误报:", e[:2]); ok = False
    # 2 换卷：docx 放另一篇正文
    build_docx(f"{out}/版X/版X一年级上册/第一单元测试卷_讲解.docx", md.replace("三加二等于五", "四加一等于六"))
    e = run()
    if not any(x.startswith("[B]") for x in e):
        print("✗ 夹具2（换卷）未报 B:", e[:2]); ok = False
    # 3 缺文件
    mk()
    os.remove(f"{out}/版X/版X一年级上册/第一单元测试卷_讲解.docx")
    e = run()
    if not any(x.startswith("[A]") for x in e):
        print("✗ 夹具3（缺件）未报 A:", e[:2]); ok = False
    # 4 题分改错
    mk()
    build_docx(f"{out}/版X/版X一年级上册/第一单元测试卷_讲解.docx", md.replace("第 2 题（6 分）", "第 2 题（5 分）"))
    e = run()
    if not any(x.startswith("[D]") for x in e):
        print("✗ 夹具4（题分错）未报 D:", e[:2]); ok = False
    # 5 合订本未重建
    mk()
    build_docx(f"{out}/版X/版X一年级上册/_合订本/版X一年级上册_试卷讲解合订本.docx", "只有目录，没有正文")
    e = run()
    if not any(x.startswith("[E]") for x in e):
        print("✗ 夹具5（合订本旧）未报 E:", e[:2]); ok = False
    # 6 多余旧名 docx
    mk()
    build_docx(f"{out}/版X/版X一年级上册/_合订本/版X一年级上册_试卷讲解合订本.docx", md)
    build_docx(f"{out}/版X/版X一年级上册/第一单元测试卷(旧)_讲解.docx", md)
    e = run()
    if not any(x.startswith("[F]") for x in e):
        print("✗ 夹具6（多余旧名）未报 F:", e[:2]); ok = False
    shutil.rmtree(tmp, ignore_errors=True)
    print(("✅" if ok else "❌") + " selftest 6/6" if ok else "❌ selftest 未过")
    return 0 if ok else 1


def build_fixture(repo, bucket, edition, book, paper, md, out):
    d = f"{repo}/data/{bucket}/exam_lectures/{book}"
    os.makedirs(d, exist_ok=True)
    json.dump({"book": book, "paper": paper, "examId": "x_u1", "markdown": md},
              open(f"{d}/{paper}.json", "w", encoding="utf-8"), ensure_ascii=False)
    build_docx(f"{out}/{edition}/{book}/{paper}_讲解.docx", md)
    build_docx(f"{out}/{edition}/{book}/_合订本/{book}_试卷讲解合订本.docx", md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--bucket")
    ap.add_argument("--edition")
    ap.add_argument("--out-root", default=OUT_ROOT)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    pairs = [(a.bucket, a.edition)] if a.bucket and a.edition else DEFAULT_PAIRS
    rc = 0
    total = 0
    for bucket, edition in pairs:
        errs, n = check(a.repo, bucket, edition, out_root=a.out_root)
        total += len(errs)
        print(f"== {edition} 讲解 docx {n} 份｜问题 {len(errs)}")
        for x in errs[:12]:
            print("   ✗", x)
        if errs:
            rc = 1
    print(f"== 合计 问题 {total}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
