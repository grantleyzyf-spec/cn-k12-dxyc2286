#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给人教版物理桶补齐 lesson 级节点的 diagnostic_question。

这 204 个课时点在建桶时就漏了该字段（schema 必填，属存量红），不是本次改卷面引入的。
补法不编题：直接取本桶题库中该课时点的一道 basic 选择题，题干与选项拼成诊断题，答案取字母。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics')
T_P = os.path.join(D, 'topics.json')
Q_P = os.path.join(D, 'questions.json')


def main():
    topics = json.load(open(T_P, encoding='utf-8'))
    qs = json.load(open(Q_P, encoding='utf-8'))

    # 每个课时点优先取 basic 选择题，其次任意选择题
    pool = {}
    for q in qs:
        if q.get('type') != 'choice' or not q.get('options'):
            continue
        tid = q['topicId']
        cur = pool.get(tid)
        if cur is None or (cur.get('difficulty') != 'basic' and q.get('difficulty') == 'basic'):
            pool[tid] = q

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

    json.dump(topics, open(T_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('补齐 diagnostic_question：%d 个课时点；无题可用 %d 个' % (filled, skipped))
    return 0 if skipped == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
