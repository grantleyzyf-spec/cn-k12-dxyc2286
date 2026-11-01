# 苏科版数学知识图谱（math-suke）

苏科版＝江苏凤凰**科学技术**出版社（初中数学）；与「苏教版」（江苏凤凰**教育**出版社，小学/高中）不是同一家，数据分别在 `data/math-suke/` 与 `data/math-sujiao/`。

## 教材范围
初中 5 册：七年级上册、七年级下册、八年级上册、八年级下册、九年级上册。
库内缺 **九年级下册**（库级缺口，按「等新教材」不建）。

| 项 | 规模 |
|---|---|
| 章 | 28 |
| 知识点 | **141**（单元级 28 + 课时级 113） |
| 题库 | **1044**（choice 544 / numeric 248 / fill 144 / short-answer 108） |
| 先修边 | 225 |
| 整卷 | 48（28 单元卷 + 20 期中期末） |
| 学层精讲 | 113 篇（24 片） |

## 数据层
`data/math-suke/{topics,questions,dependencies}.json` + `_skeleton.json`；
id 前缀 `msk_`（单元 `msk_p0xx`、课时 `msk_p1xxx`）；册名带「苏科版」前缀，`subject` 用桶名 `math-suke`（与 math-bj / math-hebei / math-hujiao 一致，避免被聚合器并进人教桶）。

## 整卷（exams/）
- **初中卷面**：90 分钟 / 120 分 / 24 题 —— 选择 10×3 + 填空 6×4 + 解答 8 题（6/6/8/8/9/9/10/10）
- 派单：`scripts/gen_exam_shards.py math-suke --prefix msk_exam` → `_exam_shards/E01–E10`（10 片 / 48 卷，按册切分不跨册）
- 合同：`_exam_shards/WORKER_EXAM.md`
- 自检：`python3 scripts/check_math_suke_exam.py <卷>`

## 学层精讲（learn/）
- 教材原文：`scripts/ocr_bucket_books.py math-suke --root msk` 按骨架 volumes 逐页渲染 + macOS Vision 识别，产出 `/tmp/msk/<tag>/ocr/pNNN.txt`
  - 实测 5 册 968 页、**失败 0**、每册 3.5–4.7 万汉字（汉字占比 0.47–0.56）
  - ⚠️ 必须用 `/usr/bin/python3`（PyMuPDF + pyobjc 在系统 python 里）；Hermes 自带的 3.14 解释器没有 pyobjc，脚本会「进度正常但文件 0 字节」
- 派单：`scripts/gen_learn_shards.py math-suke --per-shard 5 --booktag …=k7a|k7b|k8a|k8b|k9a --txt-root /tmp/msk` → 24 片 / 113 篇
- 合同：`learn/_shards/WORKER_LEARN.md`；自检：`scripts/check_math_suke_learn.py`
- 合并：`python3 scripts/merge_learn_parts.py math-suke scripts/check_math_suke_learn.py --write`

## 自检与门禁
```bash
python3 scripts/validate.py math-suke    # 0 error
python3 scripts/test_math_suke.py        # 39/39
python3 scripts/check_math_suke_exam.py  # 逐卷
```
CI：`.github/workflows/validate-math-suke.yml`（结构 + itemId + 卷面 + 学层 + 讲解五道闸门）

## 口径备忘
- `topics.json` 无 `level` 字段：课时/单元按 `chapter` 是否含「 · 」派生（测试脚本内置）。
- `standards[].quote` 原是从扫描目录页抽的残句（如「确进行有理数的乘方运算;」），已按全仓同 id 原文回填，**140/140 逐字一致**；同类残句在苏教（196 条）、湘教（127 条）、青岛（94 条）一并修过。
- 骨架里 k8a/k8b/k9a 的 `pdf` 字段曾为空（盘上却有 PDF），已补回，否则 OCR 与学层派单都会跳过这三册。
