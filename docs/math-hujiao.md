# 沪教版数学知识图谱（math-hujiao）

## 教材范围
5 册（高中）：必修第一册、必修第二册、必修第三册、选择性必修第一册、选择性必修第二册。
必修第四册与选择性必修第三册是**数学建模活动册**（目录无章、无节），按口径不建点、不出卷。

| 项 | 规模 |
|---|---|
| 章 | 21 |
| 节 | 80 |
| 知识点 | **101**（单元级 21 + 课时级 80） |
| 题库 | **745**（choice 356 / numeric 186 / fill 113 / short-answer 90；basic 241 / standard 313 / hard 191） |
| 先修边 | 159 |
| 整卷 | **41** |
| 学层精讲 | **80 篇**（22 片合并，5 册） |

## 数据层
`data/math-hujiao/{topics,questions,dependencies}.json` + `_skeleton.json`；
知识点 id：`mhj_h###`（单元）/ `mhj_h1###`（课时），册名带「沪教版」前缀。

- 课标：`mat-2017` 条目，`quote` 与仓库同 id 条目逐字一致；**79/101 点挂引文**，
  其余 22 点在 `_std_waivers.json` 登记（高中课标无直接表述，留空不编），逐点含最近邻人与相似度。
- 题目字段：`answer` 一律字符串（schema 要求）；numeric 的 `verify` 可复算。
- 题库分布：choice 356 / numeric 186 / fill 113 / short-answer 90；basic 241 / standard 313 / hard 191。

## 整卷（exams/）
- 41 卷 / 5 册 = 每册 5 份单元卷 + 期中 A/B + 期末 A/B
- 卷面统一**高中模板**：120 分钟 / 150 分 / 22 题（单选 8×5 + 多选 4×5 + 填空 4×5 + 解答 10/12/12/12/12/12）
- 派单：`_exam_shards/E*.json`（`scripts/gen_exam_shards.py math-hujiao`，按册切分不跨册）
- 逐卷自检：`python3 scripts/check_math_hujiao_exam.py <卷>`，父代重跑 **41/41 PASS**

## 学层精讲（learn/）
- 派单：`scripts/gen_learn_shards.py math-hujiao --per-shard 4` → 22 片 / 80 篇
- 教材原文：`/tmp/mhj/<h1|h2|h3|x1|x2>/pNNN.txt`（逐页 OCR）；合同 `learn/_shards/WORKER_LEARN.md`
- 自检：`python3 scripts/check_math_hujiao_learn.py <分片或合并文件>`（TXT 缺失时自动跳过回表，便于 CI）
- 合并：`python3 scripts/merge_learn_parts.py math-hujiao scripts/check_math_hujiao_learn.py --write`
- 实测：22/22 分片 PASS → 合并 5 册 **80/80 篇**，合并后逐册 checker 全 PASS

## 试卷讲解（exam_lectures/）
- 派单：`scripts/gen_lecture_shards.py math-hujiao --per-shard 2` → 21 片 / 41 卷
- 合同：`_exam_shards/_lecture_shards/WORKER_LECTURE.md`（六段 + 五步标签逐字 + 逐题 `第 N 题` 覆盖）
- 自检：`python3 scripts/check_math_hujiao_lecture.py <讲解>`（高中 4500–8800 汉字）

## 自检与门禁
```bash
python3 scripts/validate.py math-hujiao                      # 0 error
python3 scripts/test_math_hujiao.py                          # 38/38
python3 scripts/check_math_hujiao_exam.py data/math-hujiao/exams/<册>/<卷>.json
python3 scripts/merge_learn_parts.py math-hujiao scripts/check_math_hujiao_learn.py
```
CI：`.github/workflows/validate-math-hujiao.yml`

## 口径备忘
- 册名匹配必须**长键优先**：「选择性必修第一册」会被「必修第一册」误命中（`hj_extract.py` 已修）。
- 教材扫描 OCR 把数学符号读成生僻字（犃/犅/狓/犪/狀），写学层引用时只取纯汉字句，符号在正文用纯文本重述。
- `checker` 里 ASCII `<` 会被 HTML 标签正则误判 → 正文用全角 `＜`（与仓库既有卷一致）。
