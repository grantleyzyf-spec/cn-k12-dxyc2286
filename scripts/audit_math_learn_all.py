# -*- coding: utf-8 -*-
"""学层全库体检：一屏看清 19 册的达标面与缺口。

用法：
    python3 scripts/audit_math_learn_all.py            # 汇总
    python3 scripts/audit_math_learn_all.py --detail    # 每册缺口课时名也列出

判据（与 docs/math-learn-spec.md / check_math_learn_md.py 一致）：
  1 覆盖：本册已写篇数 / 课时点数
  2 结构：七段齐全（五步节存在、方法锚为「七」）
  3 字数：全篇 1200–2600，五步节 350–700
  4 分段：序号条目之间有空行（否则渲染并成一段）
  5 引文：课本原文章内 ≥2 处 `> `
  6 words 字段与实际汉字数差 ≤50
"""
import glob
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
LEARN = f"{REPO}/data/math/learn"
BOOKS = ["一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
         "四年级上册", "五年级上册", "六年级上册", "七年级上册", "七年级下册",
         "八年级上册", "八年级下册", "九年级上册",
         "必修第一册", "必修第二册", "选择性必修第一册", "选择性必修第二册", "选择性必修第三册"]
STEPS = ["锻炼", "第一个知识点", "积微", "对标", "杠铃"]


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def main():
    detail = "--detail" in sys.argv
    topics = json.load(open(f"{REPO}/data/math/topics.json", encoding="utf-8"))
    expect = {}
    for t in topics:
        ch = t.get("chapter") or ""
        if " · " in ch:
            book = ch.split(" ")[0]
            expect.setdefault(book, []).append(t)
    tot_have = tot_need = 0
    problems = []
    for book in BOOKS:
        need = expect.get(book, [])
        f = f"{LEARN}/{book}.json"
        if not os.path.exists(f):
            print(f"-- {book:10s} 0/{len(need)}  未开始")
            tot_need += len(need)
            continue
        d = json.load(open(f, encoding="utf-8"))
        have = {L["topicId"]: L for L in d.get("lessons") or []}
        n_ok = 0
        for L in d.get("lessons") or []:
            nm = L.get("title") or L["topicId"]
            md = L.get("markdown") or ""
            n = hanzi(md)
            bad = []
            if "五步学习法" not in md:
                bad.append("缺五步节")
            for k in STEPS:
                if k not in md:
                    bad.append(f"缺步骤「{k}」")
                    break
            if not re.search(r"^## 七、方法锚", md, re.M):
                bad.append("方法锚未顺延为七")
            if not (1200 <= n <= 2600):
                bad.append(f"字数 {n}")
            ls = md.split("\n")
            if any(re.match(r"^\d+\.\s", a.strip()) and re.match(r"^\d+\.\s", b.strip())
                   for a, b in zip(ls, ls[1:])):
                bad.append("序号粘连")
            sec = [x for x in re.split(r"\n(?=## )", md) if "五步学习法" in x.split("\n")[0]]
            if sec:
                sw = hanzi(sec[0])
                if not (350 <= sw <= 700):
                    bad.append(f"五步节 {sw} 字")
                if len([ln for ln in sec[0].split("\n") if re.match(r"^\d+\.\s", ln.strip())]) < 5:
                    bad.append("五步条数不足 5")
            quotes = []
            cur = ""
            for ln in ls:
                if ln.startswith("## "):
                    cur = ln
                    continue
                if ln.startswith("> ") and "课本原文" in cur and hanzi(ln) >= 8:
                    quotes.append(ln)
            if len(quotes) < 2:
                bad.append(f"引文 {len(quotes)} 处")
            if abs((L.get("words") or 0) - n) > 50:
                bad.append(f"words {L.get('words')}≠{n}")
            if bad:
                problems.append((book, nm, bad))
            else:
                n_ok += 1
        miss = [t["name"] for t in need if t["id"] not in have]
        tot_have += n_ok
        tot_need += len(need)
        flag = "OK " if n_ok == len(need) else (".. " if n_ok else "-- ")
        extra = "" if not miss else f"  缺 {len(miss)}"
        print(f"{flag}{book:10s} {n_ok}/{len(need)}{extra}")
        if detail and miss:
            print("      " + "、".join(miss[:40]))
    print(f"\n合计达标 {tot_have}/{tot_need}（{tot_have*100//max(tot_need,1)}%）")
    if problems:
        print(f"\n❌ 不合格 {len(problems)} 篇：")
        for book, nm, bad in problems[:25]:
            print(f"  {book} · {nm}: " + "；".join(bad))
        if len(problems) > 25:
            print(f"  …另有 {len(problems)-25} 篇")
        sys.exit(1)


if __name__ == "__main__":
    main()
