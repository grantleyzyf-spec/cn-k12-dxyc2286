# -*- coding: utf-8 -*-
"""生成三份「排版样张」（化学 / 物理 / 生物）+ 一份 HTML 预览，用来目视验收 typo-spec。

用法：python3 scripts/build_typo_samples.py
输出：~/Desktop/学科图谱相关资料/排版样张/<学科>排版样张.docx
      ~/Desktop/学科图谱相关资料/排版样张/index.html
"""
import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import subject_typo  # noqa: E402

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = os.path.expanduser("~/Desktop/学科图谱相关资料/排版样张")

CASES = {
    "chemistry": {
        "title": "化学 · 公式与符号排版样张",
        "lines": [
            ("课本原文式", "水通电分解：2H2O ->[通电] 2H2 + O2↑，正极产生 O2，负极产生 H2。"),
            ("化学式与下标", "常见物质：H2O、CO2、CaCO3、Fe3O4、C6H12O6；配平后 3Fe + 2O2 ->[点燃] Fe3O4。"),
            ("离子与电荷", "溶液中含有 SO4^2- 与 Fe^3+；检验 CO3^2- 可用稀盐酸。"),
            ("可逆与条件", "合成氨：N2 + 3H2 <=>[催化剂] 2NH3；碳酸钙分解：CaCO3 ->[高温] CaO + CO2↑。"),
            ("不该转的情形", "ATP、DNA 这类缩写不是化学式，保持原样；单个元素 O 也不加下标。"),
        ],
    },
    "physics": {
        "title": "物理 · 公式与符号排版样张",
        "lines": [
            ("量符号斜体", "设物体的质量为 m，速度为 v，则动量 p＝mv。"),
            ("单位正体", "汽车在平直公路上以 15 m/s 行驶，加速度为 2 m/s^2，牵引力做的功为 300 N·m。"),
            ("单位与数值空格", "重力加速度取 9.8 m/s^2；密度 1.0×10^3 kg/m^3；功率 60 W。"),
            ("复合单位", "电功 1 kW·h 等于 3.6×10^6 J；电阻 20 Ω 时电流 0.5 A。"),
            ("不该转的情形", "走了 3 步不算单位；pH 与 DNA 这类写法保持正体。"),
        ],
    },
    "biology": {
        "title": "生物 · 符号与命名排版样张",
        "lines": [
            ("基因符号斜体", "TP53 基因突变与多种肿瘤相关；BRCA1 参与 DNA 损伤修复。"),
            ("蛋白名正体", "p53 蛋白积累后启动细胞凋亡；检测到 BRCA1 蛋白表达升高。"),
            ("核酸缩写正体", "DNA 复制发生在分裂间期，mRNA 由 DNA 转录而来，ATP 供能。"),
            ("遗传比例", "杂合子自交，子代中隐性性状占 1/4，基因型为 aa 的占 1/4。"),
            ("不该转的情形", "选项 A 正确；pH 值不影响本实验结论。"),
        ],
    },
}


def set_font(run, cn="宋体", size=10.5, bold=False, en="Times New Roman"):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)


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
    return doc


def rich_para(doc, text, subject, size=10.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    for kind, val, ital in subject_typo.docx_segments(text, subject):
        if kind == "text":
            r = p.add_run(val)
            set_font(r, size=size)
            r.font.italic = bool(ital)
        else:
            p._p.append(parse_xml(val))
    return p


def real_lines(subject, n=2):
    """从本学科题库里挑含公式/单位/基因的真实句子，证明不是假数据。"""
    path = f"{REPO}/data/{subject}/questions.json"
    if not os.path.exists(path):
        return []
    items = json.load(open(path, encoding="utf-8"))
    items = items if isinstance(items, list) else items.get("questions", [])
    pat = {"chemistry": r"[A-Z][a-z]?\d|→|↑|↓",
           "physics": r"m/s|kg|N·m|J|Ω|Pa",
           "biology": r"[A-Z]{2,}\d|DNA|RNA|ATP"}.get(subject, r".")
    out = []
    for it in items:
        for key in ("prompt", "question", "explanation"):
            t = (it.get(key) or "").strip()
            if t and re.search(pat, t):
                out.append(t[:120])
                break
        if len(out) >= n:
            break
    return out


def build_docx(subject, spec):
    doc = new_doc()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(spec["title"])
    set_font(r, cn="黑体", size=16, bold=True)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("按 docs/typo-spec.md 渲染 · 左列说明规则，右列是实际排版")
    set_font(r2, size=9)
    r2.font.color.rgb = None

    for label, text in spec["lines"]:
        ph = doc.add_paragraph()
        ph.paragraph_format.space_before = Pt(8)
        rh = ph.add_run(f"【{label}】")
        set_font(rh, cn="黑体", size=11, bold=True)
        rich_para(doc, text, subject)

    real = real_lines(subject)
    if real:
        ph = doc.add_paragraph()
        ph.paragraph_format.space_before = Pt(10)
        rh = ph.add_run("【本学科题库真实句子（原文渲染）】")
        set_font(rh, cn="黑体", size=11, bold=True)
        for t in real:
            rich_para(doc, t, subject, size=10)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{subject}排版样张.docx")
    doc.save(path)
    return path


def build_html(paths):
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = []
    for subject, spec in CASES.items():
        body.append(f"<h2>{spec['title']}</h2>")
        for label, text in spec["lines"]:
            body.append(f"<p class='label'>【{label}】</p>")
            body.append(f"<p class='line'>{subject_typo.html_inline(text, esc, subject)}</p>")
        for t in real_lines(subject):
            body.append(f"<p class='line real'>{subject_typo.html_inline(t, esc, subject)}</p>")
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>学科排版样张</title>
<link rel="stylesheet" href="../../../cn-k12-dxyc2286/assets/site.css">
<style>
body{{max-width:900px;margin:24px auto;padding:0 18px;font-size:15.5px;line-height:1.85}}
h2{{margin:26px 0 10px;font-size:19px;border-left:3px solid #0f6e62;padding-left:10px}}
.label{{margin:12px 0 2px;font-size:12.5px;color:#6b7a88}}
.line{{margin:0 0 8px}}
.real{{color:#0a4c44}}
.chem sub,.chem sup{{font-size:.72em}}
.rxn{{display:inline-flex;flex-direction:column;align-items:center;vertical-align:middle;margin:0 .2em;line-height:1}}
.rxn .cond{{font-size:.7em;margin-bottom:-.15em}}
.rxn .arw{{font-size:1em}}
.unit{{font-style:normal;font-family:"Times New Roman",serif}}
.qty,.gene{{font-style:italic}}
</style></head><body>
<h1>学科公式与符号排版样张</h1>
<p>对应规范：<code>docs/typo-spec.md</code>；实现：<code>scripts/subject_typo.py</code>。
本页与 Word 样张同源（同一份文本、同一套规则），用来核对“两个通道排出来是否一致”。</p>
{''.join(body)}
</body></html>"""
    p = os.path.join(OUT, "index.html")
    open(p, "w", encoding="utf-8").write(html)
    return p


def main():
    paths = []
    for subject, spec in CASES.items():
        paths.append(build_docx(subject, spec))
    paths.append(build_html(paths))
    for p in paths:
        print("✅", p)


if __name__ == "__main__":
    main()
