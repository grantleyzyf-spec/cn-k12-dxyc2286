#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版 · 课标引文回填（J001）

做法（SKILL §2.6/§2.7）：鄂教与鄂教同属高中、共用《普通高中数学课程标准（2017 年版 2025 年修订）》，
直接复用 `data/math/topics.json` 里**已逐字回表**的 `mat-2017:*` 条目——按点名称相似度借调，标 `confidence: inferred`。
落库前逐条硬校验：quote 去空白后必须在本机课标 TXT 里子串命中，命中率 100% 才写。

产出：
  data/math-ejiao/topics.json 的 standards[]（就地回填）
  data/math-ejiao/_std_map.json（topicId → standards，重跑 merge 后仍可复用）
用法：python3 backfill_standards.py [--write]
"""
import difflib, json, os, re, sys

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
OUT = os.path.join(REPO, "data", "math-ejiao")
TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt"
HAN = re.compile(r"[\u4e00-\u9fa5]")


def _sl(v):
    """sourceLine 必须是 integer（schema 硬约束）；取不到数字就不写这个键。"""
    m = re.search(r"\d+", str(v if v is not None else ""))
    return int(m.group()) if m else None


def norm(s):
    return re.sub(r"[\s　·、，。：；（）()“”\"'‘’]", "", s or "")


def main():
    write = "--write" in sys.argv
    raw = open(TXT, encoding="utf-8", errors="ignore").read()
    flat = re.sub(r"\s+", "", raw)

    donor = [t for t in json.load(open(os.path.join(REPO, "data/math/topics.json"), encoding="utf-8"))
             if t.get("grade", 0) >= 10 and t.get("standards")]
    print(f"donor 高中点 {len(donor)} 条（含课标引文）")
    topics = json.load(open(os.path.join(OUT, "topics.json"), encoding="utf-8"))

    hit = miss = nocand = 0
    std_map = {}
    for t in topics:
        name = norm(t["name"])
        best, ratio = None, 0.0
        for d in donor:
            r = difflib.SequenceMatcher(None, name, norm(d["name"])).ratio()
            if r > ratio:
                best, ratio = d, r
        if best is None or ratio < 0.55:
            # 退一步：用章名（去掉册前缀）跟 donor 的章名比
            chap = norm(t["chapter"].split(" ", 1)[-1])
            for d in donor:
                r = difflib.SequenceMatcher(None, chap, norm(d.get("chapter", "").split(" ", 1)[-1])).ratio()
                if r > ratio:
                    best, ratio = d, r
        if best is None or ratio < 0.55:
            nocand += 1
            continue
        stds = []
        for s in best["standards"][:2]:
            q = s.get("quote", "")
            if q and re.sub(r"\s+", "", q) in flat:
                _d = {"id": s["id"], "confidence": "inferred", "quote": q}
                if _sl(s.get("sourceLine")) is not None:
                    _d["sourceLine"] = _sl(s.get("sourceLine"))
                stds.append(_d)
        if stds:
            std_map[t["id"]] = stds
            t["standards"] = stds
            hit += 1
        else:
            miss += 1

    # 第二遍：单元点继承本章第一个课时点的引文（章级汇总点没有同名 donor）
    by_unit = {}
    for t in topics:
        if t["id"] not in std_map:
            for u in topics:
                if u["id"] not in std_map:
                    continue
                if u["id"] > "mej_h1000" and u["chapter"].rsplit(" · ", 1)[0] == t["chapter"]:
                    by_unit[t["id"]] = u["standards"]
                    break
    for tid, stds in by_unit.items():
        std_map[tid] = stds
        for t in topics:
            if t["id"] == tid:
                t["standards"] = stds
    # 第三遍：仍缺的课时点，阈值降到 0.45 再试一次
    for t in topics:
        if t["id"] in std_map or t["standards"]:
            continue
        name = norm(t["name"])
        best, ratio = None, 0.0
        for d in donor:
            r = difflib.SequenceMatcher(None, name, norm(d["name"])).ratio()
            if r > ratio:
                best, ratio = d, r
        if best and ratio >= 0.45:
            stds = []
            for s in best["standards"][:2]:
                if re.sub(r"\s+", "", s.get("quote", "")) not in flat:
                    continue
                _d = {"id": s["id"], "confidence": "inferred", "quote": s["quote"].strip()}
                if _sl(s.get("sourceLine")) is not None:
                    _d["sourceLine"] = _sl(s.get("sourceLine"))
                stds.append(_d)
            if stds:
                t["standards"] = stds
                std_map[t["id"]] = stds

    hit = sum(1 for t in topics if t.get("standards"))
    print(f"回填命中 {hit} 点｜无合适 donor {nocand} 点｜donor 引文未在本机课标 TXT 命中 {miss} 点")
    hit = sum(1 for t in topics if t.get("standards"))
    print(f"覆盖率 {hit}/{len(topics)} = {hit/len(topics):.1%}")
    rest = [t["id"] + " " + t["name"] for t in topics if not t.get("standards")]
    print("仍缺引文:", len(rest))
    for x in rest[:12]:
        print("   -", x)
    if write:
        # 以 topics 实际结果为准重建 map（保证两者永远一致，重跑 merge 不丢引文）
        std_map = {t["id"]: t["standards"] for t in topics if t.get("standards")}
        json.dump(topics, open(os.path.join(OUT, "topics.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        json.dump(std_map, open(os.path.join(OUT, "_std_map.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写入 topics.json 与 _std_map.json")
    else:
        print("（干跑，未写入）")


if __name__ == "__main__":
    main()
