# 历史期中卷返修契约（期中＝前半册）

## 背景
现有 22 卷期中卷的 `scope` 写成「全册」，题目也覆盖全册 ⇒ 与期末卷同范围。本批把**每册期中 A/B 重出为「前半册」**。
原卷已备份到 `data/history/exams/_mid_backup/`，**可直接读作写法参考**（结构、文风、材料题写法照它，范围与题目必须换）。

## 输入
读你的作业单 `data/history/_mid_shards/JOB_<册>.json`：
- `scopes[]`：本册**前半册**的单元标题（逐字，必须原样写进卷面 `scope`）
- `points[]`：前半册全部可考知识点（`id/name/chapter`）
- `sections[]`：卷制（段标题、rule、type、题数、分值；`score` 为 `"22,23"` 时表示论述两题分别 22、23 分）
- `papers[]`：两卷的 `path`（落盘绝对路径）、`paper`、`examId`、`keep`（这些字段**原值保留**）
- `fullScore` / `duration`

## 硬口径
1. **范围**：`scope` 逐字等于 `scopes[]`；**每道题的 `topicIds` 必须全部落在 `points[]` 的 id 集内**（⛔ 不许考后半点）。
2. **只改 `scope` 与 `sections`**，其余键（book/kind/term/grade/stage/paper/duration/fullScore/examId）照 `keep` 原样。
3. 结构照 `sections[]`：段 `title`/`rule` 逐字、题数/分值逐项对；题号从 1 连续；`fullScore` 合计对。
4. 选择题：4 项 A–D、文本互异、`answer` ∈ A–D；**全卷选择题答案位各 ≥15%**；题干 ≥12 字、`analysis` ≥20 汉字。
5. 材料/论述题（`type: short`）：必须有 `scoreRule`（**字符串数组**，每步形如「答出……，3 分」），**各步分值之和 = 该题分**；
   `answer` 用「；」分条；`stem` 要有材料引文＋设问（可分 `（1）（2）（3）`）。
6. `itemId` = `<examId>_qNN`（NN 为题号两位）。
7. **原创性**：题干与 `data/history/questions.json` 的相似度必须 <0.85（换情境、换问法、换材料；⛔ 不许照抄题库题干）。
8. A、B 两卷题干不得重复；两卷情境与设问角度要有区分。
9. ⛔ 正文（stem/options/answer/analysis/scoreRule）禁拉丁字母（仅选项 label 与 `answer` 的 A–D）；⛔ 禁 Markdown（`**`、`#`、表格竖线）。
10. 覆盖：前半册每个知识点**至少被考到 1 次**（A 卷全覆盖，B 卷可换角度但仍全覆盖）。

## 自检（必跑）
```bash
/usr/bin/python3 scripts/check_history_exam.py "<你的卷路径>"
```
两卷都要 PASS；再跑同册 4 卷确认没破坏别人：
```bash
for f in "data/history/exams/<册>"/*.json; do /usr/bin/python3 scripts/check_history_exam.py "$f" | tail -1; done
```
另跑原创性粗判（可选）：与自己写的卷逐题和题库做 `SequenceMatcher` 估相似度。

## 汇报（一行）
`<册> | 期中A/B 重出完成 | 两卷 PASS | 前半册 N 点全覆盖 | 选择答案位 A/B/C/D = …`
