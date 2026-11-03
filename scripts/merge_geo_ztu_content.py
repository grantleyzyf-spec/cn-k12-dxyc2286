#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）地理：把 _points/*.json（点内容）＋ _bank/*.json（题库）合并进库。

产物：data/geography-zhongtu-cz/{topics.json, questions.json, dependencies.json}

口径（与 scripts/test_geo_ztu.py 同源，改一处必改另一处）：
- 点字段以 `_skeleton.json` 为骨架（id/name/level/chapter/book/grade/semester/domain/subject/unitId），
  内容从 `_points/TNN.json` 覆盖（type/description/mastery_criteria/diagnostic_question）。
- `tags` = [domain, 主题名]（`tags[0]` 必须是领域名，门禁有断言）。
- 先修：课时的 `prerequisites` **只放课时点**，按教材课序串成一条链；
  单元点的 `prerequisites=[]` ＋ `root_reason`；课时的 `prereqUpper` 指向本主题单元点。
- `dependencies` **由 prerequisites 派生**（hard 边），不手工加边。
- 合并前先跑两个分片 checker；任一片红就整批拒写（防半成品入库）。
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")
SKEL = os.path.join(D, "_skeleton.json")


def load(p):
    return json.load(open(p, encoding="utf-8"))


def atomic_dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main() -> int:
    if "--skip-check" not in sys.argv:
        bad = 0
        for p in sorted(glob.glob(os.path.join(D, "_points", "T*.json"))):
            r = subprocess.run([sys.executable, "scripts/check_geo_ztu_points.py", p],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0:
                bad += 1
                print(f"❌ 点分片未过：{os.path.basename(p)}")
                print((r.stdout or "").strip().splitlines()[-4:])
        for p in sorted(glob.glob(os.path.join(D, "_bank", "T*.json"))):
            r = subprocess.run([sys.executable, "scripts/check_geo_ztu_bank.py", p],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0:
                bad += 1
                print(f"❌ 题库分片未过：{os.path.basename(p)}")
                print((r.stdout or "").strip().splitlines()[-4:])
        if bad:
            print(f"\n共 {bad} 片未过门禁 ⇒ 拒绝合并")
            return 1

    skel = load(SKEL)
    content = {}
    for p in sorted(glob.glob(os.path.join(D, "_points", "T*.json"))):
        for pt in load(p).get("points") or []:
            content[pt["id"]] = pt
    missing = [t["id"] for t in skel if t["id"] not in content]
    if missing:
        print(f"❌ 缺内容点 {len(missing)}：{missing[:6]}")
        return 1

    topics = []
    for t in skel:
        c = content[t["id"]]
        rec = dict(t)
        rec.update(
            type=c.get("type") or "conceptual",
            description=(c.get("description") or "").strip(),
            mastery_criteria=[x.strip() for x in c.get("mastery_criteria") or []],
            diagnostic_question=c.get("diagnostic_question") or {},
            tags=[t["domain"], t.get("chapter", "").split(" ")[-1] or t["domain"]],
            verified=False,
            root_reason="主题上位点，不设先修课时" if t["level"] == "unit" else "",
            prerequisites=[],
            prereqUpper=t.get("unitId") or "",
        )
        rec.pop("book", None)  # 册名只在 chapter/grade 里体现，schema 无 book 字段
        topics.append(rec)

    # 先修链：同一册内按 id 顺序串课时点（id 即教材课序），单元点不设先修
    lessons = [t for t in topics if t["level"] == "lesson"]
    prev = None
    for t in lessons:
        if prev is not None:
            t["prerequisites"] = [prev["id"]]
        else:
            t["root_reason"] = "本册第一个课时，无先修课时"
        prev = t
    deps = [(t["prerequisites"][0], t["id"]) for t in lessons if t["prerequisites"]]

    qs = []
    for p in sorted(glob.glob(os.path.join(D, "_bank", "T*.json"))):
        qs.extend(load(p).get("questions") or [])
    qs.sort(key=lambda q: q["id"])
    ids = [q["id"] for q in qs]
    if len(set(ids)) != len(ids):
        dup = [k for k in set(ids) if ids.count(k) > 1][:5]
        print(f"❌ 题 id 重复：{dup}")
        return 1
    tids = {t["id"] for t in topics}
    orphan = [q["id"] for q in qs if q.get("topicId") not in tids]
    if orphan:
        print(f"❌ 题指向不存在的点 {len(orphan)}：{orphan[:6]}")
        return 1

    atomic_dump(os.path.join(D, "topics.json"), topics)
    atomic_dump(os.path.join(D, "questions.json"), qs)
    atomic_dump(os.path.join(D, "dependencies.json"),
                [dict(**{"from": a, "to": b}, type="hard") for a, b in deps])

    from collections import Counter
    per = Counter(q["topicId"] for q in qs)
    lu = [t for t in topics if t["level"] == "unit"]
    ll = [t for t in topics if t["level"] == "lesson"]
    print(f"合并完成：点 {len(topics)}（单元 {len(lu)} / 课时 {len(ll)}）· 题 {len(qs)} · 边 {len(deps)}")
    print(f"课时点题量 {min(per[t['id']] for t in ll)}–{max(per[t['id']] for t in ll)}，"
          f"单元点 {min(per[t['id']] for t in lu)}–{max(per[t['id']] for t in lu)}")
    print("题型", dict(Counter(q["type"] for q in qs)), "难度", dict(Counter(q["difficulty"] for q in qs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
