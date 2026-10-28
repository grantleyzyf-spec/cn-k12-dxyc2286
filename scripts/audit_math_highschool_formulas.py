# -*- coding: utf-8 -*-
"""人教 A 版高中数学 5 册：公式密集页双引擎交叉校对（Vision vs tesseract）。

背景：974 页 OCR 用的是 macOS Vision，对纯文字准；但公式（分式、根号、上下标、希腊字母）
必然有噪声。本脚本挑「公式最密」的 30 页，用**第二个引擎**（tesseract chi_sim，psm 6）
重识别同一页，再看两引擎的差异，给人工抽检排出优先级。

产出：/tmp/mtoc/hs_formula_check.md（逐页指标）+ /tmp/mtoc/hs_formula.json

用法：python3 audit_math_highschool_formulas.py [--per-book 6] [--dpi 300]
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import tempfile

import fitz

BASE = "/Users/a627692/Desktop/中小学教材/高中教材/高中数学/人教版（A版）"
OCR = os.path.expanduser("~/Desktop/qbank-upgrade/math/ocr_hs")
OUT_MD = "/tmp/mtoc/hs_formula_check.md"
OUT_JSON = "/tmp/mtoc/hs_formula.json"
BOOKS = ["必修第1册", "必修第2册", "选必第1册", "选必第2册", "选必第3册"]

FORMULA_CH = set("＝=＋+−-×÷√≤≥≠≈∈∉⊂⊃∪∩αβγθφωπΣ∫△⊥∥°²³ⁿ∑∏∠⌒≌∽±∞∴∵")
FORMULA_PAT = re.compile(r"[a-zA-Z]\s*[²³]|\d+\s*/\s*\d+|√\s*\d|\^\s*\d|\bsin|\bcos|\btan|\blog|\bln")


def norm(s):
    return re.sub(r"[\s　]", "", s or "")


def formula_score(txt):
    ch = sum(1 for c in txt if c in FORMULA_CH)
    pat = len(FORMULA_PAT.findall(txt))
    return ch + 2 * pat


def sim(a, b):
    """顺序敏感的字符级相似度（只作参考：版式重排会拉低它）。"""
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def cjk_bigrams(s):
    s = re.sub(r"[^\u4e00-\u9fa5]", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def coverage(a, b):
    """引擎 A 的中文二元组被引擎 B 覆盖的比例（顺序无关，衡量「同一段话」）。"""
    A, B = cjk_bigrams(a), cjk_bigrams(b)
    return len(A & B) / max(1, len(A))


def digits(s):
    return set(re.findall(r"\d+(?:\.\d+)?", s or ""))


def digit_agree(a, b):
    """公式里的数字串一致率（数字是公式中最承重、OCR 最稳的部分）。"""
    A, B = digits(a), digits(b)
    if not A and not B:
        return 1.0
    return len(A & B) / max(1, len(A | B))


def tesseract_page(pdf, pno, dpi, tmpdir):
    doc = fitz.open(pdf)
    pm = doc[pno].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    name = f"p{pno + 1:04d}.png"
    pm.save(os.path.join(tmpdir, name))
    doc.close()
    # macOS 的 tesseract/leptonica 不认绝对路径 ⇒ 必须 cd 到图片目录用相对名
    subprocess.run(["tesseract", name, "out", "-l", "chi_sim", "--psm", "6"],
                   cwd=tmpdir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = os.path.join(tmpdir, "out.txt")
    txt = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
    for p in (name, out):
        try:
            os.remove(os.path.join(tmpdir, p))
        except OSError:
            pass
    return txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-book", type=int, default=6)
    ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args()

    picked, rows = [], []
    for book in BOOKS:
        path = f"{OCR}/{book}.txt"
        parts = re.split(r"=====PAGE (\d+)=====", open(path, encoding="utf-8").read())
        pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
        scored = sorted(((formula_score(t), p) for p, t in pages.items()), reverse=True)
        picked += [(book, p, s) for s, p in scored[:a.per_book]]

    for book, pno, fscore in picked:
        pdf = f"{BASE}/A版 {book}.pdf"
        parts = re.split(r"=====PAGE (\d+)=====", open(f"{OCR}/{book}.txt", encoding="utf-8").read())
        vision = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}[pno]
        with tempfile.TemporaryDirectory() as td:
            tess = tesseract_page(pdf, pno - 1, a.dpi, td)
        rec = {"book": book, "pdf_page": pno, "formula_score": fscore,
               "vision_chars": len(norm(vision)), "tess_chars": len(norm(tess)),
               "sim_order": round(sim(vision, tess), 3),
               "cjk_cover": round(coverage(vision, tess), 3),
               "digit_agree": round(digit_agree(vision, tess), 3)}
        rows.append(rec)
        dump = "/tmp/mtoc/formula_pages"
        os.makedirs(dump, exist_ok=True)
        open(f"{dump}/{book}_p{pno:03d}.vision.txt", "w", encoding="utf-8").write(vision)
        open(f"{dump}/{book}_p{pno:03d}.tess.txt", "w", encoding="utf-8").write(tess)
        print(f"{book} p{pno}: 公式分 {fscore} · 二元组覆盖 {rec['cjk_cover']} · 数字一致 {rec['digit_agree']} · 顺序相似 {rec['sim_order']}")

    rows.sort(key=lambda r: (r["cjk_cover"], r["digit_agree"]))
    L = ["# 人教 A 版高中数学 5 册 · 公式密集页双引擎交叉校对", "",
         f"- 抽样：每册取「公式符号密度」最高的 {a.per_book} 页，共 {len(rows)} 页",
         "- 引擎 A：macOS Vision（zh-Hans，accurate）＝入库 OCR 所用引擎",
         "- 引擎 B：tesseract chi_sim（psm 6，300 DPI 灰度）＝独立第二引擎",
         "- 三个指标（都不看版式顺序，避免把重排误判成识别错）：",
         "  ① **中文二元组覆盖**＝Vision 的中文 2-gram 被 tesseract 覆盖的比例（衡量「同一段话」）；",
         "  ② **数字一致率**＝两引擎抽出数字串的交集/并集（公式里最承重、OCR 最稳的部分）；",
         "  ③ 顺序敏感相似度（difflib）仅作参考，分栏/公式重排会拉低它。", "",
         "| 册 | PDF 页 | 公式分 | 中文覆盖 | 数字一致 | 顺序相似 | 判读 |",
         "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for r in rows:
        if r["cjk_cover"] >= 0.85:
            verdict = "✅ 正文一致"
        elif r["cjk_cover"] >= 0.6:
            verdict = "⚠️ 正文大体一致，公式区需回看"
        else:
            verdict = "❌ 识别分歧大，公式必须人工录入"
        L.append(f"| {r['book']} | {r['pdf_page']} | {r['formula_score']} | {r['cjk_cover']} | "
                 f"{r['digit_agree']} | {r['sim_order']} | {verdict} |")
    ok = sum(1 for r in rows if r["cjk_cover"] >= 0.85)
    mid = sum(1 for r in rows if 0.6 <= r["cjk_cover"] < 0.85)
    bad = sum(1 for r in rows if r["cjk_cover"] < 0.6)
    dv = [r["digit_agree"] for r in rows]
    L += ["", f"**汇总**：{len(rows)} 页 · 正文一致 {ok} · 大体一致 {mid} · 分歧大 {bad}；"
          f"数字一致率 中位数 {sorted(dv)[len(dv)//2]:.2f}（最低 {min(dv):.2f}）",
          "", "判读口径：`中文覆盖 ≥0.85` ⇒ 该页文字可用于检索/核对；`0.6–0.85` ⇒ 文字可用但公式要回看原页；"
          "`<0.6` ⇒ 公式区不可信。数字一致率低于 0.6 的页面，公式中的数字也不能直接引用。", ""]
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(rows, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(L[-4:]))


if __name__ == "__main__":
    main()
