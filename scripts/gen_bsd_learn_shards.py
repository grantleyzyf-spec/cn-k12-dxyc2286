#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初高中「学层精讲」派单生成器（L 编号从现有最大号 +1，文件名带册名后缀）。

与 scripts/gen_learn_shards.py 的差别（这份专为 math-bsd 的初高中 9 册写）：
1. **不覆盖已有分片**：编号 = 现有 `learn/_shards/L*.json` 的最大号 +1；文件名 `L###_<册>.json`
   （跨册共享命名空间，重号会整片覆盖别册，见技能 7 号铁律）。
2. **教材原文切片**：topics 没有页码，本器按「单元名 → 课时名」在永久 textpack 的
   `整册全文.txt` 里定位，为每个课时切一段 `_shards/txt/<LID>/<topicId>.txt`（约 1500–2500 汉字），
   派单里 `lessons[].txt` 直接给这个切片路径 —— 工人不必读整册 9 万字。
3. 七段标题必须含 checker 的关键词（开场 / 课本原文 / 费曼翻译 / 例题 / 易错 / 五步学习法 / 自查）。

用法：
  python3 scripts/gen_bsd_learn_shards.py --books 必修第一册 必修第二册 --per-shard 6
  python3 scripts/gen_bsd_learn_shards.py --books 七年级上册 --dry
"""
import argparse
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = "math-bsd"
TXT_ROOT = os.path.expanduser("~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/数学/北师大版")
TAGS = {"一年级上册": "mbsd1a", "一年级下册": "mbsd1b", "二年级上册": "mbsd2a", "二年级下册": "mbsd2b",
        "三年级上册": "mbsd3a", "三年级下册": "mbsd3b", "四年级上册": "mbsd4a", "四年级下册": "mbsd4b",
        "五年级上册": "mbsd5a", "五年级下册": "mbsd5b", "六年级上册": "mbsd6a", "六年级下册": "mbsd6b",
        "七年级上册": "mbsd7a", "七年级下册": "mbsd7b", "八年级上册": "mbsd8a", "八年级下册": "mbsd8b",
        "九年级上册": "mbsd9a", "九物年级下册": "mbsd9b",
        "必修第一册": "mbsdbx1", "必修第二册": "mbsdbx2",
        "选择性必修第一册": "mbsdxb1", "选择性必修第二册": "mbsdxb2"}


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def norm(s):
    return re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", s or "")


def full_text_of(book):
    for stage in ("小学", "初中", "高中"):
        p = os.path.join(TXT_ROOT, stage, book, "整册全文.txt")
        if os.path.exists(p):
            return open(p, encoding="utf-8", errors="ignore").read()
    return ""


def find_near(raw, key, start=0, span=400):
    """在 raw 里找 key（先去标点再找），返回原文下标区间；找不到返回 -1。"""
    k = norm(key)
    if not k:
        return -1
    # 用 key 的前 6 个汉字逐点滑窗找（OCR 常把个别字读坏）
    for L in (len(k), 8, 6, 4):
        sub = k[:L]
        idx = norm(raw).find(sub, 0)
        if idx >= 0:
            break
    else:
        return -1
    # norm 后下标 ≠ 原文下标，用粗换算：按汉字比例映射
    ratio = len(raw) / max(1, len(norm(raw)))
    return int(idx * ratio)


def lesson_windows(book, lessons):
    """给每个课时切一段原文（单元名定位 → 顺序等分），返回 {topicId: text}。"""
    raw = full_text_of(book)
    if not raw:
        return {L["id"]: "" for L in lessons}, 0
    # 按单元分组
    units = {}
    for L in lessons:
        ch = L["chapter"]
        m = re.match(r"^(\S+)\s+第[一二三四五六七八九十\d]+(单元|章)\s*(.*)$", ch)
        uname = m.group(3).split(" · ")[0].strip() if m else ch
        units.setdefault(uname, []).append(L)
    out, hit = {}, 0
    for uname, group in units.items():
        a = find_near(raw, uname)
        if a < 0:
            # 单元名找不到就用本单元第一课名
            a = find_near(raw, group[0]["name"])
        if a < 0:
            for L in group:
                out[L["id"]] = ""
            continue
        # 单元文本窗口：从单元起点到「本单元课时数 × 1600 汉字」上限，且不超过全册末尾
        span = min(len(raw) - a, max(6000, 1800 * len(group)))
        unit_txt = raw[a:a + span]
        # 逐课在 unit_txt 内定位，切到下一课起点
        pos = []
        for L in group:
            p = find_near(unit_txt, L["name"])
            if p < 0:
                # 用课时名里的「——」后半段或前 4 字再试
                tail = L["name"].split("——")[-1]
                p = find_near(unit_txt, tail) if tail else -1
            pos.append(p)
        for i, L in enumerate(group):
            s = pos[i]
            if s < 0:
                # 等分兜底
                s = int(len(unit_txt) * i / max(1, len(group)))
                out[L["id"]] = unit_txt[max(0, s - 200): s + 2200]
            else:
                nxt = next((p for p in pos[i + 1:] if p > s), len(unit_txt))
                out[L["id"]] = unit_txt[s:min(len(unit_txt), nxt + 600)]
                hit += 1
    return out, hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", nargs="*", required=True)
    ap.add_argument("--per-shard", type=int, default=6)
    ap.add_argument("--txt-full", action="store_true",
                    help="不给逐课切片，改给整册全文路径（扫描件课时名与教材小节名对不上时用）")
    ap.add_argument("--skip-covered", action="store_true",
                    help="跳过 learn/_parts 里已经写过的课时点（补派时用）")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    base = os.path.join(ROOT, "data", BUCKET)
    topics = json.load(open(os.path.join(base, "topics.json"), encoding="utf-8"))
    shards_dir = os.path.join(base, "learn", "_shards")
    parts_dir = os.path.join(base, "learn", "_parts")
    txt_dir = os.path.join(shards_dir, "txt")

    existing = [os.path.basename(p) for p in glob.glob(os.path.join(shards_dir, "L*.json"))]
    nums = [int(m.group(1)) for f in existing if (m := re.match(r"L(\d+)", f))]
    start = (max(nums) + 1) if nums else 1

    want = set(a.books)
    covered = set()
    if a.skip_covered:
        for p in glob.glob(os.path.join(parts_dir, "L*.json")):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            for L in d.get("lessons") or []:
                covered.add(L.get("topicId"))
    lessons_by_book = {}
    for t in topics:
        if t.get("level") != "lesson":
            continue
        book = t["chapter"].split(" ")[0]
        if book in want and t["id"] not in covered:
            lessons_by_book.setdefault(book, []).append(t)

    n = start
    made = 0
    total_pts = 0
    for book, items in lessons_by_book.items():
        items.sort(key=lambda t: t["id"])
        total_pts += len(items)
        excerpts, hit = lesson_windows(book, items)
        if not a.dry:
            os.makedirs(parts_dir, exist_ok=True)
        for i in range(0, len(items), a.per_shard):
            chunk = items[i:i + a.per_shard]
            lid = f"L{n:03d}"
            pay_lessons = []
            full_path = ""
            if a.txt_full:
                for stage in ("小学", "初中", "高中"):
                    cand = os.path.join(TXT_ROOT, stage, book, "整册全文.txt")
                    if os.path.exists(cand):
                        full_path = cand
                        break
            for t in chunk:
                p_txt = full_path
                if not a.txt_full and not a.dry:
                    d = os.path.join(txt_dir, f"{lid}_{book}")
                    os.makedirs(d, exist_ok=True)
                    p_txt = os.path.join(d, f"{t['id']}.txt")
                    with open(p_txt, "w", encoding="utf-8") as fh:
                        fh.write(excerpts.get(t["id"], "") or "")
                pay_lessons.append({
                    "topicId": t["id"], "name": t["name"], "chapter": t["chapter"],
                    "page": t.get("page"), "misconceptions": t.get("misconceptions") or [],
                    "txt": p_txt,
                })
            payload = {"shard": lid, "bucket": BUCKET, "book": book,
                       "grade": chunk[0].get("grade"), "semester": chunk[0].get("semester"),
                       "txt_tag": TAGS.get(book, ""),
                       "out": f"data/{BUCKET}/learn/_parts/{lid}_{book}.json",
                       "lessons": pay_lessons}
            if not a.dry:
                json.dump(payload, open(os.path.join(shards_dir, f"{lid}_{book}.json"), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=2)
            n += 1
            made += 1
        print(f"{book}: 课时点 {len(items)} · 原文定位命中 {hit}/{len(items)}", flush=True)

    print(f"\n合计：册 {len(lessons_by_book)} · 课时点 {total_pts} · 新分片 {made}（L{start:03d}~L{n-1:03d}）"
          f"{'（干跑）' if a.dry else ''}")


if __name__ == "__main__":
    main()
