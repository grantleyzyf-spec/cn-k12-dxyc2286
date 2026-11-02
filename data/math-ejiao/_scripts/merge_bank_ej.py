#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版高中数学 · 合并器：_skeleton.json + _bank/<tag>.json → topics / questions / dependencies

只落 schema 允许字段（additionalProperties:false）；缺 bank 的册落缺口清单。
"""
import glob, json, os, re

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
SUBJECT = "math-ejiao"
OUT = os.path.join(REPO, "data", SUBJECT)

TOPIC_FIELDS = {'id', 'name', 'subject', 'domain', 'grade', 'semester', 'chapter', 'type',
                'description', 'mastery_criteria', 'diagnostic_question', 'external',
                'standards', 'tags', 'prerequisites', 'curriculumRef', 'verified',
                'root_reason', 'page', 'misconceptions', 'prereqUpper'}
Q_FIELDS = {'id', 'topicId', 'prompt', 'question', 'options', 'answer', 'type',
            'difficulty', 'explanation', 'verify', 'subject', 'choices', 'keypoints'}


def type_of(name):
    for t, pat in (('procedural', r'运算|计算|化简|求值|解方程|求导|求通项|求和'),
                   ('application', r'应用|模型|实际问题|估计|检验|决策'),
                   ('reasoning', r'证明|推理|判断|探究|性质')):
        if re.search(pat, name):
            return t
    return 'conceptual'


def main():
    skel = json.load(open(os.path.join(OUT, '_skeleton.json'), encoding='utf-8'))
    deps = json.load(open(os.path.join(OUT, '_deps.json'), encoding='utf-8'))
    pre = {}
    for d in deps:
        pre.setdefault(d['to'], []).append(d['from'])

    STD = {}
    _sp = os.path.join(OUT, '_std_map.json')
    if os.path.isfile(_sp):
        STD = json.load(open(_sp, encoding='utf-8'))

    topics, questions, lack = [], [], []
    # 章级分片：_bank/c01.json … c20.json 一次收齐（每片一章）
    up, lp = {}, {}
    cfiles = sorted(glob.glob(os.path.join(OUT, '_bank', 'c*.json')))
    for fp in cfiles:
        b = json.load(open(fp, encoding='utf-8'))
        for x in b.get('unit_points', []):
            up[x['id']] = x
        for x in b.get('lesson_points', []):
            lp[x['id']] = x
    if not cfiles:
        lack.append('整库缺 _bank/c*.json')
    for v in skel['volumes']:
        for u in v['units']:
            rows = [('unit', u['unit_id'], re.sub(r'^第\\d+章\\s*', '', u['unit_name']), u['unit_chapter'], None, up)]
            rows += [('lesson', l['id'], l['name'], l['chapter'], l.get('page'), lp) for l in u['lessons']]
            for kind, tid, name, chapter, page, objs in rows:
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
                t = {'id': tid, 'name': name, 'subject': SUBJECT, 'domain': u['domain'],
                     'grade': v['grade'], 'semester': v['semester'], 'chapter': chapter,
                     'type': o.get('type') or type_of(name),
                     'description': o.get('description', ''),
                     'mastery_criteria': o.get('mastery_criteria') or [],
                     'diagnostic_question': dq, 'external': False,
                     'standards': (STD.get(tid) or o.get('standards') or []),
                     'tags': o.get('tags') or [u['domain'], u['unit_name']],
                     'prerequisites': sorted(pre.get(tid, [])),
                     'curriculumRef': (o.get('standards') or [{}])[0].get('id', '') if o.get('standards') else '',
                     'verified': False}
                if page is not None:
                    t['page'] = page
                if o.get('misconceptions'):
                    t['misconceptions'] = o['misconceptions']
                if not t['prerequisites']:
                    t['root_reason'] = f"起始知识点：{chapter} 在全册图谱内无更早前置（跨学段前置不单独连边）"
                topics.append({k: val for k, val in t.items() if k in TOPIC_FIELDS})
                for q in qs:
                    qq = dict(q)
                    qq['subject'] = SUBJECT
                    qq['answer'] = str(qq.get('answer', ''))
                    qq.setdefault('question', qq.get('prompt', ''))
                    if qq.get('type') == 'choice':
                        qq.setdefault('choices', qq.get('options'))
                    questions.append({k: val for k, val in qq.items() if k in Q_FIELDS})

    ids = {t['id'] for t in topics}
    deps_ok = [d for d in deps if d['from'] in ids and d['to'] in ids]
    json.dump(topics, open(os.path.join(OUT, 'topics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(questions, open(os.path.join(OUT, 'questions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(deps_ok, open(os.path.join(OUT, 'dependencies.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'知识点 {len(topics)}｜题 {len(questions)}｜边 {len(deps_ok)}（丢弃悬空边 {len(deps)-len(deps_ok)}）')
    if lack:
        print('缺口：')
        for x in lack[:40]:
            print('  -', x)
        if len(lack) > 40:
            print(f'  …共 {len(lack)} 处')


if __name__ == '__main__':
    main()
