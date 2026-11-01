#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""politics 结构体检（只读）：目录点／重复点／框号错乱／册次与领域分布／占位字段。

用法：python3 scripts/ddfz_audit.py [--json out.json]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(REPO, "data", "politics")
NUM = "一二三四五六七八九十"


def cn2int(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + NUM.index(s[1]) + 1
    if "十" in s:
        a, b = s.split("十")
        return (NUM.index(a) + 1) * 10 + (NUM.index(b) + 1 if b else 0)
    return NUM.index(s) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    T = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))

    toc = [p for p in T if p["name"].strip() in ("目录", "目 录")]
    dup = []
    seen = defaultdict(list)
    for p in T:
        unit = re.sub(r"第[%s\d]+框\s*" % NUM, "", p["chapter"])
        seen[(unit, p["name"])].append(p["id"])
    for k, v in seen.items():
        if len(v) > 1:
            dup.append({"chapter": k[0], "name": k[1], "ids": v})

    # 框号：同一单元内「第N框」是否连续、是否重号（框号写在 chapter 尾部，name 里没有）
    box = defaultdict(list)
    for p in T:
        m = re.search(r"第([%s\d]+)框\s*" % NUM, p["chapter"])
        if m and p.get("level") == "lesson":
            unit = p["chapter"][:m.start()].strip()
            box[(p["chapter"].split(" ")[0], unit)].append(
                (cn2int(m.group(1)), p["id"], p["chapter"]))
    box_bad = []
    for k, v in box.items():
        nums = [x[0] for x in v]
        if len(set(nums)) != len(nums) or nums != sorted(nums) or (nums and nums[0] != 1):
            box_bad.append({"unit": k[1], "seq": nums, "ids": [x[1] for x in v]})

    # 占位字段
    tmpl_desc = sum(1 for p in T if p["description"] == p["name"])
    tmpl_mastery = sum(1 for p in T if p.get("mastery_criteria") and
                       p["mastery_criteria"][0].startswith("能说出「"))
    tmpl_diag = sum(1 for p in T if (p.get("diagnostic_question") or {}).get("question", "").startswith("关于「"))
    books = Counter(p["chapter"].split(" ")[0] for p in T)
    stage = Counter((p["stage"] if "stage" in p else "", p["grade"]) for p in T)
    domain = Counter(p["domain"] for p in T)

    rep = {
        "points": len(T),
        "level": dict(Counter(p["level"] for p in T)),
        "books": dict(books),
        "book_count": len(books),
        "domain": dict(domain),
        "toc_points": [p["id"] for p in toc],
        "dup_points": dup,
        "box_numbering": box_bad,
        "placeholder": {"description_eq_name": tmpl_desc,
                        "mastery_template": tmpl_mastery,
                        "diag_template": tmpl_diag},
        "standards": dict(Counter(s["confidence"] for p in T for s in p["standards"])),
        "citations": sum(len(p["standards"]) for p in T),
        "cited_entries": len({s["id"] for p in T for s in p["standards"]}),
    }
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if a.json:
        json.dump(rep, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
