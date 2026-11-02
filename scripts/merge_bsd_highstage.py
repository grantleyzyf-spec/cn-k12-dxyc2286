#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""增量合并 `_bank/*.json` 到 topics.json / questions.json —— 只 upsert，不重建。

与 `merge_bsd_bank.py` 的区别（**这个区别很重要**）：
`merge_bsd_bank.py` 用 `_bank/` 全量重建 questions.json，会抹掉并行的其它工位
（小学各册的 `_bank_out/`）已经合进 questions.json 的题。本脚本走增量：
- topics：只把 bank 里的内容字段（description / mastery_criteria / type / diagnostic_question）填进**已存在**的 topic；
- questions：按 id upsert（同 id 覆盖、新 id 追加），其余题原样保留；
- 落盘前打印「保留 N / 新增 M / 覆盖 K」，并断言总数 = 原有 + 新增。

用法:
  python3 scripts/merge_bsd_highstage.py            # 预览
  python3 scripts/merge_bsd_highstage.py --write
"""
import argparse, glob, json, os
from collections import Counter

TOPIC_FILL = ("description", "mastery_criteria", "type", "diagnostic_question")
Q_FIELDS = ["id", "topicId", "prompt", "question", "options", "choices", "answer", "type",
            "difficulty", "explanation", "verify", "keypoints"]


def norm_q(q):
    d = {k: q[k] for k in Q_FIELDS if k in q}
    d["choices"] = d.get("options", []) if d.get("type") == "choice" else []
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/math-bsd")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    topics = json.load(open(f"{a.root}/topics.json", encoding="utf-8"))
    questions = json.load(open(f"{a.root}/questions.json", encoding="utf-8"))
    T = {t["id"]: t for t in topics}

    banks = sorted(glob.glob(f"{a.root}/_bank/*.json"))
    filled, unused_t, incoming, bad_topic = 0, [], {}, []
    for bp in banks:
        b = json.load(open(bp, encoding="utf-8"))
        for t in b.get("topics") or []:
            if t["id"] not in T:
                unused_t.append((os.path.basename(bp), t["id"]))
                continue
            hit = False
            for k in TOPIC_FILL:
                if t.get(k):
                    T[t["id"]][k] = t[k]
                    hit = True
            filled += 1 if hit else 0
        for q in b.get("questions") or []:
            if q.get("topicId") not in T:
                bad_topic.append((os.path.basename(bp), q["id"], q.get("topicId")))
                continue
            incoming[q["id"]] = norm_q(q)

    have = {q["id"] for q in questions}
    new_ids = [i for i in incoming if i not in have]
    over_ids = [i for i in incoming if i in have]

    kept = [q for q in questions if q["id"] not in incoming]      # 别人的题原样保留
    merged = kept + [incoming[i] for i in incoming]
    merged.sort(key=lambda x: (x["topicId"], x["id"]))

    print(f"分片 {len(banks)} 个｜topics 填内容 {filled} 点｜bank 题 {len(incoming)} 道")
    print(f"题库：原有 {len(questions)} → 保留 {len(kept)} ＋ 新增 {len(new_ids)} "
          f"＋ 覆盖同 id {len(over_ids)} ＝ {len(merged)}")
    print("题型:", dict(Counter(q["type"] for q in merged)))
    print("难度:", dict(Counter(q["difficulty"] for q in merged)))
    by_t = Counter(q["topicId"] for q in merged)
    noq = [t for t in T if by_t.get(t, 0) == 0]
    short = [t for t in T if 0 < by_t.get(t, 0) < 8]
    nod = [t for t in T if not T[t].get("description")]
    print(f"无题点 {len(noq)}｜题量<8 {len(short)}｜缺内容点 {len(nod)}")
    if unused_t:
        print("⚠️ bank 里不属于本库的 topicId:", unused_t[:5])
    if bad_topic:
        print("⚠️ 题挂到不存在的 topicId:", bad_topic[:5])

    if a.write:
        assert len(merged) == len(kept) + len(incoming)
        json.dump(merged, open(f"{a.root}/questions.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        open(f"{a.root}/questions.json", "a", encoding="utf-8").write("\n")
        json.dump(list(T.values()), open(f"{a.root}/topics.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        open(f"{a.root}/topics.json", "a", encoding="utf-8").write("\n")
        print(f"written: questions {len(merged)} 道 / topics {len(T)} 点")


if __name__ == "__main__":
    main()
