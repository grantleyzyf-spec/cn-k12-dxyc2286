# -*- coding: utf-8 -*-
"""S2 建点「干跑」：按 19 册定稿清单算出拟建 chapter 与知识点，不改任何数据。

规则（用户 2026-10-30 口径）：
  · chapter  = `<册> 第X单元 <板块名>`（单元名里的「·阅读/·识字/·汉语拼音」保留作板块）
  · 课（kind=课）→ 1 点
  · 篇（kind=篇，古诗/子篇）→ 1 点            ← 「古诗按首」直接满足
  · 文言文篇 → 再按段切（本脚本只统计与标记，段数需读正文后在建点脚本里定）
  · 板块（kind=板块）→ 不建点
产出：/tmp/cn/s2_dryrun.md
"""
import glob
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
OUT = "/tmp/cn/s2_dryrun.md"

# 文言文篇名（用于「按段切」判定；古诗/词/曲不在此列，它们已按首建点）
WENYAN = set("""
咏雪 陈太丘与友期行 论语十二章 诫子书 孙权劝学 卖油翁 陋室铭 爱莲说 活板
三峡 答谢中书书 记承天寺夜游 与朱元思书 得道多助失道寡助 富贵不能淫 生于忧患病于安乐
愚公移山 周亚夫军细柳 桃花源记 小石潭记 核舟记 北冥有鱼 庄子与惠子游于濠梁之上
虽有嘉肴 大道之行也 马说 岳阳楼记 醉翁亭记 湖心亭看雪 曹刿论战 邹忌讽齐王纳谏
陈涉世家 出师表 劝学 师说 赤壁赋 登泰山记 子路曾皙冉有公西华侍坐 齐桓晋文之事
庖丁解牛 烛之武退秦师 鸿门宴 屈原列传 苏武传 过秦论 谏太宗十思疏 阿房宫赋 六国论
归去来兮辞 种树郭橐驼传 石钟山记 大学之道 人皆有不忍人之心 老子四章 五石之瓠 兼爱
""".split())


def norm(s):
    return re.sub(r"[\s　·・、，,。．.（）()《》“”\"'’—－\-：:；;！!？?]", "", s or "")


def is_wenyan(name):
    key = norm(name)
    key = re.sub(r"(自读|略读)$", "", key)
    for w in WENYAN:
        if w and w in key:
            return True
    return False


def main():
    topics = json.load(open(f"{REPO}/data/chinese/topics.json", encoding="utf-8"))
    have = {(t["grade"], t["semester"], t["chapter"]) for t in topics}
    rows, tot = [], {"课": 0, "篇": 0, "文言文篇": 0, "板块": 0, "章": 0}
    for f in sorted(glob.glob(f"{REPO}/data/chinese/ke_toc/*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("status") not in ("manual_final", "checked"):
            continue
        book, g, sem = d["book"], d["grade"], d["semester"]
        nk = npn = nwy = nb = 0
        chaps = []
        for u in d["units"]:
            uname = u["unit"]
            m = re.match(r"^第([一二三四五六七八九十]+)单元(?:[（(].*?[)）])?(?:[·・](.+))?$", uname)
            ch = (f"{book} 第{m.group(1)}单元 " + (m.group(2) or "")).strip() if m else f"{book} {uname}"
            chaps.append(ch)
            for it in u["items"]:
                if it["kind"] in ("课", "篇"):
                    if it["kind"] == "课":
                        nk += 1
                    else:
                        npn += 1
                    if is_wenyan(it["name"]):
                        nwy += 1
                elif it["kind"] == "板块":
                    nb += 1
        rows.append((book, len(chaps), nk, npn, nwy, nb))
        tot["章"] += len(chaps); tot["课"] += nk; tot["篇"] += npn
        tot["文言文篇"] += nwy; tot["板块"] += nb
    L = ["# 语文 S2 建点干跑（不改数据）", "",
         "| 册 | 拟建章 | 课级点 | 篇级点（古诗/子篇） | 其中文言文篇（待按段切） | 板块（不建点） |",
         "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for b_, c, nk, npn, nwy, nb in rows:
        L.append(f"| {b_} | {c} | {nk} | {npn} | {nwy} | {nb} |")
    L.append(f"| **合计** | **{tot['章']}** | **{tot['课']}** | **{tot['篇']}** | **{tot['文言文篇']}** | **{tot['板块']}** |")
    base_points = tot["课"] + tot["篇"]
    L += ["", f"- 课+篇 = **{base_points}** 个候选点（不含文言文按段展开）",
          f"- 文言文 {tot['文言文篇']} 篇若平均切 3–5 段，再增 **{tot['文言文篇']*3}–{tot['文言文篇']*5}** 点",
          f"- 现有图谱 {len(topics)} 点（板块级），拟保留作上位概念；新增课后总点数约 "
          f"**{len(topics) + base_points}–{len(topics) + base_points + tot['文言文篇']*4}**"]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
