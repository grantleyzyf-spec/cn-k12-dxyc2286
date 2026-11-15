# -*- coding: utf-8 -*-
"""把一册的学层精讲合成一本「合订本」docx（带目录、连续页码），放在 <册>/_合订本/ 下。

用法：python3 scripts/build_math_learn_booklet.py [册名]

`build_book(data, out)` 是纯渲染入口（不读环境、不拼路径）：main 与第 12 链的
「合订本版式同源」核验共用同一段渲染代码，避免核验器各抄一份后判据分叉。
"""
import glob, json, os, re, sys
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_math_learn_docx as B

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
BUCKET = os.environ.get("MATH_BUCKET", "math")
EDITION = os.environ.get("MATH_EDITION", "人教版")
LEARN = f"{REPO}/data/{BUCKET}/learn"
OUT_ROOT = os.path.expanduser(f"~/Desktop/学科图谱相关资料/学层精讲/{B.SUBJECT_NAME}/{EDITION}")


def build_book(data, out):
    """按现役版式渲染一册合订本到 out；无课时返回 None。"""
    book, lessons = data["book"], data.get("lessons") or []
    if not lessons:
        return None
    doc = B.new_doc()
    B.add_para(doc, f"{book} 学层精讲合订本", size=18, bold=True, cn="黑体", align="center", after=4)
    B.add_para(doc, f"{B.SUBJECT_NAME}（{EDITION}）· 共 {len(lessons)} 个课时 · 学生版", size=10, align="center", after=12, color="666666")
    B.add_para(doc, "目　录", size=13, bold=True, cn="黑体", align="center", after=6)
    for i, L in enumerate(lessons, 1):
        B.add_para(doc, f"{i}. {L.get('title') or L.get('name') or ''}", size=10.5, left=0.8, after=2)
    for idx, L in enumerate(lessons):
        _t = L.get("title") or L.get("name") or ""      # 华东师大版学层 JSON 用 name 而非 title
        _tp = B.add_para(doc, _t, size=15, bold=True, cn="黑体", align="center", after=2)
        # 分页必须用「段前分页」，不能用 add_page_break()：后者每次多插一个只含分页符的空段落，
        # 上一课时恰好排满整页时，这个空段落自己就占掉一整页 ⇒ 空白页（2026-11-15 实测 79 本合订本、65 处）。
        _tp.paragraph_format.page_break_before = True     # idx=0 时同样从新页起（= 原 TOC 后分页）
        B.add_para(doc, "学生版精讲 · 先读课本原文，再用大白话拆开，最后自查", size=9,
                   align="center", after=2, color="888888")   # 与单份讲解副题同源
        B.add_para(doc, f"（{len(re.findall(r'[一-龥]', L['markdown']))} 字）", size=8.5,
                   align="center", after=8, color="888888")
        for raw in L["markdown"].split("\n"):
            ln = raw.rstrip()
            if not ln.strip():
                continue
            if ln.startswith("# "):
                _h1 = ln[2:].strip()
                if _h1 == _t.strip():
                    continue          # 一级标题与课时名相同 ⇒ 已作为课时标题
                B.add_para(doc, _h1, size=11.5, bold=True, cn="黑体", align="center", before=2, after=6)
                continue
            if ln.startswith("## "):
                B.add_para(doc, ln[3:].strip(), size=12, bold=True, cn="黑体", before=9, after=5)
            elif ln.startswith("### "):
                B.add_para(doc, ln[4:].strip(), size=11, bold=True, cn="黑体", before=6, after=3)
            elif ln.startswith("> "):
                body = ln[2:].strip()
                is_q = body[:1] not in "❌✅"
                B.add_para(doc, body, size=10.5, left=0.7 if is_q else 0.4,
                           right=0.7 if is_q else 0, before=2, after=4,
                           shaded="F2F2F2" if is_q else None)
            elif ln.startswith("- [ ]"):
                B.add_para(doc, "☐ " + ln[5:].strip(), size=10.5, left=0.6, after=2)
            elif ln.startswith("- "):
                B.add_para(doc, "• " + ln[2:].strip(), size=10.5, left=0.6, after=2)
            else:
                B.add_para(doc, ln, size=10.5, after=4, first=21)
    p0 = doc.sections[0].footer.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = p0.add_run()
    B.set_font(r0, size=9)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r0._element.addnext(fld)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc.save(out)
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(glob.glob(f"{LEARN}/*.json"))
    files = [f for f in files if not os.path.basename(f).startswith("_")]   # 跳过 _ocr_waivers.json 等台账
    if only:
        files = [f for f in files if os.path.basename(f)[:-5] == only]
    for f in files:
        data = json.load(open(f, encoding="utf-8"))
        book, lessons = data["book"], data.get("lessons") or []
        if not lessons:
            continue
        out = os.path.join(OUT_ROOT, book, "_合订本", f"{book}_学层精讲合订本.docx")
        build_book(data, out)
        print(f"✅ {book}：{len(lessons)} 课时 → {out}")


if __name__ == "__main__":
    main()
