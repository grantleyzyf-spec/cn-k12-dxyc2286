#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科技版高中化学（chemistry-hukeji）：_struct/*.json → topics / dependencies / _skeleton

- 19 章（unit 点）+ 62 节（lesson 点）
- 课标引文逐字取自《普通高中化学课程标准（2017年版2025年修订）》TXT，按节名关键词给每条 2 条
- 已成库的 (id, quote) 沿用原 id；新课标句续编 che-2017:G.NR.74 起
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-hukeji")
STD_TXT = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
           "（9）普通高中化学课程标准日常修订版（2017年版2025年修订）.txt")
ORDER = ["必修第一册", "必修第二册", "选择性必修第一册", "选择性必修第二册", "选择性必修第三册"]

# 节名关键词 → 课标句里的检索词（宁缺毋滥：命中 1 个即算）
SYN = {
    "物质的分类": ["物质进行分类", "分类方法"],
    "物质的量": ["物质的量", "摩尔"],
    "实验方法": ["化学实验", "实验"],
    "海水中的氯": ["氯", "卤素"],
    "氧化还原": ["氧化还原"],
    "离子反应": ["离子反应"],
    "溴和碘": ["卤素", "溴", "碘"],
    "硫": ["硫"],
    "氮": ["氮"],
    "硫循环": ["硫", "环境"],
    "元素周期表": ["元素周期", "周期律"],
    "原子结构": ["原子结构"],
    "核外电子": ["核外电子", "电子排布"],
    "化学键": ["化学键", "共价键", "离子键"],
    "海洋中的卤素资源": ["氯", "海水", "卤素"],
    "硫、氮及其循环": ["硫", "氮"],
    "常见的有机化合物": ["有机化合物"],
    "溴和碘": ["溴", "碘", "海水"],
    "氮": ["氮"],
    "硫循环": ["硫", "氮"],
    "金属": ["金属", "钠", "铁", "铝"],
    "金属化合物": ["金属", "化合物"],
    "能量变化": ["能量", "反应热"],
    "化学反应速率": ["反应速率"],
    "化学平衡": ["化学平衡", "平衡"],
    "化工生产": ["化工", "生产"],
    "饱和烃": ["烷烃", "烃"],
    "不饱和烃": ["烯烃", "炔烃", "烃"],
    "乙醇": ["乙醇", "乙酸"],
    "烃和卤代烃": ["烃", "卤代烃"],
    "烃的含氧衍生物": ["醇", "醛", "羧酸"],
    "羧酸及其衍生物": ["羧酸", "酯"],
    "糖": ["糖类", "油脂", "蛋白质"],
    "热效应": ["反应热", "焓变"],
    "反应热": ["反应热", "焓变"],
    "燃料": ["燃料", "能源"],
    "方向": ["反应方向", "自发"],
    "限度": ["化学平衡", "限度"],
    "速率": ["反应速率"],
    "合成氨": ["合成氨", "工业"],
    "水的电离": ["电离平衡", "水的电离", "pH"],
    "弱电解质": ["电离平衡", "弱电解质"],
    "盐类水解": ["盐类水解", "中和"],
    "沉淀溶解": ["沉淀溶解", "溶度积"],
    "电化学": ["电化学", "原电池", "电解"],
    "原电池": ["原电池", "化学电源"],
    "电解池": ["电解"],
    "腐蚀": ["腐蚀", "防护"],
    "氢原子": ["原子结构", "原子轨道"],
    "电子排布": ["电子排布", "核外电子"],
    "元素周期律": ["元素周期律", "电离能", "电负性"],
    "空间结构": ["空间结构", "杂化"],
    "分子结构": ["分子结构", "分子间作用力"],
    "配位": ["配位", "超分子"],
    "金属晶体": ["晶体", "金属"],
    "离子晶体": ["离子晶体", "晶体"],
    "共价晶体": ["共价晶体", "分子晶体"],
    "有机化学": ["有机化合物", "有机化学"],
    "有机化合物": ["有机化合物"],
    "命名": ["命名", "同分异构"],
    "脂肪烃": ["烷烃", "烯烃", "脂肪烃"],
    "芳香烃": ["芳香烃", "苯"],
    "卤代烃": ["卤代烃"],
    "醇和酚": ["醇", "酚"],
    "醛和酮": ["醛", "酮"],
    "羧酸": ["羧酸", "酯"],
    "生物大分子": ["糖类", "蛋白质", "核酸"],
    "合成高分子": ["高分子", "合成"],
    "有机合成": ["有机合成", "合成路线"],
    "研究有机": ["有机化合物", "结构测定"],
}


TXT_ALL = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt",
    STD_TXT,
]


def raw_src():
    out = []
    for p in TXT_ALL:
        if os.path.exists(p):
            out.append(open(p, encoding="utf-8", errors="ignore").read())
    return re.sub(r"\s+", "", "".join(out))


def load_pool():
    src = open(STD_TXT, encoding="utf-8", errors="ignore").read()
    src = re.sub(r"={5,}.*?={5,}", "\n", src, flags=re.S)
    src = re.sub(r"第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", "\n", src)
    flat = re.sub(r"\s+", "", src)
    sents = [s for s in re.split(r"[。；]", flat) if 14 <= len(s) <= 130]
    return flat, sents


def existing_map():
    """已成库的 quote → id（复用 id，避免同一句话出现两个编号）。"""
    out = {}
    p = os.path.join(ROOT, "data", "cn-curriculum-standards.json")
    try:
        agg = json.load(open(p, encoding="utf-8"))["subjects"]["chemistry"]
    except Exception:
        return out
    for g in ("geography", "chemistry", "chemistry-luke", "chemistry-lujiao"):
        pass
    for b in ("chemistry", "chemistry-luke", "chemistry-lujiao"):
        tp = os.path.join(ROOT, "data", b, "topics.json")
        if not os.path.exists(tp):
            continue
        for t in json.load(open(tp, encoding="utf-8")):
            for s in t.get("standards") or []:
                out.setdefault(s["quote"], s["id"])
    return out


def main():
    flat, sents = load_pool()
    RAW = raw_src()
    known = existing_map()
    mint = 74
    structs = []
    for b in ORDER:
        p = os.path.join(D, "_struct", f"{b}.json")
        assert os.path.exists(p), p
        structs.append(json.load(open(p, encoding="utf-8")))

    def pick(name):
        keys = SYN.get(name) or [name[:4]]
        scored = []
        for s in sents:
            if re.sub(r"\s+", "", s) not in RAW:
                continue
            n = sum(1 for k in keys if k in s)
            if n:
                scored.append((n, -len(s), s))
        scored.sort(reverse=True)
        out, seen = [], set()
        for _, _, s in scored:
            if s in seen:
                continue
            seen.add(s)
            sid = known.get(s)
            if not sid:
                nonlocal mint
                sid = f"che-2017:G.NR.{mint:02d}"
                mint += 1
                known[s] = sid
            out.append({"id": sid, "confidence": "partial", "quote": s, "sourceLine": 1})
            if len(out) >= 2:
                break
        return out

    topics, deps, skeleton = [], [], []
    uid = lid = 0
    prev = None
    for st in structs:
        book, grade, sem = st["book"], st["grade"], st["semester"]
        sk = {"book": book, "grade": grade, "semester": sem, "units": []}
        for ch in st["chapters"]:
            uid += 1
            unit_id = f"chk_u{uid:03d}"
            chap = f"{book} 第{ch['no']}章 {ch['name']}"
            secs = ch["sections"]
            topics.append({
                "id": unit_id, "name": ch["name"], "subject": "chemistry-hukeji", "domain": ch["domain"],
                "grade": grade, "semester": sem, "chapter": chap, "level": "unit", "type": "conceptual",
                "description": f"本章「{ch['name']}」含 {len(secs)} 节，围绕{ch['domain']}的主干概念、实验与定量关系组织，形成可迁移的化学思维。",
                "mastery_criteria": [f"能说出「{ch['name']}」的主干概念与核心反应",
                                     f"能综合运用本章知识解释或解决一个真实化学问题"],
                "tags": [ch["domain"], ch["name"]], "standards": pick(ch["name"]), "prerequisites": [],
                "root_reason": "章上位点，不设先修", "curriculumRef": "", "verified": False,
            })
            topics[-1]["curriculumRef"] = (topics[-1]["standards"] or [{"id": ""}])[0]["id"]
            chap_std = topics[-1]["standards"]
            sk["units"].append({"no": ch["no"], "name": ch["name"], "unitId": unit_id,
                                "lessons": [s["name"] for s in secs]})
            for sec in secs:
                lid += 1
                tid = f"chk_j{lid:03d}"
                topics.append({
                    "id": tid, "name": sec["name"], "subject": "chemistry-hukeji", "domain": ch["domain"],
                    "grade": grade, "semester": sem, "chapter": f"{chap} · {sec['name']}",
                    "level": "lesson", "type": "conceptual",
                    "description": sec["description"], "mastery_criteria": sec["mastery_criteria"],
                    "tags": [ch["domain"], sec["name"]], "standards": pick(sec["name"]) or chap_std,
                    "prerequisites": [prev] if prev else [], "prereqUpper": [unit_id],
                    "root_reason": "" if prev else "全册第一节，作为先修链起点",
                    "curriculumRef": "", "verified": False,
                })
                topics[-1]["curriculumRef"] = (topics[-1]["standards"] or [{"id": ""}])[0]["id"]
                if prev:
                    deps.append({"from": prev, "to": tid, "type": "hard"})
                prev = tid
        skeleton.append(sk)

    json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(skeleton, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    st = sum(1 for t in topics if t["standards"])
    print(f"点 {len(topics)}（章 {sum(1 for t in topics if t['level']=='unit')}、节 "
          f"{sum(1 for t in topics if t['level']=='lesson')}）｜边 {len(deps)}｜挂标 {st}/{len(topics)}")
    miss = [t["id"] + t["name"] for t in topics if not t["standards"]]
    if miss:
        print("未挂标：", miss[:8])


if __name__ == "__main__":
    main()
