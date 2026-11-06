#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 physics-hushuke（沪科技版高中物理）外科式插条进站点三份索引 + 前端讲解包。

基座一律取 `git show HEAD:<path>`（已提交版），只替换本桶条目，其余桶原样保留。
可重跑：每次先删本桶旧条再插，不会重复计数。
"""
import json
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = "physics-hushuke"
SUBJECT = "physics"
SUBJECT_NAME = "物理"
EDITION = "沪科技版"
BOOKS = ["必修第一册", "必修第二册", "必修第三册",
         "选择性必修第一册", "选择性必修第二册", "选择性必修第三册"]
GRADE = {"必修第一册": 1, "必修第二册": 2, "必修第三册": 3,
         "选择性必修第一册": 11, "选择性必修第二册": 12, "选择性必修第三册": 13}
GRADE10 = {"必修第一册": 10, "必修第二册": 10, "必修第三册": 11,
           "选择性必修第一册": 11, "选择性必修第二册": 12, "选择性必修第三册": 12}


BASE_REF = os.environ.get("BASE_REF", "HEAD")


def head_json(path):
    out = subprocess.run(["git", "show", f"{BASE_REF}:{path}"], cwd=REPO,
                         capture_output=True, check=True)
    return json.loads(out.stdout.decode("utf-8"))


def dump(path, obj):
    p = os.path.join(REPO, path)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, p)


def learn_books():
    rows = []
    for b in BOOKS:
        src = os.path.join(REPO, "data", BUCKET, "learn", f"{b}.json")
        if not os.path.exists(src):
            continue
        d = json.load(open(src, encoding="utf-8"))
        lessons = [{"topicId": l["topicId"], "title": l["title"],
                    "chapter": l.get("chapter", ""), "words": l["words"]}
                   for l in d["lessons"]]
        rows.append({"book": b, "stage": "高中", "grade": GRADE[b],
                     "subject": SUBJECT, "subjectName": SUBJECT_NAME,
                     "edition": EDITION, "lessonCount": len(lessons),
                     "path": f"data/{BUCKET}/learn/{b}.json",
                     "lessons": lessons})
    return rows


def exam_rows():
    rows, packs = [], []
    for b in BOOKS:
        d = os.path.join(REPO, "data", BUCKET, "exams", b)
        if not os.path.isdir(d):
            continue
        papers = []
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            ex = json.load(open(os.path.join(d, fn), encoding="utf-8"))
            lect_path = os.path.join(REPO, "data", BUCKET, "exam_lectures", b, fn)
            if not os.path.exists(lect_path):
                continue
            lect = json.load(open(lect_path, encoding="utf-8"))
            papers.append({"paper": ex["paper"], "kind": ex["kind"],
                           "examId": ex["examId"], "words": lect["words"],
                           "fullScore": ex["fullScore"], "duration": ex["duration"],
                           "items": sum(len(s["items"]) for s in ex["sections"])})
        if not papers:
            continue
        rows.append({"book": b, "path": f"data/{BUCKET}-{b}.json",
                     "subject": SUBJECT, "subjectName": SUBJECT_NAME,
                     "edition": EDITION, "stage": "高中",
                     "paperCount": len(papers), "papers": papers})
        packs.append((b, papers))
    return rows, packs


def exam_meta():
    """diagnose/exam-index.json 的 exams 条目。"""
    meta = {}
    for b in BOOKS:
        d = os.path.join(REPO, "data", BUCKET, "exams", b)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            ex = json.load(open(os.path.join(d, fn), encoding="utf-8"))
            meta[ex["examId"]] = {
                "examId": ex["examId"], "subject": BUCKET,
                "path": f"exams/{b}/{fn}", "book": b, "paper": ex["paper"],
                "kind": ex["kind"], "grade": GRADE10[b], "stage": "高中",
                "edition": EDITION, "duration": ex["duration"],
                "fullScore": ex["fullScore"], "scope": ex["scope"],
                "itemCount": sum(len(s["items"]) for s in ex["sections"])}
    return meta


def main():
    lb = learn_books()
    # 1) learn/index.json
    idx = head_json("learn/index.json")
    keep = [x for x in idx["books"] if BUCKET not in x.get("path", "")]
    idx["books"] = keep + lb
    idx["count"] = sum(x.get("lessonCount", 0) for x in idx["books"])
    dump("learn/index.json", idx)
    print(f"learn/index.json: {len(keep)} → {len(idx['books'])} 册 / {idx['count']} 课时")

    # 2) learn/exam/index.json
    er, packs = exam_rows()
    eidx = head_json("learn/exam/index.json")
    ekeep = [x for x in eidx["books"] if BUCKET not in x.get("path", "")]
    eidx["books"] = ekeep + er
    eidx["count"] = sum(x.get("paperCount", 0) for x in eidx["books"])
    dump("learn/exam/index.json", eidx)
    print(f"learn/exam/index.json: {len(ekeep)} → {len(eidx['books'])} 册 / {eidx['count']} 卷")

    # 3) 前端讲解包
    os.makedirs(os.path.join(REPO, "learn", "exam", "data"), exist_ok=True)
    for b, papers in packs:
        full = []
        for p in papers:
            lect = json.load(open(os.path.join(
                REPO, "data", BUCKET, "exam_lectures", b, f"{p['paper']}.json"),
                encoding="utf-8"))
            full.append({"paper": p["paper"], "kind": p["kind"], "examId": p["examId"],
                         "words": p["words"], "markdown": lect["markdown"]})
        dump(f"learn/exam/data/{BUCKET}-{b}.json", {"book": b, "papers": full})
    print(f"前端讲解包 {len(packs)} 册")

    # 4) diagnose/exam-index.json
    meta = exam_meta()
    g = head_json("diagnose/exam-index.json")
    old = {k: v for k, v in g["exams"].items() if v.get("subject") != BUCKET}
    g["exams"] = dict(old)
    g["exams"].update(meta)
    g["count"] = len(g["exams"])
    g["subjects"][BUCKET] = {"count": len(meta), "editions": [EDITION],
                             "defaultEdition": EDITION}
    dump("diagnose/exam-index.json", g)
    print(f"diagnose/exam-index.json: {len(old)} → {len(g['exams'])} 卷；subjects {len(g['subjects'])} 版")


if __name__ == "__main__":
    main()
