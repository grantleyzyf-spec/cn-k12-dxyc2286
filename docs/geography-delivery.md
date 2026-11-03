# 地理（人教版）交付说明

> 状态：三线（试卷 / 试卷讲解 / 学层精讲）已全部产出并通过机检，已在站点登记并上线。
> 生成日期：2026-11-03。口径：2012 版章序（41 章），教材版本差异见 `docs/geography-edition-gap.md`。

## 1. 交付件位置

| 产物 | 路径 | 份数 |
| --- | --- | ---: |
| 试卷（试卷＋答案两份） | `~/Desktop/学科图谱相关资料/学科图谱原创试卷/地理/人教版/<册>/` | 154（77 卷 × 2） |
| 学层精讲（逐点 104 篇） | `~/Desktop/学科图谱相关资料/学层精讲/地理/人教版/<册>/` | 104 |
| 学层合订本 | `~/Desktop/学科图谱相关资料/学层精讲/地理/人教版/<册>/_合订本/` | 9 |
| 试卷讲解 | `~/Desktop/学科图谱相关资料/试卷讲解/地理/人教版/<册>/<卷>_讲解.docx` | 77 |

数据层（站点读的）：

| 数据 | 路径 | 规模 |
| --- | --- | ---: |
| 知识点 | `data/geography/topics.json` | 104（41 章 / 9 册） |
| 题库 | `data/geography/questions.json` | 832（8 题/点） |
| 先修边 | `data/geography/dependencies.json` | 152 |
| 试卷 | `data/geography/exams/<册>/*.json` | 77 |
| 试卷讲解 | `data/geography/exam_lectures/<册>/*.json` | 77 |
| 学层 | `data/geography/learn/<册>.json` | 9 册 / 104 篇 |
| 教材文字层 | `data/geography/_text/<册>.txt` | 9 册（引文回表源） |

## 2. 卷面口径

- 初中（七上/七下/八上/八下）：**120 分 / 120 分钟**，24 题 = 选择 18×3 分 + 综合 6×11 分。
- 高中（必修一/二、选必 1/2/3）：**150 分 / 150 分钟**，24 题 = 选择 18×3 分 + 综合 6×16 分。
- 卷型：每章 1 张单元卷（41）+ 每册 2 期中 + 2 期末（9×4=36）= **77 卷**。
- 单元卷必须覆盖本章每个知识点；期中期末覆盖本册 ≥8 个点；与题库题干相似度 < 0.85；答案位 A–D 各 ≥15%。

## 3. 复现命令（改任何一环都要按序重跑）

```bash
cd ~/Desktop/cn-k12-dxyc2286

# 题库 / 数据
python3 scripts/rebuild_aggregates_only.py
python3 scripts/build_standards_index.py
python3 scripts/test_geography.py            # 36 项不变量
python3 scripts/validate.py --all
npx --yes ajv-cli@5 validate -c ajv-formats -s data/schema-question.json -d data/geography/questions.json

# 试卷 / 讲解 / 学层
python3 scripts/check_geography_exam.py --all
python3 scripts/check_exam_lecture.py --subject geography
python3 scripts/check_geo_learn.py --dir data/geography/learn

# 站点三处索引
python3 scripts/build_exam_index.py
python3 scripts/build_learn_site.py
python3 scripts/build_exam_lecture_site_v2.py

# 交付件（docx）
MATH_BUCKET=geography SUBJECT_NAME=地理 MATH_EDITION=人教版 python3 scripts/build_math_exam_docx.py
MATH_BUCKET=geography SUBJECT_NAME=地理 MATH_EDITION=人教版 python3 scripts/build_math_learn_docx.py
MATH_BUCKET=geography SUBJECT_NAME=地理 MATH_EDITION=人教版 python3 scripts/build_math_learn_booklet.py
MATH_BUCKET=geography SUBJECT_NAME=地理 MATH_EDITION=人教版 python3 scripts/build_exam_lecture_docx.py
```

## 4. 质检记录（2026-11-03 实测）

- 卷面：77/77 PASS；1848 题，选择 1386 · 综合 462；覆盖 104/104 个知识点。
- 答案位：A 26.0% · B 26.2% · C 25.5% · D 22.3%。
- 难度：basic 497 · standard 904 · hard 447。
- 跨卷近似题：改写后 **0 对**（判据：归一化题干相似度 ≥0.93）。
- 讲解：77 份全部 PASS，字数 6,3xx–8,7xx；**0 处整段照抄卷面 analysis**。
- 学层：104 篇全部 PASS；跨篇重复句 3 条（2 条同为教材原文引用，1 条为「对标对象」句式，可接受）。
- docx：344 份全部可打开、无空壳（试卷 154 · 学层 113 · 讲解 77）。
- 排版抽检（转 PDF 看图）：标题/卷头/选项正常，无乱码溢出；已知小瑕疵见 §5。

## 5. 已知缺口

1. **章序为 2012 版**：与 2026 春/秋新版教材不一致（七下 11 章、八上 5 单元），按 A 方案执行，逐章对表见 `docs/geography-edition-gap.md`。
2. **新版新增「八上 第五章 建设美丽中国」无知识点、无卷**。
3. **旧「第一章 地球和地图」在新版拆成两章**，现有单元卷按旧口径合成一卷。
4. **综合题不自动判分**：站点只给 scoreRule 要点 + 三档自评，不能当正式成绩。
5. **未经教研审读**：机检只保证结构、分值、覆盖、原创性、答案位；题目风格与本地中考是否贴合未审。
6. **卷面排版小瑕疵**：个别选择题的作答括号「（　　）」在行末换行（内容完整、不误读），系行宽所致，非数据错误。
