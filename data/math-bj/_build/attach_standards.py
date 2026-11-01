# -*- coding: utf-8 -*-
"""课标挂标：把人教版数学已核验的课标引文继承给北京版知识点（同义教数学课标、同一份 TXT）。

两轮：
  P1 名称强匹配（同「学段」才继承），confidence 沿用原值；
  P2 同学段同领域兜底（引该学段该领域最相关的一条课标条目，confidence=partial）。
两轮都命中不了的留 standards: []，记入缺口（不编造）。

用法: python3 attach_standards.py [--write]
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data")
STD_TXT = os.path.expanduser(
    "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt")


def seg_of(grade):
    return 1 if grade <= 2 else 2 if grade <= 4 else 3 if grade <= 6 else 4


def norm_name(s):
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = re.sub(r"[\s·、，,。;；:：\"'“”‘’]", "", s)
    return s


def main():
    write = "--write" in sys.argv
    sk = json.load(open(os.path.join(HERE, "_skeleton.json"), encoding="utf-8"))
    topics = sk["topics"]
    hum = json.load(open(os.path.join(D, "math", "topics.json"), encoding="utf-8"))

    # 人教版：名称 → 引文（只取同学段的）
    by_name = defaultdict(list)
    for t in hum:
        for s in t.get("standards") or []:
            if s.get("quote"):
                by_name[norm_name(t["name"])].append((seg_of(t["grade"]), s, t["name"]))
    # 学段 × 领域 的引文库（按 课标 id 去重）
    pool = defaultdict(dict)   # (seg, id_prefix_domain) -> {id: quote}
    for t in hum:
        for s in t.get("standards") or []:
            if not s.get("quote"):
                continue
            sid = s["id"]
            if not sid.startswith("mat-2022:"):
                continue
            seg = int(sid.split(":")[1].split(".")[0])
            pool[seg].setdefault(sid, (s["quote"], t.get("domain") or ""))

    std_txt = None
    if os.path.exists(STD_TXT):
        std_txt = re.sub(r"\s+", "", open(STD_TXT, encoding="utf-8", errors="ignore").read())

    stat = Counter()
    for t in topics:
        seg = seg_of(t["grade"])
        key = norm_name(t["name"])
        got = None
        # P1 名称强匹配
        for s_seg, s, hname in by_name.get(key, []):
            if s_seg == seg:
                got = dict(id=s["id"], confidence=s.get("confidence") or "exact", quote=s["quote"])
                if s.get("sourceLine") is not None:
                    got["sourceLine"] = s["sourceLine"]
                stat["p1"] += 1
                break
        # P2 已废弃：按字重叠兜底会静默错配（「整理与复习」被挂到「探索乘法和除法的算理」）。
        # 未命中的点留空，由题库分片工位在封闭候选集内挑选，父代逐条回表复核。
        if not got:
            stat["miss"] += 1
        # 回表不过的一律丢弃（宁可留空，不保留无法核验的引文）
        if got and std_txt and re.sub(r"\s+", "", got["quote"]) not in std_txt:
            stat["drop_unverified"] += 1
            got = None
        t["standards"] = [got] if got else []
        t["curriculumRef"] = got["id"] if got else None
    # 回表自检
    bad = []
    if std_txt:
        for t in topics:
            for s in t["standards"]:
                if re.sub(r"\s+", "", s["quote"]) not in std_txt:
                    bad.append((t["id"], s["quote"][:18]))
    print("P1 名称继承:", stat["p1"], "| P2 同段同领域兜底:", stat["p2"], "| 缺口:", stat["miss"])
    print("回表未命中:", len(bad), bad[:5])
    print("confidence:", Counter(s["confidence"] for t in topics for s in t["standards"]))
    print("无课标点:", [(t["book"], t["name"]) for t in topics if not t["standards"]][:10])
    if write:
        json.dump(sk, open(os.path.join(HERE, "_skeleton.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("写入 _skeleton.json")


if __name__ == "__main__":
    main()
