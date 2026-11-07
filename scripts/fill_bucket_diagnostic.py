#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用：给某物理桶补齐缺失的 diagnostic_question（取本桶 basic 选择题）。

用法：python3 scripts/fill_bucket_diagnostic.py physics-sk [physics-yj ...]
不编题：题干与选项直接来自该点自己的题库题目，答案取字母。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fill(bucket):
    d = os.path.join(ROOT, 'data', bucket)
    tp, qp = os.path.join(d, 'topics.json'), os.path.join(d, 'questions.json')
    topics = json.load(open(tp, encoding='utf-8'))
    qs = json.load(open(qp, encoding='utf-8'))
    pool = {}
    for q in qs:
        if q.get('type') != 'choice' or not q.get('options'):
            continue
        cur = pool.get(q['topicId'])
        if cur is None or (cur.get('difficulty') != 'basic' and q.get('difficulty') == 'basic'):
            pool[q['topicId']] = q
    filled = skipped = 0
    for t in topics:
        if t.get('diagnostic_question'):
            continue
        q = pool.get(t['id'])
        if not q:
            skipped += 1
            print('  ! 无选择题可用：', t['id'], t['name'])
            continue
        stem = (q.get('question') or q.get('prompt') or '').strip().rstrip('。')
        opts = '；'.join('%s %s' % (o['label'], o['text']) for o in q['options'])
        t['diagnostic_question'] = {'question': '%s：%s' % (stem, opts), 'answer': q['answer']}
        filled += 1
    json.dump(topics, open(tp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%s：补齐 %d 个点，无题可用 %d 个' % (bucket, filled, skipped))
    return skipped


if __name__ == '__main__':
    bad = 0
    for b in sys.argv[1:]:
        bad += fill(b)
    sys.exit(0 if bad == 0 else 1)
