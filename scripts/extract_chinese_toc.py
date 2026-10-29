# -*- coding: utf-8 -*-
"""语文教材目录抽取 v2（token 流解析）+ 图谱课级核对。

v1 失败原因：PyMuPDF 把目录拆成「单元名 / 序号 / 课名 / 页码」四类独立行，按行匹配拿不到成对关系。
v2：把目录页拼成一条 token 流再正则切，单元用「第X单元·板块」分段，条目用「序号 课名 页码」/「◎ 名称 页码」。

产出：/tmp/cn/units.json（每册 单元→条目(类型/名/页)）＋ /tmp/cn/audit.md
"""
import glob
import json
import os
import re

import fitz

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
ROOT = "/Users/a627692/Desktop/中小学教材/中小学教材/语文"
OUT = "/tmp/cn"
NOISE = re.compile(r"仅供个人学习使用|未经授权|不得另做他用|电子课本")
STOP = re.compile(r"^(识字表|写字表|笔画名称表|常用偏旁名称表|后记|附录)")
UNIT = re.compile(r"(第[一二三四五六七八九十]+单元)\s*[·・]?\s*([^\s0-9◎]{0,8})?")
ITEM_NUM = re.compile(r"(?:^|\s)(\d{1,2})\s*\*?\s+([^\d◎]{1,24}?)\s+(\d{1,3})(?=\s|$)")
ITEM_MARK = re.compile(r"◎\s*([^\d◎]{2,24}?)\s+(\d{1,3})(?=\s|$)")

BOOKS = [
    (1, "上", "一年级上册", f"{ROOT}/小学/*一年级_上册*.pdf"),
    (1, "下", "一年级下册", f"{ROOT}/小学/*一年级_下册*.pdf"),
    (2, "上", "二年级上册", f"{ROOT}/小学/*二年级_上册*.pdf"),
    (2, "下", "二年级下册", f"{ROOT}/小学/*二年级_下册*.pdf"),
    (3, "上", "三年级上册", f"{ROOT}/小学/*三年级_上册*.pdf"),
    (3, "下", "三年级下册", f"{ROOT}/小学/*三年级_下册*.pdf"),
    (4, "上", "四年级上册", f"{ROOT}/小学/*四年级_上册*.pdf"),
    (5, "上", "五年级上册", f"{ROOT}/小学/*五年级_上册*.pdf"),
    (6, "上", "六年级上册", f"{ROOT}/小学/*六年级_上册*.pdf"),
    (7, "上", "七年级上册", f"{ROOT}/初中/*七年级_上册*.pdf"),
    (7, "下", "七年级下册", f"{ROOT}/初中/*七年级_下册*.pdf"),
    (8, "上", "八年级上册", f"{ROOT}/初中/*八年级_上册*.pdf"),
    (8, "下", "八年级下册", f"{ROOT}/初中/*八年级_下册*.pdf"),
    (9, "上", "九年级上册", f"{ROOT}/初中/*九年级_上册*.pdf"),
]
MARK_KINDS = ("语文园地", "快乐读书吧", "口语交际", "习作", "写话", "综合性学习", "名著导读",
              "课外古诗词诵读", "课外古诗词", "阅读链接", "书写提示", "日积月累", "和大人一起读",
              "阅读综合实践", "专题学习活动", "整本书阅读", "活动·探究", "例文", "任务一", "任务二", "任务三")


def _columns(page, mid_ratio=0.5):
    """按 x 中线把页面词切成左右两栏，各自按 y 排序 → 两段文本（语文目录常两栏排版）。"""
    w = page.rect.width
    left, right = [], []
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        (left if (x0 + x1) / 2 < w * mid_ratio else right).append((y0, x0, word))
    out = []
    for col in (left, right):
        col.sort()
        if col:
            out.append(" ".join(t for _, _, t in col))
    return out


def flatten_toc(pdf, maxpage=14):
    d = fitz.open(pdf)
    head, tail = "", ""
    for i in range(min(maxpage, d.page_count)):
        page = d[i]
        raw = page.get_text()
        if not (UNIT.search(raw) or "目录" in raw):
            continue
        cols = _columns(page) or [raw]
        for t in cols:
            t = NOISE.sub(" ", t).replace("\x09", " ")
            if not (UNIT.search(t) or "我上学了" in t or "阅读" in t):
                continue
            if not head:
                m = UNIT.search(t)
                if "我上学了" in t and (not m or t.index("我上学了") < t.index(m.group(1))):
                    head = t[t.index("我上学了"):]
                    continue
                if m:
                    head = t[m.start():]
                    continue
            tail += " " + t
    d.close()
    flat = head + " " + tail
    flat = re.sub(r"\.{2,}", " ", flat)          # 「彩虹.....28」的点引导
    flat = re.sub(r"[·]{2,}", " ", flat)
    return re.sub(r"\s+", " ", flat)


def parse(flat):
    """→ [{'unit': '第一单元·识字', 'items': [{'kind','name','page'}]}]"""
    flat = re.split(r"(识字表|写字表|笔画名称表|常用偏旁名称表|后记|附录)", flat)[0]
    # 目录块里会重复出现后面的正文页碎片，去掉超长无关段
    marks = [(m.start(), m.group(1), (m.group(2) or "").strip()) for m in UNIT.finditer(flat)]
    entry = re.search(r"我上学了", flat)
    if entry and (not marks or entry.start() < marks[0][0]):
        marks.insert(0, (entry.start(), "我上学了", ""))
    units = []
    for k, (pos, name, sub) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else len(flat)
        seg = flat[pos:end]
        seg = seg[len(re.search(r"^[\s]*" + re.escape(name), seg).group(0)):] if re.search(r"^[\s]*" + re.escape(name), seg) else seg
        items = []
        taken = []
        for m in ITEM_MARK.finditer(seg):
            nm = m.group(1).strip()
            kind = next((x for x in MARK_KINDS if nm.startswith(x)), "活动")
            items.append({"kind": kind, "name": nm, "page": int(m.group(2))})
            taken.append((m.start(), m.end()))
        for m in ITEM_NUM.finditer(seg):
            if any(a <= m.start() < b for a, b in taken):
                continue
            nm = m.group(2).strip()
            if not re.search(r"[\u4e00-\u9fa5a-zü]", nm):
                continue
            items.append({"kind": "课", "name": nm, "page": int(m.group(3))})
        items.sort(key=lambda x: x["page"])
        units.append({"unit": (name + ("·" + sub if sub else "")).strip(), "items": items})
    return [u for u in units if u["items"]]


def norm(s):
    return re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-]", "", s or "")


def core(s):
    s = norm(s)
    for w in ("第一单元", "第二单元", "第三单元", "第四单元", "第五单元", "第六单元", "第七单元",
              "第八单元", "第九单元", "识字", "阅读", "课文", "写作", "口语交际", "综合性学习",
              "名著导读", "古代诗歌", "文言文", "现代文", "活动探究", "整本书阅读", "汉字", "汉语拼音"):
        s = s.replace(w, "")
    return s


def bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}


def score(a, b):
    ca, cb = core(a), core(b)
    if not ca or not cb:
        return 0.0
    if ca in cb or cb in ca:
        return 1.0
    A, B = bigrams(ca), bigrams(cb)
    return max(len(A & B) / max(1, len(A)), len(A & B) / max(1, len(B)))


def main():
    topics = json.load(open(f"{REPO}/data/chinese/topics.json", encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    allunits, L, rows = {}, ["# 语文教材目录核（v2）", ""], []
    for g, sem, book, pat in BOOKS:
        pdfs = glob.glob(pat)
        ts = [t for t in topics if (t["grade"], t["semester"]) == (g, sem)]
        if not pdfs:
            L.append(f"## {book}\n- ⛔ 缺教材 PDF（图谱 {len(ts)} 点未核）\n")
            rows.append((book, "缺PDF", len(ts), 0, 0))
            continue
        units = parse(flatten_toc(pdfs[0]))
        allunits[book] = units
        n_lesson = sum(1 for u in units for it in u["items"] if it["kind"] == "课")
        miss = []
        for u in units:
            for it in u["items"]:
                if it["kind"] != "课":
                    continue
                best = max(((score(t["name"], it["name"]), t["name"]) for t in ts), default=(0, ""))
                if best[0] < 0.5:
                    miss.append((u["unit"], it["name"], it["page"], best[1], round(best[0], 2)))
        cover = n_lesson - len(miss)
        L += [f"## {book}",
              f"- 教材 **{len(units)} 单元 / 课文 {n_lesson} 课**；图谱 {len(ts)} 点、现有章 {len({t['chapter'] for t in ts})} 个",
              f"- 课级覆盖 **{cover}/{n_lesson}**",
              "- 单元：" + "；".join(f"{u['unit']}({len(u['items'])})" for u in units), ""]
        if miss:
            L.append("- 未对上课（候选真缺）：" + "、".join(f"{n}(p{p})" for _, n, p, _, _ in miss[:40]))
            L.append("")
        rows.append((book, f"{len(units)}单元/{n_lesson}课", len(ts), cover, n_lesson))
    L += ["## 汇总", "", "| 册 | 教材 | 图谱点 | 课级覆盖 |", "| --- | --- | ---: | ---: |"]
    for b, info, npts, cover, tot in rows:
        L.append(f"| {b} | {info} | {npts} | {cover}/{tot} |")
    open(f"{OUT}/audit.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(allunits, open(f"{OUT}/units.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(L[L.index("## 汇总"):]))


if __name__ == "__main__":
    main()
