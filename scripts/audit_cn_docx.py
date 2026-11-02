#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语文（chinese）Word 交付批量终审（只读）：逐件按**源 JSON**核，不靠人工目视。

为什么单独一份：`audit_bucket_docx.py` 的口径是数学的（22 题 / 150 分 / 120 分钟、册目录带版本前缀
`<edition><册名>`），语文三学段各不同（小学 20 题 100 分 90 分钟 / 初中 24 题 120 分 120 分钟 /
高中 21 题 150 分 150 分钟），且册目录就是「一年级上册」这种裸册名。这里全部改成**从 data/chinese 的
源 JSON 读期望值**（fullScore / duration / 题数 / 卷数 / lessons 数 / 学段字数带），所以换学段换册都不用改脚本。

用法：
    python3 scripts/audit_cn_docx.py                       # 全量
    python3 scripts/audit_cn_docx.py --book 七年级上册       # 单册
    python3 scripts/audit_cn_docx.py --skip-learn          # 只核试卷与讲解

判据（任一不过即 FAIL）：
  试卷  S1 每卷两份 docx 齐全（_试卷 / _参考答案与评分标准）
        S2 试卷首段含「语文（<edition>）<册>」且不含「人教版」；前三段含「<fullScore> 分」与「<duration> 分钟」
        S3 试卷题号集合 == {1..N}（N 取源 JSON 各段 items 合计）；答案卷题号覆盖同 N
        S4 两份都无占位符（TODO/XXX/待补/占位/{{}}/undefined/NaN）
        S5 答案卷含「评分标准」与「解析」
  讲解  L1 源 exam_lectures 每卷有一份 docx，卷头含「（<edition>）」与「讲解」
        L2 六段齐（考什么/考点地图/逐题精讲/复盘/五步学习法/自查）
        L3 汉字数在学段带内（小学 3500–7200 / 初中 4000–7800 / 高中 4500–8800，docx 口径 +2% 余量）
  学层  K1 源 learn/<册>.json 的每篇 lessons 有同名 docx
        K2 七段齐（开场|生活|先说 / 课本原文 / 费曼 / 例题 / 易错 / 五步学习法 / 自查）
        K3 汉字数 1200–2680（docx 多卷头与七个小节标题约 30 字，别套 md 的 2600）
  合订本 B1 学层合订本有「目　录」，目录篇数 == lessons 数
        B2 讲解合订本篇数 == 该册讲解份数；试卷合订本/参考答案合订本篇数 == 该册卷数
        B3 三本副标题/卷头都带「（<edition>）」
"""
import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
ROOT = os.path.expanduser("~/Desktop/学科图谱相关资料")
HAN = re.compile(r"[\u4e00-\u9fa5]")
PLACEHOLDER = re.compile(r"TODO|XXX|待补|占位符|\{\{|\}\}|undefined|NaN")   # 「占位子」是正文，别误伤
SEC7 = [("生活", "开场", "先说"), ("课本原文",), ("费曼",), ("例题",),
        ("易错",), ("五步学习法",), ("自查",)]
SEC6 = ["考什么", "考点地图", "逐题精讲", "复盘", "五步学习法", "自查"]
LEC_BAND = {"小学": (3400, 7400), "初中": (3900, 8000), "高中": (4400, 9000)}


KIND_RANK = {"unit": 0, "mid": 1, "fin": 2}
_CN = "一二三四五六七八九十"


def cn_number(text):
    """「第一单元测试卷」→1；「期中测试卷A」→0（无单元号）。与 build_math_exam_booklet 同口径。"""
    m = re.search(r"第([一二三四五六七八九十\d]+)", text or "")
    if not m:
        return 0
    s = m.group(1)
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch == "十":
            total += (cur or 1) * 10
            cur = 0
        else:
            cur = _CN.index(ch) + 1
    return total + cur


def booklet_order(items):
    """items: [(paper, kind)] → 合订本目录真实顺序"""
    return [x[0] for x in sorted(items, key=lambda t: (KIND_RANK.get(t[1], 9), cn_number(t[0])))]


def count_listed(ps, names, book=None):
    """合订本目录篇数：只认「<n>. <册名>　<篇名>」这种目录行，顺序不作判据（各生成器排序口径不一）。"""
    got = 0
    for n in names:
        mid = (re.escape(book) + "[\u3000 ]+") if book else ""
        pat = re.compile(r"^\d+\.\s*" + mid + re.escape(n) + r"$")
        if any(pat.match(x) for x in ps):
            got += 1
    return got


def dir_sequence(ps, book=None):
    """取合订本目录里「<n>. [册名　]<篇名>」的篇名序列（按出现顺序，去掉序号）。"""
    out = []
    for x in ps:
        m = re.match(r"^\d+\.\s*(.+)$", x)
        if not m:
            continue
        name = m.group(1)
        if book and (name.startswith(book + "\u3000") or name.startswith(book + " ")):
            name = name[len(book) + 1:]
        out.append(name)
    return out


def expect_order(items):
    """合订本应有的目录顺序：unit→期中→期末，同类按单元号、再按卷名字面（A 在 B 前）。"""
    return [x[0] for x in sorted(items, key=lambda t: (KIND_RANK.get(t[1], 9), cn_number(t[0]), t[0]))]


def docx_text(path):
    from docx import Document
    return [p.text.strip() for p in Document(path).paragraphs if p.text.strip()]


def items_of(exam):
    return sum(len(s.get("items") or []) for s in exam.get("sections") or [])


class Audit:
    def __init__(self):
        self.fails, self.checks = [], 0

    def ck(self, cond, msg):
        self.checks += 1
        if not cond:
            self.fails.append(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", default="chinese")
    ap.add_argument("--edition", default="统编版")
    ap.add_argument("--subject", default="语文")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--book", default=None, help="只核某册")
    ap.add_argument("--skip-learn", action="store_true")
    ap.add_argument("--skip-exam", action="store_true")
    ap.add_argument("--skip-lecture", action="store_true")
    a = ap.parse_args()

    D = os.path.join(REPO, "data", a.bucket)
    PAPER_DIR = os.path.join(a.root, "学科图谱原创试卷", a.subject, a.edition)
    LEC_DIR = os.path.join(a.root, "试卷讲解", a.subject, a.edition)
    LEARN_DIR = os.path.join(a.root, "学层精讲", a.subject, a.edition)
    A = Audit()

    books = sorted(b for b in os.listdir(os.path.join(D, "exams"))) if os.path.isdir(os.path.join(D, "exams")) else []
    if a.book:
        books = [b for b in books if b == a.book]
    n_paper = n_lec = n_learn = 0

    # ---------------- 试卷 ----------------
    if not a.skip_exam:
        for book in books:
            src = sorted(glob.glob(os.path.join(D, "exams", book, "*.json")))
            for f in src:
                ex = json.load(open(f, encoding="utf-8"))
                paper, N = ex["paper"], items_of(ex)
                full, dur, stage = ex["fullScore"], ex["duration"], ex["stage"]
                p_sheet = os.path.join(PAPER_DIR, book, f"{paper}_试卷.docx")
                p_ans = os.path.join(PAPER_DIR, book, f"{paper}_参考答案与评分标准.docx")
                if not (os.path.isfile(p_sheet) and os.path.isfile(p_ans)):
                    A.ck(False, f"缺 docx：{book}/{paper}")
                    continue
                n_paper += 1
                ps, pa = docx_text(p_sheet), docx_text(p_ans)
                head, top3 = ps[0] if ps else "", " ".join(ps[:3])
                A.ck(f"（{a.edition}）" in head and book in head and "人教版" not in head,
                     f"卷头错：{book}/{paper} → {head[:40]}")
                A.ck(f"{full} 分" in top3 and f"{dur} 分钟" in top3,
                     f"卷头分值/时长缺：{book}/{paper}")
                nums = {int(m.group(1)) for x in ps for m in [re.match(r"^(\d{1,2})．", x)] if m}
                A.ck(nums == set(range(1, N + 1)), f"试卷题号不齐（{len(nums)}/{N}）：{book}/{paper}")
                ans_nums = {int(m.group(1)) for x in pa for m in [re.match(r"^(\d{1,2})．", x)] if m}
                A.ck(ans_nums == set(range(1, N + 1)), f"答案卷题号不齐（{len(ans_nums)}/{N}）：{book}/{paper}")
                body = " ".join(ps) + " ".join(pa)
                A.ck(not PLACEHOLDER.search(body), f"占位符残留：{book}/{paper}")
                ab = " ".join(pa)
                A.ck("评分标准" in ab, f"答案卷无评分标准：{book}/{paper}")
                A.ck("解析" in ab, f"答案卷无解析：{book}/{paper}")

    # ---------------- 讲解 ----------------
    if not a.skip_lecture:
        for book in books:
            src = sorted(glob.glob(os.path.join(D, "exam_lectures", book, "*.json")))
            for f in src:
                lec = json.load(open(f, encoding="utf-8"))
                exf = os.path.join(D, "exams", book, f"{lec['paper']}.json")
                stage = json.load(open(exf, encoding="utf-8"))["stage"] if os.path.isfile(exf) else "初中"
                p = os.path.join(LEC_DIR, book, f"{lec['paper']}_讲解.docx")
                if not os.path.isfile(p):
                    A.ck(False, f"缺讲解 docx：{book}/{lec['paper']}")
                    continue
                n_lec += 1
                ps = docx_text(p)
                head, body = ps[0] if ps else "", " ".join(ps)
                A.ck(f"（{a.edition}）" in head and "讲解" in head, f"讲解卷头错：{book}/{lec['paper']}")
                miss = [k for k in SEC6 if k not in body]
                A.ck(not miss, f"讲解缺段 {miss}：{book}/{lec['paper']}")
                n = len(HAN.findall(body))
                lo, hi = LEC_BAND[stage]
                A.ck(lo <= n <= hi, f"讲解字数出带 {n}（{stage} {lo}–{hi}）：{book}/{lec['paper']}")
                A.ck(not PLACEHOLDER.search(body), f"讲解占位符：{book}/{lec['paper']}")

    # ---------------- 学层 ----------------
    if not a.skip_learn:
        for f in sorted(glob.glob(os.path.join(D, "learn", "*.json"))):
            data = json.load(open(f, encoding="utf-8"))
            book, lessons = data["book"], data.get("lessons") or []
            if a.book and book != a.book:
                continue
            for L in lessons:
                p = os.path.join(LEARN_DIR, book, f"{L['title']}.docx")
                if not os.path.isfile(p):
                    A.ck(False, f"缺学层 docx：{book}/{L['title']}")
                    continue
                n_learn += 1
                ps = docx_text(p)
                head, body = ps[0] if ps else "", " ".join(ps)
                A.ck(f"（{a.edition}）" in head and book in head, f"学层卷头错：{book}/{L['title']}")
                miss = [k[0] for k in SEC7 if not any(w in body for w in k)]
                A.ck(not miss, f"学层缺段 {miss}：{book}/{L['title']}")
                n = len(HAN.findall(body))
                A.ck(1200 <= n <= 2680, f"学层字数出带 {n}：{book}/{L['title']}")
                A.ck(not PLACEHOLDER.search(body), f"学层占位符：{book}/{L['title']}")

    # ---------------- 合订本 ----------------
    b_ok = 0
    if not a.book or a.book:
        # 学层合订本
        for f in sorted(glob.glob(os.path.join(D, "learn", "*.json"))):
            data = json.load(open(f, encoding="utf-8"))
            book, lessons = data["book"], data.get("lessons") or []
            if a.book and book != a.book:
                continue
            p = os.path.join(LEARN_DIR, book, "_合订本", f"{book}_学层精讲合订本.docx")
            if not os.path.isfile(p):
                A.ck(False, f"缺学层合订本：{book}")
                continue
            b_ok += 1
            ps = docx_text(p)
            A.ck(len(ps) > 2 and "目" in ps[2] and "录" in ps[2], f"合订本无目录：{book}")
            A.ck(f"（{a.edition}）" in " ".join(ps[:3]), f"合订本副标题版本错：{book}")
            titles = [L["title"] for L in lessons]
            got = count_listed(ps, titles)
            A.ck(got == len(lessons), f"学层合订本篇数 {got} ≠ {len(lessons)}：{book}")
            A.ck(dir_sequence(ps)[:len(titles)] == titles, f"学层合订本目录顺序错：{book}")
        # 讲解合订本
        for bdir in sorted(glob.glob(os.path.join(D, "exam_lectures", "*"))):
            book = os.path.basename(bdir)
            if a.book and book != a.book:
                continue
            srcp = sorted(glob.glob(os.path.join(bdir, "*.json")))
            _js = [json.load(open(x, encoding="utf-8")) for x in srcp]
            papers = expect_order([(j["paper"], j.get("kind")) for j in _js])
            want = len(papers)
            p = os.path.join(LEC_DIR, book, "_合订本", f"{book}_试卷讲解合订本.docx")
            if not os.path.isfile(p):
                A.ck(False, f"缺讲解合订本：{book}")
                continue
            b_ok += 1
            ps = docx_text(p)
            A.ck(f"（{a.edition}）" in " ".join(ps[:3]), f"讲解合订本副标题版本错：{book}")
            got = count_listed(ps, papers)
            A.ck(got == want, f"讲解合订本篇数 {got} ≠ {want}：{book}")
            A.ck(dir_sequence(ps)[:len(papers)] == papers, f"讲解合订本目录顺序错：{book}")
        # 试卷 / 答案合订本
        for bdir in sorted(glob.glob(os.path.join(D, "exams", "*"))):
            book = os.path.basename(bdir)
            if a.book and book != a.book:
                continue
            srcp = sorted(glob.glob(os.path.join(bdir, "*.json")))
            _js = [json.load(open(x, encoding="utf-8")) for x in srcp]
            pnames = expect_order([(j["paper"], j.get("kind")) for j in _js])
            want = len(pnames)
            for tag in ("试卷合订本", "参考答案合订本"):
                p = os.path.join(PAPER_DIR, book, "_合订本", f"{book}_{tag}.docx")
                if not os.path.isfile(p):
                    A.ck(False, f"缺{tag}：{book}")
                    continue
                b_ok += 1
                ps = docx_text(p)
                A.ck(f"（{a.edition}）" in " ".join(ps[:3]), f"{tag}卷头版本错：{book}")
                got = count_listed(ps, pnames, book=book)   # 试卷合订本目录 = 「册名　卷名」
                A.ck(dir_sequence(ps, book=book)[:len(pnames)] == pnames, f"{tag}目录顺序错：{book}")
                A.ck(got == want, f"{tag}篇数 {got} ≠ {want}：{book}")

    print(f"试卷 {n_paper} 卷 ×2 份 / 讲解 {n_lec} 份 / 学层 {n_learn} 篇 / 合订本 {b_ok} 本")
    print(f"判据 {A.checks} 项 → {'全部通过' if not A.fails else f'{len(A.fails)} 项不通过'}")
    for m in A.fails[:40]:
        print("  ❌", m)
    if len(A.fails) > 40:
        print(f"  …… 另有 {len(A.fails)-40} 项")
    return 1 if A.fails else 0


if __name__ == "__main__":
    sys.exit(main())
