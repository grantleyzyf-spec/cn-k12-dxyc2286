#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讲解↔现役卷「逐题对齐」核验（判据可复算、误报率经过抽样验证）。

判据：对每份讲解，逐题取该题块的原文片段，要求
  · 该题 stem 里的数字（小数点保留原样）至少命中 1 个，或
  · 该题 answer 的要素（数字/字母）全部命中；纯中文答案（无数字/字母）改比中文要素全中
一份讲解的「对齐率」= 命中题数 / 题数；< 0.6 判为「疑似错配」，需人工复核或重写。

为什么不用「答案整串出现」：讲解是转述，不是抄答案（实测该判据误报率 > 60%）。
为什么不先归一化再比数字：把 3.27 归一成 327 会与题干里的 327×45 假命中，
反之 0.35×0.4 归一后与题干脱形 → 假阴性。数字一律在原文里比。

用法：
  python3 verify_lecture_alignment.py [--bucket math-sujiao] [--json]
"""
import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.expanduser('~/Desktop/cn-k12-dxyc2286')
PREFIX = ("苏教版", "苏科版", "人教版", "北师大版", "沪教版", "湘教版",
          "青岛版", "冀教版", "北京版", "河北版", "华东师大版", "统编版")


def find_exam(bucket, book, paper):
    cands = [book] + [str(book)[len(p):] for p in PREFIX if str(book).startswith(p)]
    for c in cands:
        f = f'{REPO}/data/{bucket}/exams/{c}/{paper}.json'
        if os.path.exists(f):
            return json.load(open(f, encoding='utf-8'))
    return None


def blocks_of(md):
    """题块 → 起点。只认行首，可带 ###/加粗前缀。

    两级判据：先收「宽口径」行首 `第 N 题…`，再用「真题块头」`第 N 题（S 分）` 覆盖。
    原因：讲解体例里有「二、考点地图」，其行形如 `第 1 题｜平面图形与立体图形｜3 分`，
    同样是行首且带题号，宽口径首次命中会选中它 ⇒ 题块正文被挤到地图行之后，
    逐题比对全部假阴性（实测 math-bj 22 份、math-hukeji 5 份均由此误报）。
    """
    loose = {}
    for m in re.finditer(r'(?m)^[#\s\*]*第\s*(\d+)\s*题[^\n]*', md):
        loose.setdefault(int(m.group(1)), m.start())
    out = dict(loose)
    for m in re.finditer(r'(?m)^[#\s\*]*第\s*(\d+)\s*题\s*[（(]\s*\d+\s*分\s*[）)]', md):
        out[int(m.group(1))] = m.start()          # 真题块头优先
    return out


def align_rate(lec, exam):
    md = lec.get('markdown') or ''
    starts = blocks_of(md)
    order = sorted(starts.items(), key=lambda kv: kv[1])
    segs = {}
    for i, (no, st) in enumerate(order):
        end = order[i + 1][1] if i + 1 < len(order) else len(md)
        segs[no] = md[st:end]
    items = [it for s in exam.get('sections') or [] for it in (s.get('items') or [])]
    hit = 0
    miss = []
    for it in items:
        seg = segs.get(it['no'])
        if seg is None:
            miss.append((it['no'], '无题块'))
            continue
        toks = re.findall(r'\d+(?:\.\d+)?', it.get('stem') or '')
        ok_stem = any(t in seg for t in toks)
        ans = it.get('answer')
        ans = ans if isinstance(ans, str) else json.dumps(ans, ensure_ascii=False)
        atoks = re.findall(r'\d+(?:\.\d+)?|[A-D]', ans)
        ok_ans = bool(atoks) and all(t in seg for t in atoks)
        ok_cjk = False
        if not atoks:      # 纯中文答案（「西，北」「一样；一样」）：原判据无要素可比 → 必假阳性，改比中文要素
            ctoks = [t for t in re.findall(r'[\u4e00-\u9fff]+', ans) if t not in ('略', '答', '答案')]
            ok_cjk = bool(ctoks) and all(t in seg for t in ctoks)
        if ok_stem or ok_ans or ok_cjk:
            hit += 1
        else:
            miss.append((it['no'], f'stem {toks[:3]} / ans {atoks[:3]}'))
    rate = hit / len(items) if items else 0.0
    return rate, hit, len(items), miss


EXC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alignment_exceptions.json')


def load_exceptions():
    """人工复核例外（判据无法覆盖的合法体例）。低到 0.5 以下仍报警，防止整份被换掉却蒙混。"""
    if not os.path.exists(EXC):
        return {}
    try:
        return {k: v for k, v in json.load(open(EXC, encoding='utf-8')).items()
                if not k.startswith('_')}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', default='')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--min', type=float, default=0.6)
    a = ap.parse_args()
    buckets = [b for b in sorted(os.path.basename(os.path.dirname(p))
                                 for p in glob.glob(f'{REPO}/data/*/exam_lectures'))
               if b.startswith('math')]
    if a.bucket:
        buckets = [b for b in buckets if b == a.bucket]
    exc = load_exceptions()
    report, grand = {}, [0, 0, 0]
    for b in buckets:
        files = [f for f in glob.glob(f'{REPO}/data/{b}/exam_lectures/**/*.json', recursive=True)
                 if '/_stale/' not in f]
        bad = []
        for f in sorted(files):
            lec = json.load(open(f, encoding='utf-8'))
            exam = find_exam(b, lec.get('book'), lec.get('paper'))
            if exam is None:
                bad.append({'file': f, 'rate': 0.0, 'why': '无对应现役卷'})
                continue
            rate, hit, n, miss = align_rate(lec, exam)
            if rate < a.min:
                rel = os.path.relpath(f, f'{REPO}/data/{b}/exam_lectures')
                if f'{b}/{rel}' in exc and rate >= 0.5:
                    print(f'   ℹ 人工复核例外（判据不适用）{rel}｜{rate:.3f}')
                    continue
                bad.append({'file': rel,
                            'rate': round(rate, 3), 'hit': hit, 'items': n,
                            'sample_miss': miss[:4]})
        grand[0] += len(files)
        grand[1] += len(bad)
        report[b] = bad
        print(f'{b:16s} 讲解 {len(files):4d}｜对齐率 < {a.min:.0%} 的 {len(bad):3d}')
        for x in bad[:5]:
            print(f'   ⚠ {x["file"]}｜{x.get("rate")}｜{x.get("sample_miss", x.get("why"))}')
    print(f'合计 讲解 {grand[0]}｜疑似错配 {grand[1]}')
    if a.json:
        out = os.path.expanduser('~/.hermes/profiles/agent8/cache/scratch/lecture_alignment.json')
        json.dump(report, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('明细 →', out)


if __name__ == '__main__':
    main()
