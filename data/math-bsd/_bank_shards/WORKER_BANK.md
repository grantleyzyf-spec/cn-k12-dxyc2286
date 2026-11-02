# 北师大版数学（math-bsd）· 题库写手工位合同 · WB

## 你的活

读派单 `data/math-bsd/_bank_shards/<片名>.json`（含 `book / unit_no / unit_name / topics[] / need`），
为其中**每个点**写 `need[点id]` 道题（一律 8 道），落到
`data/math-bsd/_bank_out/<片名>.json`：

```json
{"shard": "<片名>", "book": "一年级下册", "unit_no": "第一单元",
 "questions": [
   {"id": "mbs_q007001", "topicId": "mbs_p032", "prompt": "…", "question": "…",
    "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
    "answer": "B", "type": "choice", "difficulty": "basic", "explanation": "…"}
 ]}
```

⛔ 只写 `_bank_out/<片名>.json`。不改 `topics.json` / `questions.json` / 别人的分片。

## 题号先取号（防撞车）

本题库 id 形如 `mbs_q<三位片号><三位题号>`。**片号取你的片名在 `_bank_shards/` 里的排序号**（派单里给了 `id_prefix`），
例如 `id_prefix = "mbs_q042"` ⇒ 你的题号是 `mbs_q042001`…`mbs_q042040`（本片 5 点 × 8 题 = 40 题）。

## 硬性要求（父代 `check_bsd_bank.py` 机器校验，红一条即退回）

1. **每点 8 题**，不多不少；`topicId` 必须与派单 `topics[].id` 一一对应。
2. **题型**：`choice / fill / numeric / short-answer`；**每个点至少 3 种题型**；
   每点建议 choice 4 + fill 2 + numeric 1 + short-answer 1（或 choice 3 + fill 2 + numeric 2 + short 1）。
3. **choice**：4 个选项、`answer` 是 label、四项文本互不相同；**答案位不得偏置**（整片 A/B/C/D 每个 ≥15%）；
   选项里不许出现「以上都对/都不对」这类免做题。
4. **fill**：题干含 `____`；`answer` 为字符串。
5. **numeric**：`answer` 为字符串形式的数（如 `"12"`），另给 `verify`（可复算表达式，如 `"3*4"`）。
6. **short-answer**：`answer` 为参考答案，另给 `keypoints`（≥2 条判分点）。
7. `prompt`（题面）≥12 汉字，`explanation` ≥20 汉字且**说清为什么**，不许「由题意可得」了事。
8. 难度只用 `basic / standard / hard`，每点至少 1 道 `basic`、至多 2 道 `hard`。
9. 题干纯文本：不许 Markdown（`**`、`##`、`` ` ``）、不许 LaTeX（`$`、`\frac`）、不许竖线表格、
   不许「如图」类依赖插图的表述（几何条件必须文字写全）。
10. 同片内题干不得重复；不同点之间也不许同题换个数（相似度 ≥0.85 视为重复）。

## 学段口径（错了要整片返工）

- 一年级：只做 20 以内加减（下册可到 100 以内），不出乘除（下册末单元「乘法初步」除外）、不出小数分数。
- 二年级：100 以内加减、表内乘除（2–9）、角的初步与方向。
- 三年级：多位数乘一位/两位数、除法、分数初步、周长与面积、年月日、统计。
- 四年级：大数、三位数乘两位数、运算律、小数意义与加减、三角形与四边形、统计图。
- 五年级：小数乘除、简易方程、因数与倍数、分数意义与加减、长方体与正方体、可能性。
- 六年级：分数乘除、比与比例、圆、圆柱与圆锥、百分数、统计与概率初探。
- ⛔ 下册里未学的内容不许提前出（如三上不出两位数除法）。

## 自检（不跑不许交）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/check_bsd_bank.py --shard data/math-bsd/_bank_out/<片名>.json
```
末行必须是 `PASS`。红项逐条改到绿，不许改 checker、不许改派单。

## 汇报

一行：片名 / 点数 / 题数 / 题型分布（choice·fill·numeric·short）/ 答案位 A·B·C·D / 自检末行。
不要贴题目正文。
