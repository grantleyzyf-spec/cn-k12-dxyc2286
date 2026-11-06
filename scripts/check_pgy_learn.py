#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学层精讲检查器（逐片 / 全量）。

用法：
  python3 scripts/check_pgy_learn.py --shard data/physics-bsd-gyy/_learn_parts/L001_out.json
  python3 scripts/check_pgy_learn.py --all

判据：
  七段标题逐字且顺序正确；1200–2600 汉字且与 words 一致；
  「课本原文」≥2 处 `> ` 引文且逐字回表本册 OCR 全文（normalize 后子串）；
  例题 2 道且 ❌/✅ 各 ≥2；五步节 350–700 且五条齐全；自查 `- [ ]` ≥3；禁 Markdown 表格/LaTeX/HTML。
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
PARTS = os.path.join(D, '_learn_parts')
SEC = ['一、开场', '二、课本原文', '三、费曼翻译', '四、例题精讲', '五、易错点拨', '六、五步学习法', '七、方法锚与自查']
HAN = re.compile(r'[\u4e00-\u9fa5]')


def han(s):
    return len(HAN.findall(s or ''))


def qn(s):
    return re.sub(r'[\s，。、；：！？“”"\'’‘（）()《》·—…\-]+', '', s or '')


def check(path):
    errs = []
    sid = os.path.basename(path).replace('_out.json', '')
    shard_p = os.path.join(PARTS, sid + '.json')
    if not os.path.exists(shard_p):
        return ['缺作业单 %s' % shard_p]
    shard = json.load(open(shard_p, encoding='utf-8'))
    try:
        out = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        return ['无法解析：%s' % e]
    md = out.get('markdown') or ''
    if not md:
        return ['markdown 为空']
    n = han(md)
    if not 1200 <= n <= 2600:
        errs.append('汉字 %d ∉[1200,2600]' % n)
    if out.get('words') != n:
        errs.append('words %s ≠ 实测 %d' % (out.get('words'), n))

    pos = [md.find('## ' + s) for s in SEC]
    if any(p < 0 for p in pos):
        errs.append('缺段：%s' % [s for s, p in zip(SEC, pos) if p < 0])
    elif pos != sorted(pos):
        errs.append('七段顺序错乱')

    # 课本原文：引文逐字回表
    txt_p = shard.get('txt')
    src = qn(open(txt_p, encoding='utf-8').read()) if txt_p and os.path.exists(txt_p) else ''
    quotes = [q.strip(' >') for q in re.findall(r'^>\s*(.+)$', md, re.M)]
    quotes = [q for q in quotes if han(q) >= 8]
    if len(quotes) < 2:
        errs.append('课本原文引文 %d 处 <2' % len(quotes))
    if src:
        miss = [q[:18] for q in quotes if qn(q) not in src]
        if miss:
            errs.append('引文未在教材逐字命中 %d 处：%s' % (len(miss), miss[:3]))
    if md.count('这句话的意思是') < 2:
        errs.append('「这句话的意思是」少于 2 处')

    # 例题
    if len(re.findall(r'例题\s*[12一二]', md)) < 2:
        errs.append('例题不足 2 道')
    if md.count('❌') < 2 or md.count('✅') < 2:
        errs.append('❌/✅ 各需 ≥2（现 %d/%d）' % (md.count('❌'), md.count('✅')))

    # 五步节
    if '六、五步学习法' in md:
        seg = md.split('六、五步学习法', 1)[1].split('七、', 1)[0]
        if not 350 <= han(seg) <= 700:
            errs.append('五步节汉字 %d ∉[350,700]' % han(seg))
        if len(re.findall(r'[①②③④⑤]', seg)) < 5:
            errs.append('五步条目不齐')

    # 自查
    if len(re.findall(r'^- \[ \]', md, re.M)) < 3:
        errs.append('自查清单 <3 条')

    if re.search(r'^\|.*\|$', md, re.M):
        errs.append('含 Markdown 表格')
    if re.search(r'\$|\\frac|\\times|<[a-z]+>', md):
        errs.append('含 LaTeX/HTML')
    if re.search(r'扫描件|OCR|抽取|残片|文字层', md):
        errs.append('含元话语（扫描件/OCR 等）')
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    files = ([a.shard] if a.shard else
             sorted(glob.glob(os.path.join(PARTS, '*_out.json'))) if a.all else [])
    if not files:
        print('用法：--shard <文件> 或 --all')
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
    print('\n共 %d 篇 · 不合格 %d · %s' % (len(files), bad, 'RESULT: PASS' if not bad else 'RESULT: FAIL'))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
