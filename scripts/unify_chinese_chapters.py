# -*- coding: utf-8 -*-
"""全库统一章节口径（用户 2026-10-30 选定方案 2）：
把老「板块级」知识点的 chapter 从 `<册> <板块>` 改成新版单元式 `<册> 第X单元 <板块>`，
并把该板块**首次出现**的单元作为归属单元（板块级点是上位概念，跨单元时归首单元，口径写进 docs）。
同时给这些点补 tag「上位概念」，便于区分课级点与板块级点。

用法：python3 unify_cn_chapters.py [--write]
"""
import collections
import glob
import json
import os
import re
import sys

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TP = f"{REPO}/data/chinese/topics.json"
WRITE = "--write" in sys.argv
TAG = "上位概念"

# 板块关键词 → 在新章名里可能出现的写法（含同义）
SYN = {
    "汉语拼音": ["汉语拼音", "拼音"],
    "识字": ["识字"],
    "课文": ["阅读"],
    "现代文": ["阅读"],
    "文言文": ["阅读"],
    "古代诗歌": ["阅读"],
    "口语交际": ["阅读", "语文园地"],
    "写话": ["阅读", "习作", "语文园地"],
    "习作": ["习作"],
    "写作": ["写作", "习作"],
    "综合性学习": ["专题学习活动", "综合性学习", "活动"],
    "名著导读": ["整本书阅读", "名著导读"],
}


def book_of(chapter):
    return chapter.split(" ", 1)[0] if " " in chapter else chapter


def main():
    topics = json.load(open(TP, encoding="utf-8"))
    # 每册的新版单元名（来自 ke_toc 定稿清单）
    units = collections.defaultdict(list)
    for f in glob.glob(f"{REPO}/data/chinese/ke_toc/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("status") not in ("manual_final", "checked"):
            continue
        book = d["book"]
        for u in d["units"]:
            m = re.match(r"^第([一二三四五六七八九十]+)单元(?:[（(].*?[)）])?(?:[·・](.+))?$", u["unit"])
            if m:
                ch = f"{book} 第{m.group(1)}单元" + (f" {m.group(2)}" if m.group(2) else "")
            else:
                ch = f"{book} {u['unit']}"
            units[book].append(ch)

    plan = []
    for t in topics:
        ch = t["chapter"]
        book = book_of(ch)
        rest = ch[len(book):].strip()
        if rest.startswith("第"):          # 已经是单元式
            continue
        if book not in units:
            plan.append((t["id"], ch, None, "该册无定稿清单，未动"))
            continue
        keys = SYN.get(rest, [rest])
        target = None
        for k in keys:
            cand = [u for u in units[book] if k and k in u]
            if cand:
                target = cand[0]
                break
        if target is None and units[book]:
            target = units[book][0]
        plan.append((t["id"], ch, target, "" if target else "无候选"))

    changed = [p for p in plan if p[2] and p[2] != p[1]]
    unknown = [p for p in plan if not p[2]]
    print(f"待改 {len(changed)} 点 · 未能定位 {len(unknown)} 点 · 已合规跳过 {len(topics) - len(plan)} 点")
    print("映射样例：")
    seen = set()
    for tid, old, new, _ in changed:
        k = (old, new)
        if k in seen:
            continue
        seen.add(k)
        print(f"  {old}  →  {new}")
        if len(seen) >= 12:
            break
    if unknown[:5]:
        print("未定位：", [(p[0], p[1], p[3]) for p in unknown[:5]])
    if not WRITE:
        print("（未加 --write，不落盘）")
        return
    m = {p[0]: p[2] for p in changed}
    n = 0
    for t in topics:
        if t["id"] in m:
            t["chapter"] = m[t["id"]]
            tags = t.get("tags") or []
            if TAG not in tags:
                tags.append(TAG)
            t["tags"] = tags
            n += 1
    json.dump(topics, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(TP, "a").write("\n")
    print(f"✅ 已改 {n} 点")


if __name__ == "__main__":
    main()
