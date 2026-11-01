#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版数学 · 教材抽取与逐册目录（供 build_skeleton_hj.py 使用）
产出 /tmp/mhj/<tag>/pNNN.txt 与 /tmp/mhj/<tag>.json（book + units[章] + sections[节] + page）
"""
import json, os, re, glob
import fitz

BOOKS = [
    ("h1", "沪教版必修第一册", "必修第一册", 10, "上", "高一年级_必修第一册", [
        ("1", "集合与逻辑", [("1.1", "集合初步"), ("1.2", "常用逻辑用语")]),
        ("2", "等式与不等式", [("2.1", "等式与不等式的性质"), ("2.2", "不等式的求解"),
                          ("2.3", "基本不等式及其应用")]),
        ("3", "幂、指数与对数", [("3.1", "幂与指数"), ("3.2", "对数")]),
        ("4", "幂函数、指数函数与对数函数", [("4.1", "幂函数"), ("4.2", "指数函数"), ("4.3", "对数函数")]),
        ("5", "函数的概念、性质及应用", [("5.1", "函数"), ("5.2", "函数的基本性质"),
                                  ("5.3", "函数的应用"), ("5.4", "反函数")]),
    ]),
    ("h2", "沪教版必修第二册", "必修第二册", 10, "下", "高一年级_必修第二册", [
        ("6", "三角", [("6.1", "正弦、余弦、正切、余切"), ("6.2", "常用三角公式"), ("6.3", "解三角形")]),
        ("7", "三角函数", [("7.1", "正弦函数的图像与性质"), ("7.2", "余弦函数的图像与性质"),
                       ("7.3", "函数y=Asin（ωx+φ）的图像"), ("7.4", "正切函数的图像与性质")]),
        ("8", "平面向量", [("8.1", "向量的概念和线性运算"), ("8.2", "向量的数量积"),
                       ("8.3", "向量的坐标表示"), ("8.4", "向量的应用")]),
        ("9", "复数", [("9.1", "复数及其四则运算"), ("9.2", "复数的几何意义"),
                    ("9.3", "实系数一元二次方程"), ("9.4", "复数的三角形式")]),
    ]),
    ("h3", "沪教版必修第三册", "必修第三册", 11, "上", "高二年级_必修第三册", [
        ("10", "空间直线与平面", [("10.1", "平面及其基本性质"), ("10.2", "直线与直线的位置关系"),
                            ("10.3", "直线与平面的位置关系"), ("10.4", "平面与平面的位置关系"),
                            ("10.5", "异面直线间的距离")]),
        ("11", "简单几何体", [("11.1", "柱体"), ("11.2", "锥体"), ("11.3", "多面体与旋转体"), ("11.4", "球")]),
        ("12", "概率初步", [("12.1", "随机现象与样本空间"), ("12.2", "古典概率"),
                        ("12.3", "频率与概率"), ("12.4", "随机事件的独立性")]),
        ("13", "统计", [("13.1", "总体与样本"), ("13.2", "数据的获取"), ("13.3", "抽样方法"),
                     ("13.4", "统计图表"), ("13.5", "统计估计"), ("13.6", "统计活动")]),
    ]),
    ("h4", "沪教版必修第四册", "必修第四册", 11, "下", "高二年级_必修第四册", []),
    ("x1", "沪教版选择性必修第一册", "选择性必修第一册", 12, "上", "高三年级_选择性必修第一册", [
        ("1", "平面直角坐标系中的直线", [("1.1", "直线的倾斜角与斜率"), ("1.2", "直线的方程"),
                                ("1.3", "两条直线的位置关系"), ("1.4", "点到直线的距离")]),
        ("2", "圆锥曲线", [("2.1", "圆"), ("2.2", "椭圆"), ("2.3", "双曲线"), ("2.4", "抛物线"),
                       ("2.5", "曲线与方程")]),
        ("3", "空间向量及其应用", [("3.1", "空间向量及其运算"), ("3.2", "空间向量基本定理"),
                            ("3.3", "空间向量的坐标表示"), ("3.4", "空间向量在立体几何中的应用")]),
        ("4", "数列", [("4.1", "等差数列"), ("4.2", "等比数列"), ("4.3", "数列"),
                    ("4.4", "数学归纳法"), ("4.5", "用迭代序列求的近似值")]),
    ]),
    ("x2", "沪教版选择性必修第二册", "选择性必修第二册", 13, "下", "高三年级_选择性必修第二册", [
        ("5", "导数及其应用", [("5.1", "导数的概念及意义"), ("5.2", "导数的运算"), ("5.3", "导数的应用")]),
        ("6", "计数原理", [("6.1", "乘法原理与加法原理"), ("6.2", "排列"), ("6.3", "组合"),
                       ("6.4", "计数原理在古典概率中的应用"), ("6.5", "二项式定理")]),
        ("7", "概率初步（续）", [("7.1", "条件概率与相关公式"), ("7.2", "随机变量的分布与特征"), ("7.3", "常用分布")]),
        ("8", "成对数据的统计分析", [("8.1", "成对数据的相关分析"), ("8.2", "一元线性回归分析"), ("8.3", "2×2列联表")]),
    ]),
    ("x3", "沪教版选择性必修第三册", "选择性必修第三册", 14, "下", "高三年级_选择性必修第三册", []),
]

SRC_DIR = "/Users/a627692/Desktop/中小学教材/中小学教材/数学/高中/沪教版"
OUT = "/tmp/mhj"
FW = str.maketrans("０１２３４５６７８９（）　．，：；", "0123456789() .,:;")


def norm(s):
    return re.sub(r"\s+", "", s.translate(FW))


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = []
    for tag, book, short, grade, sem, pdfkey, units in BOOKS:
        pdfs = [p for p in glob.glob(os.path.join(SRC_DIR, "*.pdf")) if pdfkey in os.path.basename(p)]
        assert len(pdfs) == 1, (tag, pdfs)
        doc = fitz.open(pdfs[0])
        d = os.path.join(OUT, tag)
        os.makedirs(d, exist_ok=True)
        pages = []
        for i in range(doc.page_count):
            t = doc[i].get_text()
            pages.append(t)
            open(os.path.join(d, f"p{i+1:03d}.txt"), "w", encoding="utf-8").write(t)
        npages = doc.page_count
        # 目录页（含「目　录」或「目录」）
        toc_pages = [i for i in range(min(12, npages)) if "目" in pages[i] and "录" in pages[i]]
        units_out = []
        for uno, uname, secs in units:
            # 章首：正文中「第N章」独立成行且出现在目录页之后
            upat = re.compile(r"第\s*%s\s*章" % uno)
            upage = None
            for i in range((max(toc_pages) if toc_pages else 6) + 1, npages):
                head = "\n".join(pages[i].strip().split("\n")[:4]).translate(FW)
                if upat.search(head):
                    upage = i + 1
                    break
            secs_out = []
            prev = (upage - 1) if upage else 6
            for sno, sname in secs:
                spage = None
                # 节首：某页前 5 行出现「x.y」
                pat = re.compile(r"^\s*%s(?![0-9])" % re.escape(sno))
                for i in range(prev, npages):
                    head = "\n".join(pages[i].strip().split("\n")[:5]).translate(FW)
                    if pat.search(head):
                        spage = i + 1
                        break
                if spage is None:
                    # 回退：按节名在正文中首次出现定位（限定在前一节之后）
                    key = norm(sname)
                    for i in range(prev, npages):
                        if key and key in norm(pages[i]):
                            spage = i + 1
                            break
                if spage:
                    prev = spage - 1
                secs_out.append({"sec_no": sno, "sec_name": sname, "page": spage,
                                 "_found": bool(spage)})
            units_out.append({"unit_no": uno, "unit_name": f"第{uno}章 {uname}",
                              "page": upage, "sections": secs_out})
        rec = {"tag": tag, "book": book, "short": short, "stage": "高中",
               "grade": grade, "semester": sem, "pdf": pdfs[0], "pages": npages,
               "toc_pages": [i + 1 for i in toc_pages], "units": units_out,
               "notes": "" if units else "数学建模册：教材只有引论＋9 个建模活动（第1–3部分），无章、无节，按综合实践不建知识点"}
        json.dump(rec, open(os.path.join(OUT, f"{tag}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        miss = [f"{u['unit_name']}/{s['sec_name']}" for u in units_out for s in u["sections"] if not s["_found"]]
        summary.append((tag, book, npages, len(units_out),
                        sum(len(u["sections"]) for u in units_out), len(miss), miss[:3]))
        print(f"{tag} {book} {npages}页 章{len(units_out)} 节{sum(len(u['sections']) for u in units_out)} 未定位{len(miss)} {miss[:3]}")
    print("TOTAL 章", sum(s[3] for s in summary), "节", sum(s[4] for s in summary))


if __name__ == "__main__":
    main()
