#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从「大单元整体教学设计」docx 抽课时表（小学苏教版/苏科版目录未列小节的册用这个补课时层）

输出：/tmp/msj/keshi.json
  { "<册名>": { "<单元名或单元号>": {"unit_name":…, "lessons":[{"no":1,"title":"9加几"}, …]} } }

解析路径：定位段落「十五、“教-学-评”一致性课时设计」，其后形如「（一）第1课时 9加几」的条目即一课时。
"""
import glob
import json
import os
import re
from collections import defaultdict

from docx import Document

ROOTS = [
    os.path.expanduser('~/Desktop/中小学教材/中小学教材/数学/小学/苏教版/大单元整体教学设计'),
    os.path.expanduser('~/Desktop/中小学教材/中小学教材/数学/初中/苏科版/大单元整体教学设计'),
    os.path.expanduser('~/Desktop/中小学教材/中小学教材/数学/高中/苏教版'),
]
OUT = '/tmp/msj/keshi.json'

BOOK_PAT = re.compile(r'(?P<book>[一二三四五六七八九]年级[上下]册|必修第[一二三]册|选择性必修第[一二三]册)')
UNIT_PAT = re.compile(r'(?P<unit>第[一二三四五六七八九十]+(?:单元|章)\s*[^第]*?)\s*大单元整体教学设计')
KESHI_PAT = re.compile(r'（[一二三四五六七八九十]+）第\s*(\d+)\s*课时\s*(.+)$')
# 兜底：正文叙述式「第一课时学习因数和倍数的意义；第二课时找一个数的因数…」
PROSE_PAT = re.compile(r'第([一二三四五六七八九十]+)课时([^。；；，、]{2,22})')


CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


def cn2int(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN.get(s[1], 0)
    if '十' in s:
        a, _, b = s.partition('十')
        return CN.get(a, 0) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s, 0)


def parse(path):
    d = Document(path)
    ps = [p.text.strip() for p in d.paragraphs if p.text.strip()]
    # 目录页也有「十五、」条目，务必取**最后一次**出现（正文中的那一处）
    starts = [i for i, t in enumerate(ps) if t.startswith('十五、')]
    if not starts:
        return []
    body = []
    for t in ps[starts[-1] + 1:]:
        if t.startswith('十六、'):
            break
        body.append(t)

    lessons = []
    for t in body:
        m = KESHI_PAT.search(t)
        if m:
            lessons.append({'no': int(m.group(1)), 'title': m.group(2).strip(' 。：:')})
    if lessons:
        return lessons, 'structured'

    # 兜底：从叙述里抽「第N课时 + 短语」，去重保序
    seen, out = set(), []
    for t in body:
        for m in PROSE_PAT.finditer(t):
            no = cn2int(m.group(1))
            title = m.group(2).strip(' 学习理解认识掌握运用的了是在把将会')
            if no in seen or not title:
                continue
            seen.add(no)
            out.append({'no': no, 'title': title})
    out.sort(key=lambda x: x['no'])
    return out, 'prose'


def main():
    res = defaultdict(dict)
    miss = []
    for root in ROOTS:
        for f in sorted(glob.glob(os.path.join(root, '*.docx'))):
            base = os.path.basename(f)
            mb, mu = BOOK_PAT.search(base), UNIT_PAT.search(base)
            if not mb:
                miss.append(base)
                continue
            book = mb.group('book')
            unit = mu.group('unit').strip() if mu else re.sub(
                r'^.*?' + re.escape(book), '', base).split('大单元')[0].strip()
            lessons, how = parse(f)
            if not lessons:
                miss.append(base + '（无课时段）')
                continue
            res[book][unit] = {'unit_name': unit, 'lessons': lessons,
                               'how': how, 'src': os.path.basename(f)}
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    how = {}
    for b, us in res.items():
        for u, d in us.items():
            how[d.get('how')] = how.get(d.get('how'), 0) + 1
    print('解析方式分布:', how)
    tot = sum(len(v) for v in res.values())
    nl = sum(len(u['lessons']) for v in res.values() for u in v.values())
    print(f'册 {len(res)} | 单元 {tot} | 课时 {nl}')
    for b in sorted(res):
        n = sum(len(u['lessons']) for u in res[b].values())
        print(f'  {b}: {len(res[b])} 单元 / {n} 课时')
    if miss:
        print(f'未解析 {len(miss)} 份：')
        for x in miss[:8]:
            print('  -', x[:70])


if __name__ == '__main__':
    main()
