# -*- coding: utf-8 -*-
"""化学版本桶题库检查器。

用法：
  python3 scripts/check_chem_editions_bank.py --shard <分片产物.json>     # 工位自检
  python3 scripts/check_chem_editions_bank.py --subject <bucket> --all     # 父代合并前全量
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
TYPES = {'choice', 'fill', 'short-answer', 'numeric'}
DIFF = {'basic', 'standard', 'hard'}
JUNK = ('以上都不对', '无法确定', '仅在大学学习', '以上都对')


def zh(s):
    return len([c for c in s or '' if '\u4e00' <= c <= '\u9fff'])


def load_points(bucket):
    topics = json.load(open(os.path.join(DATA, bucket, 'topics.json'), encoding='utf-8'))
    return {t['id']: t for t in topics}


def check_questions(qs, points, strict_ids=False):
    errs = []
    by_topic = {}
    for q in qs:
        tid = q.get('topicId')
        by_topic.setdefault(tid, []).append(q)
    for tid, t in points.items():
        need = 5 if t['level'] == 'unit' else 8
        got = by_topic.get(tid, [])
        if len(got) != need:
            errs.append('题量 %s(%s) %d/%d' % (t['name'], tid, len(got), need))
            continue
        types = [q.get('type') for q in got]
        diffs = {q.get('difficulty') for q in got}
        c, f = types.count('choice'), types.count('fill')
        s, nu = types.count('short-answer'), types.count('numeric')
        if c < (2 if need == 5 else 3):
            errs.append('choice 不足 %s %d' % (tid, c))
        if f < (1 if need == 5 else 2):
            errs.append('fill 不足 %s %d' % (tid, f))
        if s < 1:
            errs.append('short-answer 缺 %s' % tid)
        if nu > 1:
            errs.append('numeric 超 1 道 %s %d' % (tid, nu))
        if diffs != DIFF:
            errs.append('三档不齐 %s %s' % (tid, sorted(diffs)))
    for q in qs:
        qid = q.get('id', '?')
        if q.get('topicId') not in points:
            errs.append('题挂了不存在的点 %s' % qid)
            continue
        if q.get('type') not in TYPES:
            errs.append('type 非法 %s %s' % (qid, q.get('type')))
        if q.get('difficulty') not in DIFF:
            errs.append('difficulty 非法 %s' % qid)
        if zh(q.get('prompt')) < 8:
            errs.append('题干过短 %s' % qid)
        if zh(q.get('explanation')) < 20:
            errs.append('解析过短 %s' % qid)
        if q.get('type') == 'choice':
            opts = q.get('options') or []
            chs = q.get('choices') or []
            if len(opts) != 4:
                errs.append('选项不是 4 个 %s' % qid)
            if [o.get('label') for o in opts] != ['A', 'B', 'C', 'D']:
                errs.append('选项 label 非 ABCD %s' % qid)
            if [(o.get('label'), o.get('text')) for o in opts] != [(c.get('label'), c.get('text')) for c in chs]:
                errs.append('choices 与 options 不同构 %s' % qid)
            if q.get('answer') not in ('A', 'B', 'C', 'D'):
                errs.append('选择题答案非 ABCD %s' % qid)
            if any(any(j in (o.get('text') or '') for j in JUNK) for o in opts):
                errs.append('凑数干扰项 %s' % qid)
        elif q.get('type') == 'fill':
            if '____' not in (q.get('prompt') or ''):
                errs.append('fill 缺 ____ %s' % qid)
            if not q.get('answer'):
                errs.append('fill 缺答案 %s' % qid)
        elif q.get('type') == 'short-answer':
            if len((q.get('answer') or '').split('；')) < 2:
                errs.append('简答未分条 %s' % qid)
        elif q.get('type') == 'numeric':
            v = q.get('verify')
            if not v:
                errs.append('numeric 缺 verify %s' % qid)
            else:
                try:
                    val = eval(str(v), {'__builtins__': {}}, {})
                    if abs(float(val) - float(q.get('answer'))) > max(1e-6, abs(float(q.get('answer'))) * 1e-3):
                        errs.append('verify 复算不等 %s %s vs %s' % (qid, val, q.get('answer')))
                except Exception:
                    errs.append('verify 不可复算 %s' % qid)
        if re.search(r'\*\*|##|\|', q.get('prompt') or '') and not re.search(r'\|[^|]{1,12}\|', q.get('prompt') or ''):
            errs.append('含 Markdown %s' % qid)
    ids = [q.get('id') for q in qs]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errs.append('题号重复 %s' % sorted(dup)[:3])
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard')
    ap.add_argument('--subject')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    if a.shard:
        raw = json.load(open(a.shard, encoding='utf-8'))
        bucket = raw.get('bucket') if isinstance(raw, dict) else None
        qs = raw.get('questions') if isinstance(raw, dict) else raw
        if not bucket:
            print('ERR 分片缺 bucket 字段'); sys.exit(2)
        points = load_points(bucket)
        spec_dir = os.path.join(DATA, bucket, '_bank_spec')
        sid = raw.get('shard')
        spec = json.load(open(os.path.join(spec_dir, sid + '.json'), encoding='utf-8'))
        sub_points = {p['topicId']: points[p['topicId']] for p in spec['points']}
        errs = check_questions(qs, sub_points)
        need_ids = sorted(i for p in spec['points'] for i in p['id_range'])
        if sorted(q.get('id') for q in qs) != need_ids:
            errs.append('题号集合与 id_range 不一致')
        print('%s：%d 点 / %d 题' % (sid, len(sub_points), len(qs)))
    else:
        bucket = a.subject
        points = load_points(bucket)
        qs = json.load(open(os.path.join(DATA, bucket, 'questions.json'), encoding='utf-8'))
        errs = check_questions(qs, points)
        print('%s：%d 点 / %d 题' % (bucket, len(points), len(qs)))
    if errs:
        print('ERR %d 项' % len(errs))
        for e in errs[:25]:
            print('  - ' + e)
        print('RESULT: FAIL')
        sys.exit(1)
    print('RESULT: PASS')


if __name__ == '__main__':
    main()
