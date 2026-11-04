#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普版地理：题库分片生成（一章一片）。

- 课时点 8 题：q01/q02 choice(basic)、q03/q04 choice(standard)、q05 fill(basic)、q06 fill(standard)、q07 short-answer(hard)、q08 numeric(standard，带 verify)
- 单元点 5 题：q01/q02 choice、q03 fill、q04 numeric(带 verify)、q05 short-answer
"""
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-kepu")
SD = os.path.join(D, "_bank_shards")
os.makedirs(SD, exist_ok=True)

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
groups = {}
for t in topics:
    m = re.match(r"^(.+?) (第[一二三四五六七八九十]+单元) ", t["chapter"])
    if not m:
        continue
    key = (m.group(1), m.group(2))
    groups.setdefault(key, []).append(t)

index = []
for i, ((book, chap), pts) in enumerate(sorted(groups.items()), 1):
    chap_title = pts[0]["chapter"].split(" · ")[0]
    tag = f"GKP_B{i:02d}"
    items = []
    for t in pts:
        if t["level"] == "unit":
            slots = [("q01", "choice", "basic"), ("q02", "choice", "standard"), ("q03", "fill", "basic"),
                     ("q04", "numeric", "standard"), ("q05", "short-answer", "hard")]
        else:
            slots = [("q01", "choice", "basic"), ("q02", "choice", "basic"),
                     ("q03", "choice", "standard"), ("q04", "choice", "standard"),
                     ("q05", "fill", "basic"), ("q06", "fill", "standard"),
                     ("q07", "short-answer", "hard"), ("q08", "numeric", "standard")]
        items.append({
            "topicId": t["id"], "name": t["name"], "level": t["level"],
            "chapter": t["chapter"], "description": t.get("description", ""),
            "mastery_criteria": t.get("mastery_criteria", []),
            "slots": [{"id": f"{t['id']}_{s[0]}", "type": s[1], "difficulty": s[2]} for s in slots],
        })
    payload = {"shard": tag, "subject": "geography-kepu", "book": book, "chapter": chap_title,
               "items": items,
               "out": f"data/geography-kepu/_bank/{tag}.json"}
    json.dump(payload, open(os.path.join(SD, f"{tag}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    index.append({"shard": tag, "book": book, "chapter": chap_title,
                  "points": len(items), "questions": sum(len(x["slots"]) for x in items)})

json.dump(index, open(os.path.join(SD, "_INDEX.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"分片 {len(index)} 个 / 题 {sum(x['questions'] for x in index)}")
for x in index:
    print(f"  {x['shard']} {x['book']:6} {x['chapter']:22} 点{x['points']:2} 题{x['questions']:3}")
