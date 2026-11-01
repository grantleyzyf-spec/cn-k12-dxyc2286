# -*- coding: utf-8 -*-
"""修正卷面确认错误（子代讲解时上报、父代逐条复核过）。

只改「答案/选项/题干/解析」的确错，不动分值结构。用法: python3 fix_exam_errata.py [--write]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(os.path.dirname(HERE), "exams")

# (册, 卷名, 题号, 字段, 旧值片段, 新值)
FIXES = [
    # ① 一上 第六单元：三处答案错位（#2/#5/#9）
    ("一年级上册", "第六单元测试卷", 2, "answer", "12", "3"),
    ("一年级上册", "第六单元测试卷", 5, "answer", "3", "8"),
    ("一年级上册", "第六单元测试卷", 9, "answer", "3", "60"),
    # ② 三上 第一单元 #22：450×4=1800，末尾 2 个 0 ⇒ B
    ("三年级上册", "第一单元测试卷", 22, "answer", "C", "B"),
    # ③ 三上 第三单元 #20：1 km/2000 步 = 5 分米；原 C「50 厘米」与 B 等值 ⇒ 改 C 文本
    ("三年级上册", "第三单元测试卷", 20, "option:C", "50 厘米", "50 毫米"),
    # ④ 三上 第三单元 #22：5 分米 = 50 厘米 = 500 毫米；原 C 与 D 等值 ⇒ 改 C 文本
    ("三年级上册", "第三单元测试卷", 22, "option:C", "500 毫米", "500 厘米"),
    # ⑤ 三下 期中A #1：题干「添上一个 0」与答案 2100 矛盾 ⇒ 改题干
    ("三年级下册", "期中测试卷A", 1, "stem", "再在 21 后面添上一个 0", "再在 21 后面添上两个 0"),
    # ⑥ 四上 第一单元 #27：65 万千位是 0，省略万位尾数仍是 65 万
    ("四年级上册", "第一单元测试卷", 27, "answer", "65 万≈70 万", "65 万≈65 万"),
    ("四年级上册", "第一单元测试卷", 27, "analysis", "65 万的千位相当于 5，满 5 进一，约 70 万。",
     "65 万即 650000，省略万位后面的尾数要看千位，千位是 0，不满 5 舍去，所以 65 万≈65 万。"),
    # ⑦ 六上 第二单元 #20：答案 D 正确，解析末句字母写错
    ("六年级上册", "第二单元测试卷", 20, "analysis", "所以只有 A 互为倒数。", "所以只有 D 互为倒数。"),
    # ⑧ 九上 期末B #21：优弧 AB 所对的圆周角 = 180−30 = 150 度
    ("九年级上册", "期末测试卷B", 21, "answer", "(2) 优弧 AB 所对的圆周角是 30 度。",
     "(2) 优弧 AB 所对的圆周角是 150 度。"),
    ("九年级上册", "期末测试卷B", 21, "analysis",
     "同弧所对的圆周角等于圆心角的一半，但要注意这里取的是优弧 AB 所对的圆周角，它对着的是劣弧 AB 上的圆心角 60 度，所以等于 30 度。",
     "圆心角 角 AOB 等于 60 度，劣弧 AB 的度数为 60 度；优弧 AB 的度数为 360 度减 60 度等于 300 度。优弧 AB 所对的圆周角等于它所对弧的度数的一半，即 300 度除以 2 等于 150 度。"),
    # ⑨ 九上 第十八章 #9：题干只说「坐标都变为原来的 2 倍」⇒ 只有（6，4）
    ("九年级上册", "第十八章 相似形 测试卷", 9, "answer", "A", "B"),
    ("九年级上册", "第十八章 相似形 测试卷", 9, "analysis",
     "以原点为位似中心、位似比为 2 时，对应点在原点同侧与异侧各有一个，坐标为（6，4）或（负 6，负 4）；只写一组属于漏解，（负 6，4）是符号错。",
     "题干说「横、纵坐标都变为原来的 2 倍」，即横坐标 3 变 6、纵坐标 2 变 4，所以只有（6，4）。出现（负 6，负 4）是位似比取负值的情形，本题没有给负位似比，故不选 A；（负 6，4）是符号错。"),
]


def main():
    write = "--write" in sys.argv
    by_file = {}
    for book, paper, no, field, old, new in FIXES:
        by_file.setdefault((book, paper), []).append((no, field, old, new))
    n = 0
    for (book, paper), fixes in by_file.items():
        p = os.path.join(EX, book, paper + ".json")
        ex = json.load(open(p, encoding="utf-8"))
        items = {it["no"]: it for s in ex["sections"] for it in s["items"]}
        for no, field, old, new in fixes:
            it = items.get(no)
            if not it:
                print(f"  ⚠ 找不到 {book}/{paper} #{no}")
                continue
            if field.startswith("option:"):
                lab = field.split(":")[1]
                o = next((x for x in it.get("options") or [] if x["label"] == lab), None)
                if not o or old not in o["text"]:
                    print(f"  ⚠ {book}/{paper} #{no} 选项 {lab} 未含「{old}」")
                    continue
                o["text"] = o["text"].replace(old, new)
            else:
                cur = str(it.get(field) or "")
                if old not in cur:
                    print(f"  ⚠ {book}/{paper} #{no} {field} 未含「{old[:20]}」")
                    continue
                it[field] = cur.replace(old, new)
            n += 1
            print(f"  ✓ {book}/{paper} #{no} {field}：「{old[:16]}」→「{new[:16]}」")
        if write:
            json.dump(ex, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("改动", n, "处", "" if write else "（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
