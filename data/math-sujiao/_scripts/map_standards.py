#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 topics.json 补课标 quote（逐字来自课标 TXT，可回表核验）

用法：python3 map_standards.py --subject math-sujiao [--dry]

做法：
1. 读义务教育数学课标 / 高中数学课标 TXT，按句切分（。；换行），保留 12–60 字句；
2. 每个知识点按「名称 + 单元名」与候选句做 2-gram 重叠打分，取最高分；
3. standards = [{id, confidence:"inferred", quote, sourceLine}]；
   id 形如 mat-2022:{学段}.{bucket}.{序号}（学段 1–4 = 1-2/3-4/5-6/7-9 年级；bucket 由 domain 定），
   高中用 mat-2017:G.{bucket}.{序号}；
4. 自检：去空白后 quote 必须是课标原文子串，逐条统计命中率。
"""
import argparse
import json
import os
import re

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
YJ = os.path.expanduser('~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/'
                        '3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt')
GZ = os.path.expanduser('~/Desktop/中小学教材/2025修订课程标准TXT /高中教育/'
                        '（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt')

BUCKET = {'数与代数': 'XY', '图形与几何': 'NR', '统计与概率': 'TS',
          '综合与实践': 'MB', '函数': 'NR', '几何与代数': 'XY'}


def sentences(path):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    lines = txt.split('\n')
    out = []
    for i, ln in enumerate(lines):
        for s in re.split(r'(?<=[。；;])', ln):
            s = s.strip().strip('　 ')
            if 12 <= len(re.sub(r'\s', '', s)) <= 60 and re.search(r'[\u4e00-\u9fa5]{6,}', s):
                out.append((s, i + 1))
    return out, re.sub(r'\s', '', txt)


def grams(s, n=2):
    s = re.sub(r'[^\u4e00-\u9fa5]', '', s)
    return {s[i:i + n] for i in range(len(s) - n + 1)} if len(s) >= n else set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subject', required=True)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    d = os.path.join(REPO, 'data', a.subject)
    topics = json.load(open(os.path.join(d, 'topics.json'), encoding='utf-8'))

    yj, yj_flat = sentences(YJ)
    gz, gz_flat = sentences(GZ)

    seq = {}
    filled = miss = 0
    for t in topics:
        grade = t.get('grade') or 1
        high = grade >= 10
        pool, flat = (gz, gz_flat) if high else (yj, yj_flat)
        stage = 'G' if high else str(1 if grade <= 2 else 2 if grade <= 4 else 3 if grade <= 6 else 4)
        bucket = BUCKET.get(t.get('domain', ''), 'XY')
        target = grams(' '.join([t['name'], t.get('chapter', '').split('·')[-1]]))
        best, best_sc = None, 0
        for s, ln in pool:
            g = grams(s)
            if not g:
                continue
            sc = len(target & g) / (len(g) ** 0.5 + 1)
            if sc > best_sc:
                best, best_sc = (s, ln), sc
        if not best or best_sc <= 0:
            miss += 1
            continue
        quote, ln = best
        key = (stage, bucket)
        seq[key] = seq.get(key, 0) + 1
        sid = (f'mat-2017:G.{bucket}.{seq[key]:02d}' if high
               else f'mat-2022:{stage}.{bucket}.{seq[key]:02d}')
        t['standards'] = [{'id': sid, 'confidence': 'inferred',
                           'quote': quote, 'sourceLine': ln}]
        t['curriculumRef'] = sid
        if re.sub(r'\s', '', quote) in flat:
            filled += 1
        else:
            t['standards'][0]['confidence'] = 'partial'

    print(f'{a.subject}: 知识点 {len(topics)}｜课标命中 {filled}｜未匹配 {miss}')
    if not a.dry:
        json.dump(topics, open(os.path.join(d, 'topics.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('已写回 topics.json')


if __name__ == '__main__':
    main()
