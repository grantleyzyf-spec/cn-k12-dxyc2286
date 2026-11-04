# 化学版本桶题库合同（一点一片，逐字照做）

## 你的任务
读本目录给你的分片 JSON（`B<NN>.json`），为其中**每一个知识点**写指定数量的诊断题，
写成对象形状 `{"shard": "<片号>", "bucket": "<桶名>", "questions": [ … ]}` 落盘到分片里写的 `out` 路径。

## 题量（硬指标，多一道少一道都算不合格）
- `level=unit`（单元/章上位点）：**恰好 5 题**
- `level=lesson`（节/课题）：**恰好 8 题**

## 题型与难度（硬指标）
- choice（选择题）≥3（5 题片 ≥2）、fill（填空题）≥2（5 题片 ≥1）、short-answer ≥1、numeric ≤1
- 三档难度 `basic / standard / hard` **每点各 ≥1 道**
- 选择题必须 4 个选项、`choices` 与 `options` 逐字同构、`answer` 是字母且在 label 内
- 填空题 `answer` 用文字，题干里必须有 `____`（四个下划线）
- numeric 题必须给 `verify`：**纯算术表达式**，只许数字与 + - * / ( ) ** ，⛔ 不许 `int()`/`round()`/单位/文字；`eval(verify)` 的结果必须等于 `answer`
- short-answer 的 `answer` 用「；」分 2–3 条要点

## 字段（逐字照这个键名，不许增删）
```json
{
  "id": "<topicId>_q01",
  "topicId": "<片里给的 topicId>",
  "subject": "<桶名>",
  "type": "choice|fill|short-answer|numeric",
  "difficulty": "basic|standard|hard",
  "prompt": "题干（≥12 字，选择题结尾要有（　））",
  "options": [{"label": "A", "text": "…"}, …]    // 非选择题写 []
  "choices": [{"label": "A", "text": "…"}, …]    // 与 options 完全相同
  "answer": "B 或文字答案",
  "explanation": "解析（≥25 汉字，说明为什么，结尾写「故选 X」或给出答案依据）",
  "verify": "数值题的算式，其它题不写这个键"
}
```
题号 `id` 由父代分配（片里 `id_range` 给出），⛔ 不许自己续号、不许跳号。

## 内容要求
- 只考**本知识点**：`chapter` 与 `description` 写明范围，超纲（考到别的节的内容）算不合格。
- 二年级以上口径：化学方程式、符号、单位写规范；元素符号大小写正确（如 H₂O、CO₂ 用普通文本 H2O、CO2 也可）。
- 干扰项要像真的错的（常见错误、相近概念），⛔ 禁「以上都不对」「无法确定」「仅在大学学习」这类凑数项。
- 禁 Markdown 标记（**、##、表格竖线）；成对绝对值 `|x|` 除外。

## 自检（写完必须跑，输出贴进汇报）
```bash
python3 scripts/check_chem_editions_bank.py --shard <你的 out 路径>
```
必须看到 `RESULT: PASS`。不 PASS 就改到达标，⛔ 不要改 checker。

## 落盘
- 只写自己的 `out` 路径，⛔ 不要动 `topics.json`、`questions.json`、别人的分片、技能库文件。
- 写完在汇报里贴：点数、题数、每题题型分布、三档难度分布、自检末行。
