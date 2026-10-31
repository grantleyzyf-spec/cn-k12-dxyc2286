# -*- coding: utf-8 -*-
"""回填课标引用的 sourceLine，并把被「去标点」污染的引文还原为课标原文。

两个真坑（都在实测里踩到）：
1. `docs/math-std-quotes.md` 从单元级点导出，图形/分类类条目 sourceLine 为 None，
   自检器正则是 `sourceLine (\\d+)` ⇒ 这些条目在工位侧无法引用，写手被迫改引语义较弱的条目。
2. 更要命的是：那批老 quote 在建点时被**去掉了标点**（「会对物体图形或数据…」），
   而 `test_math.py` 的「quote 逐字回表」只去空白、留标点 ⇒ 去标点的引文永远回表失败。
   所以不能只补行号，必须把引文还原为课标原文（带标点、逐字）。

做法：把课标 TXT 拼成 raw 全文，建「去标点字符 → raw 下标 / 行号」双映射；
用去标点的 quote 在归一化全文里定位，取命中区间对应的 **raw 切片** 作为权威 quote。

产出 docs/math-std-lines.json：`{ "id||老quote": {"line": N, "quote": 原文} }`。

用法：python3 scripts/backfill_math_std_lines.py [--write]
"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
DOC = f"{REPO}/docs/math-std-quotes.md"
OUT = f"{REPO}/docs/math-std-lines.json"
TXTS = {
 "mat-2022": "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
             "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt",
 "mat-2017": "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
             "（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt",
}
KEEP = re.compile(r"[\u4e00-\u9fa5A-Za-z0-9]")


def qnorm(s):
    return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")


def parse_doc():
    rows, cur = {}, None
    for ln in open(DOC, encoding="utf-8"):
        s = ln.rstrip("\n")
        m = re.match(r"- `([^`]+)` · sourceLine (\S+)", s)
        if m:
            cur = {"id": m.group(1), "line": None if m.group(2) == "None" else int(m.group(2)),
                   "quote": None}
            continue
        if s.strip().startswith("> ") and cur is not None and cur["quote"] is None:
            cur["quote"] = s.strip()[2:].strip()
            rows[(cur["id"], cur["quote"])] = cur["line"]
            cur = None
    return rows


def load_source(path):
    """→ (归一化全文, 归一化位 → raw 位, 归一化位 → 行号, raw 全文)"""
    raw_lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    norm_chars, raw_pos, line_of = [], [], []
    pos = 0
    for n, ln in enumerate(raw_lines, 1):
        for ch in ln:
            if KEEP.match(ch):
                norm_chars.append(ch)
                raw_pos.append(pos)
                line_of.append(n)
            pos += 1
        pos += 1  # 行尾换行符占一位
    return "".join(norm_chars), raw_pos, line_of, "\n".join(raw_lines)


def main():
    write = "--write" in sys.argv
    srcs = {k: load_source(p) for k, p in TXTS.items() if os.path.exists(p)}
    rows = parse_doc()
    todo = [(i, q) for (i, q), ln in rows.items() if ln is None]
    got, miss = {}, []
    for sid, quote in todo:
        key = sid.split(":")[0]
        if key not in srcs:
            miss.append((sid, quote, "无对应课标 TXT"))
            continue
        norm_full, raw_pos, line_of, raw_full = srcs[key]
        target = qnorm(quote)
        pos = norm_full.find(target) if target else -1
        if pos < 0:
            miss.append((sid, quote, "课标全文未逐字命中（引文被改写）"))
            continue
        a, b = raw_pos[pos], raw_pos[pos + len(target) - 1]
        verbatim = raw_full[a:b + 1].replace("\n", "")
        got[f"{sid}||{quote}"] = {"line": line_of[pos], "quote": verbatim}
    print(f"待回填 {len(todo)} 条 → 成功 {len(got)} / 未命中 {len(miss)}")
    for m in miss:
        print("  ✗", m[0], m[2], "|", m[1][:34])
    if write:
        old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
        old.update(got)
        json.dump(old, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"✅ 写 {OUT}（累计 {len(old)} 条）")


if __name__ == "__main__":
    main()
