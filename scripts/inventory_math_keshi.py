# -*- coding: utf-8 -*-
"""课时清单汇总（小学 9 册 + 初中 5 册 + 高中 A 版 5 册）→ data/math/ke_json/_toc/<册>.txt

输出格式（供建点工位直接读）：
    单元序号|单元名|课时名|印刷页
    第一单元|5以内数的认识和加、减法|1～5的认识|14

小学源：data/math/keshi_toc/<册>.txt（五上若缺则读教材目录同步件）
初中源：data/math/keshi_toc/<册>.txt（gen_math_chuzhong_toc.py 产出）
高中源：教材目录「每节内容对应页码」TXT（人教 A 版）

跳过：练一练/整理和复习/复习与关联/自我评价/学习准备/数学游戏/数学活动/综合与实践/
      小结/阅读与思考/探究与发现/图说数学史/信息技术应用 —— 这些是栏目不是课时。
"""
import glob
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
TOCD = f"{REPO}/data/math/keshi_toc"
OUTD = f"{REPO}/data/math/ke_json/_toc"
XI = "/Users/a627692/Desktop/中小学教材/中小学教材/数学"
SKIP = re.compile(r"^(练一练|整理和复习|整理复习|复习与关联|应用提升|自我评价|学习准备|数学游戏|数学活动|"
                  r"综合与实践|小结|阅读与思考|探究与发现|图说数学史|信息技术应用|活动[一二三四五]|目录|致同学)$")
XIAO = ["一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
        "四年级上册", "五年级上册", "六年级上册"]
CHU = ["七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册"]
GAO = {"必修第一册": "必修第一册", "必修第二册": "必修第二册",
       "选择性必修第一册": "选择性必修第一册", "选择性必修第二册": "选择性必修第二册",
       "选择性必修第三册": "选择性必修第三册"}
CN_NO = {"一": "第一单元", "二": "第二单元", "三": "第三单元", "四": "第四单元",
         "五": "第五单元", "六": "第六单元", "七": "第七单元", "八": "第八单元",
         "九": "第九单元", "十": "第十单元"}


def parse_xiao(book):
    p = f"{TOCD}/{book}.txt"
    if not os.path.exists(p):
        p = f"{XI}/小学/人教版/{book}/教学设计/数学人教版{book}每节内容对应页码.txt"
    if not os.path.exists(p):
        return []
    rows, unit = [], None
    for ln in open(p, encoding="utf-8"):
        s = ln.rstrip("\n")
        if s.startswith("【"):
            unit = None          # 【数学游戏】【时间在哪里】【数学连环画】等＝综合与实践/预备课，不建课时点
            continue
        m = re.match(r"^([一二三四五六七八九十])　(.+?)（第(\d+)", s)
        if m:
            unit = CN_NO[m.group(1)] + " " + m.group(2)
            continue
        m = re.match(r"^　(.+?)\s+(\d+)$", s)
        if m and unit:
            nm, pg = m.group(1).strip(), m.group(2)
            if SKIP.match(nm):
                continue
            rows.append((unit, nm, pg))
    return rows


def parse_chu(book):
    p = f"{TOCD}/{book}.txt"
    if not os.path.exists(p):
        return []
    rows, unit = [], None
    for ln in open(p, encoding="utf-8"):
        s = ln.rstrip("\n")
        # 初中章号可能是「十三」「二十一」这类多字中文数字（八上起），必须 + 而不是单字
        m = re.match(r"^([一二三四五六七八九十]+)　(.+)$", s)
        if m:
            unit = m.group(2).strip()
            continue
        m = re.match(r"^　(\d+\.\d+)　(.+?)\s+(\d+|\?)$", s)
        if m and unit:
            item = (unit, f"{m.group(1)} {m.group(2)}", m.group(3))
            # 目录尾页会把第一章再列一遍 ⇒ 同名节去重（七上曾因此多出 1.1/1.2 两条）
            if item not in rows:
                rows.append(item)
    return rows


def parse_gao(book):
    cand = glob.glob(f"{XI}/高中/人教版（A版）/*{book}*每节内容对应页码*.txt")
    if not cand:
        return []
    rows, unit = [], None
    for ln in open(cand[0], encoding="utf-8"):
        s = ln.rstrip("\n")
        # 高中目录件格式：`第一章　集合与常用逻辑用语`
        m = re.match(r"^第([一二三四五六七八九十]+)章　(.+)$", s)
        if m:
            unit = f"第{m.group(1)}章 {m.group(2).strip()}"
            continue
        # 节行：`  1.1　集合的概念 ...................... 教材页码 1～5　（PDF 第7～11页）`
        # 3 级小节（4.1.1）才是真正的课时；2 级节（4.1）在有小节时只是分组
        m3 = re.match(r"^\s*(\d+\.\d+\.\d+)　(.+?)\s*\.{2,}.*?教材页码\s*(\d+)", s)
        if m3 and unit:
            rows.append((unit, f"{m3.group(1)} {m3.group(2).strip()}", m3.group(3)))
            continue
        m = re.match(r"^\s*(\d+\.\d+)\s*\*?　(.+?)\s*\.{2,}.*?教材页码\s*(\d+)", s)
        if m and unit:
            nm = f"{m.group(1)} {m.group(2).strip()}"
            if SKIP.match(nm) or nm.startswith(("小结", "复习参考题")):
                continue
            rows.append((unit, nm, m.group(3), "节"))
            continue
    # 同一节已展开成小节时，丢掉该节的 2 级行
    return [(u, n, p) for (u, n, p, *rest) in rows] if rows and isinstance(rows[0], tuple) and len(rows[0]) == 4 else rows


def main():
    os.makedirs(OUTD, exist_ok=True)
    total = 0
    for book, fn in [(b, parse_xiao) for b in XIAO] + [(b, parse_chu) for b in CHU] + \
                    [(b, parse_gao) for b in GAO]:
        rows = fn(book)
        if not rows:
            print(f"⚠️ {book}: 0 课时（清单缺）")
            continue
        lines = [f"# {book} 课时清单（单元|课时名|印刷页）"]
        for u, nm, pg in rows:
            lines.append(f"{u}|{nm}|{pg}")
        open(f"{OUTD}/{book}.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
        total += len(rows)
        print(f"{book}: {len(rows)} 课时")
    print(f"\n合计 {total} 课时 ⇒ 建点数 {total} / 题 {total*5}")


if __name__ == "__main__":
    main()
