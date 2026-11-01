# -*- coding: utf-8 -*-
"""道德与法治 / 思想政治：册 → 单元 → 课 盘点（骨架输入）。

内容源（全部有文字层，直接读 PDF 目录页）：
  义教：中小学教材/道德与法治/{小学,初中}/**/*.pdf（人教版，1–9 年级）
  高中：中小学教材/道德与法治/高中思想政治/**.pdf（必修1–4、选择性必修1–3）

目录形态两种：
  小学：`第一单元 我是小学生啦 / 1`、`第1课 开开心心上学去 /2`（带拼音行，名字里有空格）
  初中：`第一单元 少年有梦\t1`、`第一课 开启初中生活\t2`（框题行无编号，如 `奏响中学序曲 2`）
  高中：`第一课 …` / `第一框 …`

用法: python3 scripts/ddfz_inventory.py [--write]
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QD = os.path.join(ROOT, "data", "politics")
BASE = os.path.expanduser("~/Desktop/中小学教材/中小学教材/道德与法治")
CN = "一二三四五六七八九十"

RE_UNIT_P = re.compile(r"第\s*([%s]+)\s*单元\s+([^\n/\t]+?)\s*/" % CN)
RE_LESSON_P = re.compile(r"第\s*(\d+)\s*课\s+([^\n/\t]+?)\s*/\s*\d+")
RE_UNIT_J = re.compile(r"第\s*([%s]+)\s*单元\s+([^\t\n]+?)\s*(?:\t|\s{2,})\s*\d+\s*$" % CN)
RE_LESSON_J = re.compile(r"第\s*([%s]+)\s*课\s+([^\t\n]+?)\s*(?:\t|\s{2,})\s*\d+\s*$" % CN)
RE_LESSON_H = re.compile(r"^\s*第\s*([%s]+)\s*课\s+([^\t\n]+?)\s*(?:\t|\s{2,})\s*\d+\s*$" % CN)
RE_BOX_H = re.compile(r"第([%s]+)框\s*([^\t\n：]+)" % CN)


def cn2int(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1
    if "十" in s:
        a, b = s.split("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def toc(pdf, pages=24):
    return subprocess.run(["pdftotext", "-f", "1", "-l", str(pages), "-layout", pdf, "-"],
                          capture_output=True, text=True).stdout


def clean(s):
    s = re.sub(r"[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüńň\s]+", "", s)  # 去拼音与空格
    return re.sub(r"[·…\.]+$", "", s).strip()


def parse(txt, stage):
    units, cur = [], None
    for line in txt.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m = (RE_UNIT_P.search(line) if stage == "小学" else RE_UNIT_J.search(line) or RE_UNIT_P.search(line))
        if m:
            cur = {"no": cn2int(m.group(1)), "title": clean(m.group(2)), "lessons": []}
            units.append(cur)
            continue
        if stage == "高中" and cur is None:
            m0 = re.match(r"^\s*第\s*([%s]+)\s*课\s+([^\t\n]+?)\s*(?:\t|\s{2,})\s*\d+\s*$" % CN, line)
            if m0:
                cur = {"no": cn2int(m0.group(1)), "title": clean(m0.group(2)), "lessons": []}
                units.append(cur)
                continue
        if cur is None:
            continue
        m = (RE_LESSON_P.search(line) if stage == "小学" else
             (RE_LESSON_J.search(line) or RE_LESSON_P.search(line)))
        if m:
            title = clean(m.group(2))
            no = cn2int(m.group(1))
            if title and no not in [x["no"] for x in cur["lessons"]]:
                cur["lessons"].append({"no": no, "title": title})
            continue
        if stage == "高中":
            m = re.match(r"^\s{2,}([^\d\t\n]{4,30}?)\s*(?:\t|\s{2,})\s*\d+\s*$", line)
            if m:
                title = clean(m.group(1))
                if title and title not in [x["title"] for x in cur["lessons"]]:
                    cur["lessons"].append({"no": len(cur["lessons"]) + 1, "title": title, "kind": "框"})
                continue
        # 高中：课/框
        for rx, kind in ((RE_LESSON_H, "课"), (RE_BOX_H, "框")):
            m = rx.search(line)
            if m:
                title = clean(m.group(2))
                if title and title not in [x["title"] for x in cur["lessons"]]:
                    cur["lessons"].append({"no": cn2int(m.group(1)), "title": title, "kind": kind})
                break
    out, seen = [], set()
    for u in units:
        if not u["title"]:
            continue
        k = (u["no"], u["title"])
        if k in seen:      # 正文页的单元页眉会重复命中，去重
            continue
        seen.add(k)
        if not u["lessons"]:
            # 与前一单元同名同号但带课时的，合并课时
            prev = next((x for x in out if (x["no"], x["title"]) == k), None)
            if prev:
                continue
        out.append(u)
    return out


def main():
    write = "--write" in sys.argv
    books = []
    # 义教
    for stage in ("小学", "初中"):
        for pdf in sorted(glob.glob(os.path.join(BASE, stage, "*.pdf"))):
            b = os.path.basename(pdf)
            m = re.search(r"道德与法治_([一二三四五六七八九])年级_([上下])册", b)
            if not m:
                print("!! 未解析:", b)
                continue
            units = parse(toc(pdf, 40 if stage == "小学" else 24), stage)
            books.append({"book": f"{m.group(1)}年级{m.group(2)}册", "grade": CN.index(m.group(1)) + 1,
                          "semester": m.group(2), "stage": stage, "pdf": b, "units": units})
    # 高中
    for pdf in sorted(glob.glob(os.path.join(BASE, "高中思想政治", "*.pdf"))):
        b = os.path.basename(pdf)
        m = re.search(r"思想政治_([^_]+)_([^_]+)_", b)
        label = (m.group(2) if m else b[:24]).strip("_")
        if not re.match(r"必修|选择性必修", label):
            m2 = re.search(r"(必修[1-4]|选择性必修[1-3])[^_]*", b)
            label = m2.group(0).strip("_") if m2 else label
        grade = 10 if "必修" in label and "选择性" not in label else 11
        units = parse(toc(pdf), "高中")
        books.append({"book": f"高中{label}", "grade": grade, "semester": "上", "stage": "高中",
                      "pdf": b, "units": units})

    books.sort(key=lambda x: (x["grade"], x["semester"]))
    inv = {"generated_by": "scripts/ddfz_inventory.py", "books": books}
    print(f"{'册':<22}{'单元':>4}{'课/框':>6}  单元名")
    for b in books:
        nk = sum(len(u["lessons"]) for u in b["units"])
        head = "；".join(u["title"] for u in b["units"][:3])
        print(f"{b['book']:<22}{len(b['units']):>4}{nk:>6}  {head[:60]}")
    print("册数:", len(books), "| 单元:", sum(len(b["units"]) for b in books),
          "| 课/框:", sum(len(u["lessons"]) for b in books for u in b["units"]))
    empty = [(b["book"], u["no"], u["title"]) for b in books for u in b["units"] if not u["lessons"]]
    print("无课时的单元:", len(empty), empty[:5])
    if write:
        os.makedirs(QD, exist_ok=True)
        json.dump(inv, open(os.path.join(QD, "_inventory.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("WRITTEN data/politics/_inventory.json")


if __name__ == "__main__":
    main()
