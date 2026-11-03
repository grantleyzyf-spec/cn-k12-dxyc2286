# 中图版（钟作慈）地理知识图谱 —— 内容工位合同（T01–T18 同用）

你负责一个分片（TNN）。读本文件 + 你的 `_bank_spec/TNN.json` + 该章教材 docx，产出**两个 JSON 文件**。

## 0. 产物（绝对路径，写完即止）

| 产物 | 路径 | 形状 |
|---|---|---|
| 知识点内容 | `data/geography-zhongtu-cz/_points/TNN.json` | `{"shard":"TNN","points":[...]}` |
| 题库 | `data/geography-zhongtu-cz/_bank/TNN.json` | `{"shard":"TNN","questions":[...]}` |

⛔ 不改 spec、不改别的分片、不动 `topics.json`/`questions.json`。

## 1. `_points/TNN.json` —— 逐点内容

`points[]` 条数与 id 集合必须与 `_bank_spec/TNN.json` 的 `items[].topicId` **完全一致**（课时 8 点 + 单元 1 点＝9 点；T01 只有 2 点）。

每点字段：

```json
{
 "id": "gztu_j001",
 "name": "与 spec 的 items[].name 逐字一致",
 "type": "conceptual | procedural | reasoning | modeling | application",
 "description": "40–120 汉字：本点讲什么、学生要理解/会做什么，紧扣教材该课时内容",
 "mastery_criteria": ["2–3 条，每条 ≥8 汉字，互不重复，可观察可测"],
 "diagnostic_question": {"question": "≥10 字的一句话诊断问", "answer": "简短答案（可含选项字母）"},
 "tags": ["<本点 domain>", "<主题词>"]
}
```

- `tags[0]` **必须等于** spec 的 `domain`（地球与地图／世界地理／中国地理／乡土地理）。
- 单元点（`kind=unit`）的 description 写「本章统领：…」，mastery_criteria 写本章整体要求。
- 禁 Markdown（`**` `##` `|` `$` `\`）、禁元话语（扫描件/OCR/抽取/切片/文字层/残片/待补/TODO）。

## 2. `_bank/TNN.json` —— 逐槽出题

`questions[]` 的 id 集合必须与 spec `items[].slots[].id` **恰好相等**（不多不少），且每题的 `type`/`difficulty` 与槽位一致、`topicId` 等于该点。

```json
{
 "id": "gztu_j001_q01",
 "topicId": "gztu_j001",
 "prompt": "题干（与 question 完全相同）",
 "question": "题干（与 prompt 完全相同）",
 "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
 "choices": ["A","B","C","D"],
 "answer": "A",
 "type": "choice",
 "difficulty": "basic",
 "explanation": "≥25 汉字解析，讲清为什么"
}
```

分题型硬判据（`check_geo_ztu_bank.py` 同口径）：

- **choice**：恰 4 项、label 恰 A–D、文本互异；`answer` 必须是 spec 给的 `label`（规格已预分配，⛔ 不许自己改）；`choices == ["A","B","C","D"]`；禁凑数项（「以上都不对」「无法确定」「仅在大学学习」）。
- **fill**：题干必须含 `____`（四个下划线）或 `＿＿`；`options: []`、无 `choices`；`answer` 为唯一填空内容。
- **numeric**：`options: []`；`answer` 为数值字符串；必带 `verify`，且 `verify` 只含数字与 `+ - * / ** ( )`（**禁 `int()`/`round()`/`abs()`**），用 `eval(verify, {"__builtins__":{}}, {})` 复算必须等于 `answer`。
- **short-answer**：`options: []`；`answer` ≥15 汉字且含「；」分 2–3 条。
- 全题型：题干 ≥12 字；解析 ≥25 汉字；禁 Markdown（`** ## | $ \frac`）；**片内题干不得重复**（同一分片里，十道题不能都写「下列说法正确的是」——每题加**主题前缀**，如「关于亚洲的地形，下列说法正确的是」）。
- 教材口径准确：地名、数据、图名、活动名以教材原文为准，**不许编造教材没有的数据/结论**；不确定就不写具体数字。

## 3. 自检（交付前必须自己跑到 PASS）

```bash
cd ~/Desktop/cn-k12-dxyc2286
/usr/bin/python3 scripts/check_geo_ztu_points.py data/geography-zhongtu-cz/_points/TNN.json
/usr/bin/python3 scripts/check_geo_ztu_bank.py   data/geography-zhongtu-cz/_bank/TNN.json
```
两条都要 `RESULT: PASS`（或退出码 0）。红了就地改，改完重跑，直到双 PASS 再汇报。

## 4. 汇报（中文，一行）

```
TNN | 点=9 | 题=69 | points=PASS bank=PASS | 难点/遗留=<无/一句话>
```
严禁谎报：PASS 必须来自你实跑的输出。

## 5. 教材素材（唯一来源，⛔ 不联网、不编造）

- 本片对应章的大单元 docx（含引言/内容结构/学习目标/学业评价/课时设计，信息最全）：见派单卡里的 `大单元docx`。
- 七上/八上另有**逐课时分课时 docx**（文件名含「第N课时 <课时名>」），可逐课时取证；七下/八下无分课时 docx，用大单元 docx 的「十五、教-学-评一致性课时设计」段逐课时取证。
- 教材 PDF（需核对原文时用）：`~/Desktop/中小学教材/中小学教材/地理/初中/中图版（钟作慈）/`。
