# physics-bsd-lcm 试卷合同（北师大版·李春密·初中物理）

批次根：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/physics-bsd-lcm`

## 交付物
按卡片给你的作业单（`_exam_spec/PLCM_E##.json`，一张卡可能 2 份）逐份落盘：

```
…/data/physics-bsd-lcm/exams/<册>/<卷名>.json
```

卷 JSON 形状：

```json
{"book":"八年级全一册","stage":"初中","grade":8,"term":"全一册","kind":"unit",
 "paper":"第1章 热现象 测试卷","duration":120,"fullScore":120,
 "scope":["八年级全一册 第1章 热现象"],"examId":"plcm_8_u01","edition":"北师大版（李春密）",
 "sections":[{"title":"一、选择题（每小题 3 分，共36分）","rule":"共12题，36分",
   "items":[{"no":1,"type":"choice","score":3,"stem":"…","options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
             "answer":"B","analysis":"…≥60 汉字…","topicIds":["plcm_j001"]}]}]}
```

- `book/kind/paper/examId/scope/duration/fullScore/sections` 的题号与分值**逐项照作业单**，⛔ 不自行改动。
- `sections[].title` 与 `rule` 都要保留；`rule` 里的分值必须等于该段 `items[].score` 之和。
- 每题带 `no`（全卷 1–24 连续）、`type`、`score`、`stem`、`analysis`、`topicIds`。

## 题型与字段
| type | 要求 |
|---|---|
| `choice` | `options` 恰 4 项、label 必须依次 A/B/C/D、四项文本互异；`answer` ∈ A–D；禁「以上都不对/以上都对」 |
| `fill` | `answer` 非空字符串；题干里用 `____` |
| `solve`（实验探究/综合计算） | 必须有 `scoreRule`：**字符串数组**，每行含「N分」，各行分值之和 = 该题 `score` |

## 内容要求
- `stem` ≥12 字（写到 20–60 字更稳）；`analysis` ≥20 汉字（写到 60–120 汉字，含解题思路与「故选/答案为」）。
- `topicIds`：只能取作业单 `available_topicIds` 里的 id，一维字符串数组（⛔ 不许嵌套数组）。
- **单元卷**必须覆盖本单元**全部点各 ≥1 次**（`available_topicIds` 里每个 id 至少出现一次）；期中/期末按范围自由分布，但每个单元至少 1 题。
- **卷面必须原创**：与题库 `data/physics-bsd-lcm/questions.json` 的题干相似度要 <0.85 ⇒ ⛔ 不许照搬题库题干，同一考点换情境、换数据、换问法；选择题四个选项也要重写。
- 数值与常数用教材口径（g 取 10 N/kg），计算题给完整数据。
- 选择题答案位要分散：A/B/C/D 各 ≥15%（24 题里每档 ≥4 题）。
- 难度按学段正常分布（基础 5–6 成、中档 3 成、综合 1–2 成）。

## 自检（必须 PASS）
```
cd /Users/a627692/Desktop/cn-k12-dxyc2286
/usr/bin/python3 scripts/check_plcm_exam.py "<你写的卷文件绝对路径>"
```
末行须 `RESULT: PASS`（或该 checker 的成功提示）；红就改自己的卷重跑。

## 纪律
- 只写卡片上给你的那些卷文件；禁改 `_exam_spec`、题库、脚本、别人的卷。
- 禁 `search_files`；教材原文在 `_text/<册>/整册全文.txt`（grep 章名定位）。
- 回复报：每卷 卷名、题数、分值、覆盖点数、checker 末行。
