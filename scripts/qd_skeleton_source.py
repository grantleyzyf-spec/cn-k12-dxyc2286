# -*- coding: utf-8 -*-
"""青岛版数学：册次 / 单元 / 课时结构盘点（骨架的输入）。

三份内容源，按可靠性排序：
1. **教材 PDF 目录页（有文字层）** → 单元号、单元情境名、知识内容、起始页（权威）。
   小学格式：`    快乐的课堂` / `一` / `    —— 1 ~ 5 数的认识和加减法 ……… ［ 7 ］`
   初中格式：`第1章        有理数` / `1.1   正数和负数              3`
2. **大单元整体教学设计 docx** → 小学的「信息窗」名（课时粒度）；扫描版册次（无文字层）连单元也取自这里。
3. **教材 PDF 正文**（`pdftotext`）→ 仅作后续内容层引用，本脚本不解析。

产出 data/math-qd/_inventory.json：
  {books:[{book,grade,semester,stage,source,units:[{no,title,content,page,
           lessons:[{no,name,kind}]}]}], missing_books:[...]}

用法: python3 scripts/qd_skeleton_source.py [--write]
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "math-qd", "_inventory.json")
BOOKDIR = os.path.expanduser("~/Desktop/中小学教材/中小学教材/数学")
DOCXDIR = os.path.expanduser("~/Desktop/中小学教材/中小学教材/大单元整体教学设计合集/数学")
CN = "一二三四五六七八九十"

# 单元标题（小学：情境名 + 知识内容）
RE_PS_UNIT = re.compile(
    r"\n\s*(?P<title>[^\n—［\]\d]{2,20})\n(?:(?P<num>[%s]+)\n)?\s*—{1,3}\s*(?P<content>[^…\n]{2,40}?)\s*[…\s]*［\s*(?P<page>\d+)\s*］" % CN)
# 初中：第N章 + N.M 小节
RE_CH = re.compile(r"第\s*(?P<ch>\d+)\s*章\s*(?P<name>[^\n\d［］【】]{2,24})")
RE_SEC = re.compile(r"(?m)^\s*(?P<ch>\d{1,2})\.(?P<no>\d{1,2})[\s\u3000]+(?P<name>[^\n\d]{2,24}?)(?:[\s\u3000]+\d{1,3})?[\s\u3000]*$")
RE_WINDOW = re.compile(r"信息窗\s*(?P<no>\d)\s*[“\"「](?P<name>[^”\"」]{2,20})[”\"」]")
RE_DOCX_UNIT = re.compile(r"^第(?P<no>[%s]+)(?:单元|章)\s*(?P<name>.+?)\s*大单元整体教学设计" % CN)


def cn2int(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1
    if "十" in s:
        a, b = s.split("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def pdf_toc(pdf):
    """取目录页文本（前 12 页里含「目 录」到下一单元正文之间）。"""
    out = subprocess.run(["pdftotext", "-f", "1", "-l", "12", "-layout", pdf, "-"],
                         capture_output=True, text=True).stdout
    i = out.find("目")
    if i < 0:
        return ""
    j = out.find("目", i + 1)
    block = out[i:]
    # 目录结束后通常紧跟正文页码或章节标题，截到 3000 字足够
    return block[:3500]


def pdf_full(pdf):
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout


def parse_primary_toc(txt):
    out, auto = [], 0
    for m in RE_PS_UNIT.finditer("\n" + txt):
        auto += 1
        no = cn2int(m.group("num")) if m.group("num") else 0
        out.append({"no": no or auto, "numbered": bool(m.group("num")),
                    "title": m.group("title").strip(), "content": re.sub(r"\s+", "", m.group("content")),
                    "page": int(m.group("page")), "lessons": []})
    return out


def parse_junior_toc(txt):
    """初中：第N章（允许「第 2 章」带空格）+ N.M 小节，按章号分组去重。"""
    units, by_no = [], {}
    for m in RE_CH.finditer(txt):
        ch = int(m.group("ch"))
        if ch in by_no:
            continue
        u = {"no": ch, "title": m.group("name").strip(), "content": "", "page": 0, "lessons": []}
        by_no[ch] = u
        units.append(u)
    for m in RE_SEC.finditer(txt):
        ch, no, name = int(m.group("ch")), int(m.group("no")), m.group("name").strip()
        if ch in by_no and no not in [x["no"] for x in by_no[ch]["lessons"]]:
            by_no[ch]["lessons"].append({"no": no, "name": name, "kind": "节"})
    for u in units:
        u["lessons"].sort(key=lambda x: x["no"])
    return units


def docx_units(path):
    from docx import Document
    ps = [p.text.strip() for p in Document(path).paragraphs if p.text.strip()]
    body = "\n".join(t for t in ps if "\t" not in t)
    units, cur = [], None
    for t in ps:
        if "\t" in t:                      # 目录行跳过
            continue
        m = RE_DOCX_UNIT.match(t)
        if m:
            cur = {"no": cn2int(m.group("no")), "title": m.group("name").strip(), "content": "", "page": 0, "lessons": []}
            units.append(cur)
            continue
        if cur is None:
            continue
        for w in RE_WINDOW.finditer(t):
            no = int(w.group("no"))
            if no not in [x["no"] for x in cur["lessons"]]:
                cur["lessons"].append({"no": no, "name": w.group("name").strip(), "kind": "信息窗"})
    for u in units:
        u["lessons"].sort(key=lambda x: x["no"])
    return units


def main():
    write = "--write" in sys.argv
    docx_map = {}
    for d in ("小学", "初中"):
        for f in glob.glob(os.path.join(DOCXDIR, d, "*青岛版数学*.docx")):
            b = os.path.basename(f)
            m = re.search(r"青岛版数学([%s])年级([上下])册" % CN, b)
            if m:
                docx_map[(CN.index(m.group(1)) + 1, m.group(2))] = f

    books = []
    for stage, sub in (("小学", "小学"), ("初中", "初中")):
        for pdf in sorted(glob.glob(os.path.join(BOOKDIR, sub, "青岛版", "*.pdf"))):
            name = os.path.basename(pdf)
            m = re.search(r"数学_([一二三四五六七八九])年级_([上下])册", name)
            if not m:
                continue
            grade, sem = CN.index(m.group(1)) + 1, m.group(2)
            docx = docx_map.get((grade, sem))
            if grade <= 6:
                # 小学：单元与信息窗都以大单元 docx 目录为准（14 册格式统一），
                # 再用教材目录补「主题活动 / 智慧广场 / 项目学习」这类不带单元号的专题单元。
                units = docx_units(docx) if docx else []
                source = "docx"
                special = []
                for u in parse_primary_toc(pdf_toc(pdf)):
                    t = re.sub(r"\s+", "", u["title"])
                    if u.get("numbered") or not re.search(r"主题活动|智慧广场|项目学习|数学游戏|主题活动课", t):
                        continue
                    if re.fullmatch(r"[%s]", t):      # 目录排版错位产生的「四／圆」这类残行
                        continue
                    u["title"], u["numbered"], u["lessons"] = t, False, []
                    special.append(u)
                units += special
            else:
                units, source = parse_junior_toc(pdf_full(pdf)), "toc"
            books.append({"book": f"{m.group(1)}年级{sem}册", "grade": grade, "semester": sem,
                          "stage": stage, "source": source, "pdf": name,
                          "units": units})

    books.sort(key=lambda x: (x["grade"], x["semester"]))
    have = {(b["grade"], b["semester"]) for b in books}
    missing = [f"{CN[g-1]}年级{s}册" for g in range(1, 10) for s in ("上", "下") if (g, s) not in have]
    inv = {"generated_by": "scripts/qd_skeleton_source.py", "books": books, "missing_books": missing}

    print(f"{'册':<10}{'源':<10}{'单元':>4}{'课时':>6}  单元（情境名／知识内容）")
    for b in books:
        nk = sum(len(u["lessons"]) for u in b["units"])
        head = "；".join(f"{u['title']}／{u['content'] or u['title']}" for u in b["units"][:3])
        print(f"{b['book']:<10}{b['source']:<10}{len(b['units']):>4}{nk:>6}  {head[:70]}")
    print("册数:", len(books), "| 单元:", sum(len(b["units"]) for b in books),
          "| 课时:", sum(len(u["lessons"]) for b in books for u in b["units"]))
    print("缺教材:", "、".join(missing) or "无")
    empty = [(b["book"], u["no"], u["title"]) for b in books for u in b["units"] if not u["lessons"]]
    print("无课时（信息窗/小节）的单元:", len(empty), empty[:6])
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(inv, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("WRITTEN", OUT)


if __name__ == "__main__":
    main()
