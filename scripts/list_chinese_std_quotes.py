# -*- coding: utf-8 -*-
"""列出语文课标「可回表」条目：从课标 TXT 抽各学段条目原文＋行号，并标出课标索引里真实存在的 id。
用途：建点前先看本文件，避免凭空猜 id / 猜引文（第二学段没有 2.YD.01 这个坑就是这么踩的）。
用法：python3 list_cn_std_quotes.py > docs/chinese-std-quotes.md
"""
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TXT = ("/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
       "2.《义务教育语文课程标准·日常修订版)(2022年版2025年修订).txt")
IDX = f"{REPO}/data/cn-curriculum-standards.json"

SEC = {"第一学段": r"第一学段\s*\(1\s*[~一]\s*2\s*年级\)",
       "第二学段": r"第二学段\s*\(3\s*[~一]\s*4\s*年级\)",
       "第三学段": r"第三学段\s*\(5\s*[~一]\s*6\s*年级\)",
       "第四学段": r"第四学段\s*\(7\s*[~一]\s*9\s*年级\)"}
DOM = {"识字与写字": "SX", "阅读与鉴赏": "YD", "表达与交流": "BD", "梳理与探究": "SL"}


def main():
    raw = open(TXT, encoding="utf-8", errors="ignore").read().split("\n")
    ids = {e["id"] for e in json.load(open(IDX, encoding="utf-8"))["subjects"]["chinese"]["entries"]}
    grade_of = {1: "第一学段", 2: "第二学段", 3: "第三学段", 4: "第四学段"}
    out = ["# 语文课标可回表条目（自动生成，勿手改）", "",
           "> 生成脚本：`scripts/list_chinese_std_quotes.py`。引文必须与课标 TXT 逐字一致；",
           "> 该 TXT 有 OCR 错字（如「归读」「条段」「会号」），引文要避开错字处截取。", ""]
    for g, name in grade_of.items():
        pat = SEC.get(name)
        starts = [i for i, l in enumerate(raw) if pat and re.search(pat, l.replace("\u3000", ""))]
        if not starts:
            continue
        s = starts[0]
        out.append(f"## {name}")
        dom = None
        n = 1
        for i in range(s, min(s + 80, len(raw))):
            line = raw[i].strip().replace("\u3000", "")
            m = re.search(r"【([^】]{2,8})】?", line) or re.search(r"【([^】]{2,8})", line)
            if m and any(k in m.group(1) for k in DOM):
                dom = next(DOM[k] for k in DOM if k in m.group(1))
                n = 1
                out.append(f"\n### {next(k for k in DOM if k in m.group(1))}（{g}.{dom}）")
                continue
            if re.match(r"^\d+\.", line):
                num = re.match(r"^(\d+)\.", line).group(1)
                body = []
                for j in range(i, min(i + 3, len(raw))):
                    t = raw[j].strip().replace("\u3000", "")
                    if j > i and re.match(r"^\d+\.", t):
                        break
                    if t and not re.match(r"^[=page/0-9 ]+$", t) and not t.startswith("page"):
                        body.append(t)
                txt = "".join(body)[:110]
                sid = f"cyw-2022:{g}.{dom}.{num.zfill(2)}"
                flag = "✅" if sid in ids else "❌ 索引中不存在"
                out.append(f"- `{sid}` {flag} — 第 {i+1} 行起：{txt}")
                n += 1
        out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    main()
