# 沪科教版高中物理 · 题库＋点内容合同（一章一片，逐字照做）

## 你的任务
读 `data/physics-hkjy/_bank_spec/<TNN>.json`（含本章 `items[]`，每点带 `slots[]` 题槽），产出**两个文件**：

1. `data/physics-hkjy/_bank/<TNN>.json`
```json
{"shard": "TNN", "bucket": "physics-hkjy", "questions": [ … ]}
```
- 题量、`id`、`type`、`difficulty` **逐槽照抄** `slots[]`，不多不少。
- 每题字段：`id` `topicId` `prompt` `question`（与 prompt 完全相同）`type` `difficulty` `answer` `explanation` `options` `choices`（`verify` 仅 numeric 需要）。
- `choice`：4 个选项，`options` = `[{"label":"A","text":"…"}, …]`，`choices` 与 `options` **逐字同构**；`answer` 必须等于该槽 `label`；四项互异，禁凑数项（「以上都不对」「无法确定」）。
- `fill`：题干含 `____`；`options=[]`、`choices=[]`；`answer` 为文字/数值串。
- `numeric`：`answer` 为数值字符串；`verify` 只能是纯算术表达式（数字与 `+ - * / ** ( )`），`eval(verify, {"__builtins__": {}}, {})` 必须等于 `answer`；⛔ 不许 `int()/round()`。
- `short-answer`：`answer` ≥15 汉字且用「；」分 2–3 条；`options=[]`。
- 题干 ≥12 汉字，解析 ≥25 汉字；禁 Markdown（`**`、`##`、`$`、表格竖线）；片内题干不得重复。

2. `data/physics-hkjy/_points/<TNN>.json`
```json
[{"topicId": "phk_j001", "description": "…", "mastery_criteria": ["能…", "能…"], "diagnostic_question": {"question": "…", "answer": "A"}}]
```
- 覆盖本片 `items[]` 的**每一个点**（章点＋节点，一个不漏）。
- `description` 60–110 汉字，写实体内容（点名本课概念/规律/公式/情境），⛔ 不写「本章围绕…组织」这类空话。
- `mastery_criteria` 2–3 条、每条 ≤40 字、以「能」开头。
- `diagnostic_question` 为 `{question, answer}`，answer 必须是字符串。

## 物理口径
- 一律用**本册教材公式与符号**；数值题给足已知量，取 g=10 m/s²（教材口径）并在解析里写明单位。
- 计算自己复算一遍；不引入教材外的常数。

## 自检（必跑）
```bash
python3 scripts/check_phys_hkjy_bank.py data/physics-hkjy/_bank/<TNN>.json     # 末行必须 RESULT: PASS
```
只写自己这两个路径；⛔ 不动其他分片、`topics.json`、`questions.json`、技能库。
