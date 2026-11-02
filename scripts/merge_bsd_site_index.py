#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只把 math-bsd 的条目换进站点索引，其它学科条目原样保留（并行会话保护）。

并行会话会在本工作区留下未提交的其它学科数据；直接重建三份索引会把它们写进索引，
推上去就是 404 死链，还会挤掉远端合法条目。做法：
  1) 先备份旧索引；2) 跑官方 builder；3) 只保留 `data/math-bsd/` 前缀（或 subject=math-bsd）
     的新条目，其余全部回退成旧值；4) 重算 count 并打印差集。

用法：python3 scripts/merge_bsd_site_index.py [--check]
"""
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "data/math-bsd/"
FILES = ["learn/index.json", "learn/exam/index.json", "diagnose/exam-index.json"]
BAK = "/tmp/bsd_index_bak"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, o, indent=1):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, p)


def is_bsd(x):
    if isinstance(x, dict):
        p = str(x.get("path", ""))
        # 学层索引 path 形如 data/math-bsd/learn/<册>.json；
        # 讲解索引 path 形如 data/math-bsd-<册>.json（没有桶目录），故用子串判定。
        if "math-bsd" in p or p.startswith(PREFIX):
            return True
        if x.get("subject") == "math-bsd":
            return True
    return False


def merge_books(new, old):
    """learn/index.json 与 learn/exam/index.json：books[] 列表按 bsd 前缀替换。"""
    nb = [b for b in new.get("books", []) if is_bsd(b)]
    kept = [b for b in old.get("books", []) if not is_bsd(b)]
    # 保持旧顺序：非 bsd 条目按旧序，bsd 条目按新序追加在后面（bsd 属 math 组，前端按学科级联，不依赖顺序）
    out = kept + nb
    res = dict(old)
    res.update({k: v for k, v in new.items() if k != "books"})
    res["books"] = out
    # count 口径随文件而异：学层索引 = 课时总数（sum lessonCount），
    # 讲解索引 = 册数。判据看条目里有没有 lessonCount，别一律写 len(books)。
    if any("lessonCount" in b for b in out):
        res["count"] = sum(b.get("lessonCount", 0) for b in out)
    else:
        res["count"] = len(out)
    return res


def merge_exam_index(new, old):
    """diagnose/exam-index.json：exams 为 examId → 记录。"""
    nex = new.get("exams") or {}
    oex = old.get("exams") or {}
    if isinstance(nex, list):  # 兼容列表形态
        nex = {e["examId"]: e for e in nex if isinstance(e, dict) and e.get("examId")}
        oex = {e["examId"]: e for e in oex if isinstance(e, dict) and e.get("examId")} if isinstance(oex, list) else oex
    merged = {k: v for k, v in oex.items() if not is_bsd(v)}
    bsd_new = {k: v for k, v in nex.items() if is_bsd(v)}
    merged.update(bsd_new)
    res = dict(new)
    res["exams"] = merged
    res["count"] = len(merged)
    # subjects 里只更新 math-bsd 的计数
    subs = old.get("subjects") or {}
    if isinstance(subs, dict):
        subs = dict(subs)
        if "math-bsd" in (new.get("subjects") or {}):
            subs["math-bsd"] = new["subjects"]["math-bsd"]
        res["subjects"] = subs
    return res, len(bsd_new)


def main():
    check = "--check" in sys.argv
    os.makedirs(BAK, exist_ok=True)
    old = {}
    for f in FILES:
        p = os.path.join(REPO, f)
        old[f] = load(p)
        shutil.copy2(p, os.path.join(BAK, f.replace("/", "_")))

    if not check:
        for cmd in (["scripts/build_learn_site.py"],
                    ["scripts/build_exam_lecture_site_v2.py"],
                    ["scripts/build_exam_index.py"]):
            r = subprocess.run([sys.executable] + cmd, cwd=REPO, capture_output=True, text=True)
            print(f"$ {' '.join(cmd)} → rc={r.returncode} {(r.stdout or '').strip().splitlines()[-1:] }")

    for f in FILES:
        p = os.path.join(REPO, f)
        new = load(p)
        if f == "diagnose/exam-index.json":
            merged, n = merge_exam_index(new, old[f])
            print(f"{f}: math-bsd 卷 {n}，总 {merged['count']}（旧 {old[f].get('count')}）")
        else:
            merged = merge_books(new, old[f])
            nb = sum(1 for b in merged["books"] if is_bsd(b))
            print(f"{f}: math-bsd 条 {nb}，总 {merged['count']}（旧 {old[f].get('count')}）")
        if not check:
            dump(p, merged, indent=(1 if f.endswith("exam-index.json") else 2))
    print("完成" + ("（--check 未写盘）" if check else ""))


if __name__ == "__main__":
    main()
