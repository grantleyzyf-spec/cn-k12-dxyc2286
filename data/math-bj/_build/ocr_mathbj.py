# -*- coding: utf-8 -*-
"""北京版数学教材 PDF → TXT（有文字层直抽，扫描件渲染 + tesseract OCR）。
用法: python3 ocr_mathbj.py [--books 册名子串...]
输出: ~/Desktop/中小学教材/精准提取各学科教材TXT文档/数学/北京版/<学段>/<册>.txt
"""
import json
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
SRC = os.path.join(HOME, "Desktop/中小学教材/中小学教材/数学")
OUT = os.path.join(HOME, "Desktop/中小学教材/精准提取各学科教材TXT文档/数学/北京版")
WORK = os.path.join(HOME, ".hermes/profiles/agent8/cache/scratch/mathbj_ocr")

# 册名规范化：从文件名解析 (学段, 册)
BOOKS = [
    ("小学", "一上", "义务教育教科书•数学_一年级_上册_北京出版社_1754905822296.pdf"),
    ("小学", "一下", "义务教育教科书•数学_一年级_下册_北京出版社_1754905822296.pdf"),
    ("小学", "二上", "义务教育教科书•数学_二年级_上册_北京出版社_1754905823234.pdf"),
    ("小学", "二下", "义务教育教科书•数学_二年级_下册_北京出版社_1754905823234.pdf"),
    ("小学", "三上", "义务教育教科书•数学_三年级_上册_北京出版社_1754905824070.pdf"),
    ("小学", "三下", "义务教育教科书•数学_三年级_下册_北京出版社_1754905824070.pdf"),
    ("小学", "四上", "9787200202663_义务教育教科书•数学_四年级_上册_北京出版社_1787020740357.pdf"),
    ("小学", "五上", "9787200202632_义务教育教科书•数学_五年级_上册_北京出版社_1787020740525.pdf"),
    ("小学", "六上", "9787200202649_义务教育教科书•数学_六年级_上册_北京出版社_1787020740730.pdf"),
    ("初中", "七上", "9787200188653_义务教育教科书•数学_七年级_上册_北京出版社_1787020815288.pdf"),
    ("初中", "七下", "义务教育教科书•数学_七年级_下册_北京出版社_1737863675524.pdf"),
    ("初中", "八上", "9787200194951_义务教育教科书•数学_八年级_上册_北京出版社_1787020816920.pdf"),
    ("初中", "八下", "pdf北京版数学八年级下册_1772437545413.pdf"),
    ("初中", "九上", "9787200202656_义务教育教科书•数学_九年级_上册_北京出版社_1787020816122.pdf"),
]


def norm(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def direct_pdf_text(path):
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True)
    return r.stdout.decode("utf-8", errors="ignore")


def ocr_pdf(path, tag):
    d = os.path.join(WORK, tag)
    os.makedirs(d, exist_ok=True)
    if not os.path.exists(os.path.join(d, "done")):
        subprocess.run(["pdftoppm", "-r", "200", "-png", path, os.path.join(d, "pg")], check=True)
        pngs = sorted(f for f in os.listdir(d) if f.startswith("pg-") and f.endswith(".png"))
        # tesseract 在本机不认绝对路径：必须 cd 后用相对名
        cmd = "ls pg-*.png | xargs -P 8 -I{} tesseract {} {} -l chi_sim --psm 6 2>/dev/null"
        subprocess.run(["bash", "-lc", cmd], cwd=d, check=True)
        open(os.path.join(d, "done"), "w").write("ok")
    parts = []
    for f in sorted(os.listdir(d)):
        if f.startswith("pg-") and f.endswith(".png.txt"):
            parts.append(open(os.path.join(d, f), encoding="utf-8", errors="ignore").read())
    return "\n".join(parts), len([f for f in os.listdir(d) if f.endswith(".png")])


def main():
    os.makedirs(WORK, exist_ok=True)
    only = sys.argv[2:] if len(sys.argv) > 2 and sys.argv[1] == "--books" else None
    inv = []
    for seg, book, fname in BOOKS:
        if only and not any(o in book or o in fname for o in only):
            continue
        path = os.path.join(SRC, seg, "北京版", fname)
        if not os.path.exists(path):
            print("MISS", seg, book, fname, flush=True)
            continue
        direct = direct_pdf_text(path)
        if norm(direct) >= 3000:
            text, mode, pages = direct, "text", None
        else:
            text, pages = ocr_pdf(path, f"{seg}_{book}")
            mode = "ocr"
        dst_dir = os.path.join(OUT, seg)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, f"北京版数学{book}.txt")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(f"# 北京版数学 {seg} {book}｜来源 {fname}｜提取方式 {mode}\n\n{text}")
        row = dict(seg=seg, book=book, mode=mode, pages=pages, hanzi=norm(text), txt=dst)
        inv.append(row)
        print("OK", seg, book, mode, "hanzi=", row["hanzi"], flush=True)
        json.dump(inv, open(os.path.join(WORK, "_done.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
