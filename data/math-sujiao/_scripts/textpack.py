#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一册的逐页 OCR 拼成一个带页码标记的文本包，供写手定位题材。

用法：python3 textpack.py <tag> [--offset N]
  <tag>    如 s1a / h1 / k7a
  --offset 印刷页 = PDF 页 − offset（默认取目录 JSON 里的 page_offset，缺省 7/8）

输出：/tmp/msj/<tag>/textpack.txt
  <<<PDF 12 / 印5>>>  …正文…
若该册 OCR 为空（如 s3a 字体损坏），自动改拼 full.txt（PDF 文字层）。
"""
import glob
import json
import os
import re
import sys

SRC = '/tmp/msj'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    tag = sys.argv[1]
    off = None
    if '--offset' in sys.argv:
        off = int(sys.argv[sys.argv.index('--offset') + 1])
    pj = os.path.join(SRC, f'{tag}.json')
    meta = json.load(open(pj, encoding='utf-8')) if os.path.isfile(pj) else {}
    if off is None:
        off = meta.get('page_offset') or meta.get('page_offset_pdf_minus_printed') or 7

    ocr = sorted(glob.glob(os.path.join(SRC, tag, 'ocr', '*.txt')))
    ocr2 = sorted(glob.glob(os.path.join(SRC, tag, 'ocr2', '*.txt')))
    if ocr2 and sum(os.path.getsize(f) for f in ocr2) > sum(os.path.getsize(f) for f in ocr):
        ocr = ocr2          # 有二次 OCR（放大重跑）且更完整时优先
    chunks, total = [], 0
    for f in ocr:
        m = re.search(r'(\d+)', os.path.basename(f))
        if not m:
            continue
        pdf = int(m.group(1))
        t = open(f, encoding='utf-8', errors='ignore').read().strip()
        total += len(t)
        if t:
            chunks.append(f'<<<PDF {pdf} / 印{pdf - off}>>>\n{t}')

    mode = 'ocr'
    body_all = '\n'.join(chunks)
    cjk = len(re.findall(r'[\u4e00-\u9fa5]', body_all))
    cjk_ratio = cjk / max(1, len(body_all))
    need_tl = total < 2000 or cjk_ratio < 0.25   # 空 或 汉字占比过低（字体损坏）
    if need_tl:
        full = os.path.join(SRC, tag, 'full.txt')
        if os.path.isfile(full):
            body = open(full, encoding='utf-8', errors='ignore').read()
            # 文字层常以分页符 \f 分段
            pages = body.split('\f')
            chunks = [f'<<<文字层 第{i+1}段>>>\n{p.strip()}' for i, p in enumerate(pages) if p.strip()]
            mode = 'textlayer'

    out = os.path.join(SRC, tag, 'textpack.txt')
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(f'# {tag} {meta.get("book","")} 题材包（{mode}）\n'
                 f'# 印刷页 = PDF 页 − {off}\n\n')
        fh.write('\n\n'.join(chunks))
    print(f'{out}  {os.path.getsize(out)} 字节  模式={mode}  段数={len(chunks)}  汉字占比={cjk_ratio:.2f}')


if __name__ == '__main__':
    sys.exit(main())
