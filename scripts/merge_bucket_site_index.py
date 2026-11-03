#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只把某一个学科桶的条目换进三份站点索引，其余学科原样回退（并行会话保护）。

三个 builder（build_learn_site.py / build_exam_lecture_site_v2.py / build_exam_index.py）都扫
**文件系统**，本地工作区常躺着并行会话未提交的在途数据。直接重建后整文件提交，推上去就是 404 死链，
并把远端已有的合法条目挤掉。做法：备份 → 跑 builder → 只保留本桶条目（其余取备份旧值）→ 重算 count。

用法：
    python3 scripts/merge_bucket_site_index.py --bucket geography-jin
    python3 scripts/merge_bucket_site_index.py --bucket geography-jin --check

三个静默报错点：
  1) 判本桶条目要用**子串** `bucket in path`（讲解索引 path 是 `data/<bucket>-<册>.json`，前缀判会漏整册）；
  2) `count` 口径随文件而异：学层索引＝课时总数（sum lessonCount），讲解索引＝册数；
  3) `diagnose/exam-index.json` 的 exams 是 `examId -> 记录`，按 `subject == bucket` 判归属。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

FILES = ["learn/index.json", "learn/exam/index.json", "diagnose/exam-index.json"]
BUILDERS = ["scripts/build_learn_site.py",
            "scripts/build_exam_lecture_site_v2.py",
            "scripts/build_exam_index.py"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj, indent=2):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--bak", default=None)
    a = ap.parse_args()

    repo = os.path.abspath(a.repo)
    bucket = a.bucket
    bak = a.bak or f"/tmp/{bucket.replace('/', '_')}_index_bak"
    os.makedirs(bak, exist_ok=True)

    def is_ours(x):
        if not isinstance(x, dict):
            return False
        if bucket in str(x.get("path", "")):
            return True
        return x.get("subject") == bucket

    old = {}
    for f in FILES:
        p = os.path.join(repo, f)
        old[f] = load(p)
        shutil.copy2(p, os.path.join(bak, f.replace("/", "_")))

    if not a.check:
        for b in BUILDERS:
            r = subprocess.run([sys.executable, b], cwd=repo, capture_output=True, text=True)
            tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
            print(f"$ {b} -> rc={r.returncode} {tail[0][:120]}")

    for f in FILES:
        p = os.path.join(repo, f)
        new = load(p)
        if f.endswith("exam-index.json"):
            oe, ne = old[f].get("exams") or {}, new.get("exams") or {}
            if isinstance(oe, list):
                oe = {e["examId"]: e for e in oe if e.get("examId")}
            if isinstance(ne, list):
                ne = {e["examId"]: e for e in ne if e.get("examId")}
            merged = {k: v for k, v in oe.items() if not is_ours(v)}
            ours = {k: v for k, v in ne.items() if is_ours(v)}
            merged.update(ours)
            out = dict(old[f])
            out["exams"] = merged
            out["count"] = len(merged)
            subs = dict(old[f].get("subjects") or {})
            if bucket in (new.get("subjects") or {}):
                subs[bucket] = new["subjects"][bucket]
            out["subjects"] = subs
            print(f"{f}: 本桶卷 {len(ours)}，总 {out['count']}（旧 {old[f].get('count')}）")
            if not a.check:
                dump(p, out, 1)
        else:
            keep = [b for b in old[f].get("books", []) if not is_ours(b)]
            ours = [b for b in new.get("books", []) if is_ours(b)]
            books = keep + ours
            out = dict(old[f])
            out.update({k: v for k, v in new.items() if k != "books"})
            out["books"] = books
            # count 口径随文件而异：学层索引＝课时总数（lessonCount），讲解索引＝卷数（paperCount）
            if any("lessonCount" in b for b in books):
                out["count"] = sum(b.get("lessonCount", 0) for b in books)
            elif any("paperCount" in b for b in books):
                out["count"] = sum(b.get("paperCount", 0) for b in books)
            else:
                out["count"] = len(books)
            print(f"{f}: 本桶册 {len(ours)}，总 {out['count']}（旧 {old[f].get('count')}）")
            if not a.check:
                dump(p, out, 2)

    print("完成" + ("（--check 未写盘）" if a.check else f"；备份在 {bak}"))


if __name__ == "__main__":
    sys.exit(main())
