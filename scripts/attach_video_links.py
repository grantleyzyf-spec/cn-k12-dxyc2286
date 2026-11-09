#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视频 ↔ learn 课时映射，并把已生成的夸克链接挂上去。

产物：
  _assets/video_map.json   {video_key: [topicId, ...]}
  data/math/video_links.json  {topicId: {url, code, video}}
video_key = "<册>/<文件名不含扩展名>"
"""
import json, os, re, difflib
from openpyxl import load_workbook

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
BUILD = os.path.expanduser("~/Desktop/学科图谱讲解视频/_build")
ASSETS = os.path.expanduser("~/Desktop/学科图谱讲解视频/_assets")
XLSX = os.path.expanduser("~/Desktop/学科图谱讲解视频/知识点分享链接.xlsx")
MAP_OUT = os.path.join(ASSETS, "video_map.json")
LINKS_OUT = os.path.join(REPO, "data", "math", "video_links.json")

TAGS = {
    "math_rj1a": "一年级上册", "math_rj1b": "一年级下册", "math_rj2a": "二年级上册",
    "math_rj2b": "二年级下册", "math_rj3a": "三年级上册", "math_rj3b": "三年级下册",
    "math_rj4a": "四年级上册", "math_rj5a": "五年级上册", "math_rj6a": "六年级上册",
    "math_cz71": "七年级上册", "math_cz72": "七年级下册", "math_cz81": "八年级上册",
    "math_cz82": "八年级下册", "math_cz91": "九年级上册",
    "math_bx1": "必修第一册", "math_bx2": "必修第二册", "math_xb1": "选择性必修第一册",
    "math_xb2": "选择性必修第二册", "math_xb3": "选择性必修第三册",
}


def norm(s):
    s = re.sub(r"[（(]\d+[)）]", "", str(s))
    return re.sub(r"[\s·・\-—_、，,。．.：:；;！!？?（）()\[\]【】]", "", s)


def videos():
    out = []
    for tag, grade in TAGS.items():
        cdir = os.path.join(BUILD, tag, "content")
        if not os.path.isdir(cdir):
            continue
        for f in sorted(os.listdir(cdir)):
            if not f.endswith(".json") or f.startswith("_"):
                continue
            d = json.load(open(os.path.join(cdir, f), encoding="utf-8"))
            out.append({"key": f"{grade}/{d.get('id', '')}_{d.get('title', '')}",
                        "grade": grade, "name": d.get("title", ""), "chap": d.get("chap", "")})
    return out


def shares():
    """Excel -> {视频键: (url, code)}"""
    if not os.path.exists(XLSX):
        return {}
    wb = load_workbook(XLSX, read_only=True)
    out = {}
    for ws in wb.worksheets:
        head = None
        for row in ws.iter_rows(values_only=True):
            if head is None:
                head = list(row); continue
            d = dict(zip(head, row))
            url = d.get("分享链接")
            if not url:
                continue
            fn = str(d["视频文件名"]).replace(".mp4", "")
            key = f"{d['年级']}/{fn}"
            out[key] = (url, d.get("提取码", ""))
    return out


def main():
    idx = json.load(open(os.path.join(REPO, "learn", "index.json"), encoding="utf-8"))
    books = [b for b in idx["books"] if b["subject"] == "math" and "人教" in b["edition"]]
    vids = videos()
    by_grade = {}
    for v in vids:
        by_grade.setdefault(v["grade"], []).append(v)

    vmap, used = {}, {}
    for b in books:
        vs = by_grade.get(b["book"], [])
        for L in b["lessons"]:
            t = norm(L["title"])
            best, score = None, 0
            for v in vs:
                n = norm(v["name"])
                if not n:
                    continue
                if n in t or t in n:
                    s = 0.9 + 0.1 * min(len(n), len(t)) / (max(len(n), len(t)) + 1e-6)
                else:
                    s = difflib.SequenceMatcher(None, n, t).ratio()
                if s > score:
                    best, score = v, s
            if best and score >= 0.62:
                vmap.setdefault(best["key"], []).append(L["topicId"])
                used[best["key"]] = used.get(best["key"], 0) + 1
    json.dump(vmap, open(MAP_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    sh = shares()
    links = {}
    for key, topics in vmap.items():
        skey = key.replace(".", "_")
        if skey not in sh:
            continue
        url, code = sh[skey]
        for t in topics:
            links[t] = {"url": url, "code": code, "video": key.split("/")[-1]}
    os.makedirs(os.path.dirname(LINKS_OUT), exist_ok=True)
    json.dump(links, open(LINKS_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"视频 {len(vids)}，已挂到课时 {sum(len(v) for v in vmap.values())} 个（{len(vmap)} 个视频参与）")
    print(f"已上传并分享 {len(sh)}，写入 video_links {len(links)} 个课时")
    miss = [v for v in vids if v["key"] not in vmap]
    print("未匹配视频", len(miss), [m["key"] for m in miss][:5])


if __name__ == "__main__":
    main()
