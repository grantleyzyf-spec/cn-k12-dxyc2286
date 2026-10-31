# -*- coding: utf-8 -*-
"""把学层正文里从 OCR 漏进来的「数学斜体字形」还原成正常拉丁字母。

背景：高中教材 PDF 的文字层（与提取出的 OCR 文本）把数学斜体 a/b/x 等映射成了生僻汉字
（犪=a、犫=b、狓=x、狔=y…），写手照抄引文时一并抄进了正文，学生看到的是「与向量犪长度相等」。
这里按标准映射表还原，并顺带把全角拉丁字母（ｃｏｓ）折成半角。

用法：
    python3 scripts/normalize_math_ocr_glyphs.py --dry     # 只统计
    python3 scripts/normalize_math_ocr_glyphs.py --write   # 就地改写
"""
import glob
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
LEARN = f"{REPO}/data/math/learn"

# 数学斜体字形 → 拉丁字母（PDF 文字层/OCR 的通用映射）
GLYPHS = {
    "犪": "a", "犫": "b", "犮": "c", "犱": "d", "犲": "e", "犳": "f", "犵": "g",
    "犺": "h", "犻": "i", "犼": "j", "犽": "k", "犾": "l", "犿": "m", "狀": "n",
    "狆": "p", "狇": "q", "狉": "r", "狊": "s", "狋": "t", "狌": "u", "狏": "v",
    "狑": "w", "狓": "x", "狔": "y", "狕": "z",
    "犃": "A", "犅": "B", "犆": "C", "犇": "D", "犈": "E", "犉": "F", "犌": "G",
    "犎": "H", "犐": "I", "犑": "J", "犓": "K", "犔": "L", "犕": "M", "犖": "N",
    "犗": "O", "犘": "P", "犙": "Q", "犚": "R", "犛": "S", "犜": "T", "犝": "U",
    "犞": "V", "犠": "W", "犡": "X", "犢": "Y", "犣": "Z",
}
# 全角拉丁字母（ｃｏｓ θ 之类）
FW = {chr(0xFF41 + i): chr(0x61 + i) for i in range(26)}
FW.update({chr(0xFF21 + i): chr(0x41 + i) for i in range(26)})
TABLE = str.maketrans({**GLYPHS, **FW})


def clean(s):
    return s.translate(TABLE)


def main():
    write = "--write" in sys.argv
    total = 0
    for f in sorted(glob.glob(f"{LEARN}/*.json")):
        if os.path.basename(f).startswith("_"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        n = 0
        for L in d["lessons"]:
            md = L.get("markdown") or ""
            new = clean(md)
            if new != md:
                n += sum(1 for a, b in zip(md, new) if a != b) or 1
                L["markdown"] = new
                L["words"] = len(re.findall(r"[\u4e00-\u9fa5]", new))
        if n:
            total += n
            print(f"{d['book']}: 还原 {n} 处字形")
            if write:
                json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(("已改写" if write else "干跑") + f"：合计 {total} 处")


if __name__ == "__main__":
    main()
