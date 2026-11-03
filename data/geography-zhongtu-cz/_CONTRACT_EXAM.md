# 中图版（钟作慈）初中地理 —— 出卷工位合同（E01–E08 同用）

你负责一片（`_exam_shards/ENN.json`，一册一片）。片内 `papers[]` 给出本片要出的每一卷的
`examId / kind / paper / scope / topicIds / sections`（段数与题数），**卷面题文由你写**。

## 0. 产物

| 产物 | 路径 | 形状 |
|---|---|---|
| 本片全部卷 | `_exam_shards` 里 `out` 字段指定的路径（`data/geography-zhongtu-cz/_exam_out/ENN.json`） | `{"shard":"ENN","papers":[<卷>, …]}` |

⛔ 不写 `exams/` 目录（由父代合并）、不改题库、不改分片规格、不改别人的 `ENN.json`。

## 1. 卷面口径（初中，写死不许现算）

- 满分 120 分，时长 120 分钟，**24 题**。
- `sections` 两段，`title` 与 `rule` 按下面逐字写：
  - 第一段 `title`: `一、选择题（每小题 3 分，共 54 分）`，`rule`: `每小题 3 分，共 54 分`，**18 题**，每题 `score=3`，`type="choice"`。
  - 第二段 `title`: `二、综合题（每小题 11 分，共 66 分）`，`rule`: `每小题 11 分，共 66 分`，**6 题**，每题 `score=11`，`type="short-answer"`。
- 题号：全卷连续 `1..24`（`no` 字段，整数）。
- `itemId`：`<examId>_01` … `<examId>_24`（两位补零）。

## 2. 每卷字段

```json
{
 "examId": "gztu_exam_j7a_u01",
 "kind": "unit | mid | fin",
 "paper": "七年级上册 第一章 认识地球 测试卷",
 "book": "七年级上册", "grade": 7, "term": "上", "stage": "初中",
 "duration": 120, "fullScore": 120,
 "scope": ["七年级上册 第一章 认识地球"],
 "sections": [
   {"title": "一、选择题（每小题 3 分，共 54 分）", "rule": "每小题 3 分，共 54 分",
    "items": [ {"no": 1, "itemId": "gztu_exam_j7a_u01_01", "type": "choice", "difficulty": "basic",
                "topicIds": ["gztu_j002"], "score": 3, "stem": "…", 
                "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
                "answer": "B", "analysis": "…（≥20 汉字，讲清为什么，末尾写「故选 B。」）"} ]},
   {"title": "二、综合题（每小题 11 分，共 66 分）", "rule": "每小题 11 分，共 66 分",
    "items": [ {"no": 19, "itemId": "gztu_exam_j7a_u01_19", "type": "short-answer", "difficulty": "standard",
                "topicIds": ["gztu_j003"], "score": 11, "stem": "…",
                "answer": "…（分条要点，用；分隔）",
                "scoreRule": [{"desc": "…", "score": 4}, {"desc": "…", "score": 4}, {"desc": "…", "score": 3}],
                "analysis": "…（≥20 汉字）"} ]}
 ]
}
```

- `topicIds` 必须是 **本册** 点 id，取自派单 `topicIds`（单元卷＝scope 下全部单元点＋课时点）。
- **单元卷必须覆盖 scope 下每一个课时点各 ≥1 次**（这是硬闸门；综合题每题可挂 2 个点）。
- 期中/期末卷：覆盖 scope 里每个单元点各 ≥1 次、且授课时点覆盖越多越好（不强制全覆）。
- `scoreRule` 各步 `score` 之和必须**恰好等于 11**（写 3 步：4+4+3 或 5+3+3）。
- 答案位：全卷 18 道选择题的 A/B/C/D 各至少 3 道（≥15%），按 4 题一轮轮转铺。

## 3. 质量硬判据（`check_geo_ztu_exam.py` 同口径）

- 题干 ≥12 字；解析 ≥20 汉字；禁 Markdown（`**` `##` `|` `$` `\frac`）。
- 选择题恰 4 项、label 恰 A–D、文本互异、`answer` ∈ label；禁「以上都不对/以上都对/无法确定」凑数项。
- **原创性**：每题题干与 `data/geography-zhongtu-cz/questions.json` 任一道题的相似度必须 < 0.85
  （判据是 `difflib.SequenceMatcher` 去空白后的 ratio）。⛔ 不许把题库原题抄进卷面。
- 地理事实（地名、数据、图名、活动名）以教材 docx / 教材全文为准，**不得编造教材没有的数字或结论**。

## 4. 自检（交付前必跑，必须 PASS）

```bash
cd ~/Desktop/cn-k12-dxyc2286
/usr/bin/python3 - <<'PY'
import json,os,sys
sh=json.load(open("data/geography-zhongtu-cz/_exam_shards/E01.json"))
p=sh["papers"][0]
print("sample:",p["examId"],p["paper"])
PY
# 先把本片 papers 逐个拆到 /tmp/<卷名>.json（每卷一个对象，字段同 §2），再逐卷：
/usr/bin/python3 scripts/check_geo_ztu_exam.py /tmp/<卷名>.json
```
最后一片（E08）跑完再跑一次 `--all` 不现实（父代才合并），所以**自检以 `_exam_out/ENN.json` 里每卷拆出的临时文件为准**，逐卷 `RESULT: PASS`。

## 5. 汇报（中文，一行）

```
ENN | 卷=N | 题=24×N | 全卷 PASS | 遗留=<无/一句>
```
严禁谎报：PASS 必须来自实跑。
