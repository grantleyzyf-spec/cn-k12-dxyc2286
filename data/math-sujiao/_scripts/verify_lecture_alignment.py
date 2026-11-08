#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讲解↔现役卷「逐题对齐」核验（判据可复算、误报率经过抽样验证）。

判据：对每份讲解，逐题取该题块的原文片段，要求
  · 该题 stem 里的数字（小数点保留原样）至少命中 1 个，或
  · 该题 answer 的要素（数字/字母）全部命中；纯中文答案（无数字/字母）改比中文要素全中
一份讲解的「对齐率」= 命中题数 / 题数；< 0.6 判为「疑似错配」，需人工复核或重写。

第二判据（2026-11-08 加）：题干与题块的「二元字组平均重合度」< 0.15 判「疑似换卷」。
为什么需要它：「命中任一数字」太宽——同册换卷（期中 A 讲解 × 期中 B 卷）实测仍有 0.75~0.83，
旧判据整库只能抓 14.8% 的换卷。二元字组（去掉空白后相邻两字）对转述不敏感、对换题很敏感：
真件最低 0.162（1304 份中位 0.45），换卷均值 0.075 ⇒ 阈值 0.15 时真件误报 0/1304、换卷检出 90.9%
（同族期中/期末 84.4%、异单元 95.4%）。标定命令见 SKILL.md §5.4 与 references/delivery-docx-verification.md §7。

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


def find_exam(bucket, book, paper, repo=None):
    repo = repo or REPO
    cands = [book] + [str(book)[len(p):] for p in PREFIX if str(book).startswith(p)]
    for c in cands:
        f = f'{repo}/data/{bucket}/exams/{c}/{paper}.json'
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


def segs_of(md):
    """题号 → 该题块原文（到下一个题块起点为止）。"""
    starts = blocks_of(md)
    order = sorted(starts.items(), key=lambda kv: kv[1])
    return {no: md[st:(order[i + 1][1] if i + 1 < len(order) else len(md))]
            for i, (no, st) in enumerate(order)}


def _bigrams(text):
    t = re.sub(r'\s', '', str(text))
    return {t[i:i + 2] for i in range(len(t) - 1)}


def stem_cont(segs, exam):
    """题干二元字组在题块里的平均重合度；无可用题块返回 None。"""
    vals = []
    for s in exam.get('sections') or []:
        for it in s.get('items') or []:
            seg = segs.get(it.get('no'))
            if seg is None:
                continue
            g = _bigrams(it.get('stem') or '')
            if not g:
                continue
            vals.append(len(g & _bigrams(seg)) / len(g))
    return sum(vals) / len(vals) if vals else None


def align_rate(segs, exam):
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


def exc_paths():
    """例外文件位置：脚本同目录 → 仓库 data/math-sujiao/_scripts/ → $ALIGN_EXC。

    技能库里的副本与仓库副本不同目录，只查脚本同目录会在技能库跑时静默读不到例外（实测第 6 链误报 1 份）。
    """
    here = os.path.dirname(os.path.abspath(__file__))
    return [os.environ.get('ALIGN_EXC') or '',
            os.path.join(here, 'alignment_exceptions.json'),
            os.path.join(REPO, 'data/math-sujiao/_scripts/alignment_exceptions.json')]


def load_exceptions():
    """人工复核例外（判据无法覆盖的合法体例）。低到 0.5 以下仍报警，防止整份被换掉却蒙混。"""
    p = next((x for x in exc_paths() if x and os.path.exists(x)), None)
    if not p:
        return {}
    try:
        return {k: v for k, v in json.load(open(p, encoding='utf-8')).items()
                if not k.startswith('_')}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', default='')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--min', type=float, default=0.6)
    ap.add_argument('--cont-min', type=float, default=0.15,
                    help='题干二元字组平均重合度下限（低于此值判疑似换卷；0 关闭）')
    ap.add_argument('--selftest', type=int, default=0, help='每桶抽 N 份做换卷自检，报检出率')
    ap.add_argument('--repo', default='', help='仓库根（默认 ~/Desktop/cn-k12-dxyc2286），便于沙箱自测')
    a = ap.parse_args()
    repo = os.path.expanduser(a.repo) if a.repo else REPO
    buckets = [b for b in sorted(os.path.basename(os.path.dirname(p))
                                 for p in glob.glob(f'{repo}/data/*/exam_lectures'))
               if b.startswith('math')]
    if a.bucket:
        buckets = [b for b in buckets if b == a.bucket]
    exc = load_exceptions()
    report, grand = {}, [0, 0, 0]
    for b in buckets:
        files = [f for f in glob.glob(f'{repo}/data/{b}/exam_lectures/**/*.json', recursive=True)
                 if '/_stale/' not in f]
        bad = []
        for f in sorted(files):
            lec = json.load(open(f, encoding='utf-8'))
            exam = find_exam(b, lec.get('book'), lec.get('paper'), repo)
            if exam is None:
                bad.append({'file': f, 'rate': 0.0, 'why': '无对应现役卷'})
                continue
            segs = segs_of(lec.get('markdown') or '')
            rate, hit, n, miss = align_rate(segs, exam)
            cont = stem_cont(segs, exam)
            low_cont = (a.cont_min > 0 and cont is not None and cont < a.cont_min)
            if rate < a.min or low_cont:
                rel = os.path.relpath(f, f'{repo}/data/{b}/exam_lectures')
                if f'{b}/{rel}' in exc and rate >= 0.5:
                    print(f'   ℹ 人工复核例外（判据不适用）{rel}｜{rate:.3f}')
                    continue
                why = '对齐率 %.3f' % rate
                if low_cont:
                    why += '｜题干重合度 %.3f < %.2f' % (cont, a.cont_min)
                bad.append({'file': rel, 'rate': round(rate, 3), 'hit': hit,
                            'items': n, 'cont': None if cont is None else round(cont, 3),
                            'why': why, 'sample_miss': miss[:4]})
        grand[0] += len(files)
        grand[1] += len(bad)
        report[b] = bad
        n_cont = sum(1 for x in bad if '重合度' in str(x.get('why')))
        print(f'{b:16s} 讲解 {len(files):4d}｜可疑 {len(bad):3d}'
              f'（对齐率 < {a.min:.0%}：{len(bad) - n_cont}｜重合度 < {a.cont_min:.2f}：{n_cont}）')
        for x in bad[:5]:
            print(f'   ⚠ {x["file"]}｜{x.get("why", x.get("rate"))}｜{x.get("sample_miss")}')
    print(f'合计 讲解 {grand[0]}｜可疑 {grand[1]}')
    if a.selftest:
        import random
        random.seed(7)
        n_tot = n_hit = 0
        for b in buckets:
            files = [f for f in glob.glob(f'{repo}/data/{b}/exam_lectures/**/*.json', recursive=True)
                     if '/_stale/' not in f]
            for f in random.sample(files, min(a.selftest, len(files))):
                lec = json.load(open(f, encoding='utf-8'))
                ex = find_exam(b, lec.get('book'), lec.get('paper'), repo)
                if ex is None:
                    continue
                others = [g for g in glob.glob(f'{repo}/data/{b}/exams/*/*.json')
                          if '/_stale/' not in g
                          and os.path.basename(g)[:-5] != lec.get('paper')
                          and os.path.basename(os.path.dirname(g)) in
                          (lec.get('book'), str(lec.get('book')).split('版')[-1])]
                if not others:
                    continue
                wrong = json.load(open(random.choice(others), encoding='utf-8'))
                segs = segs_of(lec.get('markdown') or '')
                c = stem_cont(segs, wrong)
                n_tot += 1
                if c is not None and c < a.cont_min:
                    n_hit += 1
        print(f'自检（换卷负样本）{n_hit}/{n_tot} = {n_hit / n_tot:.1%}' if n_tot else '自检：无可用负样本')
    if a.json:
        out = os.path.expanduser('~/.hermes/profiles/agent8/cache/scratch/lecture_alignment.json')
        json.dump(report, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('明细 →', out)
    return 1 if grand[1] else 0


if __name__ == '__main__':
    sys.exit(main())
