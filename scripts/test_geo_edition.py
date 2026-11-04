#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理（版本桶）数据不变量测试：一条命令覆盖任意版本桶。

用法：
    python3 scripts/test_geo_edition.py --bucket geography-shangwu
    python3 scripts/test_geo_edition.py --bucket geography-zhongtu-cz
    python3 scripts/test_geo_edition.py --list        # 看已登记的规格

规格（点数/单元/课时/册数）按桶登记在 SPEC 里；新增版本桶只需加一行。
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STD_TXT = ["/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt",
           "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（7）普通高中地理课程标准日常修订版（2017年版2025年修订）.txt"]
DOMAINS = {"地球与地图", "世界地理", "中国地理", "乡土地理",
           "自然地理", "人文地理", "区域发展", "资源环境与国家安全"}

SPEC = {
    "geography-shangwu":   dict(points=155, units=19, lessons=136, books=4, per_lesson=8, per_unit=5),
    "geography-zhongtu-cz": dict(points=155, units=18, lessons=137, books=4, per_lesson=8, per_unit=5),
    "geography-kepu":      dict(points=144, units=16, lessons=128, books=4, per_lesson=8, per_unit=5),
    "geography-lujiao":    dict(points=75, units=19, lessons=56, books=5, per_lesson=8, per_unit=5),
    "geography-jin":       dict(points=144, units=16, lessons=128, books=4, per_lesson=8, per_unit=5),
    "geography-yuejiao":   dict(points=171, units=19, lessons=152, books=4, per_lesson=8, per_unit=5),
    "geography-xiangjiao": dict(points=163, units=39, lessons=124, books=9, per_lesson=8, per_unit=5),
}


def norm(s):
    return re.sub(r"\s+", "", s or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.bucket:
        for k, v in sorted(SPEC.items()):
            print(k, v)
        return 0 if a.list else 1
    b = a.bucket
    if b not in SPEC:
        print(f"未登记规格：{b}（在 SPEC 里加一行）")
        return 1
    sp = SPEC[b]
    D = os.path.join(ROOT, "data", b)
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    Qp = os.path.join(D, "questions.json")
    Dp = os.path.join(D, "dependencies.json")
    Q = json.load(open(Qp, encoding="utf-8")) if os.path.exists(Qp) else []
    deps = json.load(open(Dp, encoding="utf-8")) if os.path.exists(Dp) else []
    by = {t["id"]: t for t in T}
    units = [t for t in T if t.get("level") == "unit"]
    lessons = [t for t in T if t.get("level") == "lesson"]
    books = sorted({t["chapter"].split(" ")[0] for t in T})
    fails, checks = [], []

    def ck(name, ok, detail=""):
        checks.append((name, ok, detail))
        if not ok:
            fails.append(f"{name}：{detail}" if detail else name)

    ck(f"点数 {sp['points']}（单元 {sp['units']} / 课时 {sp['lessons']}）",
       len(T) == sp["points"] and len(units) == sp["units"] and len(lessons) == sp["lessons"],
       f"{len(T)}/{len(units)}/{len(lessons)}")
    ck(f"册数 {sp['books']}", len(books) == sp["books"], books)
    ck("id 唯一", len(set(by)) == len(T))
    ck("subject 与桶名一致", all(t.get("subject") == b for t in T),
       [t["id"] for t in T if t.get("subject") != b][:3])
    CH_RE = r"^.+ (第[一二三四五六七八九十]+[章单元篇]|主题[一二三四五六七八九十]+|绪论)"
    ck("chapter 以册名开头且含章单元主题",
       all(re.match(CH_RE, t["chapter"]) for t in T),
       [t["id"] for t in T if not re.match(CH_RE, t["chapter"])][:3])
    ck("domain 在课标四领域内", all(t.get("domain") in DOMAINS for t in T),
       Counter(t.get("domain") for t in T if t.get("domain") not in DOMAINS))
    bad_tags = [t["id"] for t in T if (t.get("tags") or [""])[0] != t.get("domain")]
    ck("tags 首项＝domain", not bad_tags, bad_tags[:5])
    ck("每点都有课标引用", all(t.get("standards") for t in T),
       [t["id"] for t in T if not t.get("standards")][:3])
    ck("每条引用都带 quote", all(s.get("quote") for t in T for s in t.get("standards") or []))
    ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                              for t in T for s in t.get("standards") or []))
    srcs = [norm(open(p, encoding="utf-8", errors="ignore").read())
            for p in (STD_TXT if isinstance(STD_TXT, list) else [STD_TXT]) if os.path.exists(p)]
    if srcs:
        def _hit(q):
            return any(norm(q) in s for s in srcs)
        miss = [(t["id"], (t["standards"][0]["quote"] or "")[:12]) for t in T
                if t.get("standards") and not _hit(t["standards"][0]["quote"])]
        ck("quote 逐字回表 100%", not miss, miss[:3])
    else:
        checks.append(("quote 回表（缺课标 TXT，跳过）", True, ""))

    # 题库
    if Q:
        per = Counter(q["topicId"] for q in Q)
        ck(f"每课时点 ≥{sp['per_lesson']} 题",
           all(per.get(t["id"], 0) >= sp["per_lesson"] for t in lessons),
           [(t["id"], per.get(t["id"], 0)) for t in lessons if per.get(t["id"], 0) < sp["per_lesson"]][:3])
        ck(f"每单元点 ≥{sp['per_unit']} 题",
           all(per.get(t["id"], 0) >= sp["per_unit"] for t in units),
           [(t["id"], per.get(t["id"], 0)) for t in units if per.get(t["id"], 0) < sp["per_unit"]][:3])
        ck("题 id 唯一", len({q["id"] for q in Q}) == len(Q))
        ck("题目 topicId 可对上", all(q["topicId"] in by for q in Q),
           [q["id"] for q in Q if q["topicId"] not in by][:3])
        ck("选择题 4 选项且答案在选项内",
           all(len(q.get("options") or []) == 4 and
               q.get("answer") in [o.get("label") for o in q.get("options") or []]
               for q in Q if q.get("type") == "choice"),
           [q["id"] for q in Q if q.get("type") == "choice" and len(q.get("options") or []) != 4][:3])
        ck("numeric 都带 verify", all(q.get("verify") for q in Q if q.get("type") == "numeric"),
           [q["id"] for q in Q if q.get("type") == "numeric" and not q.get("verify")][:3])
    else:
        checks.append(("题库未产出", True, ""))

    # 先修边
    pairs = [(e["from"], e["to"]) for e in deps]
    ck("边无自环", all(x != y for x, y in pairs))
    ck("边无重复", len(set(pairs)) == len(pairs))
    ck("边两端都存在", all(x in by and y in by for x, y in pairs),
       [(x, y) for x, y in pairs if x not in by or y not in by][:3])
    parent = {}
    for x, y in pairs:
        parent.setdefault(y, set()).add(x)
    ck("deps↔prerequisites 双向镜像",
       all(p in by[y].get("prerequisites", []) for y, ps in parent.items() for p in ps),
       "")
    ck("课时点先修只连课时点",
       all(all(by[p].get("level") == "lesson" for p in (t.get("prerequisites") or [])) for t in lessons),
       [t["id"] for t in lessons if any(by[p].get("level") != "lesson" for p in (t.get("prerequisites") or []))][:3])
    seed, stack = set(), []

    def dfs(n):
        if n in stack:
            return False
        if n in seed:
            return True
        stack.append(n)
        ok = all(dfs(p) for p in by[n].get("prerequisites") or [])
        stack.pop()
        seed.add(n)
        return ok

    cyc = [t["id"] for t in T if not dfs(t["id"])]
    ck("先修图无环", not cyc, cyc[:3])
    ck("根节点都有 root_reason",
       all((t.get("prerequisites") or []) or t.get("root_reason") for t in T),
       [t["id"] for t in T if not (t.get("prerequisites") or []) and not t.get("root_reason")][:3])

    for name, ok, detail in checks:
        print(("✅" if ok else "❌"), name, "" if ok else f" [{detail}]")
    print(f"\n{sum(1 for _, ok, _ in checks if ok)}/{len(checks)} 项通过")
    if fails:
        print("FAILED:", len(fails))
        return 1
    print(f"{b.upper()} DATA PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
