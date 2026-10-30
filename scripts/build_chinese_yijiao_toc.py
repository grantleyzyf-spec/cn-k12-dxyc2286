# -*- coding: utf-8 -*-
"""义教 14 册（有 PDF 的）《单元 → 板块 → 课名 → 页码》清单生成。

来源与优先级（对应技能 k12-textbook-alignment-1to12 §0）：
  ① 小学 2–6 上册：PDF 目录解析（单元骨架 + 页码）+ 教材逐课 TXT 快照（gold 篇名，召回 78–88% 的册）
     ⇒ 用 gold 篇名补/校解析结果，页码沿用解析稿（gold 无页码）；
  ② 一下/二下/三下/七下/八下：只有解析稿（无 gold），标 pending_manual；
  ③ 一上 + 七/八/九上：解析召回 <60%，**不自动出定稿**，只导出「解析稿 + gold 并列对照」供人工标定。

产出：data/chinese/ke_toc/<册>.json|.txt（带 status 字段）与 /tmp/cn/yijiao_report.md
"""
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
ROOT = "/Users/a627692/Desktop/中小学教材/中小学教材/语文"
TXT = "/Users/a627692/Desktop/中小学教材/精准提取各学科教材TXT文档/语文"

# 册 → (grade, semester, PDF glob, TXT 目录, 处理策略)
BOOKS = [
    (1, "上", "一年级上册", f"{ROOT}/小学/*一年级_上册*.pdf", f"{TXT}/小学/人教版一年级上册", "manual"),
    (1, "下", "一年级下册", f"{ROOT}/小学/*一年级_下册*.pdf", None, "parse_only"),
    (2, "上", "二年级上册", f"{ROOT}/小学/*二年级_上册*.pdf", f"{TXT}/小学/人教版二年级上册", "gold_merge"),
    (2, "下", "二年级下册", f"{ROOT}/小学/*二年级_下册*.pdf", None, "parse_only"),
    (3, "上", "三年级上册", f"{ROOT}/小学/*三年级_上册*.pdf", f"{TXT}/小学/人教版三年级上册", "gold_merge"),
    (3, "下", "三年级下册", f"{ROOT}/小学/*三年级_下册*.pdf", None, "parse_only"),
    (4, "上", "四年级上册", f"{ROOT}/小学/*四年级_上册*.pdf", f"{TXT}/小学/人教版四年级上册", "gold_merge"),
    (5, "上", "五年级上册", f"{ROOT}/小学/*五年级_上册*.pdf", f"{TXT}/小学/人教版五年级上册", "gold_merge"),
    (6, "上", "六年级上册", f"{ROOT}/小学/*六年级_上册*.pdf", f"{TXT}/小学/人教版六年级上册", "gold_merge"),
    (7, "上", "七年级上册", f"{ROOT}/初中/*七年级_上册*.pdf", f"{TXT}/初中/人教版七年级上册", "manual"),
    (7, "下", "七年级下册", f"{ROOT}/初中/*七年级_下册*.pdf", None, "parse_only"),
    (8, "上", "八年级上册", f"{ROOT}/初中/*八年级_上册*.pdf", f"{TXT}/初中/人教版八年级上册", "manual"),
    (8, "下", "八年级下册", f"{ROOT}/初中/*八年级_下册*.pdf", None, "parse_only"),
    (9, "上", "九年级上册", f"{ROOT}/初中/*九年级_上册*.pdf", f"{TXT}/初中/人教版九年级上册", "manual"),
]
BOARD_WORDS = ("语文园地", "快乐读书吧", "口语交际", "习作", "写话", "综合性学习", "名著导读",
               "阅读链接", "书写提示", "日积月累", "和大人一起读", "阅读综合实践", "专题学习活动",
               "整本书阅读", "课外古诗词诵读", "活动探究", "单元学习任务", "单元研习任务", "例文")


def norm(s):
    return re.sub(r"[\s　·・、，,。．.（）()《》“”\"'’—－\-：:；;！!？?]", "", s or "")


def gold_names(d):
    """TXT 快照 → [(板块, 篇名)]，板块由文件名前缀判定。"""
    out = []
    if not d or not os.path.isdir(d):
        return out
    for f in sorted(glob.glob(d + "/*.txt")):
        nm = os.path.basename(f)[:-4]
        m = re.match(r"t\d+(第[一二三四五六七八九十]+单元)?(.*)", nm)
        rest = m.group(2) if m else nm
        board = ""
        for w in ("阅读", "识字", "课文", "汉语拼音", "口语交际", "习作", "写话", "语文园地",
                  "古诗词诵读", "综合性学习", "名著导读", "写作", "和大人一起读", "快乐读书吧", "活动探究"):
            if rest.startswith(w):
                board, rest = w, rest[len(w):]
                break
        if rest and rest not in BOARD_WORDS:
            out.append((board, rest))
    return out


def main():
    units_all = json.load(open("/tmp/cn/units.json", encoding="utf-8"))
    report = ["# 义教 14 册清单生成报告", ""]
    total = {}
    for grade, sem, book, pat, txtdir, mode in BOOKS:
        pdfs = glob.glob(pat)
        items_src = units_all.get(book, [])
        if not pdfs:
            report.append(f"## {book}\n- ⛔ 缺 PDF（不在本次范围）\n")
            continue
        gold = gold_names(txtdir)
        if mode == "manual":
            status = "pending_manual"
            units = items_src
        elif mode == "gold_merge":
            # 单调指针匹配：gold 按教材顺序逐个来，解析稿也按页码排序后只能「向后」找。
            # 这样同名的多篇（古诗三首）会各自吃掉下一个出现位置，不会重复指向同一页；
            # 找不到的 gold 条目落到当前单元、页码留空待核。
            status = "draft_gold_first"
            parsed = sorted([(u["unit"], it) for u in items_src for it in u["items"]],
                            key=lambda x: x[1]["page"])
            units, index = [], {}
            for unit, _ in parsed:
                if unit not in index:
                    index[unit] = {"unit": unit, "items": []}
                    units.append(index[unit])
            cur_unit = parsed[0][0] if parsed else "全册"
            ptr = 0
            for board, gn in gold:
                key = norm(gn)
                hit = None
                for j in range(ptr, len(parsed)):
                    k2 = norm(parsed[j][1]["name"])
                    if k2 and (k2 in key or key in k2):
                        hit = j
                        break
                if hit is not None:
                    unit, it = parsed[hit]
                    ptr = hit + 1
                    cur_unit = unit
                    index[unit]["items"].append({"kind": it["kind"] if it["kind"] != "课" else "课",
                                                 "name": gn, "page": it["page"]})
                else:
                    index[cur_unit]["items"].append({"kind": "课", "name": gn, "page": None, "need_page": True})
        else:
            status = "parse_only"
            units = items_src
        rec = {"book": book, "grade": grade, "semester": sem, "status": status,
               "source": {"pdf": os.path.basename(pdfs[0]), "gold_txt": bool(gold)}, "units": units}
        json.dump(rec, open(f"{REPO}/data/chinese/ke_toc/{book}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        lines = [f"语文（人教版）{book}　单元/课名清单（status={status}；页码=教材印刷页）", ""]
        for u in units:
            lines.append(u["unit"])
            for it in u["items"]:
                pg = it["page"] if it["page"] is not None else "待核"
                lines.append(f"　{it['name']} {pg}")
            lines.append("")
        open(f"{REPO}/data/chinese/ke_toc/{book}.txt", "w", encoding="utf-8").write("\n".join(lines).rstrip() + "\n")
        n_item = sum(len(u["items"]) for u in units)
        total[book] = (len(units), n_item, len(gold), status)
        report.append(f"## {book}\n- {len(units)} 单元 · {n_item} 条目 · gold {len(gold)} 条 · 状态 `{status}`\n")
        print(f"{book}: {len(units)} 单元 · {n_item} 条目 · gold {len(gold)} · {status}")
    open("/tmp/cn/yijiao_report.md", "w", encoding="utf-8").write("\n".join(report) + "\n")
    print("\n合计册数", len(total), "· 条目", sum(v[1] for v in total.values()))


if __name__ == "__main__":
    main()
