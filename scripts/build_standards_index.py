#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由数据本身构建两份索引（不引入任何外部内容）：

1. data/cn-curriculum-standards.json
   课标条目索引：每条课标编号 → 覆盖的知识点数、年级、置信度分布。
   与参考仓库同名文件对齐（他们存课标原文，我们存「本库实际引用的条目索引」）。

2. data/mappings/volume-map.json
   册次地图：学科 → 册（一年级上册 / 必修第一册 / …）→ 知识点数、年级、单元列表。
   这是「教材版本 × 册次 → 知识点」映射里可自动生成的那一半；
   其它版本（沪教版、山东五四制…）需要人工给出课次对应，见 data/mappings/README.md。

用法：python3 scripts/build_standards_index.py [--check]
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

VOLUME_RE = re.compile(r'^(未分章|(?:一|二|三|四|五|六|七|八|九|十|十一|十二)?年级[上下]册|必修[一二三四五]?[上册]*|选择性必修[一二三]?[上册]*|必修第[一二三四五]册)')


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def dump(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def std_ids(t):
    ids = []
    for s in (t.get('standards') or []):
        if isinstance(s, dict) and s.get('id'):
            ids.append((s['id'], s.get('confidence') or 'exact'))
    if not ids and t.get('curriculumRef'):
        ids.append((t['curriculumRef'], 'exact'))
    return ids


def volume_of(chapter):
    chapter = (chapter or '').strip()
    m = VOLUME_RE.match(chapter)
    if m:
        return m.group(1)
    return chapter.split(' ')[0] if chapter else '未分册'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    src = load(os.path.join(DATA, 'curriculum-standards.json')).get('source', {})
    subjects = sorted(d for d in os.listdir(DATA)
                      if os.path.isdir(os.path.join(DATA, d)) and os.path.exists(os.path.join(DATA, d, 'topics.json')))

    out = {'source': src,
           'generated_from': 'data/<subject>/topics.json（本库实际引用的课标条目索引，非课标原文）',
           'subjects': {}}
    volumes = {'generated_from': 'data/<subject>/topics.json 的 chapter 字段',
               'subjects': {}}
    totals = Counter()

    for sub in subjects:
        topics = load(os.path.join(DATA, sub, 'topics.json'))
        by_std = defaultdict(lambda: {'topicIds': [], 'grades': set(), 'confidence': Counter()})
        by_vol = defaultdict(lambda: {'topicCount': 0, 'grades': set(), 'chapters': set()})
        covered = 0
        for t in topics:
            ids = std_ids(t)
            if ids:
                covered += 1
            for sid, conf in ids:
                e = by_std[sid]
                e['topicIds'].append(t['id'])
                e['grades'].add(t.get('grade'))
                e['confidence'][conf] += 1
            v = volume_of(t.get('chapter'))
            b = by_vol[v]
            b['topicCount'] += 1
            b['grades'].add(t.get('grade'))
            ch = (t.get('chapter') or '').strip()
            if ch:
                b['chapters'].add(ch)

        entries = []
        for sid, e in sorted(by_std.items()):
            entries.append({'id': sid,
                            'topicCount': len(e['topicIds']),
                            'topicIds': sorted(e['topicIds']),
                            'grades': sorted(g for g in e['grades'] if g is not None),
                            'confidence': dict(e['confidence'])})
        out['subjects'][sub] = {'entryCount': len(entries),
                                'topicsWithStandard': covered,
                                'topicsTotal': len(topics),
                                'entries': entries}

        vols = {}
        for v, b in sorted(by_vol.items()):
            vols[v] = {'topicCount': b['topicCount'],
                       'grades': sorted(g for g in b['grades'] if g is not None),
                       'chapterCount': len(b['chapters'])}
        volumes['subjects'][sub] = vols

        totals['entries'] += len(entries)
        totals['topics'] += len(topics)
        totals['covered'] += covered

    out['totals'] = {'subjects': len(subjects), 'entries': totals['entries'],
                     'topics': totals['topics'], 'topicsWithStandard': totals['covered']}

    print(f"课标条目索引：{len(subjects)} 学科 / {totals['entries']} 条目 / 覆盖 {totals['covered']}/{totals['topics']} 知识点")
    for sub in subjects:
        s = out['subjects'][sub]
        if s['topicsWithStandard'] < s['topicsTotal']:
            print(f"  ⚠ {sub}: {s['topicsWithStandard']}/{s['topicsTotal']} 有课标引用（缺口 {s['topicsTotal']-s['topicsWithStandard']}）")

    if not a.check:
        dump(os.path.join(DATA, 'cn-curriculum-standards.json'), out)
        dump(os.path.join(DATA, 'mappings', 'volume-map.json'), volumes)
        print('已写 data/cn-curriculum-standards.json 与 data/mappings/volume-map.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
