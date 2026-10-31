#!/usr/bin/env python3
"""生成 diagnose/exam-index.json —— 整卷模式（学科 → 教材版本 → 册次 → 卷）的索引。

用法：
    python3 scripts/build_exam_index.py            # 扫描所有 data/<学科>/exams/ 工作区
    python3 scripts/build_exam_index.py --tracked  # 只收 git 已跟踪的文件（避免把未提交的卷写进索引）

索引结构：
    {
      "generated": "2026-10-31",
      "count": 177,
      "subjects": { "math": {"count": 177, "editions": ["人教版"], "defaultEdition": "人教版"} },
      "exams": { examId: {examId, subject, path, book, paper, kind, grade, stage,
                          edition, duration, fullScore, scope, itemCount} }
    }

- `path` 相对 `data/<subject>/`，前端按 `../data/<subject>/<path>` 取卷；
- 卷 JSON 写了 `edition` 就以卷为准，否则用 DEFAULT_EDITION；
- 新增学科只要把卷放进 `data/<学科>/exams/<册次>/`，重跑本脚本即可自动出现在前端。
"""
import argparse
import glob
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "diagnose", "exam-index.json")
DEFAULT_EDITION = "人教版"

SUBJECTS = [
    "math", "chinese", "english", "physics", "chemistry", "biology", "history", "geography",
    "science", "information-technology", "japanese", "russian", "german", "french", "spanish",
    "music", "art",
]


def tracked_files():
    out = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "-C", ROOT, "ls-files", "-z", "data"]
    )
    rels = [p.decode("utf-8") for p in out.split(b"\0") if p]
    return [r for r in rels if "/exams/" in r and r.endswith(".json")]


def walk_files():
    rels = []
    for sub in SUBJECTS:
        base = os.path.join(ROOT, "data", sub, "exams")
        if os.path.isdir(base):
            rels += [os.path.relpath(p, ROOT).replace(os.sep, "/")
                     for p in glob.glob(os.path.join(base, "**", "*.json"), recursive=True)]
    return sorted(rels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracked", action="store_true", help="只收 git 已跟踪的卷文件")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    rels = tracked_files() if args.tracked else walk_files()
    exams = {}
    per_subject = {}
    for rel in rels:
        parts = rel.split("/")
        if len(parts) < 5 or parts[0] != "data":
            continue
        sub = parts[1]
        try:
            d = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"跳过（解析失败）{rel}: {e}")
            continue
        eid = d.get("examId")
        if not eid:
            print(f"跳过（无 examId）{rel}")
            continue
        edition = d.get("edition") or DEFAULT_EDITION
        exams[eid] = {
            "examId": eid,
            "subject": sub,
            "path": "/".join(parts[2:]),          # exams/<册次>/<卷>.json
            "book": d.get("book"),
            "paper": d.get("paper"),
            "kind": d.get("kind"),
            "grade": d.get("grade"),
            "stage": d.get("stage"),
            "edition": edition,
            "duration": d.get("duration"),
            "fullScore": d.get("fullScore"),
            "scope": d.get("scope") or [],
            "itemCount": sum(len(s.get("items") or []) for s in d.get("sections") or []),
        }
        s = per_subject.setdefault(sub, {"count": 0, "editions": set()})
        s["count"] += 1
        s["editions"].add(edition)

    subjects = {}
    for sub, v in sorted(per_subject.items()):
        eds = sorted(v["editions"])
        subjects[sub] = {"count": v["count"], "editions": eds, "defaultEdition": eds[0]}

    payload = {
        "generated": __import__("datetime").date.today().isoformat(),
        "count": len(exams),
        "subjects": subjects,
        "exams": dict(sorted(exams.items())),
    }
    # 兼容单学科时代的顶层字段（取数学）
    if "math" in subjects:
        payload["subject"] = "math"
        payload["edition"] = subjects["math"]["defaultEdition"]
        payload["editions"] = subjects["math"]["editions"]

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    kinds = {}
    for v in exams.values():
        kinds[v["kind"]] = kinds.get(v["kind"], 0) + 1
    print(f"写入 {args.out}：{len(exams)} 卷 {kinds}")
    for sub, v in subjects.items():
        print(f"  {sub}: {v['count']} 卷 · 版本 {v['editions']}")


if __name__ == "__main__":
    main()
