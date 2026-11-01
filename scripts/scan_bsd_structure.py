#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北师大版数学 盘点（v4）：分课时 docx 优先 → 大单元 docx 兜底 → 册/单元/课时 + 三重对账。

来源优先级（每册独立判定）：
1. `各学科分课时设计/数学/北师大版/<学段>/<册>/*.docx`（现只覆盖上册：小学 6 册、初中 3 册）
   —— 文件名自带「第N单元 X·第K课时 名」与「共M课时」，是权威口径。
2. `大单元整体教学设计` docx 的「十五、教-学-评一致性课时设计」段（覆盖全部 21 册，含下册）。
   只从该段取名；引号名优先，活动句与「要在/需要/方法」类句子丢弃。

对账三项：
A 册级：各单元课时之和 vs 分课时 docx 声明的「全册共N课时」
B 单元级：解析课时数 vs 「（共M课时）」
C 连续性：单元号必须 1..N 连续、单元名不重复

用法: python3 scripts/scan_bsd_structure.py --stage 小学|初中|高中 [--json out.json] [--verbose]
"""
import argparse, json, os, re
from collections import defaultdict

import docx

OUTER = os.path.expanduser("~/Desktop/中小学教材")
BOOKDIR = os.path.join(OUTER, "中小学教材")
KESHI = os.path.join(BOOKDIR, "各学科分课时设计/数学/北师大版")
DANYUAN = {
    "小学": [os.path.join(OUTER, "1.0标准合集/小学数学/北师大版小学数学大单元整体教学设计"),
             os.path.join(BOOKDIR, "数学/小学/北师大版/大单元整体教学设计")],
    "初中": [os.path.join(BOOKDIR, "数学/初中/北师大版/大单元整体教学设计")],
    "高中": [os.path.join(BOOKDIR, "数学/高中/北师大版")],
}
BOOK_RE = {
    "小学": re.compile(r"([一二三四五六]年级[上下]册)"),
    "初中": re.compile(r"([七八九]年级[上下]册)"),
    "高中": re.compile(r"(必修第[一二三四五]册|选择性必修第[一二三四五]册)"),
}
EXCLUDE = re.compile(r"总复习|数学好玩|综合实践|综合与实践|整理与复习|单元复习|复习课|章末|小结")
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
      "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15, "十六": 16,
      "十七": 17, "十八": 18, "十九": 19, "二十": 20}
ORDER = ["一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
         "四年级上册", "四年级下册", "五年级上册", "五年级下册", "六年级上册", "六年级下册",
         "七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册", "九年级下册",
         "必修第一册", "必修第二册", "选择性必修第一册", "选择性必修第二册",
         "选择性必修第三册", "选择性必修第四册"]

K_UNIT = r"(第[一二三四五六七八九十\d]+(?:单元|章)|总复习|数学好玩|综合实践|综合与实践)"
K_LESSON_A = re.compile(K_UNIT + r"\s*([^·]+?)·第(\d+)课时\s*(.+?)分课时教学设计")
K_LESSON_B = re.compile(K_UNIT + r"\s*([^·]+?)·(.+?)（第(\d+)课时）分课时教学设计")
K_UNIT_TOTAL = re.compile(K_UNIT + r"\s*([^·（(]+?)分课时设计(?:（共(\d+)课时）)?")
K_BOOK_TOTAL = re.compile(r"全册分课时教学设计（共(\d+)课时）")
EXTRA_UNIT = re.compile(r"总复习|数学好玩|综合实践|综合与实践")

BADNAME = re.compile(r"播放|讲述|呈现|出示|组织|开展|创设|引导|导入|环节|学习目标|评价任务|"
                     r"教学活动|本单元|本课|要在|要与|需要|方法要|的知识|课时")
QUOTED = re.compile(r"第([一二三四五六七八九十\d]+)(?:课时|节)\s*[“\"']([^”\"']{2,28})[”\"']")
GOAL = re.compile(r"第([一二三四五六七八九十\d]+)(?:课时|节)\s*[“\"']?([^“”\"'的]{2,24}?)[”\"']?\s*的(?:学习目标|教学目标)")
STATED = re.compile(r"(?:安排|共|计|用)\s*([一二三四五六七八九十\d]+)\s*个?(?:课时|节)")


def cn2int(s):
    s = str(s).strip()
    return int(s) if s.isdigit() else CN.get(s, 99)


def clean_name(s):
    return re.sub(r"\s+", "", s).strip("“”\"'·—-、《》 ")


def scan_keshi(book_dir):
    units, book_total, n_files = {}, None, 0
    extras = {}
    for fn in sorted(os.listdir(book_dir)):
        if not fn.endswith(".docx") or fn.startswith("~$") or fn.startswith(".~"):
            continue
        n_files += 1
        mb = K_BOOK_TOTAL.search(fn)
        if mb:
            book_total = cn2int(mb.group(1))
            continue
        ma = K_LESSON_A.search(fn)
        mbb = K_LESSON_B.search(fn)
        m = ma or mbb
        if m:
            head = m.group(1)
            if EXTRA_UNIT.search(head):           # 总复习/数学好玩/综合实践：只用于册级对账
                key = "\u0001" + head
                extras.setdefault(key, {})[int(ma.group(3) if ma else mbb.group(4))] = \
                    clean_name(ma.group(3) if ma else mbb.group(3))
                continue
            no = cn2int(re.sub(r"[第单元章]", "", head))
            uname, k, lname = (m.group(2), int(m.group(3)), m.group(4)) if ma else \
                              (m.group(2), int(m.group(4)), m.group(3))
            cur = units.setdefault(no, {"unit_no": no, "unit_name": clean_name(uname),
                                        "lessons": {}, "stated": None})
            cur["lessons"][k] = clean_name(lname)
            continue
        mu = K_UNIT_TOTAL.search(fn)
        if mu and not EXTRA_UNIT.search(mu.group(1)):
            no = cn2int(re.sub(r"[第单元章]", "", mu.group(1)))
            cur = units.setdefault(no, {"unit_no": no, "unit_name": clean_name(mu.group(2)),
                                        "lessons": {}, "stated": None})
            if mu.group(3):
                cur["stated"] = int(mu.group(3))
    for u in units.values():
        u["lessons"] = sorted(u["lessons"].items())
    n_extra = sum(len(v) for v in extras.values())
    return units, book_total, n_files, n_extra


def sec15(paras):
    idx = [i for i, s in enumerate(paras) if re.match(r"^十五、", s)]
    if not idx:
        return paras
    start, end = idx[-1], len(paras)
    for j in range(start + 1, len(paras)):
        if re.match(r"^十六、", paras[j]):
            end = j
            break
    return paras[start + 1:end]


def grab(paras, pat):
    got = {}
    for s in sec15(paras):
        for m in pat.finditer(s):
            n = cn2int(m.group(1))
            name = clean_name(m.group(2))
            if 2 <= len(name) <= 28 and not BADNAME.search(name):
                if n not in got or len(got[n]) < len(name):
                    got[n] = name
    return got


PLAIN_SENIOR = re.compile(r"^[（(][一二三四五六七八九十\d]+[）)]\s*第(\d+)课时\s+([^\s，。；：、（）(]{2,22})")


def grab_senior(paras):
    """高中写法：（一）第1课时 生活中的变量关系"""
    got = {}
    for s in sec15(paras):
        for m in PLAIN_SENIOR.finditer(s):
            name = clean_name(m.group(2))
            if 2 <= len(name) <= 22 and not BADNAME.search(name):
                got.setdefault(int(m.group(1)), name)
    return got


def scan_danyuan(d, stage):
    books = defaultdict(dict)
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".docx") or fn.startswith("~$") or fn.startswith(".~"):
            continue
        mb = BOOK_RE[stage].search(fn)
        if not mb or EXCLUDE.search(fn):
            continue
        mu = re.search(r"第([一二三四五六七八九十\d]+)(单元|章)", fn)
        if not mu:
            continue
        book, no = mb.group(1), cn2int(mu.group(1))
        paras = [p.text.strip() for p in docx.Document(os.path.join(d, fn)).paragraphs if p.text.strip()]
        q, g = grab(paras, QUOTED), grab(paras, GOAL)
        use = q if len(q) >= 3 else (g if len(g) >= 3 else {**g, **q})
        if len(use) < 3:                        # 高中写法兜底
            use = {**grab_senior(paras), **use}
        stated = None
        for s in paras[:80]:
            m = STATED.search(s)
            if m and 1 <= cn2int(m.group(1)) <= 40:
                stated = cn2int(m.group(1))
                break
        cand = {"unit_no": no,
                "unit_name": clean_name(re.sub(r"^.*?第[一二三四五六七八九十\d]+(?:单元|章)\s*", "", fn)
                                        .split("大单元整体教学设计")[0]),
                "lessons": sorted(use.items()), "stated": stated, "src": fn}
        prev = books[book].get(no)
        if prev is None or len(cand["lessons"]) > len(prev["lessons"]):
            books[book][no] = cand
    return books


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="小学", choices=list(DANYUAN))
    ap.add_argument("--json")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    stage = a.stage

    dy = defaultdict(dict)
    for d in DANYUAN[stage]:
        if not os.path.isdir(d):
            print(f"⚠️ 缺目录 {d}")
            continue
        for book, units in scan_danyuan(d, stage).items():
            for no, u in units.items():
                if no not in dy[book] or len(u["lessons"]) > len(dy[book][no]["lessons"]):
                    dy[book][no] = u

    ks_root = os.path.join(KESHI, stage)
    ks = {}
    if os.path.isdir(ks_root):
        for book in sorted(os.listdir(ks_root)):
            bd = os.path.join(ks_root, book)
            if os.path.isdir(bd) and not book.startswith("_"):
                units, total, nf, n_extra = scan_keshi(bd)
                if units:
                    ks[book] = (units, total, nf, n_extra)

    out, tot_u, tot_l = {}, 0, 0
    for book in ORDER:
        if book in ks:
            units, btotal, nf, n_extra = ks[book]
            sum_l = sum(len(u["lessons"]) for u in units.values())
            ok = (btotal is None or btotal == sum_l + n_extra)
            print(f"{book}: 单元 {len(units)} / 课时 {sum_l}(+附加块{n_extra}) 源=分课时docx({nf}件) "
                  f"{'✅册级对账一致' if ok else f'⚠️册级: 声明{btotal} vs 解析{sum_l + n_extra}'}")
            for no in sorted(units):
                u = units[no]
                if u["stated"] and len(u["lessons"]) != u["stated"]:
                    print(f"    第{no}单元 {u['unit_name'][:14]}: 解析 {len(u['lessons'])} vs 共{u['stated']}课时")
            inner = units
        elif book in dy:
            inner = dy[book]
            sum_l = sum(len(u["lessons"]) for u in inner.values())
            print(f"{book}: 单元 {len(inner)} / 课时 {sum_l} 源=大单元十五段 ⚠️无分课时docx")
        else:
            print(f"{book}: ❌ 无任何结构源")
            continue
        nos = sorted(inner)
        if nos != list(range(1, len(nos) + 1)):
            print(f"    ⚠️单元号不连续 {nos}")
        names = [inner[n]["unit_name"] for n in nos]
        dup = sorted({x for x in names if names.count(x) > 1})
        if dup:
            print(f"    ⚠️单元重名 {dup}")
        tot_u += len(nos)
        tot_l += sum_l
        if a.verbose:
            for n in nos:
                u = inner[n]
                print(f"    第{n} {u['unit_name'][:18]}({len(u['lessons'])}): "
                      + " / ".join(x for _, x in u["lessons"])[:100])
        out[book] = [{"unit_no": n, "unit_name": inner[n]["unit_name"],
                      "stated": inner[n]["stated"],
                      "lessons": [[k, v] for k, v in inner[n]["lessons"]]} for n in nos]
    print(f"\n合计：{len(out)} 册 / {tot_u} 单元 / {tot_l} 课时")
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("written", a.json)


if __name__ == "__main__":
    main()
