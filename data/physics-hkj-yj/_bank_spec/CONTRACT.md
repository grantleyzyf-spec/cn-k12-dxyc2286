# 沪科技粤教版初中物理 题库合同（按章分片，逐字照做）

## 任务
读本目录给你的分片 `B<NN>.json`，为其中**每一个知识点**写指定题量的诊断题，
落盘成对象形状 `{"shard": "<片号>", "bucket": "physics-hkj-yj", "questions": [ … ]}` 到分片里的 `out` 路径。

## 题量（硬指标，多一道少一道都判不合格）
- `level=unit`（章上位点）：**恰好 5 题**
- `level=lesson`（节）：**恰好 8 题**

## 题型与难度（硬指标）
- choice ≥3（5 题片 ≥2）、fill ≥2（5 题片 ≥1）、short-answer ≥1、numeric **最多 1**
- 三档 `basic / standard / hard` **每个点各 ≥1 道**
- 选择题 4 个选项、`choices` 与 `options` 逐字同构、`answer` 是 A/B/C/D
- 填空题 `answer` 用文字，题干必须有 `____`
- numeric 必须带 `verify`：纯算术表达式（只许数字与 + - * / ( ) **），`eval(verify)` 必须等于 `answer`；
  ⛔ 不许 `int()`、`round()`、单位、文字
- short-answer 的 `answer` 用「；」分 2–3 条要点

## 字段（键名逐字照抄，不许增删）
```json
{
  "id": "<片里 id_range 给的那个>",
  "topicId": "<片里给的 topicId>",
  "subject": "physics-hkj-yj",
  "type": "choice|fill|short-answer|numeric",
  "difficulty": "basic|standard|hard",
  "prompt": "题干（≥12 字；选择题结尾写（　））",
  "options": [{"label": "A", "text": "…"}, …],
  "choices": [{"label": "A", "text": "…"}, …],
  "answer": "B 或文字答案",
  "explanation": "解析（≥25 汉字，说明依据，结尾写「故选 X」或给出答案来源）",
  "verify": "仅 numeric 题写，纯算式"
}
```
非选择题 `options`/`choices` 写 `[]`。

## 物理学科要求
- 只考**本知识点**：照 `chapter` 与 `description` 的范围出题，⛔ 不提前考后面章节。
- 公式、单位、符号写规范：密度 ρ=m/V、压强 p=F/S、欧姆定律 I=U/R、电功率 P=UI、浮力 F浮=ρ液gV排；
  单位用国际单位（kg、m、s、N、Pa、J、W、V、A、Ω），数值与单位之间空一格。
- 计算题数据要能在题干内复算，`verify` 与 `answer` 必须一致（保留一位小数时用四舍五入后的值作 answer）。
- 实验题围绕教材本节的探究活动（如用刻度尺测长度、探究凸透镜成像、伏安法测电阻），写清器材、步骤、结论。
- 干扰项要像真的错的（常见错因、混淆概念），⛔ 禁「以上都不对」「无法确定」「仅在大学学习」。
- 禁 Markdown（**、##、表格竖线）。

## 自检（必须跑，末行贴进汇报）
```bash
python3 scripts/check_chem_editions_bank.py --shard <你的 out 路径>
```
必须看到 `RESULT: PASS`。⛔ 不要改 checker。

## 落盘纪律
- 只写自己的 `out` 路径；⛔ 不动 `topics.json`、`questions.json`、别人的分片、技能库。
- 汇报里写：点数、题数、题型分布、三档分布、自检末行。
