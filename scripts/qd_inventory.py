# -*- coding: utf-8 -*-
"""青岛版数学：从「大单元整体教学设计 整册合集」docx 抽取 册 → 单元 → 信息窗 结构。

产出 data/math-qd/_inventory.json（过程文件，供骨架脚本与写作派单使用）：
  {books:[{book, grade, semester, stage, file, units:[{no, name, windows:[...], keshi_hint}]}],
   missing_books:[...]}

用法: python3 scripts/qd_inventory.py [--write]
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "math-qd", "_inventory.json")

SRC_DIRS = [
    os.path.expanduser("~/Desktop/中小学教材/中小学教材/大单元整体教学设计合集/数学/小学"),
    os.path.expanduser("~/Desktop/中小学教材/中小学教材/大单元整体教学设计合集/数学/初中"),
]
CN = "一二三四五六七八九十"
BOOK_RE = re.compile(r"青岛版数学(?P<grade>[一二三四五六七八九])年级(?P<sem>[上下])册")
UNIT_DIR_RE = re.compile(r"^第(?P<no>[%s]+)单元\s*(?P<name>.+?)\s*大单元整体教学设计" % CN)
WINDOW_RE = re.compile(r"信息窗\s*(?P<no>\d)\s*[“\"「](?P<name>[^”\"」]{2,20})[”\"」]")
KESHIL_RE = re.compile(r"(?:共安排|单元整体安排)(?P<n>[%s\d]+)个?课时" % CN)


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


def parse_docx(path):
    from docx import Document
    doc = Document(path)
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    units, cur = [], None
    for t in paras:
        m = UNIT_DIR_RE.match(t)
        if m:
            cur = {"no": cn2int(m.group("no")), "name": m.group("name").strip(), "windows": [], "keshi": None}
            units.append(cur)
            continue
        if cur is None:
            continue
        for w in WINDOW_RE.finditer(t):
            item = {"no": int(w.group("no")), "name": w.group("name").strip()}
            if item["no"] not in [x["no"] for x in cur["windows"]]:
                cur["windows"].append(item)
        if cur["keshi"] is None:
            k = KESHIL_RE.search(t)
            if k:
                try:
                    cur["keshi"] = cn2int(k.group("n"))
                except ValueError:
                    pass
    for u in units:
        u["windows"].sort(key=lambda x: x["no"])
    return units


def main():
    write = "--write" in sys.argv
    files = []
    for d in SRC_DIRS:
        files += glob.glob(os.path.join(d, "*青岛版数学*.docx"))
    books, seen = [], set()
    for f in sorted(files):
        b = os.path.basename(f)
        m = BOOK_RE.search(b)
        if not m:
            print("!! 未解析册名:", b)
            continue
        grade = CN.index(m.group("grade")) + 1
        sem = m.group("sem")
        key = (grade, sem)
        if key in seen:
            print("!! 重复册:", b)
            continue
        seen.add(key)
        units = parse_docx(f)
        declared = re.search(r"（(?P<n>[%s]+)个?单元）" % CN, b)
        books.append({
            "book": f"{m.group('grade')}年级{sem}册", "grade": grade, "semester": sem,
            "stage": "小学" if grade <= 6 else "初中",
            "file": b, "declared_units": cn2int(declared.group("n")) if declared else None,
            "units": units,
        })
    books.sort(key=lambda x: (x["grade"], x["semester"]))
    ALL = {(g, s) for g in range(1, 10) for s in ("上", "下")}
    have = {(b["grade"], b["semester"]) for b in books}
    missing = [f"{CN[g-1]}年级{s}册" for (g, s) in sorted(ALL - have)]
    inv = {"generated_by": "scripts/qd_inventory.py", "books": books, "missing_books": missing}

    print(f"{'册':<10}{'单元数':>6}{'其中声明':>8}{'信息窗总数':>10}")
    for b in books:
        nw = sum(len(u["windows"]) for u in b["units"])
        flag = "" if b["declared_units"] in (None, len(b["units"])) else f"  ⚠️声明{b['declared_units']}"
        print(f"{b['book']:<10}{len(b['units']):>6}{str(b['declared_units']):>8}{nw:>10}{flag}")
    print("合计册数:", len(books), "| 单元:", sum(len(b["units"]) for b in books),
          "| 信息窗:", sum(len(u["windows"]) for b in books for u in b["units"]))
    print("缺教材册次:", "、".join(missing) or "无")
    no_win = [(b["book"], u["no"], u["name"]) for b in books for u in b["units"] if not u["windows"]]
    print("无信息窗的单元:", len(no_win), no_win[:8])
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(inv, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("WRITTEN", OUT)


if __name__ == "__main__":
    main()
