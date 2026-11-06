#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科教版高中物理：生成 topics.json（占位）＋ _bank_spec（逐章一片，题槽预分配）。

题槽口径：节 8 题＝选择4／填空2／简答1／数值1；章 5 题＝选择3／填空1／简答1。
难度按「每点三档齐」铺：4 选择＝basic,standard,standard,hard；2 填空＝basic,hard；
简答＝standard；数值＝hard。选项答案位按点序轮转 A/B/C/D。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
SUBJECT = "physics-hkjy"


def main(write=False):
    sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
    by_unit = {}
    for t in sk:
        if t["level"] == "unit":
            by_unit[t["id"]] = [t] + [x for x in sk if x["level"] == "lesson"
                                      and x["chapter"].startswith(t["chapter"] + " · ")]

    # 1) topics.json：课时点先给占位描述（由工位在 _points 里回填）
    topics = []
    for t in sk:
        t = dict(t)
        if t["level"] == "lesson":
            t["description"] = t.get("description") or "本课时围绕「%s」展开，讲清概念、规律与典型应用。" % t["name"]
            t["mastery_criteria"] = t.get("mastery_criteria") or [
                "能说出「%s」的核心概念与适用条件" % t["name"],
                "能完成一道本课时的基础计算或分析",
            ]
            t["diagnostic_question"] = {"question": "关于「%s」，下列说法正确的是" % t["name"], "answer": "A"}
        else:
            t["diagnostic_question"] = {"question": "本章「%s」的主线是什么" % t["name"], "answer": "A"}
        topics.append(t)

    # 2) 题槽
    os.makedirs(os.path.join(D, "_bank_spec"), exist_ok=True)
    shards = {}
    for sid, unit in enumerate(sk):
        pass
    # 按章聚合
    units = [t for t in sk if t["level"] == "unit"]
    total = 0
    for i, u in enumerate(units, 1):
        sid = "T%02d" % i
        items = []
        for p in by_unit[u["id"]]:
            lesson = p["level"] == "lesson"
            if lesson:
                plan = [("choice", "basic"), ("choice", "standard"), ("choice", "standard"), ("choice", "hard"),
                        ("fill", "basic"), ("fill", "hard"), ("short-answer", "standard"), ("numeric", "hard")]
            else:
                plan = [("choice", "basic"), ("choice", "standard"), ("fill", "basic"),
                        ("short-answer", "standard"), ("numeric", "hard")]
            slots = []
            for k, (typ, diff) in enumerate(plan, 1):
                label = "ABCD"[(i + k) % 4] if typ == "choice" else None
                slots.append({"id": "%s_q%02d" % (p["id"], k), "type": typ,
                              "difficulty": diff, "label": label})
            total += len(slots)
            items.append({"topicId": p["id"], "name": p["name"], "level": p["level"],
                          "chapter": p["chapter"], "slots": slots})
        spec = {"shard": sid, "bucket": SUBJECT, "book": u["chapter"].split(" ")[0],
                "chapter": u["chapter"], "unitId": u["id"], "domain": u["domain"],
                "grade": u["grade"], "semester": u["semester"],
                "outBank": "data/physics-hkjy/_bank/%s.json" % sid,
                "outPoints": "data/physics-hkjy/_points/%s.json" % sid,
                "items": items}
        shards[sid] = spec
        if write:
            json.dump(spec, open(os.path.join(D, "_bank_spec", sid + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    print("章 %d 片｜题槽合计 %d｜点 %d（章 %d／节 %d）" % (
        len(shards), total, len(topics),
        sum(1 for t in topics if t["level"] == "unit"),
        sum(1 for t in topics if t["level"] == "lesson")))
    if write:
        json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写入 topics.json 与 _bank_spec/%d 片" % len(shards))
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
