#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""青岛版数学「学层精讲」自检：python3 scripts/check_math_bsd_learn.py data/math-bsd/learn/<册>.json

与 check_math_learn_md.py 同口径（七段逐字、1200–2600 汉字、words ±50、≥2 处课本原文、
❌/✅ 各 ≥2、例题 ≥2、自查 ≥3、五步五条各 ≥25 汉字且节 350–700、序号不粘连、无 LaTeX/HTML/表格），
差别只有两处：课时点按 level=lesson 认定；课本原文回表用青岛版教材逐页 TXT（/tmp/mhj/*.txt，缺则跳过）。
"""
import difflib, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 按脚本位置定位仓库，本地与 CI 通用（别写死 ~/Desktop 绝对路径）
D = f"{REPO}/data/math-bsd"
TXT = {"一年级上册": "mbsd1a", "一年级下册": "mbsd1b", "二年级上册": "mbsd2a", "二年级下册": "mbsd2b", "三年级上册": "mbsd3a", "三年级下册": "mbsd3b", "四年级上册": "mbsd4a", "四年级下册": "mbsd4b", "五年级上册": "mbsd5a", "五年级下册": "mbsd5b", "六年级上册": "mbsd6a", "六年级下册": "mbsd6b", "七年级上册": "mbsd7a", "七年级下册": "mbsd7b", "八年级上册": "mbsd8a", "八年级下册": "mbsd8b", "九年级上册": "mbsd9a",
       "必修第一册": "mbsdbx1", "必修第二册": "mbsdbx2", "选择性必修第一册": "mbsdxb1", "选择性必修第二册": "mbsdxb2"}
# 永久 textpack（教材切片落盘；/tmp 只是历史遗留的临时源，缺则回落到这里）
TXT_ROOT = os.path.expanduser("~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/数学/北师大版")
SEC = ["开场", "课本原文", "费曼翻译", "例题", "易错", "五步学习法", "自查"]
STEP_KEYS = ["锻炼", "第一个知识点", "积微", "对标", "杠铃"]
errs = []


def E(m): errs.append(m)
def hanzi(s): return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))
def qnorm(s): return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("用法：python3 scripts/check_math_bsd_learn.py data/math-bsd/learn/<册>.json"); sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    book = data.get("book")
    if book not in TXT:
        print(f"❌ book 非法：{book}"); sys.exit(1)
    topics = json.load(open(f"{D}/topics.json", encoding="utf-8"))
    # 青岛版 topics.json 多数没有 level 字段：课时点用「chapter 含 · 分层」判（单元行不含 ·）
    ke = {t["id"]: t for t in topics
          if (t.get("level") == "lesson" or ("level" not in t and " · " in t["chapter"]))
          and t["chapter"].startswith(f"{book} ")}
    _dir = f"/tmp/mbsd/{TXT[book]}/ocr"
    txt_path = f"{_dir}/all.txt"
    if os.path.isdir(_dir) and not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as fh:
            for pf in sorted(__import__("glob").glob(f"{_dir}/p*.txt")):
                fh.write(open(pf, encoding="utf-8", errors="ignore").read())
    srcs = []
    if os.path.exists(txt_path):
        srcs.append(qnorm(open(txt_path, encoding="utf-8", errors="ignore").read()))
        print(f"（回表源①＝/tmp 旧 OCR：{txt_path}）")
    # 永久 textpack：<TXT_ROOT>/<学段>/<册>/{ocr/pNNN.txt, 整册全文.txt}
    # 与 /tmp 那份常是**两次不同识别**，因此两源并列：任一中逐字命中即算命中，
    # 否则工人只能挑「双源都干净」的句子，会弃掉大量合格原文。
    import glob as _glob
    base = next((p for p in _glob.glob(os.path.join(TXT_ROOT, "*", book)) if os.path.isdir(p)), "")
    if base:
        pages = sorted(_glob.glob(os.path.join(base, "ocr", "p*.txt")))
        raw = "".join(open(p, encoding="utf-8", errors="ignore").read() for p in pages)
        full = os.path.join(base, "整册全文.txt")
        if os.path.exists(full):
            fullt = open(full, encoding="utf-8", errors="ignore").read()
            if len(qnorm(raw)) < 6000 and len(fullt) > len(raw):
                raw = fullt
        sp = qnorm(raw)
        if sp and sp not in srcs:
            srcs.append(sp)
            print(f"（回表源②＝永久 textpack：{base}）")
    if not srcs:
        print("（教材 TXT 不在本机，跳过课本原文回表）")
    # 逐页 OCR 是字体损坏的产物（如 s3a 全册仅约 1900 汉字）时改用 PDF 文字层 full.txt 回表
    full_txt = f"/tmp/msj/{TXT[book]}/full.txt"
    if os.path.exists(full_txt):
        src_full = qnorm(open(full_txt, encoding="utf-8", errors="ignore").read())
        if all(len(s) < 6000 for s in srcs) and len(src_full) > max((len(s) for s in srcs), default=0):
            srcs = [src_full]
            print("（逐页 OCR 汉字过少，改用 PDF 文字层 full.txt 回表）")
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
        if srcs:
            for q in quotes:
                qq = qnorm(q)
                if any(qq in s for s in srcs): continue
                hit = False
                for s in srcs:
                    for i in range(0, max(1, len(qq) - 10), 5):
                        seg = qq[i:i + 24]
                        if seg and seg in s: hit = True; break
                    if hit: break
                if not hit and not any(
                        difflib.SequenceMatcher(None, qq, s).find_longest_match(0, len(qq), 0, len(s)).size >= 0.7 * len(qq)
                        for s in srcs):
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
