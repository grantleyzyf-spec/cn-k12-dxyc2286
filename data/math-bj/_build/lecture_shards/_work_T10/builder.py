# -*- coding: utf-8 -*-
"""T10 讲解渲染器：把卷面 JSON + 手写内容字典 → exam_lectures/<册>/<paper>.json"""
import importlib
import json
import os
import re
import sys

BASE = "/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-bj"
OUT = f"{BASE}/exam_lectures"
TOPICS = {t["id"]: t for t in json.load(open(f"{BASE}/topics.json", encoding="utf-8"))}
SHORT = {"整理与复习": "整理与复习（乘加综合）"}

HEAD = ["## 一、这份卷在考什么", "## 二、考点地图", "## 三、逐题精讲",
        "## 四、整卷复盘", "## 五、五步学习法：这份卷怎么吃透", "## 六、自查清单"]
STEPS = ["①每天锻炼一个小时", "②扎实掌握第一个知识点", "③能积微者速成",
         "④运用对标思维突破学习困境", "⑤运用杠铃法则缓解学习疲劳"]


def tname(it):
    ns = []
    for t in it.get("topicIds", []):
        n = TOPICS.get(t, {}).get("name", t)
        ns.append(SHORT.get(n, n))
    return "、".join(ns) or "综合运用"


def para(xs):
    out = []
    for x in xs:
        out.append(x)
        out.append("")
    return out


def render(meta, c):
    exam = json.load(open(meta["path"], encoding="utf-8"))
    items = [it for s in exam["sections"] for it in s["items"]]
    by_no = {it["no"]: it for it in items}

    L = []
    L.append(f"# {meta['book']} {meta['paper']}　试卷讲解")
    L.append("")
    L.append(HEAD[0])
    L.append("")
    L.extend(para(c["s1"]))
    L.append("")
    L.append(HEAD[1])
    L.append("")
    agg = {}
    for it in items:
        for t in it.get("topicIds", []):
            agg[t] = agg.get(t, 0) + it["score"]
    for it in items:
        L.append(f"- 第 {it['no']} 题｜{tname(it)}｜{it['score']} 分")
    L.append("")
    top = sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    tot = sum(v for _, v in top)
    t3 = "、".join(
        f"{SHORT.get(TOPICS[k]['name'], TOPICS[k]['name'])}（{v} 分）" for k, v in top)
    if len(top) >= 3:
        L.append(f"最重的三个考点：{t3}，合计 {tot} 分。")
    elif len(top) == 2:
        L.append(f"这份卷只覆盖两个考点：{t3}，两块合起来正好是整卷的 {tot} 分，缺一块就没分了。")
    else:
        L.append(f"这份卷只考一个考点：{t3}，全卷 {tot} 分都在这一处。")
    L.append("")
    L.append(HEAD[2])
    L.append("")
    for s in exam["sections"]:
        L.append(f"### {s['title']}" + (f"（{s['desc']}）" if s.get("desc") else ""))
        L.append("")
        for it in s["items"]:
            no = it["no"]
            th, key, err = c["items"][no]
            L.append(f"#### 第 {no} 题（{it['score']} 分）")
            L.append("")
            L.append(f"**思路**：{th}")
            L.append("")
            L.append(f"**关键一步**：{key}")
            L.append("")
            L.append(f"**易错**：{err}")
            L.append("")
    L.append(HEAD[3])
    L.append("")
    L.extend(para(c["s4"]))
    L.append("")
    L.append(HEAD[4])
    L.append("")
    for i, (lab, txt) in enumerate(c["s5"]):
        assert lab == STEPS[i], (lab, STEPS[i])
        L.append(f"**{lab}**：{txt}")
        L.append("")
    L.append(HEAD[5])
    L.append("")
    for x in c["s6"]:
        L.append(f"- [ ] {x}")
    L.append("")
    md = "\n".join(L)

    # 自检
    errs = []
    for no in by_no:
        if no not in c["items"]:
            errs.append(f"缺第 {no} 题讲解")
    for pat, why in [(r"\$", "LaTeX 美元"), (r"\\frac|\\sqrt|\\times", "LaTeX 命令"),
                     (r"<[a-zA-Z/][^>]*>", "HTML 标签"), (r"\|\s*-{3,}", "Markdown 表格")]:
        if re.search(pat, md):
            errs.append(why)
    for bad in ("分五段", "按五段", "五个部分"):
        if bad in md:
            errs.append(bad)
    n = len(re.findall(r"[\u4e00-\u9fa5]", md))
    if errs:
        print("!!", meta["paper"], errs)
    return md, n


def main():
    shard = json.load(open(sys.argv[1], encoding="utf-8"))
    mod = importlib.import_module(os.path.splitext(os.path.basename(sys.argv[2]))[0])
    sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[2])))
    total = 0
    for p in shard["papers"]:
        if p["examId"] not in mod.CONTENT:
            print(f"-- 跳过 {p['paper']}（内容未写）")
            continue
        c = mod.CONTENT[p["examId"]]
        md, n = render(p, c)
        d = f"{OUT}/{p['book']}"
        os.makedirs(d, exist_ok=True)
        json.dump({"examId": p["examId"], "book": p["book"], "paper": p["paper"],
                   "kind": p["kind"], "markdown": md},
                  open(f"{d}/{p['paper']}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        total += n
        print(f"{p['book']} / {p['paper']}  汉字 {n}")
    print("TOTAL", total)


if __name__ == "__main__":
    main()
