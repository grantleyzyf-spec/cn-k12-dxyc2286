# -*- coding: utf-8 -*-
"""小学（9 册）「候选真缺」正文回查 —— SKILL §5 四步法的第 ② 步。

背景：audit_math_xiaoxue_point_keshi.py 只把图谱点与「课时字号标题」比对，未命中的
列成「候选真缺」。按铁律，候选必须再查第二次：该册**全文正文**里有没有这个知识点的内容。
只查标题会把大量「课时名不同」的点误判成旧版残留。

判定：点名的核心字（去虚词）在该册正文里以 ≥2 字连续片段命中，或 2-gram 覆盖率 ≥0.6 → 
「表述差异（非缺口）」；两者都 0 → 「真缺」。
两处都不命中的，再在**相邻册**里找一次（有些点写错册），找到则记为「错册」。

产出：/tmp/mtoc/xiaoxue_points_body.md（人读）＋ 控制台摘要。
"""
import glob
import json
import os
import re

import fitz

XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/小学/人教版"
REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = "/tmp/mtoc/xiaoxue_points_body.md"
AUDIT_MD = "/tmp/mtoc/xiaoxue_point_keshi.md"
STOP = ["的", "与", "和", "及", "其", "之", "中", "初步", "简单", "一般", "基本", "常见", "一些",
        "概念", "定义", "性质", "运算", "计算", "方法", "应用", "问题", "及其", "认识", "了解"]
NOISE = re.compile(r"仅供个人|未经授权|不得另做他用|电子课本|公众号|微信|淘宝")


def clean(s):
    return re.sub(r"\s+", "", s or "")


def core(s):
    s = re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-/]", "", s or "")
    for w in STOP:
        s = s.replace(w, "")
    return s


def bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}


def book_pdfs():
    m = {}
    # 小学教材文件名有两套：<书号>_…数学_四年级_上册_… 与 …数学 一年级 上册_…，
    # 统一按「年级 + 上/下册」两个片段拼键（旧脚本用 book[:3]+book[-2:] 也是这个道理）
    for p in glob.glob(f"{XI}/*.pdf"):
        b = os.path.basename(p)
        mg = re.search(r"([一二三四五六])年级", b)
        ms = re.search(r"([上下])册", b)
        if mg and ms:
            m[f"{mg.group(1)}年级{ms.group(1)}册"] = p
    return m


def load_text(pdf):
    d = fitz.open(pdf)
    return clean("".join(d[i].get_text() for i in range(len(d))))


def candidates():
    """从审计报告里取「候选真缺」行：- 二年级下册 · 求一个数是另一个数的几倍"""
    out = []
    if not os.path.exists(AUDIT_MD):
        return out
    started = False
    for ln in open(AUDIT_MD, encoding="utf-8"):
        s = ln.strip()
        if s.startswith("## 候选真缺"):
            started = True
            continue
        if started and s.startswith("- ") and "·" in s:
            book, name = s[2:].split("·", 1)
            out.append((book.strip(), name.strip()))
    return out


def raw_key(name):
    """只去空格与标点、**保留虚词**的原文键：先按原文找，避免「克和千克」被 core 去「和」
    后变成「克千克」而永远命不中（这是把有内容的点误判成真缺的主因之一）。"""
    return re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-/]", "", name or "")


def hit(book_text, name):
    rk = raw_key(name)
    if len(rk) >= 2 and rk in book_text:
        return True, f"原文键「{rk}」直接命中"
    c = core(name)
    if 0 < len(c) <= 2:
        # 去虚词后只剩 1–2 字（「0的认识」→「0」、「倍的认识」→「倍」）：
        # 2-gram 集合里不可能含单字，必须直接子串判定，否则会把有内容的点误判成真缺
        return (c in book_text), f"短核心字「{c}」{'命中' if c in book_text else '未命中'}"
    if len(c) >= 3 and c in book_text:
        return True, f"核心字串「{c}」直接命中"
    cb = bigrams(c)
    if not cb:
        return False, ""
    tb = bigrams(book_text)
    cover = len(cb & tb) / len(cb)
    if cover >= 0.6:
        return True, f"2-gram 覆盖 {cover:.2f}"
    # 放宽：去掉「认识/了解」类前缀后再比
    c2 = re.sub(r"^(认识|了解|初步认识|初步了解|知道)", "", c)
    if len(c2) >= 3 and c2 in book_text:
        return True, f"去前缀后「{c2}」命中"
    return False, f"2-gram 覆盖仅 {cover:.2f}"


def main():
    books = book_pdfs()
    texts = {k: load_text(v) for k, v in books.items()}
    cands = candidates()
    rows = []
    for book, name in cands:
        t = texts.get(book)
        if t is None:
            rows.append((book, name, "该册无 PDF", ""))
            continue
        ok, why = hit(t, name)
        if ok:
            rows.append((book, name, "表述差异（非缺口）", why))
            continue
        # 相邻册再找一次
        found = [k for k, v in texts.items() if k != book and core(name) and core(name) in v]
        rows.append((book, name, "真缺", f"本册 0 命中；相邻册命中：{found}" if found else "本册与相邻册均 0 命中"))
    lines = ["# 小学数学「候选真缺」正文回查（SKILL §5 第②步）", "",
             f"- 候选 {len(cands)} 条 · 可回查册 {len(texts)} 册", ""]
    from collections import Counter
    cnt = Counter(r[2] for r in rows)
    lines.append(f"- 分类：{dict(cnt)}")
    lines.append("")
    for label in ("真缺", "表述差异（非缺口）", "该册无 PDF"):
        sel = [r for r in rows if r[2] == label]
        if not sel:
            continue
        lines.append(f"## {label}：{len(sel)} 条")
        for r in sel:
            lines.append(f"- {r[0]} · {r[1]} —— {r[3]}")
        lines.append("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:40]))
    print(f"\n✅ {OUT}")


if __name__ == "__main__":
    main()
