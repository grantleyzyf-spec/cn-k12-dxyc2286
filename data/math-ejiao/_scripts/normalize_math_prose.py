#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版高中数学题库 · 数学表达式散文化归一（高置信规则，只改文本不动 answer/verify）

只做三件不会改变语义的事（照 SKILL §7.3 的 OP/EQ 操作数边界写法）：
  「X 等于 Y」→「X=Y」   「X 乘 Y」→「X×Y」   「X 加/减 Y」→「X+/-Y」
⛔ 不碰「…的平方/的立方」（「实数的平方」「3 的平方分别为」这类会被改错）、
   不碰「除以」（「8 除以 3 减 x 的商」去掉文字会变成歧义算式）、不碰「负 n」。
用法：python3 normalize_math_prose.py [--write]
"""
import glob, json, re, sys

OUT = "/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-ejiao"
L = r"0-9A-Za-z\)）²³√π"
R = r"0-9A-Za-z\(（√π"

RULES = [
    (re.compile(rf"(?<=[{L}])\s*等于\s*(?=[{R}\-])"), "="),
    (re.compile(rf"(?<=[{L}])\s*乘\s*(?=[{R}])"), "×"),
    (re.compile(rf"(?<=[{L}])\s*加\s*(?=[{R}])"), "+"),
    (re.compile(rf"(?<=[{L}])\s*减\s*(?=[{R}])"), "-"),
]


def fix(s):
    if not isinstance(s, str):
        return s
    # 等于 / 乘：无条件安全
    s = RULES[0][0].sub(RULES[0][1], s)
    s = RULES[1][0].sub(RULES[1][1], s)
    # 除以：仅限两侧都是数字（8 除以 3 → 8÷3），不碰带字母的复合分母
    s = re.sub(r"(?<=\d)\s*除以\s*(?=\d)", "÷", s)
    # 加 / 减：句中含「除以」时跳过（避免 8 除以 3 减 x → 8 除以 3-x 的歧义）
    if "除以" not in s and "商" not in s:
        s = RULES[2][0].sub(RULES[2][1], s)
        s = RULES[3][0].sub(RULES[3][1], s)
    return re.sub(r"\s{2,}", " ", s).strip()


def main():
    write = "--write" in sys.argv
    tot = 0
    for f in sorted(glob.glob(f"{OUT}/_bank/c*.json")):
        d = json.load(open(f, encoding="utf-8"))
        n = 0
        for bag in ("unit_points", "lesson_points"):
            for pt in d.get(bag, []):
                for q in pt.get("questions", []):
                    for k in ("prompt", "explanation"):
                        new = fix(q.get(k))
                        if new != q.get(k):
                            q[k] = new; n += 1
                    for o in q.get("options") or []:
                        new = fix(o.get("text"))
                        if new != o.get("text"):
                            o["text"] = new; n += 1
        if n:
            print(f"{f.split('/')[-1]}: {n} 处")
            tot += n
            if write:
                json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"合计 {tot} 处" + ("（已写入）" if write else "（干跑）"))


if __name__ == "__main__":
    main()
