# 北师大版（郭玉英）初中物理 · 题库分片合同

## 你要写什么
读本目录下的 `S001.json`（作业单），按其中 `items[]` 逐个知识点写题，落盘到：

    /Users/a627692/Desktop/cn-k12-dxyc2286/data/physics-bsd-gyy/_bank/S001_out.json

⛔ 只写这一个文件。其他桶（`physics`、`physics-bsd-lcm`、`physics-sk`、`physics-yj`）的同名分片禁止读写。

## 题量（恰好，不多不少）
- `level = "lesson"` 的点：**8 题**
- `level = "unit"` 的点：**5 题**
逐点核对，作业单里 `need` 字段已写明。

## 题型配额（逐点核）
8 题点：`choice ≥ 3`、`fill ≥ 2`、`short-answer ≥ 1`、`numeric ≤ 1`
5 题点：`choice ≥ 2`、`fill ≥ 1`、`short-answer ≥ 1`、`numeric ≤ 1`
`type` 只认：`choice` / `fill` / `short-answer` / `numeric`（写别的直接判红）。

## 难度（逐点核）
`basic` / `standard` / `hard` **每点各 ≥1**，`difficulty` 只认这三个值。

## 字段
```json
{
  "shard": "S001",
  "topics": [{"topicId": "pgy_j001", "type": "conceptual",
              "description": "40–90 汉字的实体描述（点名本节概念/规律/实验）",
              "mastery_criteria": ["…", "…"],
              "diagnostic_question": {"question": "…", "answer": "A"}}],
  "questions": [{
    "id": "pgy_q0001",
    "topicId": "pgy_j001",
    "prompt": "题干（≥12 字，完整问句）",
    "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},
                {"label":"C","text":"…"},{"label":"D","text":"…"}],
    "answer": "B",
    "type": "choice",
    "difficulty": "basic",
    "explanation": "解析（≥25 汉字，说清为什么，选择题要点明干扰项错在哪）"
  }]
}
```
- 选择题：`options` 恰好 4 项、文本互异、`answer` 必须是 A/B/C/D 之一。
- 填空/简答/数值题：`options` 写 `[]`；填空题干必须含 `____`；数值题 `answer` 只写数字，另带
  `verify`（**纯算术表达式**，门禁 `eval(verify, {"__builtins__":{}}, {})` 必须等于 answer；
  ⛔ 不许写 `int()`/`round()`/`sqrt()`，根号写 `**0.5`）。
- 简答题 `answer` 用「；」分 2–3 条。
- 物理符号：用 `×` `÷` `＋` `－` `＝`，单位用汉字或标准符号（`N`、`kg/m³`、`Ω`、`V`、`A`、`J`、`W`、`Pa`），
  不写 LaTeX、不写 `$…$`、不写 HTML。
- ⛔ 禁 Markdown：不加 `**`、`##`、表格竖线。
- ⛔ 禁凑数干扰项：「以上都不对」「无法确定」「仅在大学学习」一律不许。
- ⛔ 每点内不得出现两道题干雷同的题（换个数字也算雷同）；也不要抄作业单里 `description` 的原句当题干。

## 自检（落盘后必须跑，把最后一行贴进汇报）
```
python3 scripts/check_pgy_bank.py --shard /Users/a627692/Desktop/cn-k12-dxyc2286/data/physics-bsd-gyy/_bank/S001_out.json
```
最后一行必须是 `RESULT: PASS`。红了就地改，不要重派。
