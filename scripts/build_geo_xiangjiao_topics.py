#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""湘教版地理：由 _skeleton.json 生成 topics 骨架（单元点 1/章 ＋ 课时点 1/节）。

- id 段：`gxj_p001` 起顺序编（单元点在前、其后紧跟本单元课时点）
- chapter：`<册> 第X章 <章名>`（单元点）／`<册> 第X章 <章名> · 第Y节 <节名>`（课时点）
- domain：按学段课标四领域（初中：地球与地图/世界地理/中国地理/乡土地理；
  高中：自然地理/人文地理/区域发展/资源环境与国家安全），先给初判，writer 复核
- description / mastery_criteria / standards 由 writer 批次回填（本脚本写空占位）
"""
import json
import os
import re

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "data", "geography-xiangjiao")
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

GRADE = {
    "七年级上册": (7, "上"), "七年级下册": (7, "下"),
    "八年级上册": (8, "上"), "八年级下册": (8, "下"),
    "必修第一册": (10, "上"), "必修第二册": (10, "下"),
    "选择性必修1": (11, "上"), "选择性必修2": (11, "下"), "选择性必修3": (12, "上"),
}

# 初判领域（writer 可复核修正）：按章名关键词
DOMAIN_RULES = [
    ("地球与地图", ["地球", "地图", "走进地理", "面貌"]),
    ("中国地理", ["中国"]),
    ("世界地理", ["世界", "大洲", "地区", "国家", "居民"]),
]
HS_RULES = [
    ("自然地理", ["宇宙", "地表形态", "大气", "水", "植被", "土壤", "地球的运动", "岩石圈", "整体性与差异性"]),
    ("区域发展", ["区域", "人口", "城镇", "乡村", "产业", "发展"]),
    ("资源环境与国家安全", ["资源", "环境", "国家安全", "可持续"]),
]


def domain_of(book, chapter_title):
    rules = DOMAIN_RULES if book.startswith(("七", "八")) else HS_RULES
    for name, kws in rules:
        if any(k in chapter_title for k in kws):
            return name
    return "世界地理" if book.startswith(("七", "八")) else "人文地理"


def sort_secs(secs):
    return sorted(secs, key=lambda s: CN.get(s["no"], 99))


def main():
    sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
    topics, n = [], 0
    for book, chapters in sk.items():
        g, sem = GRADE[book]
        for ch in chapters:
            n += 1
            chap_full = f"{book} 第{ch['no']}章 {ch['title']}"
            uid = f"gxj_p{n:03d}"
            topics.append({
                "id": uid, "name": ch["title"], "subject": "geography-xiangjiao",
                "domain": domain_of(book, ch["title"]), "grade": g, "semester": sem,
                "chapter": chap_full, "type": "conceptual", "level": "unit",
                "description": "", "mastery_criteria": [],
                "diagnostic_question": {"question": "", "answer": ""},
                "external": False, "standards": [], "tags": [], "prerequisites": [],
                "curriculumRef": "", "verified": False,
            })
            for sec in sort_secs(ch["sections"]):
                n += 1
                topics.append({
                    "id": f"gxj_p{n:03d}", "name": sec["title"], "subject": "geography-xiangjiao",
                    "domain": domain_of(book, ch["title"]), "grade": g, "semester": sem,
                    "chapter": f"{chap_full} · 第{sec['no']}节 {sec['title']}",
                    "type": "conceptual", "level": "lesson",
                    "description": "", "mastery_criteria": [],
                    "diagnostic_question": {"question": "", "answer": ""},
                    "external": False, "standards": [], "tags": [], "prerequisites": [],
                    "curriculumRef": "", "verified": False,
                })
    json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    units = sum(1 for t in topics if t["level"] == "unit")
    print(f"生成 {len(topics)} 点（单元 {units} / 课时 {len(topics)-units}）→ {D}/topics.json")


if __name__ == "__main__":
    main()
