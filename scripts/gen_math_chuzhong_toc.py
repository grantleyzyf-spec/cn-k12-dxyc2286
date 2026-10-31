# -*- coding: utf-8 -*-
"""初中（人教版）「每节内容对应页码」生成器 —— 从目录页文本解析，产出与小学同格式 TXT。

初中教材目录是纯文本、层级固定：`第一章　有理数` / `１．１　正数和负数` + 全角页码，
所以不需要字号法，直接解析目录页即可（页脚偏移按「目录标注页码 vs PDF 页序」抽样校准）。

用法：python3 scripts/gen_math_chuzhong_toc.py [--book 七年级上册] [--write]
"""
import argparse
import glob
import json
import os
import re

import fitz

SRC = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/初中/人教版"
OUT = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/math/keshi_toc")
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册"]
FW = {ord(c): str(i) for i, c in enumerate("０１２３４５６７８９")}
SKIP = re.compile(r"^(小结|数学活动|阅读与思考|探究与发现|图说数学史|信息技术应用|综合与实践|"
                  r"复习题|习题|目录|致同学|后记)")


def fw2ascii(s):
    """全角数字→ASCII；全角句点「．」（U+FF0E）→「.」；全角空格→半角。
    初中目录里节号写作「１．１」，只翻数字不翻句点会一条也匹配不上（实测 5 册全 0 节）。"""
    return (s or "").translate(FW).replace("．", ".").replace("　", " ")


def find_pdf(book):
    grade, sem = book[:3], book[-2:]
    c = [p for p in glob.glob(f"{SRC}/*.pdf") if grade in p and sem in p]
    return c[0] if c else None


def parse(book):
    pdf = find_pdf(book)
    if not pdf:
        return None
    doc = fitz.open(pdf)
    # 目录常跨 2–3 页，且只有第一页带「目　　录」抬头 ⇒ 找到抬头后连读后续页，
    # 直到某页不再出现「第X章」/「N.N」行（那是正文开始了）
    lines, start = [], None
    for i in range(min(14, len(doc))):
        t = fw2ascii(doc[i].get_text())
        if start is None:
            if "目" in t and "录" in t:
                start = i
            else:
                continue
        got = False
        for ln in t.split("\n"):
            ln = ln.strip()
            if not ln:
                continue
            if re.match(r"^第[一二三四五六七八九十]+章", ln) or re.match(r"^\d+\.\d+\s", ln) or re.fullmatch(r"\d{1,3}", ln):
                got = True
            lines.append(ln)
        if start is not None and i > start and not got:
            break
    rows, unit = [], None
    for ln in lines:
        if ln in ("目 录", "目录", "目　　录"):
            continue
        mc = re.match(r"^第([一二三四五六七八九十]+)章\s*(.+)$", ln)
        if mc:
            unit = {"no": mc.group(1), "name": mc.group(2).strip()}
            continue
        # 目录页里混着正文解说行（如「0.1 ＝110，－0.5＝」「5.32 ，0.3」），
        # 它们同样以「数字.数字」开头 ⇒ 必须要求节名是中文、且不含等号/斜杠/逗号，否则会多出假课时
        ms = re.match(r"^(\d+)\.(\d+)\s*([\u4e00-\u9fa5][\u4e00-\u9fa5、，（）与和的分式表]*)$", ln)
        if ms:
            rows.append({"unit_no": ms.group(1), "unit": unit, "no": f"{ms.group(1)}.{ms.group(2)}",
                         "name": ms.group(3).strip(), "page": None})
            continue
        if rows and rows[-1]["page"] is None and re.fullmatch(r"\d{1,3}", ln):
            rows[-1]["page"] = int(ln)
    # 页脚偏移：用「目录首页所在的 PDF 页序」与第 1 页正文校准不做强求，直接给 PDF 页序备注
    rows = [r for r in rows if not SKIP.match(r["name"])]
    return {"book": book, "pdf": os.path.basename(pdf), "pages": len(doc), "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    books = [a.book] if a.book else BOOKS
    os.makedirs(OUT, exist_ok=True)
    for b in books:
        d = parse(b)
        if not d:
            print(f"{b}: 缺 PDF")
            continue
        print(f"{b}: {len(d['rows'])} 节（{d['pages']} 页）")
        if not a.write:
            for r in d["rows"][:6]:
                print("   ", r["no"], r["name"], r["page"])
            continue
        lines = [f"数学（人教版·初中）{b}　每节内容对应页码",
                 "（自动解析自目录页文本；页码＝教材目录标注的印刷页）", ""]
        cur = None
        for r in d["rows"]:
            u = r["unit"]
            if u and u["name"] != cur:
                cur = u["name"]
                lines.append(f"{u['no']}　{u['name']}")
            pg = r["page"] if r["page"] is not None else "?"
            lines.append(f"　{r['no']}　{r['name']} {pg}")
        open(f"{OUT}/{b}.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print(f"   ✅ 写 {OUT}/{b}.txt")


if __name__ == "__main__":
    main()
