# 心理健康 · 单元素养测评卷 写手契约（WORKER_EXAM）

为北师大版心理健康某一册出**一份**「全册素养测评卷」的 JSON（不写 docx，不碰共享文件）。

## 0 输入

- 派单：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/mental-health/exams/_shards/<Exx>.json`
  内含该册的 `book`/`label`/`grade`/`semester`/`units[]`（单元名、素养、该单元各课时点名与 `id`）。
- 题库参考（**禁抄**）：`data/mental-health/questions.json` 里本册的题，卷题与题库任一条
  归一化后相似度必须 < 0.85（会机器检查）。

## 1 唯一输出

`/Users/a627692/Desktop/cn-k12-dxyc2286/data/mental-health/exams/_bank/<Exx>.json`

```json
{
  "shard": "E01", "book": "一年级上册", "title": "一年级上册 心理健康素养测评卷",
  "duration": 40, "fullScore": 100,
  "sections": [
    {"name": "一、选择题（每题 4 分，共 48 分）", "type": "choice", "items": [
      {"no": 1, "unit": "第一单元 我是小学生啦", "topicId": "mhe_p002", "stem": "…",
       "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
       "answer": "B", "score": 4, "explain": "…"},
      …
    ]},
    {"name": "二、情境判断（每题 4 分，共 16 分）", "type": "judge", "items": [
      {"no": 13, "unit": "…", "topicId": "mhe_p005", "stem": "…", "answer": "√ 或 ×",
       "score": 4, "explain": "…"}
    ]},
    {"name": "三、简答与应用（每题 9 分，共 36 分）", "type": "short", "items": [
      {"no": 17, "unit": "…", "topicId": "mhe_p010", "stem": "…", "score": 9,
       "answer": "参考答案 60–120 字", "rubric": ["要点1（3 分）", "要点2（3 分）", "要点3（3 分）"]}
    ]}
  ],
  "blueprint": [{"no": 1, "unit": "…", "domain": "自我意识", "level": "识记/理解/应用", "score": 4}],
  "coverage": {"units": 3, "covered": 3}
}
```

## 2 硬规则（机器检查）

1. **20 题**：choice 12（4 分）＋ judge 4（4 分）＋ short 4（9 分）＝ 100 分；`duration` 40 分钟。
2. **每个单元至少 4 题**（本册 3 单元则 12 题起；10 单元册则每单元至少 2 题），`coverage.covered` = 实际覆盖单元数。
3. 每题必带 `topicId`（取自派单里的课时点 id）、`unit`（单元名）、`explain`（≥15 字）。
4. choice 必须 4 个选项、答案 label 在 A–D；judge 答案只能是 `√` 或 `×`；short 必须给 `rubric`（3 个要点、分值合计 = 该题分）。
5. `blueprint` 逐题一行，`score` 合计 = 100。
6. 内容红线：只出现五素养名（自我意识／情绪管理／人际交往／学会学习／生命与社会适应）；**不作医学诊断**；不写空泛口号；情境取自学生真实生活；难度贴合该册学段。
7. 与题库去重：卷题题干不得与题库同册题高度相似（< 0.85）。

## 3 交付前自检（必须跑，贴末行）

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/data/mental-health/exams/_shards/check_exam.py E01
```

末行必须 `PASS`。

## 4 汇报（≤5 行）

```
E01 一年级上册：20 题 / 100 分 / 40 分钟；覆盖 3 个单元
choice 12 · judge 4 · short 4；blueprint 合计 100
check_exam.py → PASS
```
