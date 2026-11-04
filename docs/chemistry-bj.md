# 化学（北京版·北京出版社 2024 版·初中九年级）— 知识图谱桶 `chemistry-bj`

> 教材：`中小学教材/化学/初中/北京版/` 仅九年级上、下两册（均为扫描件，目录经 300 dpi OCR 逐条抄录）。
> 建桶日期 2026-11-04；口径对齐 `chemistry-lujiao`／`chemistry-luke` 两个兄弟桶。

## 一、范围

| 册 | 年级 | 章 | 节（课时点） | 点合计 | 卷 |
|---|---|---|---|---|---|
| 九年级上册 | 9 | 6 | 23 | 29 | 10 |
| 九年级下册 | 9 | 4 | 15 | 19 | 8 |
| **合计** | | **10** | **38** | **48** | **18** |

- 章序：1 启航化学之旅／2 揭示燃烧奥秘／3 探究水的奥秘／4 认识化学元素／5 再识化学变化／6 开展低碳行动／7 金属／8 溶液／9 酸和碱／10 常见盐。
- ⚠ 第十章按 **2024 版教材正文为「常见盐」**（旧版大单元 docx 写「海洋中的化学资源」，以教材 PDF 目录为准）。
- 领域用义教化学五领域：科学探究与化学实验／物质的组成与结构／物质的性质与应用／物质的化学变化／化学与社会·跨学科实践。
- 不建点的目录项：跨学科实践活动、学生实验、本章自我评价、附录（但计入教材课时数）。

## 二、结构源与文本包

- 结构：教材 PDF 目录页（九上 p6–p7、九下 p7–p8）＋ 第四章第一节名由大单元 docx 的「十五」课时段核对（＝「化学元素」）。
- 文本包：`_text/九年级上册.txt`（203 页／**70,813 汉字**）、`_text/九年级下册.txt`（127 页／**42,641 汉字**），逐页 `[[pN]]` 标记，学层引文回表用它。
  - 两册均为纯图版 PDF（无文字层），用 `ocr-and-documents/scripts/pdf_pages_vision_ocr.py`（macOS Vision，300 dpi，`--workers 10`）整册 OCR。
  - ⚠ OCR 讹字（「的」→「钓」、「木炭」→「本炭」）不可改，引文只能选无损坏的整句。

## 三、规模（实测）

- 点 **48**（10 章上位点 ＋ 38 课时点）· 题 **354** · 依赖边 **37** · 课标挂标 **24/48（50%）**
- 题/点分布：课时点 8 题×38、章点 5 题×10；题型 选择 164／填空 91／简答 53／数值 46；难度 basic 115／standard 142／hard 97
- 卷 **18** ＝ 10 章卷 ＋ 2 册×（期中 A/B ＋ 期末 A/B）；**22 题 / 120 分 / 120 分钟**
  - 分段：一、选择题 12×3＝36；二、填空与简答 6×6＝36；三、实验探究 2×12＝24；四、综合计算 2×12＝24
- 学层 **38 篇**（九上 23、九下 15），字数 2,186–2,799 汉字，七段
- 讲解 **18 份**，字数 5,676–7,390 汉字，六段

## 四、口径

1. 课时点 8 题（choice≥3／fill≥2／short-answer≥1／numeric≤1），章点 5 题；三档难度每点齐备。
2. 数值题 `verify` 必须纯算术且与 `answer` 等值（`eval(v, {"__builtins__": {}}, {})`），⛔ 不写 `int()/round()`。
3. 先修：38 个课时点按课序连成一条链（跨册相连）⇒ 边数 ＝ 38 − 1 ＝ **37**；10 个章上位点 `prerequisites=[]` ＋ `root_reason`，⛔ 不写 unit→lesson 边（会与「课时不挂上位点」断言互斥）。
4. 卷面：章卷覆盖本章全部课时点；期中＝本册前一半章（按解析后的章号）；期末＝全册，每章 ≥2 题。
5. 讲解硬指标：`**第 N 题（X 分）**` 与卷面 `no/score` 逐字一致；`**思路**`／`**关键一步**`／`**易错**` 各 ≥ 题数×0.7（22 题即 ≥16）；全篇 2,500–7,500 汉字。
6. 学层七段标题逐字；引文 ≥2 处逐字回表本册 `_text`；五步五条每条 65–120 汉字。

## 五、门禁命令

```bash
python3 scripts/test_chem_editions.py chemistry-bj                     # 35/35
python3 scripts/check_chem_editions_exam.py --subject chemistry-bj --all
python3 scripts/check_chem_editions_learn.py --bucket chemistry-bj --all
python3 scripts/check_chem_editions_lecture.py --bucket chemistry-bj --all
```

CI：`.github/workflows/validate-chemistry-bj.yml`（不变量 → itemId → 逐卷 → 逐册学层 → 逐份讲解）。

## 六、站点与交付

- 索引：`build_learn_site.py`（学层）、`build_exam_lecture_site_v2.py`（讲解正文包 `learn/exam/data/chemistry-bj-<册>.json`）、`build_exam_index.py`（整卷）、`build_subjects_registry.py`（版本下拉）。
- 已登记：`schema-topic.json` subject enum、`subjects.json`（化学（北京版））、`subject-groups.json`（化学 4 版：人教/鲁教/鲁科/北京）、`build_exam_index.py` 的 `SUBJECT_EDITION` 与 `SUBJECTS`、`build_subjects_registry.py` 的 `EDITIONS`。
- docx（参数化渲染器，只改环境变量）：
  `MATH_BUCKET=chemistry-bj SUBJECT_NAME=化学 MATH_EDITION=北京版` → 试卷 36 份（18×2）／学层 38 篇＋2 合订／讲解 18 份。

## 七、已知边界与缺口

1. 仅九年级上、下两册（北京版无七、八年级化学，属教材体例）。
2. 学层与讲解为纯文字，未插教材插图。
3. 课标挂标率 50%：义教化学课标引文池仅 13 条（`che-2022`），其余节名在池中无逐条对应表述，按「宁缺毋滥」留空。
4. OCR 源有讹字，个别知识点（如硬水/软水）教材原文无完整可回表句，学层改由正文叙述、引文另选。
