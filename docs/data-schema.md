# 数据契约 v2（topics / dependencies / questions）

本仓库所有学科共用一套节点契约。改数据前先对表；`scripts/normalize_to_ref_schema.py` 会把旧字段（`fall`/`spring`、`difficulty: easy/medium/hard` 别名等）归一，**不要手改汇总文件**。

## 1. 知识点 `data/<subject>/topics.json` → 汇总 `data/topics.json`

```json
{
  "id": "cnm_p001",
  "name": "20以内的进位加法",
  "subject": "math",
  "domain": "数与代数",
  "grade": 1,
  "semester": "上",
  "chapter": "一年级上册 第五单元 20以内的进位加法",
  "type": "procedural",
  "description": "掌握凑十法，能正确计算 20 以内的进位加法",
  "mastery_criteria": ["能把一个加数拆成凑十的两个数", "能正确算出 20 以内进位加法的结果"],
  "diagnostic_question": { "question": "9 + 4 = ?", "answer": "13" },
  "external": false,
  "standards": [{ "id": "cms-2022:1.NA.05", "confidence": "exact" }],
  "tags": ["数与运算", "加法"],
  "prerequisites": ["cnm_p000"],
  "curriculumRef": "cms-2022:1.NA.05",
  "verified": false
}
```

| 字段 | 必填 | 约束 |
| --- | --- | --- |
| `id` | ✅ | `^(?:[a-z]{2,6})_[ph]\\d{2,4}$`；前缀 2–6 字母（`it_`、`chem_`、`mat_` 都合法），全库唯一 |
| `subject` | ✅ | 必须是 `data/subjects.json` 里的 id（17 选 1） |
| `grade` | ✅ | `1`–`14`：`1`–`9` 义教年级，`10`–`14` 高中册次（必修一/二、选必一/二/三） |
| `semester` | ✅ | `上` / `下` / `全`；`fall`、`spring` 已废弃（脚本会迁移） |
| `type` | ✅ | `conceptual` / `procedural` / `reasoning` / `modeling` / `application` |
| `mastery_criteria` | ✅ | 1–3 条，**可观察**（能说出/能算出/能区分），禁「理解」「了解」 |
| `standards[]` | ✅（可为空数组） | `{id, confidence, quote?, sourceLine?}`；`confidence ∈ {exact, partial, inferred}` |
| `standards[].quote` | 选填 | 12–40 字，必须**逐字**出自课标原文；CI 回表核验，命中不了就不写 |
| `prerequisites[]` | ✅（可为空） | 直接先修 id，与 `dependencies.json` 互为镜像 |
| `external` | ✅ | 跨学科/外部引用节点为 `true`（不要求有先修边） |
| `verified` | ✅ | 是否经教师审核；当前全库为 `false` |

## 2. 先修边 `dependencies.json`

```json
{ "from": "cnm_p000", "to": "cnm_p001", "type": "hard" }
```

- `hard`：不掌握前者基本学不会后者（诊断只沿 hard 回溯）。
- `soft`：有帮助但非必需，多为教材编排顺序。
- 硬规则：两端必须存在、无自环、无重复边、无环；别名 `prerequisite/required/strong → hard`、`suggested/related/weak → soft` 由规范化脚本映射。

## 3. 诊断题 `questions.json`

```json
{
  "id": "cnm_p001_q1",
  "topicId": "cnm_p001",
  "prompt": "9 + 4 = ?",
  "question": "9 + 4 = ?",
  "answer": "13",
  "type": "numeric",
  "difficulty": "basic",
  "explanation": "9 凑十需要 1，4 拆成 1 和 3，10 + 3 = 13。",
  "verify": "9+4"
}
```

- `prompt` 是规范字段，`question` 仅作兼容别名（同值）。
- `type ∈ {choice, fill, short-answer, numeric}`；`choice` 必须给 4 个 `{label, text}`，`answer` 是 label。
- `difficulty ∈ {basic, standard, hard}`（`easy/medium` 由脚本归一）。
- `numeric` 的 `verify` 是能被 Python `eval` 复算的表达式，用于自动校验答案解析。

## 4. 课标条目 `cn-curriculum-standards.json`

```json
{
  "source": { "…": "来源与版次说明" },
  "generated_from": "scripts/build_standards_index.py",
  "subjects": {
    "math": { "entryCount": 314, "topicsTotal": 479, "topicsWithStandard": 479,
              "entries": [{ "id": "cms-2022:1.NA.05", "topicIds": ["cnm_p001"], "quote": "…", "sourceLine": "…" }] }
  },
  "totals": { "subjects": 17, "entries": 972, "topics": 1924, "topicsWithStandard": 1918 }
}
```

**别手改**：由 `scripts/build_standards_index.py` 生成，CI 有「重生成后 diff 必须为空」的新鲜度闸门。

## 5. Schema 与校验

- `data/schema-topic.json` / `schema-question.json` / `schema-dependency.json` 根节点是 `{"type":"array","items":{…}}`，`items` 必须显式 `"type":"object"`（ajv 严格模式要求）。
- 提交前跑：

```bash
python3 scripts/normalize_to_ref_schema.py --check
python3 scripts/normalize_to_ref_schema.py --write
python3 scripts/build_standards_index.py
python3 scripts/validate.py --all
python3 scripts/build_stats.py --write
```

## 6. 常见踩坑

1. **汇总文件不是真源**：`data/topics.json`、`dependencies.json`、`questions.json` 由分学科文件重建；改汇总会在下次重建时被覆盖。
2. **`standards` 加了 `additionalProperties:false` 后多键即红**：加字段先改 schema 再落数据。
3. **`confidence` 会被写花**（`direct`/`full`/`medium`）：规范化脚本有别名映射，映射完必须重跑 `build_standards_index.py`。
4. **id 前缀宽度**：早期正则写成 `[a-z]{3}` 会把 `it_`、`chem_` 整批判错，现为 `[a-z]{2,6}`。
