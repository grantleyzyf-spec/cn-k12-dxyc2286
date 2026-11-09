#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数学原创试卷「纯算式题」答案复算核验（7 链之一）。

判据（严格口径，宁可少核不可误报）：
  A1 题干在去掉讲解性小标签后，仅由「算式 = （ ）」若干段构成（可多空，段间用 ，、； 分隔）；
  A2 答案按同一分隔符切分后，段数与空数相同；
  A3 每段答案可解析为「数」或「数 + 中文单位」，数与 Fraction 复算值精确相等。

只核「算式直接给值」的题（口算 / 直接写得数 / 计算 / 算一算 / 笔算），
应用题、估算、保留小数、相反数 / 倒数 / 立方根 / 百分数化等语义变换题一律不核（会误报）。
不核不等于错，只表示该题不在机器可判范围内。

用法：
  python3 verify_math_exam_arithmetic.py                # 12 版全核
  python3 verify_math_exam_arithmetic.py --bucket math-sujiao
  python3 verify_math_exam_arithmetic.py --selftest     # 判据自检（含注入错答）
  python3 verify_math_exam_arithmetic.py --json out.json
退出码：0 = 无不一致；1 = 有不一致或文件缺失；2 = 用法/路径错。
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile
from decimal import Decimal
from fractions import Fraction

TR = str.maketrans({'＋': '+', '－': '-', '×': '*', '÷': '÷', '＝': '=',
                    '（': '(', '）': ')', '．': '.', '　': ' ', '∗': '*',
                    '·': '*', '—': '-', '–': '-', '﹣': '-', '﹢': '+'})
LABEL = re.compile(r'^(?:直接写出?得数|直接写得数|口算|算一算|计算|笔算|'
                   r'用竖式计算|列竖式计算|脱式计算)[：:，,]?')
NOISE = [r'[，,]?把?得数填在括号里。?', r'[，,]?填在括号里。?', r'[，,]?用简便方法计算。?']
EXPR_CH = re.compile(r'^[0-9+\-*/().÷*]+$')
SUP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789-')
# 初中/高中模板句尾语（去尾后必须只剩算式）
TAIL = re.compile(r'(?:的值是|的得数是|的结果是|的值等于|的值|等于|得|是)?[（(]?[\s_＿]*[）)]?[?？]?$')


def norm(s):
    return str(s).translate(TR).replace(' ', '').replace('\u3000', '')


def _sup(e):
    """连续上标数字 → **n（含负指数），如 (-1)²⁰²⁵ → (-1)**2025。"""
    return re.sub(r'⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+',
                  lambda m: '**' + m.group(0).translate(SUP), e)


ECH = '0-9+\\-*/().÷√∛⁰¹²³⁴⁵⁶⁷⁸⁹⁻'


def _clean_stem(stem):
    t = norm(stem).replace('。', '')
    return LABEL.sub('', t)


def extract_one(stem):
    """整句只由「算式 + 模板尾语」构成时返回算式（初中/高中体例）。"""
    t = _clean_stem(stem)
    t = re.sub(r'^(?:求|化简)[:：]?', '', t)
    m = re.match(r'^([' + ECH + r']+?)(?:的值是|的得数是|的结果是|的值等于|的值|等于|得|是)?'
                 r'[（(]?[\s_＿]*[）)]?[?？]?$', t)
    if not m:
        return None
    e = m.group(1)
    bare = _sup(e)
    if bare[:1] not in ('√', '∛') and not re.search(r'[+\-*÷/]', bare.lstrip('-')):
        return None
    if '()' in bare:
        return None
    return e


def extract_exprs(stem):
    """题干 → 算式列表；不是纯算式题则 None。"""
    t = _clean_stem(stem)
    for p in NOISE:
        t = re.sub(p, '', t)
    parts = [p for p in re.split(r'[，,；;、]', t) if p]
    out, ok = [], True
    for p in parts:
        p = re.sub(r'^\d{1,2}[)）、]', '', p.strip())
        m = re.match(r'^([' + ECH + r']+)=[（(]?[\s_＿]*[）)]?[?？]?$', p)
        if m:
            out.append(m.group(1))
        elif not re.match(r'^[()?？\s_＿]*$', p):
            ok = False
            break
    if ok and out:
        return out
    one = extract_one(stem)
    return [one] if one else None


def fracify(expr):
    """教材体例：a/b 是一个分数整体，不是连续除法（单趟替换，避免重复套括号）。"""
    return re.sub(r'(?<![0-9./(])([0-9]+)/([0-9]+)', r'(\1/\2)', expr)


def _iroot(n, k):
    """整数 n 的 k 次精确根；不是完全 k 次幂则 None。"""
    if n < 0:
        return None
    r = int(round(n ** (1.0 / k))) if n else 0
    for cand in range(max(0, r - 2), r + 3):
        if cand ** k == n:
            return cand
    return None


def _root(v, k):
    if v is None:
        return None
    num, den = v.numerator, v.denominator
    if k == 2 and num < 0:
        return None
    sign = -1 if num < 0 else 1
    a = _iroot(abs(num), k)
    b = _iroot(den, k)
    if a is None or b is None or b == 0:
        return None
    return Fraction(sign * a, b)


def eval_frac(expr):
    """Fraction 词法求值：+ - * / ** 括号、上下标幂、整式根式；不接受任何标识符。"""
    e = fracify(_sup(expr)).replace('÷', '/')
    m = re.fullmatch(r'([√∛])\((.*)\)', e)
    if m:
        inner = eval_frac(m.group(2))
        return _root(inner, 2 if m.group(1) == '√' else 3)
    if not EXPR_CH.match(e) or e.count('(') != e.count(')'):
        return None
    toks = re.findall(r'\d+\.?\d*|\*\*|[()+\-*/]', e)
    if ''.join(toks) != e:
        return None
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def eat():
        tok = toks[pos[0]]
        pos[0] += 1
        return tok

    def atom():
        tok = peek()
        if tok is None:
            raise ValueError('eof')
        if tok == '(':
            eat()
            v = add()
            if peek() != ')':
                raise ValueError('paren')
            eat()
            return v
        if tok == '-':
            eat()
            return -atom()
        if tok == '+':
            eat()
            return atom()
        eat()
        return Fraction(Decimal(tok))

    def unary():
        tok = peek()
        if tok in ('+', '-'):
            eat()
            return -unary() if tok == '-' else unary()
        return power()

    def power():
        v = atom()
        while peek() == '**':
            eat()
            ex = unary()
            if ex.denominator != 1 or abs(ex) > 10000:
                raise ValueError('exp')
            v = v ** int(ex)
        return v

    def mul():
        v = unary()
        while peek() in ('*', '/'):
            op = eat()
            r = unary()
            v = v * r if op == '*' else v / r
        return v

    def add():
        v = mul()
        while peek() in ('+', '-'):
            op = eat()
            r = mul()
            v = v + r if op == '+' else v - r
        return v

    try:
        v = add()
        return v if pos[0] == len(toks) else None
    except (ValueError, ZeroDivisionError, ArithmeticError):
        return None


def parse_num(s):
    t = norm(s).strip('。 ')
    if re.fullmatch(r'-?\d+\.?\d*', t):
        return Fraction(Decimal(t))
    m = re.fullmatch(r'(-?\d+)\s*(\d+)/(\d+)', t)
    if m:
        a = m.group(1)
        sign = -1 if a.startswith('-') else 1
        return sign * (Fraction(int(a.lstrip('-'))) + Fraction(int(m.group(2)), int(m.group(3))))
    m = re.fullmatch(r'(-?\d+)/(\d+)', t)
    if m and int(m.group(2)) != 0:
        return Fraction(int(m.group(1)), int(m.group(2)))
    return None


UNIT = re.compile(r'^(.*?)([^\d\.\-/]+)$')


def num_with_unit(s):
    t = norm(s).strip('。 ')
    v = parse_num(t)
    if v is not None:
        return v, ''
    m = UNIT.match(t)
    if not m:
        return None, ''
    v = parse_num(m.group(1))
    unit = m.group(2)
    if v is None or re.search(r'[0-9]', unit):
        return None, ''
    return v, unit


def ans_list(s):
    return [x.strip() for x in re.split(r'[，,；;、]', str(s).strip()) if x.strip()]


def repo_root(start):
    p = os.path.abspath(start)
    while p != '/':
        if os.path.isdir(os.path.join(p, 'data')) and os.path.isdir(os.path.join(p, 'scripts')):
            return p
        p = os.path.dirname(p)
    return None


def buckets_of(root):
    out = []
    for d in sorted(glob.glob(os.path.join(root, 'data', 'math*'))):
        if os.path.isdir(os.path.join(d, 'exams')):
            out.append(os.path.basename(d))
    return out


def check_bucket(root, bucket):
    st = {'files': 0, 'pool': 0, 'eval': 0, 'multi': 0, 'unit_ans': 0,
          'expr_unparsed': 0, 'count_mismatch': 0, 'ans_unparsed': 0}
    bad = []
    for f in sorted(glob.glob(os.path.join(root, 'data', bucket, 'exams', '*', '*.json'))):
        st['files'] += 1
        d = json.load(open(f, encoding='utf-8'))
        for sec in d.get('sections', []):
            for it in sec.get('items', []):
                if it.get('type') not in ('numeric', 'calc', 'operation', 'fill'):
                    continue
                st['pool'] += 1
                exprs = extract_exprs(it.get('stem', ''))
                if not exprs:
                    continue
                vals = [eval_frac(e) for e in exprs]
                if any(v is None for v in vals):
                    st['expr_unparsed'] += 1
                    continue
                ans = ans_list(it.get('answer'))
                if len(ans) != len(vals):
                    st['count_mismatch'] += 1
                    continue
                parsed = [num_with_unit(a) for a in ans]
                if any(p[0] is None for p in parsed):
                    st['ans_unparsed'] += 1
                    continue
                st['eval'] += 1
                if len(vals) > 1:
                    st['multi'] += 1
                if any(p[1] for p in parsed):
                    st['unit_ans'] += 1
                if [p[0] for p in parsed] != vals:
                    bad.append({'file': os.path.relpath(f, root), 'no': it.get('no'),
                                'stem': it.get('stem'), 'answer': it.get('answer'),
                                'calced': [str(v) for v in vals]})
    return st, bad


# ---------- 自检 ----------
POS = [
    ('直接写得数：6＋4＝（　）。', '10'),
    ('口算：3.6＋2.7＝（　）。', '6.3'),
    ('计算：8/15 ÷ 4/9＝（　）。', '1.2'),
    ('直接写出得数：12÷3/4＝（　）。', '16'),
    ('计算：2＋3×4＝（　）。', '14'),
    ('计算：(3/4－1/2)÷5/8＝（　）。', '2/5'),
    ('直接写出得数：6＋4＝（　），10－6＝（　）。', '10，4'),
    ('计算：-2⁴ + (-2)⁴ = ______。', '0'),
    ('计算 (-1)²⁰²⁵ 的结果是____。', '-1'),
    ('计算 √(49/64) 的结果是____。', '7/8'),
    ('计算 ∛(-8/27) 的结果是____。', '-2/3'),
    ('计算 12÷(-3/4)×(-1/2) 的值是 ____。', '8'),
]
NEG = [
    ('一个数的 3 倍是 27，这个数是（　）。', '9'),
    ('4÷3 的商保留两位小数约是（　）。', '1.33'),
    ('估算：398+403 的和大约是（　）。', '800'),
    ('数 -2.5 的相反数是______．', '2.5'),
    ('把 3/8 化成百分数，百分号前面的数是（　）。', '37.5'),
    ('计算 5.63÷6.1，除到商的小数部分第三位，再把得数保留两位小数，约是（　　）。', '0.92'),
]


def judge(stem, answer):
    """→ (是否认作纯算式题, 复算是否与卷答一致)"""
    exprs = extract_exprs(stem)
    if not exprs:
        return False, False
    vals = [eval_frac(e) for e in exprs]
    if any(v is None for v in vals):
        return False, False
    ans = ans_list(answer)
    if len(ans) != len(vals):
        return False, False
    parsed = [num_with_unit(a) for a in ans]
    if any(p[0] is None for p in parsed):
        return False, False
    return True, [p[0] for p in parsed] == vals


def selftest():
    ok = 0
    tot = 0
    for stem, ans in POS:
        tot += 1
        is_expr, match = judge(stem, ans)
        good = is_expr and match
        ok += 1 if good else 0
        print(('  ✓' if good else '  ✗'), '应识别且应一致:', stem, '=>', ans,
              '| 识别', is_expr, '一致', match)
    for stem, ans in NEG:
        tot += 1
        is_expr, match = judge(stem, ans)
        good = not is_expr
        ok += 1 if good else 0
        print(('  ✓' if good else '  ✗'), '应不识别:', stem, '=>', ans, '| 识别', is_expr)
    print(f'判据自检 {ok}/{tot}')
    return ok == tot


def tamper_test(root, bucket):
    """把一个真件复制到临时仓，改一处答案，确认能报出来。"""
    src = sorted(glob.glob(os.path.join(root, 'data', bucket, 'exams', '*', '*.json')))
    if not src:
        print('杀伤力自检：无卷可注入')
        return False
    tmp = tempfile.mkdtemp(prefix='arith_')
    tgt_dir = os.path.join(tmp, 'data', bucket, 'exams', '注入册')
    os.makedirs(tgt_dir)
    os.makedirs(os.path.join(tmp, 'scripts'))
    d = json.load(open(src[0], encoding='utf-8'))
    hit = False
    for sec in d.get('sections', []):
        for it in sec.get('items', []):
            if hit:
                break
            exprs = extract_exprs(it.get('stem', ''))
            if not exprs or len(exprs) != 1:
                continue
            v = eval_frac(exprs[0])
            if v is None or len(ans_list(it.get('answer'))) != 1:
                continue
            p = num_with_unit(ans_list(it.get('answer'))[0])
            if p[0] is None:
                continue
            it['answer'] = str(Fraction(v) + 1)
            hit = True
    if not hit:
        print('杀伤力自检：本卷没有可注入的纯算式题')
        return False
    for sec in d.get('sections', []):
        for it in sec.get('items', []):
            if it.get('itemId'):
                it['itemId'] = it['itemId'] + '_tamper'
    d['examId'] = str(d.get('examId', '')) + '_tamper'
    json.dump(d, open(os.path.join(tgt_dir, '注入卷.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    st, bad = check_bucket(tmp, bucket)
    print(f'杀伤力自检：注入 1 处错答 → 复算 {st["eval"]} 题，报不一致 {len(bad)} 处')
    return len(bad) == 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=os.getcwd())
    ap.add_argument('--bucket', action='append', default=None)
    ap.add_argument('--json', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    root = None
    for cand in (a.repo, os.environ.get('REPO', ''), os.path.expanduser('~/Desktop/cn-k12-dxyc2286')):
        if cand and (root := repo_root(cand)):
            break
    if not root:
        if a.selftest:          # 自检的判据部分不依赖仓库，注入部分跳过
            return 0 if selftest() else 1
        print('无法定位仓库根（需同时存在 data/ 与 scripts/），可用 --repo 指定', file=sys.stderr)
        return 2

    if a.selftest:
        ok1 = selftest()
        ok2 = tamper_test(root, 'math-sujiao')
        return 0 if (ok1 and ok2) else 1

    buckets = a.bucket or buckets_of(root)
    if not buckets:
        print('没找到任何 math* 桶', file=sys.stderr)
        return 2

    tot = {'files': 0, 'pool': 0, 'eval': 0, 'multi': 0, 'unit_ans': 0}
    allbad = []
    missing = []
    for b in buckets:
        if not os.path.isdir(os.path.join(root, 'data', b, 'exams')):
            missing.append(b)
            continue
        st, bad = check_bucket(root, b)
        for k in tot:
            tot[k] += st[k]
        allbad += bad
        print(f'[{b}] 卷 {st["files"]}｜题池 {st["pool"]}｜复算 {st["eval"]}'
              f'（多空 {st["multi"]}、带单位 {st["unit_ans"]}）｜不一致 {len(bad)}')

    if missing:
        print('缺桶:', ' '.join(missing))
    print(f'== 合计 卷 {tot["files"]}｜题池 {tot["pool"]}｜复算 {tot["eval"]}'
          f'｜不一致 {len(allbad)}')
    for r in allbad:
        print(f'  ✗ {r["file"]} 第{r["no"]}题 | {r["stem"][:60]} | 卷答 {r["answer"]}'
              f' | 复算 {" / ".join(r["calced"])}')
    if a.json:
        json.dump({'total': tot, 'mismatch': allbad}, open(a.json, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    return 0 if not allbad and not missing else 1


if __name__ == '__main__':
    sys.exit(main())
