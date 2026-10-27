# -*- coding: utf-8 -*-
"""信息科技学科数据归一（幂等）。用法: python3 scripts/fix_it.py [--write]"""
import json, os, re, sys

WRITE = "--write" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
S = "information-technology"
tp, qp, dp = f"{D}/{S}/topics.json", f"{D}/{S}/questions.json", f"{D}/{S}/dependencies.json"
topics = json.load(open(tp, encoding="utf-8"))
qs = json.load(open(qp, encoding="utf-8"))
deps = json.load(open(dp, encoding="utf-8"))

TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/9.《义务教育信息科技课程标准·日常修订版》(2022年版2025年修订).txt"
norm = lambda s: re.sub(r"\s+", "", s or "")
src = norm(open(TXT, encoding="utf-8", errors="ignore").read()) if os.path.exists(TXT) else ""

DIFF = {"medium": "standard", "easy": "basic"}
PROC = re.compile(r"(编程|编写程序|程序实现|算法实现|编码实现)")

PROMPT_FIX = {
    "it_q001": "在日常生活中，下列哪一项不属于信息？",
    "it_q009": "与本地硬盘相比，云存储最大的优点是什么？",
    "it_q024": "从安全强度看，下列四个密码中最安全的是哪一个？",
    "it_q029": "下列软件中，哪一个不属于操作系统？",
}

n_diff = n_prompt = n_type = n_root = n_conf = n_empty = 0
for q in qs:
    if q.get("difficulty") in DIFF:
        q["difficulty"] = DIFF[q["difficulty"]]
        n_diff += 1
    if q["id"] in PROMPT_FIX:
        q["prompt"] = q["question"] = PROMPT_FIX[q["id"]]
        n_prompt += 1

for t in topics:
    if t["id"] == "it_p027":          # 计算机系统组成：义教2022课标无对应条目
        t["standards"], t["curriculumRef"] = [], ""
        n_empty += 1
    if t["id"] == "it_p033":          # 数据库基础：属高中选必3范畴，义教无条目
        t["standards"], t["curriculumRef"] = [], ""
        n_empty += 1
    for s in t.get("standards", []):
        q = s.get("quote", "")
        if src and q and norm(q) in src:
            if s.get("confidence") != "exact":
                s["confidence"] = "exact"
                n_conf += 1
        else:
            s["confidence"] = "partial"
    if not t.get("prerequisites") and not t.get("root_reason"):
        g = int(t.get("grade") or 3)
        t["root_reason"] = ("起始知识点：%s 为%s阶段起始内容，图谱内无更早前置（跨学段前置不单独连边）"
                            % ((t.get("chapter") or "")[:24], "小学" if g <= 6 else "初中"))
        n_root += 1
    if t.get("type") == "conceptual" and PROC.search(t.get("name", "")):
        t["type"] = "procedural"
        n_type += 1
    if t.get("standards"):
        t["curriculumRef"] = t["standards"][0]["id"]

# 边与 prerequisites 双向镜像（只补 topics 侧，soft 边同为前置）
T = {t["id"]: t for t in topics}
n_mirror = 0
for e in deps:
    b = T.get(e["to"])
    if b is not None and e["from"] not in b.get("prerequisites", []):
        b.setdefault("prerequisites", []).append(e["from"])
        n_mirror += 1
# 去重复边
seen, dedup = set(), []
for e in deps:
    k = (e["from"], e["to"])
    if k in seen:
        continue
    seen.add(k)
    dedup.append(e)
n_dup = len(deps) - len(dedup)
deps = dedup

print(f"难度归一 {n_diff} | 题干补全 {n_prompt} | 课标清空 {n_empty} | confidence 升 exact {n_conf} "
      f"| 根节点 reason {n_root} | 题型细分 {n_type} | 补前置 {n_mirror} | 去重边 {n_dup}")
print("难度:", {k: sum(1 for q in qs if q.get("difficulty") == k) for k in ("basic", "standard", "hard")})
print("题型:", {k: sum(1 for t in topics if t.get("type") == k) for k in ("conceptual", "procedural", "reasoning")})
print("无 standards:", [t["id"] for t in topics if not t.get("standards")])
print("根节点无 reason:", [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")])

if WRITE:
    json.dump(qs, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(topics, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(deps, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written:", tp, qp, dp)
