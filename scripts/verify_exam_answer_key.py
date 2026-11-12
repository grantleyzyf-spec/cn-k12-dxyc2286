#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数学原创试卷「答案键」独立机检（第 10 链）。

与第 7 链 `verify_math_exam_arithmetic.py` 分工：第 7 链只复算「算式直接给值」的口算/计算题；
本链补三块它不覆盖、且**不依赖讲解稿**的面（讲解与卷同错时第 9 链会一起放过，本链不会）：

  A 选择结构不变量（choice/multi）：必须有 options；标签唯一；answer 每个字母都在标签里；
    单选只一个字母、多选至少两个；选项文本非空且互不重复。
  B 题干泄答案：空（括号/横线/方框/○）之后又用「括号里应填 5／括号里要填 6／括号里填 8」这类
    陈述句把答案写出来。试卷印出来就是把答案发给学生，属交付硬伤。
    判据要求「空后 + 括号类词 + 应填/要填/填上/填 + 与 answer 相同的值」，避免误命中
    「也可以分成 4 和 6」「都有 4 条边」这类题干本来就给的数。
  C 算式与代值重算（三类，都不依赖讲解稿）：
    C1 代数式代值：solve 题给了具体变量值（当 x = -2，y = 3 时 / 其中 x = -3）的，
       直接按 Fraction 精确算给定表达式，再与卷面 answer 比；化简求值不必先化简（代值同解）。
    C2 纯算式题：`计算：…` 开头的 solve 题，直接算。
    C3 空位算式（fill/numeric/calc/operation/short-answer）：题干 `算式＝（　）` 取等号左侧
       纯算式尾段；以及单位换算（元角分 / 米分米厘米毫米千米 / 时分秒 / 吨千克克），
       先化到同族基单位加减、再换到目标单位。尾段必须含运算符（防把 ∠2 读成 2），
       比号 `a : b` 与比例尺不计（否则 2.5 : 0.5 会被读成 0.5）。
    含根式（√ ∛）、未给值的字母、纯文字题、多空题一律记「不适用」，不判死。

只判死「算得出且明确不等」与「结构硬违例」「答案写在题干里」；算不出只记账。

用法：
  python3 scripts/verify_exam_answer_key.py                 # data/math* 全部桶
  python3 scripts/verify_exam_answer_key.py --bucket math-sujiao math-suke
  python3 scripts/verify_exam_answer_key.py --selftest       # 判据自检（含注入错答）
  python3 scripts/verify_exam_answer_key.py --json out.json
退出码：0 = 无硬错；1 = 有硬错/文件缺失；2 = 用法错。
"""
import argparse
import glob
import json
import os
import re
import sys
from fractions import Fraction

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")

SUP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
TR = str.maketrans({'＋': '+', '－': '-', '−': '-', '﹣': '-', '—': '-', '–': '-',
                    '＝': '=', '（': '(', '）': ')', '　': ' ', '，': ',', '；': ';'})
# × ÷ 故意留到 to_plain 再换：分式读法要先看得到「÷ x/(x²-1)」这个结构
PLAIN = str.maketrans({'×': '*', '÷': '/', '·': '*', '∗': '*'})
# 全角方括号（教材与练习册常见）走与 [ ] 相同的读法
TR.update({ord('［'): '[', ord('］'): ']'})


def norm_expr(s):
    """规范化算式：全角→半角、上标→^n、去空白。"""
    s = str(s).translate(TR)
    s = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+', lambda m: '^' + m.group(0).translate(SUP), s)
    s = s.replace(' ', '')
    return s


# ---------------------------------------------------------------- 表达式解析
class ParseError(Exception):
    pass


TOKEN = re.compile(r'\d+\.?\d*|sqrt|cbrt|abs|[A-Za-z]|[+\-*/^()]')


def tokenize(e):
    toks = []
    i = 0
    while i < len(e):
        m = TOKEN.match(e, i)
        if not m:
            raise ParseError('bad char %r at %d' % (e[i], i))
        toks.append(m.group(0))
        i = m.end()
    return toks


class P:
    """递归下降：expr→term→unary→power→atom，支持隐式乘法与 -( ) ，Fraction 精确。"""

    def __init__(self, toks, env):
        self.t = toks
        self.i = 0
        self.env = env

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise ParseError('expect %r got %r' % (want, tok))
        self.i += 1
        return tok

    def parse(self):
        v = self.expr()
        if self.i != len(self.t):
            raise ParseError('trailing %r' % self.t[self.i:])
        return v

    def expr(self):
        v = self.term()
        while self.peek() in ('+', '-'):
            op = self.eat()
            r = self.term()
            v = v + r if op == '+' else v - r
        return v

    def term(self):
        v = self.unary()
        while True:
            tok = self.peek()
            if tok in ('*', '/'):
                self.eat()
                r = self.unary()
                if tok == '*':
                    v = v * r
                else:
                    if r == 0:
                        raise ParseError('div0')
                    v = v / r
            elif tok is not None and (re.match(r'^\d', tok) or re.match(r'^[A-Za-z]+$', tok)
                                     or tok == '('):
                r = self.unary()      # 隐式乘法：2x / 3a²b / 2(x+1) / (x+2)(x-2)
                v = v * r
            else:
                return v

    def unary(self):
        if self.peek() == '-':
            self.eat()
            return -self.unary()
        if self.peek() == '+':
            self.eat()
            return self.unary()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() == '^':
            self.eat()
            neg = False
            if self.peek() == '-':
                self.eat()
                neg = True
            tok = self.eat()
            if not re.match(r'^\d+$', tok):
                raise ParseError('exp not int')
            e = int(tok)
            if neg:
                if base == 0:
                    raise ParseError('div0')
                return Fraction(1) / (base ** e)
            return base ** e
        return base

    def atom(self):
        tok = self.eat()
        if re.match(r'^\d', tok):
            return Fraction(tok) if '.' not in tok else Fraction(tok).limit_denominator(10 ** 9)
        if re.match(r'^[A-Za-z]$', tok):
            if tok not in self.env:
                raise ParseError('unbound %s' % tok)
            return self.env[tok]
        if tok in ('sqrt', 'cbrt', 'abs'):
            self.eat('(')
            v = self.expr()
            self.eat(')')
            if tok == 'abs':
                return abs(v)
            return _root(v, 2 if tok == 'sqrt' else 3)
        if tok == '(':
            v = self.expr()
            self.eat(')')
            return v
        raise ParseError('atom %r' % tok)


def _root(v, n):
    """n 次根：完全 n 次方给精确 Fraction，否则给 float（负数按实根读）。"""
    sign = -1 if v < 0 else 1
    a = abs(Fraction(v)) if not isinstance(v, float) else abs(v)
    if n == 2 and isinstance(v, float):
        a = abs(v)
    # 精确判定
    try:
        fr = Fraction(a)
        num, den = fr.numerator, fr.denominator
        rn = round(num ** (1.0 / n))
        rd = round(den ** (1.0 / n))
        if rn ** n == num and rd ** n == den:
            return Fraction(sign * rn, rd)
    except (ValueError, OverflowError):
        pass
    if v < 0:
        return -((-float(v)) ** (1.0 / n))
    return float(v) ** (1.0 / n)


TRIG = {
    ('sin', 0): 0, ('sin', 30): Fraction(1, 2), ('sin', 45): 2 ** .5 / 2,
    ('sin', 60): 3 ** .5 / 2, ('sin', 90): 1,
    ('cos', 0): 1, ('cos', 30): 3 ** .5 / 2, ('cos', 45): 2 ** .5 / 2,
    ('cos', 60): Fraction(1, 2), ('cos', 90): 0,
    ('tan', 0): 0, ('tan', 30): 1 / 3 ** .5, ('tan', 45): 1, ('tan', 60): 3 ** .5,
}
def _trigval(name, deg):
    val = TRIG.get((name, deg))
    if val is None:
        raise ParseError('三角比非特殊角 %s%d°' % (name, deg))
    return float(val)


ZH_POW = re.compile(r'(\)|\]|\d+(?:\.\d+)?|[A-Za-z])\s*的\s*(平方|立方|(\d+)\s*次方)')


def prep_expr(e):
    """口语算式 → 可解析算式：的平方/的 N 次方、方括号、绝对值、根号、三角比、加/减。"""
    s = e.replace('[', '(').replace(']', ')').replace('【', '(').replace('】', ')')
    s = re.sub(r'\|([^|]+)\|', r'abs(\1)', s)
    s = ZH_POW.sub(lambda m: '%s^%s' % (m.group(1),
                                        {'平方': '2', '立方': '3'}.get(m.group(2), m.group(3) or '2')), s)
    s = s.replace('立方根', '∛').replace('根号', '√')
    s = re.sub(r'√\s*\(([^()]*)\)', r'sqrt(\1)', s)
    s = re.sub(r'√\s*(-?\d+(?:\.\d+)?|[A-Za-z])', r'sqrt(\1)', s)
    s = re.sub(r'∛\s*\(([^()]*)\)', r'cbrt(\1)', s)
    s = re.sub(r'∛\s*(-?\d+(?:\.\d+)?|[A-Za-z])', r'cbrt(\1)', s)
    # sin²30° → norm 后是 sin^230°：指数 1 位、角取特殊角，避免把 230 读成指数
    s = re.sub(r'(sin|cos|tan)\^\s*(\d)\s*(0|30|45|60|90)\s*°',
               lambda m: '(%s)^%s' % (_trigval(m.group(1), int(m.group(3))), m.group(2)), s)

    def _trig(m):
        pre = m.string[:m.start()].rstrip()
        sep = '*' if pre and (pre[-1].isalnum() or pre[-1] in ')^') else ''
        return '%s(%s)' % (sep, _trigval(m.group(1), int(m.group(2))))
    s = re.sub(r'(sin|cos|tan)\s*(\d+)\s*°', _trig, s)
    s = s.replace('乘以', '*').replace('除以', '/').replace('加', '+').replace('减', '-')
    return s


def to_plain(e):
    return e.translate(PLAIN)


def ev(expr, env=None):
    return P(tokenize(to_plain(expr)), env or {}).parse()


def frac_literal_mode(expr):
    """分式读法：教材里 a/b 是分数整体，`÷ x/(x²-1)` 是除以整个分式，不是逐级左结合。

    ① `÷ A/B` → `÷(A/B)`（A、B 为简单 token 或括号组）；
    ② 数字对 `a/b` → `(a/b)`，于是 3/4÷3/8 读作 (3/4)÷(3/8) 而不是 ((3/4)/3)/8。
    """
    grp = r'(?:\([^()]*\)|[A-Za-z0-9⁰¹²³⁴⁵⁶⁷⁸⁹]+)'
    expr = re.sub(r'÷\s*(%s)\s*/\s*(%s)' % (grp, grp), r'÷(\1/\2)', expr)
    return re.sub(r'(\d+)/(\d+)(?![\d/])', r'(\1/\2)', expr)


# ---------------------------------------------------------------- 各链判据
def lane_A(item):
    """选择结构不变量，返回问题串或 None。"""
    if item.get('type') not in ('choice', 'multi'):
        return None
    opts = item.get('options') or []
    if not opts:
        return 'A 无 options'
    labels = [str(o.get('label', '')).strip() for o in opts]
    if len(labels) != len(set(labels)):
        return 'A 选项标签重复 %s' % labels
    a = str(item.get('answer', '')).strip()
    if not a:
        return 'A 答案为空'
    for L in a:
        if L not in labels:
            return 'A 答案 %r 不在选项 %s 中' % (a, ''.join(labels))
    if item['type'] == 'choice' and len(a) != 1:
        return 'A 单选题答案 %r 非单字母' % a
    if item['type'] == 'multi' and len(a) < 2:
        return 'A 多选题答案 %r 少于两个字母' % a
    texts = [str(o.get('text', '')).strip() for o in opts]
    if any(not t for t in texts):
        return 'A 存在空选项'
    if len(texts) != len(set(texts)):
        return 'A 选项文本重复：%s' % ' / '.join(texts)
    return None


LEAK = re.compile(r'(?:括号|横线|方框|□|○)[^。；，,]{0,6}?'
                  r'(?:应填|要填|填上|填)\s*[：:]?\s*(-?\d+(?:\.\d+)?|[A-D])(?![\d.%])')


def lane_B(item):
    """题干用陈述句把答案写出来。"""
    a = str(item.get('answer', '')).strip()
    if not a:
        return None
    stem = str(item.get('stem', ''))
    for m in LEAK.finditer(stem):
        if m.group(1) == a:
            return 'B 题干泄答案：%r 已写在题干（%s）' % (a, m.group(0))
    return None


ASSIGN = re.compile(r'([A-Za-z])\s*=\s*(-?\d+(?:\.\d+)?(?:/\d+)?)')


def cut_expr(s):
    """截到等号前：`12.6×3=（　），把得数写在括号里` → `12.6×3`。"""
    m = re.search(r'=', s)
    if m:
        rest = s[m.end():].lstrip()
        if rest == '' or rest[:1] in '（(':
            return s[:m.start()]
    return s


def _num_eq(ans, v):
    """精确优先；无理数/十进制近似用 1e-9 相对容差兜底（差 2e-3 的 0.33 vs 1/3 仍判不符）。"""
    try:
        if isinstance(v, Fraction) and Fraction(str(ans)) == v:
            return True
    except (ValueError, ZeroDivisionError):
        pass
    try:
        a = float(ans)
    except ValueError:
        return False
    return abs(a - float(v)) <= 1e-9 * max(1.0, abs(float(v)))


def _hits(ans, vals):
    return any(_num_eq(ans, v) for v in vals)


def _has_bare_letter(expr, bound=''):
    """去掉 sqrt/cbrt/abs 函数名与已赋值字母后还有字母 = 未给值的变量。"""
    t = re.sub(r'sqrt|cbrt|abs', '', expr)
    if bound:
        t = re.sub('[%s]' % re.escape(bound), '', t)
    return bool(re.search(r'[A-Za-z]', t))


# ------------------------------------------------ C3：填空/口算题的「空位算式」
# 只认两种可靠读法，其余一律记不适用（宁可少算，不可错杀）：
#   ① 题干里 `算式＝（　）`：取等号左侧的纯算式尾段复算（要求含运算符，避免把 ∠2 读成 2）；
#   ② 单位换算：`a单位1 ＋/－ b单位2 ＝（　）单位3`，先化到同族基单位做加减，再换到目标单位。
UNIT_FAM = {
    'len': {'千米': 10 ** 6, '公里': 10 ** 6, '米': 1000, '分米': 100, '厘米': 10, '毫米': 1},
    'time': {'时': 3600, '小时': 3600, '分': 60, '秒': 1},
    'mass': {'吨': 10 ** 6, '千克': 1000, '公斤': 1000, '克': 1},
    'money': {'元': 100, '角': 10, '分': 1},
    'vol': {'升': 1000, '毫升': 1},
}
UNIT_KEYS = sorted({k for t in UNIT_FAM.values() for k in t}, key=len, reverse=True)
UNIT_CHARS = set('千米公里分米厘米毫米时小分秒吨克元角升毫升')
ARITH_TAIL = re.compile(r'[0-9()+\-*/^×÷.\s√∛|]+$')


def _tail_arith(s):
    m = ARITH_TAIL.search(s)
    return m.group(0).strip() if m else ''


def _unit_items(s):
    """`2元5角` → [(2,'元'),(5,'角')]；`1元-4角` 中间插 ('OP',±1)。不认识返回 None。"""
    s = s.strip()
    if not s or re.search(r'平方|立方|面积|体积', s):
        return None
    items, i = [], 0
    while i < len(s):
        m = re.match(r'(-?\d+(?:\.\d+)?)\s*', s[i:])
        if not m:
            return None
        num = m.group(1)
        i += m.end()
        unit = ''
        for k in UNIT_KEYS:
            if s.startswith(k, i):
                unit = k
                i += len(k)
                break
        items.append((Fraction(num), unit))
        if i < len(s) and s[i] in '+-':
            items.append((1 if s[i] == '+' else -1, 'OP'))
            i += 1
    return items


def _tail_units(left):
    """从左侧串里取最后一段「量化表达式」：只由数字/运算符/单位字组成。"""
    ok = set('0123456789.+- ')
    start = 0
    for i, ch in enumerate(left):
        if ch not in ok and ch not in UNIT_CHARS:
            start = i + 1
    return left[start:].strip()


def _unit_convert(left, target):
    """同族单位加减换算到 target；异族/歧义（「分」在时间与钱两族）/不认识 → None。"""
    if not target:
        return None
    items = _unit_items(_tail_units(left))
    if not items:
        return None
    units = {u for _, u in items if u and u != 'OP'}
    fams = [f for f, tbl in UNIT_FAM.items() if target in tbl and all(u in tbl for u in units)]
    if len(fams) != 1:
        return None
    tbl = UNIT_FAM[fams[0]]
    tfac = tbl[target]
    total, sign, expect = Fraction(0), 1, True
    for val, u in items:
        if u == 'OP':
            if expect:
                return None
            sign, expect = val, True
            continue
        if not expect:
            return None
        base = tbl[u] if u else tfac          # 无单位项按目标单位计
        total += sign * val * Fraction(base, tfac)
        sign, expect = 1, False
    if expect:
        return None
    return total


def _lane_C3(item):
    a = str(item.get('answer', '')).strip()
    if not re.fullmatch(r'-?\d+(\.\d+)?', a):
        return None, '跳过（答案非纯数值）'
    n = norm_expr(str(item.get('stem', '')))
    if re.search(r'\d:\d', n):
        return None, '不适用（比/比例尺，非算式）'
    blanks = list(re.finditer(r'=\(\)', n))
    if not blanks:
        return None, '不适用（无空位算式）'
    m = blanks[-1]
    left = n[:m.start()]
    tail = _tail_arith(left)
    if tail and re.search(r'\d', tail) and re.search(r'[+\-*/^×÷√∛|]', tail) \
            and not _has_bare_letter(tail):
        e = prep_expr(cut_expr(tail.strip('.')))
        try:
            v1 = ev(e)
            v2 = ev(frac_literal_mode(e))
        except (ParseError, ZeroDivisionError, ValueError) as ex:
            return None, '不适用（解析失败：%s）' % ex
        if _hits(a, (v1, v2)):
            return None, '通过'
        return ('C 空位算式复算不符：%s = %s/%s，卷面 answer = %s' % (e, v1, v2, a)), '不符'
    tm = re.match(r'([\u4e00-\u9fff]{1,2})', n[m.end():])
    v = _unit_convert(left, tm.group(1) if tm else '')
    if v is None:
        return None, '不适用（单位/算式均未识别）'
    if _hits(a, (v,)):
        return None, '通过'
    return ('C 单位换算不符：%s → %s，卷面 answer = %s' % (left[-24:], v, a)), '不符'


def lane_C(item):
    """代数式代值重算；返回 (问题串, 说明)。"""
    t = item.get('type')
    if t != 'solve':
        if t in ('fill', 'numeric', 'calc', 'operation', 'short-answer'):
            return _lane_C3(item)
        return None, '跳过（题型不适用）'
    a = str(item.get('answer', '')).strip()
    if not re.fullmatch(r'-?\d+(\.\d+)?', a):
        return None, '跳过（答案非纯数值）'
    stem = str(item.get('stem', ''))
    env = {}
    for m in ASSIGN.finditer(stem.replace('＝', '=')):
        env[m.group(1)] = Fraction(m.group(2))
    if not env:
        # C2：纯算式题（计算/竖式计算/脱式计算…），不给变量，直接算
        m = re.search(r'(?:计算|求值|算一算|算出结果)\s*[：:]?\s*(.+?)[。．.]?\s*$', stem)
        if not m:
            return None, '不适用（未给变量值且非纯算式题）'
        expr = prep_expr(cut_expr(norm_expr(m.group(1)).strip('。．.;,')))
        expr = expr.split(',')[0].strip()
        expr = re.sub(r'的(?:值|结果)$', '', expr)
        if re.search(r'[\u4e00-\u9fff]', expr) or not re.search(r'\d', expr):
            return None, '不适用（算式后带中文说明）'
        if _has_bare_letter(expr):
            return None, '不适用（含字母变量）'
        try:
            v1 = ev(expr)
            v2 = ev(frac_literal_mode(expr))
        except (ParseError, ZeroDivisionError, ValueError) as ex:
            return None, '不适用（解析失败：%s）' % ex
        if _hits(a, (v1, v2)):
            return None, '通过'
        return ('C 算式复算不符：%s = %s/%s，卷面 answer = %s'
                % (expr, v1, v2, a)), '不符'
    cands = []
    m = re.search(r'求代数式\s*(.+?)\s*的值', stem)
    if m:
        cands.append(m.group(1))
    m = re.search(r'先化简[，,]?再求值[：:]\s*(.+?)[，,]\s*其中', stem)
    if m:
        cands.append(m.group(1))
    m = re.search(r'先化简[，,]?再求值[：:]\s*(.+?)[。．]\s*$', stem)
    if m:
        cands.append(m.group(1))
    if not cands:
        return None, '不适用（未定位到表达式）'
    expr = prep_expr(cut_expr(norm_expr(cands[0]).strip('。．.;,')))
    if _has_bare_letter(expr, ''.join(env)):
        return None, '不适用（含未赋值字母）'
    try:
        v1 = ev(expr, env)
        v2 = ev(frac_literal_mode(expr), env)
    except (ParseError, ZeroDivisionError, ValueError) as ex:
        return None, '不适用（解析失败：%s）' % ex
    if _hits(a, (v1, v2)):
        return None, '通过'
    return ('C 代值复算不符：%s 在 %s 下 = %s/%s，卷面 answer = %s'
            % (expr, {k: str(x) for k, x in env.items()}, v1, v2, a)), '不符'


# ------------------------------------------------ D：答案句内算式链自洽
# 应用题/开放式题的 answer 常写成「算式＝值，…，结论值」整句。本判据只核**答案句自身**：
#   ① 同一段里用「＝」连接的若干纯算术段必须等值（`25×16＝25×4×4＝100×4＝400` 四段全 400）；
#   ② 带余数（……／余）时核 a÷b=q…r，即 a=q·b+r（`13.4÷1.8＝7（段）……0.8（米）`）；
#   ③ 单位不同时按 UNIT_FAM 换算到同一族再比，族不明 / 复名数（1米25厘米）/ 比号 / ≈ / 字母式
#      一律跳过，不判。
# 它**不**判断「解法是否对题」（那要建模），只抓答案文本里的算术笔误与自相矛盾。
_CNTR = '个人本元角张块条棵朵支件箱盒袋组排行天岁遍次倍位名辆瓶束粒颗头页段盘盏台只双副套间层格斗升'
_ANS_UNITS = sorted({u for t in UNIT_FAM.values() for u in t}, key=len, reverse=True)
_ANS_UNIT_SET = set(_ANS_UNITS)
_ANS_LBL = re.compile(r'^\(\d{1,2}\)\s*(?=[\d(])')
_ANS_ANN = re.compile(r'\(([^()\d][^()]*)\)$')


def _split_top(s):
    """按顶层 , ; 。 、 切句（括号内的分隔符不算）。"""
    out, cur, depth = [], '', 0
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        if depth == 0 and ch in ',;。、':
            out.append(cur)
            cur = ''
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def _ans_seg(seg):
    """答案句的一段 → (候选值集合, 单位)；带非算术残留一律 (None, None)（宁可跳过）。"""
    s = seg.strip()
    m = _ANS_LBL.match(s)
    if m:
        s = s[m.end():]
    unit = ''
    m = _ANS_ANN.search(s)
    if m and not re.search(r'[A-Za-z]', m.group(1)):
        # 注释里如果是单位（`36000（毫升）`、`48（升）`），要留下来参与换算，不能当普通注解丢掉
        if m.group(1) in _ANS_UNIT_SET:
            unit = m.group(1)
        s = s[:m.start()].strip()
    for k in _ANS_UNITS:
        if s.endswith(k):
            body = s[:-len(k)].rstrip()
            if body and re.search(r'[\d)]$', body):
                s, unit = body, k
                break
    if not unit:
        m = re.match(r'^(.*[\d)])\s*([%s]{1,2})$' % re.escape(_CNTR), s)
        if m:
            s, unit = m.group(1), m.group(2)
    if re.search(r'[A-Za-z\u4e00-\u9fff]', s):
        return None, None
    s = to_plain(s)                      # × ÷ → * /（norm_expr 有意保留全角，好在分式读法里看结构）
    if not re.fullmatch(r'[-0-9.+*/^()\[\] ]+', s):
        return None, None
    try:
        e = prep_expr(s)
        v1, v2 = ev(e), ev(frac_literal_mode(e))
    except (ParseError, ZeroDivisionError, ValueError):
        return None, None
    return {v1, v2}, unit


def lane_D(item):
    """答案句算式链自洽；返回 (问题串, 说明)。"""
    if item.get('type') not in ('solve', 'fill', 'numeric', 'calc', 'operation', 'short-answer'):
        return None, '跳过（题型不适用）'
    a = norm_expr(str(item.get('answer', '')))
    if '=' not in a:
        return None, '跳过（答案句无等号）'
    checked = 0
    for p in _split_top(a):
        if '=' not in p or re.search(r'[≈<>＜＞:∶]', p):
            continue
        parts = p.split('=')
        mrem = re.match(r'^\s*(-?\d+(?:\.\d+)?)(?:\([^()]*\))?\s*(?:……|\.{3,}|余)\s*'
                        r'(-?\d+(?:\.\d+)?)(?:\([^()]*\)|[^\d()]{1,3})?\s*$', parts[-1])
        if mrem:
            q, r = Fraction(mrem.group(1)), Fraction(mrem.group(2))
            body = parts[0].strip()
            m = _ANS_LBL.match(body)
            if m:
                body = body[m.end():]
            pl = to_plain(body)
            mm = re.match(r'^(-?\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)$', pl)
            if not mm:
                continue
            a0, b0 = Fraction(mm.group(1)), Fraction(mm.group(2))
            if a0 != q * b0 + r:
                return ('D 答案句余数不符：%s = %s……%s，而 %s×%s+%s = %s'
                        % (pl, q, r, q, b0, r, q * b0 + r)), '不符'
            checked += 1
            continue
        vals, ok = [], True
        for x in parts:
            v, u = _ans_seg(x)
            if v is None:
                ok = False
                break
            vals.append((v, u))
        if not ok:
            continue
        units = {u for _, u in vals}
        marked = {u for u in units if u}      # 只有末尾一段标了单位（`…＝480（千克）`）时按原值比
        if len(marked) <= 1:
            cand = [v for v, _ in vals]
        else:
            if '' in units:
                continue
            fam = None
            for tbl in UNIT_FAM.values():
                if all(u in tbl for u in units):
                    fam = tbl
                    break
            if fam is None:
                continue
            cand = [{x * Fraction(fam[u]) for x in v} for v, u in vals]
        inter = cand[0]
        for nxt in cand[1:]:
            inter = inter & nxt
            if not inter:
                return ('D 答案句算式链不符：%s' % p), '不符'
        checked += 1
    if checked:
        return None, '通过'
    return None, '跳过（无可核算式）'


# ------------------------------------------------ E：选择题「结论句 ↔ 卷答」冲突
# 解析里明确写出的结论（故选/应选/正确答案是/答案选 X）必须与 answer 字段一致。
# 不认「错误答案 C」「故 A 错误」这类干扰项讨论——它们是逐项判断，不是结论。
_PICK = [r'故\s*选\s*[:：]?\s*([A-D](?:\s*[,，、]?\s*[A-D])*)',
         r'应\s*选\s*[:：]?\s*([A-D](?:\s*[,，、]?\s*[A-D])*)',
         r'正\s*确\s*答\s*案\s*(?:应)?\s*(?:是|为|选)\s*[:：]?\s*([A-D](?:\s*[,，、]?\s*[A-D])*)',
         r'答\s*案\s*选\s*[:：]?\s*([A-D](?:\s*[,，、]?\s*[A-D])*)']


def _pick_letters(s):
    return ''.join(sorted(set(re.findall(r'[A-D]', s))))


def lane_E(item):
    """解析结论句与 answer 冲突；返回 (问题串, 说明)。"""
    if item.get('type') not in ('choice', 'multi'):
        return None, '跳过（题型不适用）'
    txt = ' '.join(str(x) for x in (item.get('analysis'), item.get('explain'),
                                    item.get('solution')) if x)
    if not txt.strip():
        return None, '跳过（无解析）'
    hits = set()
    for p in _PICK:
        for m in re.finditer(p, txt):
            lt = _pick_letters(m.group(1))
            if lt:
                hits.add(lt)
    if not hits:
        return None, '跳过（解析无结论句）'
    if len(hits) > 1:
        return ('E 解析结论句自相矛盾：%s，卷面 answer = %s'
                % ('/'.join(sorted(hits)), item.get('answer'))), '不符'
    got = hits.pop()
    want = _pick_letters(str(item.get('answer', '')))
    if got == want:
        return None, '通过'
    return ('E 解析结论句与卷答冲突：解析「%s」，卷面 answer = %s' % (got, want)), '不符'


# ---------------------------------------------------------------- 主流程
def buckets():
    out = []
    for d in sorted(glob.glob(os.path.join(REPO, 'data', 'math*', 'exams'))):
        out.append(os.path.basename(os.path.dirname(d)))
    return [b for b in out if b != 'math_backup']


def papers(bucket):
    return sorted(glob.glob(os.path.join(REPO, 'data', bucket, 'exams', '*', '*.json')))


def run(bucket_list, verbose=True, want_json=None):
    stat = {'papers': 0, 'items': 0, 'A': 0, 'B': 0, 'C': 0,
            'C_skip': 0, 'C_pass': 0,
            'D': 0, 'D_pass': 0, 'D_skip': 0,
            'E': 0, 'E_pass': 0, 'E_skip': 0}
    errs = []
    for b in bucket_list:
        before = dict(stat)
        ps = papers(b)
        if not ps:
            errs.append({'bucket': b, 'file': None, 'no': None, 'msg': '卷目录为空/不存在'})
            continue
        for f in ps:
            stat['papers'] += 1
            d = json.load(open(f, encoding='utf-8'))
            for s in d.get('sections', []):
                for it in s.get('items', []):
                    stat['items'] += 1
                    for lane, fn in (('A', lane_A), ('B', lane_B)):
                        msg = fn(it)
                        if msg:
                            stat[lane] += 1
                            errs.append({'bucket': b, 'file': os.path.relpath(f, REPO),
                                         'no': it.get('no'), 'msg': msg})
                    msg, note = lane_C(it)     # 题型门槛在 lane_C 内分流（solve 走代值，填空/口算走空位算式）
                    if msg:
                        stat['C'] += 1
                        errs.append({'bucket': b, 'file': os.path.relpath(f, REPO),
                                     'no': it.get('no'), 'msg': msg})
                    elif note == '通过':
                        stat['C_pass'] += 1
                    else:
                        stat['C_skip'] += 1
                    for lane, fn in (('D', lane_D), ('E', lane_E)):
                        msg2, note2 = fn(it)
                        if msg2:
                            stat[lane] += 1
                            errs.append({'bucket': b, 'file': os.path.relpath(f, REPO),
                                         'no': it.get('no'), 'msg': msg2})
                        elif note2 == '通过':
                            stat[lane + '_pass'] += 1
                        else:
                            stat[lane + '_skip'] += 1
        if verbose:
            print('[%s] 卷 %d｜题 %d｜A %d｜B %d｜C 不符 %d（C 通过 %d、不适用 %d）'
                  '｜D 不符 %d（通过 %d、不适用 %d）｜E 冲突 %d（通过 %d、不适用 %d）'
                  % (b, len(ps), stat['items'] - before['items'], stat['A'] - before['A'],
                     stat['B'] - before['B'], stat['C'] - before['C'],
                     stat['C_pass'] - before['C_pass'], stat['C_skip'] - before['C_skip'],
                     stat['D'] - before['D'], stat['D_pass'] - before['D_pass'],
                     stat['D_skip'] - before['D_skip'],
                     stat['E'] - before['E'], stat['E_pass'] - before['E_pass'],
                     stat['E_skip'] - before['E_skip']))
    if want_json:
        json.dump({'stat': stat, 'errors': errs}, open(want_json, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    return stat, errs


# ---------------------------------------------------------------- 自检
FIXTURES = [
    ('A 单选答案不在选项', {'no': 1, 'type': 'choice', 'answer': 'E',
                      'options': [{'label': 'A', 'text': 'x'}, {'label': 'B', 'text': 'y'},
                                  {'label': 'C', 'text': 'z'}, {'label': 'D', 'text': 'w'}]}, True),
    ('A 选项重复', {'no': 2, 'type': 'choice', 'answer': 'A',
                 'options': [{'label': 'A', 'text': '5'}, {'label': 'B', 'text': '5'}]}, True),
    ('A 单选多字母', {'no': 3, 'type': 'choice', 'answer': 'AB',
                  'options': [{'label': 'A', 'text': '1'}, {'label': 'B', 'text': '2'}]}, True),
    ('A 干净选择', {'no': 4, 'type': 'choice', 'answer': 'C',
                 'options': [{'label': 'A', 'text': '1'}, {'label': 'B', 'text': '2'},
                             {'label': 'C', 'text': '3'}, {'label': 'D', 'text': '4'}]}, False),
    ('B 泄答案-应填', {'no': 5, 'type': 'fill', 'answer': '5',
                  'stem': '4＋（　）＝9，括号里应填5。'}, True),
    ('B 泄答案-填', {'no': 6, 'type': 'fill', 'answer': '8',
                 'stem': '接着数：6、7、（　）、9，括号里填8。'}, True),
    ('B 不误命中-同名数', {'no': 7, 'type': 'fill', 'answer': '4',
                    'stem': '10可以分成6和（　），也可以分成4和6。'}, False),
    ('B 不误命中-单位题', {'no': 8, 'type': 'fill', 'answer': '＜',
                    'stem': '在括号里填上合适的符号：7○9，应填（　）。'}, False),
    ('C 化简求值相符', {'no': 9, 'type': 'solve', 'answer': '2',
                  'stem': '先化简，再求值：2(x² - 3x) - (2x² - 5x + 1)，其中 x = -3。'}, False),
    ('C 化简求值不符', {'no': 10, 'type': 'solve', 'answer': '3',
                  'stem': '先化简，再求值：2(x² - 3x) - (2x² - 5x + 1)，其中 x = -3。'}, True),
    ('C 负数乘方', {'no': 11, 'type': 'solve', 'answer': '-9',
                 'stem': '计算：(-2)³ + 6 × (-1/2) - 10 ÷ (-5)。'}, False),
    ('C 算式错答', {'no': 13, 'type': 'solve', 'answer': '-7',
                 'stem': '计算：(-2)³ + 6 × (-1/2) - 10 ÷ (-5)。'}, True),
    ('C 根式不适用', {'no': 12, 'type': 'solve', 'answer': '0',
                  'stem': '计算：∛(-8)+√25-|-3|．'}, False),
    ('C 根式算错', {'no': 14, 'type': 'solve', 'answer': '2',
                'stem': '计算：∛(-8)+√25-|-3|．'}, True),
    ('C 无理数容差', {'no': 15, 'type': 'solve', 'answer': '1',
                 'stem': '计算：|1-√2|+|√2-√3|+|√3-2|。'}, False),
    ('C 无理数错答', {'no': 16, 'type': 'solve', 'answer': '0',
                 'stem': '计算：|1-√2|+|√2-√3|+|√3-2|。'}, True),
    ('C 口语的平方', {'no': 17, 'type': 'solve', 'answer': '14',
                 'stem': '计算：-2 的 2 次方 × (-3) - (-6) ÷ 3'}, False),
    ('C 口语的平方错', {'no': 18, 'type': 'solve', 'answer': '18',
                  'stem': '计算：-2 的 2 次方 × (-3) - (-6) ÷ 3'}, True),
    ('C 竖式等号截断', {'no': 19, 'type': 'solve', 'answer': '37.8',
                  'stem': '用竖式计算：12.6×3＝（　），把得数写在括号里。'}, False),
    ('C 竖式等号错答', {'no': 20, 'type': 'solve', 'answer': '37.08',
                  'stem': '用竖式计算：12.6×3＝（　），把得数写在括号里。'}, True),
    ('C 三角比根式', {'no': 21, 'type': 'solve', 'answer': '1',
                 'stem': '计算：√2cos45°+tan60°·tan30°-2sin30°．'}, False),
    ('C 根号汉字', {'no': 22, 'type': 'solve', 'answer': '1',
                'stem': '计算：根号12 × 根号3 - 根号50 ÷ 根号2。'}, False),
    ('C 方括号', {'no': 23, 'type': 'solve', 'answer': '1',
               'stem': '先化简，再求值：3a^2 b - [2ab^2 + 2(a^2 b - 2ab^2)]，其中 a = -2，b = 1/2。'}, False),
    ('C 三角比平方', {'no': 24, 'type': 'solve', 'answer': '1',
                 'stem': '计算 sin²30°+cos²30°+tan45°-2sin45°·cos45° 的值。'}, False),
    ('C 三角比平方错', {'no': 25, 'type': 'solve', 'answer': '0.5',
                  'stem': '计算 sin²30°+cos²30°+tan45°-2sin45°·cos45° 的值。'}, True),
    ('C 无冒号竖式', {'no': 26, 'type': 'solve', 'answer': '85',
                 'stem': '用竖式计算 58＋27，先写清相同数位对齐的方法，再算出结果。'}, False),
    ('C 无冒号竖式错', {'no': 27, 'type': 'solve', 'answer': '84',
                  'stem': '用竖式计算 58＋27，先写清相同数位对齐的方法，再算出结果。'}, True),
    ('C 近似兜底不宽松', {'no': 28, 'type': 'solve', 'answer': '0.33',
                   'stem': '计算：1÷3。'}, True),
    ('C3 空位算式相符', {'no': 29, 'type': 'fill', 'answer': '84',
                   'stem': '直接写得数：36＋48＝（　）。'}, False),
    ('C3 空位算式错答', {'no': 30, 'type': 'fill', 'answer': '83',
                   'stem': '直接写得数：36＋48＝（　）。'}, True),
    ('C3 单位换算相符', {'no': 31, 'type': 'fill', 'answer': '70',
                   'stem': '直接写得数：1米－30厘米＝（　）厘米。'}, False),
    ('C3 单位换算错答', {'no': 32, 'type': 'fill', 'answer': '60',
                   'stem': '直接写得数：1米－30厘米＝（　）厘米。'}, True),
    ('C3 分步算式末空', {'no': 33, 'type': 'fill', 'answer': '69',
                    'stem': '计算23×3时，先算20×3＝60，再算3×3＝9，最后60＋9＝（　）。'}, False),
    ('C3 分步算式末空错', {'no': 34, 'type': 'fill', 'answer': '59',
                     'stem': '计算23×3时，先算20×3＝60，再算3×3＝9，最后60＋9＝（　）。'}, True),
    # --- D：答案句算式链自洽 ---
    ('D 答案句链相符', {'no': 38, 'type': 'solve',
                   'answer': '5－3＝2（个），老师手里还剩 2 个沙包。',
                   'stem': '老师有 5 个沙包，拿走 3 个，还剩几个？'}, False),
    ('D 答案句链不符', {'no': 39, 'type': 'solve',
                   'answer': '5－3＝3（个），老师手里还剩 3 个沙包。',
                   'stem': '老师有 5 个沙包，拿走 3 个，还剩几个？'}, True),
    ('D 分步两算式不误判为链', {'no': 40, 'type': 'solve',
                        'answer': '18－9＝9（张），9＋5＝14（张），现在有 14 张卡片。',
                        'stem': '小明原有 18 张，送出 9 张后妈妈又给 5 张，现有几张？'}, False),
    ('D 链式等式相符', {'no': 41, 'type': 'solve',
                  'answer': '25×16＝25×4×4＝100×4＝400（千克）',
                  'stem': '每箱 25 千克，16 箱共多少千克？'}, False),
    ('D 链式等式不符', {'no': 42, 'type': 'solve',
                  'answer': '25×16＝25×4×4＝100×4＝480（千克）',
                  'stem': '每箱 25 千克，16 箱共多少千克？'}, True),
    ('D 余数相符', {'no': 43, 'type': 'solve',
                 'answer': '13.4÷1.8＝7（段）……0.8（米），最多剪成 7 段。',
                 'stem': '13.4 米长的绳子每 1.8 米剪一段，最多剪几段？'}, False),
    ('D 余数不符', {'no': 44, 'type': 'solve',
                 'answer': '13.4÷1.8＝7（段）……0.9（米），最多剪成 7 段。',
                 'stem': '13.4 米长的绳子每 1.8 米剪一段，最多剪几段？'}, True),
    ('D 单位链换算相符', {'no': 45, 'type': 'fill',
                    'answer': '1米＝100厘米', 'stem': '1 米等于多少厘米？'}, False),
    ('D 单位链换算不符', {'no': 46, 'type': 'fill',
                    'answer': '1米＝90厘米', 'stem': '1 米等于多少厘米？'}, True),
    ('D 字母方程跳过', {'no': 47, 'type': 'solve', 'answer': '2(2x－1)＝3(x＋2)',
                   'stem': '解方程 2(2x－1)＝3(x＋2)。'}, False),
    # --- E：解析结论句 ↔ 卷答 ---
    ('E 结论句一致', {'no': 48, 'type': 'choice', 'answer': 'C', 'analysis': '代入得 3，故选 C。',
                  'options': [{'label': 'A', 'text': '1'}, {'label': 'B', 'text': '2'},
                              {'label': 'C', 'text': '3'}, {'label': 'D', 'text': '4'}]}, False),
    ('E 结论句冲突', {'no': 49, 'type': 'choice', 'answer': 'B', 'analysis': '代入得 3，故选 C。',
                  'options': [{'label': 'A', 'text': '1'}, {'label': 'B', 'text': '2'},
                              {'label': 'C', 'text': '3'}, {'label': 'D', 'text': '4'}]}, True),
    ('E 干扰项讨论不误报', {'no': 50, 'type': 'choice', 'answer': 'B',
                      'analysis': 'A 需讨论，若误取交集会得到错误答案 C，故选 B。',
                      'options': [{'label': 'A', 'text': '1'}, {'label': 'B', 'text': '2'},
                                  {'label': 'C', 'text': '3'}, {'label': 'D', 'text': '4'}]}, False),
    ('E 多选结论句一致', {'no': 51, 'type': 'multi', 'answer': 'ABD',
                    'analysis': '逐项判断，A、B、D 正确，C 错误，故选 ABD。',
                    'options': [{'label': 'A', 'text': '1'}, {'label': 'B', 'text': '2'},
                                {'label': 'C', 'text': '3'}, {'label': 'D', 'text': '4'}]}, False),
]

# 必须判「不适用」的读法歧义样本：宁可不算，也不能把 ∠2 读成 2、把比号当除号
NO_CALC = [
    ('∠标记不误读', {'no': 35, 'type': 'fill', 'answer': '55',
                 'stem': '∠1和∠2合起来是一个直角，如果∠1＝35°，那么∠2＝（　）°。'}),
    ('比号不误读', {'no': 36, 'type': 'numeric', 'answer': '5',
                'stem': '求出下面各比的比值：2.5 : 0.5 = （　）。'}),
    ('比例尺不误读', {'no': 37, 'type': 'fill', 'answer': '3',
                 'stem': '在比例尺是 1 : 100000 的地图上，图上距离 3 厘米表示实际距离（　）千米。'}),
]


def selftest():
    ok = 0
    for name, item, expect_bad in FIXTURES:
        got = False
        if item['type'] in ('choice', 'multi'):
            got = lane_A(item) is not None
        msg_b = lane_B(item)
        if msg_b:
            got = True
        msg_c, note = lane_C(item)       # 题型门槛在 lane_C 内分流
        if msg_c:
            got = True                   # 「不适用」不改变 got：A/B 已判出的错不能被 C 的跳过覆盖
        for fn in (lane_D, lane_E):
            if fn(item)[0]:
                got = True
        verdict = 'OK' if got == expect_bad else 'FAIL'
        if verdict == 'OK':
            ok += 1
        print('  [%s] %s（期望%s，实得%s）' % (verdict, name,
                                          '报错' if expect_bad else '通过',
                                          '报错' if got else '通过'))
    # 算术双读数：3/4÷3/8 = 2（分数写法）
    e = norm_expr('3/4 ÷ 3/8')
    v1, v2 = ev(e), ev(frac_literal_mode(e))
    good = (v1 != Fraction(2)) and (v2 == Fraction(2))
    print('  [%s] 分数双读数 3/4÷3/8：左结合=%s、分数读法=%s' % ('OK' if good else 'FAIL', v1, v2))
    ok += 1 if good else 0
    for name, item in NO_CALC:
        msg_c, note = lane_C(item)
        good = msg_c is None and note != '通过'
        print('  [%s] %s（须不适用，实得 %s）' % ('OK' if good else 'FAIL', name, note))
        ok += 1 if good else 0
    total = len(FIXTURES) + 1 + len(NO_CALC)
    print('== --selftest %d/%d' % (ok, total))
    return 0 if ok == total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', nargs='*', default=None)
    ap.add_argument('--json', default=None)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    bl = a.bucket or buckets()
    stat, errs = run(bl, verbose=not a.quiet, want_json=a.json)
    print('== 合计 卷 %d｜题 %d｜A 结构 %d｜B 泄答案 %d｜C 代值不符 %d（C 通过 %d、不适用 %d）'
          '｜D 答案句不符 %d（通过 %d、不适用 %d）｜E 结论句冲突 %d（通过 %d、不适用 %d）'
          % (stat['papers'], stat['items'], stat['A'], stat['B'], stat['C'],
             stat['C_pass'], stat['C_skip'], stat['D'], stat['D_pass'], stat['D_skip'],
             stat['E'], stat['E_pass'], stat['E_skip']))
    for e in errs:
        print('  ! [%s] %s 第%s题 %s' % (e['bucket'], e['file'], e['no'], e['msg']))
    return 0 if not errs else 1


if __name__ == '__main__':
    sys.exit(main())
