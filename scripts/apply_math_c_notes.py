# -*- coding: utf-8 -*-
"""C 类 8 个「表述差异」点：description 补注新版对应课时名与教材页（不改 tags、不动点题）。

依据（本机新版 PDF 全文检索，教材印刷页）：
  复式统计表        三下 数据的收集与整理，教材页 67 原文「这个表是复式统计表」（另 76、97）
  认识钟表 / 认识秒  二下 时间在哪里，课时「认识时间」教材页 2（秒针 2–3）
  克和千克          三上 曹冲称象的故事，课时「认识质量单位」教材页 32（千克 32–37）
  倍的认识 / 求一个数是另一个数的几倍  二下 数量间的乘除关系，教材页 25–34
  观察物体(一)      三上 第一单元 观察物体，教材页 1–5
  数的产生和十进制计数法  四上 万以上数的认识，课时「亿以内数的认识」教材页 10（另 21 整理和复习）

用法：python3 apply_c_notes.py [--write]
"""
import json
import os
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/math/topics.json"
WRITE = "--write" in sys.argv

NOTES = {
    "复式统计表":
        "（表述差异，非教材缺：新版三年级下册第五单元「数据的收集与整理」教材页 67 正文原文「这个表是复式统计表」"
        "（另见教材页 76、97）；该单元课时标题为插图，未见独立课时名）",
    "认识钟表":
        "（表述差异，非教材缺：新版二年级下册「时间在哪里」课时「认识时间」教材页 2 讲时、分、秒与钟面认读）",
    "认识秒":
        "（表述差异，非教材缺：新版二年级下册「时间在哪里」课时「认识时间」教材页 2–3「秒针转 1 小格是 1 秒」）",
    "克和千克":
        "（表述差异，非教材缺：新版三年级上册「曹冲称象的故事」课时「认识质量单位」教材页 32"
        "（克、千克见教材页 32–37））",
    "倍的认识":
        "（表述差异，非教材缺：新版二年级下册第二单元「数量间的乘除关系」教材页 25–34 讲倍；该单元课时标题为插图）",
    "求一个数是另一个数的几倍":
        "（表述差异，非教材缺：新版二年级下册第二单元「数量间的乘除关系」教材页 26 起讲「几倍」；课时标题为插图）",
    "观察物体(一)":
        "（表述差异，非教材缺：新版三年级上册第一单元「观察物体」教材页 1–5，第 1 页「从不同方向看到的形状是不同的」；课时标题为插图）",
    "数的产生和十进制计数法":
        "（表述差异，非教材缺：新版四年级上册第一单元「万以上数的认识」课时「亿以内数的认识」教材页 10 原文"
        "「…叫作十进制计数法」，另教材页 21 整理和复习有复习条目）",
}


def main():
    topics = json.load(open(TP, encoding="utf-8"))
    hit = 0
    for t in topics:
        note = NOTES.get(t["name"])
        if not note or t.get("grade") is None or not (1 <= int(t["grade"]) <= 6):
            continue
        hit += 1
        if note not in t["description"]:
            t["description"] = t["description"].rstrip("。") + "。" + note
        print(f"  · {t['id']} {t['name']} ← {t['chapter']}")
    print(f"补注 {hit} 个点")
    if WRITE and hit:
        with open(TP, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("✅ 已写入", TP)


if __name__ == "__main__":
    main()
