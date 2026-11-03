#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理章序迁移（讲解层）：卷名/文件名/scope 跟随，正文里的章号按「章名锚定」替换。

只动初中四册（七上/七下/八上/八下）；高中五册的「第一章…」不受影响。
拆章（旧「第一章 地球和地图」）的讲解由新写手重写，本脚本跳过。

用法：python3 scripts/migrate_geo_lectures.py --dry | --write
"""
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography")
CN = "一二三四五六七八九十"

# (册, 旧章全名) -> (新章全名)
MAP = [
    ("七年级上册", "第二章 陆地和海洋", "第三章 陆地和海洋"),
    ("七年级上册", "第三章 天气与气候", "第四章 天气与气候"),
    ("七年级上册", "第四章 居民与聚落", "第五章 居民与文化"),
    ("七年级上册", "第五章 发展与合作", "第六章 发展与合作"),
    ("七年级下册", "第六章 我们生活的大洲——亚洲", "第七章 我们生活的大洲——亚洲"),
    ("七年级下册", "第七章 我们邻近的地区和国家", "第八章 我们邻近的地区和国家"),
    ("七年级下册", "第八章 东半球其他的地区和国家", "第九章 东半球其他的地区和国家"),
    ("七年级下册", "第九章 西半球的国家", "第十章 西半球的国家"),
    ("七年级下册", "第十章 极地地区", "第十一章 极地地区"),
    ("八年级上册", "第一章 中国的疆域与人口", "第一章 从世界看中国"),
    ("八年级下册", "第五章 中国的地理差异", "第六章 中国的地理差异"),
    ("八年级下册", "第六章 北方地区", "第七章 北方地区"),
    ("八年级下册", "第七章 南方地区", "第八章 南方地区"),
    ("八年级下册", "第八章 西北地区", "第九章 西北地区"),
    ("八年级下册", "第九章 青藏地区", "第十章 青藏地区"),
    ("八年级下册", "第十章 中国在世界中", "第十一章 奋进中的中国"),
]

# 单元卷旧卷名（含拆章那一卷，先只改名，不替换正文）
UNIT_RENAME = {}
for book, old, new in MAP:
    UNIT_RENAME[(book, old + " 测试卷")] = new + " 测试卷"


def rewrite_text(md, pairs):
    """按章名锚定替换：第X章<名> / 第X章 <名> / 第X章「名」 三种写法"""
    for book, old, new in pairs:
        old_no, old_name = old.split(" ", 1)
        new_no, new_name = new.split(" ", 1)
        for sep in ("", " ", "　"):
            md = md.replace(old_no + sep + old_name, new_no + sep + new_name)
        md = md.replace(f"{old_no}「{old_name}」", f"{new_no}「{new_name}」")
        md = md.replace(f"{old_no}《{old_name}》", f"{new_no}《{new_name}》")
    return md


def main():
    write = "--write" in sys.argv
    done = []
    for f in sorted(glob.glob(os.path.join(D, "exam_lectures", "*", "*.json"))):
        book = os.path.basename(os.path.dirname(f))
        if book not in ("七年级上册", "七年级下册", "八年级上册", "八年级下册"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        old_paper = d["paper"]
        new_paper = UNIT_RENAME.get((book, old_paper), old_paper)
        pairs = [(b, o, n) for (b, o, n) in MAP if b == book]
        # 拆章：旧「第一章 地球和地图」的讲解跳过（等重写）
        if old_paper.startswith("第一章 地球和地图"):
            continue
        d["paper"] = new_paper
        d["markdown"] = rewrite_text(d["markdown"], pairs)
        new_path = os.path.join(os.path.dirname(f), new_paper + ".json")
        done.append((f, new_path))
        if write:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            if new_path != f:
                os.replace(f, new_path)
    print(f"处理 {len(done)} 份讲解")
    for a, b in done:
        if a != b:
            print("  ", os.path.basename(a), "→", os.path.basename(b))


if __name__ == "__main__":
    main()
