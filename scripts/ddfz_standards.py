#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""politics（道德与法治／思想政治）课标回表。

源文件（2025 年修订版，均为**文字层 docx**；同名 PDF 是扫描件，无文字层）：
  义教: 中小学教材/中小学教材/2025修订课程标准/《义务教育课程标准》2025修订/word/
        1.《义务教育道德与法治课程标准·日常修订版》(2022年版2025年修订).docx
  高中: 中小学教材/中小学教材/2025修订课程标准/《普通高中课程标准》2025修订/word/
        （5）普通高中思想政治课程标准日常修订版（2017年版2025年修订）.docx

为什么不用 `2025修订课程标准TXT ` 下那份 129KB 的义教 TXT：那是扫描件的 OCR 底本，
三列表格被逐行交错抽出、且部分字形被识成拉丁字母（「RARE」「4G.」「is」），
quote 落进去会既不可读也无法与知识点语义对齐。按技能 §11「文字层 docx → 一段一行落
TXT 快照再回表」的口径，改从 docx 的「内容要求」列抽条，生成干净快照。

产物：
  data/politics/_standards_src/ddfz-2022-content.txt   义教快照（一行一条，'#' 行是说明）
  data/politics/_standards_src/zz-2017-content.txt     高中快照
  data/politics-standards-entries.json                 条目目录（id/学段/主题/序/行号/全文）
  data/politics/topics.json                            standards[] + curriculumRef（--write）

用法：
  python3 scripts/ddfz_standards.py                 # 只出报告，不写 topics.json
  python3 scripts/ddfz_standards.py --write         # 回填 standards/curriculumRef
  python3 scripts/ddfz_standards.py --rebuild-src   # 只重建快照与条目目录
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
SUB = os.path.join(DATA, "politics")
SRC_DIR = os.path.join(SUB, "_standards_src")
EC_DOCX = os.path.expanduser(
    "~/Desktop/中小学教材/中小学教材/2025修订课程标准/《义务教育课程标准》2025修订/word/"
    "1.《义务教育道德与法治课程标准·日常修订版》(2022年版2025年修订).docx")
HS_DOCX = os.path.expanduser(
    "~/Desktop/中小学教材/中小学教材/2025修订课程标准/《普通高中课程标准》2025修订/word/"
    "（5）普通高中思想政治课程标准日常修订版（2017年版2025年修订）.docx")
EC_TXT = os.path.join(SRC_DIR, "ddfz-2022-content.txt")
HS_TXT = os.path.join(SRC_DIR, "zz-2017-content.txt")
ENTRIES = os.path.join(DATA, "politics-standards-entries.json")

# 义教五／六板块 → 短码（课标原文「学习主题」）
THEME_CODE = {
    "入学教育": "RX",
    "道德教育": "DD",
    "生命安全与健康教育": "SM",
    "法治教育": "FZ",
    "中华优秀传统文化与革命传统教育": "CT",
    "中华优秀传统文化教育": "CT",
    "革命传统教育": "GC",
    "国情教育": "GQ",
}
# 高中模块 → 序（必修 1-4，选必 1-3）
HS_MODULE = [
    ("必修1", "中国特色社会主义"),
    ("必修2", "经济与社会"),
    ("必修3", "政治与法治"),
    ("必修4", "哲学与文化"),
    ("选择性必修1", "当代国际政治与经济"),
    ("选择性必修2", "法律与生活"),
    ("选择性必修3", "逻辑与思维"),
]
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4}

CJK = r"\u4e00-\u9fff"


def norm(s: str) -> str:
    """去空白（回表口径：只去空白，标点保留）。"""
    return re.sub(r"\s+", "", s or "")


def key(s: str) -> str:
    """匹配用：只留汉字与字母数字（去标点，容忍 OCR/排版差异）。"""
    return re.sub(r"[^0-9A-Za-z" + CJK + "]", "", s or "")


def squeeze(s: str) -> str:
    """把 PDF 转换留下的「汉字之间的空格」压掉，并清掉标点两侧空格。"""
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s).strip()
    for _ in range(3):
        s = re.sub(r"([" + CJK + r"，。；：、“”（）《》？！、]) (?=[" + CJK + r"，。；：、“”（）《》？！、])", r"\1", s)
        s = re.sub(r"(?<=[" + CJK + r"，。；：、“”（）《》？！、]) (?=[" + CJK + "])", "", s)
    return s.strip()


# ---------------------------------------------------------------- 义教抽取
def extract_ec():
    """返回 [{stage, theme, seq, text}]，按课件顺序。"""
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    d = docx.Document(EC_DOCX)
    stage = None
    items = []
    for child in d.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            txt = Paragraph(child, d).text.strip()
            m = re.match(r"^[（(]([一二三四])[）)]\s*第[一二三四]学段", txt)
            if m:
                stage = CN_NUM[m.group(1)]
        elif tag == "tbl":
            t = Table(child, d)
            if not t.rows:
                continue
            hdr = [c.text.strip() for c in t.rows[0].cells]
            if hdr[:2] != ["学习主题", "内容要求"]:
                continue
            assert stage, "学习主题表出现在任何学段标题之前"
            for row in t.rows[1:]:
                theme = squeeze(row.cells[0].text)
                cell = row.cells[1].text
                for raw in re.split(r"[·•]", cell):
                    txt = squeeze(raw)
                    txt = re.sub(r"^\s*[、，。;；:：]\s*", "", txt)
                    if len(key(txt)) < 6:
                        continue
                    items.append({"stage": stage, "theme": theme, "text": txt})
    # 同 (stage,theme) 内按出现顺序编号
    counter = {}
    for it in items:
        k = (it["stage"], it["theme"])
        counter[k] = counter.get(k, 0) + 1
        code = THEME_CODE[it["theme"]]
        it["seq"] = counter[k]
        it["id"] = f"ddf-2022:{it['stage']}.{code}.{it['seq']:02d}"
    return items


# ---------------------------------------------------------------- 高中抽取
def extract_hs():
    """高中：必修模块的内容要求在分页表格的「内容要求」列；选必模块在正文段落。

    坑：分页会把一条内容要求拦腰截断，前半留在上一张表末行、后半成为下一张表首行
    （实测「…推动党和国家事业取得历史性成就」被劈成两块）。所以按「当前条目」缓冲，
    非 \d+.\d+ 开头的续行一律并回当前条目，遇到新模块标题／学业要求才收口。
    """
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    d = docx.Document(HS_DOCX)
    items = []
    module = None
    theme = None
    phase = "必修"
    cur = None
    item_re = re.compile(r"^(\d+)\.(\d+)\s*(.+)$", re.S)

    def close():
        nonlocal cur
        if cur and len(key(cur["text"])) >= 6:
            cur["text"] = squeeze(cur["text"])
            items.append(cur)
        cur = None

    def feed(text):
        """一行内容要求文本：要么开新条目，要么并回当前条目。"""
        nonlocal cur
        text = text.strip()
        if not text:
            return
        m = item_re.match(text)
        if m:
            close()
            cur = {"module": module, "theme": theme or "",
                   "no": (int(m.group(1)), int(m.group(2))), "text": m.group(3)}
        elif cur and not re.match(r"^(【|◆|·|模块\d)", text):
            cur["text"] += text

    for child in d.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            txt = Paragraph(child, d).text.strip()
            # 课程类型分段标题：（一）必修课程 /（二）选择性必修课程 /（三）选修课程
            ph = re.search(r"^[（(]([一二三])[）)]\s*(必修课程|选择性必修课程|选修课程)", txt)
            if ph:
                close()
                phase = {"一": "必修", "二": "选择性必修", "三": "选修"}[ph.group(1)]
                module = None
                theme = None
                continue
            m = re.search(r"模块\s*(\d)\s*[：:]\s*([^\s·]+)", txt)
            if m:
                close()
                module = (phase, int(m.group(1)))
                theme = None
                continue
            if re.match(r"^【(学业要求|教学提示|内容要求)】", txt):
                if "学业要求" in txt or "教学提示" in txt:
                    close()
                continue
            if re.match(r"^\d+\.\s*\S", txt) and not item_re.match(txt):
                close()
                theme = squeeze(re.sub(r"^\d+\.\s*", "", txt))
                continue
            if module and item_re.match(txt):
                feed(txt)
        elif tag == "tbl":
            t = Table(child, d)
            if not t.rows:
                continue
            hdr = [c.text.strip() for c in t.rows[0].cells]
            if hdr[:1] != ["内容要求"]:
                continue
            for row in t.rows[1:]:
                for line in row.cells[0].text.split("\n"):
                    line = squeeze(line)
                    if not line:
                        continue
                    if re.match(r"^\d+\.\s*\S", line) and not item_re.match(line):
                        close()
                        theme = squeeze(re.sub(r"^\d+\.\s*", "", line))
                        continue
                    feed(line)
    close()
    # 编 id：zz-2017:G.{模块序}.{条序}（选修模块不在本图谱范围）
    items = [it for it in items if it["module"][0] != "选修"]
    for it in items:
        kind, no = it["module"]
        mod_idx = [i for i, m in enumerate(HS_MODULE) if m[0].endswith(str(no)) and
                   ((kind == "必修" and not m[0].startswith("选择性")) or
                    (kind == "选择性必修" and m[0].startswith("选择性")))][0] + 1
        it["mod_idx"] = mod_idx
        it["id"] = f"zz-2017:G.{mod_idx}.{it['no'][0]:02d}{it['no'][1]:02d}"
    return items


# ---------------------------------------------------------------- 快照与目录
def write_snapshot(items, path, title, note):
    os.makedirs(SRC_DIR, exist_ok=True)
    lines = [f"# {title}", f"# {note}", "# 一行一条内容要求；行号即 standards[].sourceLine"]
    for it in items:
        it["line"] = len(lines) + 1
        lines.append(it["text"])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def build_sources():
    ec = extract_ec()
    write_snapshot(ec, EC_TXT,
                   "义务教育道德与法治课程标准（2022年版2025年修订）· 内容要求",
                   f"源 docx：{os.path.basename(EC_DOCX)}（文字层，内容要求列逐条一行）")
    hs = extract_hs()
    write_snapshot(hs, HS_TXT,
                   "普通高中思想政治课程标准（2017年版2025年修订）· 内容要求",
                   f"源 docx：{os.path.basename(HS_DOCX)}（文字层）")
    entries = []
    for it in ec:
        entries.append({"id": it["id"], "stage": "义教", "segment": it["stage"],
                        "theme": it["theme"], "seq": it["seq"], "line": it["line"],
                        "quote": it["text"], "source": os.path.basename(EC_TXT)})
    for it in hs:
        entries.append({"id": it["id"], "stage": "高中", "segment": it["mod_idx"],
                        "theme": it["theme"], "seq": it["no"], "line": it["line"],
                        "quote": it["text"], "source": os.path.basename(HS_TXT)})
    with open(ENTRIES, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    return ec, hs, entries


# ---------------------------------------------------------------- 匹配
def bigrams(s):
    s = key(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def lcs_len(a, b):
    """最长公共子串长度（短串 <80 字，O(n*m) 可接受）。"""
    a, b = key(a), key(b)
    if not a or not b:
        return 0
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


# 领域 → 义教板块偏好（强先验：越界的条目直接不参与打分）
DOMAIN_THEME = {
    "道德教育": {"DD", "SM", "RX"},
    "法治教育": {"FZ"},
    "政治认同": {"GQ", "CT", "GC", "RX"},
    "经济发展": {"GQ", "CT"},
    "哲学思维": {"CT", "GQ", "DD"},
}
# 高中：领域 → 模块序（必修1-4=1-4，选必1-3=5-7）
DOMAIN_MODULE = {
    "道德教育": {1, 2, 3, 4, 6},
    "法治教育": {3, 6},
    "政治认同": {1, 3, 5},
    "经济发展": {1, 2, 5},
    "哲学思维": {4, 7},
}
STOP = {"我们", "自己", "什么", "一下", "可以", "能够", "进行", "通过", "以及",
        "一个", "这个", "就是", "没有", "知道", "了解", "认识", "学习", "生活"}
# 教材用语 → 课标用语 的等价桥（只列确定等价的，不猜近义）
SYN = {
    "校园": "学校", "学校": "校园", "老师": "教师", "教师": "老师",
    "同学": "朋友", "朋友": "同学", "上学": "入学", "入学": "上学",
    "上课": "课堂", "课堂": "上课", "国旗": "国旗", "国歌": "国歌",
    "家": "家庭", "家庭": "家", "爸妈": "父母", "爸爸妈妈": "父母",
    "规矩": "规则", "规则": "规矩", "班规": "规则", "公物": "公共财物",
    "卫生": "健康", "安全": "自我保护", "垃圾": "环境卫生",
    "吃饭": "饮食", "饮食": "吃饭", "作息": "作息", "睡觉": "作息",
    "红旗": "国旗", "国庆": "国旗", "升国旗": "国旗", "敬礼": "国旗",
    "排队": "秩序", "秩序": "排队", "礼貌": "礼仪", "礼仪": "礼貌",
    "诚信": "诚实守信", "说谎": "撒谎", "法律": "法治", "法治": "法律",
    "宪法": "宪法", "权利": "权利", "义务": "义务", "消费": "消费",
    "劳动": "劳动", "职业": "职业", "环境": "环境", "资源": "资源",
    "创新": "创新", "文化": "文化", "传统": "传统", "民族": "民族",
    "国家": "祖国", "祖国": "国家", "党": "中国共产党",
    "思维": "思维", "推理": "推理", "判断": "判断", "概念": "概念",
    "市场": "市场", "经济": "经济", "分配": "分配", "保障": "社会保障",
    "民主": "民主", "选举": "选举", "制度": "制度", "国际": "国际",
}


def expand(s):
    out = [s]
    for k, v in SYN.items():
        if k in s and v not in s:
            out.append(s.replace(k, v))
    return " ".join(out)


def grams(s):
    s = key(s)
    return {s[i:i + 2] for i in range(len(s) - 1)} - STOP


class Scorer:
    """IDF 加权的名称覆盖率打分：常见二元组（我们/学习/生活）几乎不贡献。"""

    def __init__(self, entries):
        import math
        from collections import Counter
        df = Counter()
        for e in entries:
            df.update(grams(e["quote"]))
        n = len(entries)
        self.idf = {g: math.log((n + 1) / (c + 1)) + 0.4 for g, c in df.items()}
        self.default_idf = math.log(n + 1)
        self.df = df
        # 区分度门槛：命中的最稀有二元组必须「整册少见」（df ≤ 4），否则 学校/学习/生活
        # 这类高频词会把它误挂到任何含该词的条目上（实测「这是我们的校园」被挂到「少先队…学校」）
        self.df_cut = 4

    def distinctive(self, point, text):
        """命中的二元组里，最稀有的那个是否够稀有。"""
        shared = grams(point["name"]) & grams(text)
        if not shared:
            return False
        best = min(shared, key=lambda g: self.df.get(g, 0))
        return self.df.get(best, 99) <= self.df_cut

    def score(self, point, text):
        g = grams(point["name"])
        if not g:
            return 0.0
        # 分母只算「课标语料里出现过」的二元组：名称里的生造组合（我向/向国/旗敬）
        # 不该稀释真实命中（否则「我向国旗敬个礼」对「认识国旗、国徽」只剩 0.25）
        total = sum(self.idf[x] for x in g if x in self.idf)
        hit = sum(self.idf[x] for x in (g & grams(text)) if x in self.idf)
        cover = hit / total if total else 0.0
        l = lcs_len(point["name"], text)
        sc = cover + min(l, 8) * 0.05
        ex = expand(point["name"])
        if ex != point["name"]:
            eg = grams(ex)
            etotal = sum(self.idf[x] for x in eg if x in self.idf)
            ehit = sum(self.idf[x] for x in (eg & grams(text)) if x in self.idf)
            if etotal:
                sc = max(sc, 0.9 * ehit / etotal + min(l, 8) * 0.05)
        return sc


def theme_code_of(entry):
    eid = entry["id"]
    return eid.split(":")[1].split(".")[1] if eid.startswith("ddf") else ""


def allowed(entry, point):
    if entry["id"].startswith("ddf"):
        return theme_code_of(entry) in DOMAIN_THEME.get(point.get("domain", ""), set())
    return entry["segment"] in DOMAIN_MODULE.get(point.get("domain", ""), set())


def score(point, entry, scorer):
    return scorer.score(point, entry["quote"])


def slice_quote(entry, point, scorer, lo=12, hi=40, hard=58):
    """从条目原文里取一段**连续**引文：优先整句，其次整分句，绝不从词中间切断。"""
    text = entry["quote"]
    if len(text) <= hi:
        return text
    # 先按句末标点切，再按分句标点切；保留标点，保证候选仍是原文连续片段
    units = [u for u in re.split(r"(?<=[。；])", text) if u.strip()]
    cands = []
    for u in units:
        u = u.strip()
        if lo <= len(u) <= hard:
            cands.append(u)
        elif len(u) > hard:
            parts = [x for x in re.split(r"(?<=[，、])", u) if x.strip()]
            buf = ""
            for x in parts:
                if len(buf) + len(x) <= hi:
                    buf += x
                else:
                    if lo <= len(buf) <= hard:
                        cands.append(buf)
                    buf = x
            if lo <= len(buf) <= hard:
                cands.append(buf)
    if not cands:
        return text if len(text) <= hard else text[:hard]
    best = max(cands, key=lambda c: (scorer.score(point, c), -abs(len(c) - 30)))
    return re.sub(r"[，、；]$", "", best).strip()


def segment_of(point):
    """义教按年级定学段（1-2→1…7-9→4）；高中按册名定模块序（必修1-4=1-4，选必1-3=5-7）。

    坑：册名「高中选择性必修3逻辑与思维」里含子串「必修3」，先判「必修N」会把它算成必修3
    ⇒ 必须**先匹配选择性必修**，再匹配必修。
    """
    ch = point["chapter"].replace("高中", "")
    m = re.match(r"^选择性必修\s*([123])", ch)
    if m:
        return ("高中", 4 + int(m.group(1)))
    m = re.match(r"^必修\s*([1234])", ch)
    if m:
        return ("高中", int(m.group(1)))
    g = point["grade"]
    return ("义教", min(4, max(1, (g + 1) // 2)))


def best_match(p, pool, scorer, floor):
    ranked = sorted(((score(p, e, scorer), e) for e in pool), key=lambda x: -x[0])
    if not ranked or ranked[0][0] < floor:
        return None
    if not scorer.distinctive(p, ranked[0][1]["quote"]):
        return None
    # 单一二元组巧合（「辩证」共享就挂到认识论条目）不算证据：要么连续 3 字重合，要么 ≥2 个二元组
    q = ranked[0][1]["quote"]
    if lcs_len(p["name"], q) < 3 and len(grams(p["name"]) & grams(q)) < 2:
        return None
    return ranked


def match_all(topics, entries):
    """两级匹配（单元表人工定标 + 课时词面择优/继承）。

    · 单元点：`_standards_src/unit_map.json` 里逐条人工定标（1–2 条）。课标条目是上位要求，
      单元名很少与原文逐字相同 ⇒ 置信度以 partial 为主，逐字命中记 exact。
    · 课时/框点：在本单元所属**同一学习主题/模块**的条目池里按 IDF 加权词面择优（≥0.45 且领先），
      择优不到就继承单元第一条，记 `inferred`（课时确实在该上位条目下讲授，但不是逐句命中）。
    """
    umap = json.load(open(os.path.join(SRC_DIR, "unit_map.json"), encoding="utf-8"))["politics"]
    by_id = {e["id"]: e for e in entries}
    scorer = Scorer(entries)

    def theme_pool(entry):
        return [e for e in entries
                if e["stage"] == entry["stage"] and e["segment"] == entry["segment"]
                and e["theme"] == entry["theme"]]

    ids_unit = {p["id"] for p in topics if p.get("level") == "unit"}
    unit_of = {}
    for p in topics:
        for pre in p.get("prerequisites") or []:
            if pre in ids_unit:
                unit_of[p["id"]] = pre
                break

    def std(p, e, conf):
        return {"id": e["id"], "confidence": conf,
                "quote": slice_quote(e, p, scorer), "sourceLine": e["line"]}

    out = {}
    for p in topics:
        if p["id"] in ids_unit:
            ids = umap.get(p["id"]) or []
            stds = []
            for eid in ids:
                e = by_id[eid]
                kn = key(p["name"])
                conf = "exact" if kn and len(kn) >= 4 and kn in key(e["quote"]) else "partial"
                stds.append(std(p, e, conf))
            out[p["id"]] = stds
    for p in topics:
        if p["id"] in ids_unit:
            continue
        uid = unit_of.get(p["id"])
        base = out.get(uid) or []
        if not base:
            out[p["id"]] = []
            continue
        pool = []
        for s in base:
            for e in theme_pool(by_id[s["id"]]):
                if e not in pool:
                    pool.append(e)
        ranked = best_match(p, pool, scorer, 0.22)
        if ranked:
            sc, e = ranked[0]
            second = ranked[1][0] if len(ranked) > 1 else 0
            kn = key(p["name"])
            if kn and len(kn) >= 4 and kn in key(e["quote"]):
                out[p["id"]] = [std(p, e, "exact")]
            elif sc - second >= 0.02:
                out[p["id"]] = [std(p, e, "partial")]
            else:
                out[p["id"]] = [dict(base[0], confidence="inferred")]
        else:
            out[p["id"]] = [dict(base[0], confidence="inferred")]
    return out


def verify_quotes(topics, entries):
    """quote 必须是同条目原文的子串（去空白口径）。"""
    by_id = {e["id"]: e for e in entries}
    bad = []
    for p in topics:
        for s in p.get("standards") or []:
            e = by_id.get(s["id"])
            if not e:
                bad.append((p["id"], s["id"], "条目不存在"))
            elif norm(s["quote"]) not in norm(e["quote"]):
                bad.append((p["id"], s["id"], "quote 不在条目原文中"))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--rebuild-src", action="store_true")
    ap.add_argument("--show", type=int, default=12)
    a = ap.parse_args()

    if a.rebuild_src or not os.path.exists(ENTRIES):
        ec, hs, entries = build_sources()
        print(f"快照已重建：义教 {len(ec)} 条 / 高中 {len(hs)} 条")
    else:
        entries = json.load(open(ENTRIES, encoding="utf-8"))
        print(f"沿用条目目录：{len(entries)} 条")

    topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
    res = match_all(topics, entries)

    hit = {k: v for k, v in res.items() if v}
    from collections import Counter
    print("覆盖：%d/%d = %.1f%%" % (len(hit), len(topics), 100 * len(hit) / len(topics)))
    print("confidence:", Counter(s["confidence"] for v in hit.values() for s in v))
    print("按学段:", Counter(segment_of(p)[0] + str(segment_of(p)[1]) for p in topics
                          if p["id"] in hit))
    print("条目覆盖：%d/%d 条被引用" % (len({s["id"] for v in hit.values() for s in v}),
                                    len(entries)))
    miss = [p for p in topics if not res.get(p["id"])]
    print("未命中 %d 个:" % len(miss), [p["name"] for p in miss[:a.show]])
    print("命中样例（前 %d）:" % a.show)
    for p in topics[:a.show]:
        for s in res.get(p["id"]) or []:
            print("  %-8s %-12s -> %-20s %-8s %s" % (p["id"], p["name"][:10], s["id"],
                                                    s["confidence"], s["quote"][:34]))

    if a.write:
        for p in topics:
            stds = res.get(p["id"]) or []
            p["standards"] = stds
            p["curriculumRef"] = stds[0]["id"] if stds else ""
        bad = verify_quotes(topics, entries)
        print("回表校验：", "全部命中" if not bad else f"{len(bad)} 条不合格")
        for b in bad[:10]:
            print("  BAD", b)
        if bad:
            sys.exit(1)
        with open(os.path.join(SUB, "topics.json"), "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=1)
        print("已写回 data/politics/topics.json")


if __name__ == "__main__":
    main()
