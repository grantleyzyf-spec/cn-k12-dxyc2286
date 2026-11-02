# 鄂教版高中数学图谱 · 题库工位契约（WORKER.md）

## 你的输入（只读）
- 派单：`data/math-ejiao/_shards/cNN.json` —— 只含你这一章：1 个单元点 + 若干课时点（id / 名称 / chapter / page / 所属节）
- 教材内容依据：本文件派单里 `lessons[].name`（课时名）与 `sections[]`（教材节名）即本章知识点边界；**不得写其他章的内容**。

## 你的产出（只写这一个文件）
`data/math-ejiao/_bank/cNN.json`，结构严格如下：

```json
{
 "unit_points": [
   {"id": "<派单的 unit_id>", "type": "conceptual",
    "description": "本章内容与地位，汉字≥40",
    "mastery_criteria": ["可观测的达成标准，汉字≥12"],
    "tags": ["<领域>", "<章名>"],
    "standards": [],
    "questions": [ 5 道题 ]}
 ],
 "lesson_points": [
   {"id": "<派单的 lesson id>", "type": "conceptual|procedural|application|reasoning",
    "description": "这个课时点教什么，汉字≥40",
    "mastery_criteria": ["…", "…"],
    "misconceptions": ["典型错误1（汉字≥8）", "典型错误2"],
    "page": <派单里该点的 page，原样整数>,
    "tags": ["<领域>", "<章名>"],
    "standards": [],
    "questions": [ 8 道题 ]}
 ]
}
```

## 题目字段（每题必填，多写 schema 之外的键会被丢弃）
| 字段 | 规则 |
|---|---|
| `id` | `mej_q_<cNN>_<三位序号>`，本章内唯一，如 `mej_q_c01_001` |
| `topicId` | 必须等于所在点的 id（单元点/课时点各归各） |
| `prompt` | 题干，汉字 ≥8，**禁用 Markdown 符号 `* _ ` # [ ] |`**；公式用纯文本（如 `sin(x)`、`2^3`、`√2`、`x²`），不要 LaTeX |
| `options` | 选择题必须恰好 4 项：`[{"label":"A","text":"…"},{"label":"B",…},{"label":"C",…},{"label":"D",…}]` |
| `answer` | 选择题写选项字母；`numeric` 写数值字符串；`fill`/`short-answer` 写文字答案 |
| `type` | `choice` / `numeric` / `fill` / `short-answer` 四选一 |
| `difficulty` | 只用 `basic` / `standard` / `hard`，**同一个点内三档必须都有** |
| `explanation` | 解析，汉字 ≥15，说清依据与易错点 |
| `verify` | 仅 `numeric` 必填：可复算的 JSON 表达式，见下 |

`verify` 的两种写法（脚本会求值并与 `answer` 比对，容差 1e-6）：
```json
{"type":"num","value":2.5}
{"type":"op","op":"div","values":[{"type":"num","value":1},{"type":"num","value":2}]}
```
op 支持 `op`(加) / `sub` / `mul` / `div` / `pow`。

## 题量与配比（逐点卡）
- 单元点：**5 题**；课时点：**8 题**。
- 每个点内：选择题 5–6 道、`numeric` 1–2 道，其余可为 `fill`；简答题（`short-answer`）每点 ≤1。
- **答案字母不得集中**：同一单元点/课时点内，选择题正确选项同一个字母的占比 **≤40%**（例：5 道选择题不要 A 占 3 道以上）。
- 干扰项要像真错因（符号错、漏条件、公式记混），不要「以上都不对」凑数。

## 内容纪律
1. 只写本章教材内容；术语用教材口径（如「函数的三要素」「等比数列的公比」「离散型随机变量的分布列」）。
2. `page` 原样照抄派单里的值，**不得自造页码**；`standards` 留空数组（引文后续统一回填）。
3. 不出「鄂教版」以外的教材栏目名；不写「本课/本单元」之类元话语。
4. 难度真实分层：`basic` 是概念直用，`standard` 需两步推理，`hard` 需综合或含参数讨论。

## 自检（必做，末行必须 PASS）
```bash
python3 data/math-ejiao/_scripts/check_bank_ej.py cNN
```
脚本会逐点核对覆盖、题量、题干/解析汉字数、选项 A–D、答案位占比、难度三档、`verify` 可复算。FAIL 就按提示改到 PASS（可反复跑）。**不要改派单、不要改脚本、不要写其他章的文件。**

## 回复格式（一句话）
`cNN 完成：单元点 1 / 课时点 K / 题 M；check_bank_ej.py 末行 PASS`
