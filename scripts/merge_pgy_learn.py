#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 _learn_parts/L*_out.json 按册合并成 data/physics-bsd-gyy/learn/<册>.json。

护栏：
  · 只吃 `*_out.json`（⛔ 不吃作业单 L0NN.json 与 _CONTRACT.md）
  · 篇数必须等于该册课时点数，缺篇整批拒写
  · 原子落盘 tmp → os.replace
用法：python3 scripts/merge_pgy_learn.py
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
PARTS = os.path.join(D, '_learn_parts')
OUT = os.path.join(D, 'learn')


def main():
    topics = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    lessons = [t for t in topics if t['level'] == 'lesson']
    want = {}
    for t in lessons:
        want.setdefault(t['chapter'].split(' ')[0], []).append(t)

    produced = {}
    for p in sorted(glob.glob(os.path.join(PARTS, 'L*_out.json'))):
        d = json.load(open(p, encoding='utf-8'))
        tid = d.get('topicId')
        md = (d.get('markdown') or '').strip()
        if not tid or not md:
            continue
        produced[tid] = d

    errs = []
    for tid in [t['id'] for t in lessons]:
        if tid not in produced:
            errs.append('缺篇 %s' % tid)
    if errs:
        print('✗ 缺篇 %d：%s' % (len(errs), errs[:6]))
        return 1

    os.makedirs(OUT, exist_ok=True)
    total = 0
    for book, ts in want.items():
        arr = []
        for t in ts:
            d = produced[t['id']]
            arr.append({'topicId': t['id'], 'title': t['name'], 'chapter': t['chapter'],
                        'grade': t['grade'], 'domain': t['domain'],
                        'markdown': d['markdown'], 'words': d.get('words')})
        dst = os.path.join(OUT, book + '.json')
        tmp = dst + '.tmp'
        json.dump({'book': book, 'lessons': arr}, open(tmp, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        os.replace(tmp, dst)
        total += len(arr)
        print('写出 learn/%s.json：%d 篇' % (book, len(arr)))
    print('合计 %d 篇（课时点 %d）' % (total, len(lessons)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
