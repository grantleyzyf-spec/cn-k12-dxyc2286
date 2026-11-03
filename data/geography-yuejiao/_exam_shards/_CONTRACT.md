# 粤教粤人版初中地理 · 单元/期中/期末试卷分片合同（GYJ_E01–E19）

## 0. 任务

一片 2 卷（同册，不跨片）。只写自己那两卷，不碰别的分片、不改仓库其他文件、不跑 git。

- 分片规格（只读）：`data/geography-yuejiao/_exam_shards/GYJ_Enn.json`
- 诊断题库（只读，用于避免撞题）：`data/geography-yuejiao/questions.json`
- 落盘：`data/geography-yuejiao/exams/<book>/<paper>.json`（`book`、`paper` 见规格里每卷字段）

## 1. 卷面结构（初中，**不得改**）

- `duration`: 120（分钟）；`fullScore`: 120
- `stage`: "初中"；`grade`: 7 或 8；`term`: "上"/"下"；`kind`: `unit` / `mid` / `fin`
- `sections` 两段：

```json
{"title": "一、选择题（每小题 3 分，共 54 分）", "rule": "每小题 3 分，共 54 分",
 "items": [ …18 道 choice，每题 score=3 … ]}
{"title": "二、综合题（每小题 11 分，共 66 分）", "rule": "每小题 11 分，共 66 分",
 "items": [ …6 道 short，每题 score=11 … ]}
```

合计 24 题 120 分；题号 `no` 全卷连续 1…24（选择题 1–18，综合题 19–24）。

## 2. 单题字段

| 字段 | 要求 |
|---|---|
| `no` | 连续题号 |
| `type` | `choice` 或 `short` |
| `stem` | 题干，≥12 字；读图题要写清「读某地……图」 |
| `options` | choice 必填，4 项 `[{"label":"A","text":"…"},…]`，文本互异；short 不填或空数组 |
| `answer` | choice 填 `"A"`–`"D"`；short 填参考答案（分点作答，句末用「；」） |
| `analysis` | 解析，≥20 汉字，说清对错原因 |
| `score` | choice 3；short 11 |
| `scoreRule` | **仅 short**：分步给分数组，如 `["写出位置 3 分", "说明成因 5 分", "归纳影响 3 分"]`，各步分值之和必须 = 11 |
| `topicIds` | 本题考查的知识点 id 数组，**必须取自本卷 `points[]` 里出现的 id** |

## 3. 覆盖与原创

- **单元卷**：`topicIds` 的并集必须覆盖本单元**全部 9 个点**（1 个单元点 + 8 个课时点）各 ≥1 次。
- **期中/期末卷**：覆盖 scope 内全部单元，每单元至少 2 个点；期末卷要覆盖全册。
- **原创性**：题干与 `questions.json` 里任何一道题的相似度必须 <0.85 —— 不要照抄题库题干，换情境、换数据、换问法。
- **答案位**：18 道选择题的 A/B/C/D 各 ≥15%（每个字母至少 3 道）。
- 禁用「以上都不对 / 以上都对 / 以上都可以」凑数项。

## 4. 卷名与 scope

- `paper` = 文件名（不含 `.json`）。
  - 单元卷：`第N单元 <单元名> 测试卷`（与规格 `paper` 逐字一致）
  - 期中/期末：`期中测试卷A` / `期中测试卷B` / `期末测试卷A` / `期末测试卷B`
- `scope` = 规格里给的数组，逐字照抄（单元卷是 1 个元素，期中/期末是多个）。

## 5. 自检（必须跑到 PASS）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/check_geo_yuejiao_exam.py data/geography-yuejiao/exams/七年级上册/"第N单元 XXX 测试卷.json"
```

末行 `✅ PASSED`。报红就地改自己这两卷（补覆盖点、改 scoreRule 分值、替换撞题题干），改完再跑，直到两卷都 PASS。
回报：分片号、两卷卷名、题数、分值合计、覆盖点数、PASS。
