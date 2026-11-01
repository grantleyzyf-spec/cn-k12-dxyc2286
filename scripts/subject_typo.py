# -*- coding: utf-8 -*-
"""学科公式与符号的渲染层（数学 / 物理 / 化学 / 生物）。

契约见 `docs/typo-spec.md`。文本层保持纯文本，本模块只负责**渲染**：

- 数学：根号（横线覆盖）、分数（上下叠排）、向量（字母上箭头）—— 复用 `math_typo`
- 化学：化学式数字下标、电荷上标、反应箭头（条件置箭头上方）
- 物理：量符号斜体、单位符号正体（白名单）
- 生物：基因符号斜体（白名单排除 DNA/RNA/ATP 等缩写）

对外 4 个入口：
    segments(text, subject)          → [(kind, value, italic?)]
    docx_segments(text, subject)     → [("text", s, italic) | ("xml", xml)]
    html_inline(text, esc, subject)  → HTML 片段
    （数学三类的 OMML 仍由 math_typo 提供，这里只做调度）

设计原则（宁可少转，不可错转）：
- 化学式要求 ≥2 个元素组，且元素符号在真实元素表里；
- 单位只认 SI 词头 + SI 单位白名单；
- 量符号只认「单个拉丁字母」紧邻关系符或出现在「设/求/记…为」之后；
- 基因只认「大写字母+数字」且不在缩写排除表里。
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math_typo  # noqa: E402

# ---------------------------------------------------------------- 词表

ELEMENTS = set("""
H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn
Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce
Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn
Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl
Mc Lv Ts Og
""".split())

UNITS = set("""
m g s A K mol cd rad sr Hz N Pa J W C V F S Wb T H lm lx Bq Gy Sv kat
L l t min h d ha bar eV u
""".split())
PREFIXES = ["Y", "Z", "E", "P", "T", "G", "M", "k", "h", "da", "d", "c", "m",
            "μ", "n", "p", "f", "a", "z", "y"]
UNIT_EXTRA = {"Ω", "°C", "°F", "%"}

# 缩写白名单：永不斜体、永不当下标处理
ABBR_NO_ITALIC = set("""
DNA RNA mRNA tRNA rRNA ATP ADP AMP GDP GTP NAD NADH NADPH FAD pH PCR ELISA ICU CT MRI
B超 GPS USB CPU AI PDF PPT LED UV IR X光 AA BB Aa Bb
""".split())

# ------------------------------------------------------------------ 正则

# 化学式：可带前导系数，≥2 个元素组，可带 ^电荷
CHEM_RE = re.compile(
    r"(?<![A-Za-z0-9])("
    r"\d{0,2}(?:[A-Z][a-z]?\d*){2,}(?:\^\d{0,2}[+\-])?"      # 多元素化学式，可带电荷
    r"|\d{0,2}[A-Z][a-z]?\d+"                                      # 单质分子：O2、H2、2Cl2
    r"|(?:[A-Z][a-z]?)\^\d{0,2}[+\-]"                            # 单元素离子：Fe^3+、Cl^-
    r")(?![A-Za-z0-9])"
)
# 反应箭头：-> / → / <=> / ⇌，可选 [条件]
RXN_RE = re.compile(r"(<=>|->|→|⇌)\s*(?:\[([^\]]{1,12})\])?")

# 通用上标：m/s^2、10^-3、x^2（幂次一律排成上标）
SUP_RE = re.compile(r"([A-Za-z0-9\)\]）]+)\^(-?\d{1,2})(?![\d])")
# 单位表达式：数字后的单位链，允许与数字紧贴（渲染时补一个空格）
UNIT_RE = re.compile(
    r"(?<=\d)(\s?)([A-Za-zμΩ°]{1,4}(?:\^?[²³]|\^-?\d)?(?:[/·][A-Za-zμΩ]{1,4}(?:\^?[²³]|\^-?\d)?)*)"
)

# 量符号：单个拉丁字母，紧邻关系符；或「设/求/记 … 为」之间的字母
QTY_BEFORE_OP = re.compile(r"(?<![\w\u4e00-\u9fa5])([A-Za-z])(?=\s*[=＝≈≤≥<>×/])")
QTY_AFTER_OP = re.compile(r"(?<=[=＝≈≤≥<>×/]\s)([A-Za-z])(?![\w])")
# 中文名 + 量符号：质量为 m / 速度 v / 设 x / 求 y（物理最常见的写法）
QTY_CN = re.compile(
    r"(?:质量|速度|加速度|力|压力|密度|时间|长度|温度|压强|功率|功|电压|电流|电阻|"
    r"动量|热量|比热容|电阻率|位移|路程|频率|周期|波长|质量分数)(?:为|是|记为|记作)?\s*([A-Za-z])(?![A-Za-z0-9])"
)
QTY_DEF = re.compile(r"(?:设|求|记|令|得)\s*([A-Za-z])(?![A-Za-z0-9])")
# 等号后紧跟字母（不空格的写法：p＝mv）
QTY_AFTER_EQ = re.compile(r"(?<=[=＝])([A-Za-z]{1,2})(?![A-Za-z0-9])")   # p＝mv 这类连写也算量符号

# 基因符号：TP53 / BRCA1 / p53（排除缩写表）
GENE_RE = re.compile(r"(?<![\w\u4e00-\u9fa5])((?:[A-Z]{2,}[0-9]{1,3}[A-Za-z]?)|p[0-9]{2,3})(?![\w\u4e00-\u9fa5])")

# ------------------------------------------------ 化学式解析与 OMML

def chem_tokens(formula):
    """把 H2SO4 / 2H2O2 / SO4^2- 拆成 [(kind, text)]，kind ∈ {coef, el, sub, sup}。"""
    out = []
    m = re.match(r"^(\d{0,2})(.*?)(\^\d{0,2}[+\-])?$", formula)
    coef, body, charge = m.group(1), m.group(2), m.group(3) or ""
    if coef:
        out.append(("coef", coef))
    for em in re.finditer(r"([A-Z][a-z]?)(\d*)", body):
        out.append(("el", em.group(1)))
        if em.group(2):
            out.append(("sub", em.group(2)))
    if charge:
        out.append(("sup", charge[1:].replace("-", "−")))
    return out


def _valid_chem(formula):
    """化学式合法性：元素必须真存在；单元素只有带下标（H2/O2）或带电荷（Fe^3+）才算化学式。"""
    toks = chem_tokens(formula)
    els = [t[1] for t in toks if t[0] == "el"]
    if not els or any(e not in ELEMENTS for e in els):
        return False
    if len(els) >= 2:
        return True
    return any(t[0] in ("sub", "sup") for t in toks)


def omml_chem(formula):
    """化学式的 OMML。

    坑：<m:sSub><m:e/>…</m:e> 这种「空基座」在 Word/LibreOffice 里会被渲染成占位方框，
    所以下标必须挂到**前一个元素符号**上，上标（电荷）挂到它前面的元素上。
    """
    from xml.sax.saxutils import escape

    def run(t):
        return f'<m:r><m:t xml:space="preserve">{escape(t)}</m:t></m:r>'

    parts = []
    pending = None          # 尚未输出的元素符号
    last_el = None          # 最近的元素符号（下标输出后仍保留，供电荷当基座）
    for kind, txt in chem_tokens(formula):
        if kind in ("el", "coef"):
            if pending:
                parts.append(run(pending))
            pending = txt
            if kind == "el":
                last_el = txt
        elif kind == "sub":
            parts.append(
                f'<m:sSub><m:sSubPr/><m:e>{run(pending or last_el or "")}</m:e>'
                f'<m:sub>{run(txt)}</m:sub></m:sSub>'
            )
            pending = None
        elif kind == "sup":
            parts.append(
                f'<m:sSup><m:sSupPr/><m:e>{run(pending or last_el or "")}</m:e>'
                f'<m:sup>{run(txt)}</m:sup></m:sSup>'
            )
            pending = None
    if pending:
        parts.append(run(pending))
    return f"<m:oMath {math_typo.M_NS}>{''.join(parts)}</m:oMath>"


def omml_sup(_base, exp):
    """独立上标：OMML 里 sSup 必须有基座，空基座会渲染成方框；
    这里改用带 vertAlign=superscript 的普通文字 run（在段落里就是右上标）。"""
    from xml.sax.saxutils import escape
    return (
        '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(exp)}</w:t></w:r>'
    )


def omml_rxn(val=("→", None)):
    """反应箭头；有条件时用 m:limUpp 把条件放到箭头上方。val=(箭头, 条件)。"""
    from xml.sax.saxutils import escape
    arrow, cond = val if isinstance(val, tuple) else ("→", val)
    if not cond:
        return (f'<m:oMath {math_typo.M_NS}><m:r><m:t>{arrow}</m:t></m:r></m:oMath>')
    return (
        f'<m:oMath {math_typo.M_NS}><m:limUpp><m:limUppPr/>'
        f'<m:e><m:r><m:t>{arrow}</m:t></m:r></m:e>'
        f'<m:lim><m:r><m:t>{escape(cond)}</m:t></m:r></m:lim></m:limUpp></m:oMath>'
    )


def unit_parts(expr):
    """m/s^2 → [('m/s', '2')]；N·m → [('N·m', None)]。返回 [(文本, 幂次或 None)]。"""
    out, buf, i = [], "", 0
    while i < len(expr):
        ch = expr[i]
        if ch in "^²³":
            if ch == "^":
                j = i + 1
                num = ""
                while j < len(expr) and (expr[j].isdigit() or expr[j] == "-"):
                    num += expr[j]
                    j += 1
                out.append((buf, num.replace("-", "−")))
                buf, i = "", j
                continue
            out.append((buf, "2" if ch == "²" else "3"))
            buf, i = "", i + 1
            continue
        buf += ch
        i += 1
    if buf:
        out.append((buf, None))
    return out


# ------------------------------------------------------------ 判定辅助

def _unit_ok(expr):
    """单位链校验：拆词头后必须在白名单里。"""
    def one(tok):
        core = re.sub(r"(\^-?\d|[²³])$", "", tok)
        if core in UNITS or core in UNIT_EXTRA:
            return True
        for p in PREFIXES:
            if core.startswith(p) and core[len(p):] in UNITS:
                return True
        return False
    parts = re.split(r"[/·]", expr)
    return all(one(p) for p in parts if p)


# ------------------------------------------------------------ 主解析

def segments(text, subject="math"):
    """返回 [(kind, value, italic)]；kind ∈ {text, rad, frac, vec, chem, rxn, unit, qty, gene}。"""
    text = text or ""
    subj = (subject or "math").lower()
    toks = []

    # 数学三类（所有学科都可能有根号/分数/向量）
    for m in math_typo.VEC_RE.finditer(text):
        toks.append(("text", m.group(1), False, m.start(), m.start(2)))
        toks.append(("vec", m.group(2), False, m.start(2), m.end(2)))
    for m in math_typo.RAD_RE.finditer(text):
        toks.append(("rad", (m.group(1) or m.group(2) or "").strip(), False, m.start(), m.end()))
    for m in math_typo.FRAC_RE.finditer(text):
        if math_typo._frac_ok(m.group(1), m.group(2)):
            toks.append(("frac", (m.group(1), m.group(2)), False, m.start(), m.end()))
    for m in SUP_RE.finditer(text):
        toks.append(("sup", (m.group(1), m.group(2).replace("-", "−")), False, m.start(), m.end()))

    if subj == "chemistry":
        for m in RXN_RE.finditer(text):
            raw, cond = m.group(1), m.group(2)
            arrow = "⇌" if raw in ("<=>", "⇌") else "→"
            toks.append(("rxn", (arrow, cond), False, m.start(), m.end()))
        for m in CHEM_RE.finditer(text):
            if _valid_chem(m.group(1)):
                toks.append(("chem", m.group(1), False, m.start(), m.end()))
    elif subj == "physics":
        for m in UNIT_RE.finditer(text):
            if _unit_ok(m.group(2)):
                toks.append(("unit", m.group(2), False, m.start(2), m.end(2)))
        for rx in (QTY_BEFORE_OP, QTY_AFTER_OP, QTY_CN, QTY_DEF, QTY_AFTER_EQ):
            for m in rx.finditer(text):
                if m.group(1) in ABBR_NO_ITALIC:
                    continue
                toks.append(("qty", m.group(1), True, m.start(1), m.end(1)))
    elif subj == "biology":
        for m in GENE_RE.finditer(text):
            if m.group(1) in ABBR_NO_ITALIC:
                continue
            # 「p53 蛋白」说的是蛋白名，按规范排正体（基因符号才斜体）
            tail = text[m.end(1):m.end(1) + 5].lstrip(" 　")
            if tail.startswith("蛋白") or tail.lower().startswith(" protein"):
                continue
            toks.append(("gene", m.group(1), True, m.start(1), m.end(1)))

    toks.sort(key=lambda t: (t[3], -(t[4] - t[3])))
    out, last = [], 0
    for kind, val, ital, s, e in toks:
        if s < last:
            continue
        if s > last:
            out.append(("text", text[last:s], False))
        out.append((kind, val, ital))
        last = e
    if last < len(text):
        out.append(("text", text[last:], False))
    return out or [("text", text, False)]


# ------------------------------------------------------------ docx 输出

def docx_segments(text, subject="math"):
    """给 python-docx 用：统一三元组 —— ('text', 字符串, 是否斜体) 或 ('xml', OMML 字符串, False)。"""
    out = []
    for kind, val, ital in segments(text, subject):
        if kind == "text":
            out.append(("text", val, ital))
        elif kind == "rad":
            out.append(("xml", math_typo.omml_rad(val), False))
        elif kind == "frac":
            out.append(("xml", math_typo.omml_frac(val[0], val[1]), False))
        elif kind == "vec":
            out.append(("xml", math_typo.omml_vec(val), False))
        elif kind == "chem":
            out.append(("xml", omml_chem(val), False))
        elif kind == "rxn":
            out.append(("xml", omml_rxn(val), False))
        elif kind == "unit":
            if out and out[-1][0] == "text" and not out[-1][1].endswith(" "):
                out.append(("text", " ", False))
            for t, exp in unit_parts(val):
                if exp is None:
                    out.append(("text", t, False))
                else:
                    out.append(("text", t, False))
                    out.append(("xml", omml_sup("", exp), False))
        elif kind == "sup":
            out.append(("text", val[0], False))
            out.append(("xml", omml_sup("", val[1]), False))
        elif kind in ("qty", "gene"):
            out.append(("text", val, ital))
    return out


# ------------------------------------------------------------ HTML 输出

def html_inline(text, esc, subject="math"):
    buf = []
    for kind, val, ital in segments(text, subject):
        if kind == "text":
            buf.append(esc(val))
        elif kind == "rad":
            buf.append('<span class="rad"><span class="sq">√</span>'
                       f'<span class="rd">{esc(val)}</span></span>')
        elif kind == "frac":
            buf.append('<span class="frac"><span class="num">' + esc(val[0]) + '</span>'
                       '<span class="den">' + esc(val[1]) + '</span></span>')
        elif kind == "vec":
            buf.append(f'<span class="vec">{esc(val)}</span>')
        elif kind == "chem":
            html = ""
            for k, t in chem_tokens(val):
                if k == "sub":
                    html += f"<sub>{esc(t)}</sub>"
                elif k == "sup":
                    html += f"<sup>{esc(t)}</sup>"
                else:
                    html += esc(t)
            buf.append(f'<span class="chem">{html}</span>')
        elif kind == "rxn":
            arrow, cond = val
            c = f'<span class="cond">{esc(cond)}</span>' if cond else ""
            buf.append(f'<span class="rxn">{c}<span class="arw">{arrow}</span></span>')
        elif kind == "unit":
            parts = "".join(
                (esc(t) if exp is None else esc(t) + f"<sup>{esc(exp)}</sup>")
                for t, exp in unit_parts(val)
            )
            space = "" if (buf and buf[-1].endswith(" ")) else " "
            buf.append(f'{space}<span class="unit">{parts}</span>')
        elif kind == "sup":
            buf.append(f'{esc(val[0])}<sup>{esc(val[1])}</sup>')
        elif kind == "qty":
            buf.append(f'<i class="qty">{esc(val)}</i>')
        elif kind == "gene":
            buf.append(f'<i class="gene">{esc(val)}</i>')
    return "".join(buf)
