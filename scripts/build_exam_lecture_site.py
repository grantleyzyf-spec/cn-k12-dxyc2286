# -*- coding: utf-8 -*-
"""试卷讲解站点数据：卷 → 讲解。

产出：
    lectures/index.json          册列表 + 每册的卷清单（不含正文）
    lectures/data/<册>.json      正文（按卷名索引）
"""
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
LEC = f"{REPO}/data/math/exam_lectures"
EXAMS = f"{REPO}/data/math/exams"
OUT = f"{REPO}/lectures"


# 中文章序 → 数值（⚠️ 绝不能按字符比：'七'<'五'、'六' 都在 二三四五 之前）
_CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9}


def cn_number(text):
    """从「第X单元」「第X章」「第X课」里取出 X 的数值；「十一」「二十三」这类也认。"""
    m = re.search(r"第([一二三四五六七八九十]+)", text or "")
    if not m:
        return 99
    t = m.group(1)
    if "十" not in t:
        return _CN_DIGIT.get(t, 99)
    head, _, tail = t.partition("十")
    tens = _CN_DIGIT.get(head, 1) if head else 1
    ones = _CN_DIGIT.get(tail, 0) if tail else 0
    return tens * 10 + ones


def paper_rank(p):
    """卷序：单元卷按单元号升序（第1→第2→…），期中 A/B、期末 A/B 排在单元卷之后。"""
    kind = {"unit": 0, "mid": 1, "fin": 2}.get(p.get("kind"), 3)
    tail = 0
    if kind in (1, 2):
        tail = {"A": 0, "B": 1}.get((p.get("paper") or "")[-1], 0)
    return (kind, cn_number(p.get("paper")), tail, p.get("paper") or "")

STAGE_ORDER = ["小学", "初中", "高中"]
BOOK_ORDER = [
    "一年级上册", "一年级下册", "二年级上册", "二年级下册",
    "三年级上册", "三年级下册", "四年级上册",
    "五年级上册", "六年级上册",
    "七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册",
    "必修第一册", "必修第二册",
    "选择性必修第一册", "选择性必修第二册", "选择性必修第三册",
]


def kind_of(name):
    if "期中" in name:
        return "mid"
    if "期末" in name:
        return "fin"
    return "unit"


def han(t):
    return len(re.findall(r"[\u4e00-\u9fa5]", t))


def main():
    os.makedirs(f"{OUT}/data", exist_ok=True)
    books = []
    total = 0
    for f in sorted(glob.glob(f"{LEC}/*/*.json")):
        lec = json.load(open(f, encoding="utf-8"))
        book = lec["book"]
        # 卷面元信息（满分/时长/题量）
        exf = f"{EXAMS}/{book}/{lec['paper']}.json"
        meta = {}
        if os.path.exists(exf):
            ex = json.load(open(exf, encoding="utf-8"))
            meta = {
                "fullScore": ex.get("fullScore"),
                "duration": ex.get("duration"),
                "items": sum(len(s["items"]) for s in ex["sections"]),
            }
        entry = {
            "paper": lec["paper"],
            "kind": lec.get("kind") or kind_of(lec["paper"]),
            "examId": lec.get("examId"),
            "words": han(lec.get("markdown", "")),
            **meta,
        }
        b = next((x for x in books if x["book"] == book), None)
        if b is None:
            b = {"book": book, "papers": [], "path": f"data/{book}.json"}
            books.append(b)
        b["papers"].append(entry)
        total += 1

    # 排序要在落盘之前：页面渲染读的是 data/<册>.json 的数组顺序
    for b in books:
        b["papers"].sort(key=paper_rank)

    # 每册正文单独落盘
    for b in books:
        payload = {"book": b["book"], "papers": []}
        for e in b["papers"]:
            lec = json.load(open(f"{LEC}/{b['book']}/{e['paper']}.json", encoding="utf-8"))
            payload["papers"].append({
                "paper": e["paper"],
                "kind": e["kind"],
                "examId": e["examId"],
                "markdown": lec.get("markdown", ""),
            })
        json.dump(payload, open(f"{OUT}/{b['path']}", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    # 册序：学段（小学→初中→高中）→ 册
    def book_rank(name):
        return BOOK_ORDER.index(name) if name in BOOK_ORDER else 99

    for b in books:
        b["paperCount"] = len(b["papers"])
        b["stage"] = "小学" if "年级" in b["book"] and b["book"][0] in "一二三四五六" else (
            "初中" if "年级" in b["book"] else "高中")
    books.sort(key=lambda b: (STAGE_ORDER.index(b["stage"]), book_rank(b["book"])))

    idx = {"books": books, "count": total,
           "updated": __import__("datetime").date.today().isoformat()}
    json.dump(idx, open(f"{OUT}/index.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"✅ {OUT}/index.json：{len(books)} 册 · {total} 份试卷讲解")


if __name__ == "__main__":
    main()
