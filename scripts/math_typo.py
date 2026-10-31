# -*- coding: utf-8 -*-
"""数学排版：把纯文本里的根式（√3、√(x+1)、2√6）渲染成**带横线（vinculum）的规范根号**。

文本层保持原样（`√3` 好读好维护），只在下游渲染时转换：
- docx：写成 OMML `<m:rad>`，Word 里是真正的根号（根指数省略，横线盖住被开方数）；
- HTML：写成 `<span class="rad"><span class="sq">√</span><span class="rd">3</span></span>`，
  配合 `.rd { border-top: … }` 出横线（learn.css 已有）。
"""
import re

# √ 后可跟括号组（中文括号也算），或一段 1–8 位的紧凑被开方数
RAD_RE = re.compile(
    r"√\s*(?:[\(（]([^()（）]{1,30})[\)）]|([0-9A-Za-z\u4e00-\u9fa5ππ·×°′″²³⁻⁺/．.]{1,8}))"
)

M_NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'


def segments(text):
    """切成 [(kind, value)]，kind ∈ {'text','rad'}；rad 的 value 是被开方数。"""
    out, pos = [], 0
    for m in RAD_RE.finditer(text or ""):
        if m.start() > pos:
            out.append(("text", text[pos:m.start()]))
        rad = (m.group(1) or m.group(2) or "").strip()
        out.append(("rad", rad))
        pos = m.end()
    if pos < len(text or ""):
        out.append(("text", text[pos:]))
    return out or [("text", text or "")]


def omml_rad(radicand):
    """返回一段 OMML 根号的 XML 字符串（根指数省略）。"""
    from xml.sax.saxutils import escape

    return (
        f"<m:oMath {M_NS}><m:rad><m:radPr><m:degHide m:val=\"1\"/></m:radPr><m:deg/>"
        f"<m:e><m:r><m:t xml:space=\"preserve\">{escape(radicand)}</m:t></m:r></m:e>"
        f"</m:rad></m:oMath>"
    )


def html_inline(text, esc):
    """把文本转成 HTML 片段；esc 是调用方提供的转义函数。"""
    buf = []
    for kind, val in segments(text):
        if kind == "text":
            buf.append(esc(val))
        else:
            buf.append(
                '<span class="rad"><span class="sq">√</span>'
                f'<span class="rd">{esc(val)}</span></span>'
            )
    return "".join(buf)
