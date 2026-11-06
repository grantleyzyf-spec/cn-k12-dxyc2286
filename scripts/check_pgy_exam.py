#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版（郭玉英）初中物理 试卷检查器（逐卷 / 全量）。

用法：
  python3 scripts/check_pgy_exam.py --exam data/physics-bsd-gyy/exams/八年级上册/<卷名>.json
  python3 scripts/check_pgy_exam.py --all        # 逐卷跑全部（排除 _stale/）

判据：
  1. 结构：24 题、题号 1..24 连续、itemId 唯一、sections[].title 与 rule 一致
  2. 分值：逐段「题数 × 每题分」== rule 声明；全卷合计 == fullScore（120）
  3. 覆盖：单元卷 scope 内课时点各 ≥1 次；期中/期末每单元 ≥2 题且课时点覆盖 ≥80%
  4. 原创性：题干与题库相似度 <0.85
  5. 内容：解析 ≥30 汉字、禁 Markdown/LaTeX、选择题 4 项且答案在选项内、
     非选择题 scoreRule 各步之和 == 题分
退出码：0 = PASS
"""
import argparse
import difflib
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
HAN = re.compile(r'[\u4e00-\u9fa5]')


def han(s):
    return len(HAN.findall(s or ''))


def norm(s):
    return re.sub(r'[\s，。、；：（）()？?“”"\'’]+', '', s or '')


def load_bank():
    qs = json.load(open(os.path.join(D, 'questions.json'), encoding='utf-8'))
    return [(q['id'], norm(q.get('prompt'))) for q in qs]


def check(path, bank, topics):
    e = json.load(open(path, encoding='utf-8'))
    errs = []
    items = e.get('items') or []
    if len(items) != 24:
        errs.append('题数 %d ≠ 24' % len(items))
    nos = [it.get('no') for it in items]
    if nos != list(range(1, len(items) + 1)):
        errs.append('题号不连续：%s' % nos[:6])
    ids = [it.get('itemId') for it in items]
    if len(set(ids)) != len(ids):
        errs.append('itemId 重复')
    # 分段
    secs = e.get('sections') or []
    if len(secs) != 4:
        errs.append('分段数 %d ≠ 4' % len(secs))
    total = 0
    for s in secs:
        its = [it for it in items if it.get('section') == s.get('title')]
        if len(its) != s.get('count'):
            errs.append('%s 题数 %d ≠ %d' % (s.get('title'), len(its), s.get('count')))
        sm = sum(it.get('score', 0) for it in its)
        if sm != s.get('score'):
            errs.append('%s 分值合计 %d ≠ %d' % (s.get('title'), sm, s.get('score')))
        if s.get('rule') and str(s['score']) not in s['rule']:
            errs.append('%s rule 未写分值：%s' % (s.get('title'), s.get('rule')))
        total += sm
    if total != e.get('fullScore', 120):
        errs.append('全卷合计 %d ≠ %d' % (total, e.get('fullScore', 120)))

    # 覆盖
    scope = e.get('scope') or []
    unit_topic = {t['id']: t for t in topics}

    def in_scope(t):
        return any(t['chapter'] == sc or t['chapter'].startswith(sc + ' · ') for sc in scope)

    scoped_lessons = {t['id'] for t in topics if t['level'] == 'lesson' and in_scope(t)}
    scoped_units = {t['id'] for t in topics if t['level'] == 'unit' and in_scope(t)}
    got = set()
    for it in items:
        for tid in it.get('topicIds') or []:
            if isinstance(tid, list):
                errs.append('第%s题 topicIds 含嵌套数组' % it.get('no'))
                continue
            got.add(tid)
    if e.get('kind') == 'unit':
        miss = scoped_lessons - got
        if miss:
            errs.append('未覆盖课时点 %d 个：%s' % (len(miss), sorted(miss)[:4]))
    else:
        for uid in scoped_units:
            ch = unit_topic[uid]['chapter']
            lessons = {t['id'] for t in topics
                       if t['level'] == 'lesson' and t['chapter'].startswith(ch + ' · ')}
            hit = len(lessons & got)
            if hit < 2:
                errs.append('单元「%s」卷面命中 %d 题 <2' % (unit_topic[uid]['name'], hit))
        if scoped_lessons:
            cov = len(scoped_lessons & got) / len(scoped_lessons)
            if cov < 0.8:
                errs.append('课时点覆盖 %.0f%% <80%%' % (cov * 100))

    # 逐题
    for it in items:
        no = it.get('no')
        stem = it.get('stem') or ''
        if han(stem) < 10:
            errs.append('第%s题题干过短' % no)
        if han(it.get('analysis')) < 30:
            errs.append('第%s题解析 %d 汉字 <30' % (no, han(it.get('analysis'))))
        if re.search(r'\*\*|##|\$|\\frac|<[a-z]+>', stem + (it.get('analysis') or '')):
            errs.append('第%s题含 Markdown/LaTeX' % no)
        if it.get('type') == 'choice':
            opts = it.get('options') or []
            if len(opts) != 4:
                errs.append('第%s题选项 %d ≠4' % (no, len(opts)))
            if it.get('answer') not in [o.get('label') for o in opts]:
                errs.append('第%s题答案不在选项内' % no)
        else:
            sr = it.get('scoreRule') or []
            if sr:
                ssum = 0
                for step in sr:
                    m = re.search(r'(\d+)\s*分', step if isinstance(step, str) else str(step))
                    ssum += int(m.group(1)) if m else 0
                if ssum != it.get('score'):
                    errs.append('第%s题 scoreRule 合计 %d ≠ %d' % (no, ssum, it.get('score')))
        # 原创性
        nstem = norm(stem)
        best = 0.0
        for qid, qn in bank:
            if abs(len(qn) - len(nstem)) > 12:
                continue
            r = difflib.SequenceMatcher(None, nstem, qn).ratio()
            if r > best:
                best = r
        if best >= 0.85:
            errs.append('第%s题与题库相似度 %.2f ≥0.85' % (no, best))
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exam')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    bank = load_bank()
    topics = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    files = ([a.exam] if a.exam else
             sorted(p for p in glob.glob(os.path.join(D, 'exams', '**', '*.json'), recursive=True)
                    if '_stale' not in p) if a.all else [])
    if not files:
        print('用法：--exam <文件> 或 --all')
        return 1
    bad = 0
    for f in files:
        errs = check(f, bank, topics)
        if errs:
            bad += 1
            print('✗ %s' % os.path.basename(f))
            for e in errs[:8]:
                print('   -', e)
            if len(errs) > 8:
                print('   - …另有 %d 项' % (len(errs) - 8))
        else:
            print('✓ %s' % os.path.basename(f))
    print('\n共 %d 卷 · 不合格 %d · %s' % (len(files), bad, 'RESULT: PASS' if not bad else 'RESULT: FAIL'))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
