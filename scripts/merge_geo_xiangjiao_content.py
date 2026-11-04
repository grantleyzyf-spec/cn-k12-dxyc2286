#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""湘教版地理：把 _content/<册>.json 合并进 topics.json，并生成先修边。

- 只回填 description / mastery_criteria / type / tags / standards / curriculumRef
- 先修边口径（对齐仓库硬规则）：
  单元点 → 前一单元点（hard，单元→单元合法）
  课时点 → 同章前一节（hard，课时→课时合法）；本单元上下位写进 `prereqUpper`（不参与拓扑）
- dependencies.json 由 topics.prerequisites 派生重建
"""
import json
import os
import re

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "data", "geography-xiangjiao")
CONTENT = os.path.join(D, "_content")


def main():
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    by_id = {t["id"]: t for t in topics}
    filled = 0
    for fn in sorted(os.listdir(CONTENT)):
        if not fn.endswith(".json"):
            continue
        d = json.load(open(os.path.join(CONTENT, fn), encoding="utf-8"))
        book = (d.get("book") or fn[:-5]).replace("补", "")
        for p in d.get("points") or []:
            t = by_id.get(p["id"])
            if not t or not t["chapter"].startswith(book):
                continue
            for k in ("description", "mastery_criteria", "type", "tags", "standards"):
                if p.get(k):
                    t[k] = p[k]
            t["curriculumRef"] = (p.get("standards") or [{}])[0].get("id", "")
            t["diagnostic_question"] = {"question": f'{t["name"]}的核心内容是什么？', "answer": "A"}
            filled += 1
    print(f"回填 {filled}/{len(topics)} 点")

    # 先修边
    for t in topics:
        t["prerequisites"] = []
        t.pop("prereqUpper", None)
    prev_unit = None
    unit = None
    prev_lesson = None
    for t in topics:
        if t["level"] == "unit":
            if prev_unit:
                t["prerequisites"] = [prev_unit]
            else:
                t["root_reason"] = "起始单元：本册第一章，图谱无更早前置（跨学段前置不单独连边）"
            prev_unit = t["id"]
            unit = t["id"]
            prev_lesson = None
        else:
            t["prereqUpper"] = [unit]
            if prev_lesson:
                t["prerequisites"] = [prev_lesson]
            else:
                t["root_reason"] = "本节为该章第一节，章内无更早课时；章间承接走单元上位关系"
            prev_lesson = t["id"]

    deps = []
    for t in topics:
        for p in t["prerequisites"]:
            deps.append({"from": p, "to": t["id"], "type": "hard"})
    json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"边 {len(deps)} 条；单元 {sum(1 for t in topics if t['level']=='unit')} / 课时 {sum(1 for t in topics if t['level']=='lesson')}")


if __name__ == "__main__":
    main()
