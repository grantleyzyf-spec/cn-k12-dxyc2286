# -*- coding: utf-8 -*-
"""把义教数学课标 TXT 重切成「学段 × 领域 × 内容要求」条目池（新命名空间 mat-2022n:*）。

为什么重切：仓库内 `mat-2022:*` 的 id 是各版本桶各自编号的，同一 id 在不同桶挂着完全不同的句子
（`4.XY.01` 一个 id 挂 6 条互不相干），id 无稳定语义。本脚本按课标原文「一 id 一义」重建，
旧 id 全部保留为 alias，不动任何已挂点。

输出：data/math-bj/_build/_std_work/items.json
    {"txt": <源路径>, "count": N, "items": [{item_id, stage, domain, topic, no, text}]}
用法：python3 parse_std_items.py [--write]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_std_work")
TXT = os.path.expanduser(
    "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt")

DOMAINS = [("数与代数", "SD"), ("图形与几何", "TX"), ("统计与概率", "TJ"), ("综合与实践", "ZH")]
STAGE_CN = {"一": 1, "二": 2, "三": 3, "四": 4}
# 条目行首：1. (1) CD) 6) 《5) 之类（OCR 变体）
ITEM_HEAD = re.compile(r"^\s*[（(《ＣC]?\s*[0-9０-９]{1,2}\s*[)）]")
# 主题行：1. 数与运算
TOPIC_HEAD = re.compile(r"^\s*[0-9０-９]{1,2}\s*[.．]\s*(.{2,12})$")
NOISE_LINE = re.compile(r"^=+\s*$|^page \d+ / \d+$|^\d{1,3}$")


def norm(s):
    return re.sub(r"[\s　，。、；：？！“”‘’（）()《》〈〉·—…\-~,.;:?!\"'/\\|\[\]【】]+", "", s or "")


def clean_lines(raw):
    out = []
    for ln in raw.split("\n"):
        s = ln.strip()
        if not s or NOISE_LINE.match(s):
            continue
        out.append(s)
    return out


def hanzi_ratio(s):
    if not s:
        return 0
    return len(re.findall(r"[\u4e00-\u9fa5]", s)) / len(s)


def main():
    write = "--write" in sys.argv
    raw_lines = open(TXT, encoding="utf-8", errors="ignore").read().split("\n")
    lines_keep_blank = ["" if (NOISE_LINE.match(x.strip()) or x.strip().startswith("====")) else x.rstrip()
                        for x in raw_lines]
    # ⛔ 目录页也有「(一) 数与代数 …… 17」这类行，必须先跳过目录：
    # 从「四、课程内容」之后开始解析，否则领域头会落在目录上、整段内容被切碎（实测学段一只出 10 条）
    start_at = next((i for i, x in enumerate(lines_keep_blank) if x.strip().startswith("四、课程内容")), 0)
    lines_keep_blank = lines_keep_blank[start_at:]
    lines = clean_lines("\n".join(lines_keep_blank))
    # 回表源必须用「去掉分页标记后的同一份文本」，否则跨页的句子永远拼不回去（分母数字会插在句中）
    src_norm = norm("".join(lines))

    cur_domain, cur_stage, in_req, cur_topic = None, None, False, ""
    items, buf, no = [], [], 0
    counts = {}

    def flush():
        nonlocal buf, no
        if not buf or cur_domain is None or cur_stage is None:
            buf = []
            return
        text = "".join(buf).strip()
        buf = []
        if len(re.findall(r"[\u4e00-\u9fa5]", text)) < 8 or hanzi_ratio(text) < 0.45:
            return  # 整条被 OCR 打坏
        if norm(text) not in src_norm:
            return  # 拼接后回表失败
        code = dict(DOMAINS)[cur_domain]
        no += 1
        items.append({"item_id": f"mat-2022n:{cur_stage}.{code}.{no:02d}",
                      "stage": cur_stage, "domain": cur_domain,
                      "topic": cur_topic, "no": no, "text": text})
        counts[(cur_stage, cur_domain)] = counts.get((cur_stage, cur_domain), 0) + 1

    # 按「空行分段」切条目：OCR 会把 (1) 读成 CD)/C1)/《5)，靠行首编号切会漏
    for ln in lines_keep_blank:
        m = re.match(r"^[（(]([一二三四])[)）]\s*(数与代数|图形与几何|统计与概率|综合与实践)", ln)
        if m:
            flush()
            cur_domain, cur_stage, in_req, cur_topic = m.group(2), None, False, ""
            no = 0
            continue
        m = re.match(r"^第([一二三四])学段", ln)
        if m:
            flush()
            cur_stage, in_req, cur_topic = STAGE_CN[m.group(1)], False, ""
            no = 0
            continue
        if ln.strip().startswith("【"):
            # OCR 会把「【学业要求】」读成「【学业要求了」、「【教学提示】」读成「【教学提示了」
            # ⇒ 只要遇到任意【X】就切换段落类型，避免把学业要求/教学提示的散文当条目收进来
            flush()
            in_req = "内容要求" in ln
            continue
        if not in_req or cur_domain is None or cur_stage is None:
            continue
        if not ln.strip():
            flush()
            continue
        mt = TOPIC_HEAD.match(ln.strip())
        if mt and not buf and len(mt.group(1)) <= 12 and "。" not in mt.group(1):
            cur_topic = mt.group(1)
            continue
        t0 = ln.strip()
        if not buf:
            # 去掉行首编号标记与 OCR 噪声：CD) / C1) / 《5) / 6) / @ / @@
            t0 = re.sub(r"^[@＠\s]*([（(《ＣC][ＤD]?\s*[0-9０-９]{0,2}\s*[)）]|[（(]?\s*[0-9０-９]{1,2}\s*[)）]|@+|＠+)\s*", "", t0)
        buf.append(t0)

    flush()

    print(f"源：{os.path.basename(TXT)}")
    print(f"条目 {len(items)} 条")
    for st in (1, 2, 3, 4):
        row = {d: counts.get((st, d), 0) for d, _ in DOMAINS}
        print(f"  学段{st}：{sum(row.values()):3d} 条  " + "  ".join(f"{k} {v}" for k, v in row.items()))
    short = [i for i in items if len(i["text"]) < 14]
    print(f"  最短条目 {min((len(i['text']) for i in items), default=0)} 字 · <14 字的 {len(short)} 条")
    if write:
        os.makedirs(OUT, exist_ok=True)
        json.dump({"txt": TXT, "count": len(items), "items": items},
                  open(os.path.join(OUT, "items.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("已写", os.path.join(OUT, "items.json"))
    else:
        print("（干跑，加 --write 落盘）")


if __name__ == "__main__":
    main()
