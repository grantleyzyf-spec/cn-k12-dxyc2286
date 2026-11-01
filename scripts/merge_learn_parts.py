#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用「学层分片合并器」：把 data/<subject>/learn/_parts/L*.json 合并成 data/<subject>/learn/<册>.json。

- 课时顺序按 topics.json 册内顺序（不支持 level 字段的桶按 chapter 的「 · 」/page 判定课时点）
- 输出 {"book": "<册>", "lessons": [{topicId,title,markdown,words}]}
- --write 时逐册跑对应 checker（--checker 指定），未过不写盘（先写临时文件再 os.replace）

用法：
  python3 scripts/merge_learn_parts.py math-hujiao scripts/check_math_hujiao_learn.py [--write]
  python3 scripts/merge_learn_parts.py math-sujiao scripts/check_math_sujiao_learn.py [--write]
"""
import argparse, glob, json, os, subprocess, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def lesson_ids(topics):
    """返回有序课时 id 列表 + {id: book}。"""
    has_level = any("level" in t for t in topics)
    out, book_of = [], {}
    for t in topics:
        ok = (t.get("level") == "lesson") if has_level else (" · " in (t.get("chapter") or "") or t.get("page") is not None)
        if not ok:
            continue
        out.append(t["id"])
        ch = t.get("chapter") or ""
        # 册名 = chapter 里第一个空格前的完整册名（如「苏教版一年级上册 第一单元 · 认识1、2、3」）
        book_of[t["id"]] = ch.split(" ")[0] if " " in ch else ch
    return out, book_of


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("checker")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    D = os.path.join(ROOT, "data", a.subject)
    topics = load(os.path.join(D, "topics.json"))
    ids, book_of = lesson_ids(topics)
    order = {tid: i for i, tid in enumerate(ids)}
    expect = defaultdict(int)
    for tid in ids:
        expect[book_of[tid]] += 1

    parts = sorted(glob.glob(os.path.join(D, "learn", "_parts", "L*.json")))
    by_book = defaultdict(dict)
    for p in parts:
        d = load(p)
        for L in d.get("lessons") or []:
            by_book[d["book"]][L["topicId"]] = L
    print(f"分片 {len(parts)} | 册 {len(by_book)} | 课时点 {len(ids)}")

    bad = 0
    for book in sorted(by_book):
        seq = sorted(by_book[book].values(), key=lambda L: order.get(L["topicId"], 10 ** 6))
        need = expect.get(book, 0)
        flag = "" if len(seq) == need else f"  !! 缺口 {need - len(seq)}"
        print(f"  {book}: {len(seq)}/{need} 篇{flag}")
        if a.write:
            p = os.path.join(D, "learn", f"{book}.json")
            dump(p, {"book": book, "lessons": seq})
            r = subprocess.run([sys.executable, os.path.join(ROOT, a.checker), p],
                               capture_output=True, text=True)
            last = (r.stdout.strip().split("\n") or [""])[-1]
            print(f"    checker: {last}")
            if r.returncode != 0:
                bad += 1
                os.remove(p)
                print("    !! 已撤回，未写盘")
    print(f"失败册 {bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
