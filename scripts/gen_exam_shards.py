#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为某版本桶生成「试卷派单」（_exam_shards/E*.json）——按册分片，单元卷 + 期中A/B + 期末A/B。

复用冀教（math-hebei）已成型的派单口径：每片 ≤6 卷、`template` 按学段、`topicIds` 为该章全部点。

用法：
  python3 scripts/gen_exam_shards.py math-sujiao --prefix msj --dry   # 只打印
  python3 scripts/gen_exam_shards.py math-sujiao --prefix msj        # 写 _exam_shards/
"""
import argparse
import glob
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
    # 高中册按仓库口径：grade = 10 + 册序（必修一 10 / 必修二 11 / 必修三 12 / 选必一 13 / 选必二 14）
    code = book_code(book)
    seq = {"b1": 1, "b2": 2, "b3": 3, "b4": 4, "x1": 4, "x2": 5, "x3": 6}.get(code)
    if seq is None:
        m = re.search(r"([一二三四五六七八九])年级", book)
        seq = CN.get(m.group(1), 1) if m else 1
    return "高中", 9 + seq


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
    ap.add_argument("--prefix", required=True, help="examId 前缀，如 msj / msk / mxj / mqd（只写字母部分，脚本自己拼 _exam_）")
    ap.add_argument("--per-shard", type=int, default=6)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    # ⛔ 传 --prefix msk_exam 会拼出 msk_exam_exam_g7a_u01（实测踩过 48 卷）；这里统一剥掉尾部 _exam
    a.prefix = re.sub(r"[_-]?exam$", "", a.prefix)


    base = os.path.join(ROOT, "data", a.bucket)
    topics = json.load(open(os.path.join(base, "topics.json"), encoding="utf-8"))
    # 册 → (grade, semester)：一律取 topics.json 的既有值，不按册名猜（各社高中册次编号不统一）
    bookmeta = {}
    for t in topics:
        b = (t.get("chapter") or "").split(" ")[0]
        bookmeta.setdefault(b, (t.get("grade"), t.get("semester")))
    units, by_book = [], {}
    for t in topics:
        ch = t.get("chapter") or ""
        book = ch.split(" ")[0]
        by_book.setdefault(book, {"units": [], "all": []})
        if t.get("level") == "unit" or (" · " not in ch and t.get("level") != "lesson"):
            if " · " not in ch:
                by_book[book]["units"].append(t)
                units.append(t)
    # 单元 → 它名下的全部点（单元点 + 课时点）
    def points_of(unit):
        ch = unit["chapter"]
        ids = [unit["id"]]
        ids += [t["id"] for t in topics
                if (t.get("chapter") or "").startswith(ch + " · ")]
        return ids

    shards, cur = [], []
    cur_book = [None]

    def push(item):
        """追加一卷；跨册或满片就切分（分片必须单册，否则 checker 与合并器全片判死）。"""
        if cur and (item["shard_book"] != cur_book[0] or len(cur) >= a.per_shard):
            shards.append(cur[:]); cur.clear()
        cur.append(item)
        cur_book[0] = item["shard_book"]

    for book, info in sorted(by_book.items(), key=lambda kv: kv[0]):
        stage, grade = stage_grade(book)
        g_real, sem = bookmeta.get(book, (grade, "上"))
        grade = g_real if isinstance(g_real, int) else grade
        tmpl = template_of(grade)
        code = book_code(book)
        for i, u in enumerate(info["units"], 1):
            push({"shard_book": book, "stage": stage, "grade": grade, "template": tmpl,
                  "kind": "unit",
                  "exam": {"paper": f"{u['chapter']} 测试卷", "scope": [u["chapter"]],
                           "topicIds": points_of(u),
                           "examId": f"{a.prefix}_exam_{code}_u{i:02d}"}})
        # 期中 A/B：前半册；期末 A/B：全册
        allch = [u["chapter"] for u in info["units"]]
        half = allch[: max(1, len(allch) // 2)]
        for kind, label, scope in [("mid", "期中", half), ("fin", "期末", allch)]:
            for suf in ("A", "B"):
                push({"shard_book": book, "stage": stage, "grade": grade, "template": tmpl,
                      "kind": kind,
                      "exam": {"paper": f"{label}测试卷{suf}", "scope": scope,
                               "topicIds": [t["id"] for t in topics
                                            if any((t.get("chapter") or "").startswith(c + " · ")
                                                   or (t.get("chapter") or "") == c for c in scope)],
                               "examId": f"{a.prefix}_exam_{code}_{kind}_{suf.lower()}"}})
    if cur:
        shards.append(cur)

    out_dir = os.path.join(base, "_exam_shards")
    n_units = sum(len(v["units"]) for v in by_book.values())
    print(f"{a.bucket}: 册 {len(by_book)} · 单元卷 {n_units} · 期中期末 {len(by_book)*4} · 分片 {len(shards)}")
    if not a.dry:
        os.makedirs(out_dir, exist_ok=True)
        for i, group in enumerate(shards, 1):
            eid = f"E{i:02d}"
            books = {g["shard_book"] for g in group}
            payload = {"shard": eid, "bucket": a.bucket,
                       "book": group[0]["shard_book"],
                       "grade": group[0]["grade"], "stage": group[0]["stage"],
                       "template": group[0]["template"],
                       "kind": group[0]["kind"],
                       "exams": [g["exam"] for g in group]}
            if len(books) > 1:
                raise SystemExit(f"{eid} 跨册（{books}）—— 分片必须单册")
            json.dump(payload, open(os.path.join(out_dir, eid + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        print("写出", out_dir)


if __name__ == "__main__":
    main()
