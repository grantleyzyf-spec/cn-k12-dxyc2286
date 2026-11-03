#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）初中地理 → _outline.json ＋ _skeleton.json ＋ _points 派单分片。

结构源：
  七上 / 八上 —— 分课时 docx 文件名（`…第X章 <章名>·第N课时 <课时名>分课时教学设计.docx`，七上另含「绪论」1 课时）
  七下 / 八下 —— 大单元 docx 的「十五、教-学-评一致性课时设计」段

口径（与 geography-jin 同构）：
  单元点 id `gztu_u0NN`、课时点 id `gztu_j0NN`，按「册 → 章 → 课时」连续分配
  chapter：单元点 = `<册> 第X章 <章名>`；课时点 = 同上 ＋ ` · 第N课时 <课时名>`
  domain 只用义教地理四领域：地球与地图 / 世界地理 / 中国地理 / 乡土地理
"""
import os, re, json, glob
from docx import Document

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")
BASE = "/Users/a627692/Desktop/中小学教材/中小学教材/各学科分课时设计/地理/中图版（钟作慈）/初中"
DU = "/Users/a627692/Desktop/中小学教材/中小学教材/地理/初中/中图版（钟作慈）"
CN = "一二三四五六七八九十"
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]
GRADE = {"七年级上册": (7, "上"), "七年级下册": (7, "下"), "八年级上册": (8, "上"), "八年级下册": (8, "下")}

# 章 → 义教地理四领域（逐章人工裁定）
DOMAIN = {
    ("七年级上册", "绪论"): "地球与地图",
    ("七年级上册", "一"): "地球与地图",   # 认识地球
    ("七年级上册", "二"): "地球与地图",   # 学用地图
    ("七年级上册", "三"): "世界地理",     # 认识海洋和陆地
    ("七年级上册", "四"): "世界地理",     # 认识天气与气候
    ("七年级上册", "五"): "世界地理",     # 认识人文环境
    ("七年级下册", "六"): "世界地理",     # 认识大洲
    ("七年级下册", "七"): "世界地理",     # 认识地区
    ("七年级下册", "八"): "世界地理",     # 认识国家
    ("七年级下册", "九"): "世界地理",     # 共建人类地球家园
    ("八年级上册", "一"): "中国地理",     # 疆域和人口
    ("八年级上册", "二"): "中国地理",     # 自然环境
    ("八年级上册", "三"): "中国地理",     # 自然资源
    ("八年级上册", "四"): "中国地理",     # 主要的生产活动
    ("八年级下册", "一"): "中国地理",     # 区域划分与地方文化景观
    ("八年级下册", "二"): "中国地理",     # 中国的地理分区
    ("八年级下册", "三"): "乡土地理",     # 认识家乡
    ("八年级下册", "四"): "中国地理",     # 建设美丽中国
}


def cn2num(s):
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN.index(s[1]) + 1
    if "十" in s:
        a, b = s.split("十")
        return (CN.index(a) + 1) * 10 + (CN.index(b) + 1 if b else 0)
    return CN.index(s) + 1


def from_fenkeshi(bk):
    units = {}
    pat = re.compile(r"地理" + bk + r"第([一二三四五六七八九十]+)章\s*(.+?)·第(\d+)课时\s*(.+?)分课时教学设计")
    pat0 = re.compile(r"地理" + bk + r"绪论\s*(.+?)·第(\d+)课时\s*(.+?)分课时教学设计")
    for p in glob.glob(os.path.join(BASE, bk, "*.docx")):
        n = os.path.basename(p)
        m = pat.search(n)
        if m:
            ch, un, no, name = m.group(1), m.group(2).strip(), int(m.group(3)), m.group(4).strip()
            units.setdefault(ch, {"unit": un, "lessons": {}})["lessons"][no] = name
            continue
        m = pat0.search(n)
        if m:
            un, no, name = m.group(1).strip(), int(m.group(2)), m.group(3).strip()
            units.setdefault("绪论", {"unit": un, "lessons": {}})["lessons"][no] = name
    return units


def from_danyuan(bk):
    units = {}
    for p in glob.glob(os.path.join(DU, "*%s第*大单元整体教学设计*.docx" % bk)):
        m = re.search(r"第([一二三四五六七八九十]+)章\s*(.+?)\s*大单元整体教学设计", os.path.basename(p))
        if not m:
            continue
        ch, un = m.group(1), m.group(2).strip()
        d = Document(p)
        paras = [x.text.strip() for x in d.paragraphs if x.text.strip()]
        idx = [i for i, t in enumerate(paras) if t.startswith("十五、")]
        lessons, cur = {}, None
        if idx:
            i = idx[-1]
            j = next((k for k in range(i + 1, len(paras)) if paras[k].startswith("十六、")), len(paras))
            for t in paras[i + 1:j]:
                mm = re.match(r"^（[一二三四五六七八九十]+）\s*第([一二三四五六七八九十\d]+)课时[：:、\s]*(.+)$", t)
                if mm:
                    cur = cn2num(mm.group(1))
                    lessons[cur] = mm.group(2).strip()
        units[ch] = {"unit": un, "lessons": lessons}
    return units


def main():
    os.makedirs(D, exist_ok=True)
    outline = {}
    for bk in BOOKS:
        u = from_fenkeshi(bk) if bk in ("七年级上册", "八年级上册") else from_danyuan(bk)
        outline[bk] = {ch: v for ch, v in u.items() if v["lessons"]}
        print("%s：%d 单元位 / %d 课时" % (bk, len(outline[bk]), sum(len(v["lessons"]) for v in outline[bk].values())))

    order = {"绪论": 0}
    points, shards = [], []
    ui = li = 0
    for bk in BOOKS:
        g, sem = GRADE[bk]
        chs = sorted(outline[bk].keys(), key=lambda c: order.get(c, cn2num(c) if c != "绪论" else 0))
        for ch in chs:
            u = outline[bk][ch]
            ui += 1
            uid = "gztu_u%03d" % ui
            label = ("绪论 %s" % u["unit"]) if ch == "绪论" else ("第%s章 %s" % (ch, u["unit"]))
            points.append(dict(id=uid, name=u["unit"], level="unit", chapter="%s %s" % (bk, label),
                               book=bk, unitNo=ui, lessonNo=0, grade=g, semester=sem,
                               domain=DOMAIN[(bk, ch)], subject="geography-zhongtu-cz",
                               type="conceptual", external=False))
            lessons = []
            for no in sorted(u["lessons"]):
                li += 1
                lid = "gztu_j%03d" % li
                name = u["lessons"][no]
                points.append(dict(id=lid, name=name, level="lesson",
                                   chapter="%s %s · 第%d课时 %s" % (bk, label, no, name),
                                   book=bk, unitNo=ui, lessonNo=no, grade=g, semester=sem,
                                   domain=DOMAIN[(bk, ch)], subject="geography-zhongtu-cz",
                                   type="conceptual", external=False, unitId=uid))
                lessons.append(dict(id=lid, name=name, lessonNo=no))
            shards.append(dict(shard="T%02d" % ui, book=bk, unitNo=ui, unitId=uid,
                               unitLabel=label, domain=DOMAIN[(bk, ch)],
                               grade=g, semester=sem, lessons=lessons,
                               chapter="%s %s" % (bk, label)))
    json.dump({b: outline[b] for b in BOOKS}, open(os.path.join(D, "_outline.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(points, open(os.path.join(D, "_skeleton.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(D, "_shards"), exist_ok=True)
    for s in shards:
        qids = []
        for les in s["lessons"]:
            qids += ["%s_q%02d" % (les["id"], i) for i in range(1, 9)]
        qids += ["%s_q%02d" % (s["unitId"], i) for i in range(1, 6)]
        s.update(book_no=s["unitNo"], outPoints="data/geography-zhongtu-cz/_points/%s.json" % s["shard"],
                 outBank="data/geography-zhongtu-cz/_bank/%s.json" % s["shard"], questionIds=qids)
        json.dump(s, open(os.path.join(D, "_shards", "%s.json" % s["shard"]), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    nu = sum(1 for p in points if p["level"] == "unit")
    nl = sum(1 for p in points if p["level"] == "lesson")
    print("单元点 %d ＋ 课时点 %d ＝ %d 点；派单分片 %d 片；题槽 %d"
          % (nu, nl, len(points), len(shards), sum(len(s["questionIds"]) for s in shards)))
    for s in shards:
        print("  %s %s %s（%s）课时 %d" % (s["shard"], s["book"], s["unitLabel"], s["domain"], len(s["lessons"])))


if __name__ == "__main__":
    main()
