#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中物理（physics-sk）：教材目录（4 册 PDF）→ _skeleton.json / _shards / _points 规格。

结构源：苏科版物理八上/八下/九上/九下 PDF 目录页（章 → 一、二、… 节）
口径：单元位 = 序言 + 17 章；课时点 = 各节；id 前缀 psk_u / psk_j
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
PREFIX = "psk"
SUBJECT = "physics-sk"

BOOKS = [
    ("八年级上册", 8, "上", "9787571345006_义务教育教科书•物理_八年级_上册_江苏凤凰科学技术出版社_1754905999864.pdf", [
        ("序言", "走进物理世界", "物质的物理属性", ["奇妙的物理现象", "物理学与科技强国", "体验科学探究"]),
        ("第一章", "声现象", "运动和相互作用", ["声音是什么", "声音的特性", "噪声及其控制", "人耳听不到的声音"]),
        ("第二章", "光现象", "运动和相互作用", ["光的色彩", "光的直线传播", "平面镜", "光的反射"]),
        ("第三章", "光的折射 透镜", "运动和相互作用", ["光的折射", "透镜", "凸透镜成像的规律", "透镜的应用", "人眼看不见的光"]),
        ("第四章", "物态变化", "物质", ["物质的三态 温度的测量", "汽化和液化", "熔化和凝固", "升华和凝华", "水循环"]),
        ("第五章", "物体的运动", "运动和相互作用", ["长度与时间的测量", "速度", "直线运动", "运动的相对性"]),
    ]),
    ("八年级下册", 8, "下", "9787571345006_义务教育教科书•物理_八年级_下册_江苏凤凰科学技术出版社_1754905999864.pdf", [
        ("第六章", "物质的物理属性", "物质", ["质量及其测量", "密度", "密度知识的应用", "物质的物理属性"]),
        ("第七章", "力", "运动和相互作用", ["力 弹力", "重力 力的示意图", "摩擦力", "力的作用是相互的"]),
        ("第八章", "力与运动", "运动和相互作用", ["二力平衡", "牛顿第一定律", "力与运动的关系"]),
        ("第九章", "压强和浮力", "运动和相互作用", ["压强", "液体的压强", "气体的压强", "浮力", "物体的浮与沉"]),
        ("第十章", "从粒子到宇宙", "物质", ["走进分子世界", "静电现象", "探索更小的微粒", "日心说与太阳系", "宇宙探秘"]),
    ]),
    ("九年级上册", 9, "上", "9787571345006_义务教育教科书•物理_九年级_上册_江苏凤凰科学技术出版社_1754905999864.pdf", [
        ("第十一章", "简单机械和功", "能量", ["杠杆", "滑轮", "功", "功率", "机械效率"]),
        ("第十二章", "机械能和内能", "能量", ["机械能", "内能 热传递", "物质的比热容", "机械能与内能的相互转化"]),
        ("第十三章", "简单电路", "能量", ["初识家用电器和电路", "电路连接的基本方式", "电流和电流表", "电压和电压表", "串、并联电路的特点"]),
        ("第十四章", "欧姆定律", "能量", ["电阻", "变阻器", "欧姆定律", "欧姆定律的应用"]),
    ]),
    ("九年级下册", 9, "下", "9787571345006_义务教育教科书•物理_九年级_下册_江苏凤凰科学技术出版社_1754905999864.pdf", [
        ("第十五章", "电功和电热", "能量", ["电功", "电功率", "电流的热效应 焦耳定律", "家庭电路与安全用电"]),
        ("第十六章", "电和磁", "运动和相互作用", ["磁体与磁场", "电流的磁场", "磁场对电流的作用 电动机", "电磁感应 发电机"]),
        ("第十七章", "电磁波与现代通信", "运动和相互作用", ["信息与信息传播", "电磁波及其传播", "现代通信"]),
        ("第十八章", "能源与可持续发展", "能量", ["能源利用与社会发展", "核能 太阳能", "能量转化的基本规律", "能源与可持续发展"]),
    ]),
]


def main(write=False):
    topics, deps, shards = [], [], []
    uid = lid = 0
    prev = None
    for book, grade, sem, pdf, units in BOOKS:
        for idx, (no, uname, domain, lessons) in enumerate(units, 1):
            uid += 1
            unit_id = "%s_u%03d" % (PREFIX, uid)
            chapter = ("%s 序言 %s" % (book, uname)) if no == "序言" else ("%s %s %s" % (book, no, uname))
            topics.append({
                "id": unit_id, "name": uname, "subject": SUBJECT, "domain": domain,
                "grade": grade, "semester": sem, "chapter": chapter, "level": "unit",
                "type": "conceptual",
                "description": "%s本%s围绕「%s」组织，含 %d 个课题，覆盖%s领域的核心概念与探究方法。" % (
                    book + "，", "序言" if no == "序言" else "章", uname, len(lessons), domain),
                "mastery_criteria": ["能说出「%s」的主线与各课题之间的关系" % uname,
                                     "能运用本%s知识解释或解决一个实际问题" % ("序言" if no == "序言" else "章")],
                "tags": [domain, uname], "standards": [],
                "prerequisites": [], "root_reason": "单元上位点，不设先修",
            })
            les_rows = []
            for lname in lessons:
                lid += 1
                tid = "%s_j%03d" % (PREFIX, lid)
                topics.append({
                    "id": tid, "name": lname, "subject": SUBJECT, "domain": domain,
                    "grade": grade, "semester": sem, "chapter": "%s · %s" % (chapter, lname),
                    "level": "lesson", "type": "conceptual",
                    "description": "", "mastery_criteria": [], "tags": [domain, lname],
                    "standards": [], "prerequisites": [prev] if prev else [], "prereqUpper": [unit_id],
                })
                if prev:
                    deps.append({"from": prev, "to": tid, "type": "hard"})
                prev = tid
                les_rows.append({"id": tid, "name": lname})
            shards.append({"shard": "T%02d" % uid, "book": book, "unitId": unit_id, "unitLabel": uname,
                           "no": no, "domain": domain, "grade": grade, "semester": sem,
                           "chapter": chapter, "lessons": les_rows})
    for t in topics:
        if t["level"] == "lesson" and not t["prerequisites"]:
            t["root_reason"] = "本册第一节，作为本教材先修链起点"
    nu = sum(1 for t in topics if t["level"] == "unit")
    nl = sum(1 for t in topics if t["level"] == "lesson")
    print("%s：单元 %d ＋ 课时 %d ＝ %d 点｜边 %d｜分片 %d" % (SUBJECT, nu, nl, len(topics), len(deps), len(shards)))
    if write:
        os.makedirs(D, exist_ok=True)
        os.makedirs(os.path.join(D, "_points"), exist_ok=True)
        os.makedirs(os.path.join(D, "_shards"), exist_ok=True)
        json.dump(topics, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for s in shards:
            s["outPoints"] = "data/physics-sk/_points/%s.json" % s["shard"]
            s["outBank"] = "data/physics-sk/_bank/%s.json" % s["shard"]
            json.dump(s, open(os.path.join(D, "_shards", "%s.json" % s["shard"]), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写入 _skeleton / dependencies / _shards")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
