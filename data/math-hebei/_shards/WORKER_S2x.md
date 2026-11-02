# 冀教版数学 · 一年级上册补建 · 分片工位契约（S22 / S23 / S24）

> 父代已经做完的事：骨架补到 6 单元 / 43 课时（`data/math-hebei/_skeleton.json`，本片点位已含 `level`）、
> 派单落盘（`data/math-hebei/_shards/S2x.json`）、教材全文备好在 `textbook` 字段指向的路径。
> 你只做一件事：**把派单里那几个点写成「内容层 + 题库」分片**。

## 1 只许写这一个文件

```
/Users/a627692/Desktop/cn-k12-dxyc2286/data/math-hebei/_bank/<你的分片号>.json
```

⛔ 不要改 `topics.json` / `questions.json` / `dependencies.json` / `_skeleton.json` / `_shards/*`
⛔ 不要写 `data/math-hebei/learn/`、`exams/`、`exam_lectures/`（那些是别的工位）
⛔ 不要在自己分片里塞别的片的点；不要「顺手修」别人的数据

## 2 分片文件结构

```json
{
  "shard": "S22",
  "topics":    [ /* 每个派单点位一条，字段见 §3 */ ],
  "questions": [ /* 每点题量见 §4 */ ]
}
```

点位、`chapter`、`level`、`id` 一律**逐字照抄派单**（`_shards/S2x.json` 的 `points`），不许改名、不许改号。

## 3 内容层字段（每个点必须齐全）

| 字段 | 要求 |
| --- | --- |
| `id` | 照抄派单 |
| `description` | **≥100 汉字**（硬下限 40，但请按 100+ 写）：讲清这一点学什么、怎么理解、学完能做什么。低年级要写具体情境（数一数、摆一摆、比一比），不要空话 |
| `domain` | 四类之一：`数与代数` / `图形与几何` / `统计与概率` / `综合与实践` |
| `type` | **仓库枚举只有这五个**：`conceptual`（概念）/ `procedural`（技能）/ `reasoning`（推理）/ `modeling`（建模）/ `application`（应用）。⛔ 不要写 `representational`（不在枚举里，会红「type 枚举」） |
| `mastery_criteria` | **2–3 条**，每条是一个可观察的「能做什么」 |
| `misconceptions` | **≥2 条**，写学生真实会犯的错（一年级：把第几当成几个、加减混淆、数数漏数、把 0 当成没有数等） |
| `standards` | **≥1 条**，每条 `{"id","confidence":"exact","quote"}`。`id` 与 `quote` **必须从派单的 `standards_catalog` 里逐字复制**，`quote` 一个字都不许改。选与本点最贴的条目（数概念 / 加减运算 / 图形认识 / 分类 等） |
| `diagnostic_question` | `{"question": "...", "answer": "..."}`，一道口头能答的诊断题，答案写清依据 |
| `tags` | 2–6 个关键词 |

## 4 题库（每点题量恰好）

- `level == "unit"` → **恰好 5 题**
- `level == "lesson"` → **恰好 8 题**

字段（缺一不可）：

```json
{"id":"mhb_q22####","topicId":"mhb_p2xx","type":"choice","difficulty":"basic",
 "prompt":"…","answer":"B","explanation":"…",
 "options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}]}
```

- `id`：前缀取派单的 `idPrefix`，后接 4 位序号，**从 `0001` 起连续**，不得跳号、不得与本片其他题重号
- `type`：`choice` / `fill` / `numeric`（比例约 60% / 20% / 20%）
- `difficulty`：`basic` / `standard` / `hard`（比例约 55% / 33% / 12%）
- `prompt` **≥12 字符**（一年级算式题请加情境句，如「算一算，得数是多少？」）
- `explanation` **≥20 字符**，写清怎么算出来的，并点出易错处
- `answer` 一律**字符串**（数值题也写 `"7"` 不是 `7`）
- `choice` 题：`options` **恰好 4 个**，`label` 为 A/B/C/D，选项文本互不相同，`answer` 必须是其中一个 `label`；
  正确答案的**位置要打散**（一片内 A/B/C/D 各占约 1/4，任何一位不超过 60%）
- `fill` 题：题干里用 `____` 表示空格；`numeric` 题只填数
- 非选择题不要带 `options` 字段

## 5 内容纪律

- 一切以**教材原文**为准：`textbook` 字段是整册全文（逐页 `===== PAGE n =====` 分隔）。写题前先 `grep` 单元名/课时名定位，
  再顺读相邻页（一年级一课常跨 2–4 页）
- 课时名在教材里可能写作别的字样（如「认识1~5」在书上写作「认识 1～5」），**按单元名先定位再对号**
- 只写本册（一年级上册）内容，**不要**掺入下册/高年级知识（如 20 以内退位减法、乘法口诀）
- 不出需要纸笔作图才能完成的题；不出依赖课件的题
- 数字与符号用纯文本：`+` `-` `=` `>` `<`，不用图片、不用 LaTeX

## 6 自检（交付前必须跑，末行是全绿才算完）

```bash
cd /Users/a627692/Desktop/cn-k12-dxyc2286
/usr/bin/python3 scripts/check_math_hebei_bank.py data/math-hebei/_bank/<你的分片号>.json
```

末行形态：`✅ S22.json：点 14 · 题 109 · 不合格 0`。
出现 `❌` 就按提示逐条改（每条都会指出 id 与原因），改到 0 不合格再汇报。

## 7 汇报格式（一行，≤120 字）

`S22 | 点 14 · 题 109 | ✅ 不合格 0 | 最高单点题数 8 | 选择题答案位 A5/B5/C5/D4`
