# -*- coding: utf-8 -*-
"""诊断 F1：把每条未命中的题干引文，与教材正文对齐，输出「引文 → 教材原文」候选对。

用法：/usr/bin/python3 scripts/diag_chinese_f1.py [--limit N]
输出：/tmp/cn_f1_pairs.tsv（qid \t 册 \t 引文 \t 教材原文候选 \t 相似度）
"""
import difflib
import importlib.util
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
spec = importlib.util.spec_from_file_location("aud", f"{REPO}/scripts/audit_chinese_quality.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

LIMIT = None
for i, a in enumerate(sys.argv):
    if a == "--limit":
        LIMIT = int(sys.argv[i + 1])


def best_window(pages, frag):
    """在教材正文里找与 frag 最相似的窗口，返回 (相似度, 原文)。"""
    f = A.qnorm(frag)
    if len(f) < 6:
        return 0.0, ""
    # 用前 6 字定位，再在该页 ±120 字窗口里做相似度对齐
    head = f[:4]
    best = (0.0, "")
    for p in pages:
        start = 0
        while True:
            idx = p.find(head, start)
            if idx < 0:
                break
            win = p[max(0, idx - 30): idx + len(f) + 60]
            sm = difflib.SequenceMatcher(None, f, win)
            m = sm.find_longest_match(0, len(f), 0, len(win))
            cand = win[m.b:m.b + max(len(f), m.size)]
            ratio = sm.ratio()
            if ratio > best[0]:
                best = (ratio, cand)
            start = idx + 1
    return best


def main():
    topics = json.load(open(f"{REPO}/data/chinese/topics.json", encoding="utf-8"))
    qs = json.load(open(f"{REPO}/data/chinese/questions.json", encoding="utf-8"))
    by_topic = {}
    for q in qs:
        by_topic.setdefault(q["topicId"], []).append(q)
    books = A.load_book_texts()
    out = []
    n = 0
    for t in topics:
        pref = (t.get("chapter") or "").split(" ")[0]
        pages = books.get(pref)
        if not pages:
            continue
        for q in by_topic.get(t["id"], []):
            for frag in re.findall(r"「([^」]{8,})」", q.get("prompt") or ""):
                frag2 = frag.replace("____", q.get("answer") or "")
                if A.in_book(pages, A.qnorm(frag2)):
                    continue
                ratio, orig = best_window(pages, frag2)
                out.append((q["id"], pref, frag2, orig, round(ratio, 2), q.get("prompt", "")))
                n += 1
                if LIMIT and n >= LIMIT:
                    break
    with open("/tmp/cn_f1_pairs.tsv", "w", encoding="utf-8") as fh:
        fh.write("qid\t册\t引文\t教材原文候选\t相似度\t题干\n")
        for r in out:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"F1 未命中 {len(out)} 条 → /tmp/cn_f1_pairs.tsv")
    for r in out[:12]:
        print(f"[{r[5][:2]}] {r[0]} ({r[4]}) 引文: {r[2][:34]}")
        print(f"     原文: {r[3][:44]}")


if __name__ == "__main__":
    main()
