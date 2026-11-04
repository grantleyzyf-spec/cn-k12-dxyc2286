#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""湘教版地理 9 册 → 章/节骨架（_skeleton.json）。

教材文字层里「目录」区是逐行铺开的（`第X章` 一行、标题一行、页码一行），
所以按「目录区行序」解析：章行 → 节行 ＋ 紧随的标题行。
探究与实践 / 后记 不入骨架（按仓库口径：实践类不建点）。
"""
import json
import os
import re
import sys

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "data", "geography-xiangjiao")
TEXT = os.path.join(D, "_text")
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册",
         "必修第一册", "必修第二册", "选择性必修1", "选择性必修2", "选择性必修3"]
CN = "一二三四五六七八九十"
CH_RE = re.compile(rf"^第([{CN}]+)章(.*)$")
SEC_RE = re.compile(rf"^第([{CN}]+)节(.*)$")


def toc_lines(book):
    raw = open(os.path.join(TEXT, f"{book}.txt"), encoding="utf-8").read()
    lines = []
    for l in raw.split("\n"):
        l = re.sub(r"@@PAGE \d+@@", "", l).strip()
        if l:
            lines.append(l)
    # 目录区 = 第一次出现「第X章」到「第一章」正文页之前的连续块
    start = next(i for i, l in enumerate(lines) if CH_RE.match(l))
    block = []
    chapter_seen = 0
    for l in lines[start:start + 400]:
        if CH_RE.match(l):
            chapter_seen += 1
            if chapter_seen > 60:
                break
        block.append(l)
        if len(block) > 360:
            break
    return block


def parse(book):
    block = toc_lines(book)
    chapters = []
    seen_no = set()
    i = 0
    while i < len(block):
        m = CH_RE.match(block[i])
        if not m:
            i += 1
            continue
        if m.group(1) in seen_no:      # 目录已结束，后面是正文/页眉
            break
        seen_no.add(m.group(1))
        no, tail = m.group(1), m.group(2).strip()
        title = tail
        j = i + 1
        if not title:
            # 标题在下一行（跳过页码/空行）
            while j < len(block) and (re.fullmatch(r"\d+", block[j]) or not block[j]):
                j += 1
            if j < len(block) and not SEC_RE.match(block[j]) and not CH_RE.match(block[j]):
                title = block[j]
                j += 1
        ch = {"no": no, "title": title.replace("\b", "").strip(), "sections": []}
        # 收集本节下的节
        while j < len(block):
            if CH_RE.match(block[j]):
                break
            sm = SEC_RE.match(block[j])
            if sm:
                sno, stail = sm.group(1), sm.group(2).strip()
                # 目录是分栏排的，节号可能乱序（第三节排在第四节之后）⇒ 只按「章内已出现」去重
                if any(x["no"] == sno for x in ch["sections"]):
                    j += 1
                    continue
                k = j + 1
                if not stail:
                    while k < len(block) and (re.fullmatch(r"\d+", block[k]) or not block[k]):
                        k += 1
                    if k < len(block) and not SEC_RE.match(block[k]) and not CH_RE.match(block[k]):
                        stail = block[k]
                        j = k
                ch["sections"].append({"no": sno, "title": stail.replace("\b", "").strip()})
            j += 1
        chapters.append(ch)
        i = j
    return chapters


def main():
    out = {}
    for b in BOOKS:
        chs = parse(b)
        out[b] = chs
        nsec = sum(len(c["sections"]) for c in chs)
        print(f"{b}: {len(chs)} 章 / {nsec} 节")
        for c in chs:
            print(f"   第{c['no']}章 {c['title']}  ({len(c['sections'])} 节)")
            for s in c["sections"]:
                print(f"      第{s['no']}节 {s['title']}")
    json.dump(out, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("→", os.path.join(D, "_skeleton.json"))


if __name__ == "__main__":
    main()
