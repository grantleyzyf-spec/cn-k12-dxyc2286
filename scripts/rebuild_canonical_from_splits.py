#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把按学段拆分的学科数据合并成参考仓库口径的单文件：
  topics.json / questions.json / dependencies.json（去重、排序）

背景：math 目录下同时存在 topics.json(24 条旧存根) 与 topics_grade*.json(455 条)、
topics_all.json(479 条)，站点读的是 topics.json ⇒ 只看到 24 个知识点。
本脚本以「拆分文件 + 现有单文件」的并集为准重建单文件。

用法：python3 scripts/rebuild_canonical_from_splits.py [--check|--write]
"""
import argparse, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def dump(p, obj):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def union(subject, stem, keyfn):
    d = os.path.join(DATA, subject)
    parts = [p for p in glob.glob(os.path.join(d, f'{stem}_*.json')) if not p.endswith('_all.json')]
    parts.append(os.path.join(d, f'{stem}.json'))
    seen, out = set(), []
    for p in parts:
        if not os.path.exists(p):
            continue
        for item in load(p):
            k = keyfn(item)
            if k in seen:
                continue
            seen.add(k)
            out.append(item)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    subjects = sorted(d for d in os.listdir(DATA)
                      if os.path.isdir(os.path.join(DATA, d)) and os.path.exists(os.path.join(DATA, d, 'topics.json')))
    changed = False
    for sub in subjects:
        d = os.path.join(DATA, sub)
        splits = glob.glob(os.path.join(d, 'topics_*.json'))
        if not splits:
            continue
        before = len(load(os.path.join(d, 'topics.json')))
        topics = union(sub, 'topics', lambda t: t.get('id'))
        qs = union(sub, 'questions', lambda q: q.get('id') or (q.get('topicId') or q.get('topic_id'), q.get('question') or q.get('prompt') or q.get('stem')))
        deps = union(sub, 'dependencies', lambda x: (x.get('from'), x.get('to'), x.get('type')))
        print(f"{sub}: topics {before} → {len(topics)} | questions → {len(qs)} | dependencies → {len(deps)}")
        if a.write:
            dump(os.path.join(d, 'topics.json'), topics)
            dump(os.path.join(d, 'questions.json'), qs)
            dump(os.path.join(d, 'dependencies.json'), deps)
            changed = True
    print('已写' if changed else '（未写，仅体检）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
