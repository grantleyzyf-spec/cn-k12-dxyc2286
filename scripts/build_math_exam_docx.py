# -*- coding: utf-8 -*-
"""把 exam JSON 渲染成两份 docx：`<卷名>_试卷.docx` 与 `<卷名>_参考答案与评分标准.docx`。

版式口径（与教师打印习惯一致）：
- A4，上下 2.2cm / 左右 2.0cm；正文宋体五号（10.5pt），标题黑体，英文数字 Times New Roman
- 卷头一行「时间 X 分钟　满分 Y 分」，另起一行「学校＿＿＿ 班级＿＿＿ 姓名＿＿＿ 成绩＿＿＿」
- 选择题选项 A–D 同段排两行（每题一行 A/B，一行 C/D），避免竖排浪费版面
- 解答题按分值留答题空行（每 6 分留 2 行，至少 3 行）
- 答案卷：每题给「答案 + 解析 + 分步评分标准」，解答题逐行列出给分点

用法：
    python3 scripts/build_math_exam_docx.py                 # 渲染 data/math/exams 下全部卷
    python3 scripts/build_math_exam_docx.py 七年级上册       # 只渲某册
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
from docx.shared import Cm, Pt

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
EXAM = f"{REPO}/data/math/exams"
OUT_ROOT = os.path.expanduser("~/Desktop/数学测试卷交付")


def set_font(run, cn="宋体", size=10.5, bold=False, en="Times New Roman"):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)


def para(doc, text="", size=10.5, bold=False, align=None, cn="宋体",
         space_before=0, space_after=0, line=1.25, indent_first=False, hanging=False,
         keep_next=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if indent_first:
        pf.first_line_indent = Pt(size * 2)
    if hanging:
        # 题干换行后回退到题号右侧，不回到最左边（2 字符悬挂）
        pf.left_indent = Pt(size * 2)
        pf.first_line_indent = Pt(-size * 2)
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if keep_next:
        pf.keep_with_next = True
    if text:
        r = p.add_run(text)
        set_font(r, cn=cn, size=size, bold=bold)
    return p


def add_page_number_footer(doc):
    for section in doc.sections:
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run()
        set_font(r, size=9)
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        r._element.addnext(fld)


def _cjk_settings(doc):
    """打开 Word 中文版式的「标点溢出边界 / 允许标点压缩 / 中英文自动间距」。
    不开这几项时，行末的「。」容易把上一句的最后一两个字挤到下一行，出现「面。」这种孤行。"""
    el = doc.settings.element
    for tag in ("w:overflowPunct", "w:kinsoku", "w:autoSpaceDE", "w:autoSpaceDN", "w:adjustRightInd"):
        if el.find(qn(tag)) is None:
            node = OxmlElement(tag)
            el.append(node)


def new_doc():
    doc = Document()
    _cjk_settings(doc)
    s = doc.sections[0]
    # python-docx 默认模板是 Letter（21.6×27.9cm），中文卷子必须显式设成 A4（21.0×29.7cm），
    # 否则打印会被缩排或裁边
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(2.2)
    s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.0)
    s.right_margin = Cm(2.0)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    return doc


def head(doc, ex, answer=False):
    title = f"数学（人教版）{ex['book']}　{ex['paper']}"
    if answer:
        title += "　参考答案与评分标准"
    para(doc, title, size=16, bold=True, align="center", cn="黑体", space_after=4)
    para(doc, f"时间：{ex['duration']} 分钟　　满分：{ex['fullScore']} 分"
              + (f"　　范围：{'、'.join(ex.get('scope') or [])}" if answer else ""),
         size=10.5, align="center", space_after=6)
    if not answer:
        para(doc, "学校＿＿＿＿＿＿　班级＿＿＿＿＿＿　姓名＿＿＿＿＿＿　成绩＿＿＿＿＿＿",
             size=10.5, align="center", space_after=8)
    else:
        para(doc, "", space_after=4)


def render_paper(ex, path):
    doc = new_doc()
    head(doc, ex)
    for sec in ex["sections"]:
        rule = sec["rule"]
        # rule 形如「每小题 5 分，共 20 分（全部选对…）」时，两段要并进同一对括号，
        # 否则要么套成双层括号，要么标题与说明之间没有分隔符
        m = re.match(r"^(.*?)（(.+)）$", rule)
        head_txt = f"{sec['title']}（{m.group(1)}；{m.group(2)}）" if m else f"{sec['title']}（{rule}）"
        para(doc, head_txt, size=12, bold=True, cn="黑体",
             space_before=8, space_after=4, hanging=True, keep_next=True)
        items = sec["items"]
        # 小学/初中「计算」「直接写得数」这类纯算式题：同一前缀（如「直接写出得数：」）在每题重复 6 遍
        # 既啰嗦又占版面 ⇒ 提炼成一句导语，题目按 2–3 题一行紧凑排。
        lead = ""
        stems = [it["stem"] for it in items]
        m2 = re.match(r"^(.{4,12}：)", stems[0]) if stems else None
        if m2 and all(s.startswith(m2.group(1)) for s in stems):
            lead = m2.group(1)
            for it in items:
                it = dict(it)
            items = [dict(it, stem=it["stem"][len(lead):].strip()) for it in items]
        pure = all(len(it["stem"]) <= 22 and it["type"] not in ("choice", "multi", "solve") for it in items)
        compact = ("计算" in sec["title"] or "直接写得数" in sec["title"] or lead) and pure
        if compact:
            if lead:
                para(doc, lead, size=10.5, space_after=2, line=1.4)
            per_row = 3 if max((len(it["stem"]) for it in items), default=0) <= 12 else 2
            sep = "　　　　" if per_row == 3 else "　　　　　　"
            for i in range(0, len(items), per_row):
                para(doc, sep.join(f"{it['no']}．{it['stem']}" for it in items[i:i + per_row]),
                     size=10.5, space_after=4, line=1.7)
            continue
        for it in items:
            # 题干末尾若已自带「（　）」就不再补，否则会出现「（　）（　　）」
            raw = it["stem"].rstrip()
            need_blank = it["type"] in ("choice", "multi") and "（" not in raw[-4:]
            stem = f"{it['no']}．{raw}" + ("（　　）" if need_blank else "")
            para(doc, stem, size=10.5, space_after=2, line=1.4, hanging=True, keep_next=True)
            if it["type"] in ("choice", "multi"):
                opts = it["options"]
                # 选项里有长句时两列会顶到右边界、对不齐 ⇒ 按最长选项自适应：
                # 超过 10 个汉字就一列一项，否则两项一行
                longest = max(len(o["text"]) for o in opts)
                if longest > 10:
                    for i, o in enumerate(opts):
                        para(doc, f"　　{o['label']}．{o['text']}", size=10.5,
                             space_after=0, line=1.3, hanging=True,
                             keep_next=(i < len(opts) - 1))
                    para(doc, "", size=6, space_after=2)
                else:
                    para(doc, "　　".join(f"{o['label']}．{o['text']}" for o in opts[:2]),
                         size=10.5, space_after=0, line=1.3, hanging=True, keep_next=True)
                    para(doc, "　　".join(f"{o['label']}．{o['text']}" for o in opts[2:]),
                         size=10.5, space_after=4, line=1.3, hanging=True)
            elif it["type"] == "solve":
                blank = max(3, int(round(it["score"] / 6)) * 2)
                for _ in range(blank):
                    para(doc, "", size=10.5, space_after=0, line=1.6)
                para(doc, "", space_after=2)
            else:
                para(doc, "", space_after=4)
    add_page_number_footer(doc)
    doc.save(path)


def render_answer(ex, path):
    doc = new_doc()
    head(doc, ex, answer=True)
    for sec in ex["sections"]:
        para(doc, sec["title"], size=12, bold=True, cn="黑体", space_before=8, space_after=4)
        for it in sec["items"]:
            ans = it["answer"]
            line = f"{it['no']}．{ans}" if it["type"] != "solve" else f"{it['no']}．参考答案：{ans}"
            para(doc, line, size=10.5, bold=True, space_after=1, line=1.35)
            para(doc, f"解析：{it['analysis']}", size=10.5, space_after=1, line=1.35, indent_first=True)
            sr = it.get("scoreRule") or []
            if sr:
                para(doc, "评分标准：" + "；".join(sr), size=10.5, space_after=4, line=1.35)
    add_page_number_footer(doc)
    doc.save(path)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(glob.glob(f"{EXAM}/*/*.json"))
    if only:
        files = [f for f in files if f"/{only}/" in f]
    if not files:
        print("没有找到卷 JSON")
        return
    n = 0
    for f in files:
        ex = json.load(open(f, encoding="utf-8"))
        d = os.path.join(OUT_ROOT, ex["book"])
        os.makedirs(d, exist_ok=True)
        cap = os.path.abspath(f).split("/data/math/exams/")[-1]
        if ex["paper"] not in os.path.basename(f):
            print(f"⚠️ 文件名与 paper 不一致：{cap} → {ex['paper']}")
        p1 = os.path.join(d, f"{ex['paper']}_试卷.docx")
        p2 = os.path.join(d, f"{ex['paper']}_参考答案与评分标准.docx")
        render_paper(ex, p1)
        render_answer(ex, p2)
        n += 1
        print(f"✅ {ex['book']} / {ex['paper']}")
    print(f"\n共渲染 {n} 卷 × 2 份 docx → {OUT_ROOT}")


if __name__ == "__main__":
    main()
