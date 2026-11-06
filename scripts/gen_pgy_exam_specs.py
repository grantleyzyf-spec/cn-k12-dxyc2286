#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版（郭玉英）初中物理 出卷规格生成器（28 卷）。

卷制写死（初中 120 分 / 120 分钟 / 24 题，不现算）：
  一、选择题 12×3 = 36
  二、填空题 6×4 = 24
  三、实验探究题 3×8 = 24
  四、计算与应用题 3×12 = 36
合计 24 题 / 120 分。

卷数 = 每章单元卷 16 + 每册期中 A/B 与期末 A/B（3 册 × 4）= 28。
期中 scope = 该册**前一半章**（按章号解析后取前 ceil(n/2)）；期末 = 全册。

产物：data/physics-bsd-gyy/_exam_spec/<examId>.json
用法：python3 scripts/gen_pgy_exam_specs.py [--only <examId>]
"""
import argparse
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
SPEC = os.path.join(D, '_exam_spec')

BOOK_CODE = {'八年级上册': '8a', '八年级下册': '8b', '九年级全一册': '9a'}

SECTIONS = [
    ('一、选择题', 12, 3),
    ('二、填空题', 6, 4),
    ('三、实验探究题', 3, 8),
    ('四、计算与应用题', 3, 12),
]
CN = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


def cn_no(n):
    return CN[n] if n <= 10 else '十' + CN[n - 10]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    a = ap.parse_args()
    topics = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    os.makedirs(SPEC, exist_ok=True)

    chapters = []  # (book, ch_no, ch_name, unit_id, [lesson ids])
    seen = {}
    for t in topics:
        head, _, tail = t['chapter'].partition(' · ')
        book, _, rest = head.partition(' ')
        ch_no = int(rest.split('第')[1].split('章')[0]) if '第' in rest else 0
        ch_name = rest.split(' ', 1)[1] if ' ' in rest else rest
        key = (book, ch_no)
        if key not in seen:
            seen[key] = {'book': book, 'no': ch_no, 'name': ch_name,
                         'unit': t['id'] if t['level'] == 'unit' else None, 'lessons': []}
            chapters.append(seen[key])
        if t['level'] == 'lesson':
            seen[key]['lessons'].append(t['id'])

    jobs = []
    for c in chapters:
        code = BOOK_CODE[c['book']]
        points = ([c['unit']] if c['unit'] else []) + c['lessons']
        jobs.append({
            'examId': 'pgy_exam_%s_u%02d' % (code, c['no']),
            'kind': 'unit', 'book': c['book'], 'grade': 8 if c['book'].startswith('八') else 9,
            'paper': '第%s章 %s 测试卷' % (cn_no(c['no']), c['name']),
            'scope': ['%s 第%d章 %s' % (c['book'], c['no'], c['name'])],
            'topicIds': points, 'sections': SECTIONS, 'fullScore': 120, 'duration': 120,
        })

    for book in BOOK_CODE:
        chs = [c for c in chapters if c['book'] == book]
        chs.sort(key=lambda x: x['no'])
        half = math.ceil(len(chs) / 2)
        code = BOOK_CODE[book]
        grade = 8 if book.startswith('八') else 9
        for kind, sub, label in (('mid', 'a', '期中测试卷A'), ('mid', 'b', '期中测试卷B'),
                                 ('fin', 'a', '期末测试卷A'), ('fin', 'b', '期末测试卷B')):
            sel = chs[:half] if kind == 'mid' else chs
            points = []
            for c in sel:
                points.append(c['unit']) if c['unit'] else None
                points.extend(c['lessons'])
            jobs.append({
                'examId': 'pgy_exam_%s_q%s%s' % (code, 'z' if kind == 'mid' else 'm', sub),
                'kind': kind, 'book': book, 'grade': grade,
                'paper': '%s %s' % (book, label),
                'scope': ['%s 第%d章 %s' % (c['book'], c['no'], c['name']) for c in sel],
                'topicIds': points, 'sections': SECTIONS, 'fullScore': 120, 'duration': 120,
            })

    n = 0
    for j in jobs:
        if a.only and j['examId'] != a.only:
            continue
        p = os.path.join(SPEC, j['examId'] + '.json')
        json.dump(j, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        n += 1
    print('生成 %d 卷（单元 %d / 期中 %d / 期末 %d）'
          % (n, sum(1 for j in jobs if j['kind'] == 'unit'),
             sum(1 for j in jobs if j['kind'] == 'mid'), sum(1 for j in jobs if j['kind'] == 'fin')))
    ids = [j['examId'] for j in jobs]
    assert len(set(ids)) == len(ids), 'examId 撞号'
    mid = [j['scope'] for j in jobs if j['kind'] == 'mid' and j['book'] == '九年级全一册']
    fin = [j['scope'] for j in jobs if j['kind'] == 'fin' and j['book'] == '九年级全一册']
    print('九全 期中覆盖 %d 章 / 期末覆盖 %d 章（期中必须更少）' % (len(mid[0]), len(fin[0])))


if __name__ == '__main__':
    main()
