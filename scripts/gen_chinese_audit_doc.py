# -*- coding: utf-8 -*-
"""生成 docs/chinese-alignment-audit.md（语文教材对齐体检 + 分阶段方案）。数据全部现算。"""
import collections
import json
import os
import re

REPO = os.path.expanduser("~/Desktop/cn-k12-dxyc2286")
ts = json.load(open(f"{REPO}/data/chinese/topics.json", encoding="utf-8"))
qs = json.load(open(f"{REPO}/data/chinese/questions.json", encoding="utf-8"))
audit = open("/tmp/cn/audit.md", encoding="utf-8").read()

per = collections.Counter(f"{t['grade']}{t['semester']}" for t in ts)


def key(k):
    g = int(re.sub(r"\D", "", k) or 0)
    return (g, k[-1])


dist = " · ".join(f"{k} {v}" for k, v in sorted(per.items(), key=lambda x: key(x[0])))
summary = audit.split("## 汇总")[-1].strip() if "## 汇总" in audit else audit
chapters = sorted({t["chapter"] for t in ts})
sample_ch = "、".join(f"`{c}`" for c in chapters[:6])

doc = f"""# 语文（`chinese`）教材对齐核对 —— 现状与补全方案

> 依据技能 `k12-textbook-alignment-1to12`（核对层）执行。本文件是**体检结论 + 分阶段方案**，不是完成报告。

## 1. 现状（可复算）

| 项 | 数值 |
| --- | --- |
| 知识点 | **{len(ts)}**（23 册：1上–9下 义教 18 册 + 高中 10上/10下/11上/11下/12上 5 册） |
| 先修边 | 201 |
| 题 | **{len(qs)}**（**全部 `choice`**，1 题/点） |
| 课标 | 77 条目 / 234 quote（234/234 回表） |
| `domain` | 识字与写字 44 · 阅读与鉴赏 112 · 表达与交流 48 · **梳理与探究 1** |
| 册次分布 | {dist} |
| 章数 | {len(chapters)}，形如 {sample_ch} |

**核心问题：图谱是「板块级」不是「课级」。** 现有 chapter 形如 `一年级上册 识字`、`七年级上册 现代文`，点名为「汉语拼音」「识字」「课文」「写作」「文言文」这类板块名；而人教版语文教材以**课**为最小单位（含略读课 `3*`、口语交际、习作、语文园地、快乐读书吧、阅读综合实践、整本书阅读、课外古诗词诵读等板块）。⇒ 图谱与教材课**无法逐课对应**，这是课级覆盖极低的原因 —— 不是教材缺。

## 2. 教材与课标资源盘点（本机实测）

| 学段 | 有 PDF | 缺 PDF |
| --- | --- | --- |
| 小学 | 一上、一下、二上、二下、三上、三下、四上、五上、六上（9 册） | **四下、五下、六下** |
| 初中 | 七上、七下、八上、八下、九上（5 册） | **九下** |
| 高中 | **无**（本机没有高中语文教材目录） | 必修上/下、选必上/中/下（5 册） |

另：`精准提取各学科教材TXT文档/语文/` 有 9 册逐课精读快照（一上/二上/三上/四上/五上/六上/七上/八上/九上），文件名形如 `t05第一单元天地人.txt`、`t01阅读大青树下的小学.txt` —— **版式每册不同，只能逐册校**。

## 3. 目录抽取实测（脚本 `scripts/extract_chinese_toc.py`）

{summary}

判读：
- **小学 9 册单元数都抽对了（8 单元/册）**，课数 28–41/册（含语文园地、口语交际、习作等活动条目）；
- **初中只抽到 3–5 单元**（七上/八上/九上目录为两栏排版且「第一单元 第二单元」在页眉同排，需逐册标定）；
- **课级覆盖 0–7/N**：图谱点在板块级，没有课级点，所以覆盖低。

## 4. 分阶段方案

| 阶段 | 做什么 | 产出 | 量级 |
| --- | --- | --- | --- |
| **S1 课级清单** | 14 册逐册校订《单元 → 板块 → 课名 → 页码》定稿，入库 `data/chinese/ke_toc/<册>.txt` | 14 份清单，约 **420 课** | 每册 20–40 分钟（人工校订） |
| **S2 课级建点** | chapter 重建为 `<册> 第X单元 <板块>`；按「1 课 = 1 点」建点，保留板块级点作上位概念；课标按学段回表 | ≈ **420 课级点**（205 → 约 500–550） | 脚本批量 + 抽查 |
| **S3 题库 5 题/点** | 每点 5 题、四类题型（choice/fill/numeric/short-answer），简答带 `keypoints` | 约 **2500 题**（现 205） | 分片工人，数轮批次 |
| **S4 收口** | 先修边重建、`domain` 按四领域重挂（`梳理与探究` 现仅 1 点）、docs/README、`test_chinese.py` 扩到本口径 | CI 双绿 | — |

## 5. 硬阻断（需你定）

1. **缺 4 册教材 PDF**：四下、五下、六下、九下 —— 这 4 册课级清单无法建，只能保留板块级并标「教材未到」。
2. **高中 5 册本机完全没有教材**（必修上/下、选必上/中/下）：现有 69 点只能按课标口径核，**不能**按课文建点。要么补教材 PDF，要么高中只做「课标级点 + 题库补齐」。
3. **粒度确认**：S2 采用「1 课 = 1 点」；若更细（古诗按首、文言文按段）或更粗（按单元），点数量会变成 420 的 1.5 倍或 0.25 倍。

## 6. 复算命令

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/test_chinese.py          # 现有口径自检（32 项）
python3 scripts/validate.py chinese
python3 scripts/extract_chinese_toc.py   # 目录抽取 + 课级覆盖核对（输出 /tmp/cn/audit.md、/tmp/cn/units.json）
```
"""
out = f"{REPO}/docs/chinese-alignment-audit.md"
open(out, "w", encoding="utf-8").write(doc)
print("已写", out, len(doc), "字符")
