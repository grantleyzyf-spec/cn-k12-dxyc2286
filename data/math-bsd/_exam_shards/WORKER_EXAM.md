# 北师大版数学（math-bsd）试卷工位合同 · 初高中

## 你的活

读派单 `data/math-bsd/_exam_shards/<EID>.json`（含 `book / grade / stage / template / kind / exams[]`，
每卷给出 `paper / scope / topicIds / examId`），为**每卷**写一个 JSON：
`data/math-bsd/exams/<book>/<paper>.json`，并让自检 0 error：

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/check_math_bsd_exam.py "data/math-bsd/exams/<book>/<paper>.json"
```

⛔ 只写自己派单里的卷文件；不改题库、骨架、别人的卷、不改脚本。

## 卷面模板（按派单 `template`）

- `初中`：90 分钟 / 120 分 —— 选择 10×3 ・ 填空 6×4 ・ 解答 8 题（分值依次 6/6/8/8/9/9/10/10）
- `高中`：120 分钟 / 150 分 —— 单选题 8×5 ・ 多选题 4×5 ・ 填空题 4×5 ・ 解答题 6 题（10/12/12/12/12/12）
- `小学1-2`：40 分钟 / 100 分 —— 直接写得数 10×2 ・ 填空 10×2 ・ 选择 8×2 ・ 操作 4×4 ・ 解决问题 4×7
- `小学3-6`：60 分钟 / 100 分 —— 计算 6×4 ・ 填空 10×2 ・ 选择 8×2 ・ 操作 3×4 ・ 解决问题 4×7

## 字段

顶层：`book / kind / term / grade / stage / subject / paper / duration / fullScore / scope / topicIds / examId / sections[]`
（`subject` 写 `math-bsd`；`term` 上册写「上册」、下册写「下册」；`topicIds` 直接用派单给的那一组）。

`sections[i]`：`title`（必须含模板里的题型词，如「一、选择题」）、`rule`（如「每小题 3 分，共 30 分」）、`items[]`。

`items[j]`：
- `no`（全卷连续 1…N）、`score`、`type`（`choice` / `multi` / `fill` / `solve` / `numeric`）、`difficulty`（`basic`/`standard`/`hard`）
- `stem`（≥12 字，纯文本，禁 Markdown 与 LaTeX，公式写 `x²`、`√3`、`a/b` 这种纯文本）
- `options`：choice 4 个 A–D 且文本互异；高中 multi 4 个 A–D 且至少两个正确
- `answer`（字符串）、`analysis`（≥20 字，讲清为什么）、`topicIds`（**必须是本册知识点 id**；
  **单元卷要把 `scope` 那一章的全部课时点各覆盖 ≥1 次**）
- `scoreRule`（`solve` 必填：`[{"desc": "…", "score": n}, …]`，≥2 步且分值之和 = 本题 `score`）
- `itemId` = `<examId>_q<两位数题号>`，如 `mbs_exam_g7a_u01_q01`

## 硬约束（checker 会拦）

- **原创性**：与 `data/math-bsd/questions.json` 任一题干去空白后相似度 **<0.85**（换情境、换数字、换问法）
- **答案位**：choice 的 A–D 分布均匀（同一字母 ≤40%）
- **数学正确**：每题自己复核（方程真解、几何条件写全、数值可算）；不出超纲内容
- **分值自洽**：每段 `items` 分值之和 = 该段 `rule` 写的分；全卷合计 = `fullScore`
- 卷面禁出现「北师大版」以外的出版社名，禁出现课本页码

## 卷种

- `unit`：`paper` 已是「<章全名> 测试卷」，`scope` 只含该章；难度按学段常规单元卷
- `mid` / `fin`：期中 A/B、期末 A/B，`scope` 给的是多章，覆盖面要摊开

## 交付

文件 UTF-8 无 BOM。回复一行汇总：`EID / 卷数 / 各卷 checker 末行 RESULT / 若 FAIL 列出错项`。
