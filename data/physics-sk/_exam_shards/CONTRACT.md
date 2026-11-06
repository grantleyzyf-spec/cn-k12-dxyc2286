# 苏科版初中物理 试卷工位合同（E01–E08）

## 产物

`{"book":"…","papers":[<卷>]}` 写到 `data/physics-sk/_exam_out/ENN.json`；卷数、`examId`、`paper`、`kind`、`scope`、`topicIds` 逐字照抄 `_exam_shards/ENN.json`，只补内容。

## 卷面口径（硬指标）

- 初中：**满分 120、时长 120 分钟、24 题**。
- 两段：`{"rule":"每小题 3 分，共 54 分","items":[18 题]}` ＋ `{"rule":"每小题 11 分，共 66 分","items":[6 题]}`，合计 120。
- 题号 `no` 全卷连续 1→24；`itemId` = `<examId>_qNN`，全卷唯一。

## 每题字段

```json
{"no":1,"itemId":"psk_exam_j8a_u02_q01","type":"choice","score":3,
 "stem":"题干（≥12 字）",
 "options":[{"label":"A","text":"…"},{"label":"B","text":"…"},{"label":"C","text":"…"},{"label":"D","text":"…"}],
 "answer":"B","analysis":"解析（≥20 汉字）","topicIds":["psk_j004"]}
```

- 综合题 `type` 用 `short-answer`/`solve`，必须带 `scoreRule`（各步之和 = 11）。
- `fill`/`numeric` 的 `answer` 非空；`numeric` 另带 `verify`（纯算式，可 eval 复算）。
- `topicIds` 非空且属本册；**单元卷必须覆盖 scope 下全部点**（含单元点本身）。

## 质量要求

- 题干 ≥12 字、解析 ≥20 汉字；选择题 4 项 A–D 互异、`answer` ∈ label；全卷 A/B/C/D 各 ≥15%。
- 与 `data/physics-sk/questions.json` 题干相似度 <0.85（⛔ 不许搬题库题）。
- 物理量、单位、公式按教材口径（g 取 10 N/kg；ρ水=1.0×10³ kg/m³）；计算题必须自己复算。
- 禁 Markdown（`**`、`##`、`|`、`$`）。

## 自检

```bash
cd /Users/a627692/Desktop/cn-k12-dxyc2286
/usr/bin/python3 - <<'PY'
import json
d=json.load(open('data/physics-sk/_exam_out/ENN.json'))
for i,p in enumerate(d['papers']):
    json.dump(p, open('/tmp/ENN_%d.json'%i,'w'), ensure_ascii=False)
PY
for f in /tmp/ENN_*.json; do /usr/bin/python3 scripts/check_phys_sk_exam.py "$f" || echo "FAIL $f"; done
```
全部 PASS 才算完。

## 汇报

`ENN | 卷=N | 题=24N | check=PASS`
