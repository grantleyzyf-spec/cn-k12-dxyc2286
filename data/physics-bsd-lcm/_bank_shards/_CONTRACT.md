# physics-bsd-lcm 题库分片合同（北师大版·李春密·初中物理）

批次根：`/Users/a627692/Desktop/cn-k12-dxyc2286/data/physics-bsd-lcm`

## 你要交的只有一件
按你那张卡的分片号（如 `PLCM_C12`）写一个文件：

```
/Users/a627692/Desktop/cn-k12-dxyc2286/data/physics-bsd-lcm/_bank/PLCM_Cxx_out.json
```

形状（**必须是对象，不能是裸数组**）：

```json
{"shard": "PLCM_Cxx",
 "topics": [{"id":"plcm_j001","name":"温度及其测量","level":"lesson","chapter":"八年级全一册 第1章 热现象 · 第1节 温度及其测量","domain":"物质","type":"procedural","description":"…40–90 汉字…","mastery_criteria":["…","…"]}],
 "questions": [{"id":"plcm_q0001","topicId":"plcm_j001","type":"choice","difficulty":"basic","stem":"…","options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],"choices":[同上四项],"answer":"B","analysis":"…≥25 汉字…"}]}
```

- `topics` 必须**覆盖分片 spec 里全部点**（spec 的 `topics[]` 就是清单），每点写：`description`（40–90 汉字，落到本节的真实物理内容）、`mastery_criteria`（1–3 条）、`type`（照 spec 同点的 type）。
- `questions` 的题量、`id`、`topicId` 全部照 spec 的 `slots[]`：每槽 `count` 道、`idRange` 里取 id，**不许自己编号**。

## 逐题硬指标（checker 逐条查）
- `type` 只认 `choice` / `fill` / `short-answer` / `numeric`；`difficulty` 只认 `basic` / `standard` / `hard`。
- 题干 ≥12 汉字；解析 `analysis` ≥25 汉字（写到 40–80 更稳）；题干与解析禁 Markdown（`**` `##` `$$` `\frac` `|`）。
- `choice`：`options` 恰 4 项、`label` A/B/C/D 互异、四项文本互异、`answer` 必须是其中一个 label、`choices` 与 `options` 逐字相同；禁「以上都不对 / 以上都对 / 无法确定 / 仅在大学学习」这类凑数项。
- `fill`：题干含 `____`；`answer` 非空字符串；`options` 必须为 `[]`。
- `short-answer`：`answer` 用「；」分成 2–3 条要点。
- `numeric`：给 `verify`（**纯算术表达式**，只能用数字和 + - * / ** 和括号，⛔ 不许 `int()` `round()` 等函数），`eval(verify)` 必须等于 `answer`（`answer` 写数字字符串）。
- 题量配额（每槽）：8 题的课时点必须 `choice≥3 / fill≥2 / short-answer≥2 / numeric≥1`，且 `basic/standard/hard` 三档各≥1；5 题的单元点必须 `choice≥3 / fill≥1 / short-answer≥1`（不做三档要求）。
- 片内题干不许重复（去掉空白后比对），同一句模板改数字也算重复。

## 内容来源（真实教材，不编知识）
- 本册全文（Vision OCR，含页标记）：
  `…/data/physics-bsd-lcm/_text/八年级全一册/整册全文.txt`
  `…/data/physics-bsd-lcm/_text/九年级全一册/整册全文.txt`
- 先 `grep -n "<本章名>" 整册全文.txt` 定位本章起止页，再 `sed -n 'a,bp'` 读该章正文，题干与解析要贴合该章的概念、规律、实验与习题口径。
- 数值题优先用本册给出的数据与单位（g 取 10 N/kg）；不要引入教材外的常数。

## 自检（必须跑到 PASS）
```
cd /Users/a627692/Desktop/cn-k12-dxyc2286
/usr/bin/python3 scripts/check_plcm_bank.py data/physics-bsd-lcm/_bank/PLCM_Cxx_out.json
```
末行必须是 `RESULT: PASS`。报错就改自己的文件重跑，直到 PASS。

## 纪律
- 只写自己的 `_bank/PLCM_Cxx_out.json`；**不许**动 `topics.json` / `dependencies.json` / 别的分片 / 脚本 / 技能库。
- 禁 `search_files` 全仓检索（会超时）；只用上面给的绝对路径 + `read_file` / `grep` / `sed`。
- 写完在回复里报：分片号、题数、PASS 行原文。
