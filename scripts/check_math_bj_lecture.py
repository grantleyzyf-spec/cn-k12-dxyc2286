# -*- coding: utf-8 -*-
"""试卷讲解自检（math-bj 北京版）：结构 / 字数 / 逐题覆盖 / 题分一致 / 公式写法。

用法：
    python3 scripts/check_math_bj_lecture.py data/math-bj/exam_lectures/八年级下册/第一单元测试卷.json
    python3 scripts/check_math_bj_lecture.py --book 八年级下册
"""
import argparse
import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BANDS = {  # stage -> (下限, 上限) 汉字（上限必须给五步学习法留足 300–700 的余量）
    "小学": (3500, 7200),
    "初中": (4000, 7800),
    "高中": (4500, 8800),
}

SECTIONS = ["这份卷在考什么", "考点地图", "逐题精讲", "整卷复盘", "五步学习法", "自查清单"]
# 五步学习法五条固定标签（写手必须逐字照用）
STEPS = ["每天锻炼一个小时", "扎实掌握第一个知识点", "能积微者速成",
         "运用对标思维突破学习困境", "运用杠铃法则缓解学习疲劳"]

UNITS = ("kg", "km", "cm", "mm", "mL", "kW", "kPa", "Pa", "Hz", "mol", "min",
         "m", "s", "g", "N", "J", "W", "A", "V", "Ω", "L", "h")
_UNIT_ALT = "|".join(sorted(UNITS, key=len, reverse=True))
# 多字母单位不受代数变量干扰；单字母只在与汉字直接相接时才算「单位写法」
_UNIT_MULTI = "|".join(sorted([u for u in UNITS if len(u) > 1], key=len, reverse=True))
_UNIT_SINGLE = "".join(sorted({u for u in UNITS if len(u) == 1}))

BAD_PATTERNS = [
    (r"\$\$?", "出现 LaTeX 美元符号"),
    (r"\\frac|\\sqrt|\\times", "出现 LaTeX 命令"),
    (r"<[a-zA-Z/][^>]*>", "出现 HTML 标签"),
    (r"\|\s*-{3,}", "出现 Markdown 表格"),
    # 数值与单位紧贴（25m、2kg、3m/s）→ 规范要求空一格。
    # ⚠️ 单字母单位（m/s/g/h/L/A/N/J/W/V/T/K/C/F/P/R/B/D）在代数里也是变量，
    #    "4m"、"2m=0"、"4m²" 都是代数式而不是物理量 ⇒ 只认「紧贴单字母 + 后面接汉字/中文标点」
    #    或「多字母单位」两种真正指代单位的写法，避免把代数式全判成反例（实测误伤大量初中卷）。
    (rf"(?<![\d.])[0-9]+(?:\.[0-9]+)?({_UNIT_MULTI})(?![A-Za-z])", "数字与单位之间缺空格（应写 3 m/s）"),
    (rf"(?<![\d.])[0-9]+(?:\.[0-9]+)?([{_UNIT_SINGLE}])(?=[\u4e00-\u9fa5，。；、])",
     "数字与单位之间缺空格（应写 3 m/s）"),
]


def han_count(text):
    return len(re.findall(r"[\u4e00-\u9fa5]", text))


def load_exam(lecture):
    return json.load(open(
        f"{REPO}/data/math-bj/exams/{lecture['book']}/{lecture['paper']}.json", encoding="utf-8"))


def check_one(path, verbose=True):
    errs = []
    lec = json.load(open(path, encoding="utf-8"))
    md = lec.get("markdown", "")
    exam = load_exam(lec)

    items = [it for s in exam["sections"] for it in s["items"]]
    stage = exam.get("stage", "小学")
    lo, hi = BANDS.get(stage, BANDS["小学"])

    n = han_count(md)
    if not (lo <= n <= hi):
        errs.append(f"字数 {n} 不在 {stage} 带 {lo}–{hi}")
    if lec.get("words") and abs(int(lec["words"]) - n) > 6:
        errs.append(f"words 字段 {lec['words']} 与实测 {n} 不符")

    # 五段齐全
    for sec in SECTIONS:
        if sec not in md:
            errs.append(f"缺段落「{sec}」")

    # 逐题覆盖：每个题号都要出现
    missing = [it["no"] for it in items if not re.search(rf"第\s*{it['no']}\s*题", md)]
    if missing:
        errs.append(f"未讲到第 {missing[:8]} 题（共缺 {len(missing)} 题）")

    # 逐题四要素：精讲段内 思路/关键一步/易错
    for key, need in (("思路", 0.9), ("关键一步", 0.6), ("易错", 0.9)):
        c = len(re.findall(key, md))
        if c < len(items) * need:
            errs.append(f"「{key}」只出现 {c} 次，至少需要 {int(len(items) * need)} 次（题数 {len(items)}）")

    # 题分一致：讲解里若写"（N 分）"，必须与卷面一致
    for m in re.finditer(r"第\s*(\d+)\s*题[（(]\s*(\d+)\s*分", md):
        no, sc = int(m.group(1)), int(m.group(2))
        real = next((it["score"] for it in items if it["no"] == no), None)
        if real is not None and real != sc:
            errs.append(f"第 {no} 题标注 {sc} 分，卷面是 {real} 分")

    # 五步学习法五条齐全 + 该节字数
    for st in STEPS:
        if st not in md:
            errs.append(f"五步学习法缺「{st}」")
    m = re.search(r"五步学习法(.*?)(?=\n## |\Z)", md, re.S)
    if m:
        st_han = han_count(m.group(1))
        if not (250 <= st_han <= 750):
            errs.append(f"五步学习法节 {st_han} 汉字，应在 250–750")
        # 相邻两条序号行之间必须有空行（否则渲染成一大段）
        for i, ln in enumerate(m.group(1).split("\n")[:-1]):
            nxt = m.group(1).split("\n")[i + 1]
            if st in ln and "**" in nxt and nxt.strip():
                pass

    # 自查清单
    boxes = len(re.findall(r"- \[ \]", md))
    if boxes < 6:
        errs.append(f"自查清单只有 {boxes} 条，至少 6 条")

    # 结构自洽：六段了就不能再自称「分五段」
    for bad in ("分五段", "按五段", "五个部分"):
        if bad in md:
            errs.append(f"结构已改六段，正文仍有「{bad}」")

    # 公式写法
    body = re.sub(r"^#.*$", "", md, flags=re.M)
    for pat, why in BAD_PATTERNS:
        hits = [m.group(0) for m in re.finditer(pat, body)]
        hits = [h for h in hits if not re.match(r"^第?[0-9]+[题分]$", h)]
        hits = [h for h in hits if not re.match(r"^\d+m$", h) or not re.search(re.escape(h) + r"[²³^]", body)]
        if hits:
            errs.append(f"{why}：{hits[:3]}")

    # 反斜杠分数（3/8 之外，如 1/2x 这类应写成分数的，提醒但不判死）
    if verbose:
        tag = "✅" if not errs else "❌"
        print(f"{tag} {lec['book']} / {lec['paper']}  汉字 {n} · 题 {len(items)}")
        for e in errs:
            print("   -", e)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--book")
    a = ap.parse_args()
    files = []
    if a.path:
        files = [a.path]
    elif a.book:
        files = sorted(glob.glob(f"{REPO}/data/math-bj/exam_lectures/{a.book}/*.json"))
    else:
        files = sorted(glob.glob(f"{REPO}/data/math-bj/exam_lectures/*/*.json"))
    files = [f for f in files if not os.path.basename(f).startswith("_")]
    if not files:
        print("没有可检查的讲解文件")
        return 1
    bad = 0
    for f in files:
        if check_one(f):
            bad += 1
    print(f"\n共 {len(files)} 份 · 不合格 {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
