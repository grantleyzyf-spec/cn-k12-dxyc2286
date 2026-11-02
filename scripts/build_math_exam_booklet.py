# -*- coding: utf-8 -*-
"""把一册的试卷（及参考答案）合成两本「合订本」docx：封面 + 目录 + 逐卷并入。

做法：用 scripts/build_math_exam_docx.py 的 new_doc()/head() 造母本，再把已渲染好的
单卷 docx 的 body 元素逐个深拷贝进来（版式是逐段内联设置的，拷贝后保持一致）。

用法：
    MATH_BUCKET=math-bj MATH_EDITION=北京版 python3 scripts/build_math_exam_booklet.py
    MATH_BUCKET=math-bj MATH_EDITION=北京版 python3 scripts/build_math_exam_booklet.py 一年级上册
"""
import copy
import glob
import importlib.util
import json
import os
import re
import sys

from docx import Document

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("exam_docx", os.path.join(HERE, "build_math_exam_docx.py"))
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

KIND_RANK = {"unit": 0, "mid": 1, "fin": 2}
CN = "一二三四五六七八九十"


def cn_number(text):
    m = re.search(r"第([一二三四五六七八九十百零〇\d]+)", text or "")
    if not m:
        return 999
    s = m.group(1)
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch == "十":
            total += (cur or 1) * 10
            cur = 0
        elif ch in CN:
            cur = CN.index(ch) + 1
    return total + cur


def merge_body(master, src_path):
    """把 src_path 的正文元素深拷贝进 master（丢弃源 sectPr）"""
    src = Document(src_path)
    body = master.element.body
    for child in src.element.body:
        if child.tag.endswith("}sectPr"):
            continue
        body.append(copy.deepcopy(child))


def build(master, papers, title, subtitle, out_path):
    E.para(master, title, size=18, bold=True, align="center", cn="黑体", space_after=6)
    E.para(master, subtitle, size=10, align="center", space_after=14)
    E.para(master, "目　录", size=13, bold=True, align="center", cn="黑体", space_after=6)
    for i, (ex, _) in enumerate(papers, 1):
        E.para(master, f"{i}. {ex['book']}　{ex['paper']}", size=10.5, space_after=2)
    master.add_page_break()
    for idx, (ex, src) in enumerate(papers):
        if idx:
            master.add_page_break()
        merge_body(master, src)
    E.add_page_number_footer(master)
    master.save(out_path)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    books = sorted({os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(E.EXAM, "*", "*.json"))})
    if only:
        books = [b for b in books if b == only]
    n_paper = n_ans = 0
    for book in books:
        files = sorted(glob.glob(os.path.join(E.EXAM, book, "*.json")))
        exs = [json.load(open(f, encoding="utf-8")) for f in files]
        exs.sort(key=lambda d: (KIND_RANK.get(d.get("kind"), 9), cn_number(d.get("paper"))))
        out_dir = os.path.join(E.OUT_ROOT, book, "_合订本")
        os.makedirs(out_dir, exist_ok=True)
        for kind_cn, suffix, tag in (("试卷", "_试卷.docx", "试卷合订本"), ("参考答案与评分标准", "_参考答案与评分标准.docx", "参考答案合订本")):
            pairs, miss = [], []
            for ex in exs:
                src = os.path.join(E.OUT_ROOT, book, f"{ex['paper']}{suffix}")
                (pairs if os.path.exists(src) else miss).append((ex, src) if os.path.exists(src) else ex["paper"])
            if miss:
                print(f"⚠️ {book} {kind_cn}：{len(miss)} 卷缺单份 docx（{miss[:3]}），跳过这些卷")
            if not pairs:
                continue
            master = E.new_doc()
            out = os.path.join(out_dir, f"{book}_{tag}.docx")
            build(master, pairs, f"数学（{E.EDITION}）{book}", f"{kind_cn}合订本 · 共 {len(pairs)} 卷 · 学生打印版", out)
            if suffix.startswith("_试卷"):
                n_paper += len(pairs)
            else:
                n_ans += len(pairs)
            print(f"✅ {book}：{kind_cn}合订本 {len(pairs)} 卷 → {out}")
    print(f"合计 试卷 {n_paper} 卷 · 参考答案 {n_ans} 卷")


if __name__ == "__main__":
    main()
