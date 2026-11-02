# 数学（鄂教版）`math-ejiao`

湖北教育出版社《普通高中教科书·数学》，7 册（必修第一~四册 + 选择性必修第一~三册）。
本学科桶与 `math`（人教版）、`math-hujiao`（沪教版）、`math-xiangjiao`（湘教版）等并列，站点按 `subject` 分别取数。

## 1. 规模

| 项 | 数量 |
|---|---|
| 知识点 | **232**（章级 20 + 课时级 212） |
| 诊断题 | **1796** |
| 试卷 | **48**（单元 20 + 期中 14 + 期末 14）/ **1056 题** |
| 学层精讲 | **212 篇 / 7 册 / 356,414 汉字**（平均 1,681 字） |
| 试卷讲解 | 48 份（每卷一份，六段） |
| 课标挂标 | 91.8%（`mat-2022` 条目，逐字回表） |

## 2. 册次与结构

| 册 | 点数（章+课时） | 卷数 | 学层篇数 | grade |
|---|---|---|---|---|
| 必修第一册 | 31（3 章 + 28） | 7 | 28 | 10 |
| 必修第二册 | 42（4 章 + 38） | 8 | 38 | 11 |
| 必修第三册 | 39（3 章 + 36） | 7 | 36 | 12 |
| 必修第四册 | 22（2 章 + 20） | 6 | 20 | 13 |
| 选择性必修第一册 | 39（3 章 + 36） | 7 | 36 | 14 |
| 选择性必修第二册 | 24（2 章 + 22） | 6 | 22 | 15 |
| 选择性必修第三册 | 35（3 章 + 32） | 7 | 32 | 16 |

- `chapter` 形如「鄂教版必修第一册 第1章 集合」，课时级再加「 · 集合的概念与元素」；**没有 `level` 字段**，课时点靠 `chapter` 是否含「 · 」判定（门禁与派单脚本都按这条口径）。
- 教材全部是扫描件，正文用本地 OCR 落 `_src/h1~h7_full.txt`；学层「课本原文」逐字回表以该全文为准。

## 3. 卷面规格

高中模板：**150 分 / 120 分钟 / 22 题**——单选题 8×5、多选题 4×5、填空题 4×5、解答题 6 题（10, 12, 12, 12, 12, 12）。
`examId` 形如 `mej_exam_b1_u01`（b1~b4 = 必修一~四，x1~x3 = 选必一~三）；每题必带 `itemId = <examId>_qNN`。

## 4. 门禁

| 脚本 | 判据 |
|---|---|
| `data/math-ejiao/_scripts/test_math_ejiao.py` | 学科不变式（id 命名、四领域、先修无环、每题有诊断题、课标 id 可解析等） |
| `scripts/check_math_ejiao_exam.py` | 单卷：结构/满分/时长/题号连续/section 分值和＝满分/topicIds 属本册且单元卷覆盖 scope 全部点/选项互异/`verify` 可复算/与题库相似度 <0.85 |
| `data/math-ejiao/_scripts/check_learn_ej.py` | 单篇（`--shard <topicId>`）或整册：七段标题、1000–2000 汉字、`> ` 引文 ≥2 处且在本册 OCR 全文逐字命中、❌/✅ 各 ≥2、例题 ≥2、五步五条、自查 ≥3 |
| `scripts/check_math_ejiao_lecture.py` | 单份讲解：六段标题、高中字数带 4500–8800、逐题覆盖、五步五条、自查 ≥6 |

## 5. 复现流程

```bash
cd data/math-ejiao
python3 _scripts/make_exam_shards_ej.py --write      # 48 卷 → 12 片
python3 _scripts/merge_learn_ej.py --write           # _learn_out/*.json → learn/<册>.json
python3 _scripts/test_math_ejiao.py                  # 学科不变式
for f in /path/to/exams/*/*.json; do python3 ../../scripts/check_math_ejiao_exam.py "$f"; done
for f in learn/*.json; do python3 _scripts/check_learn_ej.py "$(basename $f .json)"; done
```

## 6. 已知缺口

1. **选择性必修第四册无教材**（本地无 PDF），该册不出点、不出卷。
2. 教材为扫描件，OCR 有少量错字（`α/β` 常被读成 `a/β`、`{}` 读成 `〈〉`），引文一律保持「逐字照 OCR 原样」，不做人工改写。
3. 课标挂标 91.8%，其余为课标无逐条条文的章级/方法课点。
