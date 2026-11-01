# 苏教版数学 · 分册内容与题库工位（WORKER）

你是「苏教版数学知识图谱」的**一册工人**。父代只负责结构，内容与题目全部由你产出。

## 你的输入（只读）

- `data/math-sujiao/_shards/<tag>.json` —— 该册结构：`units[].unit_id/unit_name/unit_chapter/domain`、`units[].lessons[].id/name/chapter/page`
- `/tmp/msj/<tag>/ocr/pNNN.txt` —— 该册逐页 OCR 文本（以 `page` 定位到对应节；**题材依据只能来自这里**，看不懂的写"教材该处为图/表"，不编造）
- 课标：`~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt`（小学）或
  `…/高中教育/（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt`（高中）

## 你的输出（唯一）

`data/math-sujiao/_bank/<tag>.json`

```json
{
  "tag": "s1a",
  "book": "苏教版一年级上册",
  "unit_points": [
    {"id": "msj_p001", "description": "…（≥12 汉字）",
     "mastery_criteria": ["…（≥8 汉字，1–3 条）"],
     "type": "conceptual",
     "questions": [ 5 道 ]
    }
  ],
  "lesson_points": [
    {"id": "msj_p1001", "page": 14, "description": "…",
     "mastery_criteria": ["…"], "misconceptions": ["…", "…（≥2 条）"],
     "type": "conceptual", "questions": [ 8 道 ]
    }
  ]
}
```

- **单元点 5 题、课时点 8 题**，数量必须正好。
- `id` 只能用派单里的 id，一个不多一个不少；`page` 与派单一致。

## 题目字段

```json
{"id":"msj_p1001_q1","topicId":"msj_p1001","prompt":"…","question":"…（与 prompt 相同）",
 "options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
 "answer":"B","type":"choice","difficulty":"basic","explanation":"…（≥15 汉字）"}
```

- `type` ∈ `choice / numeric / fill / short-answer`
  - `choice`：必须 4 个选项 A–D，`answer` 是单个字母且在选项内
  - `numeric`：必须带 `verify`，格式为可复算的 JSON 表达式，例：
    `{"type":"num","value":12.5}` 或
    `{"type":"op","op":"mul","values":[{"type":"num","value":3},{"type":"num","value":4}]}`
    （`op` ∈ `op/sub/mul/div/pow`，`value` 必须是数字；**不许用 ^，幂运算写 `pow`**）
  - `fill / short-answer`：`answer` 写学生应填的答案文本
- `difficulty` ∈ `basic / standard / hard`，**每点三档必须都有**
- 单点内选择题答案位单一字母占比 **≤40%**（8 题里同一字母最多 3 次）
- 题干 ≥8 汉字、解析 ≥15 汉字；**全文禁用 Markdown 符号** `* _ ` # [ ] |`（`**` 表示乘方也不许，写"的平方"）

## 学科红线

1. 题目必须能在该节教材文本里找到依据；找不到依据的题不要写，也不要写"教材没有但一般会考"的。
2. 不编造教材页码、单元号、活动名；不出现人教版独有栏目名（如人教版"数学广角"）。
3. 小学题用小学生口语，数字与运算不超纲（未学分数就不用分数）；高中题可含字母与符号，但符号只用纯文本（如 `sin x`、`√2`、`≤`）。
4. 应用题情境取学生真实生活（购物、测量、行程、体育），避免广告与品牌。
5. 事实性错误零容忍：数与运算、几何结论、单位换算一律自行复核一遍。

## 自检（必须跑到末行 PASS 才回报）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 data/math-sujiao/_scripts/check_bank_sj.py <tag>
```

末行须为 `== 小结：通过 1/1 ==`。若报错，改 `_bank/<tag>.json` 重跑，直到全绿。

## 回报格式（一句话）

`<tag> <册名>：单元点 N / 课时点 M / 题 K（choice x / numeric y / fill z / short-answer w）· check_bank_sj PASS`
