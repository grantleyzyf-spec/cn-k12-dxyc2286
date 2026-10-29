# -*- coding: utf-8 -*-
"""高中 5 册「高风险 58 页」逐页用视觉模型读公式，并与 OCR 文本比对，产出公式台账。

为什么不让脚本自己判断"对不对"：OCR 引擎（Vision / tesseract）实测数字一致率中位仅 0.60，
公式不可信；口径是「公式只走视觉模型」。本脚本负责把 58 页逐页读出来并算出「OCR 漏了多少」，
再产出台账供人工抽查。

用法：
  python3 formula_ledger.py --limit 2          # 试跑
  python3 formula_ledger.py                    # 全量 58 页（4 并发，逐页落盘 /tmp/fml/）
  python3 formula_ledger.py --report           # 只汇总
"""
import base64
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import fitz

BASE = "/Users/a627692/Desktop/中小学教材/高中教材/高中数学/人教版（A版）"
OUT = "/tmp/fml"
RISK = "/tmp/mtoc/formula_risk.json"
OCR = "/Users/a627692/Desktop/qbank-upgrade/math/ocr_hs"
MODEL = "agnes-3.0-flash"
THRESHOLD = 60

PROMPT = (
    "这是人教A版高中数学教材的一页（{book}，PDF 第 {page} 页）。请只做一件事："
    "逐条转写本页出现的数学公式（定义式、定理式、例题里的算式与结果、结论式），"
    "每条占一行并以「1. 」「2. 」这样编号；符号必须照原页，分式/根式/上下标写成可读形式。"
    "不要解释、不要翻译、不要复述中文题干、不要总结。若本页确实没有任何公式，只输出 NONE。"
)


def env(key):
    for ln in open(os.path.expanduser("~/.ppt-master/.env"), encoding="utf-8"):
        if ln.strip().startswith(key + "="):
            return ln.strip().split("=", 1)[1].strip().strip('"')
    return None


def pdf_path(book):
    for p in os.listdir(BASE):
        if p.endswith(".pdf") and book[:3] in p and book[-2:] in p:
            return os.path.join(BASE, p)
    raise FileNotFoundError(book)


def render(book, page, dpi=160):
    d = fitz.open(pdf_path(book))
    pix = d[page - 1].get_pixmap(dpi=dpi)
    png = pix.tobytes("png")
    d.close()
    return png


def ask(key, book, page):
    png = render(book, page)
    b64 = base64.b64encode(png).decode()
    body = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": 900,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT.format(book=book, page=page)},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}},
        ]}],
    }
    req = urllib.request.Request(
        "https://apihub.agnes-ai.com/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    last = None
    for attempt in range(6):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            return r["choices"][0]["message"]["content"].strip()
        except Exception as e:                      # 网络/限流重试：429 指数退避
            last = e
            wait = 30 * (attempt + 1) if "429" in str(e) else 5 * (attempt + 1)
            time.sleep(wait)
    raise RuntimeError(f"{book} p{page}: {last}")


def ocr_text(book, page):
    p = f"{OCR}/{book}.txt"
    txt = open(p, encoding="utf-8").read()
    parts = re.split(r"=====PAGE (\d+)=====", txt)
    pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
    return re.sub(r"\s+", "", pages.get(page, ""))


def missing_tokens(formula, ocr):
    """公式里较长的一段字符（≥3 个字母数字）在 OCR 文本里找不到 → 记为 OCR 丢失。"""
    toks = re.findall(r"[A-Za-z0-9]{3,}", formula)
    miss = [t for t in toks if t.lower() not in ocr.lower()]
    return miss


def classify(answer):
    """→ (条数, 行列表)。剔除模型自己的客套话。"""
    if not answer or answer.strip().upper().startswith("NONE"):
        return 0, []
    lines = []
    for ln in answer.split("\n"):
        s = ln.strip()
        if not s:
            continue
        s = re.sub(r"^[\-\*•]?\s*\d+\s*[.、)]\s*", "", s)
        if len(s) < 2:
            continue
        if re.search(r"(没有|无任何|未见)公式", s) and len(s) < 25:
            continue
        lines.append(s[:160])
    return len(lines), lines[:40]


def one(key, item):
    book, page = item["book"], item["page"]
    dst = f"{OUT}/{book}_p{page}.json"
    if os.path.exists(dst):
        return json.load(open(dst, encoding="utf-8"))
    ans = ask(key, book, page)
    n, lines = classify(ans)
    ocr = ocr_text(book, page)
    rows = []
    for f in lines:
        rows.append({"formula": f, "ocr_missing": missing_tokens(f, ocr)})
    rec = {"book": book, "page": page, "score": item.get("score"),
           "formula_count": n, "formulas": rows,
           "ocr_missing_total": sum(len(r["ocr_missing"]) for r in rows),
           "raw_head": ans[:300]}
    os.makedirs(OUT, exist_ok=True)
    json.dump(rec, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rec


def report():
    files = sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []
    recs = [json.load(open(f"{OUT}/{f}", encoding="utf-8")) for f in files if f.endswith(".json")]
    per = {}
    for r in recs:
        d = per.setdefault(r["book"], {"pages": 0, "formulas": 0, "missing": 0, "empty": 0})
        d["pages"] += 1
        d["formulas"] += r["formula_count"]
        d["missing"] += r["ocr_missing_total"]
        if r["formula_count"] == 0:
            d["empty"] += 1
    print(f"已读 {len(recs)} 页 · 公式 {sum(r['formula_count'] for r in recs)} 条 · "
          f"OCR 丢失字符组 {sum(r['ocr_missing_total'] for r in recs)}")
    for b, d in per.items():
        print(f"  {b}: {d['pages']} 页 · {d['formulas']} 条公式 · 无公式页 {d['empty']} · OCR 丢失 {d['missing']}")
    worst = sorted(recs, key=lambda r: -r["ocr_missing_total"])[:8]
    print("OCR 丢失最多的页：", [(r["book"], r["page"], r["ocr_missing_total"]) for r in worst])
    return recs


def main():
    key = env("AGNES_API_KEY")
    if not key:
        raise SystemExit("未找到 AGNES_API_KEY")
    if "--report" in sys.argv:
        report()
        return
    risk = [x for x in json.load(open(RISK, encoding="utf-8")) if x["score"] >= THRESHOLD]
    risk.sort(key=lambda x: -x["score"])
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
        risk = risk[:limit]
    print(f"待读 {len(risk)} 页（公式分 ≥{THRESHOLD}），模型 {MODEL}")
    done, failed = 0, []
    def safe(it):
        try:
            return one(key, it)
        except Exception as e:
            failed.append((it["book"], it["page"], str(e)[:60]))
            return None
    with ThreadPoolExecutor(max_workers=2) as ex:
        for rec in ex.map(safe, risk):
            done += 1
            if rec:
                print(f"  [{done}/{len(risk)}] {rec['book']} p{rec['page']} 公式 {rec['formula_count']} 条 "
                      f"· OCR 丢失 {rec['ocr_missing_total']}", flush=True)
            else:
                print(f"  [{done}/{len(risk)}] 跳过（失败待重试）", flush=True)
    if failed:
        print("失败页：", failed)
    report()


if __name__ == "__main__":
    main()
