# 化学版本桶「试卷」合同（一卷一片）

## 你的任务
读本目录给你的分片 JSON（`<examId>.json`），按其中 `sections` 的结构与分值写**一整份试卷**，
写成对象形状落盘到片内 `out` 路径。

## 卷面结构（逐字照分片的 sections，不许增删题目数、不许改分值）
- 分片里每个 section 给了 `title` / `type` / `count` / `score_each` / `score_total`，
  成品里写成 `{"title": "...", "rule": "每小题 X 分，共 Y 分", "type": "...", "items": [...]}`。
- `items[].no` 从 1 连续编号；`items[].itemId` = `<examId>_qNN`（两位，父代已给范围）。
- 每题必须带 `topicIds`（数组，取自分片 `points` 里的 topicId，1–2 个），`score`、`stem`、`answer`、`analysis`。
- 选择题另带 `options`（A/B/C/D 四项）；`answer` 是字母。多选题 `answer` 用「AB」这种多字母组合。
- 实验探究 / 综合计算题：`answer` 给结论与关键数值，`analysis` 写清步骤，`scoreRule` 可选（写了就必须各步之和＝题分）。

## 覆盖（硬指标）
- 单元卷：本单元**每个课时点至少被 1 道题引用**（`topicIds` 并集 ⊇ 该单元全部 lesson 点）。
- 期中卷：覆盖分片 `scope` 里的单元（每单元 ≥2 题）。
- 期末卷：覆盖全册（每单元 ≥2 题）。

## 原创性
- ⛔ 不许照抄题库题干：与 `questions.json` 里任何题干的相似度必须 < 0.85，同一点换情境、换数据、换设问。

## 字段（逐字照键名）
```json
{
  "examId": "...", "kind": "unit|mid|fin", "paper": "...", "book": "...",
  "stage": "初中|高中", "term": "上|下", "grade": 9或10-12,
  "duration": 120, "fullScore": 120,
  "scope": ["<单元 chapter 串>", ...],
  "sections": [
    {"title": "一、选择题", "rule": "每小题 3 分，共 36 分", "type": "choice",
     "items": [{"no": 1, "itemId": "<examId>_q01", "type": "choice", "difficulty": "basic",
                "topicIds": ["clj_j001"], "score": 3,
                "stem": "题干（≥12 字，选择题结尾（　））",
                "options": [{"label":"A","text":"…"}, …],
                "answer": "B",
                "analysis": "解析（≥25 汉字，说明为什么，结尾「故选 B」）"}]}
  ]
}
```

## 自检（写完必须跑，输出贴进汇报）
```bash
python3 scripts/check_chem_editions_exam.py --exam <你的 out 路径>
```
必须 `RESULT: PASS`。⛔ 不许改 checker。

## 落盘
只写片内 `out`；⛔ 不动 topics.json / questions.json / 别人的卷 / 技能库。
