# -*- coding: utf-8 -*-
"""北京版数学结构盘点：从 大单元整体教学设计 docx（单元/章）+ 教材 TXT（节）解析
「册 → 单元 → 课时」三层结构，输出 units.json。

用法: python3 parse_structure.py
输出: data/math-bj/_build/units.json
"""
import glob
import json
import os
import re

HOME = os.path.expanduser("~")
DOCX = os.path.join(HOME, "Desktop/中小学教材/中小学教材/数学")
TXT = os.path.join(HOME, "Desktop/中小学教材/精准提取各学科教材TXT文档/数学/北京版")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "units.json")

CN = "一二三四五六七八九十"
BOOK_ORDER = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "四下",
              "五上", "五下", "六上", "六下", "七上", "七下", "八上", "八下", "九上", "九下"]


def cn_number(s):
    """中文序号 → int，支持 1–99。"""
    s = s.strip()
    if not s:
        return None
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1 if len(s) > 1 else 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1 if s in CN else None


def parse_docx_name(fn):
    """从大单元 docx 文件名解析 (学段, 册, 单元号, 单元名)。"""
    m = re.search(r"(小学|初中)?([一二三四五六七八九])年级([上下])册", fn)
    if not m:
        return None
    seg = "小学" if cn_number(m.group(2)) <= 6 else "初中"
    book = f"{m.group(2)}年{m.group(3)}册".replace("年级", "年")
    book = f"{m.group(2)}上" if m.group(3) == "上" else f"{m.group(2)}下"
    tail = fn[m.end():]
    tail = re.sub(r"\s*大单元整体教学设计.*$", "", tail).strip()
    # 单元/章号：第N单元 / 第一章 / 一、
    m2 = re.match(r"^第?([一二三四五六七八九十]+)(?:单元|章)(.*)$", tail)
    if m2:
        return seg, book, cn_number(m2.group(1)), m2.group(2).strip()
    m3 = re.match(r"^([一二三四五六七八九十]+)、\s*(.+)$", tail)
    if m3:
        return seg, book, cn_number(m3.group(1)), m3.group(2).strip()
    # 无编号（数学百花园 / 总复习 / 主题活动）
    return seg, book, None, tail.strip()


def docx_lessons(path):
    """小学大单元 docx 的「十五、教-学-评一致性课时设计」里的 第N课时 名称。"""
    try:
        import docx
    except ImportError:
        return []
    d = docx.Document(path)
    paras = [p.text.strip() for p in d.paragraphs if p.text.strip()]
    out = []
    for p in paras:
        m = re.match(r"^[（(]?[一二三四五六七八九十]+[）)]?\s*第(\d+)课时\s*(.+)$", p)
        if m:
            name = re.sub(r"^[\s:：、.]+", "", m.group(2)).strip()
            if 2 <= len(name) <= 30:
                out.append((int(m.group(1)), name))
    return out


def txt_sections(book):
    """初中教材 TXT 目录里的 x.y 节标题 → [(节号, 节名)]。"""
    for seg in ("小学", "初中"):
        p = os.path.join(TXT, seg, f"北京版数学{book}.txt")
        if os.path.exists(p):
            return open(p, encoding="utf-8", errors="ignore").read()
    return ""


def main():
    rows = []
    for seg in ("小学", "初中"):
        d = os.path.join(DOCX, seg, "北京版", "大单元整体教学设计")
        for f in sorted(os.listdir(d)):
            if not f.endswith(".docx") or f.startswith("~$"):
                continue
            info = parse_docx_name(f)
            if not info:
                print("UNPARSED", f)
                continue
            s, book, unit_no, unit_name = info
            lessons = docx_lessons(os.path.join(d, f)) if s == "小学" else []
            rows.append(dict(seg=s, book=book, unit_no=unit_no, unit_name=unit_name,
                             docx=f, lessons=[{"no": n, "name": nm} for n, nm in lessons],
                             n_lessons=len(lessons)))
    rows.sort(key=lambda r: (r["seg"] != "小学", BOOK_ORDER.index(r["book"]) if r["book"] in BOOK_ORDER else 99,
                             r["unit_no"] or 99))
    json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    by_book = {}
    for r in rows:
        k = (r["seg"], r["book"])
        by_book.setdefault(k, dict(units=0, lessons=0))
        by_book[k]["units"] += 1
        by_book[k]["lessons"] += r["n_lessons"]
    tot_u = tot_l = 0
    for (seg, book), v in sorted(by_book.items(), key=lambda x: (x[0][0] != "小学", BOOK_ORDER.index(x[0][1]) if x[0][1] in BOOK_ORDER else 99)):
        print(f"  {seg} {book}: 单元 {v['units']:2d}  课时 {v['lessons']:3d}")
        tot_u += v["units"]
        tot_l += v["lessons"]
    print(f"合计 单元 {tot_u} / 课时 {tot_l}")
    no_lesson = [r for r in rows if r["n_lessons"] == 0]
    print("无课时名的单元:", len(no_lesson))
    for r in no_lesson[:12]:
        print("   -", r["seg"], r["book"], r["unit_no"], r["unit_name"])


if __name__ == "__main__":
    main()
