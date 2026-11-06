#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科教版高中物理（physics-hkjy）：6 册教材目录 → _skeleton.json / dependencies / _shards。

结构源：沪科教版高中物理必修第一~三册、选择性必修第一~三册 PDF 目录页（p4–p5），逐条抄录。
口径：单元位＝章（31）；课时点＝节（129）；id 前缀 phk_u / phk_j。
⛔ 开篇（0.1–0.3）不建点；总结与评价、研究课题示例、评价表不建点。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
PREFIX = "phk"
SUBJECT = "physics-hkjy"

BOOKS = [
    ("必修第一册", 10, "上", [
        (1, "物体运动的描述", "力学",
         ["运动与质点模型", "怎样描述运动的快慢", "怎样描述运动的快慢(续)", "怎样描述速度变化的快慢"]),
        (2, "匀变速直线运动的规律", "力学",
         ["伽利略对落体运动的研究", "匀变速直线运动的规律", "自由落体运动的规律", "匀变速直线运动规律的应用"]),
        (3, "力与相互作用", "力学",
         ["重力", "弹力", "摩擦力", "分析物体的受力情况", "怎样求合力", "怎样分解力", "共点力的平衡及其应用"]),
        (4, "牛顿运动定律", "力学",
         ["牛顿第一定律", "探究加速度与力、质量的关系", "牛顿第二定律", "牛顿第三定律",
          "牛顿运动定律的案例分析", "超重与失重"]),
    ]),
    ("必修第二册", 10, "下", [
        (1, "功和机械能", "力学",
         ["动能变化跟做功的关系", "功与功率", "动能定理的应用", "势能的变化与机械功", "机械能守恒定律"]),
        (2, "抛体运动", "力学",
         ["飞机投弹与平抛运动", "平抛运动的规律", "斜抛运动"]),
        (3, "圆周运动", "力学",
         ["怎样描述圆周运动", "匀速圆周运动的规律", "圆周运动的案例分析", "离心现象及其应用"]),
        (4, "万有引力与航天", "力学",
         ["从托勒密到开普勒", "万有引力定律是怎样发现的", "飞出地球去"]),
        (5, "经典力学的局限性与相对论初步", "近代物理",
         ["经典力学的巨大成就和局限性", "狭义相对论的基本原理", "相对论的时空观与宇宙演化"]),
    ]),
    ("必修第三册", 11, "上", [
        (1, "电荷的相互作用", "电磁学",
         ["静电现象与电荷守恒", "电荷相互作用的规律", "静电的应用和防护"]),
        (2, "电场的性质", "电磁学",
         ["电场强度", "电场力做功的特点 电势能", "电势 电荷在电场中的运动", "电容器 电容"]),
        (3, "电路", "电磁学",
         ["多用电表", "电流、电压和电阻", "影响电阻的因素"]),
        (4, "闭合电路欧姆定律", "电磁学",
         ["闭合电路欧姆定律", "闭合电路欧姆定律的应用", "电路中的能量转化与守恒", "现代家庭电路"]),
        (5, "电磁场与电磁波", "电磁学",
         ["磁与人类文明", "磁场的描述", "电磁感应", "电磁波"]),
        (6, "能源与可持续发展", "热学",
         ["能量的转化与守恒", "能源利用与环境污染", "能源开发与环境保护",
          "节约能源、保护资源与可持续发展"]),
    ]),
    ("选择性必修第一册", 11, "上", [
        (1, "碰撞与动量守恒", "力学",
         ["动量变化与冲量的关系", "动量守恒定律", "动量守恒定律的案例分析", "美妙的守恒定律"]),
        (2, "机械振动", "力学",
         ["简谐运动", "物体做简谐运动的原因", "摆钟的物理原理", "单摆振动的周期", "受迫振动与共振"]),
        (3, "机械波", "力学",
         ["机械波的产生", "机械波的描述", "机械波案例分析", "惠更斯原理 波的反射与折射",
          "波的干涉与衍射", "多普勒效应"]),
        (4, "光及其应用", "光学",
         ["光的折射", "全反射与光导纤维", "光的干涉", "用双缝干涉仪测量光的波长",
          "光的衍射", "光的偏振与立体电影", "激光"]),
    ]),
    ("选择性必修第二册", 11, "下", [
        (1, "磁场力与现代科技", "电磁学",
         ["安培力", "洛伦兹力", "洛伦兹力与现代科技"]),
        (2, "电磁感应与现代生活", "电磁学",
         ["感应电流产生的条件", "感应电流的方向—楞次定律",
          "感应电动势的大小—法拉第电磁感应定律", "电磁感应的案例分析",
          "自感现象与日光灯", "涡流现象与电磁炉"]),
        (3, "交变电流的产生与输送", "电磁学",
         ["交变电流的产生", "交变电流的描述", "电能的输送", "变压器为什么能改变电压"]),
        (4, "电磁振荡与电磁波", "电磁学",
         ["麦克斯韦的电磁场理论", "电磁振荡和电磁波", "无线电通信", "电磁波家族"]),
        (5, "传感器与现代社会", "电磁学",
         ["传感器的原理", "热敏电阻的温度特性", "用传感器制作自动控制装置",
          "信息时代离不开传感器"]),
    ]),
    ("选择性必修第三册", 11, "下", [
        (1, "分子动理论", "热学",
         ["走进分子世界", "无序中的有序", "分子动理论 内能"]),
        (2, "气体定律与人类生活", "热学",
         ["气体的状态", "玻意耳定律", "查理定律和盖-吕萨克定律"]),
        (3, "固体、液体与新材料", "热学",
         ["固体的性质", "液体的表面性质", "液晶与显示器", "半导体材料和纳米材料"]),
        (4, "热力学定律", "热学",
         ["热力学第一定律", "能量守恒定律", "热力学第二定律"]),
        (5, "原子世界探秘", "近代物理",
         ["电子的发现", "原子模型的提出", "量子论视野下的原子模型"]),
        (6, "波粒二象性", "近代物理",
         ["光电效应现象", "光电效应的理论解释", "光的波粒二象性", "实物粒子具有波动性"]),
        (7, "原子核与核能", "近代物理",
         ["原子核结构探秘", "原子核的衰变", "原子核的结合能", "裂变与聚变",
          "粒子物理与宇宙起源"]),
    ]),
]


def main(write=False):
    topics, deps, shards = [], [], []
    uid = lid = 0
    prev = None
    for book, grade, sem, units in BOOKS:
        for no, uname, domain, lessons in units:
            uid += 1
            unit_id = "%s_u%03d" % (PREFIX, uid)
            chapter = "%s 第%d章 %s" % (book, no, uname)
            topics.append({
                "id": unit_id, "name": uname, "subject": SUBJECT, "domain": domain,
                "grade": grade, "semester": sem, "chapter": chapter, "level": "unit",
                "type": "conceptual",
                "description": "%s本章围绕「%s」组织，含 %d 个课题，覆盖%s领域的核心概念、规律与研究方法。" % (
                    book + "，", uname, len(lessons), domain),
                "mastery_criteria": ["能说出「%s」的主线与各课题之间的关系" % uname,
                                     "能运用本章规律分析并解决一个实际问题"],
                "tags": [domain, uname], "standards": [],
                "prerequisites": [], "root_reason": "单元上位点，不设先修",
            })
            les_rows = []
            for lname in lessons:
                lid += 1
                tid = "%s_j%03d" % (PREFIX, lid)
                topics.append({
                    "id": tid, "name": lname, "subject": SUBJECT, "domain": domain,
                    "grade": grade, "semester": sem,
                    "chapter": "%s · %s" % (chapter, lname),
                    "level": "lesson", "type": "conceptual",
                    "description": "", "mastery_criteria": [], "tags": [domain, lname],
                    "standards": [], "prerequisites": [prev] if prev else [],
                    "prereqUpper": [unit_id],
                })
                if prev:
                    deps.append({"from": prev, "to": tid, "type": "hard"})
                prev = tid
                les_rows.append({"id": tid, "name": lname})
            shards.append({"shard": "T%02d" % uid, "book": book, "unitId": unit_id,
                           "unitLabel": uname, "no": no, "domain": domain,
                           "grade": grade, "semester": sem,
                           "chapter": chapter, "lessons": les_rows})
    for t in topics:
        if t["level"] == "lesson" and not t["prerequisites"]:
            t["root_reason"] = "本册第一节，作为本教材先修链起点"
    nu = sum(1 for t in topics if t["level"] == "unit")
    nl = sum(1 for t in topics if t["level"] == "lesson")
    print("%s：章 %d ＋ 节 %d ＝ %d 点｜边 %d｜分片 %d" % (SUBJECT, nu, nl, len(topics), len(deps), len(shards)))
    if write:
        os.makedirs(os.path.join(D, "_points"), exist_ok=True)
        os.makedirs(os.path.join(D, "_bank"), exist_ok=True)
        os.makedirs(os.path.join(D, "_shards"), exist_ok=True)
        json.dump(topics, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        for s in shards:
            s["outPoints"] = "data/physics-hkjy/_points/%s.json" % s["shard"]
            s["outBank"] = "data/physics-hkjy/_bank/%s.json" % s["shard"]
            json.dump(s, open(os.path.join(D, "_shards", "%s.json" % s["shard"]), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
        print("已写入 _skeleton / dependencies / _shards（%d 片）" % len(shards))
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
