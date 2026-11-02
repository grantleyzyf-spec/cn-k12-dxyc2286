# -*- coding: utf-8 -*-
"""学层（诊断讲解）站点索引：learn/index.json —— 多学科多版本通用版。

扫描 `data/*/learn/*.json`，按 `data/subject-groups.json` 的
「学科 → 版本」注册关系补齐 subject / subjectName / edition，
生成 `learn/index.json`（learn/learn.js 直接读它做三级级联）。

用法：
    python3 scripts/build_learn_site.py            # 重建
    python3 scripts/build_learn_site.py --check    # 只比对不写（收尾/CI 用）
"""
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
OUT = os.path.join(REPO, "learn", "index.json")

_CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_number(text):
    m = re.search(r"第([一二三四五六七八九十]+)", text or "")
    if not m:
        return 99
    t = m.group(1)
    if "十" not in t:
        return _CN.get(t, 99)
    head, _, tail = t.partition("十")
    return (_CN.get(head, 1) if head else 1) * 10 + (_CN.get(tail, 0) if tail else 0)


_EDITIONS_STRIP = ("苏教版", "苏科版", "人教版", "北师大版", "沪教版", "湘教版", "青岛版", "冀教版", "北京版")


def strip_edition(book):
    """册名去掉版本前缀（站点数据里苏教/苏科等版本的 book 带前缀，其余不带）。"""
    for _pre in _EDITIONS_STRIP:
        if book.startswith(_pre) and len(book) > len(_pre):
            return book[len(_pre):]
    return book

def book_rank(book):
    """册次排序键：学段(1小学/2初中/3高中) + 年级/册序 + 上下册。"""
    book = strip_edition(book)
    m = re.match(r"^([一二三四五六]年级)(上|下)册$", book)
    if m:
        return (1, _CN[m.group(1)[0]], 1 if m.group(2) == "上" else 2)
    m = re.match(r"^([七八九]年级)(上|下)册$", book)
    if m:
        return (2, _CN[m.group(1)[0]], 1 if m.group(2) == "上" else 2)
    m = re.match(r"^必修(上|下)册$", book)
    if m:
        return (3, 1, 1 if m.group(1) == "上" else 2)
    m = re.match(r"^选择性必修(上|中|下)册$", book)
    if m:
        return (3, 2 + {"上": 0, "中": 1, "下": 2}[m.group(1)], 1)
    m = re.match(r"^必修第([一二三四五六])册$", book)
    if m:
        return (3, _CN[m.group(1)], 1)
    m = re.match(r"^选择性必修第([一二三四五六])册$", book)
    if m:
        return (3, 10 + _CN[m.group(1)], 1)
    return (9, 99, 1)


def stage_of(book):
    return {1: "小学", 2: "初中", 3: "高中"}.get(book_rank(book)[0], "高中")


def load_registry():
    reg = json.load(open(os.path.join(DATA, "subject-groups.json"), encoding="utf-8"))
    # 版本名优先取注册表；注册表未收录的版本目录（如在途数据）回退到
    # scripts/build_subjects_registry.py 里的 EDITIONS 映射，避免把「冀教版」标成「人教版」。
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "bsr", os.path.join(REPO, "scripts", "build_subjects_registry.py"))
    bsr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bsr)
    EDITIONS = getattr(bsr, "EDITIONS", {})
    dir2info = {}
    order = {}
    for gi, g in enumerate(reg.get("subjects") or []):
        order[g["id"]] = gi
        for e in g.get("editions") or []:
            dir2info[e["id"]] = (g["id"], g["name"], e.get("name") or EDITIONS.get(e["id"]) or "人教版")
    for dir_id, ed_name in EDITIONS.items():
        if dir_id in dir2info:
            continue
        base = dir_id.split("-")[0]
        if base in order:
            gname = next(x["name"] for x in reg["subjects"] if x["id"] == base)
            dir2info[dir_id] = (base, gname, ed_name)
    return dir2info, order


def build():
    dir2info, order = load_registry()
    books = []
    for f in sorted(glob.glob(os.path.join(DATA, "*", "learn", "*.json"))):
        if os.path.basename(f).startswith("_"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        book = d.get("book")
        # 兼容两种册级 schema：标准 lessons[{topicId,title,markdown,words}]
        # 与心理健康等桶的 items[{topicId,title,han,md}]（同一份内容，键名不同）
        raw = d.get("lessons") or d.get("items") or []
        if not book or not raw:
            continue
        raw = [{"topicId": L.get("topicId"), "title": L.get("title"),
                "words": L.get("words") or L.get("han") or 0} for L in raw]
        d["lessons"] = raw
        dir_id = os.path.basename(os.path.dirname(os.path.dirname(f)))
        subj, sname, edition = dir2info.get(dir_id, (dir_id, dir_id, "人教版"))
        topics = json.load(open(os.path.join(DATA, dir_id, "topics.json"), encoding="utf-8"))
        tmap = {t["id"]: t for t in topics}
        torder = {t["id"]: i for i, t in enumerate(topics)}
        lessons = []
        for L in d["lessons"]:
            ch = (tmap.get(L.get("topicId"), {}) or {}).get("chapter") or ""
            unit = ch.split(" · ")[0]
            if unit.startswith(book + " "):
                unit = unit[len(book) + 1:]
            lessons.append({"topicId": L.get("topicId"), "title": L.get("title"),
                            "chapter": unit, "words": L.get("words") or 0})
        lessons.sort(key=lambda x: (cn_number(x["chapter"]), torder.get(x["topicId"], 10 ** 9)))
        books.append({"book": book, "stage": stage_of(book), "grade": book_rank(book)[1],
                      "subject": subj, "subjectName": sname, "edition": edition,
                      "lessonCount": len(lessons),
                      "path": f"data/{dir_id}/learn/{book}.json",
                      "lessons": lessons})
    books.sort(key=lambda b: (order.get(b["subject"], 99), book_rank(b["book"])))
    return {"generated": "2026-11-02", "count": sum(b["lessonCount"] for b in books), "books": books}


def main():
    out = build()
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        same = json.loads(cur) == json.loads(text) if cur else False
        print("learn/index.json 是否最新：", "是" if same else "否")
        return 0 if same else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    subs = {}
    for b in out["books"]:
        subs.setdefault(b["subjectName"] + "（" + b["edition"] + "）", []).append(b)
    print(f"✅ {OUT} · 册 {len(out['books'])} · 课时 {out['count']}")
    for k, v in subs.items():
        print(f"   {k}: {len(v)} 册 / {sum(x['lessonCount'] for x in v)} 课时")
    return 0


if __name__ == "__main__":
    sys.exit(main())
