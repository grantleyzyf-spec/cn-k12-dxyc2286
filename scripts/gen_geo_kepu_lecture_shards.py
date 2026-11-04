# -*- coding: utf-8 -*-
"""科普版地理：试卷讲解分片（每片 2 卷，同册不跨片）。"""
import glob, json, os, re
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data', 'geography-kepu')
SD = os.path.join(D, '_lecture_shards'); os.makedirs(SD, exist_ok=True)
for f in glob.glob(SD + '/GKP_K*.json'):
    os.remove(f)
papers = sorted(glob.glob(D + '/exams/*/*.json'))
shards, cur, n = [], [], 0
for p in papers:
    d = json.load(open(p, encoding='utf-8'))
    item = {'examId': d['examId'], 'book': d['book'], 'paper': d['paper'], 'kind': d['kind'],
            'stage': d['stage'],
            'examPath': f'data/geography-kepu/exams/{d["book"]}/{d["paper"]}.json',
            'outPath': f'data/geography-kepu/exam_lectures/{d["book"]}/{d["paper"]}.json'}
    if cur and (cur[0]['book'] != item['book'] or len(cur) >= 2):
        shards.append(cur); cur = []
    cur.append(item)
if cur:
    shards.append(cur)
idx = []
for i, grp in enumerate(shards, 1):
    tag = f'GKP_K{i:02d}'
    json.dump({'shard': tag, 'subject': 'geography-kepu', 'edition': '科普版', 'papers': grp},
              open(f'{SD}/{tag}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    idx.append({'shard': tag, 'book': grp[0]['book'], 'papers': [x['paper'] for x in grp]})
json.dump(idx, open(f'{SD}/_INDEX.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('讲解分片', len(idx), '/ 卷', len(papers))
