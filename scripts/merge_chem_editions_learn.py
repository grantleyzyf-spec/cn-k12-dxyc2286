# -*- coding: utf-8 -*-
"""把 learn/_parts/<册>/*.json 合并成 learn/<册>.json（按 topics.json 课序）。

用法：python3 scripts/merge_chem_editions_learn.py <chemistry-lujiao|chemistry-luke>
"""
import json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = sys.argv[1] if len(sys.argv) > 1 else 'chemistry-lujiao'
D = os.path.join(REPO, 'data', BUCKET)
T = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
order = {t['id']: i for i, t in enumerate(T)}
books = {}
for t in T:
    if t['level'] == 'lesson':
        books.setdefault(t['chapter'].split(' ')[0], []).append(t['id'])

tot = 0
for book, ids in books.items():
    pd = os.path.join(D, 'learn', '_parts', book)
    got = []
    for tid in ids:
        p = os.path.join(pd, tid + '.json')
        if not os.path.exists(p):
            continue
        obj = json.load(open(p, encoding='utf-8'))
        les = obj['lessons'] if isinstance(obj, dict) and 'lessons' in obj else [obj]
        for x in les:
            if x.get('topicId') == tid:
                got.append({'topicId': tid, 'title': x.get('title'), 'words': x.get('words'),
                            'markdown': x.get('markdown')})
    if not got:
        continue
    os.makedirs(os.path.join(D, 'learn'), exist_ok=True)
    out = os.path.join(D, 'learn', book + '.json')
    json.dump({'book': book, 'lessons': got}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot += len(got)
    print('%-16s %-5s 篇 %2d / 应 %2d' % (BUCKET, book, len(got), len(ids)))
print('%s 学层合计 %d 篇' % (BUCKET, tot))
