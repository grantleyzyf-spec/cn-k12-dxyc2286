# -*- coding: utf-8 -*-
"""把一册的试卷讲解合成一本「合订本」docx（封面 + 目录 + 逐份讲解，页脚连续页码）。

版式与单份讲解同源（复用 scripts/build_exam_lecture_docx.py 的段落渲染），
只多封面与目录页。输出：<根>/<学科>/<版本>/<册>/_合订本/<册>_试卷讲解合订本.docx

用法：
    MATH_BUCKET=math-bj MATH_EDITION=北京版 python3 scripts/build_exam_lecture_booklet.py
    MATH_BUCKET=math-bj MATH_EDITION=北京版 python3 scripts/build_exam_lecture_booklet.py 一年级上册
"""
import glob
import importlib.util
import json
import os
import re
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("lec_docx", os.path.join(HERE, "build_exam_lecture_docx.py"))
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)

KIND_RANK = {"unit": 0, "mid": 1, "fin": 2}
CN = "一二三四五六七八九十"


def cn_number(text):
    m = re.search(r"第([一二三四五六七八九十百零〇\d]+)", text or "")
    if not m:
        return 999
    s = m.group(1)
    if s.isdigit():
        return int(s)
    if s == "百":
        return 100
    total, cur = 0, 0
    for ch in s:
        if ch == "十":
            total += (cur or 1) * 10
            cur = 0
        elif ch in CN:
            cur = CN.index(ch) + 1
    return total + cur


def render_md_into(doc, md, subj_key):
    """把一份讲解 markdown 追加进已有 doc（与单份讲解版式一致）"""
    for raw in md.split("\n"):
        ln = raw.rstrip()
        if not ln.strip() or ln.startswith("# "):
            continue
        if ln.startswith("## "):
            L.add_para(doc, ln[3:].strip(), subject=subj_key, size=12, bold=True, cn="黑体", before=10, after=6)
        elif ln.startswith("### "):
            L.add_para(doc, ln[4:].strip(), subject=subj_key, size=11, bold=True, cn="黑体", before=6, after=4)
        elif ln.startswith("> "):
            L.add_para(doc, ln[2:].strip(), subject=subj_key, size=10, left=0.6, before=2, after=4, shaded="F5F5F5")
        elif re.match(r"^\d+\.\s", ln):
            pp = L.add_para(doc, ln, subject=subj_key, size=10.5, after=4)
            pp.paragraph_format.left_indent = L.Cm(0.7)
            pp.paragraph_format.first_line_indent = L.Cm(-0.7)
        elif ln.startswith("- [ ]"):
            L.add_para(doc, "☐ " + ln[5:].strip(), subject=subj_key, size=10.5, left=0.6, after=2)
        elif ln.startswith("- "):
            L.add_para(doc, "• " + ln[2:].strip(), subject=subj_key, size=10.5, left=0.6, after=2)
        else:
            L.add_para(doc, ln, subject=subj_key, size=10.5, after=4, first=21)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    books = sorted(glob.glob(os.path.join(L.LEC, "*")))
    books = [b for b in books if os.path.isdir(b)]
    if only:
        books = [b for b in books if os.path.basename(b) == only]
    total = 0
    for bdir in books:
        book = os.path.basename(bdir)
        papers = []
        for f in glob.glob(os.path.join(bdir, "*.json")):
            d = json.load(open(f, encoding="utf-8"))
            papers.append(d)
        if not papers:
            continue
        papers.sort(key=lambda d: (KIND_RANK.get(d.get("kind"), 9), cn_number(d.get("paper")), d.get("paper") or ""))
        exams = {}
        for f in glob.glob(os.path.expanduser(f"{L.REPO}/data/{os.environ.get('MATH_BUCKET', 'math')}/exams/{book}/*.json")):
            e = json.load(open(f, encoding="utf-8"))
            exams[e["paper"]] = e
        subject, version, stage = L.book_info(book)
        subj_key = {"数学": "math", "物理": "physics", "化学": "chemistry", "生物": "biology", "语文": "chinese"}.get(
            subject, os.environ.get("MATH_BUCKET", "math"))
        doc = L.new_doc()
        L.add_para(doc, f"{subject}（{version}）{book}", subject=subj_key, size=20, bold=True, cn="黑体",
                   align="center", after=6)
        L.add_para(doc, f"试卷讲解合订本 · 共 {len(papers)} 份 · 学生版",
                   subject=subj_key, size=11, align="center", after=14, color="666666")
        L.add_para(doc, "目　录", subject=subj_key, size=13, bold=True, cn="黑体", align="center", after=6)
        for i, p in enumerate(papers, 1):
            L.add_para(doc, f"{i}. {p['paper']}", subject=subj_key, size=10.5, left=0.8, after=2)
        doc.add_page_break()
        for idx, p in enumerate(papers):
            if idx:
                doc.add_page_break()
            ex = exams.get(p["paper"], {})
            L.add_para(doc, p["paper"], subject=subj_key, size=15, bold=True, cn="黑体", align="center", after=2)
            L.add_para(doc,
                       f"满分 {ex.get('fullScore', '')} 分 · {ex.get('duration', '')} 分钟 · "
                       f"{sum(len(s['items']) for s in ex.get('sections', []))} 题",
                       subject=subj_key, size=9, align="center", after=8, color="888888")
            render_md_into(doc, p.get("markdown") or "", subj_key)
        p0 = doc.sections[0].footer.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run()
        L.set_font(r0, size=9)
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        r0._element.addnext(fld)
        d = os.path.join(L.OUT_ROOT, subject, version, book, "_合订本")
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, f"{book}_试卷讲解合订本.docx")
        doc.save(out)
        total += len(papers)
        print(f"✅ {book}：{len(papers)} 份讲解 → {out}")
    print(f"合计 {total} 份讲解并入合订本")


if __name__ == "__main__":
    main()
