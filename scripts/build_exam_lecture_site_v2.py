# -*- coding: utf-8 -*-
"""试卷讲解站点数据（多学科通用版）。

产出：
    learn/exam/index.json            册列表 + 每册的卷清单（不含正文）
    learn/exam/data/<册>.json        正文（数学沿用旧文件名）
    learn/exam/data/<学科>-<册>.json  其他学科的正文（避免同名册互相覆盖）

扫描 `data/<学科目录>/exam_lectures/<册>/*.json`，与同目录 `exams/<册>/` 对照取
fullScore / duration / 题数；subject / subjectName / edition 取自
`data/subject-groups.json`（回退 `scripts/build_subjects_registry.py` 的 EDITIONS）。

用法：python3 scripts/build_exam_lecture_site_v2.py [--check]
"""
import glob
import importlib.util
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
OUT_DIR = os.path.join(REPO, "learn", "exam")
INDEX = os.path.join(OUT_DIR, "index.json")


def registry():
    reg = json.load(open(os.path.join(DATA, "subject-groups.json"), encoding="utf-8"))
    spec = importlib.util.spec_from_file_location(
        "bsr", os.path.join(REPO, "scripts", "build_subjects_registry.py"))
    bsr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bsr)
    ED = getattr(bsr, "EDITIONS", {})
    info, order = {}, {}
    for gi, g in enumerate(reg.get("subjects") or []):
        order[g["id"]] = gi
        for e in g.get("editions") or []:
            info[e["id"]] = (g["id"], g["name"], e.get("name") or ED.get(e["id"]) or "人教版")
    for d, name in ED.items():
        if d in info:
            continue
        base = d.split("-")[0]
        if base in order:
            info[d] = (base, next(x["name"] for x in reg["subjects"] if x["id"] == base), name)
    return info, order


BOOK_RANK = {}

_CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_number(text):
    """「第三单元测试卷」→ 3；「期中测试卷A」等无数号 → 99（同类内部再按名字排）。"""
    import re
    m = re.search(r"第([一二三四五六七八九十]+)", text or "")
    if not m:
        return 99
    t = m.group(1)
    if "十" not in t:
        return _CN.get(t, 99)
    head, _, tail = t.partition("十")
    return (_CN.get(head, 1) if head else 1) * 10 + (_CN.get(tail, 0) if tail else 0)


def book_key(book):
    if book not in BOOK_RANK:
        import re
        CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
        m = re.match(r"^([一二三四五六])年级(上|下)册$", book)
        if m:
            BOOK_RANK[book] = (1, CN[m.group(1)[0]], 0 if m.group(2) == "上" else 1)
        else:
            m = re.match(r"^([七八九])年级(上|下)册$", book)
            if m:
                BOOK_RANK[book] = (2, CN[m.group(1)[0]], 0 if m.group(2) == "上" else 1)
            else:
                m = re.match(r"^必修(上|下)册$", book)
                if m:
                    BOOK_RANK[book] = (3, 1, 0 if m.group(1) == "上" else 1)
                else:
                    m = re.match(r"^选择性必修(上|中|下)册$", book)
                    if m:
                        BOOK_RANK[book] = (3, 2 + {"上": 0, "中": 1, "下": 2}[m.group(1)], 0)
                    else:
                        BOOK_RANK[book] = (9, 99, 0)
    return BOOK_RANK[book]


def stage_of(book):
    return {1: "小学", 2: "初中", 3: "高中"}.get(book_key(book)[0], "高中")


def build():
    info, order = registry()
    books = []
    for sub_dir in sorted(glob.glob(os.path.join(DATA, "*"))):
        if not os.path.isdir(sub_dir):
            continue
        dir_id = os.path.basename(sub_dir)
        lec_root = os.path.join(sub_dir, "exam_lectures")
        if not os.path.isdir(lec_root):
            continue
        subject, sname, edition = info.get(dir_id, (dir_id, dir_id, "人教版"))
        for book_dir in sorted(glob.glob(os.path.join(lec_root, "*"))):
            if not os.path.isdir(book_dir):
                continue
            book = os.path.basename(book_dir)
            papers, bundle = [], []
            for f in sorted(glob.glob(os.path.join(book_dir, "*.json"))):
                L = json.load(open(f, encoding="utf-8"))
                exam_f = os.path.join(sub_dir, "exams", book, f"{L.get('paper')}.json")
                full = dur = items = None
                if os.path.exists(exam_f):
                    E = json.load(open(exam_f, encoding="utf-8"))
                    full = E.get("fullScore")
                    dur = E.get("duration")
                    items = sum(len(s["items"]) for s in E.get("sections") or [])
                papers.append({"paper": L.get("paper"), "kind": L.get("kind"),
                               "examId": L.get("examId"), "words": L.get("words"),
                               "fullScore": full, "duration": dur, "items": items})
                bundle.append({"paper": L.get("paper"), "kind": L.get("kind"),
                               "examId": L.get("examId"), "words": L.get("words"),
                               "markdown": L.get("markdown")})
            # 中文序号绝不能按字符排（一<三<二<五<四）：单元卷按 cn_number，kind 顺序 unit→mid→fin
            kind_rank = {"unit": 0, "midterm": 1, "mid": 1, "final": 2, "fin": 2}
            papers.sort(key=lambda p: (kind_rank.get(p.get("kind"), 9), cn_number(p.get("paper"))))
            bundle.sort(key=lambda p: (kind_rank.get(p.get("kind"), 9), cn_number(p.get("paper"))))
            if not papers:
                continue
            fname = f"{book}.json" if dir_id == "math" else f"{dir_id}-{book}.json"
            books.append({
                "book": book, "path": f"data/{fname}", "subject": subject,
                "subjectName": sname, "edition": edition, "stage": stage_of(book),
                "paperCount": len(papers), "papers": papers,
                "_bundle": {"book": book, "papers": bundle}, "_fname": fname,
            })
    books.sort(key=lambda b: (order.get(b["subject"], 99), book_key(b["book"])))
    return books


def main():
    books = build()
    bundles = [(b.pop("_fname"), b.pop("_bundle")) for b in books]
    index = {"books": books, "count": sum(b["paperCount"] for b in books), "updated": "2026-11-02"}
    os.makedirs(os.path.join(OUT_DIR, "data"), exist_ok=True)
    if "--check" in sys.argv:
        print("讲解索引检查：册", len(books), "卷", index["count"])
        return 0
    for fname, bundle in bundles:
        with open(os.path.join(OUT_DIR, "data", fname), "w", encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False, indent=1)
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"✅ {INDEX} · 册 {len(books)} · 卷 {index['count']}")
    key = {}
    for b in books:
        key.setdefault(b["subjectName"] + "（" + b["edition"] + "）", []).append(b["paperCount"])
    for k, v in key.items():
        print(f"   {k}: {len(v)} 册 / {sum(v)} 卷")
    return 0


if __name__ == "__main__":
    sys.exit(main())
