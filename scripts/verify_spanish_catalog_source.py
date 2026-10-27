#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 data/spanish-standards-entries.json 的每条 quote 都能在《普通高中西班牙语课程标准
（2017年版2020年修订）》PDF 原文里逐字命中（去空白后子串匹配）。

课标 PDF 不在本机时（CI）自动跳过，退出码 0。
用法：python3 scripts/verify_spanish_catalog_source.py [--pdf <path>]
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data", "spanish-standards-entries.json")
DEFAULT_PDF = os.path.expanduser(
    "~/Desktop/中小学教材/中小学教材/2025修订课程标准/"
    "普通高中课程方案及20科课程标准（2017年版2020年修订)/21.普通高中西班牙语课程标准（2017年版2020年修订）.pdf")

ap = argparse.ArgumentParser()
ap.add_argument("--pdf", default=DEFAULT_PDF)
a = ap.parse_args()

doc = json.load(open(CAT, encoding="utf-8"))
entries = doc["entries"]

if not os.path.exists(a.pdf):
    print("课标 PDF 不在本机（CI 环境），跳过目录回表。entries =", len(entries))
    sys.exit(0)

tmp = "/tmp/spa_kb_source.txt"
subprocess.run(["pdftotext", "-enc", "UTF-8", a.pdf, tmp], check=True)

def norm(s):
    return re.sub(r"\s+", "", s or "")

src = norm(open(tmp, encoding="utf-8", errors="ignore").read())
miss = [(e["id"], e["quote"][:20]) for e in entries if norm(e["quote"]) not in src]
print(f"目录条目 {len(entries)} 条，逐字命中 {len(entries) - len(miss)} 条")
if miss:
    for m in miss[:10]:
        print("  MISS", m)
    print("FAILED:", len(miss))
    sys.exit(1)
print("SPANISH STANDARDS CATALOG: 100% 回表通过")
