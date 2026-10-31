# -*- coding: utf-8 -*-
"""学层（学生版精讲）自检器。

用法：python3 scripts/check_math_learn_md.py data/math/learn/<册>.json

检查项：
 1 结构：book 合法；每课时 topicId 属于**本册**课时点；title/markdown/words 齐全
 2 字数：汉字数 1000–2000（去掉 Markdown 符号、空白、标点后统计汉字）
 3 六段结构：开场 / 课本原文 / 费曼翻译 / 例题精讲 / 易错点拨 / 自查 六个小标题都在
 4 引文：`> ` 块引用至少 2 处，每处 ≥8 汉字，且必须能在本册教材正文里**逐字命中**（去标点比对）
 5 例题 ≥2 道：正文出现「例」题目段落（`### 例题` 或「例题」小节下 ≥2 个「**例」）
 6 易错 ≥2 条；自查 ≥3 题（`- [ ]`）
 7 禁用：LaTeX（$…$、\\( \\)）、HTML 标签、Markdown 表格
"""
import glob
import json
import os
import re
import sys

import difflib

import fitz

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math"
XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学"
BOOKS = {
 "一年级上册": ("小学", "人教版"), "一年级下册": ("小学", "人教版"),
 "二年级上册": ("小学", "人教版"), "二年级下册": ("小学", "人教版"),
 "三年级上册": ("小学", "人教版"), "三年级下册": ("小学", "人教版"),
 "四年级上册": ("小学", "人教版"), "五年级上册": ("小学", "人教版"),
 "六年级上册": ("小学", "人教版"),
 "七年级上册": ("初中", "人教版"), "七年级下册": ("初中", "人教版"),
 "八年级上册": ("初中", "人教版"), "八年级下册": ("初中", "人教版"),
 "九年级上册": ("初中", "人教版"),
 "必修第一册": ("高中", "人教版（A版）"), "必修第二册": ("高中", "人教版（A版）"),
 "选择性必修第一册": ("高中", "人教版（A版）"), "选择性必修第二册": ("高中", "人教版（A版）"),
 "选择性必修第三册": ("高中", "人教版（A版）"),
}
SEC = ["开场", "课本原文", "费曼翻译", "例题", "易错", "五步学习法", "自查"]
STEP_KEYS = ["锻炼", "第一个知识点", "积微", "对标", "杠铃"]   # 五步学习法五步的关键词，缺一即不合格
errs = []


def E(m):
    errs.append(m)


def hanzi(s):
    return re.findall(r"[\u4e00-\u9fa5]", s or "")


def fuzzy_hit(q, src, thr=0.88):
    """OCR 回表用：引文与 OCR 文本相差个别符号（²与2、−与一）时，按 88% 相似度在窗口内判定。"""
    if len(q) < 12:
        return False
    for start in range(0, max(1, len(q) - 6), 6):
        anchor = q[start:start + 6]
        if len(anchor) < 6:
            break
        pos = src.find(anchor)
        guard = 0
        while pos >= 0 and guard < 50:
            s0 = max(0, pos - start)
            seg = src[s0:s0 + len(q)]
            if difflib.SequenceMatcher(None, q, seg).ratio() >= thr:
                return True
            pos = src.find(anchor, pos + 1)
            guard += 1
    return False


def qnorm(s):
    return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")


def book_pdf(book):
    stage, ed = BOOKS[book]
    pats = glob.glob(f"{XI}/{stage}/{ed}/*.pdf")
    mg = re.search(r"([一二三四五六七八九])年级", book)   # 七/八/九 也是初中册，别只写一二三四五六
    ms = re.search(r"([上下])册", book)
    for p in pats:
        b = os.path.basename(p)
        if mg and ms:
            if mg.group(1) in b and ms.group(1) in b and "年级" in b:
                return p
        elif book.replace("选择性", "") in b or book in b:
            return p
    # 高中：按 A版 选必/必修 匹配
    key = book.replace("第", "").replace("册", "")
    for p in pats:
        b = os.path.basename(p)
        if all(ch in b for ch in ("选必" if "选择性" in book else "必修",)):
            num = {"一": "1", "二": "2", "三": "3"}.get(book[-2], "")
            if num and num in b:
                return p
    return None


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("用法：python3 scripts/check_math_learn_md.py data/math/learn/<册>.json")
        sys.exit(1)
    path = sys.argv[1]
    data = json.load(open(path, encoding="utf-8"))
    book = data.get("book")
    if book not in BOOKS:
        print(f"❌ book 非法：{book}")
        sys.exit(1)
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    ke = {t["id"]: t for t in topics
          if " · " in (t.get("chapter") or "") and (t.get("chapter") or "").startswith(f"{book} ")}
    pdf = book_pdf(book)
    src = ""
    src_note = ""
    if pdf:
        doc = fitz.open(pdf)
        src = qnorm("".join(doc[i].get_text() for i in range(len(doc))))
    else:
        E(f"找不到本册教材 PDF：{book}")
    # 扫描本只有几十字的文字层（封面），引文永远回表失败 ⇒ 回退到 OCR 全册文本
    if pdf and len(src) < 5000:
        OCR = {
            "必修第一册": "必修第1册", "必修第二册": "必修第2册",
            "选择性必修第一册": "选必第1册", "选择性必修第二册": "选必第2册",
            "选择性必修第三册": "选必第3册",
        }
        name = OCR.get(book)
        ocr = f"{REPO}/data/math/ocr_highschool/{name}.txt" if name else None
        if ocr and os.path.exists(ocr):
            _raw = open(ocr, encoding="utf-8", errors="ignore").read()
            src = qnorm(_raw)
            # OCR 会把变量字母认成生僻汉字（l→犾、x→狓、n→狀），逐字比对必失配 ⇒ 另存"只留汉字"的源做二级回表
            src_han = "".join(re.findall(r"[\u4e00-\u9fa5]", _raw))
            src_note = f"（本册为扫描本，引文按 OCR 文本回表：{os.path.basename(ocr)}）"
        else:
            E(f"{book}: PDF 无文字层且找不到 OCR 回表源")
    else:
        src_han = ""

    # OCR 误识豁免（须有目视证据，见 _ocr_waivers.json）
    waivers = set()
    wf = f"{D}/learn/_ocr_waivers.json"
    if os.path.exists(wf):
        wj = json.load(open(wf, encoding="utf-8"))
        for it in wj.get(book, []) or []:
            waivers.add(qnorm(it.get("quote") or ""))
    lessons = data.get("lessons") or []
    n_waived = 0
    if not lessons:
        E("lessons 为空")
    seen = set()
    for L in lessons:
        tid = L.get("topicId")
        nm = L.get("title") or tid
        if tid not in ke:
            E(f"{nm}: topicId 不属于本册课时点（{tid}）")
            continue
        if tid in seen:
            E(f"{nm}: topicId 重复")
        seen.add(tid)
        md = L.get("markdown") or ""
        n = len(hanzi(md))
        # 教学正文 1000–2000（用户口径）＋ 五步学习法 400–600 ⇒ 全篇 1200–2600
        if not (1200 <= n <= 2600):
            E(f"{nm}: 汉字数 {n}，应在 1200–2600（正文 1000–2000 ＋ 五步学习法 400–600）")
        if abs((L.get("words") or 0) - n) > 50:
            E(f"{nm}: words 字段写 {L.get('words')}，实际 {n}")
        for s in SEC:
            if s not in md:
                E(f"{nm}: 缺「{s}」小节")
        # 只校验「课本原文」那一节里的块引用：❌/✅ 对照也用 `> ` 排版，不能一起当引文回表
        cur, quotes = "", []
        for ln in md.split("\n"):
            if ln.startswith("## "):
                cur = ln
                continue
            if ln.startswith("> ") and "课本原文" in cur:
                q = ln[2:].strip()
                if len(hanzi(q)) >= 8:
                    quotes.append(q)
        if len(quotes) < 2:
            E(f"{nm}: 课本原文引用不足 2 处（现 {len(quotes)}）")
        fuzzy_ok = 0
        for q in quotes:
            if not src:
                continue
            qq = qnorm(q)
            if qq in src:
                continue
            if qq in waivers:
                n_waived += 1
                continue
            if src_note and (fuzzy_hit(qq, src) or
                             fuzzy_hit("".join(re.findall(r"[\u4e00-\u9fa5]", q)), src_han, 0.9)):
                fuzzy_ok += 1       # 扫描本/OCR 源：允许符号级（²/2、−/一、l/犾）差异
                continue
            E(f"{nm}: 引文未在教材逐字命中 → {q[:24]}")
        if md.count("❌") < 2 or md.count("✅") < 2:
            E(f"{nm}: 例题需至少 2 处「❌ 常见错法 / ✅ 正确做法」对照")
        # 例题：出现 2 个及以上「例 1/例1/例2」或「**例」
        # 「例题 1」「例1」「**例 2**」都算，正则要允许「题」字夹在中间
        if len(re.findall(r"例\s*题?\s*[12２１]", md)) < 2:
            E(f"{nm}: 例题不足 2 道")
        if len(re.findall(r"- \[ \]", md)) < 3:
            E(f"{nm}: 自查题不足 3 道（用 - [ ] 列表）")
        # 五步学习法：五步齐、每条 ≥25 汉字（防一句话凑数）
        for k in STEP_KEYS:
            if k not in md:
                E(f"{nm}: 五步学习法缺「{k}」这一步")
        sec = re.split(r"\n(?=## )", md)
        sec = [x for x in sec if "五步学习法" in x.split("\n")[0]]
        if not sec:
            E(f"{nm}: 缺「五步学习法」小节")
        else:
            steps = [ln for ln in sec[0].split("\n") if re.match(r"^\d\.\s", ln.strip())]
            if len(steps) < 5:
                E(f"{nm}: 五步学习法只有 {len(steps)} 条（应 5 条）")
            for st in steps:
                if len(hanzi(st)) < 25:
                    E(f"{nm}: 五步学习法某条不足 25 汉字 → {st[:18]}")
            sw = len(hanzi(sec[0]))
            if not (350 <= sw <= 700):
                E(f"{nm}: 五步学习法节 {sw} 汉字，应在 350–700")
        # 序号条目之间必须有空行：粘连会让渲染器把五步并成一段（用户已就此返修一次）
        ls = md.split("\n")
        for a, b in zip(ls, ls[1:]):
            if re.match(r"^\d+\.\s", a.strip()) and re.match(r"^\d+\.\s", b.strip()):
                E(f"{nm}: 序号条目粘连未分段 → {a.strip()[:16]}")
                break
        if md.count("易错") < 1:
            E(f"{nm}: 缺易错点拨")
        if re.search(r"\$[^$]+\$|\\\\\(|\\\\\[", md):
            E(f"{nm}: 出现 LaTeX 语法，改用 Unicode 符号")
        if re.search(r"</?[a-zA-Z]+[^>]*>", md):
            E(f"{nm}: 出现 HTML 标签")
        if re.match(r"^\|.*\|$", md, re.M):
            E(f"{nm}: 出现 Markdown 表格")

    print(f"册：{book} · 课时 {len(lessons)} · 覆盖课时点 {len(seen)}/{len(ke)}{src_note}"
          + (f" · 引用豁免 {n_waived} 条（OCR 误识，已目视核对）" if n_waived else ""))
    if errs:
        print(f"\n❌ {len(errs)} 条问题：")
        for e in errs[:30]:
            print("  -", e)
        if len(errs) > 30:
            print(f"  …另有 {len(errs)-30} 条")
        sys.exit(1)
    print("✅ 自检通过")


if __name__ == "__main__":
    main()
