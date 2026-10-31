# -*- coding: utf-8 -*-
"""生成站点用的学层索引：learn/index.json（学生端「点课时→看讲解」的数据入口）。

结构：
{
  "generated": "2026-11-01",
  "count": 72,
  "books": [
    {"book": "一年级上册", "stage": "小学", "grade": 1, "edition": "人教版",
     "lessonCount": 22, "path": "data/math/learn/一年级上册.json",
     "lessons": [{"topicId": "mat_p1000", "title": "...", "chapter": "第一单元 ...", "words": 1300}]}
  ]
}
章节取自 topics.json 的 chapter（`<册> <单元> · <课时名>` 取 ` · ` 之前部分再去掉册名）。

用法：python3 scripts/build_math_learn_site.py
"""
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math"
OUT = f"{REPO}/learn/index.json"


def stage_of(book):
    if re.match(r"[一二三四五六]年级", book):
        return "小学", int("一二三四五六".index(book[0]) + 1)
    if re.match(r"[七八九]年级", book):
        return "初中", int("七八九".index(book[0]) + 7)
    return "高中", {"必修第一册": 10, "必修第二册": 11}.get(book, 12)


def main():
    topics = {t["id"]: t for t in json.load(open(f"{D}/topics.json", encoding="utf-8"))}
    books = []
    for f in sorted(glob.glob(f"{D}/learn/*.json")):
        if os.path.basename(f).startswith("_"):    # _ocr_waivers.json 等台账不是册数据
            continue
        data = json.load(open(f, encoding="utf-8"))
        book = data["book"]
        stage, grade = stage_of(book)
        lessons = []
        for L in data.get("lessons") or []:
            t = topics.get(L["topicId"], {})
            ch = t.get("chapter") or ""
            unit = ch.split(" · ")[0]
            if unit.startswith(book + " "):
                unit = unit[len(book) + 1:]
            lessons.append({"topicId": L["topicId"], "title": L["title"],
                            "chapter": unit, "words": L.get("words") or 0})
        books.append({"book": book, "stage": stage, "grade": grade, "edition": "人教版",
                      "lessonCount": len(lessons),
                      "path": f"data/math/learn/{book}.json", "lessons": lessons})
    order = {"一年级上册": 1, "一年级下册": 2, "二年级上册": 3, "二年级下册": 4,
             "三年级上册": 5, "三年级下册": 6, "四年级上册": 7, "五年级上册": 8, "六年级上册": 9,
             "七年级上册": 10, "七年级下册": 11, "八年级上册": 12, "八年级下册": 13, "九年级上册": 14,
             "必修第一册": 15, "必修第二册": 16, "选择性必修第一册": 17,
             "选择性必修第二册": 18, "选择性必修第三册": 19}
    books.sort(key=lambda b: order.get(b["book"], 99))
    out = {"generated": "2026-11-01", "count": sum(b["lessonCount"] for b in books), "books": books}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ {OUT}")
    print(f"册 {len(books)} · 课时 {out['count']}")
    for b in books:
        print(f"  {b['book']}: {b['lessonCount']} 篇（{b['stage']}）")


if __name__ == "__main__":
    main()
