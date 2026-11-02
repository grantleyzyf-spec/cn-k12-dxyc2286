#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版 · 学层精讲单篇/整册自检器

用法：
  python3 check_learn_ej.py --shard <topicId>        # 子代自查单篇（读 _learn_out/<id>.json）
  python3 check_learn_ej.py <册名>                    # 父代整册（读 learn/<册>.json）

检查项（照 check_math_learn_md.py 口径，引文源改为本批 OCR 全文 _src/h*_full.txt）：
 1 结构齐全：topicId/title/markdown/words
 2 汉字数 1000–2000（words 字段须等于实测）
 3 七个小标题：开场 / 课本原文 / 费曼翻译 / 例题 / 易错 / 五步学习法 / 自查
 4 引文：`> ` 块 ≥2 处、每处 ≥8 汉字，去标点后须在本册 OCR 全文里逐字命中
 5 例题 ≥2（**例1 / **例2）
 6 易错 ≥2；自查 `- [ ]` ≥3
 7 禁 LaTeX（$…$）、HTML 标签、Markdown 表格（| 开头行）
"""
import json, os, re, sys

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
D = os.path.join(REPO, "data/math-ejiao")
SRC = os.path.join(D, "_src")
SEC = ["开场", "课本原文", "费曼翻译", "例题", "易错", "五步学习法", "自查"]
STEPS = ["锻炼", "第一个知识点", "积微", "对标", "杠铃"]
BOOK2TAG = {"鄂教版必修第一册": "h1", "鄂教版必修第二册": "h2", "鄂教版必修第三册": "h3",
            "鄂教版必修第四册": "h4", "鄂教版选择性必修第一册": "h5",
            "鄂教版选择性必修第二册": "h6", "鄂教版选择性必修第三册": "h7"}


def norm(s):
    return re.sub(r"[^\u4e00-\u9fa50-9A-Za-z²³√π]", "", s or "")


def hanzi(s):
    return re.findall(r"[\u4e00-\u9fa5]", s or "")


def check_lesson(md, book, title=""):
    errs = []
    hz = len(hanzi(md))
    if not (1000 <= hz <= 2000):
        errs.append(f"汉字数 {hz} 不在 1000–2000")
    for s in SEC:
        if s not in md:
            errs.append(f"缺小节「{s}」")
    for k in STEPS:
        if k not in md:
            errs.append(f"五步学习法缺「{k}」")
    quotes = [m.strip() for m in re.findall(r"^>\s*(.+)$", md, re.M)]
    quotes = [q for q in quotes if len(hanzi(q)) >= 8]
    if len(quotes) < 2:
        errs.append(f"课本原文块引用 {len(quotes)} 处 < 2")
    tag = BOOK2TAG.get(book)
    src = open(os.path.join(SRC, f"{tag}_full.txt"), encoding="utf-8",
               errors="ignore").read() if tag else ""
    flat = norm(src)
    for q in quotes:
        if norm(q) and norm(q)[:24] not in flat:
            errs.append(f"引文未在教材 OCR 命中：{q[:24]}")
    if len(re.findall(r"\*\*例\s*\d", md)) < 2:
        errs.append("例题 < 2（需 **例1 / **例2）")
    err_sec = md.split("易错", 1)[-1][:600] if "易错" in md else ""
    if len(re.findall(r"^\s*[-*]\s+", err_sec, re.M)) < 2:
        errs.append("易错点拨 < 2 条")
    if len(re.findall(r"-\s*\[\s*\]", md)) < 3:
        errs.append("自查清单 < 3 条")
    if re.search(r"\$[^$]+\$|\\\(|\\\)", md):
        errs.append("含 LaTeX")
    if re.search(r"</?[a-zA-Z][^>]*>", md):
        errs.append("含 HTML 标签")
    if re.search(r"^\s*\|.*\|\s*$", md, re.M):
        errs.append("含 Markdown 表格")
    return errs, hz


def main():
    if len(sys.argv) < 2:
        print("usage: check_learn_ej.py --shard <topicId> | <册名>"); return 2
    if sys.argv[1] == "--shard":
        tid = sys.argv[2]
        sh = json.load(open(os.path.join(D, "_learn_shards", f"{tid}.json"), encoding="utf-8"))
        p = sh["outPath"]
        if not os.path.isfile(p):
            print(f"FAIL 缺产物 {p}"); return 1
        d = json.load(open(p, encoding="utf-8"))
        errs, hz = check_lesson(d.get("markdown", ""), sh["book"], sh.get("title", ""))
        if d.get("topicId") != tid:
            errs.append(f"topicId 应为 {tid}")
        if not d.get("title"):
            errs.append("缺 title")
        if d.get("words") != hz:
            errs.append(f"words 字段 {d.get('words')} ≠ 实测 {hz}")
        print(f"{tid}｜{sh['title']}｜汉字 {hz}")
        if errs:
            print("FAIL:")
            for e in errs:
                print("  -", e)
            return 1
        print("PASS")
        return 0

    book = sys.argv[1]
    p = os.path.join(D, "learn", f"{book}.json")
    if not os.path.isfile(p):
        print(f"FAIL 缺 {p}"); return 1
    d = json.load(open(p, encoding="utf-8"))
    bad = 0
    for L in d.get("lessons", []):
        errs, hz = check_lesson(L.get("markdown", ""), book, L.get("title", ""))
        if errs:
            bad += 1
            print(f"✗ {L['topicId']} {L.get('title','')[:16]}：{errs[:3]}")
    print(f"== {book}：{len(d.get('lessons', []))} 篇，失败 {bad} ==")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
