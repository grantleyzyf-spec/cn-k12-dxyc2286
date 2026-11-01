# -*- coding: utf-8 -*-
import json, sys, collections
REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
topics = {x["id"]: x["name"] for x in json.load(open(f"{REPO}/data/math-bj/topics.json", encoding="utf-8"))}

def report(paper, book="四年级上册"):
    d = json.load(open(f"{REPO}/data/math-bj/exams/{book}/{paper}.json", encoding="utf-8"))
    items = [it for s in d["sections"] for it in s["items"]]
    agg = collections.OrderedDict()
    for it in items:
        t = topics[it["topicIds"][0]]
        agg.setdefault(t, 0)
        agg[t] += it["score"]
        print(f"第 {it['no']} 题｜{t}｜{it['score']} 分")
    print("--- totals")
    for t, s in sorted(agg.items(), key=lambda kv: -kv[1]):
        print(f"{s}  {t}")
    print("sum", sum(s for s in agg.values()), "items", len(items),
          "scores", sum(it["score"] for it in items))

if __name__ == "__main__":
    report(sys.argv[1])
