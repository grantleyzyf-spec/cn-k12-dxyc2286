# -*- coding: utf-8 -*-
"""C 类（疑似旧版残留）处置：按用户口径「旧版延伸内容·新版未设」打标保留。

但打标前逐条实测【该册正文关键词命中】，只给「该册不作课时、正文也只有零星提及」的点打标；
正文里真正讲到的（复式统计表/秒/倍/观察物体/十进制……）属「课时名不同」，不打标，避免污染标签语义。

判定依据（本机新版 PDF 全文检索，教材印刷页）：
  认识公顷     四上 p56 唯一一处「124公顷森林」＝练习题干用词，新版四上无公顷课时  ⇒ 打标
  认识平方千米 四上 全书 0 处「平方千米」，仅 km² 符号出现在题目单位        ⇒ 打标
  认识射线和直线 四上只有「射线」被角的度量借用，无「线段、直线、射线」课时（新版已前移到三上线和角）⇒ 打标
  认识东南西北 六上 0 处；新版二上「校园小导游」讲东、南、西、北                    ⇒ 打标（册次待定）
  认识八个方向 六上只讲「方向＋距离」，不列八个方向（旧版提法）                      ⇒ 打标

不打标（正文有、仅课时名不同）：复式统计表、认识钟表、认识秒、克和千克、倍的认识、
求一个数是另一个数的几倍、观察物体(一)、数的产生和十进制计数法。

用法：python3 apply_c_points.py [--write]
"""
import json
import os
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/math/topics.json"
WRITE = "--write" in sys.argv
TAG = "旧版·新版未设"

NOTES = {
    "认识公顷": "（旧版延伸内容：新版四年级上册未设公顷课时，正文仅练习题干出现「124公顷森林」；册次照旧）",
    "认识平方千米": "（旧版延伸内容：新版四年级上册全书未出现「平方千米」，仅以 km² 出现在题目单位中；册次照旧）",
    "认识射线和直线": "（旧版延伸内容：新版四年级上册不设「线段、射线、直线」课时（该内容已前移到三年级上册线和角），四上仅角的度量借用射线；册次照旧）",
    "认识东南西北": "（旧版延伸内容：新版六年级上册确定位置只讲有序数对与方向＋距离，不讲东、南、西、北（该内容在新版二年级上册校园小导游）；册次待定）",
    "认识八个方向": "（旧版延伸内容：新版六年级上册只讲方向＋距离，不列「八个方向」这一旧版提法；册次照旧）",
}


def main():
    topics = json.load(open(TP, encoding="utf-8"))
    hit = 0
    for t in topics:
        note = NOTES.get(t["name"])
        if not note:
            continue
        if t["grade"] is None:
            continue
        # 只处理小学（grade 1–6）
        if not (1 <= int(t["grade"]) <= 6):
            continue
        hit += 1
        tags = t.get("tags") or []
        if TAG not in tags:
            tags.insert(min(1, len(tags)), TAG)
            t["tags"] = tags
        if note not in t["description"]:
            t["description"] = t["description"].rstrip("。") + "。" + note
        print(f"  · {t['id']} {t['grade']}年级{'上' if t['semester']=='上' else '下'} {t['name']}"
              f"  ← {t['chapter']}")
    print(f"命中并打标 {hit} 个点")
    if WRITE and hit:
        with open(TP, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("✅ 已写入", TP)


if __name__ == "__main__":
    main()
