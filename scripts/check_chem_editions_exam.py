# -*- coding: utf-8 -*-
"""化学版本桶单卷检查器。

用法：
  python3 scripts/check_chem_editions_exam.py --exam <卷 JSON>        # 工位自检
  python3 scripts/check_chem_editions_exam.py --subject <bucket> --all # 父代全量
"""
import argparse, difflib, glob, itertools, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
MIN_STEM, MIN_ANA = 12, 25


def zh(s):
    return len([c for c in s or '' if '\u4e00' <= c <= '\u9fff'])


def load_bank(bucket):
    p = os.path.join(DATA, bucket, 'questions.json')
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8'))


def check(exam, points_map, bank, spec=None):
    errs = []
    eid = exam.get('examId')
    if not eid:
        return ['缺 examId']
    for k in ('kind', 'paper', 'book', 'stage', 'term', 'grade', 'duration', 'fullScore', 'scope', 'sections'):
        if k not in exam:
            errs.append('缺字段 %s' % k)
    secs = exam.get('sections') or []
    total_score = sum((it.get('score') or 0) for s in secs for it in s.get('items') or [])
    if exam.get('fullScore') and total_score != exam['fullScore']:
        errs.append('分值合计 %s ≠ fullScore %s' % (total_score, exam['fullScore']))
    nos, ids = [], []
    for si, s in enumerate(secs):
        title = s.get('title') or ''
        if not s.get('rule'):
            errs.append('第 %d 段缺 rule' % (si + 1))
        items = s.get('items') or []
        for it in items:
            nos.append(it.get('no'))
            ids.append(it.get('itemId'))
            if zh(it.get('stem')) < MIN_STEM:
                errs.append('题干过短 %s' % it.get('itemId'))
            if zh(it.get('analysis')) < MIN_ANA:
                errs.append('解析过短 %s' % it.get('itemId'))
            if not it.get('answer'):
                errs.append('缺答案 %s' % it.get('itemId'))
            if not it.get('topicIds'):
                errs.append('缺 topicIds %s' % it.get('itemId'))
            for tid in it.get('topicIds') or []:
                if tid not in points_map:
                    errs.append('题挂了不存在/不在范围的点 %s → %s' % (it.get('itemId'), tid))
            if s.get('type') in ('choice', 'multi'):
                opts = it.get('options') or []
                if len(opts) != 4:
                    errs.append('选项不是 4 个 %s' % it.get('itemId'))
                labels = [o.get('label') for o in opts]
                if labels != ['A', 'B', 'C', 'D']:
                    errs.append('选项 label 非 ABCD %s' % it.get('itemId'))
                ans = str(it.get('answer') or '')
                if not ans or any(ch not in 'ABCD' for ch in ans):
                    errs.append('选择题答案非法 %s' % it.get('itemId'))
    if nos != list(range(1, len(nos) + 1)):
        errs.append('题号不连续：%s…' % nos[:6])
    if len(set(ids)) != len(ids):
        errs.append('itemId 重复')
    # 覆盖
    cover = {tid for s in secs for it in s.get('items') or [] for tid in it.get('topicIds') or []}
    if exam.get('kind') == 'unit':
        need = [t for t in points_map.values() if t['level'] == 'lesson']
        miss = [t['name'] for t in need if t['id'] not in cover]
        if miss:
            errs.append('单元卷未覆盖课时点：%s' % '、'.join(miss[:4]))
    else:
        # 期中/期末：每个 scope 单元至少 2 题
        per = {}
        for s in secs:
            for it in s.get('items') or []:
                for tid in it.get('topicIds') or []:
                    t = points_map.get(tid)
                    if not t:
                        continue
                    for sc in exam.get('scope') or []:
                        if t['chapter'] == sc or t['chapter'].startswith(sc + ' · '):
                            per[sc] = per.get(sc, 0) + 1
        for sc in exam.get('scope') or []:
            if per.get(sc, 0) < 2:
                errs.append('scope「%s」仅 %d 题（<2）' % (sc, per.get(sc, 0)))
    # 原创性
    if bank:
        stems = [q.get('prompt') or q.get('stem') or '' for q in bank]
        for s in secs:
            for it in s.get('items') or []:
                st = it.get('stem') or ''
                for b in stems:
                    if b and difflib.SequenceMatcher(None, st, b).ratio() >= 0.85:
                        errs.append('与题库题干过近 %s' % it.get('itemId'))
                        break
    return errs


def resolve_bucket(exam_id):
    """反查卷所属桶：先按历史前缀快判，再按 _exam_spec 存在性定位（ckp 等新桶）。"""
    s = str(exam_id or '')
    if s.startswith('clj'):
        return 'chemistry-lujiao'
    if s.startswith('clk'):
        return 'chemistry-luke'
    if s.startswith('chj'):
        return 'chemistry-hujiao'
    hits = sorted(glob.glob(os.path.join(DATA, '*', '_exam_spec', s + '.json')))
    if hits:
        return os.path.basename(os.path.dirname(os.path.dirname(hits[0])))
    return 'chemistry-luke'


def resolve_exam_path(arg):
    """--exam 既可给卷文件路径，也可只给 examId（此时按分片 out 定位）。"""
    if os.path.exists(arg):
        return arg
    for sp in sorted(glob.glob(os.path.join(DATA, '*', '_exam_spec', arg + '.json'))):
        out = (json.load(open(sp, encoding='utf-8')) or {}).get('out')
        if out and os.path.exists(out):
            return out
    return arg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exam')
    ap.add_argument('--subject')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    if a.exam:
        exam = json.load(open(resolve_exam_path(a.exam), encoding='utf-8'))
        bucket = a.subject or resolve_bucket(exam.get('examId'))
        spec_p = os.path.join(DATA, bucket, '_exam_spec', exam['examId'] + '.json')
        spec = json.load(open(spec_p, encoding='utf-8')) if os.path.exists(spec_p) else None
        topics = json.load(open(os.path.join(DATA, bucket, 'topics.json'), encoding='utf-8'))
        ids = {p['topicId'] for p in (spec or {}).get('points', [])} or {t['id'] for t in topics}
        points_map = {t['id']: t for t in topics if t['id'] in ids}
        errs = check(exam, points_map, load_bank(bucket), spec)
        print('%s：%d 段 / %d 题' % (exam['examId'], len(exam.get('sections') or []),
                                    sum(len(s.get('items') or []) for s in exam.get('sections') or [])))
    else:
        bucket = a.subject
        topics = {t['id']: t for t in json.load(open(os.path.join(DATA, bucket, 'topics.json'), encoding='utf-8'))}
        bank = load_bank(bucket)
        files = sorted(glob.glob(os.path.join(DATA, bucket, 'exams', '*', '*.json')))
        errs = []
        for f in files:
            exam = json.load(open(f, encoding='utf-8'))
            spec_p = os.path.join(DATA, bucket, '_exam_spec', exam.get('examId', '') + '.json')
            spec = json.load(open(spec_p, encoding='utf-8')) if os.path.exists(spec_p) else None
            ids = {p['topicId'] for p in (spec or {}).get('points', [])}
            pm = {k: v for k, v in topics.items() if not ids or k in ids}
            e = check(exam, pm, bank, spec)
            if e:
                errs.append((f, e))
        # 同册跨卷不得出现重复题干（A/B 卷、期中期末与单元卷之间）
        bybook = {}
        for f in files:
            exam = json.load(open(f, encoding='utf-8'))
            for s in exam.get('sections') or []:
                for it in s.get('items') or []:
                    bybook.setdefault(exam.get('book'), []).append(
                        (exam.get('examId'), it.get('itemId'), it.get('stem') or ''))
        dups = []
        for book, items in bybook.items():
            for (e1, i1, s1), (e2, i2, s2) in itertools.combinations(items, 2):
                r = 1.0 if s1 == s2 else difflib.SequenceMatcher(None, s1, s2).ratio()
                if r >= 0.90:
                    dups.append((e1, i1, e2, i2, round(r, 3)))
        if dups:
            errs.append(('跨卷重复题干', ['%s/%s ↔ %s/%s (%.2f)' % d for d in dups[:5]]))
        print('%s：卷 %d 份／题 %d' % (bucket, len(files), sum(len(b) for b in bybook.values())))
    if errs:
        if a.exam:
            print('ERR %d 项' % len(errs))
            for e in errs[:20]:
                print('  - ' + e)
        else:
            for f, e in errs[:10]:
                print('ERR %s' % os.path.basename(f))
                for x in e[:3]:
                    print('   - ' + x)
        print('RESULT: FAIL')
        sys.exit(1)
    print('RESULT: PASS')


if __name__ == '__main__':
    main()
