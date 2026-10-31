# 试卷 ↔ 自适应诊断：链接规范（V1.0）

数据层三件套 + 判定口径。任何诊断引擎（自研 / 第三方题库系统）照这份读就能接。

## 1 稳定 id

| 对象 | 规则 | 例 |
|---|---|---|
| 卷 | `mat_exam_<册码>_<卷码>` | `mat_exam_g7a_u1` |
| 题 | `<examId>_q<两位题号>` | `mat_exam_g7a_u1_q01` |
| 知识点 | 已有 `mat_p####`（小学初中）/ `mat_h###`（高中） | `mat_p1022` |

册码：`g1a…g9b`（年级＋上下册）、`bx1/bx2`（必修一二）、`xx1/xx2/xx3`（选必一二三）。
卷码：`u1…u10`（单元卷）、`mid_a/mid_b`（期中 A/B）、`fin_a/fin_b`（期末 A/B）。

## 2 每道题挂三个链接（`scripts/build_math_exam_links.py` 自动生成，勿手写）

```json
{"no": 6, "itemId": "mat_exam_g7a_u1_q06", "type": "choice", "score": 3,
 "topicIds": ["mat_p1022"],
 "prereq": ["mat_p1021"],
 "prereqUpper": ["mat_p712"],
 "reteach": ["mat_p1022_q1", "mat_p1022_q2"]}
```

- `topicIds`：主考知识点（可多个，得分按题分**均摊**到各点）
- `prereq`：**课时点 → 课时点**的学习顺序前置（同单元上一课时）
- `prereqUpper`：单元级点（上位概念）——**只展示、不参与缺口判定**
- `reteach`：该点题库同点题（错后回练，最多 3 道）

⚠️ 2026-10-31 修正：早期把「同章单元级点」当课时点的硬前置连边，导致
「1.1 正数和负数」的前置成了「科学记数法」。已剔除 512 条错边
（`scripts/fix_math_ke_prereq_model.py`），课时→课时边升为 `hard`；
降为根节点的 97 个课时点补了 `root_reason`。

## 3 两个索引

- `data/math/exam_links.json` —— 卷 → 题 → 知识点/前置/回练（诊断引擎主入口）
- `data/math/topic_exam_map.json` —— 知识点 → 考过它的 `itemId`（错题归因、看板）

## 4 掌握度判定（`webapp/app.py` 实现，参数可改）

| 条件 | 结论 |
|---|---|
| 该知识点得分率 ≥ 80% | **掌握** |
| 60% ≤ 得分率 < 80% | **待巩固**（回练同点题） |
| 得分率 < 60% | **未掌握** |
| 未掌握 且 其课时前置得分率 < 50% | **前置缺口**（先补前置，别刷本点） |
| 前置点本卷未考 | 记 `prereqUnknown`，补练里给 1 道基础题当**探针** |

得分率 = 该点得分 / 该点分值；卷中一题挂多个点时按题分均摊。
`rate` 一律存 4 位小数（曾用 2 位导致 6/108.5 显示成 6.0%，已修）。

## 5 错因标签

`data/math/misconceptions/<册>.json` → 合并进 `topics.json` 的 `misconceptions`（3–5 条/点，
每条 ≥8 字，写「症状 + 为什么错」）。523 个课时点已全覆盖（2100 条）。
自检：`scripts/check_math_misconceptions.py`。禁止「粗心/不认真/马虎」这类空话，
也禁止自相矛盾（如「认为绝对值大的反而小」却举 −2<−5）。

## 6 答题站（本地单机）

```bash
python3 webapp/app.py 8855        # → http://127.0.0.1:8855
```

- 判题：choice 精确；multi 集合相等（全对才得分）；fill 去空白/全角归一，支持「或」多答案；
  numeric 容差 1e-6（支持分数）；solve 显示参考答案与评分标准，由学生/老师按步骤自评
- 输出：`data/math/attempts.db`（SQLite，每次作答一行，payload 含逐题得分与诊断结论）
- 接口：`/api/papers` `/api/paper?examId=` `/api/submit`(POST) `/api/report?attempt=` `/api/practice?attempt=`
- 补练优先级：前置缺口 → 未掌握 → 待巩固

## 7 一条命令跑通数据链

```bash
/usr/bin/python3 scripts/build_math_exam_links.py     # 注 id + 三向链接 + 生成两个索引
/usr/bin/python3 scripts/merge_math_misconceptions.py --write
/usr/bin/python3 scripts/rebuild_aggregates_only.py
/usr/bin/python3 scripts/test_math.py && /usr/bin/python3 scripts/validate.py math
```
