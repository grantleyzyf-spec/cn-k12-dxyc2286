#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏教版数学 · 合并器：_skeleton.json + _bank/<tag>.json → topics.json / questions.json

只放 schema 允许的字段（additionalProperties: false），辅助字段一律丢弃。
若某册缺 bank，该册不落库并在末尾打印缺口清单。
"""
import glob
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SUBJECT = 'math-sujiao'
if '--subject' in sys.argv:
    SUBJECT = sys.argv[sys.argv.index('--subject') + 1]
OUT = os.path.join(REPO, 'data', SUBJECT)

TOPIC_FIELDS = {'id', 'name', 'subject', 'domain', 'grade', 'semester', 'chapter', 'type',
                'description', 'mastery_criteria', 'diagnostic_question', 'external',
                'standards', 'tags', 'prerequisites', 'curriculumRef', 'verified',
                'root_reason', 'page', 'misconceptions', 'prereqUpper'}
Q_FIELDS = {'id', 'topicId', 'prompt', 'question', 'options', 'answer', 'type',
            'difficulty', 'explanation', 'verify', 'subject', 'choices', 'keypoints'}
DEVICE = {'小学': 100, '初中': 120, '高中': 150}


def type_of(name):
    for t, pat in ((('procedural'), r'计算|运算|解方程|化简|求值|口算|笔算|竖式|加减|乘除'),
                   ('application', r'解决问题|实际问题|应用|比例|百分数|利息|折扣'),
                   ('reasoning', r'探索|规律|猜想|推理|证明')):
        if isinstance(t, tuple):
            t = t[0]
        if re.search(pat, name):
            return t
    return 'conceptual'


def main():
    skel = json.load(open(os.path.join(OUT, '_skeleton.json'), encoding='utf-8'))
    deps = json.load(open(os.path.join(OUT, '_deps.json'), encoding='utf-8'))
    pre = {}
    for d in deps:
        pre.setdefault(d['to'], []).append(d['from'])

    topics, questions, lack = [], [], []
    for v in skel['volumes']:
        parts = sorted(glob.glob(os.path.join(OUT, '_bank', f"{v['tag']}.part*.json")))
        single = os.path.join(OUT, '_bank', f"{v['tag']}.json")
        files = parts if parts else ([single] if os.path.isfile(single) else [])
        if not files:
            lack.append(v['tag'])
            continue
        bank = {'unit_points': [], 'lesson_points': []}
        for fp in files:
            b = json.load(open(fp, encoding='utf-8'))
            bank['unit_points'] += b.get('unit_points', [])
            bank['lesson_points'] += b.get('lesson_points', [])
        up = {x['id']: x for x in bank.get('unit_points', [])}
        lp = {x['id']: x for x in bank.get('lesson_points', [])}
        for u in v['units']:
            for kind, tid, name, chapter, page, objs in [
                ('unit', u['unit_id'], u['unit_name'], u['unit_chapter'], None, up),
                *[('lesson', l['id'], l['sec_name'], l['chapter'], l.get('page'), lp)
                  for l in u['lessons']]]:
                o = objs.get(tid)
                if not o:
                    lack.append(f"{v['tag']}:{tid} 缺内容")
                    continue
                qs = o.get('questions') or []
                dq = next(({'question': q.get('prompt', ''), 'answer': str(q.get('answer', ''))}
                           for q in qs if q.get('type') == 'choice'), None)
                if not dq:
                    dq = {'question': qs[0].get('prompt', '') if qs else '',
                          'answer': str(qs[0].get('answer', '')) if qs else ''}
                t = {
                    'id': tid,
                    'name': name,
                    'subject': 'math',
                    'domain': u['domain'],
                    'grade': v['grade'],
                    'semester': v['semester'],
                    'chapter': chapter,
                    'type': o.get('type') or type_of(name),
                    'description': o.get('description', ''),
                    'mastery_criteria': o.get('mastery_criteria') or [],
                    'diagnostic_question': dq,
                    'external': False,
                    'standards': o.get('standards') or [],
                    'tags': o.get('tags') or [u['domain'], u['unit_name']],
                    'prerequisites': sorted(pre.get(tid, [])),
                    'curriculumRef': (o.get('standards') or [{}])[0].get('id', '') if o.get('standards') else '',
                    'verified': False,
                }
                if page is not None:
                    t['page'] = page
                if o.get('misconceptions'):
                    t['misconceptions'] = o['misconceptions']
                if not t['prerequisites']:
                    t['root_reason'] = (f"起始知识点：{chapter} 在全册图谱内无更早前置"
                                        f"（跨学段前置不单独连边）")
                topics.append({k: val for k, val in t.items() if k in TOPIC_FIELDS})
                for q in qs:
                    qq = dict(q)
                    qq['subject'] = 'math'
                    qq.setdefault('question', qq.get('prompt', ''))
                    if qq.get('type') == 'choice':
                        qq.setdefault('choices', qq.get('options'))
                    questions.append({k: val for k, val in qq.items() if k in Q_FIELDS})

    json.dump(topics, open(os.path.join(OUT, 'topics.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(questions, open(os.path.join(OUT, 'questions.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(deps, open(os.path.join(OUT, 'dependencies.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    ids = {t['id'] for t in topics}
    deps_ok = [d for d in deps if d['from'] in ids and d['to'] in ids]
    dropped = len(deps) - len(deps_ok)
    json.dump(deps_ok, open(os.path.join(OUT, 'dependencies.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print(f'知识点 {len(topics)}｜题 {len(questions)}｜边 {len(deps_ok)}'
          f'（丢弃悬空边 {dropped}）')
    if lack:
        print('缺口：')
        for x in lack:
            print('  -', x)


if __name__ == '__main__':
    main()
