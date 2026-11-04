#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_geo_lujiao_skeleton.py —— 鲁教版高中地理 5 册骨架（19 单元 / 56 节）。

教材：~/Desktop/中小学教材/中小学教材/地理/高中/鲁教版/*.pdf（5 册，均有文字层）
课标：普通高中地理课程标准（2017年版2025年修订）；条目由 /tmp/geo_std_items.json 逐字解析而来
      （G1=地理1／G2=地理2／X1=选必1／X2=选必2／X3=选必3，编号即课标「内容要求」条目号）
产出：data/geography-lujiao/_skeleton.json + _outline.json
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "geography-lujiao")
STD = json.load(open("/tmp/geo_std_items.json", encoding="utf-8"))

BOOKS = [
    # (册名, grade, semester, domain, [(单元号, 单元名, [(节名, [课标条目])])])
    ("必修第一册", 10, "上", "自然地理", [
        ("一", "从宇宙看地球", [("地球的宇宙环境", ["G1.1"]), ("地球的形成与演化", ["G1.3"]),
                                ("地球的圈层结构", ["G1.2"])]),
        ("二", "从地球圈层看地表环境", [("大气圈与大气运动", ["G1.5", "G1.6"]),
                                        ("水圈与水循环", ["G1.7"]), ("生物圈与植被", ["G1.10"])]),
        ("三", "从圈层作用看地貌与土壤", [("走近桂林山水", ["G1.4"]),
                                          ("走进敦煌风成地貌的世界", ["G1.4"]),
                                          ("探秘澜沧江—湄公河流域的河流地貌", ["G1.4"]),
                                          ("分析土壤形成的原因", ["G1.9"])]),
        ("四", "从人地作用看自然灾害", [("自然灾害的成因", ["G1.11"]), ("自然灾害的防避", ["G1.11"])]),
    ]),
    ("必修第二册", 10, "上", "人文地理", [
        ("一", "人口与环境", [("人口分布", ["G2.1"]), ("人口迁移", ["G2.1"]), ("人口合理容量", ["G2.1"])]),
        ("二", "乡村与城镇", [("城乡内部空间结构", ["G2.2"]), ("地域文化与城乡景观", ["G2.3"]),
                              ("城镇化", ["G2.4"])]),
        ("三", "产业区位选择", [("农业的区位选择", ["G2.5"]), ("工业的区位选择", ["G2.5"]),
                                ("服务业的区位选择", ["G2.5"])]),
        ("四", "环境与发展", [("交通运输与区域发展", ["G2.6"]), ("长江经济带发展战略", ["G2.7"]),
                              ("海洋权益与海洋发展战略", ["G2.8", "G2.9"]),
                              ("走可持续发展之路", ["G2.10"])]),
    ]),
    ("选择性必修1", 11, "上", "自然地理", [
        ("一", "地球运动的意义", [("地球自转的意义", ["X1.1"]), ("地球公转的意义", ["X1.1"])]),
        ("二", "地形变化的原因", [("岩石圈的组成及物质循环", ["X1.2"]), ("地形变化的动力", ["X1.3"]),
                                  ("人类活动与地表形态", ["X1.3"])]),
        ("三", "大气变化的效应", [("常见的天气系统", ["X1.4"]), ("气压带、风带与气候", ["X1.5"])]),
        ("四", "水体运动的影响", [("陆地水体及其相互关系", ["X1.6"]), ("洋流及其影响", ["X1.7"]),
                                  ("海-气相互作用及其影响", ["X1.8"])]),
        ("五", "自然环境的特征", [("自然环境的差异性", ["X1.9"]), ("自然环境的整体性", ["X1.9"])]),
    ]),
    ("选择性必修2", 11, "上", "区域发展", [
        ("一", "地理环境与区域发展", [("认识区域", ["X2.1"]), ("比较区域发展的异同", ["X2.2"])]),
        ("二", "不同类型区域的发展", [("生态脆弱地区的发展——以黄土高原地区为例", ["X2.6"]),
                                      ("资源枯竭地区的发展——以德国鲁尔区为例", ["X2.5"]),
                                      ("产业结构转型地区的发展——以珠三角地区为例", ["X2.4"])]),
        ("三", "区域联系与区域发展", [("大都市辐射对区域发展的影响——以上海市为例", ["X2.3"]),
                                      ("产业转移对区域发展的影响——以亚太地区为例", ["X2.7"]),
                                      ("资源跨区域调配对区域发展的影响——以我国南水北调为例", ["X2.7"])]),
        ("四", "区域协调发展", [("区域协调发展的内涵与意义", ["X2.2"]),
                                ("流域内部的协作发展——以尼罗河流域为例", ["X2.8"]),
                                ("国家之间的合作发展——以“一带一路”为例", ["X2.9"])]),
    ]),
    ("选择性必修3", 12, "上", "资源环境与国家安全", [
        ("一", "自然资源与国家安全", [("自然资源与人类活动", ["X3.1"]), ("石油与国家安全", ["X3.2"]),
                                      ("耕地与粮食安全", ["X3.3"]), ("海洋空间资源与国家安全", ["X3.4"])]),
        ("二", "生态环境与国家安全", [("碳排放与环境安全", ["X3.5"]), ("自然保护区与生态安全", ["X3.6"]),
                                      ("污染物跨境转移与环境安全", ["X3.7"]),
                                      ("环境保护与国家安全", ["X3.8"])]),
    ]),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    units, lessons, outline = [], [], []
    ui = li = 0
    for book, grade, sem, domain, us in BOOKS:
        b = {"book": book, "grade": grade, "semester": sem, "domain": domain, "units": []}
        for uno, uname, ls in us:
            ui += 1
            uid = "glj_u%03d" % ui
            uch = "%s 第%s单元 %s" % (book, uno, uname)
            units.append({
                "id": uid, "name": uname, "level": "unit", "subject": "geography-lujiao",
                "chapter": uch, "unitNo": ui, "grade": grade, "semester": sem, "domain": domain,
                "type": "conceptual", "external": False,
                "standards": [{"id": "geo-2017:" + k, "confidence": "partial",
                               "quote": STD[k]} for k in ls[0][1]],
            })
            bu = {"unit": uch, "unitId": uid, "lessons": []}
            for lno, (lname, keys) in enumerate(ls, 1):
                li += 1
                lid = "glj_p%03d" % li
                lch = "%s · 第%s节 %s" % (uch, "一二三四五六七八九十"[lno - 1], lname)
                lessons.append({
                    "id": lid, "name": lname, "level": "lesson", "subject": "geography-lujiao",
                    "chapter": lch, "unitNo": ui, "lessonNo": lno, "grade": grade, "semester": sem,
                    "domain": domain, "type": "conceptual", "external": False, "unitId": uid,
                    "standards": [{"id": "geo-2017:" + k, "confidence": "partial", "quote": STD[k]}
                                  for k in keys],
                })
                bu["lessons"].append({"id": lid, "name": lname, "std": keys})
            units[-1]["lessonCount"] = len(ls)
            b["units"].append(bu)
            outline.append(bu)
        b["lessonCount"] = sum(len(x[2]) for x in us)
        outline_book = b
    sk = {"subject": "geography-lujiao", "edition": "鲁教版", "stage": "高中",
          "books": [{"book": b[0], "grade": b[1], "semester": b[2], "domain": b[3],
                     "units": len(b[4]), "lessons": sum(len(x[2]) for x in b[4])} for b in BOOKS],
          "units": units, "lessons": lessons,
          "counts": {"units": len(units), "lessons": len(lessons), "points": len(units) + len(lessons)}}
    json.dump(sk, open(os.path.join(OUT, "_skeleton.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(outline, open(os.path.join(OUT, "_outline.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("单元 %d ｜ 课时点 %d ｜ 合计 %d" % (len(units), len(lessons), len(units) + len(lessons)))
    for b in sk["books"]:
        print("  %-8s grade=%2d %s ｜ %s ｜ %d 单元 / %d 节" %
              (b["book"], b["grade"], b["semester"], b["domain"], b["units"], b["lessons"]))
    # 断言
    assert len(units) == 19 and len(lessons) == 56
    for t in units + lessons:
        assert t.get("standards") and all(s["quote"] for s in t["standards"]), t["id"]
    print("OK")


if __name__ == "__main__":
    main()
