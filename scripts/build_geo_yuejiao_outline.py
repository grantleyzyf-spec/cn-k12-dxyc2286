#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""粤教粤人版初中地理：从大单元教学设计 docx 抽册/单元/课时结构 → _outline.json

结构源：<教材目录>/2026{春,秋}粤教粤人版义务教育地理<册>第<X>单元 … 大单元整体教学设计.docx
取「十五、教-学-评一致性课时设计」段内的「第N课时：<课时名>」，每单元 8 课时。
"""
import glob
import json
import os
import re
import zipfile
from xml.etree import ElementTree as ET

SRC = os.path.expanduser("~/Desktop/中小学教材/中小学教材/地理/初中/粤教粤人版")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "geography-yuejiao", "_outline.json")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

CN = "一二三四五六七八九十"


def doc_text(path):
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    return "\n".join("".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p"))


def main():
    books = {}
    pat = re.compile(r"粤教粤人版义务教育地理(.+?册)第([一二三四五六七八九十]+)单元\s*(.+?)\s*大单元整体教学设计")
    for f in sorted(glob.glob(os.path.join(SRC, "*.docx"))):
        name = os.path.basename(f)
        m = pat.search(name)
        if not m:
            continue
        book, unit_no, unit_name = m.group(1), m.group(2), m.group(3).strip()
        txt = doc_text(f)
        i = txt.rfind("十五、")
        j = txt.find("十六、", i)
        seg = txt[i:j] if i >= 0 else ""
        lessons = re.findall(r"第([一二三四五六七八九十\d]+)课时[：:]\s*(.+)", seg)
        lessons = [(n, s.strip()) for n, s in lessons]
        books.setdefault(book, []).append({"unit": unit_no, "name": unit_name, "lessons": lessons})

    order = ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]
    out = []
    for b in order:
        us = sorted(books.get(b, []), key=lambda x: CN.index(x["unit"][0]) if x["unit"][0] in CN else 99)
        out.append({"book": b, "units": us})
        print(f"{b}: {len(us)} 单元 / {sum(len(u['lessons']) for u in us)} 课时")
        for u in us:
            assert len(u["lessons"]) == 8, (b, u["name"], len(u["lessons"]))
            print(f"   第{u['unit']}单元 {u['name']}: {[x[1] for x in u['lessons']][:2]} …")
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("→", OUT)


if __name__ == "__main__":
    main()
