# -*- coding: utf-8 -*-
"""轻量自检：统计每课时汉字数、五步节汉字数、每步字数、引文数。"""
import importlib.util
import re
import sys
import os

W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)


def hanzi(s):
    return re.findall(r"[\u4e00-\u9fa5]", s or "")


def load(parts):
    out = []
    for p in parts:
        spec = importlib.util.spec_from_file_location(p, os.path.join(W, p + ".py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        out.extend(m.LESSONS)
    return out


def report(lessons):
    for L in lessons:
        md = L["markdown"]
        n = len(hanzi(md))
        secs = re.split(r"\n(?=## )", md)
        wubu = [x for x in secs if x.split("\n")[0].find("五步学习法") >= 0]
        sw = len(hanzi(wubu[0])) if wubu else -1
        steps = [ln for ln in (wubu[0].split("\n") if wubu else []) if re.match(r"^\d+\.\s", ln.strip())]
        sc = [len(hanzi(s)) for s in steps]
        quotes = []
        cur = ""
        for ln in md.split("\n"):
            if ln.startswith("## "):
                cur = ln
                continue
            if ln.startswith("> ") and "课本原文" in cur and len(hanzi(ln)) >= 8:
                quotes.append(ln[2:].strip())
        # 每个一级段落字数
        detail = []
        for s in secs:
            h = s.split("\n")[0].replace("## ", "")
            detail.append(f"{h[:6]}:{len(hanzi(s))}")
        bad = []
        if not (1200 <= n <= 2600):
            bad.append(f"总字数{n}")
        if not (350 <= sw <= 700):
            bad.append(f"五步{sw}")
        if len(steps) < 5:
            bad.append(f"步数{len(steps)}")
        if any(c < 25 for c in sc):
            bad.append(f"某步{sc}")
        if len(quotes) < 2:
            bad.append("引文<2")
        if md.count("❌") < 2 or md.count("✅") < 2:
            bad.append("❌✅")
        if len(re.findall(r"例\s*题?\s*[12２１]", md)) < 2:
            bad.append("例题")
        if len(re.findall(r"- \[ \]", md)) < 3:
            bad.append("自查")
        ls = md.split("\n")
        for a, b in zip(ls, ls[1:]):
            if re.match(r"^\d+\.\s", a.strip()) and re.match(r"^\d+\.\s", b.strip()):
                bad.append("序号粘连")
                break
        print(f"{L['topicId']:10s} 总{n:5d} 五步{sw:4d} 步{sc} 引{len(quotes)} "
              f"{'OK' if not bad else 'BAD ' + ','.join(bad)}")
        print("          ", " ".join(detail))


if __name__ == "__main__":
    parts = sys.argv[1:] or ["part1"]
    report(load(parts))
