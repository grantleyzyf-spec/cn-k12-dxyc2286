# -*- coding: utf-8 -*-
"""小学 9 册 chapter 单元号校正：以《每节内容对应页码》定稿里的 42pt 单元号为准。

背景：图谱里的小学 chapter 是早先按「目录页出现顺序」写的，而新版教材目录页是分栏排版，
目录页上的单元名与正文页的 42pt 单元号不一定同序；并且综合实践（1亿有多大、校园小导游、
身体上的尺子、年月日的秘密、生活中的负数、体育中的数学……）教材根本不编号，却被当成了单元，
导致这些册从该处起所有单元号 +1（四上最典型：1亿有多大被算成第二单元，角的度量变第三、
多位数乘两位数变第四……）。

规则
  · 正常单元  → `<册> 第<中文序>单元 <单元名>`
  · 综合实践/预备课（教材无单元号）→ `<册> 综合与实践 <名称>`
  · 复习与关联 → `<册> 复习与关联`（教材把它编为最后一个单元，但为免与前面撞号且它不建点，统一不带号）
  · `附：…（旧版延伸内容·新版未设）` 一律不动

用法：python3 renumber_xiaoxue.py [--write]
"""
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/math/topics.json"
XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/小学/人教版"
WRITE = "--write" in sys.argv
CN = "一二三四五六七八九十"


def read_units(book):
    """→ [(单元号 or None, 单元名)]，保持教材顺序。"""
    p = f"{XI}/{book}/教学设计/数学人教版{book}每节内容对应页码.txt"
    txt = open(p, encoding="utf-8").read()
    units = []
    if "【目录结构】" in txt:                       # 五上：人工件，目录结构块
        block = txt.split("【目录结构】", 1)[1]
        for ln in block.split("\n"):
            m = re.match(r"^([一二三四五六七八九十])\s*[　 ](.+?)\s+\d+\s*$", ln.strip())
            if m:
                units.append((m.group(1), m.group(2).strip()))
            else:
                m2 = re.match(r"^[　 ]+(.+?)\s+\d+\s*$", ln.strip() or " ")
                if m2 and "教师" not in m2.group(1):
                    units.append((None, m2.group(1).strip()))
        return units
    for ln in txt.split("\n"):                      # 8 册定稿：`一　单元名（第x—y页）` / `【活动名】`
        s = ln.strip()
        if not s or s.startswith("数学（") or s.startswith("（"):
            continue
        m = re.match(r"^([一二三四五六七八九十])\s*[　 ]+(.+?)（第", s)
        if m:
            units.append((m.group(1), m.group(2).strip()))
            continue
        m = re.match(r"^【(.+?)】", s)
        if m:
            units.append((None, m.group(1).strip()))
    return units


def main():
    topics = json.load(open(TP, encoding="utf-8"))
    BOOKS = [(1, "上", "一年级上册"), (1, "下", "一年级下册"), (2, "上", "二年级上册"),
             (2, "下", "二年级下册"), (3, "上", "三年级上册"), (3, "下", "三年级下册"),
             (4, "上", "四年级上册"), (5, "上", "五年级上册"), (6, "上", "六年级上册")]
    total = 0
    for g, sem, book in BOOKS:
        units = read_units(book)
        named = {n: no for no, n in units}
        unknown, changed = set(), 0
        for t in topics:
            if (t["grade"], t["semester"]) != (g, sem):
                continue
            ch = t["chapter"]
            if "旧版延伸内容" in ch:
                continue
            body = ch.split(" ", 1)[1] if " " in ch else ch
            name = re.sub(r"^第[一二三四五六七八九十]+单元\s*", "", body)
            name = re.sub(r"^附：", "", name).strip()
            if name in named:
                no = named[name]
                new = f"{book} 复习与关联" if name == "复习与关联" else (
                    f"{book} 第{no}单元 {name}" if no else f"{book} 综合与实践 {name}")
            elif name == "复习与关联":
                new = f"{book} 复习与关联"
            else:
                unknown.add(name)
                continue
            if new != ch:
                t["chapter"] = new
                changed += 1
        total += changed
        print(f"== {book}：教材 {len(units)} 个单元/活动 · 改章 {changed} 点"
              + (f" · ⚠ 对不上的旧章名 {sorted(unknown)}" if unknown else ""))
        for no, n in units:
            pts = [t["name"] for t in topics
                   if (t["grade"], t["semester"]) == (g, sem) and t["chapter"].endswith(n)]
            tag = f"第{no}单元" if no else "综合与实践"
            print(f"    {tag:<6} {n}（{len(pts)} 点）")
    print(f"合计改章 {total} 点")
    if WRITE and total:
        json.dump(topics, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(TP, "a").write("\n")
        print("✅ 已写入", TP)


if __name__ == "__main__":
    main()
