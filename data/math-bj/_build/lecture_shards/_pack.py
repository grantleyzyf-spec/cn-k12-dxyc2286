# -*- coding: utf-8 -*-
"""把 _md/<book>_<paper>.md 包成交付 JSON 并落盘。"""
import json, os, sys
REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
SHARD = os.path.dirname(os.path.abspath(__file__))

def build(book, paper):
    shard = json.load(open(f"{SHARD}/T14.json", encoding="utf-8"))
    meta = next(p for p in shard["papers"] if p["paper"] == paper and p["book"] == book)
    md = open(f"{SHARD}/_md/{book}_{paper}.md", encoding="utf-8").read()
    out = {"examId": meta["examId"], "book": book, "paper": paper,
           "kind": meta["kind"], "markdown": md}
    d = f"{REPO}/data/math-bj/exam_lectures/{book}"
    os.makedirs(d, exist_ok=True)
    p = f"{d}/{paper}.json"
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", p)

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
