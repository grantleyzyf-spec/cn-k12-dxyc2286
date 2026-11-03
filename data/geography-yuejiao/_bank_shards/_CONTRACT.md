# 粤教粤人版初中地理 · 诊断题库分片合同（GYJ_B01–B19）

## 0. 你的任务

为**一个单元**写 9 个知识点的正文 + 69 道诊断题。只写自己那一片，绝不碰别的分片、绝不改仓库其他文件、绝不跑 git。

- 分片规格（**只读**）：`data/geography-yuejiao/_bank_shards/GYJ_Bnn.json`
- 教材原文摘录（**只读**）：`data/geography-yuejiao/_src/GYJ_Bnn.txt`
- 落盘（**只写这一个文件**）：`data/geography-yuejiao/_bank/GYJ_Bnn.json`

## 1. 输出形状

```json
{
  "shard": "GYJ_B01",
  "subject": "geography-yuejiao",
  "book": "七年级上册",
  "chapter": "七年级上册 第一单元 地理工具与地理实践",
  "items": [
    {"topicId":"gyj_p001","name":"地理工具与地理实践","level":"unit",
     "description":"……","mastery_criteria":["……","……"],
     "diagnostic_question":{"question":"……","answer":""}}
  ],
  "questions": [ … 69 道 … ]
}
```

`items` 必须**恰好覆盖规格里 `items[]` 的 9 个 topicId**，顺序一致，`name` 与规格逐字相同。

- `description`：40–90 汉字，写这一课/这一单元**实际学什么**（具体到地理概念、读图技能、区域案例），不要写「理解……的核心内容」这类空话。
- `mastery_criteria`：2 条，各 15–35 字，可观察可检测（「能说出……」「能在图上指出……」「能比较……的差异」）。
- `diagnostic_question`：一道入门口试题干 + `"answer": ""` 留空。

## 2. 题目槽位（规格里 `items[].slots` 已固定，**不得增删改**）

- 课时点 8 题：`q01` choice/basic、`q02` choice/basic、`q03` choice/standard、`q04` choice/standard、
  `q05` fill/basic、`q06` fill/standard、`q07` short-answer/hard、`q08` numeric/standard
- 单元点 5 题：`q01` choice/basic、`q02` choice/standard、`q03` fill/basic、`q04` numeric/standard、`q05` short-answer/hard

题 `id` 一律 `{topicId}_{qNN}`，逐字照抄规格，**不得自己编号**。

## 3. 每道题必填字段

| 字段 | 要求 |
|---|---|
| `id` | 照抄槽位 | 
| `topicId` | 照抄槽位 |
| `prompt` | 题干，≥12 字，完整问句 |
| `question` | 与 `prompt` **完全相同** |
| `type` | 照抄槽位（choice / fill / numeric / short-answer） |
| `difficulty` | 照抄槽位（basic / standard / hard） |
| `options` | 选择题 4 项 `[{"label":"A","text":"…"},…]`；非选择题为 `[]` |
| `choices` | 选择题**与 options 完全相同**；非选择题 `[]` |
| `answer` | 选择题为 `"A"`–`"D"`；填空为词或短语；数值题为**纯数字**；简答为 2–3 条用「；」分隔 |
| `explanation` | 解析，≥25 汉字，说清为什么对、错项错在哪 |
| `verify` | **仅 numeric 题**：纯算术表达式，复算结果必须等于 `answer` |

### 硬性判据（checker 逐条查）

1. 选择题：4 项、label 顺序 A–D、选项文本互不相同、`answer` 在 A–D 内、`choices == options`；
   **禁用**「以上都不对 / 以上都对 / 以上都可以 / 无法确定」这类凑数项。
2. 填空：题干必须含 `____`（四个下划线）。
3. 数值：`answer` 是数字字符串，`verify` **只能含数字与 `+ - * / ** ( )` 和空格**，
   例：比例尺 1:50000 图上 3 厘米 → 实地 `3*50000/100000` = 1.5 千米，`answer: "1.5"`。
   ⛔ 不许出现 `int(...)`、`round(...)`、`√`、单位汉字。
4. 简答：`answer` ≥15 汉字，且含「；」分 2–3 条要点。
5. 题干 ≥12 字；`explanation` ≥25 汉字。
6. 片内题干不得重复（19 道选择题不要都写「下列关于……的说法正确的是」）。
7. 选择题答案位 A/B/C/D **各占 ≥15%**（19 道选择题里每个字母至少 3 道）。
8. 禁 Markdown（`**`、`##`、`|`）；禁套话（首先、其次、综上所述、总而言之、由此可见、赋能、抓手、闭环、值得注意的是）。

## 4. 内容质量

- **以教材摘录为准**：地名、数据、气候类型、地形区、河流特征、资源分布必须与摘录一致；摘录没写的常识性地理事实可以用，但不得编造具体数字与年份。
- **地理味**：题干尽量挂图、挂案例、挂区域（「读某地气温曲线和降水量柱状图……」「结合珠江三角洲的区位条件……」），不要写成政治或语文题。
- 覆盖该点的主干：概念 → 分布/规律 → 成因 → 影响/应用，四类题各有落点。
- 数值题要落在真实地理计算上：比例尺换算、相对高度、气温垂直递减（每升 100 米降 0.6℃）、人口密度、人口自然增长率、年较差、地方时/时区差。

## 5. 自检（必须跑到 PASS 才算交）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/check_geo_yuejiao_bank.py data/geography-yuejiao/_bank/GYJ_Bnn.json
```

末行必须是 `RESULT: PASS`。报红就**就地改自己这一片**（不要重写别的分片），改完再跑，直到 PASS。
最后回报：分片号、题数、`RESULT: PASS`、以及 items 里 9 个 topicId。
