# 沪科教版高中物理 · 出卷合同（一工位两卷）

## 你的任务
读 `data/physics-hkjy/_exam_tasks.json` 里属于你的 `E<NN>` 条目（含 `exams[]` 卷号），再逐卷读
`data/physics-hkjy/_exam_spec/<examId>.json`，按 spec 写**整卷**，落盘到 spec 的 `out`。

## 卷面（逐字照 spec 的 `sections`，不许增删题目、不许改分值）
- 150 分 / 90 分钟 / **21 题**：一、单项选择 10×3＝30；二、多项选择 5×4＝20；三、实验题 2×15＝30；四、计算题 4 题（15+18+18+19）＝70。
- 每题字段：`no`（1–21 连续）、`itemId`（`<examId>_qNN`）、`type`（choice/multi/experiment/calc）、
  `score`、`stem`、`answer`、`analysis`、`topicIds`（1–2 个，取自 spec 的 `must_cover`）。
- `choice`/`multi` 另带 `options`（4 项，label 严格 A–D，文本互异）与 `answer`（字母；多选写「AB」这种组合）。
- `experiment`/`calc` 必须带 `scoreRule`（字符串数组，逐条写「… 3 分」），**各条分值之和＝该题分**。
- `sections[].title` 必须逐字写成「一、单项选择题（每小题 3 分，共 30 分）」这种带分值的形态。

## 覆盖（硬指标）
- **章卷**：`topicIds` 并集必须覆盖该章**全部课时点**（spec `must_cover` 里的 `phk_j*`）。
- 期中/期末：`must_cover` 里每个章点至少 1 题、课时点覆盖 ≥80%。

## 质量
- 题干 ≥12 汉字、解析 ≥25 汉字；与 `data/physics-hkjy/questions.json` 题干相似度 **<0.85**（原创，换情境换数据）。
- 数值自算一遍；g 取 10 m/s²、π 取 3.14（题干注明）；结论、单位、有效数字写清。
- 禁 Markdown（`**`、`##`、`$`、表格竖线）。
- 单选答案位 A–D 各 ≥15%。

## 自检（每卷必跑）
```bash
python3 scripts/check_phys_hkjy_exam.py "<你的卷路径>"     # 末行必须 RESULT: PASS
```
只写 `out` 指定的两份卷；⛔ 不改题库、topics、别人卷、技能库。
