#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""politics 文案分片自检：description / mastery_criteria 的质量门禁。

用法: python3 scripts/ddfz_check_copy.py <shard.json> --shard=W01
通过时末行打印 PASS；否则列 FAIL 并退出码 1。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, "data", "politics")

BAD_AI = ("总之", "综上所述", "不仅", "赋能", "抓手", "闭环", "维度", "随着", "值得注意的是",
          "至关重要", "涵盖", "彰显", "助力", "深耕")
TPL = ("核心观点并联系生活实例说明", "本课主要讲了", "本框主要讲了", "旨在帮助", "通过学习，")
VERBS = ("能", "会", "懂得", "知道", "理解", "辨别", "举例", "说明", "运用", "说出", "区分",
         "认识", "体会", "感受", "认同", "掌握", "分析", "判断", "解释", "列举", "做到")


def han(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def main():
    path = sys.argv[1]
    tag = next((a.split("=")[1] for a in sys.argv if a.startswith("--shard=")), None)
    wm = os.path.join(SUB, "_batch", "wen", tag, "WORKER.md")
    want = re.findall(r"\| (pol_p\d+) \|", open(wm, encoding="utf-8").read())
    items = json.load(open(path, encoding="utf-8"))
    got = {x["id"]: x for x in items}
    fails = []
    if set(got) != set(want):
        fails.append("id 不齐：缺 %s，多 %s" % (sorted(set(want) - set(got))[:5],
                                              sorted(set(got) - set(want))[:5]))
    topics = {t["id"]: t for t in json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))}
    for pid in want:
        x = got.get(pid)
        if not x:
            continue
        d = (x.get("description") or "").strip()
        ms = x.get("mastery_criteria") or []
        t = topics[pid]
        if not (40 <= han(d) <= 90):
            fails.append("%s description 汉字 %d（要 40–90）" % (pid, han(d)))
        if d == t["name"]:
            fails.append("%s description 等于 name" % pid)
        for w in TPL:
            if w in d:
                fails.append("%s description 含模板句「%s」" % (pid, w))
        for w in BAD_AI:
            if w in d:
                fails.append("%s description 含 AI 腔词「%s」" % (pid, w))
        if not (2 <= len(ms) <= 3):
            fails.append("%s mastery_criteria %d 条（要 2–3）" % (pid, len(ms)))
        for m in ms:
            if not (15 <= han(m) <= 50):
                fails.append("%s 掌握标准汉字 %d（要 15–50）：%s" % (pid, han(m), m[:20]))
            if not m.startswith(VERBS):
                fails.append("%s 掌握标准未以行为动词开头：%s" % (pid, m[:16]))
            for w in BAD_AI:
                if w in m:
                    fails.append("%s 掌握标准含 AI 腔词「%s」" % (pid, w))
        if len({m.strip() for m in ms}) != len(ms):
            fails.append("%s 掌握标准有重复条目" % pid)

    print("分片 %s：%d/%d 点" % (tag, len(got), len(want)))
    if fails:
        for f in fails[:25]:
            print("  ❌", f)
        print("FAILED %d" % len(fails))
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
