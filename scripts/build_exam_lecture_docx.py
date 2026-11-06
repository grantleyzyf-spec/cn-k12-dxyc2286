# -*- coding: utf-8 -*-
"""试卷讲解（单元/期中/期末）Markdown → docx（学生打印版），一卷一份。

版式同学层精讲（A4 / 黑体标题 / 宋体五号 1.5 倍行距），公式走 subject_typo，
所以化学式下标、物理单位、基因名正斜体与学层完全同源。

用法：
    python3 scripts/build_exam_lecture_docx.py                  # 全部
    python3 scripts/build_exam_lecture_docx.py 八年级下册        # 单册
"""
import glob
import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subject_typo  # noqa: E402

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
BUCKET = os.environ.get("MATH_BUCKET", "math")
EDITION = os.environ.get("MATH_EDITION", "人教版")
SUBJECT_NAME = os.environ.get("SUBJECT_NAME", "数学")   # 学科名（语文等）；非数学时绕过 BOOK_INFO 用通用学段判定
LEC = f"{REPO}/data/{BUCKET}/exam_lectures"
# 根目录到「试卷讲解」，学科/版本由 book_info() 拼接（避免与 EDITION 重复嵌套）
OUT_ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料/试卷讲解")

# 册名 → (学科, 版本, 学段)
BOOK_INFO = {
    "一年级上册": ("数学", "人教版", "小学"), "一年级下册": ("数学", "人教版", "小学"),
    "二年级上册": ("数学", "人教版", "小学"), "二年级下册": ("数学", "人教版", "小学"),
    "三年级上册": ("数学", "人教版", "小学"), "三年级下册": ("数学", "人教版", "小学"),
    "四年级上册": ("数学", "人教版", "小学"), "五年级上册": ("数学", "人教版", "小学"),
    "六年级上册": ("数学", "人教版", "小学"),
    "七年级上册": ("数学", "人教版", "初中"), "七年级下册": ("数学", "人教版", "初中"),
    "八年级上册": ("数学", "人教版", "初中"), "八年级下册": ("数学", "人教版", "初中"),
    "九年级上册": ("数学", "人教版", "初中"),
    "必修第一册": ("数学", "人教版", "高中"), "必修第二册": ("数学", "人教版", "高中"),
    "选择性必修第一册": ("数学", "人教版", "高中"),
    "选择性必修第二册": ("数学", "人教版", "高中"),
    "选择性必修第三册": ("数学", "人教版", "高中"),
}


def _stage_of(book):
    m = re.match(r"([一二三四五六七八九])年级", book or "")
    if m:
        return "小学" if m.group(1) in "一二三四五六" else "初中"
    return "高中"


def book_info(book):
    if SUBJECT_NAME != "数学":          # 语文等非数学学科：统一学科名 + 通用学段
        return (SUBJECT_NAME, EDITION, _stage_of(book))
    # 版本取环境变量 EDITION（版本桶：MATH_BUCKET/MATH_EDITION），不以表内「人教版」为准
    if book in BOOK_INFO:
        subj, _ver, stage = BOOK_INFO[book]
        return (subj, EDITION, stage)
    for k, v in BOOK_INFO.items():
        if k in book or book in k:
            subj, _ver, stage = v
            return (subj, EDITION, stage)
    return ("数学", EDITION, "小学")


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


def add_para(doc, text="", subject="math", size=10.5, bold=False, cn="宋体", align=None,
             before=0, after=4, line=1.5, left=0, first=0, color=None, shaded=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if left:
        pf.left_indent = Cm(left)
    if first:
        pf.first_line_indent = Pt(first)
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if text:
        parts = re.split(r"\*\*(.+?)\*\*", text)
        # 「**第 3 题（2 分）**：」这类加粗题号要单独成行观感更好，但同段内也保留
        for i, seg in enumerate(parts):
            if not seg:
                continue
            b = bold or (i % 2 == 1)
            for kind, val, ital in subject_typo.docx_segments(seg, subject):
                if kind == "text":
                    r = p.add_run(val)
                    set_font(r, cn=cn, size=size, bold=b)
                    r.font.italic = bool(ital)
                    if color:
                        r.font.color.rgb = RGBColor.from_string(color)
                else:
                    p._p.append(parse_xml(val))
    if shaded:
        shade(p, shaded)
    return p


def new_doc():
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.top_margin = s.bottom_margin = Cm(2.2)
    s.left_margin = s.right_margin = Cm(2.2)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    for tag in ("w:overflowPunct", "w:kinsoku", "w:autoSpaceDE", "w:autoSpaceDN"):
        if doc.settings.element.find(qn(tag)) is None:
            doc.settings.element.append(OxmlElement(tag))
    return doc


def subject_of(book):
    return "math" if book_info(book)[0] == "数学" else "physics"


def render(md, lec, exam, path):
    subject, version, stage = book_info(lec["book"])
    subj_key = {"数学": "math", "物理": "physics", "化学": "chemistry", "生物": "biology",
                "语文": "chinese"}.get(subject) or os.environ.get("MATH_BUCKET", "math")
    doc = new_doc()
    book_disp = lec["book"] or ""
    if version and book_disp.startswith(version):   # 册名自带版本前缀（苏教版一年级上册）时不再重复
        book_disp = book_disp[len(version):].strip()
    paper_disp = str(lec["paper"] or "")
    # 卷名自带册名/版本前缀（「湘教版七年级上册 第1章 有理数 测试卷」）时，标题里不再重复
    for _pfx in (str(lec["book"] or ""), version, f"{version}{book_disp}"):
        if _pfx and paper_disp.startswith(_pfx) and len(paper_disp) > len(_pfx):
            paper_disp = paper_disp[len(_pfx):].strip()
            break
    add_para(doc, f"{subject}（{version}）{book_disp}　{paper_disp} · 讲解", subject=subj_key,
             size=16, bold=True, cn="黑体", align="center", after=2)
    add_para(doc,
             f"满分 {exam.get('fullScore', '')} 分 · {exam.get('duration', '')} 分钟 · "
             f"{len(exam.get('items') or [i for s in exam['sections'] for i in s.get('items', [])])} 题　学生版：先想一遍，再看思路",
             subject=subj_key, size=9, align="center", after=10, color="666666")
    for raw in md.split("\n"):
        ln = raw.rstrip()
        if not ln.strip():
            continue
        if ln.startswith("# "):
            continue
        if ln.startswith("## "):
            add_para(doc, ln[3:].strip(), subject=subj_key, size=12, bold=True, cn="黑体",
                     before=10, after=6)
        elif ln.startswith("### "):
            add_para(doc, ln[4:].strip(), subject=subj_key, size=11, bold=True, cn="黑体",
                     before=6, after=4)
        elif ln.startswith("> "):
            add_para(doc, ln[2:].strip(), subject=subj_key, size=10, left=0.6,
                     before=2, after=4, shaded="F5F5F5")
        elif re.match(r"^\d+\.\s", ln):
            pp = add_para(doc, ln, subject=subj_key, size=10.5, after=4)
            pp.paragraph_format.left_indent = Cm(0.7)
            pp.paragraph_format.first_line_indent = Cm(-0.7)
        elif ln.startswith("- [ ]"):
            add_para(doc, "☐ " + ln[5:].strip(), subject=subj_key, size=10.5, left=0.6, after=2)
        elif ln.startswith("- "):
            add_para(doc, "• " + ln[2:].strip(), subject=subj_key, size=10.5, left=0.6, after=2)
        else:
            add_para(doc, ln, subject=subj_key, size=10.5, after=4, first=21)
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
    files = sorted(glob.glob(f"{LEC}/*/*.json"))
    files = [f for f in files if not os.path.basename(f).startswith("_") and "/_stale/" not in f]
    if only:
        files = [f for f in files if f"/{only}/" in f]
    if not files:
        print("没有找到试卷讲解 JSON")
        return
    n = 0
    for f in files:
        lec = json.load(open(f, encoding="utf-8"))
        # exams/ 目录名可能不带版本前缀，讲解 book 带前缀：逐个候选路径找
        _cands = [lec["book"]]
        for _pre in ("苏教版", "苏科版", "人教版", "北师大版", "沪教版", "湘教版", "青岛版", "冀教版"):
            if str(lec["book"]).startswith(_pre):
                _cands.append(str(lec["book"])[len(_pre):])
        _path = next((p_ for p_ in (f"{REPO}/data/{BUCKET}/exams/{c}/{lec['paper']}.json" for c in _cands)
                      if os.path.exists(p_)),
                     f"{REPO}/data/{BUCKET}/exams/{lec['book']}/{lec['paper']}.json")
        exam = json.load(open(_path, encoding="utf-8"))
        subject, version, stage = book_info(lec["book"])
        d = os.path.join(OUT_ROOT, subject, version, lec["book"])
        os.makedirs(d, exist_ok=True)
        safe = re.sub(r"[\\/:*?\"<>|]", "_", lec["paper"])
        render(lec["markdown"], lec, exam, os.path.join(d, f"{safe}_讲解.docx"))
        n += 1
    print(f"共渲染 {n} 份试卷讲解 docx → {OUT_ROOT}")


if __name__ == "__main__":
    main()
