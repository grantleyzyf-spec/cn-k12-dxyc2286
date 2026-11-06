#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""试卷讲解检查器（physics-bsd-gyy 专用，卷面 items 在顶层）。

用法：python3 scripts/check_pgy_lecture.py --file <讲解json> | --all
判据（与合同一致）：
  六段齐全顺序正确；4000–7800 汉字且 words 相符；
  24 个题号全部出现；「思路」≥0.9×题数、「关键一步」≥0.6×题数、「易错」≥0.9×题数；
  「第 N 题（X 分）」的分值与卷面一致；五步学习法五条逐字齐全、该节 250–750 汉字；
  自查清单 ≥6 条；禁 Markdown 表格 / LaTeX / HTML。
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
SECS = ['这份卷在考什么', '考点地图', '逐题精讲', '整卷复盘', '五步学习法', '自查清单']
STEPS = ['每天锻炼一个小时', '扎实掌握第一个知识点', '能积微者速成',
         '运用对标思维突破学习困境', '运用杠铃法则缓解学习疲劳']
HAN = re.compile(r'[\u4e00-\u9fa5]')


def han(s):
    return len(HAN.findall(s or ''))


def check(path):
    errs = []
    lec = json.load(open(path, encoding='utf-8'))
    md = lec.get('markdown') or ''
    book, paper = lec.get('book'), lec.get('paper')
    ep = os.path.join(D, 'exams', book, paper + '.json')
    if not os.path.exists(ep):
        return ['找不到卷面 %s' % ep]
    exam = json.load(open(ep, encoding='utf-8'))
    items = exam['items']
    n = han(md)
    if not 4000 <= n <= 7800:
        errs.append('汉字 %d ∉[4000,7800]' % n)
    if lec.get('words') and abs(int(lec['words']) - n) > 6:
        errs.append('words %s ≠ 实测 %d' % (lec['words'], n))
    pos = [md.find(s) for s in SECS]
    if any(p < 0 for p in pos):
        errs.append('缺段：%s' % [s for s, p in zip(SECS, pos) if p < 0])
    elif pos != sorted(pos):
        errs.append('六段顺序错乱')
    missing = [it['no'] for it in items if not re.search(r'第\s*%d\s*题' % it['no'], md)]
    if missing:
        errs.append('未讲到第 %s 题（缺 %d）' % (missing[:8], len(missing)))
    for key, need in (('思路', 0.9), ('关键一步', 0.6), ('易错', 0.9)):
        c = md.count(key)
        if c < len(items) * need:
            errs.append('「%s」%d 次 < %d' % (key, c, int(len(items) * need)))
    for m in re.finditer(r'第\s*(\d+)\s*题[（(]\s*(\d+)\s*分', md):
        no, sc = int(m.group(1)), int(m.group(2))
        real = next((it['score'] for it in items if it['no'] == no), None)
        if real is not None and real != sc:
            errs.append('第 %d 题标注 %d 分，卷面 %d 分' % (no, sc, real))
    for st in STEPS:
        if st not in md:
            errs.append('五步缺「%s」' % st)
    seg = md.split('五步学习法', 1)[1].split('自查清单', 1)[0] if '五步学习法' in md else ''
    if seg and not 250 <= han(seg) <= 750:
        errs.append('五步节 %d 汉字 ∉[250,750]' % han(seg))
    if len(re.findall(r'^- \[ \]', md, re.M)) < 6:
        errs.append('自查清单 <6 条')
    if re.search(r'^\|.*\|$', md, re.M):
        errs.append('含 Markdown 表格')
    if re.search(r'\$|\\frac|\\sqrt|<[a-z]+>', md):
        errs.append('含 LaTeX/HTML')
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    files = ([a.file] if a.file else
             sorted(glob.glob(os.path.join(D, 'exam_lectures', '**', '*.json'), recursive=True))
             if a.all else [])
    if not files:
        print('用法：--file <json> 或 --all')
        return 1
    bad = 0
    for f in files:
        errs = check(f)
        if errs:
            bad += 1
            print('✗ %s' % os.path.basename(f))
            for e in errs[:6]:
                print('   -', e)
        else:
            print('✓ %s' % os.path.basename(f))
    print('\n共 %d 份 · 不合格 %d · %s' % (len(files), bad, 'RESULT: PASS' if not bad else 'RESULT: FAIL'))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
