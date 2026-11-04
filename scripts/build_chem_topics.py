#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：由 _skeleton.json 生成 topics.json / dependencies.json（保留已有 id）。

口径：
- 单元点 `level=unit`（每单元/章 1 个）、课时点 `level=lesson`（每课题/节 1 个）。
- 课时点 `prereqUpper=[uid]`（不写 unit→lesson 硬边，避免与「课时先修只连课时」互斥）。
- 先修链：同单元内课时按教材顺序成链；每单元首课时 `prerequisites=[]` + `root_reason`。
- 已有 72 点按「册＋点名」复用 id（id 只增不改），新增点续号 chem_p1xx / chem_h1xx。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")

UNIT_DOMAIN = {
    "走进化学世界": "科学探究与化学实验", "空气和氧气": "物质的性质与应用",
    "物质构成的奥秘": "物质的组成与结构", "自然界的水": "物质的性质与应用",
    "化学反应的定量关系": "物质的化学变化", "碳和碳的氧化物": "物质的性质与应用",
    "能源的合理利用与开发": "化学与社会·跨学科实践", "金属和金属材料": "物质的性质与应用",
    "溶液": "物质的性质与应用", "常见的酸、碱、盐": "物质的性质与应用",
    "化学与社会": "化学与社会·跨学科实践",
    "物质及其变化": "物质的化学变化", "海水中的重要元素——钠和氯": "物质的性质与应用",
    "铁 金属材料": "物质的性质与应用", "物质结构 元素周期律": "物质的组成与结构",
    "化工生产中的重要非金属元素": "物质的性质与应用", "化学反应与能量": "物质的化学变化",
    "有机化合物": "物质的性质与应用", "化学与可持续发展": "化学与社会·跨学科实践",
    "化学反应的热效应": "物质的化学变化", "化学反应速率与化学平衡": "物质的化学变化",
    "水溶液中的离子反应与平衡": "物质的化学变化", "化学反应与电能": "物质的化学变化",
    "原子结构与性质": "物质的组成与结构", "分子结构与性质": "物质的组成与结构",
    "晶体结构与性质": "物质的组成与结构",
    "有机化合物的结构特点与研究方法": "物质的组成与结构", "烃": "物质的性质与应用",
    "烃的衍生物": "物质的性质与应用", "生物大分子": "物质的性质与应用",
    "合成高分子": "物质的性质与应用",
}


def norm(s):
    return re.sub(r"\s+|·|：|:", "", s or "")


def main():
    sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
    old = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    pool = {}
    for t in old:
        pool.setdefault((t["chapter"].split(" ")[0], norm(t["name"])), t)
    used = set()
    maxp = max([int(re.sub(r"\D", "", t["id"])) for t in old if t["id"].startswith("chem_p")] or [0])
    maxh = max([int(re.sub(r"\D", "", t["id"])) for t in old if t["id"].startswith("chem_h")] or [0])
    topics, deps = [], []
    reused = added = 0
    for b in sk["books"]:
        book = b["book"]
        is_primary = b["stage"] == "初中"
        prev_unit_id = None
        for u in b["units"]:
            dom = UNIT_DOMAIN.get(u["name"], "物质的性质与应用")
            uid = f"chem_u{b['grade']}{u['no']:02d}" if False else None
            # 单元 id 用全局序号，保证唯一且可读
            uid = f"chem_u{len([t for t in topics if t.get('level') == 'unit']) + 1:03d}"
            chapter = f"{book} 第{u['no']}{u['kind']} {u['name']}"
            lesson_names = [l["name"] for l in u["lessons"]]
            topics.append({
                "id": uid, "name": u["name"], "subject": "chemistry", "domain": dom,
                "grade": b["grade"], "semester": b["semester"], "chapter": chapter,
                "level": "unit", "type": "conceptual",
                "description": (f"本{u['kind']}围绕「{u['name']}」组织教学，覆盖"
                                + "、".join(lesson_names)
                                + f"，共 {len(lesson_names)} 个课题。")[:118],
                "mastery_criteria": [f"能说出「{u['name']}」的核心概念与研究对象",
                                     f"能在本{u['kind']}范围内建立课题之间的联系并解决综合问题"],
                "tags": [dom, u["name"]], "standards": [], "prerequisites": [],
                "root_reason": f"{u['kind']}上位点，按教材{u['kind']}顺序承接，不设课时先修",
                "diagnostic_question": {"question": f"关于「{u['name']}」，下列整体认识正确的是",
                                        "answer": "A"},
            })
            prev_lesson = None
            for idx, l in enumerate(u["lessons"]):
                key = (book, norm(l["name"]))
                hit = pool.get(key)
                if hit and hit["id"] not in used:
                    lid = hit["id"]
                    used.add(lid)
                    reused += 1
                else:
                    if is_primary:
                        maxp += 1
                        lid = f"chem_p{maxp:03d}"
                    else:
                        maxh += 1
                        lid = f"chem_h{maxh:03d}"
                    added += 1
                lchapter = f"{chapter} · 第{l['no']}{l['kind']} {l['name']}"
                t = {
                    "id": lid, "name": l["name"], "subject": "chemistry", "domain": dom,
                    "grade": b["grade"], "semester": b["semester"], "chapter": lchapter,
                    "level": "lesson", "type": "conceptual",
                    "description": f"学习「{l['name']}」：掌握本{l['kind']}的核心概念、典型事实与基本方法。",
                    "mastery_criteria": [f"能说出「{l['name']}」涉及的核心概念与事实",
                                         f"能用本{l['kind']}的方法解释相关现象或解决简单问题"],
                    "tags": [dom, u["name"]], "standards": [],
                    "prereqUpper": [uid],
                    "prerequisites": [prev_lesson] if prev_lesson else [],
                }
                if not prev_lesson:
                    t["root_reason"] = f"本{u['kind']}首{l['kind']}，单元内无更早课时"
                topics.append(t)
                if prev_lesson:
                    deps.append({"from": prev_lesson, "to": lid, "type": "hard"})
                prev_lesson = lid
            prev_unit_id = uid
    out = topics
    with open(os.path.join(D, "topics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8") as f:
        json.dump(deps, f, ensure_ascii=False, indent=1)
        f.write("\n")
    # 把旧库里未匹配上的点存档，便于追查
    legacy = [t for t in old if t["id"] not in used]
    with open(os.path.join(D, "_legacy_topics.json"), "w", encoding="utf-8") as f:
        json.dump(legacy, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"点 {len(out)}（unit {sum(1 for t in out if t.get('level')=='unit')} / "
          f"lesson {sum(1 for t in out if t.get('level')=='lesson')}）边 {len(deps)}")
    print(f"复用旧 id {reused}，新增 {added}，旧库未匹配 {len(legacy)}")


if __name__ == "__main__":
    main()
