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
  C 代数式代值重算：solve 题给了具体变量值（当 x = -2，y = 3 时 / 其中 x = -3）的，
    直接按 Fraction 精确算给定表达式，再与卷面 answer 比；化简求值不必先化简（代值同解）。
    含根式（√ ∛）、未给值的字母、纯文字题一律记「不适用」，不判死。

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


def lane_C(item):
    """代数式代值重算；返回 (问题串, 说明)。"""
    if item.get('type') != 'solve':
        return None, '跳过（非 solve）'
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
            'C_skip': 0, 'C_pass': 0}
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
                    if it.get('type') == 'solve':
                        msg, note = lane_C(it)
                        if msg:
                            stat['C'] += 1
                            errs.append({'bucket': b, 'file': os.path.relpath(f, REPO),
                                         'no': it.get('no'), 'msg': msg})
                        elif note == '通过':
                            stat['C_pass'] += 1
                        else:
                            stat['C_skip'] += 1
        if verbose:
            print('[%s] 卷 %d｜题 %d｜A %d｜B %d｜C 不符 %d（C 通过 %d、不适用 %d）'
                  % (b, len(ps), stat['items'] - before['items'], stat['A'] - before['A'],
                     stat['B'] - before['B'], stat['C'] - before['C'],
                     stat['C_pass'] - before['C_pass'], stat['C_skip'] - before['C_skip']))
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
        if item['type'] == 'solve':
            msg_c, note = lane_C(item)
            if msg_c:
                got = True
            elif note != '通过' and expect_bad and '不适用' in note:
                got = False
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
    print('== --selftest %d/%d' % (ok, len(FIXTURES) + 1))
    return 0 if ok == len(FIXTURES) + 1 else 1


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
          % (stat['papers'], stat['items'], stat['A'], stat['B'], stat['C'],
             stat['C_pass'], stat['C_skip']))
    for e in errs:
        print('  ! [%s] %s 第%s题 %s' % (e['bucket'], e['file'], e['no'], e['msg']))
    return 0 if not errs else 1


if __name__ == '__main__':
    sys.exit(main())
