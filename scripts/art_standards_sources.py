# -*- coding: utf-8 -*-
"""美术（art）课标回表底本的公共模块：路径、OCR 误识表、按 quote 定位行号。

被 scripts/fix_art.py（算 sourceLine）与 scripts/test_art.py（逐字回表）共用，
避免两份脚本各写一套归一/修正规则。

底本由 scripts/ocr_art_standards.py 生成：
- YIJIAO：义务教育艺术课标（扫描版 PDF，无文字层）→ 逐页 OCR 拼接文本
- GAOZHONG：普通高中美术课标 TXT（GB18030）→ UTF-8 转存文本
"""
import os
import re

YIJIAO = "/tmp/art_yijiao_ocr.txt"
GAOZHONG = "/tmp/gaozhong_meishu.txt"

# 义教扫描件 OCR 误识 → 正确字（**归一文本上的**片段，标点已去掉）。
# 回表前先把底本里的误识改回正确字，再与 quote 比；新增一条必须同步 docs/art.md 的登记表。
OCR_FIX = {
    "折和县揉搓压": "折剪揉搓压",       # 1.T2.04「折、剪、揉、搓、压」
    "书法繁刻": "书法篆刻",             # 2.T1.01
    "运用线条有形状": "运用线条形状",     # 4.T1.04（OCR 多出一字）
    "形式原理汰析": "形式原理分析",       # 4.T1.04
    "情况感情继承": "情况感悟继承",       # 4.T4.01
}


def norm(s):
    """回表归一：只保留汉字与字母数字（去空白与全部标点，含 PDF/OCR 杂符）。"""
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", s or "")


def read_source(path):
    """读底本；GB18030 的原件也能读（先用 UTF-8，出现乱码特征再退回 GB18030）。"""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "gb18030"):
        try:
            txt = raw.decode(enc)
        except UnicodeDecodeError:
            continue
        if enc == "utf-8" and txt.count("美术") < 10:
            continue
        return txt
    return None


def yijiao_text():
    """义教 OCR 底本原文（未打补丁；只看内容用）。"""
    return read_source(YIJIAO)


def index(text):
    """返回 (归一文本, 归一字符→原文下标)；可对归一文本套用 OCR_FIX 并同步下标。"""
    chars, pos = [], []
    for i, ch in enumerate(text or ""):
        if re.match(r"[^\u4e00-\u9fffA-Za-z0-9]", ch):
            continue
        chars.append(ch)
        pos.append(i)
    for bad, good in OCR_FIX.items():
        hay = "".join(chars)
        at = hay.find(bad)
        while at >= 0:
            chars[at:at + len(bad)] = list(good)
            pos[at:at + len(bad)] = [pos[at]] + pos[at + 1:at + len(bad)]
            hay = "".join(chars)
            at = hay.find(bad, at + len(good))
    return "".join(chars), pos


def find_line(text, quote, use_ocr_fix=False):
    """返回 quote 首次出现处的 1-based 行号；找不到返回 0。

    先按「归一文本」定位（忽略空白/标点差异），再把归一位置映射回原文位置数换行，
    与 scripts/fix_japanese.py 的 line_of 同款思路。use_ocr_fix 用于扫描件 OCR 底本。
    """
    if not text or not quote:
        return 0
    needle = norm(quote)
    if not needle:
        return 0
    if use_ocr_fix:
        hay, pos = index(text)
    else:
        hay, pos = index(text)  # 非 OCR 底本无补丁可打，index 里的 OCR_FIX 不命中即无副作用
    at = hay.find(needle)
    if at < 0:
        return 0
    return text.count("\n", 0, pos[at]) + 1
