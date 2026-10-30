# -*- coding: utf-8 -*-
"""语文教材目录抽取 + 与图谱 chapter/点 的核对（单元级 + 课级）。

输出：/tmp/cn/audit.md（每册：单元数、课数、图谱点数、未对上/真缺清单）
用法：python3 audit_cn_units.py [--write-report]
"""
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
ROOT = "/Users/a627692/Desktop/中小学教材/中小学教材/语文"
OUT = "/tmp/cn"
CN = "一二三四五六七八九十"

# (grade, semester, 册名关键词, PDF glob 目录)
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
NOISE = re.compile(r"仅供个人学习使用|未经授权|不得另做他用")
UNIT_RE = re.compile(r"(第[一二三四五六七八九十]+单元)(?:[·・]\s*(\S+))?")
PAGE_TAIL = re.compile(r"^(.*?)[\s　]*(\d{1,3})$")


def read_toc(pdf):
    """→ [(unit, [ (num|kind, name, page) ])]，按目录页顺序。"""
    import fitz
    d = fitz.open(pdf)
    lines = []
    for i in range(min(12, d.page_count)):
        t = d[i].get_text()
        if "目录" in t or UNIT_RE.search(t):
            for ln in t.split("\n"):
                s = ln.strip().replace("\x09", " ")
                if not s or NOISE.search(s) or s == "目录":
                    continue
                lines.append(s)
    d.close()
    units, cur = [], None
    buf = []
    for s in lines:
        m = UNIT_RE.match(s.replace(" ", ""))
        if m:
            head = s.replace(" ", "")
            cur = {"unit": head, "items": []}
            units.append(cur)
            continue
        if cur is None:
            continue
        # 「◎ 语文园地一 15」「1 天地人 8」「天地人 8」
        mm = PAGE_TAIL.match(s)
        if mm:
            name = mm.group(1).strip()
            page = int(mm.group(2))
            name = re.sub(r"^[◎○\d]{1,3}[\s　]*", "", name).strip()
            if not name or re.fullmatch(r"[\d\s　]+", name):
                continue
            kind = "园地" if re.search(r"语文园地|快乐读书吧|口语交际|习作|综合性学习|名著导读|课外古诗词", name) else "课"
            cur["items"].append((kind, name, page))
    return [u for u in units if u["items"]]


def norm(s):
    return re.sub(r"[\s　（）()【】\[\]、，,．.·・「」“”\"'’!！?？:：;；—\-·]", "", s or "")


def core(s):
    s = norm(s)
    for w in ("第一单元", "第二单元", "第三单元", "第四单元", "第五单元", "第六单元",
              "第七单元", "第八单元", "第九单元", "第十单元", "识字", "阅读", "课文",
              "写作", "口语交际", "综合性学习", "名著导读", "古代诗歌", "文言文", "现代文"):
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
    L = ["# 语文教材目录核对（单元级 + 课级）", ""]
    rows = []
    for g, sem, book, pat in BOOKS:
        pdfs = glob.glob(pat)
        ts = [t for t in topics if (t["grade"], t["semester"]) == (g, sem)]
        if not pdfs:
            L.append(f"## {book}\n- ⛔ 本机缺教材 PDF（图谱 {len(ts)} 点，未核）\n")
            rows.append((book, "缺PDF", len(ts), 0, 0, 0, 0))
            continue
        toc = read_toc(pdfs[0])
        n_units = len(toc)
        n_lessons = sum(1 for u in toc for k, _, _ in u["items"] if k == "课")
        n_yuan = sum(1 for u in toc for k, _, _ in u["items"] if k == "园地")
        # 课级覆盖：每个课名能否找到一个图谱点
        miss = []
        for u in toc:
            for k, nm, pg in u["items"]:
                if k != "课":
                    continue
                best = max(((score(t["name"], nm), t["name"]) for t in ts), default=(0, ""))
                if best[0] < 0.5:
                    miss.append((u["unit"], nm, pg, best[1], round(best[0], 2)))
        cover = n_lessons - len(miss)
        L.append(f"## {book}")
        L.append(f"- 教材：{n_units} 单元 · 课文 {n_lessons} 课 · 园地/活动 {n_yuan} 个；图谱 **{len(ts)} 点**，"
                 f"现有章：{len({t['chapter'] for t in ts})} 个")
        L.append(f"- 课级覆盖：**{cover}/{n_lessons}**（判据 2-gram ≥0.50）")
        if miss:
            L.append("- 未对上课（候选真缺）：")
            for u, nm, pg, near, sc in miss:
                L.append(f"    - {u} · **{nm}**（第{pg}页；最近点「{near}」{sc}）")
        L.append("")
        rows.append((book, f"{n_units}单元/{n_lessons}课", len(ts), cover, n_lessons, n_yuan, len(miss)))
    L += ["## 汇总", "", "| 册 | 教材 | 图谱点 | 课级覆盖 | 未对上 |", "| --- | --- | ---: | ---: | ---: |"]
    for b, info, npts, cover, tot, yuan, miss in rows:
        L.append(f"| {b} | {info} | {npts} | {cover}/{tot} | {miss} |")
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/audit.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[L.index("## 汇总"):]))
    print(f"\n报告 → {OUT}/audit.md")


if __name__ == "__main__":
    main()
