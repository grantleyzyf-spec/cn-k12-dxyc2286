#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏教版数学 · 单册分片门禁（子代必须跑到末行 PASS）

用法：python3 check_bank_sj.py <tag>      # 如 s1a / h2
判定：分片结构、点覆盖、题量、题型、答案位、难度、字数、可复算
"""
import glob
import json
import os
import re
import sys
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SUBJECT = 'math-sujiao'
for _i, _a in enumerate(sys.argv):
    if _a == '--subject' and _i + 1 < len(sys.argv):
        SUBJECT = sys.argv[_i + 1]
OUT = os.path.join(REPO, 'data', SUBJECT)
HAN = re.compile(r'[\u4e00-\u9fa5]')
BAD_MD = re.compile(r'[*_`#\[\]|]')
TYPES = {'choice', 'numeric', 'fill', 'short-answer'}
DIFFS = {'basic', 'standard', 'hard'}


def han(s):
    return len(HAN.findall(s or ''))


def safe_eval(expr):
    def ev(n):
        t = n.get('type')
        if t == 'num':
            return n['value']
        a, b = n['values']
        a, b = ev(a), ev(b)
        return {'op': lambda: a + b, 'sub': lambda: a - b,
                'mul': lambda: a * b, 'div': lambda: a / b,
                'pow': lambda: a ** b}[n['op']]()
    try:
        return ev(json.loads(expr))
    except Exception:
        return None


def check(tag, partial=False):
    errs = []
    shard_p = os.path.join(OUT, '_shards', f'{tag}.json')
    if not os.path.isfile(shard_p):
        return [f'缺派单 {shard_p}']
    bank_dir = os.path.join(OUT, '_bank')
    parts = sorted(glob.glob(os.path.join(bank_dir, f'{tag}.part*.json')))
    single = os.path.join(bank_dir, f'{tag}.json')
    if not parts and not os.path.isfile(single):
        return [f'缺产出 {single} 或 {tag}.part*.json']
    shard = json.load(open(shard_p, encoding='utf-8'))
    bank = {'unit_points': [], 'lesson_points': []}
    for fp in (parts if parts else [single]):
        d = json.load(open(fp, encoding='utf-8'))
        bank['unit_points'] += d.get('unit_points', [])
        bank['lesson_points'] += d.get('lesson_points', [])

    want_units = [u['unit_id'] for u in shard['units']]
    want_lessons = [l['id'] for u in shard['units'] for l in u['lessons']]
    page_of = {l['id']: l.get('page') for u in shard['units'] for l in u['lessons']}

    up = {x.get('id'): x for x in bank.get('unit_points', [])}
    lp = {x.get('id'): x for x in bank.get('lesson_points', [])}
    if not partial:
        if set(up) != set(want_units):
            errs.append(f'单元点覆盖不符：缺 {sorted(set(want_units)-set(up))[:5]} 多 {sorted(set(up)-set(want_units))[:5]}')
        if set(lp) != set(want_lessons):
            errs.append(f'课时点覆盖不符：缺 {sorted(set(want_lessons)-set(lp))[:5]} 多 {sorted(set(lp)-set(want_lessons))[:5]}')
    else:
        extra = (set(up) - set(want_units)) | (set(lp) - set(want_lessons))
        if extra:
            errs.append(f'出现派单外的点：{sorted(extra)[:5]}')

    all_q_ids = set()
    for kind, bag, want_n in (('单元点', up, 5), ('课时点', lp, 8)):
        for tid, obj in bag.items():
            if han(obj.get('description')) < 12:
                errs.append(f'{tid}: description 汉字 <12')
            if not obj.get('mastery_criteria') or han(obj['mastery_criteria'][0]) < 8:
                errs.append(f'{tid}: mastery_criteria 缺或过短')
            if kind == '课时点':
                if len(obj.get('misconceptions') or []) < 2:
                    errs.append(f'{tid}: misconceptions <2 条')
                if obj.get('page') != page_of.get(tid):
                    errs.append(f'{tid}: page 应为 {page_of.get(tid)}（实为 {obj.get("page")}）')
            qs = obj.get('questions') or []
            if len(qs) != want_n:
                errs.append(f'{tid}: 题量 {len(qs)} ≠ {want_n}')
            diffs = set()
            letters = Counter()
            for q in qs:
                qid = q.get('id')
                if not qid:
                    errs.append(f'{tid}: 有题缺 id'); continue
                if qid in all_q_ids:
                    errs.append(f'题 id 重复 {qid}')
                all_q_ids.add(qid)
                if q.get('topicId') != tid:
                    errs.append(f'{qid}: topicId 应为 {tid}')
                t = q.get('type')
                if t not in TYPES:
                    errs.append(f'{qid}: type 非法 {t}')
                if q.get('difficulty') not in DIFFS:
                    errs.append(f'{qid}: difficulty 非法 {q.get("difficulty")}')
                diffs.add(q.get('difficulty'))
                if han(q.get('prompt')) < 8:
                    errs.append(f'{qid}: 题干汉字 <8')
                if han(q.get('explanation')) < 15:
                    errs.append(f'{qid}: 解析汉字 <15')
                if BAD_MD.search(q.get('prompt') or ''):
                    errs.append(f'{qid}: 题干含 Markdown 符号')
                if t == 'choice':
                    opts = q.get('options') or []
                    if len(opts) != 4 or [o.get('label') for o in opts] != ['A', 'B', 'C', 'D']:
                        errs.append(f'{qid}: 选择题须 4 选项 A–D')
                    a = q.get('answer')
                    if a not in [o.get('label') for o in opts]:
                        errs.append(f'{qid}: 答案不在选项内')
                    letters[a] += 1
                elif t == 'numeric':
                    if not (q.get('verify') or '').strip():
                        errs.append(f'{qid}: 数值题缺 verify')
                    else:
                        v = safe_eval(q['verify'])
                        if v is None:
                            errs.append(f'{qid}: verify 不可复算')
                        else:
                            try:
                                if abs(float(v) - float(q.get('answer'))) > 1e-6:
                                    errs.append(f'{qid}: verify={v} ≠ answer {q.get("answer")}')
                            except Exception:
                                pass
                if t in ('fill', 'short-answer') and not q.get('answer'):
                    errs.append(f'{qid}: 缺答案')
            if want_n >= 5 and diffs != DIFFS:
                errs.append(f'{tid}: 难度三档没齐（有 {sorted(diffs)}）')
            if letters:
                tot = sum(letters.values())
                hot, cnt = letters.most_common(1)[0]
                if tot and cnt / tot > 0.4:
                    errs.append(f'{tid}: 答案 {hot} 占 {cnt}/{tot} > 40%')

    return errs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-') and a not in ('math-sujiao', 'math-suke')]
    if not args:
        print('usage: check_bank_sj.py <tag>|--all'); return 2
    partial = '--partial' in sys.argv
    if args and args[0] == '--all':
        seen = set()
        for f in sorted(os.listdir(os.path.join(OUT, '_bank'))):
            if f.endswith('.json'):
                seen.add(f.split('.')[0])
        tags = sorted(seen)
    else:
        tags = args
    bad = 0
    for t in tags:
        e = check(t, partial=partial)
        if e:
            bad += 1
            print(f'✗ {t}: {len(e)} 处问题')
            for x in e[:8]:
                print(f'   - {x}')
        else:
            print(f'✓ {t} PASS')
    print(f'\n== 小结：通过 {len(tags)-bad}/{len(tags)} ==')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
