# -*- coding: utf-8 -*-
"""课标「条目化」候选池（义教数学课标 TXT → 领域×学段×模块 的逐条条文）+ 为无课标点生成候选分片。

用法: python3 build_std_pool.py [--write]
输出:
  _std_pool.json                    条目池（id 与 quote 逐字取自课标 TXT）
  _std_work/W01.json …              无课标点的候选分片（每片 ≤45 点，含 top5 候选）
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TXT = os.path.expanduser(
    "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt")
D = os.path.expanduser("~/Desktop/cn-k12-dxyc2286/data")
DOMAINS = {"一": "数与代数", "二": "图形与几何", "三": "统计与概率", "四": "综合与实践"}
SEG_KEY = {"一": 1, "二": 2, "三": 3, "四": 4}


def norm(x):
    return re.sub(r"\s+", "", x or "")


def main():
    write = "--write" in sys.argv
    src = open(TXT, encoding="utf-8", errors="ignore").read()

    # —— 领域块 ——
    doms = [(m.start(), DOMAINS[m.group(1)]) for m in
            re.finditer(r"\(([一二三四])\)\s*(?:数与代数|图形与几何|统计与概率|综合与实践)", src)]
    doms.append((len(src), "END"))

    pool = []          # {seg, domain, mod, text}
    for i in range(len(doms) - 1):
        start, dom = doms[i]
        end = doms[i + 1][0]
        block = src[start:end]
        # 学段切分
        segs = [(m.start(), SEG_KEY[m.group(1)]) for m in
                re.finditer(r"\s*第([一二三四])学段\s*[（(]\s*\d", block)]
        mods = [(m.start(), ("NR" if "内容要求" in m.group(0) else "XY" if "学业要求" in m.group(0) else "TS"))
                for m in re.finditer(r"[【\[]?(内容要求|学业要求|教学提示)[】\]]?", block)]
        marks = sorted([(p, "SEG", v) for p, v in segs] + [(p, "MOD", v) for p, v in mods])
        cur_seg, cur_mod = None, None
        for k, (pos, kind, val) in enumerate(marks):
            cur_seg = val if kind == "SEG" else cur_seg
            cur_mod = val if kind == "MOD" else cur_mod
            nxt = marks[k + 1][0] if k + 1 < len(marks) else len(block)
            if kind != "MOD" or cur_seg is None or cur_mod is None:
                continue
            body = block[pos + 20:nxt]
            # 按 (1) (2) / 1. 2. 切条
            parts = re.split(r"(?:\(\s*\d+\s*\)|(?<![\d.])\d{1,2}\s*[.、])", body)
            for part in parts:
                t = re.sub(r"[ \t]+", "", part).strip()
                t = re.sub(r"^\W+", "", t)
                if len(norm(t)) < 12 or not re.search(r"[\u4e00-\u9fff]", t):
                    continue
                # 取到句末，限 12–46 字（quote 建议长度）
                sent = re.split(r"[。;;]", t)[0].strip()
                if not (12 <= len(norm(sent)) <= 46):
                    sent = norm(sent)[:44]
                if norm(sent) not in norm(src):
                    continue
                pool.append(dict(seg=cur_seg, domain=dom, mod=cur_mod, text=sent))
    # 去重
    seen, uniq = set(), []
    for p in pool:
        k = (p["seg"], norm(p["text"]))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    # —— id 分配：句文与人教版已用 quote 相同则复用其 id，否则按 (学段, 模块) 续编 ——
    topics = json.load(open(os.path.join(D, "math-bj", "topics.json"), encoding="utf-8"))
    hum = json.load(open(os.path.join(D, "math", "topics.json"), encoding="utf-8"))
    by_quote, maxno = {}, {}
    for t in hum:
        for s in t.get("standards") or []:
            sid = s.get("id") or ""
            if not sid.startswith("mat-2022:") or not s.get("quote"):
                continue
            seg, rest = sid.split(":", 1)[1].split(".", 1)
            mod, no = rest.split(".")
            by_quote.setdefault((int(seg), norm(s["quote"])), sid)
            maxno[(int(seg), mod)] = max(maxno.get((int(seg), mod), 0), int(no))
    for p in uniq:
        q = norm(p["text"])
        sid = by_quote.get((p["seg"], q))
        if not sid:
            key = (p["seg"], p["mod"])
            maxno[key] = maxno.get(key, 0) + 1
            sid = f"mat-2022:{p['seg']}.{p['mod']}.{maxno[key]:02d}"
            by_quote[(p["seg"], q)] = sid
        p["id"] = sid
    print("条目池：", len(uniq), "条 |", {s: sum(1 for p in uniq if p["seg"] == s) for s in (1, 2, 3, 4)})
    from collections import Counter
    print("模块分布：", dict(Counter(p["mod"] for p in uniq)), "| 领域：", dict(Counter(p["domain"] for p in uniq)))

    # —— 无课标点的候选（同领域、同学段优先，按字重叠打分取 top5） ——
    def seg_of(g):
        return 1 if g <= 2 else 2 if g <= 4 else 3 if g <= 6 else 4
    miss = [t for t in topics if not t.get("standards")]
    print("无课标点：", len(miss))
    items = []
    for t in miss:
        seg = seg_of(t["grade"])
        key = set(re.sub(r"[（(].*?[）)]", "", t["name"]))
        cands = []
        for p in uniq:
            if p["seg"] != seg:
                continue
            score = sum(1 for ch in key if ch in p["text"])
            if p["domain"] == t["domain"]:
                score += 2
            if score >= 2:
                cands.append((score, p))
        cands.sort(key=lambda x: -x[0])
        items.append(dict(id=t["id"], name=t["name"], domain=t["domain"], grade=t["grade"],
                          chapter=t["chapter"], seg=seg,
                          candidates=[dict(id=p["id"], text=p["text"]) for _, p in cands[:5]]))
    os.makedirs(os.path.join(HERE, "_std_work"), exist_ok=True)
    n = 0
    for i in range(0, len(items), 45):
        n += 1
        chunk = items[i:i + 45]
        json.dump(dict(shard=f"W{n:02d}", subject="math-bj", points=chunk),
                  open(os.path.join(HERE, "_std_work", f"W{n:02d}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    print("候选分片：", n, "片（每片 ≤45 点）")
    print("样例：", json.dumps(items[0], ensure_ascii=False)[:400])
    if write:
        json.dump(uniq, open(os.path.join(HERE, "_std_pool.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("写入 _std_pool.json")


if __name__ == "__main__":
    main()
