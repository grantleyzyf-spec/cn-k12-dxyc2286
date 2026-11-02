#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为某版本桶生成「试卷派单」（_exam_shards/E*.json）——按册分片，单元卷 + 期中A/B + 期末A/B。

为什么用生成器：手写 100+ 卷派单一定会出现「同一卷两个 examId」「跨册混片（单册口径的 checker 全片判死）」
「topicIds 漏本册点」三类错，而这三类都能在生成时断言掉。

用法：
  python3 scripts/gen_exam_shards.py math-sujiao --prefix msj --dry   # 只报数，不写文件
  python3 scripts/gen_exam_shards.py math-sujiao --prefix msj        # 写 <repo>/data/<bucket>/_exam_shards/

口径（与冀教/苏教实测一致）：
  · 单元卷 examId = <prefix>_exam_<book_code>_uNN；期中/期末 = <prefix>_exam_<book_code>_mid_a|b / fin_a|b
  · 每卷 topicIds = 该章单元点 + 其下全部课时点（`chapter` 以「<章> · 」开头）
  · 分片 ≤6 卷且**必须单册**——跨册就切（push() 里带 book 变化判断）
  · template 按学段：小学1-2 / 小学3-6 / 初中 / 高中（卷子体例由 checker 的 TEMPLATES 决定）
"""
import argparse
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CN = {c: i for i, c in enumerate("一二三四五六七八九十", 1)}


def book_code(book):
    """册名 → examId 片段：一年级上册→g1a；必修第一册→b1；选择性必修第一册→x1。"""
    m = re.search(r"([一二三四五六七八九])年级([上下])册", book)
    if m:
        return f"g{CN[m.group(1)]}{'a' if m.group(2) == '上' else 'b'}"
    m = re.search(r"选择性必修(第)?([一二三四五])册", book)
    if m:
        return f"x{CN[m.group(2)]}"
    m = re.search(r"必修(第)?([一二三四五])册", book)
    if m:
        return f"b{CN[m.group(2)]}"
    return re.sub(r"\W", "", book)[:4]


def stage_grade(book):
    m = re.search(r"([一二三四五六七八九])年级", book)
    if m:
        g = CN[m.group(1)]
        return ("小学" if g <= 6 else "初中"), g
    return "高中", {"b1": 10, "b2": 11, "x1": 11, "x2": 12}.get(book_code(book), 10)


def template_of(grade):
    if grade <= 2:
        return "小学1-2"
    if grade <= 6:
        return "小学3-6"
    if grade <= 9:
        return "初中"
    return "高中"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bucket")
    ap.add_argument("--prefix", required=True, help="examId 前缀，如 msj / msk / mxj / mqd / mhb")
    ap.add_argument("--per-shard", type=int, default=6)
    ap.add_argument("--books", nargs="*", default=[], help="只出这些册（留空=全桶）")
    ap.add_argument("--skip-match", default="数学建模活动|综合与实践|总复习|主题活动",
                    help="chapter 命中此正则的单元不出卷")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    base = os.path.join(ROOT, "data", a.bucket)
    topics = json.load(open(os.path.join(base, "topics.json"), encoding="utf-8"))
    skip_re = re.compile(a.skip_match) if a.skip_match else None
    by_book = {}
    for t in topics:
        ch = t.get("chapter") or ""
        book = ch.split(" ")[0]
        if a.books and book not in set(a.books):
            continue
        by_book.setdefault(book, {"units": [], "all": []})
        by_book[book]["all"].append(t)
        if " · " not in ch and t.get("level") != "lesson":
            if skip_re and skip_re.search(ch):
                continue
            by_book[book]["units"].append(t)

    def points_of(unit):
        ch = unit["chapter"]
        return [unit["id"]] + [t["id"] for t in topics
                               if (t.get("chapter") or "").startswith(ch + " · ")]

    shards, cur, cur_book = [], [], [None]

    def push(item):
        """追加一卷；跨册或满片就切分（分片必须单册，否则 checker 与合并器全片判死）。"""
        if cur and (item["shard_book"] != cur_book[0] or len(cur) >= a.per_shard):
            shards.append(cur[:])
            cur.clear()
        cur.append(item)
        cur_book[0] = item["shard_book"]

    for book, info in sorted(by_book.items()):
        stage, grade = stage_grade(book)
        tmpl, code = template_of(grade), book_code(book)
        for i, u in enumerate(info["units"], 1):
            push({"shard_book": book, "stage": stage, "grade": grade, "template": tmpl,
                  "kind": "unit",
                  "exam": {"paper": f"{u['chapter']} 测试卷", "scope": [u["chapter"]],
                           "topicIds": points_of(u),
                           "examId": f"{a.prefix}_exam_{code}_u{i:02d}"}})
        allch = [u["chapter"] for u in info["units"]]
        half = allch[: max(1, len(allch) // 2)]
        for kind, label, scope in (("mid", "期中", half), ("fin", "期末", allch)):
            ids = [t["id"] for t in topics
                   if any((t.get("chapter") or "") == c or (t.get("chapter") or "").startswith(c + " · ")
                          for c in scope)]
            for suf in ("A", "B"):
                push({"shard_book": book, "stage": stage, "grade": grade, "template": tmpl,
                      "kind": kind,
                      "exam": {"paper": f"{label}测试卷{suf}", "scope": scope, "topicIds": ids,
                               "examId": f"{a.prefix}_exam_{code}_{kind}_{suf.lower()}"}})
    if cur:
        shards.append(cur)

    n_units = sum(len(v["units"]) for v in by_book.values())
    print(f"{a.bucket}: 册 {len(by_book)} · 单元卷 {n_units} · 期中期末 {len(by_book) * 4} · 分片 {len(shards)}")
    if a.dry:
        return
    out_dir = os.path.join(base, "_exam_shards")
    os.makedirs(out_dir, exist_ok=True)
    used = [int(m.group(1)) for f in os.listdir(out_dir)
            if (m := re.match(r"E(\d+)\.json$", f))]
    start = (max(used) + 1) if used else 1
    for k, group in enumerate(shards):
        i = start + k
        books = {g["shard_book"] for g in group}
        if len(books) > 1:
            raise SystemExit(f"E{i:02d} 跨册（{books}）——分片必须单册")
        payload = {"shard": f"E{i:02d}", "bucket": a.bucket, "book": group[0]["shard_book"],
                   "grade": group[0]["grade"], "stage": group[0]["stage"],
                   "template": group[0]["template"], "kind": group[0]["kind"],
                   "exams": [g["exam"] for g in group]}
        json.dump(payload, open(os.path.join(out_dir, f"E{i:02d}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    print("写出", out_dir)


if __name__ == "__main__":
    main()
