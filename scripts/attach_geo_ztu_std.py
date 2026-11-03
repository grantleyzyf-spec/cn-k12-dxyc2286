#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）地理：给 144 个点挂《义务教育地理课程标准（2022 年版 2025 年修订）》条目。

做法（SKILL §7.4「封闭候选 ＋ 父代直判」的自动化版）：
1. 候选池**只取仓库内已回表的 (id, quote) 对**（来自 `data/geography` 与 `data/geography-xiangjiao`
   的 `standards`），并再次逐字回表到义教地理课标 TXT —— 不过池不许用，⛔ 不许现造 id 或改写 quote。
2. 打分：点文本（课时名 ＋ 主题名 ＋ description 前 60 字）与 quote 的 2-gram 重叠率 ＋ 关键词加成。
3. 三档 confidence：命中 ≥2 个实词且分数 ≥0.30 → exact；≥0.15 → partial；否则 inferred
   （inferred 也要挂，取**本主题单元点**的同一条，语义仍属本单元）。
4. 落盘后 `test_geo_ztu.py` 的「quote 逐字回表 100%」是唯一验收。

跨版本借标必须登记：写 `data/_std_waivers.json`（幂等合并，键＝桶名）。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")
STD_TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt"
WAIVER = os.path.join(ROOT, "data", "_std_waivers.json")
BUCKET = "geography-zhongtu-cz"
SRC_BUCKETS = ["geography", "geography-xiangjiao"]

# 主题关键词 → 加成（地理课标条目本身较短，靠关键词把「同一领域」拉得更近）
KEY = {
    "地球": ["地球", "经线", "纬线", "半球", "地球仪", "赤道"],
    "宇宙": ["宇宙", "太阳", "星系", "天体", "月球"],
    "地图": ["地图", "比例尺", "等高线", "方向", "图例"],
    "海陆": ["海陆", "大洲", "大洋", "板块", "火山", "地震"],
    "气候": ["气候", "气温", "降水", "天气", "季节"],
    "人口": ["人口", "人种", "语言", "宗教", "民族", "聚落", "城市"],
    "中国": ["中国", "疆域", "行政区划", "地形", "河流", "黄河", "长江"],
    "资源": ["资源", "土地", "水", "矿产", "耕地"],
    "产业": ["农业", "工业", "交通", "运输", "产业"],
    "区域": ["区域", "差异", "联系", "合作", "发展"],
    "家乡": ["家乡", "乡土地理", "调查"],
    "国家": ["国家", "日本", "美国", "巴西", "澳大利亚", "地区"],
}


def norm(s):
    return re.sub(r"\s+", "", s or "")


def grams(s):
    s = norm(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def build_pool(src_norm):
    pool = {}
    for b in SRC_BUCKETS:
        p = os.path.join(ROOT, "data", b, "topics.json")
        if not os.path.exists(p):
            continue
        for t in json.load(open(p, encoding="utf-8")):
            for s in t.get("standards") or []:
                q = s.get("quote") or ""
                if q and norm(q) in src_norm:
                    pool[s["id"]] = q
    return pool


def main() -> int:
    if not os.path.exists(STD_TXT):
        print(f"❌ 找不到课标 TXT：{STD_TXT}")
        return 1
    src_norm = norm(open(STD_TXT, encoding="utf-8", errors="ignore").read())
    pool = build_pool(src_norm)
    if len(pool) < 20:
        print(f"❌ 候选池只有 {len(pool)} 条，过少，先核 geography 桶的 standards")
        return 1
    print(f"候选池：{len(pool)} 条（全部逐字回表通过）")

    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    gcache = {k: grams(q) for k, q in pool.items()}
    by_unit = {}

    def pick(text, unit_key):
        tg = grams(text)
        bonus_terms = [w for ws in KEY.values() for w in ws if w in text]
        best = (0.0, None)
        for sid, q in pool.items():
            qg = gcache[sid]
            if not tg or not qg:
                continue
            inter = len(tg & qg)
            sc = inter / max(1, min(len(tg), len(qg)))
            sc += 0.03 * sum(1 for w in bonus_terms if w in q)
            if sc > best[0]:
                best = (sc, sid)
        score, sid = best
        if sid is None:
            return None, 0.0
        if score >= 0.30:
            conf = "exact"
        elif score >= 0.15:
            conf = "partial"
        else:
            conf = "inferred"
            # inferred 时退到本主题单元点已选的那条，保证同单元口径一致
            if unit_key in by_unit:
                sid = by_unit[unit_key]
            else:
                by_unit[unit_key] = sid
        return sid, score

    for t in topics:
        unit_key = t.get("prereqUpper") or t["id"]
        text = f"{t.get('name','')}{t['chapter']}{t.get('description','')[:60]}"
        sid, score = pick(text, unit_key)
        if sid is None:
            print(f"❌ {t['id']} 没有可用候选")
            return 1
        conf = "exact" if score >= 0.30 and sid in pool else ("partial" if score >= 0.15 else "inferred")
        t["standards"] = [{"id": sid, "quote": pool[sid], "confidence": conf,
                           "source": "义务教育地理课程标准（2022年版2025年修订）",
                           "borrowed_from": "跨版本借标（同一课标）"}]
        t["curriculumRef"] = sid

    from collections import Counter
    c = Counter(t["standards"][0]["confidence"] for t in topics)
    print(f"挂标完成：{len(topics)} 点 · 置信度 {dict(c)} · 用到条目 {len({t['curriculumRef'] for t in topics})} 条")

    # 逐字回表自检
    bad = [t["id"] for t in topics if norm(t["standards"][0]["quote"]) not in src_norm]
    if bad:
        print(f"❌ 回表失败 {len(bad)}：{bad[:5]}")
        return 1
    print("✅ quote 逐字回表 100%")

    tmp = os.path.join(D, "topics.json.tmp")
    json.dump(topics, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(D, "topics.json"))

    # 借标台账（幂等）
    led = json.load(open(WAIVER, encoding="utf-8")) if os.path.exists(WAIVER) else {}
    led[BUCKET] = {
        "borrowed_from": SRC_BUCKETS,
        "standard": "义务教育地理课程标准（2022年版2025年修订）",
        "reason": "中图版（钟作慈）初中地理教材按 2022 课标编写，课标条目与教材版本无关，直接沿用同一课标条目",
        "points": len(topics),
        "confidence": dict(c),
    }
    json.dump(led, open(WAIVER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"借标台账已写：{WAIVER}（键 {BUCKET}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
