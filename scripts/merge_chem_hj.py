#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版初中化学（chemistry-hujiao）：把 _points/*.json ＋ _bank/*.json 合并进库。

产物：data/chemistry-hujiao/{topics.json, questions.json, dependencies.json}

口径：
- 点字段以 `_skeleton.json` 为骨架（id/name/level/chapter/book/grade/semester/domain/subject/unitId），
  内容从 `_points/BNN.json` 覆盖（type/description/mastery_criteria/diagnostic_question/tags）。
- tags = [domain, 主题名]（tags[0] 必须是领域名，门禁有断言）。
- 先修：课时 prerequisites **只放课时点**，按教材课序串成链；单元点 prerequisites=[] ＋ root_reason；
  课时 prereqUpper 指向本章单元点。
- dependencies 由 prerequisites 派生（hard 边），不手工加边。
- 合并前先跑两个分片 checker；任一片红就整批拒写（防半成品入库）。

用法：
  python3 scripts/merge_chem_hj.py            # 校验 + 合并
  python3 scripts/merge_chem_hj.py --skip-check
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry-hujiao")
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
        for p in sorted(glob.glob(os.path.join(D, "_points", "B*.json"))):
            r = subprocess.run([sys.executable, "scripts/check_chem_hj_points.py", p],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0:
                bad += 1
                print(f"❌ 点分片未过：{os.path.basename(p)}")
                print("\n".join((r.stdout or "").strip().splitlines()[-4:]))
        for p in sorted(glob.glob(os.path.join(D, "_bank", "B*.json"))):
            r = subprocess.run([sys.executable, "scripts/check_chem_hj_bank.py", p],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0:
                bad += 1
                print(f"❌ 题库分片未过：{os.path.basename(p)}")
                print("\n".join((r.stdout or "").strip().splitlines()[-4:]))
        if bad:
            print(f"\n共 {bad} 片未过门禁 ⇒ 拒绝合并")
            return 1

    skel = load(SKEL)
    # 课标 side-map：合并是「从分片重建」，不带上会把已挂的课标冲掉（技能 §5.9）
    old_topics = load(os.path.join(D, "topics.json")) if os.path.exists(os.path.join(D, "topics.json")) else []
    std_map = {t["id"]: (t.get("standards"), t.get("curriculumRef")) for t in old_topics if t.get("standards")}
    content = {}
    for p in sorted(glob.glob(os.path.join(D, "_points", "B*.json"))):
        for pt in load(p).get("points") or []:
            content[pt["id"]] = pt

    questions = []
    for p in sorted(glob.glob(os.path.join(D, "_bank", "B*.json"))):
        questions.extend(load(p).get("questions") or [])

    missing = [t["id"] for t in skel if t["id"] not in content]
    if missing:
        print(f"❌ 缺内容的点 {len(missing)} 个，例：{missing[:5]} ⇒ 拒绝合并")
        return 1

    topics = []
    # 按单元分组，做先修链
    by_unit = {}
    for t in skel:
        by_unit.setdefault(t.get("unitId") or t["id"], []).append(t)

    for t in skel:
        c = content[t["id"]]
        row = {
            "id": t["id"], "name": t["name"], "level": t["level"], "subject": "chemistry-hujiao",
            "grade": t["grade"], "semester": t["semester"], "chapter": t["chapter"],
            "unitNo": t.get("unitNo"), "domain": t["domain"],
            "type": c.get("type") or t.get("type") or "conceptual",
            "description": c.get("description") or "",
            "mastery_criteria": c.get("mastery_criteria") or [],
            "diagnostic_question": c.get("diagnostic_question") or {},
            "tags": c.get("tags") or [t["domain"], t["name"]],
            "unitId": t.get("unitId") or t["id"],
        }
        if t["level"] == "lesson":
            row["lessonNo"] = t.get("lessonNo")
            row["prereqUpper"] = t.get("unitId")
        if t["id"] in std_map:
            row["standards"], row["curriculumRef"] = std_map[t["id"]]
        topics.append(row)

    # 先修链：同单元课时按 lessonNo 串链
    for uid, members in by_unit.items():
        lessons = sorted([m for m in members if m["level"] == "lesson"], key=lambda x: x.get("lessonNo") or 0)
        prev = None
        for m in lessons:
            row = next(r for r in topics if r["id"] == m["id"])
            row["prerequisites"] = [prev] if prev else []
            if not prev:
                row["root_reason"] = "本主题首课时，无先修课时"
            prev = m["id"]
        for m in members:
            if m["level"] == "unit":
                row = next(r for r in topics if r["id"] == m["id"])
                row["prerequisites"] = []
                row["root_reason"] = "单元上位点，不设先修课时"

    deps = []
    for r in topics:
        for pre in r.get("prerequisites") or []:
            deps.append({"from": pre, "to": r["id"], "type": "hard"})

    # 基本自检
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "题 id 重复"
    topic_ids = {t["id"] for t in topics}
    bad = [q["id"] for q in questions if q.get("topicId") not in topic_ids]
    assert not bad, f"题挂了不存在的点：{bad[:5]}"

    atomic_dump(os.path.join(D, "topics.json"), topics)
    atomic_dump(os.path.join(D, "questions.json"), questions)
    atomic_dump(os.path.join(D, "dependencies.json"), deps)
    print(f"✅ 合并完成：点 {len(topics)}（单元 {sum(1 for t in topics if t['level']=='unit')} / "
          f"课时 {sum(1 for t in topics if t['level']=='lesson')}）｜题 {len(questions)}｜边 {len(deps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
