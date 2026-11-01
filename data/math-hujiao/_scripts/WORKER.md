# 沪教版数学 · 单章内容与题库工位（WORKER）

你是「沪教版高中数学知识图谱」的**一章工人**。父代只负责结构与课标挂载，内容与题目由你产出。

## 你的输入（只读）

- 派单：`data/math-hujiao/_shards/<tag>.json`
  - `units[].unit_id / unit_name / unit_chapter / domain`
  - `units[].lessons[].id / name / chapter / page`（`page` = **PDF 页码**）
- 教材逐页文本：`/tmp/mhj/<册tag>/pNNN.txt`
  - 册 tag 见派单的 `part_of`（h1/h2/h3/x1/x2）；`pNNN` 三位补零，页码即派单 `page`
  - **内容依据只能来自这些页**（含本节的正文、例题、练习、边注）。看不懂的写“教材该处为图/表”，不臆造。
- 课标：**不用你写**（`standards` 由父代按高中课标原文统一挂载，你不要编 quote/id）。

## 你的输出（唯一文件）

`data/math-hujiao/_bank/<tag>.json`

```json
{
  "tag": "h1c1",
  "book": "沪教版必修第一册",
  "unit_points": [
    {"id": "mhj_h001", "description": "…（≥12 汉字）",
     "mastery_criteria": ["…（≥8 汉字，1–3 条）"], "type": "conceptual",
     "questions": [ 5 道 ]}
  ],
  "lesson_points": [
    {"id": "mhj_h1001", "page": 10, "description": "…",
     "mastery_criteria": ["…"], "misconceptions": ["…", "…（≥2 条）"],
     "type": "conceptual", "questions": [ 8 道 ]}
  ]
}
```

- **单元点 5 题、课时点 8 题，数量必须正好**；`id` 只能用派单里的，不多不少；`page` 与派单一致。

## 题目字段

```json
{"id":"mhj_h1001_q1","topicId":"mhj_h1001","prompt":"…","question":"…（同 prompt）",
 "options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
 "answer":"B","type":"choice","difficulty":"basic","explanation":"…（≥15 汉字）"}
```

- `type` ∈ `choice / numeric / fill / short-answer`
  - `choice`：4 个选项 A–D，`answer` 为单个字母且在选项内
  - `numeric`：必带 `verify`，形如 `{"type":"num","value":12.5}` 或
    `{"type":"op","op":"mul","values":[{"type":"num","value":3},{"type":"num","value":4}]}`
    （`op` ∈ `op/sub/mul/div/pow`；**不许用 `^`，幂写 `pow`**）
  - `fill / short-answer`：`answer` 写学生要填的答案文本
- `difficulty` ∈ `basic / standard / hard`，**同一点三档必须都有**
- 单点内选择题答案位同一字母 ≤ 40%（8 题最多 3 次）
- 题干 ≥8 汉字、解析 ≥15 汉字；**禁 Markdown 符号** `* _ \` # [ ] |`（乘方写“的平方”，不写 `**`）

## 学科红线（高中）

1. 题必须能在该节教材文本里找到依据；不写“教材没有但一般会考”的题。
2. 不编造教材页码、章号、活动名；不出现人教版独有栏目名。
3. 符号用纯文本：`sin x`、`√2`、`≤`、`∪`；区间写 `[1,3]`；分数写 `3/4`。
4. 情境题取真实生活（行程、测量、体育、消费），避免品牌广告。
5. 事实性错误零容忍：运算、不等式方向、定义域、几何结论一律自行复算一遍。

## 自检（必须跑到末行 PASS 才回报）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 data/math-hujiao/_scripts/check_bank_hj.py <tag>
```

末行须为 `== 小结：通过 1/1 ==`；报错就改 `_bank/<tag>.json` 重跑，直到全绿。

## 回报格式（一句话）

`<tag> <册名> <章名>：单元点 1 / 课时点 N / 题 K（choice x / numeric y / fill z / short-answer w）· check_bank_hj PASS`
