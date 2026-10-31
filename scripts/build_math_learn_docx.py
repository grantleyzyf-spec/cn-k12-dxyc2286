# -*- coding: utf-8 -*-
"""学层（学生版精讲）Markdown → docx（学生打印版），一课时一份。

版式：A4；标题黑体三号居中；小节标题黑体小四、左侧竖线色块；正文宋体五号 1.5 倍行距；
课本原文引用：浅灰底 + 左缩进；❌/✅ 对照保留原来的行首符号；自查题用方框列表。

用法：
    python3 scripts/build_math_learn_docx.py                  # 全部册
    python3 scripts/build_math_learn_docx.py 七年级上册        # 单册
"""
import glob
import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
LEARN = f"{REPO}/data/math/learn"
OUT_ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料/学层精讲/数学/人教版")


def set_font(run, cn="宋体", size=10.5, bold=False, en="Times New Roman"):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)


def shade(p, color="F2F2F2"):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), color)
    p._p.get_or_add_pPr().append(el)


def add_para(doc, text="", size=10.5, bold=False, cn="宋体", align=None,
             before=0, after=4, line=1.5, left=0, right=0, first=0, color=None, shaded=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if left:
        pf.left_indent = Cm(left)
    if right:
        pf.right_indent = Cm(right)
    if first:
        pf.first_line_indent = Pt(first)
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if text:
        # 行内 **bold** 拆成多个 run
        for i, seg in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
            if not seg:
                continue
            r = p.add_run(seg)
            set_font(r, cn=cn, size=size, bold=bold or (i % 2 == 1))
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
    if shaded:
        shade(p, shaded)
    return p


def new_doc():
    doc = Document()
    s = doc.sections[0]
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(2.2)
    s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.2)
    s.right_margin = Cm(2.2)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    for tag in ("w:overflowPunct", "w:kinsoku", "w:autoSpaceDE", "w:autoSpaceDN"):
        if doc.settings.element.find(qn(tag)) is None:
            doc.settings.element.append(OxmlElement(tag))
    return doc


def render(md, book, title, path):
    doc = new_doc()
    add_para(doc, f"数学（人教版）{book}　{title}", size=16, bold=True, cn="黑体",
             align="center", after=2)
    add_para(doc, "学生版精讲 · 先读课本原文，再用大白话拆开，最后自查", size=9,
             align="center", after=10, color="666666")
    for raw in md.split("\n"):
        ln = raw.rstrip()
        if not ln.strip():
            continue
        if ln.startswith("# "):
            continue                     # 一级标题已作为文档标题
        if ln.startswith("## "):
            add_para(doc, ln[3:].strip(), size=12, bold=True, cn="黑体", before=10, after=6)
        elif ln.startswith("### "):
            add_para(doc, ln[4:].strip(), size=11, bold=True, cn="黑体", before=6, after=4)
        elif ln.startswith("> "):
            body = ln[2:].strip()
            # ❌/✅ 对照不做灰底，课本原文引用做灰底
            is_q = body[:1] not in "❌✅"
            add_para(doc, body, size=10.5, left=0.7 if is_q else 0.4,
                     right=0.7 if is_q else 0, before=2, after=4,
                     shaded="F2F2F2" if is_q else None)
        elif re.match(r"^\d+\.\s", ln):
            txt = re.sub(r"^(\d+)\.\s*", r"\1. ", ln)
            pp = add_para(doc, txt, size=10.5, after=6, first=0)
            pp.paragraph_format.left_indent = Cm(0.7)
            pp.paragraph_format.first_line_indent = Cm(-0.7)
        elif ln.startswith("- [ ]"):
            add_para(doc, "☐ " + ln[5:].strip(), size=10.5, left=0.6, after=2)
        elif ln.startswith("- "):
            add_para(doc, "• " + ln[2:].strip(), size=10.5, left=0.6, after=2)
        else:
            add_para(doc, ln, size=10.5, after=4, first=21)
    # 页脚页码
    p0 = doc.sections[0].footer.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = p0.add_run()
    set_font(r0, size=9)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r0._element.addnext(fld)
    doc.save(path)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(glob.glob(f"{LEARN}/*.json"))
    if only:
        files = [f for f in files if os.path.basename(f)[:-5] == only]
    if not files:
        print("没有找到学层 JSON")
        return
    n = 0
    for f in files:
        data = json.load(open(f, encoding="utf-8"))
        book = data["book"]
        d = os.path.join(OUT_ROOT, book)
        os.makedirs(d, exist_ok=True)
        used = set()
        for L in data.get("lessons") or []:
            safe = re.sub(r"[\\/:*?\"<>|]", "_", L["title"])
            # 同册可能有两课时同名（如两个「练习一」）⇒ 撞名时补 topicId，否则后一篇会覆盖前一篇
            if safe in used:
                safe = f"{safe}_{L['topicId']}"
            used.add(safe)
            render(L["markdown"], book, L["title"], os.path.join(d, f"{safe}.docx"))
            n += 1
    print(f"共渲染 {n} 篇学层 docx → {OUT_ROOT}")


if __name__ == "__main__":
    main()
