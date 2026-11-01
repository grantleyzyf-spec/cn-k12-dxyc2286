# 道德与法治 / 思想政治（politics）

> 数据目录 `data/politics/`，学科代码 `politics`。义教 14 册（人教版）＋ 高中 7 册（统编版）。

## 规模（2026-11-02 结构返修后）

| 项 | 值 |
| --- | --- |
| 册 | 21（义教 14 ＋ 高中 7） |
| 教材单元 | 78（义教 57 ＋ 高中 21） |
| 课 | 高中 58（义教是「单元→课」两级，「课」即课时点） |
| 框 | 高中 135 |
| 知识点 | **435**（单元点 115 ＝ 义教 57 单元 ＋ 高中 58 课；课时点 320 ＝ 义教 185 课 ＋ 高中 135 框） |
| 先修边 | **646**（hard 576 ／ soft 70） |
| 空引文点 | 0 |
| 目录点 / 框号乱序 | 0 / 0 |

教材缺 4 册：四年级下册、五年级下册、六年级下册、九年级下册（无 PDF，**不造点**）。

## 高中结构（2026-11-02 重建）

原盘点把「课」标成「第N单元」、框题靠正文里的「第X框」反推，结果卷进目录页与「目」级子标题（5 个 `目录` 点、14 个单元框号乱序、选必册序倒置）。现改为**只读 PDF 目录页**重建：

- 层级 `第X单元 第Y课 第Z框` 写进 `chapter`；`level=unit` 落在**课**上、`level=lesson` 落在**框**上（口径：以框为可诊断点、课为单元点）。
- 册序按课程顺序写死（文件名按 ISBN 排序会把选必 3 排到最前）。
- 框题在目录里没有「第X框」编号 ⇒ 靠缩进与「带页码的非课行」判定；课名折行（必修 1 第四课）按「无页码 + 下一行续」合并。
- `综合探究`（21 个）不单独建点，保留在 `_inventory.json` 的 `explores` 里。
- 必修 1 教材不分单元 ⇒ `chapter` 直接是 `第N课`，不虚构单元标题。

课/框数：必修1 4/9、必修2 4/8、必修3 9/23、必修4 9/26、选必1 9/20、选必2 10/21、选必3 13/28。

## 课标口径

| 学段 | 课标 | 条目数 | 编号式 |
| --- | --- | --- | --- |
| 义教 | 《义务教育道德与法治课程标准（2022年版2025年修订）》 | 134 | `ddf-2022:{学段}.{板块}.{序}` |
| 高中 | 《普通高中思想政治课程标准（2017年版2025年修订）》 | 65 | `zz-2017:G.{模块}.{序}` |

板块短码：`RX` 入学教育／`DD` 道德教育／`SM` 生命安全与健康教育／`FZ` 法治教育／`CT` 中华优秀传统文化（与革命传统）教育／`GC` 革命传统教育／`GQ` 国情教育。高中模块序：必修 1–4 = 1–4，选择性必修 1–3 = 5–7。

**源文件是文字层 docx，不是那份 129KB 的 TXT**：`2025修订课程标准TXT` 下的义教 TXT 是对扫描 PDF 的 OCR，三列表格被逐行交错抽出、部分字形被识成拉丁字母（`RARE`、`4G.`、`is`），引文落进去既不可读也无法对齐。按「文字层 docx → 一段一行落 TXT 快照」的既定做法，从 docx 的「内容要求」列抽条：

- `data/politics/_standards_src/ddfz-2022-content.txt`（134 条，一行一条，行号即 `sourceLine`）
- `data/politics/_standards_src/zz-2017-content.txt`（65 条）
- `data/politics-standards-entries.json`（条目目录：id／学段／主题／序／行号／全文）
- 高中必修模块的内容要求在分页表格里，一条会被分页拦腰截断（前半在上一张表末行、后半成下一张表首行）⇒ 抽取按「当前条目」缓冲续行。

## 课标回表

| 指标 | 值 |
| --- | --- |
| 有引文的知识点 | 435 / 435（100%） |
| 引文条数 | **489** |
| 逐字回表（按 `sourceLine` 读快照再比对） | 489 / 489 |
| 置信度 | `exact` 31 ／ `partial` 268 ／ `inferred` 190 |
| 被引用条目 | 149 / 199 |

两级做法：

1. **单元点 115 个逐条人工定标**（`_standards_src/unit_map.json`，每条 1–2 个条目）。课标条目是上位要求，单元/课名很少与原文逐字相同 ⇒ 以 `partial` 为主。
2. **课时/框点 320 个**在本单元所属同一学习主题/模块的条目池里按 IDF 加权词面择优（要求连续 3 字重合或 ≥2 个二元组命中，且命中的最稀有二元组 df ≤ 4）；择优不到继承单元第一条，记 `inferred`。

⚠️ 语义精度如实说明：`exact` 是逐字命中；`partial` 是同主题块内的词面择优（抽样目测 8–9 成贴题）；`inferred` 是继承单元上位条目。**不宣称 489 条都是逐句精确对齐**；逐句精确只能对 320 个课时点逐条人工审定。

## 题库（2026-11-02 建成）

| 指标 | 值 |
| --- | --- |
| 题量 | **3135**（课时/框点 320×8 ＋ 单元/课点 115×5） |
| 覆盖 | 435 / 435 知识点，每点题量**恰好** 8 / 5（无一点不足） |
| 分片 | 57 片（`data/politics/_shards/S01…S57`），逐片 `qd_check_bank.py` 末行 PASS |
| 题型 | 全部 `choice`（4 选项、答案 ∈ labels） |
| 难度 | basic 935 ／ standard 1246 ／ hard 954 |
| 答案位 | A 794 ／ B 804 ／ C 779 ／ D 758（单档 24.2–25.6%） |
| 题干 | 最短 13 字、中位 47 字；**无模板题干**（无「关于「X」，下列说法正确的是」）、**无重复题干** |
| 解析 | 最短 42 字、中位 83 字；逐项点出错因（以偏概全／概念混淆／绝对化／主体错位／张冠李戴） |
| 义教 / 高中 | 1765 ／ 1370 题 |
| schema | `jsonschema.validate(questions, schema-question)` OK |

`scripts/test_politics.py` **39 项全过**（结构 25 项 ＋ 课标 6 项 ＋ 题库 8 项），
`python3 scripts/validate.py politics` → Total Errors: 0（435 点 / 646 边 / 3135 题）。

题库口径：义教用学生身边情境（班级、家庭、校园、社区），高中用时政/材料情境；
错项必须是真实错法，禁「以上都不是／不知道／与本题无关」这类占位项（门禁已断言）。

## 已知缺口

1. **字段占位**：435 点的 `description` 全等于 `name`，`mastery_criteria`/`diagnostic_question` 全为同一模板。写题阶段必须逐点重写（第 2–4 步）。
2. 教材缺 4 册（见上），未造点。
3. 高中 `综合探究`（21 个）不建点，只留在盘点表 `explores`。
4. 高中按「课＝单元点、框＝课时点」入图；若改按课诊断，只动 `level` 一处。
5. 题库为空（`questions.json` = `[]`），第 2–4 步待做。

## 自检命令

```bash
python3 scripts/ddfz_hs_rebuild.py --show          # 高中 7 册结构（单元/课/框）
python3 scripts/ddfz_hs_rebuild.py --write         # 重建高中点与边（义教 242 点原样保留）
python3 scripts/ddfz_standards.py                  # 课标回表报告（不写）
python3 scripts/ddfz_standards.py --write          # 回填 standards/curriculumRef（含逐字回表校验）
python3 scripts/ddfz_standards.py --rebuild-src    # 从 docx 重建快照与条目目录
python3 scripts/ddfz_audit.py --json data/politics/_audit.json   # 结构体检（目录点/框号/占位）
python3 scripts/validate.py politics               # Total Errors: 0
python3 -c "import json,jsonschema;jsonschema.validate(json.load(open('data/politics/topics.json')),json.load(open('data/schema-topic.json')));print('OK')"
```
