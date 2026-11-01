# 心理健康知识图谱 · 分片写手契约（WORKER）

你在为 `cn-k12-dxyc2286` 仓库补「心理健康（北师大版）」的知识点内容与诊断题库。
**只写自己那一份分片**，绝不改共享文件（`topics.json` / `questions.json` / `_skeleton.json` / `_deps.json`）。

## 0 你的三道输入

1. 派单：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/mental-health/_shards/<Sxxx>.json`
   —— 内含本册的 `units[]`，每个单元有 `unit_id`、`unit_name`、`domain`、`standards_id`、`quote`，
   以及 `lessons[]`（每条有 `id`/`no`/`name`）。
2. 本契约（本文件）。
3. 课标口径：`domain` 五选一——**自我意识 / 情绪管理 / 人际交往 / 学会学习 / 生命与社会适应**。
   高中年级的写法：内容要更深入（自我同一性、生涯规划、心理危机识别与求助），小学低年级要浅白（活动、游戏、图画表达）。

## 1 唯一输出文件

`/Users/a627692/Desktop/cn-k12-dxyc2286/data/mental-health/_bank/<Sxxx>.json`

```json
{
  "shard": "S01",
  "topics": [
    {"id": "mhe_p001", "description": "…60–120 字…",
     "mastery_criteria": ["…≤50 字，可观测…", "…"],
     "diagnostic_question": {"question": "…≤30 字…", "answer": "…内容词，不给字母…"},
     "tags": ["整理与收纳", "习惯养成"]}
  ],
  "questions": [
    {"id": "mhe_q0001", "topicId": "mhe_p002", "prompt": "…≥12 字…", "question": "同 prompt",
     "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
     "answer": "B", "type": "choice", "difficulty": "basic",
     "explanation": "…≥15 字，说清为什么对/为什么错…"}
  ]
}
```

- `topics[]` 必须**逐一覆盖**派单里的每个 `unit_id` 与每个 `lessons[].id`，不得增、不得漏、不得改 id。
- 题目：**单元点 5 题 / 课时点 8 题**；`topicId` 用骨架里的 id。
- 题目 id 自编号，规则 `mhe_q####`，**在你这份分片内从 0001 起连续编号**，并在题号前加你的分片号避免撞车：
  用 `mhe_q{分片序号2位}{流水4位}`，例如 S01 → `mhe_q010001`。

## 2 硬规则（会被脚本机器检查）

1. `choice` 必须恰好 4 个选项，`answer` 是选项 label（A/B/C/D），且正确项文本确实正确。
   正确项位置要分散（A/B/C/D 大致均匀），不许一半题都是 B。
2. `fill` / `short-answer` **不带 options**；`answer` 为文字答案。
3. `difficulty` 只能是 `basic` / `standard` / `hard`，三档都要出现。
4. `prompt` ≥12 字；`question` 与 `prompt` 同值；`explanation` ≥15 字。
5. 禁 Markdown 符号（`**`、`#`、`_`、`` ` ``）；引号用中文「」或“”。
6. 内容红线：
   - 用课标五素养词汇，**不得出现其他学科素养名**（如「唯物史观」「计算思维」「技术意识」「运动能力」）。
   - **不做医学诊断**：不写「你有××症」「诊断为抑郁」这类表述；涉及严重困扰时写「应当向心理老师或专业机构求助」。
   - 不写空泛口号（「让我们都成为阳光少年」这类），每题都要能落到具体做法或具体情境。
   - 情境题用学生真实生活（课堂、家庭、同伴、考试、手机）。
7. 每道题必须与所属知识点（课名）**内容相关**，不能跨课张冠李戴。

## 3 交付前自检（必须跑，把末行贴进汇报）

```bash
python3 /Users/a627692/Desktop/cn-k12-dxyc2286/data/mental-health/_shards/check_bank.py S01
```

末行必须是 `PASS`；不 PASS 就改到 PASS 再汇报。

## 4 汇报格式（≤6 行）

```
S01 一年级上册：单元 3 + 课时 18 = 21 点；题 159 道（choice 120 / fill 25 / short 14）
难度 basic 60 / standard 70 / hard 29；答案分布 A40 B40 C40 D39
check_bank.py → PASS
```
