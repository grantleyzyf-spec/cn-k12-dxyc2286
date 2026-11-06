#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版（郭玉英）初中物理 题库分片检查器。

用法：
  python3 scripts/check_pgy_bank.py --shard data/physics-bsd-gyy/_bank/S001_out.json
  python3 scripts/check_pgy_bank.py --all       # 全部分片
判定（与 gen_pgy_bank_shards.py 的合同一致）：
  题量恰好 8/5；类型配额；难度三档齐；选项/答案；解析 ≥25 汉字；题干 ≥12 字；禁 Markdown；片内题干不重复；id 落在作业单区间内。
退出码：0 = PASS，1 = FAIL
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'physics-bsd-gyy')
SPEC = os.path.join(D, '_bank_spec')
TYPES = {'choice', 'fill', 'short-answer', 'numeric'}
DIFFS = {'basic', 'standard', 'hard'}
BAD_STEMS = ('以上都不对', '以上都正确', '无法确定', '仅在大学学习')
HAN = re.compile(r'[\u4e00-\u9fa5]')


def han(s):
    return len(HAN.findall(s or ''))


def check_shard(path):
    errs = []
    try:
        out = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        return ['无法解析 JSON：%s' % e]
    if isinstance(out, list):
        return ['输出必须是对象 {"shard","topics","questions"}，不能是裸数组']

    sid = os.path.basename(path).replace('_out.json', '')
    spec_path = os.path.join(SPEC, sid + '.json')
    if not os.path.exists(spec_path):
        return ['找不到作业单 %s' % spec_path]
    spec = json.load(open(spec_path, encoding='utf-8'))
    items = {it['topicId']: it for it in spec['items']}
    id_range = set(spec['id_range'])
    qs = out.get('questions') or []

    # topics 内容必须齐（新点内容不能丢）
    tps = {t.get('topicId'): t for t in (out.get('topics') or [])}
    for tid, it in items.items():
        tp = tps.get(tid)
        if not tp:
            errs.append('%s 缺 topics 条目（新点内容丢失）' % tid)
            continue
        if not (40 <= han(tp.get('description')) <= 120):
            errs.append('%s description 汉字 %d ∉[40,120]' % (tid, han(tp.get('description'))))
        if len(tp.get('mastery_criteria') or []) < 2:
            errs.append('%s mastery_criteria 少于 2 条' % tid)

    # 逐点题量/配额/难度
    by = {}
    for q in qs:
        by.setdefault(q.get('topicId'), []).append(q)
    for tid, it in items.items():
        lst = by.get(tid, [])
        need = it['need']
        if len(lst) != need:
            errs.append('%s 题量 %d ≠ %d' % (tid, len(lst), need))
        cnt = {t: sum(1 for q in lst if q.get('type') == t) for t in TYPES}
        if need == 8:
            if cnt['choice'] < 3: errs.append('%s choice %d <3' % (tid, cnt['choice']))
            if cnt['fill'] < 2: errs.append('%s fill %d <2' % (tid, cnt['fill']))
            if cnt['short-answer'] < 1: errs.append('%s short-answer %d <1' % (tid, cnt['short-answer']))
        else:
            if cnt['choice'] < 2: errs.append('%s choice %d <2' % (tid, cnt['choice']))
            if cnt['fill'] < 1: errs.append('%s fill %d <1' % (tid, cnt['fill']))
            if cnt['short-answer'] < 1: errs.append('%s short-answer %d <1' % (tid, cnt['short-answer']))
        if cnt['numeric'] > 1: errs.append('%s numeric %d >1' % (tid, cnt['numeric']))
        if set(q.get('difficulty') for q in lst) - DIFFS:
            errs.append('%s difficulty 非法值 %s' % (tid, set(q.get('difficulty') for q in lst) - DIFFS))
        missing = DIFFS - set(q.get('difficulty') for q in lst)
        if missing:
            errs.append('%s 缺难度档 %s' % (tid, '/'.join(sorted(missing))))

    # 逐题
    seen = {}
    for q in qs:
        qid = q.get('id') or ''
        if qid not in id_range:
            errs.append('题号 %s 不在作业单 id_range' % qid)
        stem = (q.get('prompt') or '').strip()
        if han(stem) < 12:
            errs.append('%s 题干太短（%d 汉字）' % (qid, han(stem)))
        if any(b in stem for b in BAD_STEMS):
            errs.append('%s 含凑数干扰项' % qid)
        key = re.sub(r'\s+', '', stem)
        if key in seen:
            errs.append('%s 与 %s 题干重复' % (qid, seen[key]))
        seen[key] = qid
        if han(q.get('explanation')) < 25:
            errs.append('%s 解析 %d 汉字 <25' % (qid, han(q.get('explanation'))))
        if re.search(r'\*\*|##|\$|\\frac|<[a-z]+>', stem + (q.get('explanation') or '')):
            errs.append('%s 含 Markdown/LaTeX/HTML' % qid)
        if q.get('type') == 'choice':
            opts = q.get('options') or []
            if len(opts) != 4:
                errs.append('%s 选项 %d ≠4' % (qid, len(opts)))
            txts = [re.sub(r'\s+', '', o.get('text') or '') for o in opts]
            if len(set(txts)) != len(txts):
                errs.append('%s 选项重复' % qid)
            if q.get('answer') not in {o.get('label') for o in opts}:
                errs.append('%s answer %s 不在选项内' % (qid, q.get('answer')))
        else:
            if q.get('options'):
                errs.append('%s 非选择题不该带 options' % qid)
            if q.get('type') == 'fill' and '____' not in stem:
                errs.append('%s 填空题干缺 ____' % qid)
            if q.get('type') == 'numeric':
                try:
                    val = eval(str(q.get('verify')), {'__builtins__': {}}, {})
                    if abs(float(val) - float(q.get('answer'))) > 1e-6:
                        errs.append('%s verify %s ≠ answer %s' % (qid, val, q.get('answer')))
                except Exception as e:
                    errs.append('%s verify 无法复算（%s）' % (qid, e))
            if q.get('type') == 'short-answer' and '；' not in (q.get('answer') or ''):
                errs.append('%s 简答答案未用「；」分条' % qid)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shard')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    files = ([a.shard] if a.shard else
             sorted(glob.glob(os.path.join(D, '_bank', '*_out.json'))) if a.all else [])
    if not files:
        print('用法：--shard <文件> 或 --all')
        return 1
    bad = 0
    for f in files:
        errs = check_shard(f)
        name = os.path.basename(f)
        if errs:
            bad += 1
            print('✗ %s' % name)
            for e in errs[:12]:
                print('   -', e)
            if len(errs) > 12:
                print('   - …另有 %d 项' % (len(errs) - 12))
        else:
            print('✓ %s' % name)
    print('\n共 %d 片 · 不合格 %d · %s' % (len(files), bad, 'RESULT: PASS' if not bad else 'RESULT: FAIL'))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
