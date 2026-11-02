#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""语文（小学）学层分片合并器：把批次目录 out/<tag>.json 合成 data/chinese/learn/<册>.json。

用法：
    python3 scripts/merge_cn_learn_shards.py --batch /tmp/cn_learn_w4 [--write] [--books 一年级上册,一年级下册]

- 分片顺序以批次 INDEX.json 为准（同一册内按 S01→S14 顺序拼接）
- 逐册先自检（scripts/check_cn_learn_md.py），未过不写盘；--write 才落 data/chinese/learn/
- 不做任何内容改写；已存在的册文件备份为 <册>.json.bak.<时间戳>
"""
import argparse, glob, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEARN = os.path.join(ROOT, "data", "chinese", "learn")
CHECK = os.path.join(ROOT, "scripts", "check_cn_learn_md.py")
han = lambda s: len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--books", default="")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    idx = json.load(open(os.path.join(a.batch, "INDEX.json"), encoding="utf-8"))
    want = {b.strip() for b in a.books.split(",") if b.strip()}

    per_book = {}
    for e in idx:
        book = e["book"]
        if want and book not in want:
            continue
        out = e["out"] if isinstance(e["out"], str) else e["out"][0]
        per_book.setdefault(book, []).append((e["tag"], out))

    for book in sorted(per_book):
        shards = sorted(per_book[book])
        miss = [t for t, p in shards if not (os.path.exists(p) and os.path.getsize(p) > 500)]
        if miss:
            print(f"[SKIP] {book}: 缺 {len(miss)} 片（{', '.join(miss[:4])}…）")
            continue
        lessons, seen = [], set()
        for tag, path in shards:
            d = json.load(open(path, encoding="utf-8"))
            for les in d.get("lessons") or []:
                tid = les.get("topicId")
                if not tid or tid in seen:
                    continue
                seen.add(tid)
                les["words"] = han(les.get("markdown"))
                lessons.append(les)
        obj = {"book": book, "lessons": lessons}
        tmp = os.path.join("/tmp", f"cn_learn_{book}.json")
        json.dump(obj, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, CHECK, tmp], capture_output=True, text=True)
        ok = r.returncode == 0
        ws = [x["words"] for x in lessons]
        print(f"[{'PASS' if ok else 'FAIL'}] {book}: {len(shards)} 片 / {len(lessons)} 课 / "
              f"字数 {min(ws)}–{max(ws)} / 合计 {sum(ws)}")
        if not ok:
            tail = (r.stdout or r.stderr).strip().splitlines()[-6:]
            for line in tail:
                print("      ", line)
            continue
        if a.write:
            dst = os.path.join(LEARN, f"{book}.json")
            if os.path.exists(dst):
                os.replace(dst, dst + ".bak." + time.strftime("%Y%m%d%H%M%S"))
            os.replace(tmp, dst)
            print("      → written", os.path.relpath(dst, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
