#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教材原文检索器：帮学层写手找「逐字可回表」的课本句子。

用法：
  python3 scripts/find_geo_quote.py 七年级上册 地球的形状
  python3 scripts/find_geo_quote.py 必修第一册 热力环流 --n 6

输出：每条命中给「印刷页（PDF 页）＋ 上下文窗口」，窗口内的文字就是可引用的原文
（数据层写引文时去掉换行、保留原字，check_geo_learn.py 用去空白子串回表）。
"""
import os, re, sys

D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data/geography/_text")
if "--root" in sys.argv:
    D = sys.argv[sys.argv.index("--root") + 1]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    book, kw = sys.argv[1], sys.argv[2]
    n = 5
    if "--n" in sys.argv:
        n = int(sys.argv[sys.argv.index("--n") + 1])
    path = os.path.join(D, f"{book}.txt")
    if not os.path.exists(path):
        print(f"没有 {path}")
        return 1
    raw = open(path, encoding="utf-8").read()
    # 逐页索引（兼容两种落盘：标记单独一行 / 标记紧跟正文）
    pieces = re.split(r"@@PAGE (\d+)@@\s*", raw)
    pages = []
    for i in range(1, len(pieces) - 1, 2):
        pages.append((pieces[i], pieces[i + 1]))
    hits = 0
    for pno, body in pages:
        flat = re.sub(r"\s+", "", body)
        start = 0
        while True:
            i = flat.find(kw, start)
            if i < 0:
                break
            lo, hi = max(0, i - 60), min(len(flat), i + len(kw) + 80)
            print(f"[PDF p.{pno}] …{flat[lo:hi]}…")
            hits += 1
            start = i + len(kw)
            if hits >= n:
                return 0
    if not hits:
        print("未命中，换关键词（二字词更好命中）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
