#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""粤教粤人版初中地理：生成 topics.json / dependencies.json / _skeleton.json

- 19 单元点 + 152 课时点（每单元 8 课时，来自大单元 docx 第十五部分）
- id 段 gyj_p001..gyj_p171，先单元点、后该单元 8 个课时点
- domain 取义教地理课标四领域：地球与地图 / 世界地理 / 中国地理 / 乡土地理
- standards 逐字取自《义务教育地理课程标准（2022年版2025年修订）》TXT，回表由 test_geo_yuejiao.py 复核
"""
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-yuejiao")
OUTLINE = os.path.join(D, "_outline.json")
STD_TXT = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
           "6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt")

DOMAIN = {
    ("七年级上册", "一"): "地球与地图", ("七年级上册", "二"): "地球与地图", ("七年级上册", "三"): "地球与地图",
    ("七年级上册", "四"): "世界地理", ("七年级上册", "五"): "世界地理",
    ("七年级下册", "六"): "世界地理", ("七年级下册", "七"): "世界地理",
    ("七年级下册", "八"): "世界地理", ("七年级下册", "九"): "世界地理",
    ("八年级上册", "一"): "中国地理", ("八年级上册", "二"): "中国地理", ("八年级上册", "三"): "中国地理",
    ("八年级上册", "四"): "中国地理", ("八年级上册", "五"): "中国地理",
    ("八年级下册", "六"): "中国地理", ("八年级下册", "七"): "中国地理",
    ("八年级下册", "八"): "中国地理", ("八年级下册", "九"): "中国地理", ("八年级下册", "十"): "中国地理",
}

Q = {
    "七上1": ["结合科学故事、史实材料等，说出人类对地球形状的认识过程，使用数据、类比等方式描述地球的大小。",
              "在地球仪上识别经线和纬线，说出经度和纬度的分布规律;用经纬度描述某一地理事物或现象所在地的位置。",
              "在地图上辨别方向，判读经度和纬度，量算距离，识别图例所表示的地理事物或现象，并描述地理事物或现象的空间分布特征。",
              "结合地形观察，说出等高线地形图、分层设色地形图表示地形的方法;在地形图上识别一些基本地形。"],
    "七上2": ["运用图片、影视资料以及数字技术等手段，描述地球的宇宙环境、地球在太阳系中的位置，认识地球是迄今人类唯一的家园。",
              "结合图片、影视资料等，描述探月工程、火星探测以及空间站建设等人类太空探索的进展与意义。",
              "收集中国航天及太空观测发展的相关材料，举例说出中国太空探索的成就。"],
    "七上3": ["运用地球仪或软件，演示地球的自转运动，说出地球的自转方向、周期。",
              "运用模型或软件，演示地球的公转运动，说出地球的公转方向、周期。",
              "结合实例，说出地球自转产生的主要自然现象及其对人们生产生活的影响。",
              "结合实例，说出地球公转产生的主要自然现象及其对人们生产生活的影响。"],
    "七上4": ["阅读世界地图，描述世界海陆分布状况，说出七大洲、四大洋的分布。",
              "结合实例，说明海洋和陆地处于不断的运动变化之中;说出板块构造学说的基本观点，并解释世界火山、地震带的分布与板块运动的关系。",
              "收看天气预报节目，识别常见的天气符号，模拟播报天气。",
              "阅读世界气候类型分布图，描述世界主要气候类型的分布特征;结合实例，说明纬度位置、海陆分布、地形等对气候的影响。"],
    "七上5": ["运用地图和相关资料，描述并简要归纳世界人口数量变化和人口空间分布特点。",
              "通过阅读图像、观看视频或实地考察等，描述城镇与乡村的景观特征及其变化。",
              "运用反映人种、语言、宗教、习俗等内容的图文资料，描述世界文化的丰富多彩，树立尊重世界文化多样性的意识。",
              "以某发达国家和某发展中国家为例，描述不同国家发展水平的差异。"],
    "七下6": ["运用地图和相关资料，描述某大洲的地理位置，并依据大洲地理位置特点，判断大洲所处热量带和降水的空间分布概况。",
              "简要归纳某大洲的地形、气候",
              "运用地图和相关资料，说出某国家的地理位置、范围、领土构成和首都;选择与该国地理位置差异明显的国家，比较它们纬度位置和海陆位置的差异。",
              "运用地图和相关资料，联系某国家的自然地理环境特点，结合实例简要分析该国因地制宜发展经济的途径。"],
    "七下7": ["以某地区的一种自然资源为例，说出该资源在当地的分布状况、对外输出地区以及对当地乃至世界的重要意义。",
              "运用地图和相关资料，简要分析某国家在资源开发、环境保护方面的经验和教训。",
              "运用地图和相关资料，联系某国家的自然地理环境特点，结合实例简要分析该国因地制宜发展经济的途径。"],
    "七下8": ["结合实例，说明某地区发展旅游业的优势。",
              "结合某国家的实例，简要说明该国家与其他国家在经济社会等方面的联系及其意义。",
              "结合实例，描述不同区域的差异，说明区域联系和协同发展对经济社会发展的意义。"],
    "七下9": ["根据南极、北极地区自然地理环境的特殊性，说明开展极地科学考察和保护极地环境的重要性。",
              "结合实例，简要说明一个国家对某地自然环境的改造活动对其他地方自然环境的影响。",
              "协调人地关系是人类社会可持续发展的必然选择，人与自然和谐共生是中国式现代化的特色之一"],
    "八上1": ["运用地图，描述中国的地理位置",
              "运用中国行政区划图，识别 34 个省级行政区，记住它们的简称和行政中心。",
              "运用地图和相关资料，描述中国人口的基本状况和变化。",
              "运用地图和相关资料，简要归纳中国的民族分布特点，树立中华民族共同体意识。",
              "钓鱼岛及其附属岛屿是中国固有领土，增强国家版图意识与海洋权益意识"],
    "八上2": ["简要归纳中国地形、和气候、河湖等的特征",
              "运用地图和相关资料，描述长江、黄河的特点，举例说明其对经济发展和人们生活的影响。",
              "运用地图和相关资料，描述中国主要的自然灾害和环境问题;针对某一自然灾害或环境问题提出合理的防治建议;掌握一定的气象灾害和地质灾害的安全防护技能。"],
    "八上3": ["运用地图和相关资料，描述中国水资源、土地资源、矿产资源和海洋资源等自然资源的主要特征，举例说明自然资源与人们生产生活的关系，认识开发、利用、保护自然资源的重要意义。"],
    "八上4": ["中国农业、工业等生产活动的分布",
              "并用实例说明科学技术在产业发展中的重要作用",
              "说明中国交通运输线的分布特征"],
    "八上5": ["进行野外考察或运用相关资料，说明自然环境与地方文化景观之间的关系。",
              "描述中国不同地区的主要地理特征，比较区域差异",
              "能够观察、描述地球上人口、城乡、文化等人文环境要素的基本状况"],
    "八下6": ["运用地图、图像等资料，说明秦岭一淮河等重要自然地理界线在地理分区中的意义。",
              "结合实例，描述不同区域的差异",
              "描述中国不同地区的主要地理特征，比较区域差异"],
    "八下7": ["运用地图和相关资料，说明北京的自然地理特点、历史文化传统和城市建设成就，认识首都职能。",
              "认识台湾自古以来就是中国不可分割的领土",
              "说出某区域的地理位置和自然地理特征，说明自然条件对该区域经济社会发展的影响"],
    "八下8": ["以某地区的一种自然资源为例，说出该资源在当地的分布状况",
              "初步形成因地制宜、区域协调发展的观念",
              "结合实例，简要说明一个国家对某地自然环境的改造活动对其他地方自然环境的影响。"],
    "八下9": ["说明区域联系和协同发展对经济社会发展的意义",
              "从区域的视角说明人类活动与自然环境和资源的关系",
              "结合实例，说明加强国际合作的重要意义"],
    "八下10": ["协调人地关系是人类社会可持续发展的必然选择，人与自然和谐共生是中国式现代化的特色之一",
               "描述和说明中国基本的地理面貌，表达热爱祖国的情感",
               "初步形成因地制宜、区域协调发展的观念"],
}

CN2INT = {c: i for i, c in enumerate("一二三四五六七八九十", 1)}


def main():
    src = re.sub(r"\s+", "", open(STD_TXT, encoding="utf-8").read())
    # 已入库的 (id, quote) 池，命中即沿用 id
    pool = {}
    for b in ("geography", "geography-kepu", "geography-jin", "geography-shangwu", "geography-xiangjiao"):
        p = os.path.join(REPO, "data", b, "topics.json")
        if not os.path.exists(p):
            continue
        for t in json.load(open(p, encoding="utf-8")):
            for s in t.get("standards") or []:
                pool.setdefault(s["quote"], s["id"])
    mint = [66]
    outline = json.load(open(OUTLINE, encoding="utf-8"))

    def _fit(quote):
        for i in range(len(quote)):
            q = quote[i:]
            while q and re.sub(r"\s+", "", q) not in src:
                q = q[:-1]
            if len(q) >= 10:
                return q
        return ""

    def std(quote):
        q = _fit(quote)
        assert q, f"课标引文回表失败：{quote[:30]}"
        i = pool.get(q)
        if not i:
            # 允许池内同一句带/不带句末标点
            for pq, pid in pool.items():
                if pq.startswith(q[:20]) and re.sub(r"\s+", "", pq) in src:
                    i, q = pid, pq
                    break
        if not i:
            i = f"geo-2022:4.NR.{mint[0]:02d}"
            mint[0] += 1
        return {"id": i, "confidence": "partial", "quote": q}

    topics, deps, skeleton = [], [], []
    n = 0
    for blk in outline:
        book = blk["book"]
        grade = int(re.search(r"([七八九])年级", book).group(1).translate(str.maketrans("七八九", "789")))
        sem = "上" if "上" in book else "下"
        for u in blk["units"]:
            cn = u["unit"]
            dom = DOMAIN[(book, cn)]
            n += 1
            uid = f"gyj_p{n:03d}"
            chap = f"{book} 第{cn}单元 {u['name']}"
            topics.append({
                "id": uid, "name": u["name"], "subject": "geography-yuejiao", "domain": dom,
                "grade": grade, "semester": sem, "chapter": chap, "level": "unit",
                "type": "conceptual",
                "description": f"本单元「{u['name']}」共 8 课时，梳理该单元的主干概念、读图方法与区域认知路径，形成可迁移的地理思维。",
                "mastery_criteria": [f"能说出「{u['name']}」的主干概念与读图方法",
                                     f"能把本单元知识迁移到{dom}的真实情境中"],
                "diagnostic_question": {"question": f"关于「{u['name']}」，下列说法正确的是？", "answer": ""},
                "external": False, "standards": [std(q) for q in Q[f"{book[0]}{'下' if '下' in book else '上'}{CN2INT[cn]}"]],
                "tags": [dom, u["name"]], "prerequisites": [], "root_reason": "单元上位点，不设先修课时",
                "curriculumRef": "", "verified": False,
            })
            topics[-1]["curriculumRef"] = topics[-1]["standards"][0]["id"]
            ustd = topics[-1]["standards"]
            skeleton.append({"id": uid, "book": book, "unit": cn, "name": u["name"],
                             "chapter": chap, "domain": dom, "lessons": len(u["lessons"])})
            prev = None
            for i, (no, title) in enumerate(u["lessons"], 1):
                n += 1
                lid = f"gyj_p{n:03d}"
                topics.append({
                    "id": lid, "name": title, "subject": "geography-yuejiao", "domain": dom,
                    "grade": grade, "semester": sem, "chapter": f"{chap} · {title}", "level": "lesson",
                    "type": "conceptual",
                    "description": f"本课时学习「{title}」，围绕{dom}的核心概念与读图方法展开，能在实例中说明其地理意义。",
                    "mastery_criteria": [f"能说明「{title}」的基本内容",
                                         f"能运用相关知识解释{dom}中的具体现象"],
                    "diagnostic_question": {"question": f"关于「{title}」，下列叙述正确的是？", "answer": ""},
                    "external": False, "standards": ustd,
                    "tags": [dom, title], "prerequisites": [prev] if prev else [],
                    "prereqUpper": uid, "root_reason": "" if prev else "单元起始课时，无先修",
                    "curriculumRef": ustd[0]["id"], "verified": False,
                })
                if prev:
                    deps.append({"from": prev, "to": lid, "type": "hard"})
                prev = lid

    json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(skeleton, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"知识点 {len(topics)}（单元 {len(skeleton)} + 课时 {len(topics)-len(skeleton)}）/ 边 {len(deps)}")
    print("minted ids:", mint[0] - 66)


if __name__ == "__main__":
    main()
