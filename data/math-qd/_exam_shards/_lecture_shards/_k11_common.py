# -*- coding: utf-8 -*-
"""K11 青岛版三年级上册试卷讲解装配器：结构性数字全部由卷面现算。"""
import json
import os
import re
import sys

REPO = "/Users/a627692/Desktop/cn-k12-dxyc2286"
TOPICS = {t["id"]: t["name"] for t in json.load(open(f"{REPO}/data/math-qd/topics.json", encoding="utf-8"))}
STEPS = ["每天锻炼一个小时", "扎实掌握第一个知识点", "能积微者速成",
         "运用对标思维突破学习困境", "运用杠铃法则缓解学习疲劳"]
DIFF = {"basic": "基础", "standard": "中档", "medium": "中档", "hard": "较难"}


def han(t):
    return len(re.findall(r"[\u4e00-\u9fa5]", t))


def sec_block(title):
    for s in title:
        pass


def build(exam_path, C, out_path=None):
    ex = json.load(open(exam_path, encoding="utf-8"))
    items = [it for s in ex["sections"] for it in s["items"]]
    by_no = {it["no"]: it for it in items}

    # ---- 一、这份卷在考什么 ----
    struct = []
    for i, s in enumerate(ex["sections"], 1):
        nm = s["title"]
        struct.append(f"{nm} {len(s['items'])} 小题共 {sum(x['score'] for x in s['items'])} 分")
    dcount = {}
    for it in items:
        d = DIFF.get(it.get("difficulty"), "中档")
        dcount.setdefault(d, [0, 0])
        dcount[d][0] += 1
        dcount[d][1] += it["score"]
    dline = "、".join(f"{k} {v[0]} 题 {v[1]} 分" for k, v in dcount.items())
    sec1 = (f"满分 {ex['fullScore']} 分，考试时间 {ex['duration']} 分钟。全卷 {len(items)} 道小题，"
            f"分成五个大题：" + "；".join(struct) + "。难度分布是 " + dline + "。\n\n" + C["lead"])

    # ---- 二、考点地图 ----
    groups = {}
    for it in items:
        for tid in it.get("topicIds", []):
            groups.setdefault(tid, []).append(it)
    lines = []
    total = 0
    for tid, its in groups.items():
        nos = "、".join(f"第 {x['no']} 题" for x in its)
        tot = sum(x["score"] for x in its)
        total += tot
        name = TOPICS.get(tid, tid)
        dep = C["depths"].get(tid, "").replace("\n- ", "\n　　· ")
        lines.append(f"- {nos}｜{name}｜{tot} 分。{dep}")
    note = ("本卷每个课时点的分值相加正好等于满分，说明一题只挂一个点，看行就看全了。"
            if total == ex["fullScore"] else
            f"本卷各课时点分值相加得 {total} 分，超过满分 {ex['fullScore']} 分，"
            "因为有些题同时挂着两个课时点，重复计了一次；对照题号看单行就行。")
    sec2 = note + "\n\n" + "\n".join(lines)

    # ---- 三、逐题精讲 ----
    blocks = []
    for it in items:
        no = it["no"]
        ic = C["items"][no]
        head = f"### 第 {no} 题（{it['score']} 分）　{it['stem'].split('：')[0][:26]}"
        parts = [head, f"**思路**：{ic['idea']}", f"**关键一步**：{ic['key']}", f"**易错**：{ic['err']}"]
        if it["type"] == "choice":
            opts = ic.get("opts") or {}
            if opts:
                parts.append("**干扰项**：" + "；".join(f"{k} 项 {v}" for k, v in opts.items()))
        if it["type"] == "solve" and it.get("scoreRule"):
            steps = it["scoreRule"]
            txt = "；".join(f"{s.get('step') or s.get('desc')} 得 {s['score']} 分" for s in steps)
            assert sum(s["score"] for s in steps) == it["score"], (no, steps)
            parts.append(f"**分步给分**：{txt}，合计 {it['score']} 分")
        if ic.get("more"):
            parts.append(f"**再想一层**：{ic['more']}")
        blocks.append("\n\n".join(parts))
    sec3 = "\n\n".join(blocks)

    # ---- 四、整卷复盘 ----
    sec4 = C["review"]

    # ---- 五、五步学习法 ----
    five = []
    for lab, body in zip(STEPS, C["five"]):
        five.append(f"**{lab}**\n\n{body}")
    sec5 = "\n\n".join(five)

    # ---- 六、自查清单 ----
    sec6 = "\n".join(f"- [ ] {c}" for c in C["checks"])

    md = (f"# {ex['paper']} · 讲解\n\n"
          f"## 一、这份卷在考什么\n\n{sec1}\n\n"
          f"## 二、考点地图\n\n{sec2}\n\n"
          f"## 三、逐题精讲\n\n{sec3}\n\n"
          f"## 四、整卷复盘\n\n{sec4}\n\n"
          f"## 五、五步学习法\n\n{sec5}\n\n"
          f"## 六、自查清单\n\n{sec6}\n")

    # 自检：< 后接 ASCII 字母会被当标签；单字母单位紧贴汉字
    bad = re.findall(r"<[a-zA-Z/][^>]*>", md)
    single = re.findall(r"(?<![\d.])[0-9]+(?:\.[0-9]+)?([msgLANJWVh])(?=[\u4e00-\u9fa5，。；、])", md)
    multi = re.findall(r"(?<![\d.])[0-9]+(?:\.[0-9]+)?(kg|km|cm|mm|mL|Pa|Hz|min)(?![A-Za-z])", md)
    if bad or single or multi:
        print("⚠ 公式写法隐患", bad[:3], single[:5], multi[:5])
    n = han(md)
    sec = {k: han(v) for k, v in (("一", sec1), ("二", sec2), ("三", sec3), ("四", sec4),
                                  ("五", sec5), ("六", sec6))}
    if out_path:
        lec = {"examId": ex["examId"], "book": ex["book"], "paper": ex["paper"],
               "kind": ex["kind"], "markdown": md, "words": n}
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        json.dump(lec, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{ex['paper']} 汉字 {n} 各节 {sec} 精讲占比 {han(sec3)/n:.0%}")
    assert 3500 <= n <= 7200, f"字数 {n} 出带"
    return md
