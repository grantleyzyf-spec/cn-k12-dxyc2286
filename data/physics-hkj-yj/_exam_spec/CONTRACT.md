# 沪科技粤教版初中物理 试卷合同（一卷一片）

## 任务
读分片 JSON，按 `sections` 的结构与分值写**一整份试卷**，落盘到片内 `out` 路径（对象形状，键名逐字照下）。

## 卷面结构（逐字照 sections，不许增删题数、不许改分值）
`{"examId","book","paper","kind","scope","fullScore","duration","sections":[{"title","rule","type","items":[…]}]}`

- `items[].no` 从 1 连续；`items[].itemId` = `<examId>_qNN`
- 每题必带 `topicIds`（数组，1–2 个，取自分片 `points`）、`score`、`stem`、`answer`、`analysis`
- 选择题带 `options`（A/B/C/D 四项），`answer` 是字母
- 实验探究 / 综合计算：`answer` 给结论与关键数值，`analysis` 写步骤；`scoreRule` 可选，写了各步之和必须＝题分

## 覆盖（硬指标）
- 单元卷：本单元**每个课时点至少被 1 题引用**
- 期中/期末：scope 内每章 ≥2 题、课时点覆盖 ≥80%

## 原创性（硬指标）
- ⛔ 不抄题库题干：同一考点换情境、换数据、换问法，选择题四项也重写；与题库相似度 <0.85
- `analysis` ≥30 汉字；`stem` ≥12 汉字；答案与解析里的数值必须自洽

## 物理卷要求
- 数值题必须有单位、数据能在题干内复算；实验题写器材、步骤、现象与结论
- 公式规范（ρ=m/V、p=F/S、I=U/R、P=UI、Q=cmΔt、F浮=ρ液gV排）
- 禁 Markdown（**、##、表格竖线）

## 自检（必须跑，末行贴进汇报）
```bash
python3 scripts/check_chem_editions_exam.py --exam <你的 out 路径>
```
必须 `RESULT: PASS`。⛔ 不改 checker。

## 落盘纪律
只写自己的 `out`；⛔ 不动 topics/questions/别人的卷/技能库。
