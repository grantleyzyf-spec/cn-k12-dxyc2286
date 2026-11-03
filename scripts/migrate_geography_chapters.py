#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理章序迁移：2012 版 → 2026 春夏新版（只改 chapter 与卷名/scope，不动点与题）。

旧 → 新（人教 2026）：
七上  第一章 地球和地图（拆两章）→ 第一章 地球 / 第二章 地图
      第二章 陆地和海洋 → 第三章
      第三章 天气与气候 → 第四章
      第四章 居民与聚落 → 第五章 居民与文化
      第五章 发展与合作 → 第六章
七下  第六~十章 → 第七~十一章（同名）
八上  第一章 中国的疆域与人口 → 第一章 从世界看中国
      第二/三/四章 不变；新增 第五章 建设美丽中国
八下  第五章 → 第六章；六~九章 → 七~十章；第十章 中国在世界中 → 第十一章 奋进中的中国

用法：python3 scripts/migrate_geography_chapters.py --dry | --write
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography")

# (书, 旧章名) → [(新章号, 新章名)]；拆章的多于一条
MAP = {
    ("七年级上册", "第一章 地球和地图"): [("第一章", "地球"), ("第二章", "地图")],
    ("七年级上册", "第二章 陆地和海洋"): [("第三章", "陆地和海洋")],
    ("七年级上册", "第三章 天气与气候"): [("第四章", "天气与气候")],
    ("七年级上册", "第四章 居民与聚落"): [("第五章", "居民与文化")],
    ("七年级上册", "第五章 发展与合作"): [("第六章", "发展与合作")],
    ("七年级下册", "第六章 我们生活的大洲——亚洲"): [("第七章", "我们生活的大洲——亚洲")],
    ("七年级下册", "第七章 我们邻近的地区和国家"): [("第八章", "我们邻近的地区和国家")],
    ("七年级下册", "第八章 东半球其他的地区和国家"): [("第九章", "东半球其他的地区和国家")],
    ("七年级下册", "第九章 西半球的国家"): [("第十章", "西半球的国家")],
    ("七年级下册", "第十章 极地地区"): [("第十一章", "极地地区")],
    ("八年级上册", "第一章 中国的疆域与人口"): [("第一章", "从世界看中国")],
    ("八年级上册", "第二章 中国的自然环境"): [("第二章", "中国的自然环境")],
    ("八年级上册", "第三章 中国的自然资源"): [("第三章", "中国的自然资源")],
    ("八年级上册", "第四章 中国的经济发展"): [("第四章", "中国的经济发展")],
    ("八年级下册", "第五章 中国的地理差异"): [("第六章", "中国的地理差异")],
    ("八年级下册", "第六章 北方地区"): [("第七章", "北方地区")],
    ("八年级下册", "第七章 南方地区"): [("第八章", "南方地区")],
    ("八年级下册", "第八章 西北地区"): [("第九章", "西北地区")],
    ("八年级下册", "第九章 青藏地区"): [("第十章", "青藏地区")],
    ("八年级下册", "第十章 中国在世界中"): [("第十一章", "奋进中的中国")],
}

# 拆章：按知识点归入哪个新章（其余归「地球」）
SPLIT_TO_MAP = {"geo_p007", "geo_p008"}   # 地图三要素、等高线地形图 → 第二章 地图


def chap_of(chapter):
    """'七年级上册 第一章 地球和地图' → ('七年级上册', '第一章 地球和地图')"""
    m = re.match(r"^(.+?)\s+(第[一二三四五六七八九十]+章.*)$", chapter)
    return (m.group(1), m.group(2)) if m else (chapter, "")


def new_chapter(book, ch, tid=None):
    for (b, old), targets in MAP.items():
        if b == book and old == ch:
            if len(targets) == 1:
                no, name = targets[0]
            else:
                no, name = targets[0] if tid not in SPLIT_TO_MAP else targets[1]
            return f"{book} {no} {name}"
    return None


def main():
    write = "--write" in sys.argv
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    changed = 0
    for t in topics:
        book, ch = chap_of(t["chapter"])
        if book not in ("七年级上册", "七年级下册", "八年级上册", "八年级下册"):
            continue
        nc = new_chapter(book, ch, t["id"])
        if nc and nc != t["chapter"]:
            t["chapter"] = nc
            changed += 1
    print(f"知识点 chapter 改写 {changed} 条")
    if write:
        json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        open(os.path.join(D, "topics.json"), "a").write("\n")
    # 卷面
    exdir = os.path.join(D, "exams")
    renames, scope_fix = [], 0
    for book in os.listdir(exdir):
        p = os.path.join(exdir, book)
        if not os.path.isdir(p):
            continue
        for fn in sorted(os.listdir(p)):
            if not fn.endswith(".json"):
                continue
            fp = os.path.join(p, fn)
            d = json.load(open(fp, encoding="utf-8"))
            kind = d.get("kind")
            new_scope = []
            for sc in d.get("scope") or []:
                b, ch = chap_of(sc)
                targets = MAP.get((b, ch))
                if targets:
                    # 单元卷只认一个章：拆章时留在「第一章 地球」，第二章 容单独出卷
                    pick = targets[:1] if kind == "unit" else targets
                    for no, name in pick:
                        new_scope.append(f"{b} {no} {name}")
                    scope_fix += 1
                    continue
                new_scope.append(sc)
            d["scope"] = new_scope
            if kind == "unit" and len(new_scope) == 1:
                b, ch = chap_of(new_scope[0])
                m = re.match(r"(第[一二三四五六七八九十]+章)\s*(.*)$", ch)
                if m:
                    d["paper"] = f"{m.group(1)} {m.group(2)} 测试卷"
                    if d["paper"] != fn[:-5]:
                        renames.append((fp, os.path.join(p, d["paper"] + ".json")))
            if write:
                json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"卷面 scope 改写 {scope_fix} 处 · 待改名 {len(renames)} 卷")
    for old, new in renames:
        print("  ", os.path.basename(old), "→", os.path.basename(new))
        if write:
            os.replace(old, new)


MAP_BOOKS = {"七年级上册", "七年级下册", "八年级上册", "八年级下册"}

if __name__ == "__main__":
    main()
