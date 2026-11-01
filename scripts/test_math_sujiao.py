#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""江苏线数学图谱不变量（苏教版 / 苏科版）

用法：python3 scripts/test_math_sujiao.py [math-sujiao|math-suke]（缺省两个都跑）
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

EXPECT = {
    'math-sujiao': {'pfx': 'msj', 'prefix_of_book': '苏教版', 'books': 13,
                    'units': 108, 'lessons': 393,
                    'book_names': ['苏教版一年级上册', '苏教版一年级下册', '苏教版二年级上册',
                                   '苏教版二年级下册', '苏教版三年级上册', '苏教版三年级下册',
                                   '苏教版四年级上册', '苏教版五年级上册', '苏教版六年级上册',
                                   '苏教版必修第一册', '苏教版必修第二册',
                                   '苏教版选择性必修第一册', '苏教版选择性必修第二册']},
    'math-suke': {'pfx': 'msk', 'prefix_of_book': '苏科版', 'books': 5,
                  'units': 28, 'lessons': 113,
                  'book_names': ['苏科版七年级上册', '苏科版七年级下册', '苏科版八年级上册',
                                 '苏科版八年级下册', '苏科版九年级上册']},
}

fails = []


def ck(name, cond, detail=''):
    if cond:
        print(f'  ✓ {name}')
    else:
        print(f'  ✗ {name}  {detail}')
        fails.append(name)


def run(subject):
    cfg = EXPECT[subject]
    base = os.path.join(D, subject)
    topics = json.load(open(os.path.join(base, 'topics.json'), encoding='utf-8'))
    qs = json.load(open(os.path.join(base, 'questions.json'), encoding='utf-8'))
    deps = json.load(open(os.path.join(base, 'dependencies.json'), encoding='utf-8'))
    ids = {t['id'] for t in topics}
    by_point = defaultdict(list)
    for q in qs:
        by_point[q['topicId']].append(q)

    unit_pts = [t for t in topics if not re.search(r'_[ph]1\d{3}$', t['id'])]
    lesson_pts = [t for t in topics if re.search(r'_[ph]1\d{3}$', t['id'])]

    print(f'\n== {subject} ==')
    ck('知识点总数 = 单元点+课时点', len(topics) == len(unit_pts) + len(lesson_pts))
    ck(f"单元点 {len(unit_pts)} ≥ {cfg['units']}", len(unit_pts) >= cfg['units'], len(unit_pts))
    ck(f"课时点 {len(lesson_pts)} ≥ {cfg['lessons']}", len(lesson_pts) >= cfg['lessons'], len(lesson_pts))
    ck('全部 subject=math', all(t.get('subject') == 'math' for t in topics))
    ck(f"id 前缀全为 {cfg['pfx']}_", all(t['id'].startswith(cfg['pfx'] + '_') for t in topics))
    ck('id 唯一', len(ids) == len(topics))
    ck('id 符合 schema 正则', all(re.fullmatch(r'[a-z]{2,6}_[ph]\d{2,4}', t['id']) for t in topics))

    books = Counter(t['chapter'].split(' ')[0] for t in topics)
    ck(f"册数 = {cfg['books']}", len(books) == cfg['books'], sorted(books))
    ck('所有册名带版本前缀', all(b.startswith(cfg['prefix_of_book']) for b in books),
       [b for b in books if not b.startswith(cfg['prefix_of_book'])])
    missing_books = [b for b in cfg['book_names'] if b not in books]
    ck('册名与人手清单一致', not missing_books, missing_books)

    ck('单元点 chapter 不含「·」', all('·' not in t['chapter'] for t in unit_pts))
    ck('课时点 chapter 含「·」', all('·' in t['chapter'] for t in lesson_pts))

    bad_u = [t['id'] for t in unit_pts if len(by_point.get(t['id'], [])) != 5]
    bad_l = [t['id'] for t in lesson_pts if len(by_point.get(t['id'], [])) != 8]
    ck('单元点题量恰 5', not bad_u, bad_u[:5])
    ck('课时点题量恰 8', not bad_l, bad_l[:5])

    diff_ok = all({'basic', 'standard', 'hard'} <= {q.get('difficulty') for q in by_point[t['id']]}
                  for t in topics)
    ck('每点难度三档齐', diff_ok)

    choice_bad = [q['id'] for q in qs if q['type'] == 'choice'
                  and (len(q.get('options') or []) != 4 or q['answer'] not in
                       [o['label'] for o in q.get('options') or []])]
    ck('选择题 4 选项且答案在内', not choice_bad, choice_bad[:5])
    ck('numeric 全有 verify', all(q.get('verify') for q in qs if q['type'] == 'numeric'))
    ck('题干 ≥8 汉字', all(len(re.findall(r'[\u4e00-\u9fa5]', q['prompt'])) >= 8 for q in qs))
    ck('解析 ≥15 汉字', all(len(re.findall(r'[\u4e00-\u9fa5]', q.get('explanation', ''))) >= 15 for q in qs))
    ck('题 id 唯一', len({q['id'] for q in qs}) == len(qs))
    ck('题都挂在本学科点上', all(q['topicId'] in ids for q in qs))

    letters = Counter(q['answer'] for q in qs if q['type'] == 'choice')
    tot = sum(letters.values())
    hot = letters.most_common(1)[0]
    ck('答案位整体不偏（最高占比 ≤45%）', hot[1] / tot <= 0.45, f'{hot} {hot[1]}/{tot}')

    ck('边引用都存在', all(d['from'] in ids and d['to'] in ids for d in deps))
    ck('先修都已落到 prerequisites',
       all(d['from'] in (t.get('prerequisites') or [])
           for t in topics for d in deps if d['to'] == t['id'] and d['type'] == 'hard'))
    ck('无自环', all(d['from'] != d['to'] for d in deps))

    # 无环
    g = defaultdict(list)
    for d in deps:
        g[d['from']].append(d['to'])
    color = {}

    def dfs(u):
        color[u] = 1
        for v in g.get(u, []):
            if color.get(v) == 1:
                return False
            if color.get(v) is None and not dfs(v):
                return False
        color[u] = 2
        return True

    acyclic = all(dfs(n) for n in list(ids) if color.get(n) is None)
    ck('先修图无环', acyclic)

    ck('课标 quote 覆盖率 ≥90%',
       sum(1 for t in topics if t.get('standards')) / len(topics) >= 0.90,
       f"{sum(1 for t in topics if t.get('standards'))}/{len(topics)}")

    ck('description ≥12 汉字', all(len(re.findall(r'[\u4e00-\u9fa5]', t.get('description', ''))) >= 12
                                 for t in topics))
    ck('课时点都有 misconceptions ≥2 条',
       all(len(t.get('misconceptions') or []) >= 2 for t in lesson_pts))


def main():
    targets = [sys.argv[1]] if len(sys.argv) > 1 else list(EXPECT)
    for s in targets:
        run(s)
    print(f"\n{'ALL PASSED' if not fails else 'FAILED: ' + ', '.join(fails)}")
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
