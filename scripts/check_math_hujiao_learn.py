#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版数学「学层精讲」自检：python3 scripts/check_math_hujiao_learn.py data/math-hujiao/learn/<册>.json

与 check_math_learn_md.py 同口径（七段逐字、1200–2600 汉字、words ±50、≥2 处课本原文、
❌/✅ 各 ≥2、例题 ≥2、自查 ≥3、五步五条各 ≥25 汉字且节 350–700、序号不粘连、无 LaTeX/HTML/表格），
差别只有两处：课时点按 level=lesson 认定；课本原文回表用沪教版教材逐页 TXT（/tmp/mhj/*.txt，缺则跳过）。
"""
import difflib, json, os, re, sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
D = f"{REPO}/data/math-hujiao"
TXT = {"沪教版必修第一册": "h1", "沪教版必修第二册": "h2", "沪教版必修第三册": "h3",
       "沪教版选择性必修第一册": "x1", "沪教版选择性必修第二册": "x2"}
SEC = ["开场", "课本原文", "费曼翻译", "例题", "易错", "五步学习法", "自查"]
STEP_KEYS = ["锻炼", "第一个知识点", "积微", "对标", "杠铃"]
errs = []


def E(m): errs.append(m)
def hanzi(s): return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))
def qnorm(s): return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("用法：python3 scripts/check_math_hujiao_learn.py data/math-hujiao/learn/<册>.json"); sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    book = data.get("book")
    if book not in TXT:
        print(f"❌ book 非法：{book}"); sys.exit(1)
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    ke = {t["id"]: t for t in topics if t.get("level") == "lesson" and t["chapter"].startswith(f"{book} ")}
    _dir = f"/tmp/mhj/{TXT[book]}"
    txt_path = f"{_dir}/all.txt"
    if os.path.isdir(_dir) and not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as fh:
            for pf in sorted(__import__("glob").glob(f"{_dir}/p*.txt")):
                fh.write(open(pf, encoding="utf-8", errors="ignore").read())
    src = ""
    if os.path.exists(txt_path):
        src = qnorm(open(txt_path, encoding="utf-8", errors="ignore").read())
    else:
        print("（教材 TXT 不在本机，跳过课本原文回表）")
    lessons = data.get("lessons") or []
    if not lessons: E("lessons 为空")
    seen = set()
    for L in lessons:
        tid = L.get("topicId"); nm = L.get("title") or tid
        if tid not in ke:
            E(f"{nm}: topicId 不属于本册课时点（{tid}）"); continue
        if tid in seen: E(f"{nm}: topicId 重复")
        seen.add(tid)
        md = L.get("markdown") or ""
        n = hanzi(md)
        if not (1200 <= n <= 2600): E(f"{nm}: 汉字数 {n}，应 1200–2600")
        if abs((L.get("words") or 0) - n) > 50: E(f"{nm}: words {L.get('words')} ≠ 实际 {n}")
        for s in SEC:
            if s not in md: E(f"{nm}: 缺「{s}」小节")
        cur, quotes = "", []
        for ln in md.split("\n"):
            if ln.startswith("## "): cur = ln; continue
            if ln.startswith("> ") and "课本原文" in cur:
                q = ln[2:].strip()
                if hanzi(q) >= 8: quotes.append(q)
        if len(quotes) < 2: E(f"{nm}: 课本原文引用不足 2 处（现 {len(quotes)}）")
        if src:
            for q in quotes:
                qq = qnorm(q)
                if qq in src: continue
                hit = False
                for i in range(0, max(1, len(qq) - 10), 5):
                    seg = qq[i:i + 24]
                    if seg and seg in src: hit = True; break
                if not hit and difflib.SequenceMatcher(None, qq, src).find_longest_match(0, len(qq), 0, len(src)).size < 0.7 * len(qq):
                    E(f"{nm}: 引文未在教材命中 → {q[:24]}")
        if md.count("❌") < 2 or md.count("✅") < 2: E(f"{nm}: ❌/✅ 各需 ≥2")
        if len(re.findall(r"例\s*题?\s*[12２１]", md)) < 2: E(f"{nm}: 例题不足 2 道")
        if len(re.findall(r"- \[ \]", md)) < 3: E(f"{nm}: 自查题不足 3 道")
        for k in STEP_KEYS:
            if k not in md: E(f"{nm}: 五步学习法缺「{k}」")
        sec = [x for x in re.split(r"\n(?=## )", md) if "五步学习法" in x.split("\n")[0]]
        if not sec:
            E(f"{nm}: 缺「五步学习法」小节")
        else:
            steps = [ln for ln in sec[0].split("\n") if re.match(r"^\d\.\s", ln.strip())]
            if len(steps) < 5: E(f"{nm}: 五步只有 {len(steps)} 条")
            for st in steps:
                if hanzi(st) < 25: E(f"{nm}: 五步某条不足 25 汉字 → {st[:16]}")
            sw = hanzi(sec[0])
            if not (350 <= sw <= 700): E(f"{nm}: 五步节 {sw} 汉字，应 350–700")
        ls = md.split("\n")
        for a, b in zip(ls, ls[1:]):
            if re.match(r"^\d+\.\s", a.strip()) and re.match(r"^\d+\.\s", b.strip()):
                E(f"{nm}: 序号条目粘连未分段 → {a.strip()[:16]}"); break
        if md.count("易错") < 1: E(f"{nm}: 缺易错点拨")
        if re.search(r"\$[^$]+\$|\\\(|\\\[", md): E(f"{nm}: 出现 LaTeX 语法")
        if re.search(r"</?[a-zA-Z]+[^>]*>", md): E(f"{nm}: 出现 HTML 标签")
        if re.match(r"^\|.*\|$", md, re.M): E(f"{nm}: 出现 Markdown 表格")
    print(f"册：{book} · 课时 {len(lessons)} · 覆盖课时点 {len(seen)}/{len(ke)}")
    if errs:
        print(f"\n❌ {len(errs)} 条问题：")
        for e in errs[:25]: print("  -", e)
        sys.exit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
