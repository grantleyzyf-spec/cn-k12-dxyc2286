# -*- coding: utf-8 -*-
"""把 _bank/*_out.json 合并成 questions.json（幂等，按 id 去重，原子落盘）。

用法：python3 scripts/merge_chem_editions_bank.py [--subject <bucket>]
"""
import argparse, glob, json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')


def merge(bucket):
    d = os.path.join(DATA, bucket)
    files = sorted(glob.glob(os.path.join(d, '_bank', '*_out.json')))
    topics = {t['id']: t for t in json.load(open(os.path.join(d, 'topics.json'), encoding='utf-8'))}
    seen, qs = set(), []
    for f in files:
        raw = json.load(open(f, encoding='utf-8'))
        items = raw.get('questions') if isinstance(raw, dict) else raw
        for q in items or []:
            if q.get('id') in seen:
                continue
            seen.add(q.get('id'))
            q.setdefault('subject', bucket)
            qs.append(q)
    # 只保留挂在已知点上的题
    orphan = [q['id'] for q in qs if q.get('topicId') not in topics]
    qs = [q for q in qs if q.get('topicId') in topics]
    qs.sort(key=lambda q: (q['topicId'], q['id']))
    out = os.path.join(d, 'questions.json')
    fd, tmp = tempfile.mkstemp(dir=d, suffix='.tmp')
    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
        json.dump(qs, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    covered = len({q['topicId'] for q in qs})
    return len(files), len(qs), covered, len(topics), orphan


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject')
    a = ap.parse_args()
    buckets = [a.subject] if a.subject else ['chemistry-lujiao', 'chemistry-luke']
    for b in buckets:
        nf, nq, cov, tot, orphan = merge(b)
        print('%s：分片 %d → 题 %d ｜ 覆盖点 %d/%d ｜ 孤儿题 %d' % (b, nf, nq, cov, tot, len(orphan)))
        if orphan:
            print('  孤儿题号', orphan[:5])
