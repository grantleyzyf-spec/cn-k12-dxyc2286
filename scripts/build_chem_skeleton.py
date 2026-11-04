#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：抽取「单元/章 → 课题/节」骨架（教材目录页解析）。

结构源：教材 PDF 前 6–10 页的目录页（人教版化学初中、高中目录页都有文字层）。
单元/章名以 `CANON` 表为准——目录页在「章名跨行 / 公式图夹排」时会读坏（实测选必2 第二章读成「α」、
必修一第三章读成「铁」），教案表比正则可靠；课题/节名按「单元名或单元号锚点的位置切段」取，
⛔ 不用「下一个锚点」的相对规则（人教版初中第六单元起锚点前置、前五个单元锚点后置，混用会整单元串位）。

用法：python3 scripts/build_chem_skeleton.py [--write]
产物：data/chemistry/_skeleton.json
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")
SRC_PRI = "/Users/a627692/Desktop/中小学教材/中小学教材/化学/初中/人教版"
SRC_HIGH = "/Users/a627692/Desktop/中小学教材/中小学教材/化学/高中/人教版"
CN = "一二三四五六七八九十"
M = {c: i + 1 for i, c in enumerate(CN[:10])}

CANON = {
    "九年级上册": ["走进化学世界", "空气和氧气", "物质构成的奥秘", "自然界的水",
                   "化学反应的定量关系", "碳和碳的氧化物", "能源的合理利用与开发"],
    "九年级下册": ["金属和金属材料", "溶液", "常见的酸、碱、盐", "化学与社会"],
    "必修第一册": ["物质及其变化", "海水中的重要元素——钠和氯", "铁 金属材料", "物质结构 元素周期律"],
    "必修第二册": ["化工生产中的重要非金属元素", "化学反应与能量", "有机化合物", "化学与可持续发展"],
    "选择性必修第一册": ["化学反应的热效应", "化学反应速率与化学平衡",
                          "水溶液中的离子反应与平衡", "化学反应与电能"],
    "选择性必修第二册": ["原子结构与性质", "分子结构与性质", "晶体结构与性质"],
    "选择性必修第三册": ["有机化合物的结构特点与研究方法", "烃", "烃的衍生物",
                          "生物大分子", "合成高分子"],
}
LESSON_FIX = {("选择性必修第二册", 2, 1): "共价键"}
BOOKS = [("九年级上册", "初中", 9, "上", 1, "单元"), ("九年级下册", "初中", 9, "下", 8, "单元"),
         ("必修第一册", "高中", 10, "上", 1, "章"), ("必修第二册", "高中", 10, "下", 5, "章"),
         ("选择性必修第一册", "高中", 11, "上", 1, "章"),
         ("选择性必修第二册", "高中", 11, "下", 1, "章"),
         ("选择性必修第三册", "高中", 12, "上", 1, "章")]
PDF_HINT = {"九年级上册": ("初中", "化学 九年级 上册"), "九年级下册": ("初中", "化学 九年级 下册"),
            "必修第一册": ("高中", "必修第一册"), "必修第二册": ("高中", "必修第二册"),
            "选择性必修第一册": ("高中", "选择性必修1"), "选择性必修第二册": ("高中", "选择性必修2"),
            "选择性必修第三册": ("高中", "选择性必修3")}


def cn2int(s):
    if s.isdigit():
        return int(s)
    if s in M:
        return M[s]
    if s.startswith("十"):
        return 10 + M.get(s[1:], 0)
    if s.endswith("十"):
        return M.get(s[:-1], 0) * 10
    return 0


def norm(s):
    return re.sub(r"\s+", "", s or "")


def toks_of(book, pages):
    stage, hint = PDF_HINT[book]
    base = SRC_PRI if stage == "初中" else SRC_HIGH
    cands = [f for f in glob.glob(os.path.join(base, "*.pdf")) if hint in os.path.basename(f)]
    if not cands:
        return []
    t = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", "1", "-l", str(pages), cands[0], "-"],
                       capture_output=True, text=True).stdout
    i = t.find("目录")
    blk = t[i:] if i >= 0 else t
    out = []
    for x in blk.split("\n"):
        x = x.strip()
        if not x or re.match(r"^\d+$", x) or x.startswith("仅供个人学习使用"):
            continue
        out.append(x)
    return out


def trim_toc(toks):
    """目录块截断：遇到正文标记（练习与应用/附录/实验活动正文）就停，防止正文被当作目录。"""
    for i, x in enumerate(toks):
        if x.strip() in ("练习与应用", "附录", "绪言", "引言") or x.startswith("附录"):
            if i > 5:
                return toks[:i]
    return toks[:400]


def build_book(book, stage, grade, sem, first_no, kind):
    toks = trim_toc(toks_of(book, 8 if stage == "初中" else 18))
    names = CANON[book]
    starts, prev = [], 0
    for i, nm in enumerate(names, 1):
        no = first_no + i - 1
        idx_name = next((k for k in range(prev, len(toks))
                         if norm(toks[k]) == norm(nm) or norm(toks[k]).startswith(norm(nm))), None)
        idx_anchor = next((k for k in range(prev, len(toks))
                           if re.match(rf"^第[{CN}\d]+{kind}", toks[k])
                           and cn2int(re.match(rf"^第([{CN}\d]+)", toks[k]).group(1)) == no), None)
        cand = [x for x in (idx_name, idx_anchor) if x is not None]
        idx = min(cand) if cand else len(toks)
        starts.append((no, nm, idx))
        prev = idx
    units = []
    for j, (no, nm, st) in enumerate(starts):
        end = starts[j + 1][2] if j + 1 < len(starts) else len(toks)
        seg = toks[st:end]
        pat = (re.compile(rf"^课题\s*([{CN}\d]+)\s*(.*)$") if kind == "单元"
               else re.compile(rf"^第([{CN}\d]+)节\s*(.*)$"))
        lessons, i = [], 0
        while i < len(seg):
            m = pat.match(seg[i])
            if m and i + 1 < len(seg):
                lno = cn2int(m.group(1))
                lname = (m.group(2) or "").strip() or seg[i + 1]
                if not re.match(rf"^第[{CN}\d]+[章节]$", lname) and not re.match(rf"^课题\s*[{CN}\d]+$", lname):
                    lessons.append({"no": lno, "name": LESSON_FIX.get((book, no, lno), lname),
                                    "kind": "课题" if kind == "单元" else "节"})
                    i += 2
                    continue
            i += 1
        lessons.sort(key=lambda x: x["no"])
        seen, uniq = set(), []
        for l in lessons:
            if l["no"] in seen:
                continue
            seen.add(l["no"])
            uniq.append(l)
        units.append({"no": no, "kind": kind, "name": nm, "lessons": uniq,
                      "book": book, "stage": stage, "grade": grade, "semester": sem})
    return {"book": book, "stage": stage, "grade": grade, "semester": sem, "units": units}


def main():
    books = [build_book(*b) for b in BOOKS]
    uid = lid = 0
    tu = tl = 0
    for b in books:
        for u in b["units"]:
            uid += 1
            u["uid"] = f"chem_u{uid:03d}"
            u["chapter"] = f"{b['book']} 第{u['no']}{u['kind']} {u['name']}"
            for l in u["lessons"]:
                lid += 1
                l["lid"] = f"chem_l{lid:03d}"
                l["chapter"] = f"{u['chapter']} · 第{l['no']}{l['kind']} {l['name']}"
        n = sum(len(u["lessons"]) for u in b["units"])
        print(f"{b['book']:10} {len(b['units']):>2} {b['units'][0]['kind'] if b['units'] else '-'} / 课时 {n:>3}")
        tu += len(b["units"])
        tl += n
    print(f"合计 单元 {tu} / 课时点 {tl}")
    for b in books:
        for u in b["units"]:
            print(f"  {u['uid']} 第{u['no']}{u['kind']} {u['name']}  [{len(u['lessons'])}] "
                  + "、".join(l["name"] for l in u["lessons"]))
    if "--write" in sys.argv:
        with open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8") as f:
            json.dump({"subject": "chemistry", "edition": "人教版", "books": books,
                       "counts": {"units": tu, "lessons": tl}}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("→ data/chemistry/_skeleton.json")


if __name__ == "__main__":
    main()
