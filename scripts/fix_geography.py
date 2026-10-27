#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理学科数据归一（幂等）。用法: python3 scripts/fix_geography.py [--write]
覆盖：难度别名 / 题干补全 / 三选项改填空 / 根节点 reason / 题型细分 /
      册次与章节口径纠偏 / 先修边双向镜像 / 重复边去重。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography")
tp, dp, qp = (os.path.join(D, f) for f in ("topics.json", "dependencies.json", "questions.json"))
WRITE = "--write" in sys.argv

topics = json.load(open(tp, encoding="utf-8"))
deps = json.load(open(dp, encoding="utf-8"))
qs = json.load(open(qp, encoding="utf-8"))

DIFF = {"medium": "standard", "easy": "basic"}
PROC = re.compile(r"(计算|运算|换算|判读|测量|绘制|绘图|统计|读图|定位)")
REAS = re.compile(r"(分析|解释|推断|比较|评价|成因)")

# 题干 <12 字 → 补上下文（逐题手写，不加机械前缀）
PROMPT_FIX = {
    "geo_pq002": "在地球仪上，赤道是哪一条特殊的纬线？",
    "geo_pq003": "本初子午线指的是地球上哪一条经线？",
    "geo_pq005": "地球绕地轴自转一周所需要的时间是？",
    "geo_pq012": "世界年降水量的分布规律是？",
    "geo_pq013": "地中海气候的气温和降水特征是？",
    "geo_pq017": "从世界范围看，发达国家主要分布在？",
    "geo_pq018": "我国领土的最东端位于下列哪个位置？",
    "geo_pq019": "我国人口分布的地理分界线是？",
    "geo_pq021": "我国地势的总体特征是？",
    "geo_pq023": "长江最终注入哪一个海？",
    "geo_pq031": "我国南方地区典型的天然植被是？",
    "geo_hq004": "恐龙繁盛的地质年代是？",
    "geo_hq013": "桂林山水属于下列哪一种地貌类型？",
    "geo_hq014": "野外观察地貌时合理的顺序是？",
    "geo_hq015": "下列植被类型中属于森林植被的是？",
    "geo_hq019": "环境承载力指的是？",
    "geo_hq024": "大型超市一般选择布局在？",
    "geo_hq032": "黄河最主要的补给水源是？",
    "geo_hq034": "喜马拉雅山脉的形成原因是？",
    "geo_hq036": "花岗岩按照成因属于哪一类岩石？",
    "geo_hq037": "下列各项中，不属于区域基本特征的是？",
    "geo_pq021": "我国地势的总体特征是怎样的？",
    "geo_pq023": "长江自西向东最终注入哪一个海？",
    "geo_hq004": "地质历史上恐龙繁盛的时代是？",
    "geo_hq019": "区域环境承载力指的是什么？",
    "geo_pq034": "亚洲与欧洲之间的分界线是？",
    "geo_pq035": "亚洲地势的总体特征是怎样的？",
}

# 册次 / 章节口径纠偏（人教 2012 版初中、人教 2019 版高中）
CH_FIX = {
    # 七上 第2—5章 被误标为七下
    ("七年级下册 第二章 陆地和海洋", 7, "下"): ("七年级上册 第二章 陆地和海洋", 7, "上"),
    ("七年级下册 第三章 天气与气候", 7, "下"): ("七年级上册 第三章 天气与气候", 7, "上"),
    ("七年级下册 第四章 居民与聚落", 7, "下"): ("七年级上册 第四章 居民与聚落", 7, "上"),
    ("七年级下册 第五章 发展与合作", 7, "下"): ("七年级上册 第五章 发展与合作", 7, "上"),
    # 八上 第四章 中国的经济发展 被误标为八下
    ("八年级下册 第四章 中国的经济发展", 8, "下"): ("八年级上册 第四章 中国的经济发展", 8, "上"),
    # 八下 第5—9章 现全部挂在「第五章」，按教材拆开
    ("八年级下册 第五章 中国的地理差异", 8, "下"): ("八年级下册 第五章 中国的地理差异", 8, "下"),
    # 选必1：章序与章名为「地表形态的演化 / 大气的运动 / 水的运动」
    ("选择性必修1 第二章 大气运动", 11, "上"): ("选择性必修1 第三章 大气的运动", 11, "上"),
    ("选择性必修1 第三章 水的运动", 11, "上"): ("选择性必修1 第四章 水的运动", 11, "上"),
    ("选择性必修1 第四章 地貌的演化", 11, "上"): ("选择性必修1 第二章 地表形态的演化", 11, "上"),
    # 选必2：第一章改为「区域与区域发展」，产业转移／区域协调发展归第四章
    ("选择性必修2 第一章 区域发展", 11, "下"): ("选择性必修2 第一章 区域与区域发展", 11, "下"),
    ("选择性必修2 第二章 资源、环境与区域发展", 11, "下"):
        ("选择性必修2 第二章 资源、环境与区域发展", 11, "下"),
}
# 八下 分区章（按主题归章）
CH_BY_TOPIC = {
    "geo_p030": "八年级下册 第六章 北方地区",
    "geo_p031": "八年级下册 第七章 南方地区",
    "geo_p032": "八年级下册 第八章 西北地区",
    "geo_p033": "八年级下册 第九章 青藏地区",
    "geo_h040": "选择性必修2 第四章 区际联系与区域协调发展",
    "geo_h043": "选择性必修2 第四章 区际联系与区域协调发展",
}

n_diff = n_prompt = n_choice = n_root = n_type = n_ch = 0

for q in qs:
    if q.get("difficulty") in DIFF:
        q["difficulty"] = DIFF[q["difficulty"]]
        n_diff += 1
    if q["id"] in PROMPT_FIX and len(q.get("prompt", "")) < 12:
        q["prompt"] = q["question"] = PROMPT_FIX[q["id"]]
        n_prompt += 1
    if q.get("type") == "choice" and len(q.get("options") or []) not in (4,):
        q["type"] = "fill"
        q["options"] = []
        n_choice += 1

for t in topics:
    key = (t.get("chapter"), int(t.get("grade") or 0), t.get("semester"))
    if key in CH_FIX:
        ch, g, sem = CH_FIX[key]
        if (t.get("chapter"), t.get("grade"), t.get("semester")) != (ch, g, sem):
            t["chapter"], t["grade"], t["semester"] = ch, g, sem
            n_ch += 1
    if t["id"] in CH_BY_TOPIC and t.get("chapter") != CH_BY_TOPIC[t["id"]]:
        t["chapter"] = CH_BY_TOPIC[t["id"]]
        n_ch += 1
    if not t.get("prerequisites") and not t.get("root_reason"):
        g = int(t.get("grade") or 0)
        band = "小学" if g <= 6 else ("初中" if g <= 9 else "高中")
        t["root_reason"] = (f"起始知识点：{(t.get('chapter') or '')[:24]} 为{band}阶段起始内容，"
                            "图谱内无更早前置（跨学段前置不单独连边）")
        n_root += 1
    if t.get("type") == "conceptual":
        nm = t.get("name", "")
        if PROC.search(nm):
            t["type"] = "procedural"; n_type += 1
        elif REAS.search(nm):
            t["type"] = "reasoning"; n_type += 1


# 领域分类（原文大批知识点 domain 误用「地球与宇宙」兜底）
DOMAIN_BY_ID = {}
for _i in range(1, 7):
    DOMAIN_BY_ID[f"geo_p{_i:03d}"] = "地球与宇宙"
for _i in range(7, 9):
    DOMAIN_BY_ID[f"geo_p{_i:03d}"] = "地图与地理工具"
for _i in range(9, 18):
    DOMAIN_BY_ID[f"geo_p{_i:03d}"] = "世界地理"
for _i in range(18, 34):
    DOMAIN_BY_ID[f"geo_p{_i:03d}"] = "中国地理"
for _i in range(34, 47):
    DOMAIN_BY_ID[f"geo_p{_i:03d}"] = "世界地理"
for _i in range(47, 50):
    DOMAIN_BY_ID[f"geo_p{_i:03d}"] = "中国地理"
for _i in range(1, 6):
    DOMAIN_BY_ID[f"geo_h{_i:03d}"] = "地球与宇宙"
for _i in range(28, 30):
    DOMAIN_BY_ID[f"geo_h{_i:03d}"] = "地球与宇宙"
for _i in list(range(6, 17)) + list(range(30, 38)):
    DOMAIN_BY_ID[f"geo_h{_i:03d}"] = "自然地理"
for _i in list(range(17, 28)) + list(range(38, 56)):
    DOMAIN_BY_ID[f"geo_h{_i:03d}"] = "人文地理"

n_domain = 0
for t in topics:
    want = DOMAIN_BY_ID.get(t["id"])
    if want and t.get("domain") != want:
        t["domain"] = want
        n_domain += 1

# ---- 先修边：去重 + 双向镜像 ----
seen, clean = set(), []
for e in deps:
    k = (e["from"], e["to"])
    if k in seen or e["from"] == e["to"]:
        continue
    seen.add(k)
    e["type"] = e.get("type") if e.get("type") in ("hard", "soft") else "hard"
    clean.append(e)
n_dedup = len(deps) - len(clean)
deps = clean

T = {t["id"]: t for t in topics}
# topics.prerequisites → deps 缺失补边
add_edges = 0
for t in topics:
    for p in t.get("prerequisites", []):
        if (p, t["id"]) not in seen and p in T:
            deps.append({"from": p, "to": t["id"], "type": "hard"})
            seen.add((p, t["id"]))
            add_edges += 1
# deps → topics.prerequisites 缺失补镜像
add_pre = 0
for e in deps:
    to = T.get(e["to"])
    if to is None:
        continue
    pre = to.setdefault("prerequisites", [])
    if e["from"] not in pre:
        pre.append(e["from"])
        add_pre += 1
# 边上的悬空端点检查
dangling = [(e["from"], e["to"]) for e in deps if e["from"] not in T or e["to"] not in T]

print(f"难度归一 {n_diff} | 题干补全 {n_prompt} | 选项不合规改填空 {n_choice} | "
      f"根节点补 reason {n_root} | 题型细分 {n_type} | 册次/章节纠偏 {n_ch} | 领域纠偏 {n_domain}")
print(f"重复边去重 {n_dedup} | 补边 {add_edges} | 补镜像 prerequisites {add_pre} | 悬空边 {len(dangling)}")
print("难度:", {k: sum(1 for q in qs if q.get("difficulty") == k) for k in ("basic", "standard", "hard")})
print("题型:", {k: sum(1 for t in topics if t.get("type") == k)
               for k in ("conceptual", "procedural", "reasoning", "modeling", "application")})
print("根节点:", sum(1 for t in topics if not t.get("prerequisites")),
      "| 无 root_reason:", sum(1 for t in topics if not t.get("prerequisites") and not t.get("root_reason")))
print("册次:", {f"{g}{s}": sum(1 for t in topics if t["grade"] == g and t["semester"] == s)
               for g, s in sorted({(t["grade"], t["semester"]) for t in topics})})

if WRITE:
    json.dump(qs, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(topics, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(deps, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("written:", tp, dp, qp)
