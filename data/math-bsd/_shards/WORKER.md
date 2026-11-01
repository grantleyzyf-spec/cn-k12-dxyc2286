# 北师大版小学数学 题库写手派单（WORKER.md）

你只写**一个分片**：读完自己的 spec，产出**一个** bank 文件。不要碰别的文件，不要改
`data/math-bsd/topics.json` / `questions.json` / 别人的 `_bank/*.json`。

## 输入（绝对路径，父代会写进你的任务里）
`~/Desktop/cn-k12-dxyc2286/data/math-bsd/_shards/<册>_第<N>单元.json`
形如：
```json
{"book":"一年级上册","unit_no":"一","unit_name":"生活中的数",
 "topics":[{"id":"mbs_p001","name":"可爱的校园——数一数","domain":"数与代数","grade":1,"chapter":"一年级上册 第一单元 生活中的数"}, …]}
```

## 输出（唯一产物）
`~/Desktop/cn-k12-dxyc2286/data/math-bsd/_bank/<册>_第<N>单元.json`
```json
{"book":"一年级上册","unit_no":"一",
 "topics":[{"id":"mbs_p001","description":"…","mastery_criteria":["…","…"],
            "type":"procedural","diagnostic_question":{"question":"…","answer":"…"}}],
 "questions":[{"id":"mbs_q010001","topicId":"mbs_p001","prompt":"…","question":"…",
               "options":[{"label":"A","text":"…"},…],"answer":"A","type":"choice",
               "difficulty":"basic","explanation":"…"}]}
```

## 硬性要求（父代 `check_bsd_bank.py` 逐条机器校验，红一条即退回）
1. **每点 8 题**，题数不多不少；`topicId` 必须与 spec 里的点**一一对应**（不多不少）。
2. **题型**：每题 `type` ∈ `choice / fill / numeric / short-answer`；**每个知识点至少 3 种题型**；
   整片 `numeric ≥ 20%`、`fill ≥ 18%`、`short-answer ≥ 18%`（按 8 题算：choice 4、fill 2、numeric 2 起，
   简答至少 1–2 道）。
3. **choice**：4 个选项、`answer` 是 label；四项文本互不相同；**答案位不得偏置**（整片 A/B/C/D 每个 ≥15%）。
4. **numeric**：`answer` 是纯数字字符串，`verify` 是能被 Python `eval` 复算的表达式且**结果等于 answer**
   （例：`answer:"7"`, `verify:"3+4"`）。
5. **short-answer**：带 `keypoints`（≥2 条要点，供要点自动判读）。
6. `prompt`（`question` 同值）**≥12 字**，`explanation` **≥20 字**（写清「为什么对 / 错项错在哪」）。
7. **不得出现 Markdown 符号**：`**`、`##`、`` ` ``、`$`、`\frac`、表格竖线一律不许；数学式用
   `×`、`÷`、`＋`、`＝`、`＞`、`＜` 或中文表述；分数写「四分之三」或 `3/4`。
8. **难度三档**：`basic / standard / hard`，一片内三档都要有（建议 4/3/1）。
9. **不得超纲**：
   - 一年级上册：数数 ≤ 10（第四单元 ≤ 10 的加减）、20 以内只做数数；不许出现乘除、分数、字母表示数。
   - 全册通用：题目情境用学生生活（校园、家庭、游戏），不用方程、不用初中符号。
10. **题号**：`mbs_q<分片号两位><流水四位>`，分片号见任务单（如 S01 → `mbs_q010001`…），
    一片内从 0001 连续递增，不跳号不重号。
11. `topics[]` 里每点还要给：`description`（40–120 字，说清这节课学什么、在单元里的位置）、
    `mastery_criteria`（2–3 条，可观察可测量）、`type`（`conceptual/procedural/reasoning/modeling/application`）、
    `diagnostic_question`（1 道入口题：`{"question","answer"}`，答案用文字，简短）。

## 自检（必须自己跑，末行必须是 PASS）
```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/check_bsd_bank.py data/math-bsd/_shards/<册>_第<N>单元.json data/math-bsd/_bank/<册>_第<N>单元.json
```
红了就改自己的 bank 文件，别改 checker、别改 spec。

## 汇报格式（一句话，不要长篇）
`<分片> 完成：点 n / 题 m（choice a·fill b·numeric c·short d）/ 难度 4·3·1 / checker PASS`
