#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版物理 学层分片 excerpt 修复：把「目录行」换成「正文段落」。

原分片里的 excerpt 全部取自目录页（形如「长度和时间的测量…………11第2节」），
拿它做「课本原文」逐字引用等于引目录，必然被 checker 的正文回表打回。

判定规则：
  目录行 → 同一行里含 3 个以上「…」或「.」的连缀；
  正文标题 → 标题出现处前后 120 字内不含这种连缀，且长度 ≥ 400 汉字。
"""
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH = os.path.join(REPO, 'data', 'physics', '_learn_shards')
DOTS = re.compile(r'[….·]{3,}')


def toc_score(seg):
    """目录页特征分：短行多、纯数字页码行多、几乎没有句读。"""
    lines = [l.strip() for l in seg.split('\n') if l.strip()]
    if not lines:
        return 1.0
    bad = 0
    for l in lines:
        if re.fullmatch(r'[0-9]+', l):
            bad += 1
        elif len(l) <= 26 and not re.search(r'[。，？！；：]', l):
            bad += 1
    return bad / len(lines)


def is_toc(text, pos, span=400):
    seg = text[max(0, pos - span): pos + span]
    if len(DOTS.findall(seg)) >= 2:
        return True
    return toc_score(seg) > 0.45


def _positions(text, title):
    """标题在原文里的所有位置：精确匹配 + 去空白匹配（OCR 常把标题拆行）。"""
    pos = [m.start() for m in re.finditer(re.escape(title), text)]
    compact_idx = {}
    buf = []
    for j, ch in enumerate(text):
        if not ch.isspace():
            compact_idx[len(buf)] = j
            buf.append(ch)
    flat = ''.join(buf)
    key = re.sub(r'\s+', '', title)
    i = flat.find(key)
    while i >= 0:
        pos.append(compact_idx[i])
        i = flat.find(key, i + 1)
    return sorted({p for p in pos if p > 200})


def prose(p, text):
    """正文度：700 字里的句末标点个数。目录页几乎为 0，正文通常 5 个以上。"""
    seg = text[p:p + 700]
    return len(re.findall(r'[。！？]', seg))


def find_body(text, title):
    """全标题 + 分词候选一起打分，取正文度最高的那一处。"""
    cands = list(_positions(text, title))
    for tok in [t for t in re.split(r'[\s　]+', title) if len(t) >= 2]:
        cands += _positions(text, tok)
    cands = sorted(set(cands))
    if not cands:
        return None
    # 取正文度最高的一处（目录页约 0～3 个句末标点，正文 5 个以上）
    return max(cands, key=lambda p: (prose(p, text), -p))


def trim_leading_toc(seg):
    """题干命中处可能还压在目录尾巴上：逐行丢掉「无句读的短行 + 纯数字行」。"""
    lines = seg.split('\n')
    i = 0
    while i < len(lines) and i < 40:
        l = lines[i].strip()
        if not l:
            i += 1
            continue
        if re.fullmatch(r'[0-9]+', l) or (len(l) <= 30 and not re.search(r'[。，？！；：]', l)):
            i += 1
            continue
        break
    return '\n'.join(lines[i:])


def take_excerpt(text, start, want=1200):
    seg = text[start:start + want * 2]
    # 在段末收口
    cut = seg.find('\n\n', want)
    if cut > 0:
        seg = seg[:cut]
    else:
        seg = seg[:want]
    seg = trim_leading_toc(seg.strip())
    seg = seg.strip()
    if len(seg) > want:
        seg = seg[:want].rsplit('\n', 1)[0]
    return seg


def main():
    fixed = bad = 0
    report = []
    for f in sorted(glob.glob(os.path.join(SH, '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        if not isinstance(d, dict):
            continue
        text = open(os.path.join(REPO, d['text_file']), encoding='utf-8').read()
        for les in d['lessons']:
            pos = find_body(text, les['title'])
            if pos is None:
                bad += 1
                report.append(('MISS', les['topicId'], les['title']))
                continue
            old = les.get('excerpt') or ''
            new = take_excerpt(text, pos)
            if DOTS.search(new[:200]) or len(new) < 400:
                bad += 1
                report.append(('WEAK', les['topicId'], les['title'], len(new)))
                continue
            if new != old:
                les['excerpt'] = new
                fixed += 1
        json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('重取 excerpt：改写 %d 篇 · 失败 %d 篇' % (fixed, bad))
    for r in report[:15]:
        print('  ', r)
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())