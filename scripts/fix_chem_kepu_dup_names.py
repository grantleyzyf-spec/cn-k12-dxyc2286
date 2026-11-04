#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只给**重名课时**补全名（消歧），其余课时名保持不变 —— 最小改动，避免已派单的学层/题库失配。

重名来源：首版抽取把「单元整理与提升——xxx」截成「单元整理与提升」，多单元撞名。
做法：同名课时改用 docx 原文全名（含破折号后的限定语），其余一字不动。
同步：topics.json / _skeleton.json / dependencies.json（chapter 尾段随 name 更新）。
"""
import json
import re
from collections import Counter

D = "data/chemistry-kepu"
UNITS = "/tmp/chem_kepu_units.json"


def main():
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    units = json.load(open(UNITS, encoding="utf-8"))

    # (册, 单元名, 课时序号) → 全名
    full = {}
    for u in units:
        for l in u["lessons"]:
            full[(u["book"], u["unitName"], l["no"])] = l["name"]

    les = [t for t in topics if t["level"] == "lesson"]
    cnt = Counter(t["name"] for t in les)
    dups = {n for n, c in cnt.items() if c > 1}

    changed = []
    for t in les:
        if t["name"] not in dups:
            continue
        m = re.match(r"^(.+?) 第(\d+)单元 (.+?) · (.+)$", t["chapter"])
        if not m:
            continue
        book, _, uname, old = m.group(1), m.group(2), m.group(3), m.group(4)
        # 课时序号需按同单元内顺序推出
        idx = [x for x in les if x["chapter"].startswith(f"{book} 第{m.group(2)}单元 {uname} ·")]
        no = idx.index(t) + 1
        nn = full.get((book, uname, no))
        if not nn or nn == old:
            continue
        t["name"] = nn
        t["chapter"] = t["chapter"].rsplit(" · ", 1)[0] + " · " + nn
        changed.append((old, nn))

    json.dump(topics, open(f"{D}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    skel = json.load(open(f"{D}/_skeleton.json", encoding="utf-8"))
    byid = {t["id"]: t for t in topics}
    for s in skel:
        for u in s.get("units", []):
            les_ids = [t["id"] for t in topics
                       if t["level"] == "lesson" and t.get("prereqUpper") == [u["unitId"]]]
            if les_ids:
                u["lessons"] = [byid[i]["name"] for i in les_ids]
    json.dump(skel, open(f"{D}/_skeleton.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    left = Counter(t["name"] for t in les)
    print("改名 %d 处 ｜仍有重名 %d %s" % (len(changed), sum(1 for v in left.values() if v > 1),
                                          [k for k, v in left.items() if v > 1][:3]))
    for a, b in changed[:8]:
        print("  ", a, "→", b)


if __name__ == "__main__":
    main()
