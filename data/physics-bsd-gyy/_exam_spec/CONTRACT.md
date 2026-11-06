# 北师大版（郭玉英）初中物理 · 试卷合同（120 分 / 120 分钟 / 24 题）

## 输入 / 输出
- 规格：`data/physics-bsd-gyy/_exam_spec/<examId>.json`（含 `examId / kind / book / paper / scope / topicIds`）
- 落盘：`data/physics-bsd-gyy/exams/<册>/<paper>.json`（册目录写成 `八年级上册` 这种裸册名）
- 自检：`python3 scripts/check_pgy_exam.py --exam <你的产物绝对路径>`，末行须 `RESULT: PASS`

## 卷面模板（逐字照抄，不许改数字）
```
一、选择题（每小题 3 分，共 36 分）   12 题
二、填空题（每小题 4 分，共 24 分）    6 题
三、实验探究题（每小题 8 分，共 24 分） 3 题
四、计算与应用题（每小题 12 分，共 36 分）3 题
```
合计 24 题 / 120 分 / 120 分钟。

## 数据结构
```json
{
  "examId": "pgy_exam_8a_u01",
  "kind": "unit",
  "book": "八年级上册",
  "paper": "第一章 物态及其变化 测试卷",
  "grade": 8,
  "fullScore": 120,
  "duration": 120,
  "scope": ["八年级上册 第1章 物态及其变化"],
  "sections": [
    {"title": "一、选择题（每小题 3 分，共 36 分）", "count": 12, "score": 36, "rule": "每小题 3 分，共 36 分"},
    {"title": "二、填空题（每小题 4 分，共 24 分）", "count": 6, "score": 24, "rule": "每小题 4 分，共 24 分"},
    {"title": "三、实验探究题（每小题 8 分，共 24 分）", "count": 3, "score": 24, "rule": "每小题 8 分，共 24 分"},
    {"title": "四、计算与应用题（每小题 12 分，共 36 分）", "count": 3, "score": 36, "rule": "每小题 12 分，共 36 分"}
  ],
  "items": [
    {"no": 1, "itemId": "<examId>_q01", "section": "一、选择题（每小题 3 分，共 36 分）",
     "type": "choice", "score": 3,
     "stem": "……（≥10 汉字，完整问句）",
     "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
     "answer": "B", "analysis": "……（≥30 汉字，写清推理与干扰项错因）",
     "topicIds": ["pgy_j002"]}
  ]
}
```
非选择题（填空/实验探究/计算）：
- `options: []`
- `answer` 写答案要点（计算题写最终结果＋单位）
- `scoreRule`：字符串数组，每条形如 `"列式正确（3 分）"`、`"代入数据并计算（4 分）"`、`"结果与单位正确（5 分）"`，
  **各条分值之和必须等于该题题分**（12 分题给 3–4 步，8 分题给 2–3 步）。
- 计算题在 `analysis` 里写完整解题过程，g 取 10 N/kg 并注明。

## 硬性禁则
- ⛔ **卷面必须原创**：不许照搬 `data/physics-bsd-gyy/questions.json` 的题干（查重阈值 0.85），同一考点要换情境、换数据、换问法；选择题四个选项都自己写。
- ⛔ 禁 Markdown（`**`、`##`、表格竖线）、禁 LaTeX（`$…$`、`\\frac`）。
- ⛔ 禁「以上都不对」「无法确定」这类凑数项。
- 物理符号统一 `× ÷ ＋ － ＝`，单位用 N / kg / m³ / kg/m³ / Pa / J / W / V / A / Ω / ℃。
- 题号 1–24 连续；`itemId` 命名 `<examId>_qNN`（NN 两位数）。

## 覆盖要求（检查器会算）
- 单元卷：`scope` 内**每个课时点至少被 1 道题挂到**（`topicIds` 里出现）。
- 期中/期末：每章 ≥2 题，整卷覆盖该册课时点 ≥80%；期中只考前一章半（scope 已给），期末考全册。

## 流程
1. 读规格 JSON，按 `scope` 到 `topics.json` 取本卷可用的点与课时（只读这两个文件，⛔ 不用 `search_files`）
2. 按上面的模板写 24 题，落盘
3. 跑 checker 到 `RESULT: PASS`；红了就地改，⛔ 不要改 checker、不要改别的卷
