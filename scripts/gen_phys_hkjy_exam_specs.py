#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪科教版高中物理：试卷 spec 生成器（31 章卷 ＋ 6 册×4 期中期末 ＝ 55 卷）。

卷制（高中物理）：150 分 / 90 分钟 / 21 题
  一、单项选择题 10×3＝30
  二、多项选择题  5×4＝20
  三、实验题      2×15＝30
  四、计算题      4 题（15+18+18+19）＝70
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")

BOOK_CODE = {"必修第一册": "b1", "必修第二册": "b2", "必修第三册": "b3",
             "选择性必修第一册": "x1", "选择性必修第二册": "x2", "选择性必修第三册": "x3"}

SECTIONS = [("一、单项选择题", "choice", 10, 3),
            ("二、多项选择题", "multi", 5, 4),
            ("三、实验题", "experiment", 2, 15),
            ("四、计算题", "calc", 4, None)]      # 计算题逐题分值见 CALC_SCORES
CALC_SCORES = [15, 18, 18, 19]


def main(write=False):
    topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    books = {}
    for t in topics:
        book = t["chapter"].split(" ")[0]
        books.setdefault(book, []).append(t)

    specs = {}
    for book, ts in books.items():
        code = BOOK_CODE[book]
        grade = ts[0]["grade"]
        sem = ts[0]["semester"]
        units = [t for t in ts if t["level"] == "unit"]
        units.sort(key=lambda u: int(re.search(r"第(\d+)章", u["chapter"]).group(1)))
        # 章卷
        for u in units:
            no = int(re.search(r"第(\d+)章", u["chapter"]).group(1))
            eid = "phk_exam_%s_u%02d" % (code, no)
            lessons = [t for t in ts if t["level"] == "lesson" and t["chapter"].startswith(u["chapter"] + " · ")]
            specs[eid] = dict(examId=eid, book=book, grade=grade, semester=sem, stage="高中",
                              kind="unit", paper="第%d章 %s 测试卷" % (no, u["name"]),
                              scope=[u["chapter"]],
                              must_cover=[u["id"]] + [l["id"] for l in lessons],
                              out=os.path.join(D, "exams", book, "第%d章 %s 测试卷.json" % (no, u["name"])))
        # 期中/期末
        half = units[: max(1, (len(units) + 1) // 2)]
        for kind, sel, label in (("mid", half, "期中"), ("fin", units, "期末")):
            for ab in ("A", "B"):
                suffix = ("qza" if ab == "A" else "qzb") if kind == "mid" else ("qma" if ab == "A" else "qmb")
                eid = "phk_exam_%s_%s" % (code, suffix)
                paper = "%s测试卷%s" % (label, ab)
                cov = []
                for u in sel:
                    cov.append(u["id"])
                    cov += [t["id"] for t in ts if t["level"] == "lesson" and t["chapter"].startswith(u["chapter"] + " · ")]
                specs[eid] = dict(examId=eid, book=book, grade=grade, semester=sem, stage="高中",
                                  kind=kind, paper=paper, scope=[u["chapter"] for u in sel],
                                  must_cover=cov,
                                  out=os.path.join(D, "exams", book, paper + ".json"))

    # 段落结构
    for s in specs.values():
        secs = []
        for title, typ, cnt, each in SECTIONS:
            secs.append({"title": title, "type": typ, "count": cnt, "score_each": each,
                         "scores": CALC_SCORES if each is None else [each] * cnt})
        s["sections"] = secs
        s["duration"] = 90
        s["fullScore"] = 150
        s["totalItems"] = sum(len(x["scores"]) for x in secs)

    print("卷 %d（章卷 %d ＋ 期中期末 %d）" % (len(specs),
          sum(1 for s in specs.values() if s["kind"] == "unit"),
          sum(1 for s in specs.values() if s["kind"] != "unit")))
    eids = list(specs)
    assert len(eids) == len(set(eids)), "examId 撞号"
    if write:
        os.makedirs(os.path.join(D, "_exam_spec"), exist_ok=True)
        for eid, s in specs.items():
            json.dump(s, open(os.path.join(D, "_exam_spec", eid + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
        print("已写入 _exam_spec/%d" % len(specs))
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))