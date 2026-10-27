# -*- coding: utf-8 -*-
"""从扫描版《义务教育俄语课程标准（2022年版）》PDF 重建可回表的 TXT 源。

为什么需要它：该 PDF 无文字层（111 页整页图像，pdftotext 只出 111 字节），
而 russian 学科 96 个知识点的 standards[].quote 需要「逐字回表」。本脚本用
PyMuPDF 抽出整页图 → tesseract chi_sim 2 倍放大识别 → 行级抽查重识别（见
LINE_REOCR）→ 输出带页标记的 TXT，供 scripts/test_russian.py 回表。

用法：python3 scripts/ocr_russian_standard.py [--out <txt>]
依赖：pymupdf, pillow, tesseract(+chi_sim)
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import tempfile

PDF = ("/Users/a627692/Desktop/中小学教材/中小学教材/2025修订课程标准/"
       "义务教育2022课程标准/义务教育俄语课程标准（2022年版）.pdf")
OUT = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
       "《义务教育俄语课程标准》(2022年版) 扫描件OCR.txt")

# 整页 2 倍识别仍错的页：对这些页里「命中关键词的行」改成 6 倍行级重识别。
# 例：第 23 页「2. 简单句：掌握陈述句、疑问句和祈使句的意义和用法」整页识别
# 会把「句」读成「铅/名/铝」，行级 6 倍 + psm 6 才能读对。
LINE_REOCR = {23: ["简单", "陈述"]}

# 行级重识别仍不能完全读对的行：人工逐字核对后的定本（对照依据写进注释）。
# 第 23 页该行「句」字被 6 倍重识别读成「名」（陈述名/祈使名），用 9 倍裁切图
# 逐字目视核对为「2. 简单句：掌握陈述句、疑问句和祈使句的意义和用法。」
LINE_OVERRIDE = {
    (23, "陈述"): "2. 简单句：掌握陈述句、疑问句和祈使句的意义和用法。",
}

HEADER = ("【OCR 派生文本】义务教育俄语课程标准（2022年版）\n"
          "原件为扫描 PDF（无文字层），由 scripts/ocr_russian_standard.py "
          "逐页 tesseract chi_sim 识别生成；第 23 页「简单句」行经 6/9 倍行级重识别 + 人工逐字核对。\n"
          "本文件仅供课标回表校验，不可作为原文引用版式依据。\n\n")


def norm(s):
    return re.sub(r"\s+", "", s or "")


def tesseract(img_path, psm="3"):
    """返回 (纯文本, tsv 行)。tesseract 的 stderr 非 UTF-8，必须 errors=replace。"""
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "o")
        r = subprocess.run(["tesseract", img_path, base, "-l", "chi_sim",
                            "--psm", psm],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if r.returncode != 0:
            raise RuntimeError(f"tesseract 失败 {img_path}: {(r.stderr or '')[:200]}")
        txt = open(base + ".txt", encoding="utf-8", errors="replace").read()
        subprocess.run(["tesseract", img_path, base, "-l", "chi_sim",
                        "--psm", psm, "tsv"], capture_output=True)
        rows = list(csv.DictReader(open(base + ".tsv", encoding="utf-8",
                                        errors="replace"), delimiter="\t"))
    return txt, rows


def reocr_lines(img2x, img6x, rows, keywords, zoom_ratio=3):
    """把命中 keywords 的行按 6 倍图行级重识别，返回 {原行文本: 新文本}。"""
    groups = {}
    for r in rows:
        if not (r.get("text") or "").strip() or r.get("level") != "5":
            continue
        key = (r["block_num"], r["par_num"], r["line_num"])
        groups.setdefault(key, []).append(r)
    patch = {}
    for key, words in groups.items():
        line = "".join(w["text"] for w in words)
        if not any(k in line for k in keywords):
            continue
        l = min(int(w["left"]) for w in words)
        t = min(int(w["top"]) for w in words)
        rgt = max(int(w["left"]) + int(w["width"]) for w in words)
        bot = max(int(w["top"]) + int(w["height"]) for w in words)
        pad = 12
        box = (max(0, l - pad) * zoom_ratio, max(0, t - pad) * zoom_ratio,
               (rgt + pad) * zoom_ratio, (bot + pad) * zoom_ratio)
        crop = img6x.crop(box)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
            crop.save(fh.name)
            new, _ = tesseract(fh.name, psm="6")
        os.unlink(fh.name)
        new = new.strip()
        if new and norm(new) != norm(line):
            patch[line] = new
            print(f"    · 行级重识别: {line.strip()[:24]} → {new[:24]}")
    return patch


def apply_patch(text, patch):
    """把行级重识别结果替换回整页文本。

    页文本里词间有空格、tsv 拼出的行没有，所以不能直接 str.replace，
    要用「空白可有可无」的正则匹配旧行。
    """
    for old, new in patch.items():
        pat = r"\s*".join(re.escape(ch) for ch in old)
        text = re.sub(pat, new, text, count=1)
    return text


PAGE_MARK = re.compile(r"={60}\n page (\d+) / (\d+)\n={60}\n")


def split_pages(body):
    """把已生成的 TXT 拆成 (头部, {页号: 该页整块文本（含页标记）})。"""
    starts = [(m.start(), int(m.group(1))) for m in PAGE_MARK.finditer(body)]
    if not starts:
        return body, {}
    head = body[:starts[0][0]]
    blocks = {}
    for idx, (pos, page_no) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(body)
        blocks[page_no] = body[pos:end]
    return head, blocks


def render_page(doc, Image, td, page_no):
    """单页：整页图 → 2 倍识别（含 LINE_REOCR 行级重识别）→ 带页标记的块。"""
    total = doc.page_count
    mark = f"{'=' * 60}\n page {page_no} / {total}\n{'=' * 60}\n"
    imgs = doc[page_no - 1].get_images(full=True)
    if not imgs:
        return "\n" + mark
    raw = doc.extract_image(imgs[0][0])["image"]
    p = os.path.join(td, f"p{page_no:03d}.img")
    open(p, "wb").write(raw)
    im = Image.open(p).convert("L")
    im2 = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    p2 = os.path.join(td, f"p{page_no:03d}_2x.png")
    im2.save(p2)
    text, rows = tesseract(p2)
    if page_no in LINE_REOCR:
        im6 = im.resize((im.width * 6, im.height * 6), Image.LANCZOS)
        text = apply_patch(text, reocr_lines(im2, im6, rows, LINE_REOCR[page_no]))
    for (pg, key), fixed in LINE_OVERRIDE.items():
        if pg != page_no:
            continue
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if key in ln:
                print(f"    · 人工核订第 {page_no} 页: {ln.strip()[:22]} → {fixed[:22]}")
                lines[i] = fixed
        text = "\n".join(lines)
    return "\n" + mark + text


def main():
    import fitz
    from PIL import Image

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--pdf", default=PDF)
    ap.add_argument("--pages", default="",
                    help="只重做这些页并就地替换（逗号分隔，如 23），其余页沿用现有输出")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    only = sorted({int(x) for x in args.pages.split(",") if x.strip()}) if args.pages else None
    print(f"PDF {doc.page_count} 页，无文字层扫描件 → OCR"
          + (f"（仅重做第 {only} 页）" if only else ""))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        if only and os.path.exists(args.out):
            head, blocks = split_pages(open(args.out, encoding="utf-8").read())
            for page_no in only:
                blocks[page_no] = render_page(doc, Image, td, page_no)
                print(f"  · 重做第 {page_no} 页")
            body = HEADER + "".join(blocks[k] for k in sorted(blocks))
        else:
            chunks = [HEADER]
            for page_no in range(1, doc.page_count + 1):
                chunks.append(render_page(doc, Image, td, page_no))
                if page_no % 20 == 0:
                    print(f"  … {page_no}/{doc.page_count}")
            body = "".join(chunks)

    open(args.out, "w", encoding="utf-8").write(body)
    print(f"写出 {args.out}（{len(body)} 字符 / {body.count(chr(10))} 行）")


if __name__ == "__main__":
    sys.exit(main())
