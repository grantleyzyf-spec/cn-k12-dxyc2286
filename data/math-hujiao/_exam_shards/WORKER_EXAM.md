# 沪教版数学（math-hujiao）试卷工位合同 · W2

## 你的活
读派单 `data/math-hujiao/_exam_shards/<EID>.json`（含 `book / grade / stage / template / kind / exams[]`，
每卷给出 `paper / scope / topicIds / examId`），为**每卷**写一个 JSON：
`data/math-hujiao/exams/<book>/<paper>.json`，并让自检 0 error：

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/check_math_hujiao_exam.py "data/math-hujiao/exams/<book>/<paper>.json"
```

⛔ 只写自己派单里的卷文件；不改题库、骨架、别人的卷、不改脚本。

## 卷面模板（按派单 `template`）
- `小学1-2`：40 分钟 / 100 分 —— 直接写得数 10×2 ・ 填空 10×2 ・ 选择 8×2 ・ 操作 4×4 ・ 解决问题 4×7
- `小学3-6`：60 分钟 / 100 分 —— 计算 6×4 ・ 填空 10×2 ・ 选择 8×2 ・ 操作 3×4 ・ 解决问题 4×7
- `初中`：90 分钟 / 120 分 —— 选择 10×3 ・ 填空 6×4 ・ 解答 8 题（6/6/8/8/9/9/10/10）
- `高中`：120 分钟 / 150 分 —— 单选题 8×5 ・ 多选题 4×5 ・ 填空题 4×5 ・ 解答题 6 题（10/12/12/12/12/12）

## 字段
`book / kind / paper / stage / grade / duration / fullScore / scope / examId / sections[]`；
`sections[i]`：`title`（必须含模板里的题型词）、`items[]`；
`items[j]`：`no`（全卷连续 1…N）、`score`、`type`（choice / multi / fill / solve / numeric）、`difficulty`、
`stem`（≥12 字，纯文本，禁 Markdown 与 LaTeX）、`options`（choice/multi 必须 4 个 A–D 且文本互异）、
`answer`、`analysis`（≥20 字）、`topicIds`（**必须是本册知识点 id**；unit 卷要覆盖 `scope` 章节的全部点各 ≥1 次）、
`scoreRule`（solve 必填，≥2 步、分值和 = 本题 score）。

## 硬约束（checker 会拦）
- **原创性**：与 `data/math-hujiao/questions.json` 任一题干去空白后相似度 **<0.85**
- **答案位**：choice 的 A–D 分布均匀（同一字母 ≤40%）
- **数学正确**：每题自己复核；几何题文字写全条件、不依赖插图；小学不出超纲内容；π 取 3.14 并注明
- 卷面数字与语境要符合该册教材（小学低年级不出乘除法以外的超纲运算，高中不出超纲定理）

## 卷种
- `unit`：`paper` 已是「<章/单元全名> 测试卷」，`scope` 只含该章
- `mid` / `fin`：期中 A/B、期末 A/B，`scope` 是派单给的多章

## 交付
文件 UTF-8 无 BOM；回复一行汇总：`EID / 卷数 / 各卷 checker 末行 RESULT / 若 FAIL 列出错项`。
