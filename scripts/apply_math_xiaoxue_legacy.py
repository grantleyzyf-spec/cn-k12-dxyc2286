# -*- coding: utf-8 -*-
"""小学数学「候选真缺」回查后的处置（幂等）。

来源：scripts/audit_math_xiaoxue_point_keshi.py（点↔课时标题比对）→ 63 条候选；
再用 scripts/audit_math_xiaoxue_points_body.py 做 SKILL §5 第②步（该册全文正文回查）：

- 48 条 → 表述差异（教材有内容，只是课时名不同）⇒ 只在 docs 留档，不改数据；
- 15 条 → 真缺。其中 3 条（数学广角——搭配(一)、数学广角——推理、认识东南西北）
  早前一轮已打标 `旧版·新版未设`；本次补打其余 12 条。

打标三件事（与既有口径一致）：chapter 尾部加「（旧版延伸内容·新版未设）」、
tags 第 2 位写 `旧版·新版未设`、description 末尾补依据。点与题一律保留，不下架。

用法：python3 scripts/apply_math_xiaoxue_legacy.py [--write]
"""
import json
import os
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/math/topics.json"
WRITE = "--write" in sys.argv
MARK = "（旧版延伸内容·新版未设）"

# 点名 → (册, 依据)
LEGACY = {
 "连加连减": ("一年级下册", "该册正文 0 命中「连加」，只有「连减」；新版把连加连减并入 100 以内加减法的口算与解决问题"),
 "加减混合运算": ("一年级下册", "该册正文 0 命中「混合」；新版不单列加减混合课时，随情境题处理"),
 "找规律": ("一年级下册", "该册 0 命中「规律」专题；新版「找规律」已移至二年级下册数学广角与四年级上册"),
 "用减法解决实际问题（求剩余、求比一个数少几）": ("一年级下册", "该册 0 命中该表述；新版把减法实际问题并入「100 以内的加法和减法（一）」的解决问题课时"),
 "几百几十加减几百几十": ("二年级下册", "该册 0 命中该表述；新版万以内加减法不再单列「几百几十」口算课时"),
 "除数是两位数的除法(口算)": ("四年级上册", "该册 0 命中「除数是两位数」「除法」课时名；新版该单元只保留笔算与试商，口算随练习处理"),
 "除数是两位数的除法(笔算)": ("四年级上册", "该册 0 命中「除数是两位数」「除法」课时名；新版表述为「除数是两位数的除法」单元下的试商课时"),
 "方程的意义": ("五年级上册", "该册 0 命中「方程」；按 2022 课标，简易方程移至初中（七年级上册一元一次方程）"),
 "解方程": ("五年级上册", "该册 0 命中「方程」；解方程随简易方程一并移至初中"),
 "列方程解决问题": ("五年级上册", "该册 0 命中「方程」；列方程解决问题随简易方程移至初中"),
 "观察中的遮挡与范围": ("五年级上册", "该册 0 命中该表述；新版观察物体只保留「搭组合体」与三视图初步"),
 "按比分配": ("六年级上册", "该册 0 命中「按比」「比的应用」；新版比的认识只到比的意义与基本性质，按比分配随比例下移"),
}


def main():
    topics = json.load(open(TP, encoding="utf-8"))
    hit, skip = [], []
    for t in topics:
        name = t.get("name")
        if name not in LEGACY:
            continue
        book, why = LEGACY[name]
        if not (t.get("chapter") or "").startswith(book):
            skip.append((name, "册不符", t.get("chapter")))
            continue
        if MARK in (t.get("chapter") or "") or "旧版·新版未设" in (t.get("tags") or []):
            skip.append((name, "已打标", ""))
            continue
        t["chapter"] = (t.get("chapter") or "") + MARK
        tags = list(t.get("tags") or [])
        tags.insert(1 if tags else 0, "旧版·新版未设")
        t["tags"] = tags
        desc = (t.get("description") or "").rstrip("。")
        t["description"] = desc + f"。（旧版延伸内容：{why}）"
        hit.append(name)
    print(f"打标 {len(hit)} 条；跳过 {len(skip)} 条 {skip}")
    for h in hit:
        print("  ✓", h)
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    json.dump(topics, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(TP, "a").write("\n")
    print("✅ 已写入")


if __name__ == "__main__":
    main()
