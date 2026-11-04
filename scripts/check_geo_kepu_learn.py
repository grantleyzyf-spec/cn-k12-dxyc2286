#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科普版地理 学层精讲 校验。

用法：
  python3 scripts/check_geo_xiangjiao_learn.py <片或成品.json>       # 逐篇校验（片可以是 {lessons:[...]} 或单篇）
  python3 scripts/check_geo_xiangjiao_learn.py --dir <册或目录>      # 目录下所有 json 逐个校验
  python3 scripts/merge_geo_learn.py                        # 合并 learn/_parts → learn/<册>.json

七段固定：一、开场 / 二、课本原文 / 三、费曼翻译 / 四、例题精讲 / 五、易错点拨 / 六、五步学习法 / 七、自查清单
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-kepu")
TEXT = os.path.join(D, "_text")
SEC = ["开场", "课本原文", "费曼翻译", "例题精讲", "易错点拨", "五步学习法", "自查清单"]
STEPS = ["每天锻炼一个", "扎实掌握第一个知识点", "能积微者速成", "对标思维", "杠铃法则"]
BAN = ["首先", "其次", "综上所述", "总而言之", "由此可见", "赋能", "抓手", "闭环", "值得注意的是"]


def han(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", str(s)))


def qnorm(s):
    return re.sub(r"[\s\u3000，。、；：“”‘’（）()《》！？—…·]", "", str(s))


def book_text(book):
    p = os.path.join(TEXT, f"{book}.txt")
    if not os.path.exists(p):
        return ""
    return qnorm(open(p, encoding="utf-8").read())


def check_lesson(les, books_cache):
    err = []
    md = les.get("markdown", "") or ""
    book = les.get("book") or ""
    w = han(md)
    if not (1200 <= w <= 2800):
        err.append("字数 %d ∉1200—2800" % w)
    if les.get("words") not in (None, w) and abs((les.get("words") or 0) - w) > 10:
        err.append("words 标注 %s ≠ 实测 %d" % (les.get("words"), w))
    for s in SEC:
        if s not in md:
            err.append("缺段 %s" % s)
    pos = [md.find(s) for s in SEC]
    if not (all(p >= 0 for p in pos) and pos == sorted(pos)):
        err.append("七段顺序/缺失")
    tail = md.split("五步学习法", 1)[-1] if "五步学习法" in md else ""
    for st in STEPS:
        if st not in tail:
            err.append("五步缺「%s」" % st)
    wstep = han(tail.split("七、")[0]) if tail else 0
    if not (350 <= wstep <= 900):
        err.append("五步节 %d ∉350—900" % wstep)
    if md.count("- [ ]") < 3:
        err.append("自查勾选 <3")
    if "❌" not in md or "✅" not in md:
        err.append("例题缺 ❌/✅")
    quotes = re.findall(r"^>\s*(.+)$", md, re.M)
    if len(quotes) < 2:
        err.append("课本原文引用 <2 处")
    if book:
        if book not in books_cache:
            books_cache[book] = book_text(book)
        src = books_cache[book]
        if src:
            bad = [q for q in quotes if qnorm(q)[:24] not in src]
            if bad:
                err.append("引文失配 %d 处（例：%s）" % (len(bad), bad[0][:30]))
    for b in BAN:
        if b in md:
            err.append("禁词 %s" % b)
    if re.search(r"^#{1,3} (?!一、|二、|三、|四、|五、|六、|七、)", md, re.M):
        err.append("出现非规范小节标题")
    return err


def lessons_of(obj, default_book=""):
    if isinstance(obj, dict) and "lessons" in obj:
        bk = obj.get("book") or default_book
        out = []
        for les in obj["lessons"]:
            les = dict(les)
            les.setdefault("book", bk)
            out.append(les)
        return bk, out
    if isinstance(obj, list):
        return default_book, obj
    les = dict(obj)
    les.setdefault("book", default_book)
    return les.get("book"), [les]


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    files = []
    if args[0] == "--dir":
        root = args[1]
        for dirpath, _, names in os.walk(root):
            for n in sorted(names):
                if n.endswith(".json"):
                    files.append(os.path.join(dirpath, n))
    else:
        files = [args[0]]
    cache, bad_n, tot = {}, 0, 0
    for f in files:
        obj = json.load(open(f, encoding="utf-8"))
        book, lessons = lessons_of(obj, os.path.basename(os.path.dirname(f)))
        for les in lessons:
            tot += 1
            err = check_lesson(les, cache)
            tag = "✅" if not err else "❌"
            if err:
                bad_n += 1
                print(f"{tag} {os.path.basename(f)} · {les.get('topicId')} · {les.get('title')} · {han(les.get('markdown'))} 字")
                for e in err[:8]:
                    print("   -", e)
    print(f"\n共 {tot} 篇 · 不合格 {bad_n}")
    return 1 if bad_n else 0


if __name__ == "__main__":
    sys.exit(main())
