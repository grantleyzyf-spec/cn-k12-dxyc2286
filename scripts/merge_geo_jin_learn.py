#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""晋教版地理：学层分片（_parts/L*.json）合并成按册成品（learn/<册>.json）。

护栏（SKILL §5.7）：
- 合并前逐片跑 `check_geo_jin_learn.py`，任一片红就整批拒写；
- 目标册已存在且现有篇数 **多于** 本次合并篇数 → 拒绝写入并列明原因（防分片缺失把成品截成残本）；
- 写盘用 tmp → os.replace 原子落盘。
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-jin")
PARTS = os.path.join(D, "learn", "_parts")
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]


def main() -> int:
    skip_check = "--skip-check" in sys.argv
    parts = sorted(glob.glob(os.path.join(PARTS, "L*.json")))
    if not parts:
        print("❌ 没有学层分片")
        return 1
    if not skip_check:
        bad = []
        for p in parts:
            r = subprocess.run([sys.executable, "scripts/check_geo_jin_learn.py", p],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode != 0:
                bad.append((os.path.basename(p), (r.stdout or "").strip().splitlines()[:6]))
        if bad:
            print(f"❌ {len(bad)} 片未过门禁 ⇒ 拒绝合并")
            for n, tail in bad:
                print(" ", n)
                for x in tail:
                    print("    ", x)
            return 1

    by_book = {b: [] for b in BOOKS}
    for p in parts:
        d = json.load(open(p, encoding="utf-8"))
        book = d.get("book")
        for les in d.get("lessons") or []:
            les.setdefault("book", book)
            by_book.setdefault(book, []).append(les)

    ok = True
    for book, lessons in by_book.items():
        if not lessons:
            continue
        out = os.path.join(D, "learn", f"{book}.json")
        if os.path.exists(out):
            old = json.load(open(out, encoding="utf-8"))
            old_n = len(old.get("lessons") or [])
            if old_n > len(lessons):
                print(f"❌ {book}: 现有成品 {old_n} 篇 > 本次 {len(lessons)} 篇 ⇒ 拒绝写入（分片缺失？）")
                ok = False
                continue
        lessons.sort(key=lambda x: x["topicId"])
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(dict(book=book, lessons=lessons), fh, ensure_ascii=False, indent=1)
        os.replace(tmp, out)
        ns = [len(x.get("markdown") or "") for x in lessons]
        ws = [x.get("words") or 0 for x in lessons]
        print(f"✅ {book}: {len(lessons)} 篇 → {out}（字数 {min(ws)}–{max(ws)}）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
