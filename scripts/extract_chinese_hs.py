# -*- coding: utf-8 -*-
"""语文 19 册目录抽取 v3：输出「单元 → 板块 → 篇目（篇名/作者/页码/自读）」清单。

与 v2 的差别：
  1. 加入高中 5 册（必修上/下、选必上/中/下），目录是单栏「课号 篇名/作者 页码」格式；
  2. 高中一课多篇（如「2 立在地球边上放号/郭沫若 4 红烛/闻一多 4」）按篇拆开 —— 这正是
     「古诗按首」粒度所需的原始数据；
  3. 小学/初中保留「单元·板块」分段；高中保留「单元名 + 学习任务/整本书阅读/古诗词诵读」板块。

产出：/tmp/cn/units_v3.json
"""
import glob
import json
import os
import re

import fitz

ROOT = "/Users/a627692/Desktop/中小学教材/中小学教材/语文"
OUT = "/tmp/cn"
NOISE = re.compile(r"仅供个人学习使用|未经授权|不得另做他用|^\s*目\s*录\s*$|^注：")
UNIT = re.compile(r"第([一二三四五六七八九十]+)单元")
BOARD = re.compile(r"(古诗词诵读|整本书阅读|单元学习任务|单元研习任务|学习活动|词语积累与词语解释|逻辑的力量|家乡文化生活)")
PAGE_NO = re.compile(r"^\d{1,3}$")

HS = [
    (10, "上", "必修上册", f"{ROOT}/高中/*必修上册*.pdf"),
    (10, "下", "必修下册", f"{ROOT}/高中/*必修下册*.pdf"),
    (11, "上", "选择性必修上册", f"{ROOT}/高中/*选择性必修上册*.pdf"),
    (11, "中", "选择性必修中册", f"{ROOT}/高中/*选择性必修中册*.pdf"),
    (11, "下", "选择性必修下册", f"{ROOT}/高中/*选择性必修下册*.pdf"),
]
YJ = [
    (1, "上", "一年级上册", f"{ROOT}/小学/*一年级_上册*.pdf"),
    (1, "下", "一年级下册", f"{ROOT}/小学/*一年级_下册*.pdf"),
    (2, "上", "二年级上册", f"{ROOT}/小学/*二年级_上册*.pdf"),
    (2, "下", "二年级下册", f"{ROOT}/小学/*二年级_下册*.pdf"),
    (3, "上", "三年级上册", f"{ROOT}/小学/*三年级_上册*.pdf"),
    (3, "下", "三年级下册", f"{ROOT}/小学/*三年级_下册*.pdf"),
    (4, "上", "四年级上册", f"{ROOT}/小学/*四年级_上册*.pdf"),
    (5, "上", "五年级上册", f"{ROOT}/小学/*五年级_上册*.pdf"),
    (6, "上", "六年级上册", f"{ROOT}/小学/*六年级_上册*.pdf"),
    (7, "上", "七年级上册", f"{ROOT}/初中/*七年级_上册*.pdf"),
    (7, "下", "七年级下册", f"{ROOT}/初中/*七年级_下册*.pdf"),
    (8, "上", "八年级上册", f"{ROOT}/初中/*八年级_上册*.pdf"),
    (8, "下", "八年级下册", f"{ROOT}/初中/*八年级_下册*.pdf"),
    (9, "上", "九年级上册", f"{ROOT}/初中/*九年级_上册*.pdf"),
]


def columns(page, ratio=0.5):
    """单栏页直接返回原文顺序；只有「没有一行跨过中线」时才按左右两栏拼。"""
    w = page.rect.width
    mid = w * ratio
    lines = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            x0, _, x1, _ = ln["bbox"]
            txt = "".join(sp["text"] for sp in ln["spans"]).strip()
            if txt:
                lines.append((x0, x1, txt))
    if not lines:
        return []
    if any(x0 < mid < x1 for x0, x1, _ in lines):
        return [" ".join(t for _, _, t in lines)]          # 单栏
    l = sorted([(x0, t) for x0, x1, t in lines if (x0 + x1) / 2 < mid])
    r = sorted([(x0, t) for x0, x1, t in lines if (x0 + x1) / 2 >= mid])
    return [" ".join(t for _, t in c) for c in (l, r) if c]


def toc_pages(pdf, maxpage=12):
    d = fitz.open(pdf)
    out = []
    for i in range(min(maxpage, d.page_count)):
        p = d[i]
        raw = p.get_text()
        if "目录" in raw or UNIT.search(raw):
            for col in (columns(p) or [raw]):
                if UNIT.search(col) or "我上学了" in col or "古诗词诵读" in col:
                    out.append(col)
    d.close()
    return out


def parse_hs(cols):
    """高中：位置法——先定「第X单元」「板块」标记位置，再把「篇名/作者 页码」按位置归入前面的标记。"""
    flat = re.sub(r"\s+", " ", " ".join(cols))
    flat = re.sub(r"目\s*录|注：篇名前标有\*的.*?课文。", " ", flat)
    flat = re.sub(r"\s*([—－·])\s*", r"\1", flat)      # 「A ——记…」拼回一个篇名
    flat = re.sub(r"\s*([《》])\s*", r"\1", flat)
    marks = [(m.start(), "单元", f"第{m.group(1)}单元") for m in UNIT.finditer(flat)]
    for m in BOARD.finditer(flat):
        marks.append((m.start(), "板块", m.group(1)))
    marks.sort()
    ITEM = re.compile(r"(?:\d{1,2}\s+)?([\u4e00-\u9fa5“”《》·A-Za-z（）()—－：:、\.]{2,28}?)/([\u4e00-\u9fa5《》·A-Za-z（）()—、\.]{1,16}?)\s*(\d{1,3})(?=\s|$)")
    BLOCK_WORDS = ("单元学习任务", "单元研习任务", "学习活动", "整本书阅读", "古诗词诵读",
                   "词语积累与词语解释", "家乡文化生活", "逻辑的力量", "注：篇名前标有")
    units = []
    for k, (pos, kind, name) in enumerate(marks):
        if kind != "单元":
            continue
        nxt = next((p for p, k2, _ in marks[k + 1:] if k2 == "单元"), len(flat))
        seg, base = flat[pos:nxt], pos
        items = []
        for m in ITEM.finditer(seg):
            title = m.group(1).strip(" ＊*·")
            if len(title) < 2 or re.fullmatch(r"[\d\s]+", title):
                continue
            if any(w in title for w in BLOCK_WORDS):
                items.append({"kind": "板块", "name": title, "author": "", "page": int(m.group(3)), "self": False})
                continue
            items.append({"kind": "篇", "name": title, "author": m.group(2).strip(),
                          "page": int(m.group(3)), "self": False})
        # 板块条目（整本书阅读《乡土中国》80 / 古诗词诵读 140）用「名称 页码」补
        for bm in BOARD.finditer(seg):
            tail = seg[bm.end():bm.end() + 24]
            pm = re.match(r"\s*([\u4e00-\u9fa5《》·]{2,16})?\s*(\d{1,3})", tail)
            if pm and pm.group(2):
                items.append({"kind": "板块", "name": (pm.group(1) or bm.group(1)).strip(),
                              "author": "", "page": int(pm.group(2)), "self": False})
        seen, keep = set(), []
        for it in items:
            if (it["name"], it["page"]) in seen:
                continue
            seen.add((it["name"], it["page"]))
            keep.append(it)
        units.append({"unit": name, "items": sorted(keep, key=lambda x: x["page"])})
    # 古诗词诵读（在最后单元之后）单独成块
    tailpos = flat.rfind("古诗词诵读")
    if tailpos > 0:
        seg = flat[tailpos:]
        ITEM2 = re.compile(r"([\u4e00-\u9fa5“”《》·（）()—：:、\.]{2,28}?)/([\u4e00-\u9fa5《》·A-Za-z]{1,16}?)\s*(\d{1,3})(?=\s|$)")
        items = [{"kind": "篇", "name": m.group(1).strip(), "author": m.group(2).strip(),
                  "page": int(m.group(3)), "self": False} for m in ITEM2.finditer(seg)]
        if items:
            gsc = {(i["name"], i["page"]) for i in items}
            for u in units:
                u["items"] = [i for i in u["items"] if (i["name"], i["page"]) not in gsc]
            units.append({"unit": "古诗词诵读", "items": sorted(items, key=lambda x: x["page"])})
    return [u for u in units if u["items"]]


def main():
    os.makedirs(OUT, exist_ok=True)
    data, rows = {}, []
    for g, sem, book, pat in HS + YJ:
        pdfs = glob.glob(pat)
        if not pdfs:
            rows.append((book, "缺PDF", 0, 0))
            continue
        cols = toc_pages(pdfs[0])
        if (g, sem) in [(x[0], x[1]) for x in HS]:
            units = parse_hs(cols)
        else:
            units = []          # 小学/初中走 v2 解析（本脚本只管高中）
        n_items = sum(len(u["items"]) for u in units)
        n_units = len(units)
        data[book] = units
        rows.append((book, f"{n_units}单元/{n_items}篇", n_units, n_items))
        print(f"{book}: {n_units} 单元 · {n_items} 条（含板块）")
    json.dump(data, open(f"{OUT}/units_v3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n| 册 | 解析结果 |\n| --- | --- |")
    for b, info, _, _ in rows:
        print(f"| {b} | {info} |")


if __name__ == "__main__":
    main()
