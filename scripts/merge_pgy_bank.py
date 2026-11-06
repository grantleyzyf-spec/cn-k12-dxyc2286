#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 _bank/*_out.json 合并成 questions.json，并回写 topics.json 的内容字段（幂等）。

规则：
  · 只吃 `*_out.json`（⛔ 不吃作业单 S0NN.json）
  · 每个点的题量必须恰好等于作业单 `need`（8 / 5），不等整批拒写
  · 题号必须在作业单 `id_range` 内、且全库唯一
  · 分片 `topics[]` 的 description / mastery_criteria / diagnostic_question 回写 topics.json
  · 原子落盘（tmp → os.replace）；护栏：现有题数 > 本次合并数时拒写

用法：python3 scripts/merge_pgy_bank.py [--force]
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()

    tpath = os.path.join(D, 'topics.json')
    qpath = os.path.join(D, 'questions.json')
    topics = json.load(open(tpath, encoding='utf-8'))
    tmap = {t['id']: t for t in topics}
    specs = {}
    for p in glob.glob(os.path.join(D, '_bank_spec', 'S*.json')):
        s = json.load(open(p, encoding='utf-8'))
        specs[s['shard']] = s

    outs = sorted(glob.glob(os.path.join(D, '_bank', '*_out.json')))
    if not outs:
        print('没有分片产物')
        return 1

    errs, questions, seen_ids, filled = [], [], set(), set()
    by_topic = {}
    for f in outs:
        sid = os.path.basename(f).replace('_out.json', '')
        spec = specs.get(sid)
        if not spec:
            errs.append('%s 无对应作业单' % sid)
            continue
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            errs.append('%s 解析失败：%s' % (sid, e))
            continue
        if isinstance(d, list):
            d = {'shard': sid, 'topics': [], 'questions': d}
        need_by = {it['topicId']: it['need'] for it in spec['items']}
        idr = set(spec['id_range'])

        for tp in d.get('topics') or []:
            tid = tp.get('topicId')
            if tid in tmap:
                t = tmap[tid]
                for k in ('description', 'mastery_criteria', 'diagnostic_question'):
                    if tp.get(k):
                        t[k] = tp[k]
                if len(t.get('mastery_criteria') or []) > 3:
                    t['mastery_criteria'] = t['mastery_criteria'][:3]
                    print('  ! %s mastery_criteria 超 3 条，已截断' % tid)
                filled.add(tid)

        for q in d.get('questions') or []:
            qid = q.get('id')
            if qid in seen_ids:
                errs.append('%s 题号重复 %s' % (sid, qid))
                continue
            if qid not in idr:
                errs.append('%s 题号 %s 不在作业单区间' % (sid, qid))
            if q.get('topicId') not in need_by:
                errs.append('%s 题目挂到非本片知识点 %s' % (sid, q.get('topicId')))
            seen_ids.add(qid)
            questions.append(q)
            by_topic[q.get('topicId')] = by_topic.get(q.get('topicId'), 0) + 1

    # 题量对表（只对已交付的点校验）
    for sid, spec in specs.items():
        for it in spec['items']:
            got = by_topic.get(it['topicId'])
            if got is None:
                continue
            if got != it['need']:
                errs.append('%s %s 题量 %d ≠ %d' % (sid, it['topicId'], got, it['need']))

    if errs:
        print('✗ 合并拒绝（%d 项）' % len(errs))
        for e in errs[:15]:
            print('  -', e)
        return 1

    if os.path.exists(qpath) and not a.force:
        old = json.load(open(qpath, encoding='utf-8'))
        if len(old) > len(questions):
            print('✗ 现有 questions.json 有 %d 题 > 本次 %d，疑似分片缺失；确认无误加 --force'
                  % (len(old), len(questions)))
            return 1

    tmp = qpath + '.tmp'
    json.dump(questions, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, qpath)

    tmp = tpath + '.tmp'
    json.dump(topics, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, tpath)

    print('合并完成：分片 %d，题 %d，点数 %d，回写内容点 %d'
          % (len(outs), len(questions), len(topics), len(filled)))
    import collections
    print('题型：', dict(collections.Counter(q['type'] for q in questions)))
    print('难度：', dict(collections.Counter(q['difficulty'] for q in questions)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
