# -*- coding: utf-8 -*-
"""湘教版地理：试卷讲解分片（一片一卷，同卷不跨片）。"""
import glob, json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data', 'geography-xiangjiao')
SD = os.path.join(D, '_lecture_shards')
os.makedirs(SD, exist_ok=True)
for f in glob.glob(SD + '/GXJ_K*.json'):
    os.remove(f)

papers = sorted(glob.glob(D + '/exams/*/*.json'))
idx = []
for i, p in enumerate(papers, 1):
    d = json.load(open(p, encoding='utf-8'))
    tag = f'GXJ_K{i:02d}'
    item = {'examId': d['examId'], 'book': d['book'], 'paper': d['paper'], 'kind': d['kind'],
            'stage': d['stage'],
            'examPath': f'data/geography-xiangjiao/exams/{d["book"]}/{d["paper"]}.json',
            'outPath': f'data/geography-xiangjiao/exam_lectures/{d["book"]}/{d["paper"]}.json'}
    json.dump({'shard': tag, 'subject': 'geography-xiangjiao', 'edition': '湘教版', 'papers': [item]},
              open(f'{SD}/{tag}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    idx.append({'shard': tag, 'book': d['book'], 'paper': d['paper'], 'examId': d['examId']})

json.dump(idx, open(f'{SD}/_INDEX.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
names = [(x['book'], x['paper']) for x in idx]
assert len(set(names)) == len(names), '同册卷名重复'
assert len({x['examId'] for x in idx}) == len(idx), 'examId 重复'
print('讲解分片', len(idx), '/ 卷', len(papers))
