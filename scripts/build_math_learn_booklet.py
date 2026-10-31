# -*- coding: utf-8 -*-
"""把一册的学层精讲合成一本「合订本」docx（带目录、连续页码），放在 <册>/_合订本/ 下。

用法：python3 scripts/build_math_learn_booklet.py [册名]
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
LEARN = f"{REPO}/data/math/learn"
OUT_ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料/学层精讲/数学/人教版")


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
        doc = B.new_doc()
        B.add_para(doc, f"{book} 学层精讲合订本", size=18, bold=True, cn="黑体", align="center", after=4)
        B.add_para(doc, f"数学（人教版）· 共 {len(lessons)} 个课时 · 学生版", size=10, align="center", after=12, color="666666")
        B.add_para(doc, "目　录", size=13, bold=True, cn="黑体", align="center", after=6)
        for i, L in enumerate(lessons, 1):
            B.add_para(doc, f"{i}. {L['title']}", size=10.5, left=0.8, after=2)
        doc.add_page_break()
        for idx, L in enumerate(lessons):
            if idx:
                doc.add_page_break()
            B.add_para(doc, L["title"], size=15, bold=True, cn="黑体", align="center", after=2)
            B.add_para(doc, f"（{len(re.findall(r'[一-龥]', L['markdown']))} 字）", size=8.5,
                       align="center", after=8, color="888888")
            for raw in L["markdown"].split("\n"):
                ln = raw.rstrip()
                if not ln.strip() or ln.startswith("# "):
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
        d = os.path.join(OUT_ROOT, book, "_合订本")
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, f"{book}_学层精讲合订本.docx")
        doc.save(out)
        print(f"✅ {book}：{len(lessons)} 课时 → {out}")


if __name__ == "__main__":
    main()
