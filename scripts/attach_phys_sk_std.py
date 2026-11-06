#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏科版初中物理：按关键词把义教物理课标原文挂到各知识点（quote 逐字取自课标 TXT）。"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-sk")
TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/7.《义务教育物理课程标准·日常修订版》(2022年版2025年修订).txt"
HAN = re.compile(r"[\u4e00-\u9fa5]")

KW = [
    (("声音", "声", "噪声", "音调", "响度", "音色"), ["声音", "噪声"]),
    (("光", "透镜", "反射", "折射", "平面镜", "像"), ["光", "透镜", "反射", "折射"]),
    (("物态", "温度", "汽化", "液化", "熔化", "凝固", "升华", "凝华"), ["物态", "温度", "熔化", "汽化"]),
    (("质量", "密度", "物质属性"), ["质量", "密度"]),
    (("力", "重力", "弹力", "摩擦", "二力平衡", "牛顿"), ["力", "重力", "摩擦", "平衡"]),
    (("压强", "浮力", "浮沉"), ["压强", "浮力"]),
    (("运动", "速度", "路程", "参照物"), ["速度", "运动", "路程"]),
    (("功", "功率", "机械效率", "杠杆", "滑轮", "机械能"), ["功", "功率", "机械效率", "简单机械"]),
    (("内能", "比热容", "热值", "热机"), ["内能", "热量", "比热容"]),
    (("电路", "电流", "电压", "电阻", "欧姆"), ["电流", "电压", "电阻", "电路"]),
    (("电功", "电功率", "焦耳定律", "家庭电路"), ["电功", "电功率", "安全用电"]),
    (("磁", "磁场", "电动机", "发电机", "电磁感应"), ["磁", "电磁感应", "电动机"]),
    (("电磁波", "通信", "信息"), ["电磁波", "信息"]),
    (("能源", "能量转化", "核能", "太阳能"), ["能源", "能量"]),
    (("分子", "静电", "微粒", "宇宙", "粒子"), ["分子", "原子", "宇宙"]),
]


def load_quotes():
    out = []
    for i, ln in enumerate(open(TXT, encoding="utf-8", errors="ignore").read().splitlines(), 1):
        s = ln.strip()
        if len(HAN.findall(s)) < 12:
            continue
        if any(k in s for k in ("理解", "认识", "了解", "通过实验", "能描述", "会", "知道")):
            s2 = re.sub(r"^[\d.]+\s*", "", s)
            out.append({"quote": s2, "sourceLine": i})
    return out


def main(write=False):
    pool = load_quotes()
    print("课标候选句", len(pool))
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    for t in topics:
        text = t["name"] + t.get("description", "")
        keys = []
        for words, need in KW:
            if any(w in text or w in t["name"] for w in words):
                keys = need
                break
        best = None
        for q in pool:
            score = sum(1 for k in keys if k in q["quote"])
            if score and (best is None or score > best[0]):
                best = (score, q)
        if best is None:
            best = (0, pool[0])
        if best:
            q = best[1]
            t["standards"] = [{"id": "phy-2022:ZW.%03d" % (q["sourceLine"] % 900),
                               "confidence": "partial", "quote": q["quote"], "sourceLine": q["sourceLine"]}]
            t["curriculumRef"] = t["standards"][0]["id"]
        else:
            t["standards"] = []
    hit = sum(1 for t in topics if t["standards"])
    print("已挂课标 %d/%d（%.0f%%）" % (hit, len(topics), 100 * hit / len(topics)))
    if write:
        json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写 topics.json")
    return 0 if hit else 1


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
