# -*- coding: utf-8 -*-
"""数学排版：把纯文本里的**根式**与**分数**渲染成规范排版。

文本层保持原样（`√3`、`2√6`、`3/8` 好读好改好检索），只在下游渲染时转换：
- docx：写成 OMML —— 根号 `<m:rad>`、分数 `<m:f>`，Word 里就是印刷体的根号与上下叠分式；
- HTML：`.rad/.rd`（横线靠 border-top）、`.frac/.num/.den`（叠行加分数线）。

识别口径（宁少不错）：
- 根式：`√3`、`2√6`、`√(x+1)`、`√500`
- 分数：分子/分母**至少一侧是数字或 π**，如 `3/8`、`1.5/2`、`π/2`、`x/3`、`(a+b)/2`；
  `a/b` 这类纯字母比不转（单位 `km/h`、`吨/小时` 也自动排除）；
  `√3/2` 不转（√ 的范围有歧义，交给正文说清）；日期 `2026/11/01` 不转。
"""
import re

# √ 后可跟括号组（中文括号也算），或一段 1–8 位的紧凑被开方数
RAD_RE = re.compile(
    r"√\s*(?:[\(（]([^()（）]{1,30})[\)）]|([0-9A-Za-z\u4e00-\u9fa5ππ·×°′″²³⁻⁺/．.]{1,8})(\^[0-9]{1,2})?)"
)

_NUM = r"(?:\d+(?:\.\d+)?[²³]?|π|[a-zA-Z]|\([^()（）]{1,14}\)|[²³])"
# 分数：两侧都不能是中文（排除「吨/小时」），且不被数字或斜杠包住（排除日期）
FRAC_RE = re.compile(rf"(?<![\d/√])({_NUM})\s*/\s*({_NUM})(?![\d/])")

# 向量：中文「向量」后跟 1–4 个拉丁字母/数字（向量 OA、向量AB、向量a），箭头加在字母上方
VEC_RE = re.compile(r"(向量)\s*([A-Za-z][A-Za-z0-9]{0,3})")

M_NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'


def _numlike(s):
    s = (s or "").strip()
    return bool(s) and (s[0].isdigit() or s[0] == "π")


def _frac_ok(a, b):
    a, b = (a or "").strip(), (b or "").strip()
    if not a or not b:
        return False
    if not (_numlike(a) or _numlike(b)):
        return False
    if len(a) == 1 and len(b) == 1 and a.isalpha() and b.isalpha():
        return False
    return True


def segments(text):
    """切成 [(kind, value)]；kind ∈ {'text','rad','frac','vec'}，frac 的 value 是 (分子, 分母)。"""
    text = text or ""
    toks = []
    for m in VEC_RE.finditer(text):
        # 只把字母部分包成向量，前面的「向量」二字原样保留
        toks.append(("text", m.start(), m.start(2), m.group(1)))
        toks.append(("vec", m.start(2), m.end(2), m.group(2)))
    for m in RAD_RE.finditer(text):
        rad = (m.group(1) or m.group(2) or "").strip()
        if m.group(3):                      # √a^2 里的 ^2 属于被开方数，不能留在根号外
            rad += m.group(3)
        toks.append(("rad", m.start(), m.end(), rad))
    for m in FRAC_RE.finditer(text):
        if _frac_ok(m.group(1), m.group(2)):
            toks.append(("frac", m.start(), m.end(), (m.group(1), m.group(2))))
    toks.sort(key=lambda t: (t[1], -(t[2] - t[1])))     # 靠前优先，同起点取更长
    out, last = [], 0
    for kind, s, e, val in toks:
        if s < last:
            continue
        if s > last:
            out.append(("text", text[last:s]))
        out.append((kind, val))
        last = e
    if last < len(text):
        out.append(("text", text[last:]))
    return out or [("text", text)]


SUP_IN = re.compile(r"\^(-?\d{1,2})")


def radicand_parts(radicand):
    """被开方数内部再拆：a^2 → [('t','a'),('sup','2')]；9/2 → [('frac',('9','2'))]。
    根号划线必须完整盖住整个被开方数，里面还带幂/分数时也必须画在根号里面。"""
    out = []
    for seg in re.split(r"(\^\-?\d{1,2})", radicand or ""):
        if not seg:
            continue
        if seg.startswith("^"):
            out.append(("sup", seg[1:]))
            continue
        m = FRAC_RE.search(seg)
        if m and _frac_ok(m.group(1), m.group(2)):
            if seg[:m.start()]:
                out.append(("t", seg[:m.start()]))
            out.append(("frac", (m.group(1), m.group(2))))
            if seg[m.end():]:
                out.append(("t", seg[m.end():]))
        else:
            out.append(("t", seg))
    # 幂次必须挂在**前一个字符**上：OMML 里空基座的 sSup 会被渲染成空白方框
    merged = []
    for kind, val in out:
        if kind == "sup" and merged and merged[-1][0] == "t" and merged[-1][1]:
            prev = merged[-1][1]
            merged[-1] = ("t", prev[:-1])
            if not prev[:-1]:
                merged.pop()
            merged.append(("tsup", (prev[-1], val)))
        else:
            merged.append((kind, val))
    return merged or [("t", radicand or "")]


def _omml_runs(parts):
    from xml.sax.saxutils import escape
    xml = []
    for kind, val in parts:
        if kind == "t":
            xml.append(f'<m:r><m:t xml:space="preserve">{escape(val)}</m:t></m:r>')
        elif kind == "tsup":
            base, exp = val
            xml.append(
                f'<m:sSup><m:sSupPr/><m:e><m:r><m:t>{escape(base)}</m:t></m:r></m:e>'
                f'<m:sup><m:r><m:t>{escape(exp)}</m:t></m:r></m:sup></m:sSup>'
            )
        else:
            xml.append(
                f'<m:f><m:fPr><m:type m:val="bar"/></m:fPr>'
                f'<m:num><m:r><m:t>{escape(val[0])}</m:t></m:r></m:num>'
                f'<m:den><m:r><m:t>{escape(val[1])}</m:t></m:r></m:den></m:f>'
            )
    return "".join(xml)


def omml_rad(radicand):
    """OMML 根号（根指数省略，横线盖住整个被开方数）。"""
    return (
        f'<m:oMath {M_NS}><m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/>'
        f"<m:e>{_omml_runs(radicand_parts(radicand))}</m:e>"
        f"</m:rad></m:oMath>"
    )


def omml_frac(num, den):
    """OMML 分数（横线型分式，上下叠排）。"""
    from xml.sax.saxutils import escape

    return (
        f"<m:oMath {M_NS}><m:f><m:fPr><m:type m:val=\"bar\"/></m:fPr>"
        f"<m:num><m:r><m:t xml:space=\"preserve\">{escape(num)}</m:t></m:r></m:num>"
        f"<m:den><m:r><m:t xml:space=\"preserve\">{escape(den)}</m:t></m:r></m:den>"
        f"</m:f></m:oMath>"
    )


def omml_vec(letters):
    """OMML 向量（字母上加右箭头，即 \\overrightarrow{AB}）。"""
    from xml.sax.saxutils import escape

    return (
        f"<m:oMath {M_NS}><m:acc><m:accPr><m:chr m:val=\"⃗\"/></m:accPr>"
        f"<m:e><m:r><m:t xml:space=\"preserve\">{escape(letters)}</m:t></m:r></m:e>"
        f"</m:acc></m:oMath>"
    )


def html_inline(text, esc):
    """把文本转成 HTML 片段；esc 是调用方提供的转义函数。"""
    buf = []
    for kind, val in segments(text):
        if kind == "text":
            buf.append(esc(val))
        elif kind == "rad":
            buf.append(
                '<span class="rad"><span class="sq">√</span>'
                f'<span class="rd">{esc(val)}</span></span>'
            )
        elif kind == "vec":
            buf.append(f'<span class="vec">{esc(val)}</span>')
        else:
            num, den = val
            buf.append(
                '<span class="frac"><span class="num">' + esc(num) + '</span>'
                '<span class="den">' + esc(den) + '</span></span>'
            )
    return "".join(buf)
