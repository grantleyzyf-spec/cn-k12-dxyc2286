#!/usr/bin/env python3
"""生成 diagnose/exam-index.json —— 整卷模式（单元/期中/期末）用的卷索引。

用法：
    python3 scripts/build_exam_index.py            # 扫描 data/math/exams/ 工作区
    python3 scripts/build_exam_index.py --tracked  # 只收 git 已跟踪的文件（避免把未提交的卷写进索引）

索引结构：
    { subject, generated, count, exams: { examId: {examId, path, book, paper, kind,
      grade, stage, duration, fullScore, scope, itemCount} } }

约定：每个卷 JSON 必须含 examId / book / paper / kind / grade / stage / duration /
fullScore / sections。path 相对 data/math/（前端按 ../data/math/<path> 取）。
"""
import argparse
import glob
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EDITION = "人教版"   # 卷 JSON 没写 edition 时的默认教材版本
OUT = os.path.join(ROOT, "diagnose", "exam-index.json")


def tracked_files():
    out = subprocess.check_output(
        ["git", "-c", "core.quotepath=false", "-C", ROOT, "ls-files", "-z", "data/math/exams"]
    )
    paths = [p.decode("utf-8") for p in out.split(b"\0") if p]
    return [os.path.join(ROOT, p) for p in paths if p.endswith(".json")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracked", action="store_true", help="只收 git 已跟踪的卷文件")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    files = tracked_files() if args.tracked else sorted(glob.glob(os.path.join(ROOT, "data/math/exams/**/*.json"), recursive=True))
    exams = {}
    for fp in files:
        try:
            d = json.load(open(fp, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"跳过（解析失败）{fp}: {e}")
            continue
        eid = d.get("examId")
        if not eid:
            print(f"跳过（无 examId）{fp}")
            continue
        rel = os.path.relpath(fp, os.path.join(ROOT, "data/math")).replace(os.sep, "/")
        edition = d.get("edition") or DEFAULT_EDITION
        exams[eid] = {
            "examId": eid,
            "path": rel,
            "book": d.get("book"),
            "paper": d.get("paper"),
            "kind": d.get("kind"),
            "grade": d.get("grade"),
            "stage": d.get("stage"),
            "duration": d.get("duration"),
            "fullScore": d.get("fullScore"),
            "edition": edition,
            "scope": d.get("scope") or [],
            "itemCount": sum(len(s.get("items") or []) for s in d.get("sections") or []),
        }

    editions = sorted({v["edition"] for v in exams.values()})
    payload = {"subject": "math", "edition": DEFAULT_EDITION, "editions": editions,
               "generated": __import__("datetime").date.today().isoformat(),
               "count": len(exams), "exams": dict(sorted(exams.items()))}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    kinds = {}
    for v in exams.values():
        kinds[v["kind"]] = kinds.get(v["kind"], 0) + 1
    ed = {}
    for v in exams.values():
        ed[v["edition"]] = ed.get(v["edition"], 0) + 1
    print(f"写入 {args.out}：{len(exams)} 卷 {kinds} 版本分布 {ed}")


if __name__ == "__main__":
    main()
