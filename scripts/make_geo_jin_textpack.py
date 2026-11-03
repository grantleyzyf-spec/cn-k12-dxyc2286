#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""晋教版初中地理（山西教育出版社）PDF → 永久 textpack。

产物（学层引文回表的**唯一权威源**，⛔ 不放 /tmp）：
  ~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/晋教版/初中/<册>/
      整册全文.txt      —— 全册逐页拼接
      ocr/pNNN.txt      —— 逐页（名沿惯例保留 ocr/ 前缀，实为 PDF 文字层直转）

判文字层：抽前 20 页数汉字，>500 视为有文字层直接转；否则报「需 OCR」并跳过
（晋教版四册实测均有文字层，InDesign 输出）。
规范化：去掉汉字/字母/数字之间的排版空格（InDesign 常一字一行/字距拆开），
去掉纯页码行与分页符，保留原句逐字可 grep。
"""
import os
import re
import subprocess
import sys

TEXTBOOK = os.path.expanduser("~/Desktop/中小学教材/中小学教材/地理/初中/晋教版")
OUT_ROOT = os.path.expanduser(
    "~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/晋教版/初中"
)

# 册名 → 源 PDF（文件名含出版社与导入时间戳，故按前缀匹配）
SRC = {
    "七年级上册": "9787570340552_义务教育教科书•地理_七年级_上册_山西教育出版社",
    "七年级下册": "9787570340552_义务教育教科书•地理_七年级_下册_山西教育出版社",
    "八年级上册": "9787570346141_义务教育教科书•地理_八年级_上册_山西教育出版社",
    "八年级下册": "9787570346141_义务教育教科书•地理_八年级_下册_山西教育出版社",
}

HAN = re.compile(r"[\u4e00-\u9fff]")
# 只在「汉字/数字/字母 + 空格 + 汉字/数字/字母」之间去空格；标点后的空格留给分词不必要，也一并去
SPACE_BETWEEN = re.compile(r"(?<=[\u4e00-\u9fff0-9A-Za-z])\s+(?=[\u4e00-\u9fff0-9A-Za-z])")


def norm_page(txt: str) -> str:
    lines = []
    for ln in txt.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        # 纯页码 / 页码+符号：丢掉
        if re.fullmatch(r"[\d\s\-—·.、()（）]{1,8}", ln):
            continue
        lines.append(SPACE_BETWEEN.sub("", ln))
    return "\n".join(lines)


def find_pdf(prefix: str) -> str:
    hits = [f for f in os.listdir(TEXTBOOK) if f.startswith(prefix) and f.lower().endswith(".pdf")]
    if not hits:
        return ""
    starts = [h for h in hits if "（" not in h and "(" not in h]  # 排除「(1)」这类副本
    return os.path.join(TEXTBOOK, sorted(starts or hits)[0])


def main() -> int:
    bad = 0
    for book, prefix in SRC.items():
        pdf = find_pdf(prefix)
        if not pdf:
            print(f"❌ {book}: 找不到源 PDF（前缀 {prefix}）")
            bad += 1
            continue
        probe = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", "1", "-l", "20", pdf, "-"],
                               capture_output=True, text=True)
        if len(HAN.findall(probe.stdout or "")) < 500:
            print(f"❌ {book}: 前 20 页汉字 {len(HAN.findall(probe.stdout or ''))} < 500，判为非文字层，需 OCR（本脚本不处理）")
            bad += 1
            continue

        info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", info)
        pages = int(m.group(1)) if m else 0

        out_dir = os.path.join(OUT_ROOT, book)
        page_dir = os.path.join(out_dir, "ocr")
        os.makedirs(page_dir, exist_ok=True)

        total_han = 0
        full_parts = []
        for pno in range(1, pages + 1):
            r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", str(pno), "-l", str(pno), pdf, "-"],
                               capture_output=True, text=True)
            t = norm_page(r.stdout or "")
            total_han += len(HAN.findall(t))
            with open(os.path.join(page_dir, f"p{pno:03d}.txt"), "w", encoding="utf-8") as fh:
                fh.write(t + "\n")
            full_parts.append(t)

        full = "\n".join(full_parts)
        with open(os.path.join(out_dir, "整册全文.txt"), "w", encoding="utf-8") as fh:
            fh.write(full)
        print(f"✅ {book}: {pages} 页 / {total_han} 汉字 → {out_dir}")
    print("全部完成" if not bad else f"有 {bad} 册未成")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
