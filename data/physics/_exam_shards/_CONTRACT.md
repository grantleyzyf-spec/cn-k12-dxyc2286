# 人教版物理 · 试卷分片合同（PHYS_E01–E44）

> 只读本文件 ＋ 自己的分片 JSON ＋ 教材文字层。**只写 `data/physics/exams/<册>/<卷名>.json`**；不改仓库其它文件。

## 1. 输入

`data/physics/_exam_shards/PHYS_Enn.json`：
- `papers[]`：本片要写的卷（1–2 卷，**按给几卷写几卷**），含 `paper/kind/book/stage/term/grade/scope/examId`
- `spec`：本学段卷制（sections 的 title / rule / 题型 / 题数 / 每小题分）
- `topics`：`examId → 可用知识点[]`（`id/name/level/chapter`），⛔ 只能用这些点
- `out`：落盘路径模板（把 `{book}` `{paper}` 换掉）

## 2. 卷面口径（写死，别现算）

| 学段 | 满分 | 时长 | 结构 |
|---|---:|---:|---|
| 初中（八/九年级） | 120 | 120 分钟 | 一、选择题 18×3＝54 ｜ 二、综合题 6×11＝66 |
| 高中 | 150 | 150 分钟 | 一、选择题 18×3＝54 ｜ 二、综合题 6×16＝96 |

- 卷根字段：`examId / kind / paper / book / stage / term / grade / duration / fullScore / scope / sections`
- `paper` 必须与文件名逐字一致。
- `sections[]` 每段必须带 `title`（形如「一、选择题（每小题 3 分，共 54 分）」）与 `rule`（「每小题 3 分，共 54 分」），`items[]` 题号 1..24 连续。

## 3. 题目字段

```json
{"no": 1, "itemId": "<examId>_q01", "type": "choice", "difficulty": "basic",
 "topicIds": ["chem_p001"], "score": 3, "stem": "…≥12 字…",
 "options": [{"label":"A","text":"…"}, …4 项…], "answer": "B", "analysis": "…≥20 汉字…"}
```
- `itemId` = `<examId>_qNN`（NN 两位，与 no 一致）。
- 综合题 `type: "short"`，带 `"scoreRule": ["写出…… 4 分", "…… 4 分", "…… 3 分"]`（**字符串数组**），各步之和＝题分；`answer` 写参考答案要点。
- 物理量用普通文本（`v=s/t`、`F=ma`、`ρ=m/V`、`P=UI`），数值题带单位（m/s、kg/m³、N、J、W），禁下标字符、禁公式对象、禁 Markdown（`**`、`##`、`|`、`$`）。

## 4. 覆盖与原创（上一批就栽在这两条，逐字照做）

- **单元卷**：`scope` 只有一章/单元 ⇒ 卷面必须覆盖该 scope 下**全部知识点各 ≥1 次**（写完后数一遍 `items[].topicIds` 并集）。
- **期中/期末**：覆盖 `scope` 内每章 ≥2 题，且覆盖该 scope 的课时点 ≥80%。
- 🔴 **卷面题目必须原创**：⛔ 不要把 `questions.json` 里的题干搬进卷面（上一批 35 处被判 0.88–1.00 相似度）。
  正确做法：同一考点换新情境（新物质、新数据、新设问），选择题四个选项也要重写；解析自己写。
  写完后跑 checker，出现「相似度 ≥0.85」就继续改到 0 处。
- **`topicIds` 是一维字符串数组**（`["chem_p001"]`），⛔ 不许嵌套 `[["chem_p001"]]`。
- 每题 `analysis` **≥30 汉字**（门禁是 20，留余量，上一批 63 处不足）。
- 选择题 18 题里 A/B/C/D 各 ≥3 题（≥15%）。

## 5. 自检（必跑）

```bash
python3 scripts/check_chem_exam.py "data/physics/exams/<册>/<卷名>.json"
```
到 `RESULT: PASS`（或 `✅ PASSED`）。报错就改自己的卷，⛔ 不改 checker、不改题库。

## 6. 汇报

```
DONE PHYS_Enn | papers=2 | items=48 | selfcheck=PASS
```
