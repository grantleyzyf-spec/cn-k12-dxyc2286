#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量试卷体检：逐卷跑门禁 + 按 (book, paper) 查重 + 按册统计缺口。

用法：python3 audit_exams.py [--json out.json]
输出：每册一行（卷数 / 通过 / 未过 / 重复），未过卷附首条错误摘要。
"""
import concurrent.futures as cf
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

REPO = os.path.expanduser('~/Desktop/cn-k12-dxyc2286')
JOBS = 8  # 并发子进程数（--jobs N 可改）
SUBJ = {'math-sujiao': 'scripts/check_math_sujiao_exam.py',
        'math-suke': 'scripts/check_math_suke_exam.py'}


def run(ck, path):
    r = subprocess.run(['/usr/bin/python3', ck, path], capture_output=True, text=True,
                       env={**os.environ, 'PYTHONPATH': ''}, cwd=REPO)
    out = [x for x in (r.stdout or '').splitlines() if x.strip()]
    # checker 侧输出口径已改为 `RESULT: PASS errors=N`（旧版是「自检通过」），两种都认；
    # 否则脚本会把全部卷判成「未过」——实测 168 卷全绿却报 0/168。
    tail = out[-1] if out else ''
    passed = bool(out) and ('自检通过' in tail or 'RESULT: PASS' in tail)
    first_err = ''
    for line in out:
        if line.strip().startswith('✗') or '不在' in line or ('第' in line and '题' in line):
            first_err = line.strip()[:90]
            break
    if not passed and not first_err:
        first_err = (out[-1][:90] if out else (r.stderr or '')[-90:]).strip()
    return passed, first_err, len(out)


def main():
    global JOBS
    if '--jobs' in sys.argv:
        JOBS = int(sys.argv[sys.argv.index('--jobs') + 1])
    report = {}
    for sub, ck in SUBJ.items():
        base = os.path.join(REPO, 'data', sub, 'exams')
        ckpath = os.path.join(REPO, ck)
        if not os.path.isdir(base):
            continue
        rows = []
        dup = defaultdict(list)
        # 并发跑 checker：每个卷都是一个 /usr/bin/python3 子进程，串行跑 216 卷实测 >12 分钟
        # （2026-11-10 收口时超时），8 线程后一分钟级。判据不变，只改驱动方式。
        files, meta = [], {}
        for f in sorted(glob.glob(os.path.join(base, '*', '*.json'))):
            try:
                meta[f] = json.load(open(f, encoding='utf-8'))
            except Exception as e:
                rows.append({'path': os.path.relpath(f, base), 'book': '?', 'paper': '?',
                             'pass': False, 'err': f'JSON 不可读: {e}'})
                continue
            files.append(f)

        def _one(f):
            ok, err, _n = run(ckpath, f)
            return f, ok, err

        results = {}
        with cf.ThreadPoolExecutor(max_workers=JOBS) as ex:
            for f, ok, err in ex.map(_one, files):
                results[f] = (ok, err)

        for f in files:
            d = meta[f]
            ok, err = results.get(f, (False, 'checker 未返回'))
            rec = {'path': os.path.relpath(f, base), 'book': d.get('book', '?'),
                   'paper': d.get('paper', '?'), 'examId': d.get('examId', ''),
                   'kind': d.get('kind', ''), 'pass': ok, 'err': err,
                   'items': sum(len(s.get('items', [])) for s in d.get('sections', []))}
            rows.append(rec)
            dup[(rec['book'], rec['paper'])].append(rec['path'])
        report[sub] = {'rows': rows,
                       'dup': {f'{k[0]} || {k[1]}': v for k, v in dup.items() if len(v) > 1}}

        by_book = defaultdict(lambda: [0, 0, 0])
        for r in rows:
            by_book[r['book']][0] += 1
            by_book[r['book']][1 if r['pass'] else 2] += 1
        print(f'\n=== {sub} ===')
        for book in sorted(by_book):
            n, ok, bad = by_book[book]
            print(f'{book or "?":24s} 卷 {n:3d} 通过 {ok:3d} 未过 {bad:3d}')
        print(f'合计 {len(rows)} 卷｜通过 {sum(r["pass"] for r in rows)}｜未过 {sum(not r["pass"] for r in rows)}'
              f'｜重复键 {len(report[sub]["dup"])}')
        for k, v in report[sub]['dup'].items():
            print(f'  ⚠ 重复 {k}: {len(v)} 份')
        for r in rows:
            if not r['pass']:
                print(f'  ✗ {r["path"]} :: {r["err"]}')

    out = os.path.join(os.path.expanduser('~/.hermes/profiles/agent8/cache/scratch'),
                       'exam_audit.json')
    if '--json' in sys.argv:
        json.dump(report, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'\n明细写入 {out}')


if __name__ == '__main__':
    main()
