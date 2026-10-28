# -*- coding: utf-8 -*-
"""小学 9 册：每个图谱点能否在教材正文里找到「课时标题」出处（点 → 课时 方向）。

为什么用这个方向：小学新版教材目录只到单元，课时标题在正文；而「先把课时清单抽干净」很难
（五上人工基准 23 条，自动抽取名字级只对上 61%）。但判断「某知识点教材里有没有对应课时」
只需要把该点名字与全册所有「课时字号」短标题做匹配——不依赖单元归属，也不怕多抽几条。

判定：去虚词 + 2-gram 覆盖率 ≥0.6 视为「有出处」；否则列为**候选真缺**。

产出：/tmp/mtoc/xiaoxue_point_keshi.md
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

import fitz

XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/小学/人教版"
REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = "/tmp/mtoc/xiaoxue_point_keshi.md"
BOOKS = [("一年级上册", 1, "上"), ("一年级下册", 1, "下"), ("二年级上册", 2, "上"), ("二年级下册", 2, "下"),
         ("三年级上册", 3, "上"), ("三年级下册", 3, "下"), ("四年级上册", 4, "上"),
         ("五年级上册", 5, "上"), ("六年级上册", 6, "上")]
STOP = ["的", "与", "和", "及", "其", "之", "中", "初步", "简单", "一般", "基本", "常见", "一些",
        "概念", "定义", "性质", "运算", "计算", "方法", "应用", "问题", "及其"]
NOISE = re.compile(r"仅供个人|未经授权|不得另做他用|电子课本|公众号|微信|淘宝|义\s*务\s*教\s*育")
TITLE_SKIP = re.compile(r"^(练习[一二三四五六七八九十\d]*|做一做|试一试|想一想|整理和复习|复习与关联|"
                        r"数学游戏|数学活动|阅读与思考|成长小档案|自我评价|总复习|活动[一二三四五]|"
                        r"目录|致同学|小讲堂|数学连环画)$")


def core(s):
    s = re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-]", "", s or "")
    for w in STOP:
        s = s.replace(w, "")
    return s


def bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}


def score(a, b):
    ca, cb = core(a), core(b)
    if not ca or not cb:
        return 0.0
    if ca in cb or cb in ca:
        return 1.0
    ba, bb = bigrams(ca), bigrams(cb)
    return max(len(ba & bb) / max(1, len(ba)), len(ba & bb) / max(1, len(bb)))


def keshi_titles(book):
    c = [p for p in glob.glob(f"{XI}/*.pdf") if book[:3] in p and book[-2:] in p]
    if not c:
        return []
    d = fitz.open(c[0])
    hist, shortc = Counter(), Counter()
    page_lines = []
    for i in range(d.page_count):
        ls = []
        for b in d[i].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                if t and not NOISE.search(t):
                    sz = round(max(s["size"] for s in l["spans"]), 1)
                    ls.append((sz, t))
                    hist[sz] += 1
                    cc = core(t)
                    if 2 <= len(cc) <= 16 and re.search(r"[\u4e00-\u9fa5]", t) and not re.search(r"[0-9０-９=＝+＋]", t):
                        shortc[sz] += 1
        page_lines.append(ls)
    d.close()
    body = hist.most_common(1)[0][0]
    unit_c = [(shortc.get(sz, 0), sz) for sz in hist if 21 <= sz <= 30 and hist[sz] >= 3]
    unit_sz = sorted(unit_c, reverse=True)[0][1] if unit_c else 24.0
    # 课时字号可能不止一档（正文 12 的册课时 16，但同册 18pt 也可能是课时/单元下的小标题）
    # ⇒ 取「短中文行占比 ≥0.30 且出现 ≥8 次」的所有字号，取并集，避免单档选错整册丢标题
    ke_sizes = sorted({sz for sz in hist
                       if body < sz < unit_sz - 1 and hist[sz] >= 8
                       and shortc.get(sz, 0) / max(1, hist[sz]) >= 0.30})
    if not ke_sizes:
        ke_sizes = [16.0]
    titles, seen = [], set()
    for ls in page_lines:
        for sz, t in ls:
            if not (any(abs(sz - k) <= 0.6 for k in ke_sizes) or (ke_sizes and (min(ke_sizes) - 1.6) <= sz <= (unit_sz - 2.1))):
                continue
            nm = re.sub(r"^\d{1,2}\s*[.．、]\s*", "", re.sub(r"\s+", "", t))
            c2 = core(nm)
            if not (2 <= len(c2) <= 16) or TITLE_SKIP.match(nm) or re.search(r"[0-9０-９=＝+＋%％]", nm):
                continue
            if c2 in seen:
                continue
            seen.add(c2)
            titles.append(nm)
    return titles


def main():
    topics = json.load(open(f"{REPO}/data/math/topics.json", encoding="utf-8"))
    L = ["# 小学 9 册 · 图谱点 ↔ 教材课时标题（点 → 课时 方向）", "",
         "- 判定：把图谱点名与该册所有「课时字号」短标题做「去虚词 + 2-gram 覆盖率」匹配，≥0.6 记为有出处",
         "- 阈值不足 0.6 的列为**候选真缺**（教材可能有但名字差异大，需人工核）", ""]
    rows, todo = [], []
    for book, g, sem in BOOKS:
        ts = [t for t in topics if (t["grade"], t["semester"]) == (g, sem)]
        titles = keshi_titles(book)
        ok, miss, covered = 0, [], []
        for t in ts:
            scored = sorted(((score(t["name"], x), x) for x in titles), reverse=True)
            best = scored[0] if scored else (0, "")
            if best[0] >= 0.6:
                ok += 1
                covered.append((t["name"], best[1]))
            else:
                miss.append((t["name"], best[1], best[0]))
        L.append(f"## {book}（图谱 {len(ts)} 点 · 抓到课时标题 {len(titles)} 条）")
        L.append("")
        L.append(f"- 有出处 **{ok}** · 候选真缺 **{len(miss)}**")
        if miss:
            L.append("- 候选真缺：" + "；".join(f"{n}（最近「{x}」{s:.2f}）" for n, x, s in miss))
        L.append("")
        rows.append((book, len(ts), len(titles), ok, len(miss)))
        for m in miss:
            todo.append((book, m[0]))
    L += ["## 汇总", "", "| 册 | 图谱点 | 课时标题 | 有出处 | 候选真缺 |", "| --- | ---: | ---: | ---: | ---: |"]
    for r in rows:
        L.append("| {} | {} | {} | {} | {} |".format(*r))
    a, b = sum(r[1] for r in rows), sum(r[3] for r in rows)
    L.append(f"| **合计** | {a} | {sum(r[2] for r in rows)} | {b} | {a - b} |")
    L += ["", "## 候选真缺清单", ""]
    for book, n in todo:
        L.append(f"- {book} · {n}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[L.index("## 汇总"):]))


if __name__ == "__main__":
    main()
