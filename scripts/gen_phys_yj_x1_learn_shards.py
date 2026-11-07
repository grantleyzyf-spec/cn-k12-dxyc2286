#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只给 physics-yj 的「选择性必修第一册」补学层分片（2 节/片）。

excerpt 取法：标题在全书里做「去空白」匹配，取其后 700 字里句末标点最多的一处
（目录行句末标点≈0），再剥掉开头残留的目录行。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-yj')
BOOK = '选择性必修第一册'
TEXT = os.path.join(D, '_text', BOOK + '.txt')
OUT = os.path.join(D, '_learn_shards')


def flat_positions(text, title):
    key = re.sub(r'\s+', '', title)
    idx_map, buf = {}, []
    for j, ch in enumerate(text):
        if not ch.isspace():
            idx_map[len(buf)] = j
            buf.append(ch)
    flat = ''.join(buf)
    pos, i = [], flat.find(key)
    while i >= 0:
        pos.append(idx_map[i])
        i = flat.find(key, i + 1)
    return [p for p in pos if p > 300]


def prose(p, text):
    return len(re.findall(r'[。！？]', text[p:p + 700]))


CURSOR = [5000]      # 目录在前 5 000 字内；正文按课时顺序向后推进


def excerpt(text, title, want=1200):
    cands = [p for p in flat_positions(text, title) if p > CURSOR[0]]
    if not cands:
        cands = [p for p in flat_positions(text, title) if p > 5000] or flat_positions(text, title)
    if not cands:
        return ''
    p = min(cands)
    CURSOR[0] = p + 200
    seg = text[p:p + want + 400]
    cut = seg.find('\n\n', want)
    seg = seg[:cut] if cut > 0 else seg[:want]
    lines = seg.split('\n')
    i = 0
    while i < len(lines) and i < 60:
        l = lines[i].strip()
        if not l or re.fullmatch(r'[0-9]+', l) or (len(l) <= 30 and not re.search(r'[。，？！；：]', l)):
            i += 1
            continue
        break
    return '\n'.join(lines[i:]).strip()[:want]


def main():
    text = open(TEXT, encoding='utf-8').read()
    topics = json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8'))
    les = [t for t in topics
           if (t.get('chapter') or '').startswith(BOOK) and t.get('level') == 'lesson']
    les.sort(key=lambda t: t['id'])
    n = 0
    made = 0
    for i in range(0, len(les), 2):
        n += 1
        group = les[i:i + 2]
        shard = {
            'shard': 'LY%02d' % n,
            'bucket': 'physics-yj',
            'book': BOOK,
            'text_file': 'data/physics-yj/_text/%s.txt' % BOOK,
            'lessons': [],
        }
        for t in group:
            ex = excerpt(text, t['name'])
            if not ex:
                print('  ! excerpt 空:', t['id'], t['name'])
            shard['lessons'].append({
                'topicId': t['id'], 'title': t['name'], 'chapter': t.get('chapter'),
                'description': t.get('description'),
                'mastery_criteria': t.get('mastery_criteria'),
                'standards': t.get('standards'), 'excerpt': ex,
            })
        json.dump(shard, open(os.path.join(OUT, shard['shard'] + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        made += len(group)
    print('生成 %d 个分片 / %d 篇（%s）' % (n, made, BOOK))


if __name__ == '__main__':
    sys.exit(main())
