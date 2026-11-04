#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""苏教版高中化学桶（chemistry-sujiao）建库：_structure.json ＋ _desc/<册>.json → topics/deps/_skeleton。

与 chemistry-luke / chemistry-lujiao 同口径（同 build_chem_editions.build 的字段形状），
差异只在：结构来自教材目录 docx 抽取的 _structure.json，描述来自各册 _desc 工位产物。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-sujiao")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

POOL = json.load(open(os.path.join(ROOT, "data", "_chem_std_pool.json"), encoding="utf-8"))
import chem_std_map as std_map  # noqa: E402

BOOKMETA = {
    "必修第一册": (10, "上", "必修第一册",
                "9787549981311_普通高中教科书·化学_高一年级_必修第一册_江苏凤凰教育出版社_1787291666337.pdf"),
    "必修第二册": (10, "下", "必修第二册",
                "9787549981311_普通高中教科书·化学_高一年级_必修第二册_江苏凤凰教育出版社_1787291666337.pdf"),
    "选择性必修第一册": (11, "上", "选择性必修第一册",
                   "9787549981311_普通高中教科书·化学_高一年级_选择性必修第一册_江苏凤凰教育出版社_1787291666337.pdf"),
    "选择性必修第二册": (11, "下", "选择性必修第二册",
                   "9787549981311_普通高中教科书·化学_高一年级_选择性必修第二册_江苏凤凰教育出版社_1787291666337.pdf"),
    "选择性必修第三册": (12, "上", "选择性必修第三册",
                   "9787549981311_普通高中教科书·化学_高一年级_选择性必修第三册_江苏凤凰教育出版社_1787291666337.pdf"),
}
ORDER = list(BOOKMETA)
PREFIX = "csj"
SUBJECT = "chemistry-sujiao"


KW_STD = [
    (("氧化还原",), "氧化还原反应的本质"),
    (("离子反应", "电解质", "电离", "离子共存", "离子方程式"), "离子反应及其发生的条件"),
    (("元素周期", "原子结构", "元素性质", "核外电子", "递变"), "元素性质呈周期性变化"),
    (("化学键", "共价键", "离子键", "微粒间", "分子间作用力", "晶体", "杂化", "配合物"), "离子键和共价键的形成"),
    (("钠", "铁", "金属", "冶炼", "材料", "腐蚀"), "钠、铁及其重要化合物"),
    (("氯", "硫", "氮", "海水", "二氧化硫", "氨", "硝酸", "硫酸"), "氯、氮、硫及其重要化合物"),
    (("分类", "物质及其反应"), "物质进行分类"),
    (("速率", "平衡", "水解", "溶度积", "沉淀溶解", "酸碱", "pH"), "对常见的反应进行分析说明"),
]


def pick_std(name):
    keys = list(std_map.GAOZHONG.get(name, []))
    hits = []
    if not keys:
        for words, needle in KW_STD:
            if any(w in name for w in words):
                hits.append(needle)
    out, seen = [], set()
    for k in keys:
        for p in POOL:
            if k in p["quote"] and p["quote"] not in seen and p["id"].startswith("che-2017"):
                seen.add(p["quote"])
                out.append({"id": p["id"], "confidence": "partial", "quote": p["quote"],
                            "sourceLine": p["sourceLine"] if isinstance(p["sourceLine"], int) else 1})
                break
    for needle in hits:
        for p in POOL:
            if needle in p["quote"] and p["quote"] not in seen:
                seen.add(p["quote"])
                out.append({"id": p["id"], "confidence": "partial", "quote": p["quote"],
                            "sourceLine": p["sourceLine"] if isinstance(p["sourceLine"], int) else 1})
                break
    return out[:2]


def main(write=False):
    struct = json.load(open(os.path.join(D, "_structure.json"), encoding="utf-8"))
    descs = {}
    for b in ORDER:
        p = os.path.join(D, "_desc", "%s.json" % b)
        if not os.path.exists(p):
            print("❌ 缺描述文件 %s" % p)
            return 1
        descs[b] = json.load(open(p, encoding="utf-8"))

    topics, deps, skeleton = [], [], []
    uid = lid = 0
    prev = None
    for b in ORDER:
        grade, sem, unit_word, pdf = BOOKMETA[b]
        sk = {"book": b, "pdf": pdf, "grade": grade, "semester": sem, "units": []}
        dv = {u["no"]: u for u in descs[b]["units"]}
        for u in struct[b]:
            uid += 1
            unit_id = "%s_u%03d" % (PREFIX, uid)
            chapter = "%s 第%d专题 %s" % (b, u["no"], u["name"])
            du = dv[u["no"]]
            topics.append({
                "id": unit_id, "name": u["name"], "subject": SUBJECT, "domain": du["domain"],
                "grade": grade, "semester": sem, "chapter": chapter, "level": "unit",
                "type": "conceptual",
                "description": "%s本专题围绕「%s」组织，含 %d 个课题，覆盖%s的核心内容与方法。" % (
                    b + "，", u["name"], len(u["lessons"]), du["domain"]),
                "mastery_criteria": ["能说出「%s」的主线与本专题各课题之间的关系" % u["name"],
                                     "能综合运用本专题知识解决一个真实情境问题"],
                "tags": [du["domain"], u["name"]], "standards": [],
                "prerequisites": [], "root_reason": "专题上位点，不设先修",
            })
            sk["units"].append({"no": u["no"], "name": u["name"], "unitId": unit_id,
                                "lessons": list(u["lessons"])})
            dls = {l["name"]: l for l in du["lessons"]}
            for lname in u["lessons"]:
                lid += 1
                tid = "%s_j%03d" % (PREFIX, lid)
                dl = dls[lname]
                topics.append({
                    "id": tid, "name": lname, "subject": SUBJECT, "domain": du["domain"],
                    "grade": grade, "semester": sem,
                    "chapter": "%s · %s" % (chapter, lname), "level": "lesson",
                    "type": "conceptual", "description": dl["description"],
                    "mastery_criteria": [dl["c1"], dl["c2"]], "tags": [du["domain"], lname],
                    "standards": pick_std(lname),
                    "prerequisites": [prev] if prev else [],
                    "prereqUpper": [unit_id],
                })
                if prev:
                    deps.append({"from": prev, "to": tid, "type": "hard"})
                prev = tid
        skeleton.append(sk)
    for t in topics:
        if t["level"] == "lesson" and not t["prerequisites"]:
            t["root_reason"] = "本册第一节，作为本教材先修链起点"
    n_u = sum(1 for t in topics if t["level"] == "unit")
    n_l = sum(1 for t in topics if t["level"] == "lesson")
    st = sum(1 for t in topics if t["standards"])
    print("%s：单元 %d ＋ 课时 %d ＝ %d 点｜边 %d｜挂课标 %d（%.0f%%）" % (
        SUBJECT, n_u, n_l, len(topics), len(deps), st, 100.0 * st / len(topics)))
    if write:
        os.makedirs(D, exist_ok=True)
        json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(skeleton, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("已写入 topics/dependencies/_skeleton")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
