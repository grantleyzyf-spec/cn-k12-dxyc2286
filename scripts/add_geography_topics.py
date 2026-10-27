#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理学科内容补齐（幂等）：人教版 2012 版初中七下/八上/八下缺失章节 + 人教 2019 版选必2缺失章。
用法: python3 scripts/add_geography_topics.py [--write]
所有 standards.quote 先对课标 TXT 做去空白子串校验，命中才写入。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography")
TP, DP, QP = (os.path.join(D, f) for f in ("topics.json", "dependencies.json", "questions.json"))
WRITE = "--write" in sys.argv

TXT_BASE = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT "
TXT = [TXT_BASE + "/义务教育/6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt",
       TXT_BASE + "/高中教育/（7）普通高中地理课程标准日常修订版（2017年版2025年修订）.txt"]
norm = lambda s: re.sub(r"\s+", "", s or "")
SRC = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))

Q_Y = "运用地图和相关资料，描述某大洲的地理位置"
Q_YZ = "简要归纳某大洲的地形、气候"
Q_DQ = "运用地图和相关资料，描述某地区的地理位置，简要归纳自然地理特征，说明该特征对当地人们生产生活的影响"
Q_DQZY = "以某地区的一种自然资源为例，说出该资源在当地的分布状况、对外输出地区以及对当地乃至世界的重要意义"
Q_LY = "结合实例，说明某地区发展旅游业的优势"
Q_JD = "根据南极、北极地区自然地理环境的特殊性，说明开展极地科学考察和保护极地环境的重要性"
Q_GJ_WZ = "运用地图和相关资料，说出某国家的地理位置、范围、领土构成和首都"
Q_GJ_ZR = "运用地图和相关资料，描述某国家突出的自然地理特征"
Q_GJ_RW = "运用地图和相关资料，说出某国家人文地理主要特点及其与自然地理环境的联系"
Q_GJ_JJ = "运用地图和相关资料，联系某国家的自然地理环境特点，结合实例简要分析该国因地制宜发展经济的途径"
Q_GJ_JY = "运用地图和相关资料，简要分析某国家在资源开发、环境保护方面的经验和教训"
Q_GJ_LX = "结合某国家的实例，简要说明该国家与其他国家在经济社会等方面的联系及其意义"
Q_ZG_ZY = "描述中国水资源、土地资源、矿产资源"
Q_ZG_GX = "举例说明自然资源与人们生产生活的关系"
Q_ZG_QY = "说明区域联系和协同发展对经济社会发展的意义"
Q_H_DS = "以某大都市为例，从区域空间组织的视角出发，说明大都市辐射功能"
Q_H_JG = "以某地区为例，分析地区产业结构变化过程及原因"
Q_H_ZP = "以某区域为例，说明产业转移和资源跨区域调配对区域发展的影响"

ALL_Q = [Q_Y, Q_YZ, Q_DQ, Q_DQZY, Q_LY, Q_JD, Q_GJ_WZ, Q_GJ_ZR, Q_GJ_RW, Q_GJ_JJ, Q_GJ_JY,
         Q_GJ_LX, Q_ZG_ZY, Q_ZG_GX, Q_ZG_QY, Q_H_DS, Q_H_JG, Q_H_ZP]

NEW = [
    # ---------- 七年级下册（人教 2012 版，原库完全缺失）----------
    dict(id="geo_p034", name="亚洲的位置和范围", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第六章 我们生活的大洲——亚洲", type="conceptual",
         description="说明亚洲的半球位置、经纬度位置和海陆位置，说出亚洲与欧洲、非洲的分界线，认识亚洲是世界第一大洲。",
         mastery_criteria=["能在图上指出亚洲的半球位置、经纬度范围与四周濒临的海洋",
                           "能说出亚洲与欧洲、非洲的分界线及亚洲的面积地位"],
         dq=("亚洲与欧洲的分界线是？",
             ["乌拉尔山脉—乌拉尔河—里海—大高加索山脉—黑海—土耳其海峡", "苏伊士运河", "巴拿马运河", "白令海峡"], "A"),
         std=[(Q_Y, "geo-2022:4.NR.24", "exact", 298)],
         tags=["世界地理", "亚洲"], pre=["geo_p009"]),
    dict(id="geo_p035", name="亚洲的自然环境与人文环境", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第六章 我们生活的大洲——亚洲", type="conceptual",
         description="归纳亚洲地形以高原山地为主、地势中部高四周低，气候复杂多样、季风气候显著、大陆性气候分布广的特点，说明亚洲人口分布与经济发展差异。",
         mastery_criteria=["能归纳亚洲的地形与地势特点，并说明其对河流流向的影响",
                           "能说出亚洲气候复杂多样、季风气候显著、大陆性气候分布广的成因"],
         dq=("亚洲地势的总体特征是？",
             ["中部高、四周低", "东高西低", "南高北低", "四周高、中部低"], "A"),
         std=[(Q_YZ, "geo-2022:4.NR.25", "exact", 299)],
         tags=["世界地理", "亚洲", "自然环境"], pre=["geo_p034", "geo_p013"]),
    dict(id="geo_p036", name="日本", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第七章 我们邻近的地区和国家", type="conceptual",
         description="认识日本作为岛国的位置与领土构成，理解多火山地震的原因、海岸线曲折与资源贫乏对加工贸易型经济的影响，说出工业集中分布在太平洋沿岸和濑户内海沿岸的缘由。",
         mastery_criteria=["能说出日本的领土构成、首都与多火山地震的原因",
                           "能解释日本工业集中分布在太平洋沿岸和濑户内海沿岸的原因"],
         dq=("日本的工业主要集中分布在？",
             ["太平洋沿岸和濑户内海沿岸", "日本海沿岸", "北海道内陆", "四国岛南部"], "A"),
         std=[(Q_GJ_WZ, "geo-2022:4.NR.26", "exact", 305)],
         tags=["世界地理", "国家", "日本"], pre=["geo_p009"]),
    dict(id="geo_p037", name="东南亚", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第七章 我们邻近的地区和国家", type="conceptual",
         description="说明东南亚地处亚洲与大洋洲、太平洋与印度洋之间的十字路口位置，认识马六甲海峡的重要性、热带雨林与热带季风气候、水稻与热带经济作物生产，以及山河相间、城市沿河分布的特点。",
         mastery_criteria=["能在地图上指出东南亚的十字路口位置与马六甲海峡",
                           "能说明热带气候对当地农业生产与生活的影响"],
         dq=("马六甲海峡沟通的两大洋是？",
             ["太平洋与印度洋", "太平洋与大西洋", "印度洋与大西洋", "北冰洋与太平洋"], "A"),
         std=[(Q_DQ, "geo-2022:4.NR.27", "exact", 303)],
         tags=["世界地理", "地区", "东南亚"], pre=["geo_p009"]),
    dict(id="geo_p038", name="印度", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第七章 我们邻近的地区和国家", type="conceptual",
         description="认识印度作为南亚人口大国的位置与地形，理解热带季风气候下西南季风不稳定造成的水旱灾害，说明服务外包产业与绿色革命对经济发展的作用。",
         mastery_criteria=["能说明西南季风强弱与进退时间对印度降水的影响",
                           "能举例说明印度因地制宜发展农业与软件外包业的途径"],
         dq=("印度水旱灾害频繁的主要原因是？",
             ["西南季风强弱与进退时间不稳定", "地形以平原为主", "河流全部为内流河", "纬度位置过高"], "A"),
         std=[(Q_GJ_JJ, "geo-2022:4.NR.28", "exact", 311)],
         tags=["世界地理", "国家", "印度"], pre=["geo_p034"]),
    dict(id="geo_p039", name="俄罗斯", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第七章 我们邻近的地区和国家", type="conceptual",
         description="认识俄罗斯横跨亚欧两大洲的位置、以温带大陆性气候为主的气候与丰富的自然资源，说明其重工业发达、铁路运输为主的特点，以及人口和城市集中在欧洲部分的原因。",
         mastery_criteria=["能说出俄罗斯的领土构成、气候特点与主要自然资源",
                           "能分析俄罗斯人口、城市与工业分布的特点及成因"],
         dq=("俄罗斯的人口和城市主要集中在？",
             ["欧洲部分", "亚洲部分的北部", "西伯利亚中部", "远东地区"], "A"),
         std=[(Q_GJ_JY, "geo-2022:4.NR.29", "exact", 313)],
         tags=["世界地理", "国家", "俄罗斯"], pre=["geo_p034"]),
    dict(id="geo_p040", name="中东", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第八章 东半球其他的地区和国家", type="conceptual",
         description="认识中东地处三洲五海之地的位置，理解石油资源丰富而水资源匮乏、宗教文化差异显著对本区生产生活与地区局势的影响。",
         mastery_criteria=["能在地图上指出中东的位置、主要产油国与石油输出方向",
                           "能说明水资源匮乏与宗教文化差异对本区的影响"],
         dq=("中东地区储量最丰富、出口量最大的矿产资源是？",
             ["石油", "煤炭", "铁矿", "锡矿"], "A"),
         std=[(Q_DQZY, "geo-2022:4.NR.30", "exact", 304)],
         tags=["世界地理", "地区", "中东"], pre=["geo_p009"]),
    dict(id="geo_p041", name="欧洲西部", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第八章 东半球其他的地区和国家", type="conceptual",
         description="认识欧洲西部发达国家集中、温带海洋性气候广布的特点，理解气候对畜牧业与园艺业的影响，说明其旅游资源丰富、旅游业发达的条件。",
         mastery_criteria=["能说明温带海洋性气候对欧洲西部农业类型的影响",
                           "能结合实例说出欧洲西部发展旅游业的优势条件"],
         dq=("欧洲西部畜牧业发达的主要自然原因是？",
             ["温带海洋性气候温和湿润，适宜多汁牧草生长", "全年高温多雨", "地形以高原为主",
              "河流全部结冰期长"], "A"),
         std=[(Q_LY, "geo-2022:4.NR.31", "exact", 306)],
         tags=["世界地理", "地区", "欧洲西部"], pre=["geo_p013"]),
    dict(id="geo_p042", name="撒哈拉以南非洲", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第八章 东半球其他的地区和国家", type="conceptual",
         description="认识撒哈拉以南非洲以高原为主、热带草原气候广布的自然环境，理解人口增长过快、粮食短缺与单一商品经济形成的原因与出路。",
         mastery_criteria=["能说出撒哈拉以南非洲的地形与气候特点",
                           "能解释单一商品经济的主要特征与不利影响"],
         dq=("撒哈拉以南非洲许多国家出口初级产品、进口工业制成品，这种经济特征被称为？",
             ["单一商品经济", "进口替代经济", "知识经济", "循环经济"], "A"),
         std=[(Q_DQZY, "geo-2022:4.NR.30", "exact", 304)],
         tags=["世界地理", "地区", "非洲"], pre=["geo_p012"]),
    dict(id="geo_p043", name="澳大利亚", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第八章 东半球其他的地区和国家", type="conceptual",
         description="认识澳大利亚独占一块大陆的位置、特有古老生物众多的原因，说明其养羊业与采矿业发达、人口和城市集中在东南沿海的特点。",
         mastery_criteria=["能解释澳大利亚特有古老生物多的原因",
                           "能说明澳大利亚人口与城市分布的特点及自然原因"],
         dq=("澳大利亚特有古老生物较多的主要原因是？",
             ["大陆长期孤立，生物演化缓慢", "纬度跨度大", "地形以山地为主", "受季风影响显著"], "A"),
         std=[(Q_GJ_RW, "geo-2022:4.NR.32", "exact", 308)],
         tags=["世界地理", "国家", "澳大利亚"], pre=["geo_p009"]),
    dict(id="geo_p044", name="美国", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第九章 西半球的国家", type="conceptual",
         description="认识美国作为移民国家的人口构成、地形南北纵列三大区与专业化农业带，说明其工业与高新技术产业发达、人口集中在东北部与太平洋沿岸的特点。",
         mastery_criteria=["能在地图上指出美国的地形三大区与主要农业带",
                           "能说明美国农业地区生产专业化的形成条件"],
         dq=("美国农业生产最突出的特点是？",
             ["地区生产专业化，形成农业带", "全部依靠进口", "以水稻种植为主", "农场规模小而分散"], "A"),
         std=[(Q_GJ_JJ, "geo-2022:4.NR.28", "exact", 311)],
         tags=["世界地理", "国家", "美国"], pre=["geo_p018"]),
    dict(id="geo_p045", name="巴西", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第九章 西半球的国家", type="conceptual",
         description="认识巴西作为拉丁美洲面积最大国家的位置、亚马孙平原与热带雨林，说明人口和城市集中在东南沿海、铁矿与水能资源丰富、热带经济作物发达的特点。",
         mastery_criteria=["能说出巴西的位置、主要地形区与热带雨林的环境价值",
                           "能说明巴西人口与城市集中在东南沿海的原因"],
         dq=("巴西的人口和城市主要分布在？",
             ["东南沿海地区", "亚马孙平原中部", "巴西高原西部", "北部热带雨林深处"], "A"),
         std=[(Q_GJ_LX, "geo-2022:4.NR.33", "exact", 315)],
         tags=["世界地理", "国家", "巴西"], pre=["geo_p044"]),
    dict(id="geo_p046", name="极地地区", domain="世界地理", grade=7, semester="下",
         chapter="七年级下册 第十章 极地地区", type="conceptual",
         description="比较南极地区与北极地区在位置、地形、气候和生物方面的差异，说明极地科学考察的价值与保护极地环境的重要性，了解我国极地考察站的分布。",
         mastery_criteria=["能比较南极与北极地区自然环境的差异并说明成因",
                           "能举例说明极地科学考察的意义与极地环境保护的要求"],
         dq=("南极地区比北极地区更寒冷的主要原因是？",
             ["南极以大陆为主，冰雪覆盖、平均海拔高", "南极纬度更低", "南极受暖流影响", "北极四周是陆地"], "A"),
         std=[(Q_JD, "geo-2022:4.NR.34", "exact", 307)],
         tags=["世界地理", "极地"], pre=["geo_p009"]),
    # ---------- 八年级上册 第三章 补充 ----------
    dict(id="geo_p047", name="中国的土地资源", domain="中国地理", grade=8, semester="上",
         chapter="八年级上册 第三章 中国的自然资源", type="conceptual",
         description="认识我国土地资源类型齐全、总量大而人均少、耕地林地草地比重与分布差异，理解十分珍惜、合理利用土地和切实保护耕地的基本国策。",
         mastery_criteria=["能说出我国耕地、林地、草地的分布差异",
                           "能举例说明保护耕地的基本国策与具体做法"],
         dq=("我国土地资源的基本国情是？",
             ["类型齐全，但人均占有量少、耕地比重小", "耕地比重最大", "后备耕地资源充足", "土地利用类型单一"], "A"),
         std=[(Q_ZG_ZY, "geo-2022:4.NR.35", "exact", 336)],
         tags=["中国地理", "自然资源", "土地资源"], pre=["geo_p025"]),
    dict(id="geo_p048", name="中国的水资源", domain="中国地理", grade=8, semester="上",
         chapter="八年级上册 第三章 中国的自然资源", type="conceptual",
         description="认识我国水资源时间上夏秋多冬春少、空间上南丰北缺的分布特点，理解跨流域调水与节约用水对缓解水资源紧张的作用。",
         mastery_criteria=["能说出我国水资源时空分布不均的表现",
                           "能举例说明解决水资源不足的主要措施"],
         dq=("我国水资源空间分布的特点是？",
             ["南丰北缺，东多西少", "北丰南缺", "西多东少", "全国均衡"], "A"),
         std=[(Q_ZG_GX, "geo-2022:4.NR.36", "exact", 337)],
         tags=["中国地理", "自然资源", "水资源"], pre=["geo_p025"]),
    # ---------- 八年级下册 第十章 ----------
    dict(id="geo_p049", name="中国在世界中", domain="中国地理", grade=8, semester="下",
         chapter="八年级下册 第十章 中国在世界中", type="application",
         description="认识我国在世界经济、政治与文化发展中的地位与作用，理解共建“一带一路”与构建人类命运共同体的意义，树立开放包容的国际视野。",
         mastery_criteria=["能举例说明我国与世界其他国家在经济、技术、文化方面的联系",
                           "能说明区域联系与协同发展对我国和世界发展的意义"],
         dq=("我国提出共建“一带一路”倡议的主要意义是？",
             ["促进沿线国家互联互通与共同发展", "减少对外交流", "只向发达国家开放", "限制国际贸易"], "A"),
         std=[(Q_GJ_LX, "geo-2022:4.NR.33", "inferred", 315)],
         tags=["中国地理", "国际合作"], pre=["geo_p028"]),
    # ---------- 选择性必修2 第三章 / 第四章 ----------
    dict(id="geo_h053", name="大都市的辐射功能", domain="人文地理", grade=11, semester="下",
         chapter="选择性必修2 第三章 城市、产业与区域发展", type="conceptual",
         description="从区域空间组织的视角认识大都市通过产业转移、交通联通与要素流动对周边地区产生的辐射带动作用，说明都市圈与城市群的形成机制。",
         mastery_criteria=["能说明大都市辐射功能的主要表现与实现途径",
                           "能结合实例分析大都市对周边区域发展的带动作用"],
         dq=("大都市对周边地区的辐射功能主要通过哪些途径实现？",
             ["产业转移、交通联通与人才资金等要素流动", "行政命令限制人口流动", "减少对外交通联系",
              "只发展农业"], "A"),
         std=[(Q_H_DS, "geo-2017:G.NR.27", "exact", 0)],
         tags=["人文地理", "城市", "区域发展"], pre=["geo_h020"]),
    dict(id="geo_h054", name="地区产业结构变化", domain="人文地理", grade=11, semester="下",
         chapter="选择性必修2 第三章 城市、产业与区域发展", type="procedural",
         description="认识地区产业结构由第一产业为主向第二、第三产业为主演变的一般规律，分析资源禀赋、技术进步、政策与市场对产业结构变化的影响。",
         mastery_criteria=["能描述区域产业结构演变的一般规律",
                           "能结合实例分析产业结构变化的原因"],
         dq=("区域产业结构演变的一般规律是？",
             ["第一产业比重下降，第二、第三产业比重上升", "第一产业比重持续上升",
              "第二产业比重始终最高且不变", "三次产业比重保持不变"], "A"),
         std=[(Q_H_JG, "geo-2017:G.NR.28", "exact", 0)],
         tags=["人文地理", "产业", "区域发展"], pre=["geo_h023"]),
    dict(id="geo_h055", name="资源跨区域调配", domain="人文地理", grade=11, semester="下",
         chapter="选择性必修2 第四章 区际联系与区域协调发展", type="reasoning",
         description="理解资源跨区域调配的必然性与实现方式，结合西气东输、西电东送、南水北调等工程说明其对资源输出区、输入区及沿线地区发展的影响。",
         mastery_criteria=["能说明资源跨区域调配的原因与主要工程",
                           "能分析资源跨区域调配对输出区和输入区的不同影响"],
         dq=("我国西气东输工程对东部地区的主要影响是？",
             ["缓解能源紧张，改善能源结构", "增加东部煤炭开采", "减少东部人口", "降低东部交通需求"], "A"),
         std=[(Q_H_ZP, "geo-2017:G.NR.29", "exact", 0)],
         tags=["人文地理", "资源调配", "区域联系"], pre=["geo_h025"]),
]

topics = json.load(open(TP, encoding="utf-8"))
qs = json.load(open(QP, encoding="utf-8"))
deps = json.load(open(DP, encoding="utf-8"))
have = {t["id"] for t in topics}

# 课标 quote 校验（缺字即中止，绝不编造）
bad = [(q, "quote 未在课标原文命中") for q in ALL_Q if norm(q) not in SRC]
if bad:
    print("课标 quote 校验失败:", bad)
    sys.exit(1)
print(f"课标 quote 校验: {len(ALL_Q)}/{len(ALL_Q)} 命中")

# 题型细分关键词
PROC = re.compile(r"(计算|运算|换算|判读|测量|绘制|绘图|统计|读图|定位)")

n_t = n_q = n_e = 0
for spec in NEW:
    if spec["id"] in have:
        continue
    stds = [{"id": sid, "confidence": conf, "quote": q} for q, sid, conf, line in spec["std"]]
    for s, (q, sid, conf, line) in zip(stds, spec["std"]):
        if line:
            s["sourceLine"] = line
    t = {
        "id": spec["id"], "name": spec["name"], "subject": "geography", "domain": spec["domain"],
        "grade": spec["grade"], "semester": spec["semester"], "chapter": spec["chapter"],
        "type": spec["type"], "description": spec["description"],
        "mastery_criteria": spec["mastery_criteria"],
        "diagnostic_question": {"question": spec["dq"][0], "answer": spec["dq"][2]},
        "external": False, "standards": stds, "tags": spec["tags"],
        "prerequisites": spec["pre"], "curriculumRef": spec["std"][0][1], "verified": False,
    }
    topics.append(t)
    have.add(t["id"])
    n_t += 1
    # 诊断题（题库）
    labels = ["A", "B", "C", "D"]
    qid = ("geo_pq" if t["grade"] <= 9 else "geo_hq") + f"{len([x for x in qs if x['id'].startswith('geo_pq' if t['grade']<=9 else 'geo_hq')]) + 1:03d}"
    qs.append({"id": qid, "topicId": t["id"], "prompt": spec["dq"][0], "question": spec["dq"][0],
               "options": [{"label": l, "text": x} for l, x in zip(labels, spec["dq"][1])],
               "answer": spec["dq"][2], "type": "choice", "difficulty": "standard",
               "explanation": spec["description"]})
    n_q += 1
    for p in spec["pre"]:
        if (p, t["id"]) not in {(e["from"], e["to"]) for e in deps}:
            deps.append({"from": p, "to": t["id"], "type": "hard"})
            n_e += 1

print(f"新增知识点 {n_t} | 新增题 {n_q} | 新增边 {n_e} | 现规模 {len(topics)} 点 / {len(qs)} 题 / {len(deps)} 边")
print("册次:", {f"{g}{s}": sum(1 for t in topics if t["grade"] == g and t["semester"] == s)
               for g, s in sorted({(t["grade"], t["semester"]) for t in topics})})
if WRITE:
    json.dump(topics, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(qs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(deps, open(DP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("written")
