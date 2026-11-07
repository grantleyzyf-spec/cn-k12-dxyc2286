#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修 ID 命名空间冲突：沪科技粤教版（初中 physics-hkj-yj）与沪科教版（高中 physics-hkjy）
都用了 `phk_` 前缀，105 个知识点 id、780 个题号、105 条先修边完全撞车，
导致 data/questions.json 聚合按题号去重后，这 780 题被高中桶覆盖（解析与题干对不上）。

处置：把**初中桶**整体改名 `phk_` → `phkc_`（105 点 / 780 题，体量小的一侧），
文件内全量替换 + 文件名同步改名，之后聚合不再有重复 id。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-hkj-yj')
PAT = re.compile(r'\bphk_')
NEW = 'phkc_'


def count_ids():
    t = len(json.load(open(os.path.join(D, 'topics.json'), encoding='utf-8')))
    q = len(json.load(open(os.path.join(D, 'questions.json'), encoding='utf-8')))
    dep = len(json.load(open(os.path.join(D, 'dependencies.json'), encoding='utf-8')))
    return t, q, dep


def main():
    before = count_ids()
    files = []
    for pat in ('**/*.json', '**/*.md'):
        files += glob.glob(os.path.join(D, pat), recursive=True)
    files = [f for f in files if '/_text/' not in f]
    changed = 0
    for f in files:
        try:
            s = open(f, encoding='utf-8').read()
        except UnicodeDecodeError:
            continue
        if 'phk_' not in s:
            continue
        s2 = PAT.sub(NEW, s)
        open(f, 'w', encoding='utf-8').write(s2)
        changed += 1
    renamed = 0
    for f in glob.glob(os.path.join(D, '**', '*'), recursive=True):
        if not os.path.isfile(f):
            continue
        b = os.path.basename(f)
        nb = PAT.sub(NEW, b)
        if nb != b:
            os.rename(f, os.path.join(os.path.dirname(f), nb))
            renamed += 1
    after = count_ids()
    # 残留检查
    left = 0
    for f in glob.glob(os.path.join(D, '**', '*'), recursive=True):
        if os.path.isfile(f) and '/_text/' not in f and f.endswith(('.json', '.md')):
            if 'phk_' in open(f, encoding='utf-8', errors='ignore').read():
                left += 1
    print('内容替换 %d 文件 · 改名 %d 文件 · 残留 %d' % (changed, renamed, left))
    print('点/题/边：改前 %s → 改后 %s' % (before, after))
    assert before == after, '条目数不应变化'
    assert left == 0, '仍有 phk_ 残留'
    return 0


if __name__ == '__main__':
    sys.exit(main())
