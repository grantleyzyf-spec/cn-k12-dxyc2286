# 湘教版地理（geography-xiangjiao）· 断点与续跑

> 断点时间：2026-11-04 13:40（谷段收口）。阶段 0–8 已完成，门禁全绿；阶段 9（推送）进行中。
> 谷段（12:00–14:00、18:00–次日 09:00）跑重活；峰段只做只读与单点修改。

## 1. 已完成（阶段 0–4，全部门禁绿）

| 阶段 | 产物 | 判据 |
| --- | --- | --- |
| 0 教材 | 湘教版 9 册文字层 → `data/geography-xiangjiao/_text/*.txt` | 39.4k–64.2k 汉字/册 |
| 1 结构 | `_skeleton.json`：39 章 / 124 节 | 章号连续、节号章内递增 |
| 2 知识点 | `topics.json`：163 点（39 单元 + 124 课时），内容 163/163 回填 | `scripts/test_geo_xiangjiao.py` **31/31** |
| 3 题库 | `questions.json`：1187 题（课时 8、单元 5），39 片全 PASS | 同上 |
| 4 试卷 | `exams/<册>/*.json`：**75 卷 / 1800 题**（39 单元 + 18 期中 + 18 期末），覆盖 163/163 点 | `scripts/check_geo_xiangjiao_exam.py --all` **75/75 PASS** |

其他已过：`validate.py geography-xiangjiao` 0 错；ajv `schema-topic` / `schema-question` 两份 valid；
注册四处（`schema-topic.json` enum、`data/subjects.json`、`data/subject-groups.json`、`explore/app.js`）；
专用 CI `.github/workflows/validate-geography-xiangjiao.yml`。

## 2. 12:00 谷段要做（按序，每步门禁绿了再下一步）

### 5. 学层精讲（124 篇 / 33 片）——✅ 已完成

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 scripts/gen_geo_xiangjiao_learn_shards.py     # 已生成，可重跑（幂等）
ls data/geography-xiangjiao/_learn_shards/GXJ_L*.json | wc -l    # 应为 33
```
- 契约：`/Users/a627692/Desktop/qbank-upgrade/geography-xiangjiao/CONTRACT_LEARN.md`
- 每片 4 篇（尾片少），落盘 `data/geography-xiangjiao/learn/_parts/<册>/<topicId>.json`
- 引文检索：`python3 scripts/find_geo_quote.py <册> <关键词> --root data/geography-xiangjiao/_text`
- 自检：`python3 scripts/check_geo_xiangjiao_learn.py --dir data/geography-xiangjiao/learn/_parts/<册>`
- 派单：一次 `delegate_task` 派 ≤50 片（33 片正好一批），上下文只写「读契约 + 分片号 + 落盘 + 自检」

合并与验收：
```bash
python3 scripts/merge_geo_learn.py --bucket geography-xiangjiao 2>/dev/null || cp -r data/geography-xiangjiao/learn/_parts/* data/geography-xiangjiao/learn/
python3 scripts/check_geo_xiangjiao_learn.py --dir data/geography-xiangjiao/learn
```
（若 `merge_geo_learn.py` 不认桶名，直接照 `data/geography/learn/*.json` 的形状写一个 9 行合并脚本，或用 `merge_geo_learn.py` 改 `D` 常量。）

### 6. 试卷讲解（75 份）——✅ 已完成

```bash
# 生成讲解分片（一片一卷）
python3 scripts/gen_geo_xiangjiao_lecture_shards.py   # 若缺，照 geography 的 gen_lecture_shards.py 改 D 常量
```
- 契约：`/Users/a627692/Desktop/qbank-upgrade/geography-xiangjiao/CONTRACT_LECTURE.md`
- 落盘 `data/geography-xiangjiao/exam_lectures/<册>/<卷名>.json`
- 自检：`python3 scripts/check_exam_lecture.py --subject geography-xiangjiao <json>`
- 派单：75 片分两批（38 + 37）

### 7. 站点三索引——✅ 已完成（湘教 9 册知识点 / 9 册 75 卷 / 75 卷）

```bash
python3 scripts/build_exam_index.py                 # diagnose/exam-index.json
python3 scripts/build_learn_site.py                 # learn/index.json
python3 scripts/build_exam_lecture_site_v2.py       # learn/exam/index.json + learn/exam/data/*.json
```
核对：地理（湘教版）应在三处都有条目；`build_exam_index.py` 的 `SUBJECTS` 与 `SUBJECT_EDITION` 需含 `geography-xiangjiao`（缺则补一行）。

### 8. docx 交付——✅ 已完成（试卷 150 / 学层 133 / 讲解 75）

```bash
MATH_BUCKET=geography-xiangjiao SUBJECT_NAME=地理 MATH_EDITION=湘教版 python3 scripts/build_math_exam_docx.py
MATH_BUCKET=geography-xiangjiao SUBJECT_NAME=地理 MATH_EDITION=湘教版 python3 scripts/build_math_learn_docx.py
MATH_BUCKET=geography-xiangjiao SUBJECT_NAME=地理 MATH_EDITION=湘教版 python3 scripts/build_math_learn_booklet.py
MATH_BUCKET=geography-xiangjiao SUBJECT_NAME=地理 MATH_EDITION=湘教版 python3 scripts/build_exam_lecture_docx.py
```
预期：试卷 150 份（75×2）、学层 133 份（124 + 9 合订）、讲解 75 份。

### 9. 聚合与上线——⏳ 推送中（214 文件，Git Data API）

```bash
python3 scripts/test_geo_xiangjiao.py && python3 scripts/validate.py --all
# 推 data/geography-xiangjiao + scripts + docs + workflow + 三索引 + subjects/schema
```
⚠️ 派生共享文件（`cn-curriculum-standards.json`、`volume-map.json`、`stats.json`、`subject-groups.json`）**不要用本地全量重建结果推**——
本地含并行会话 WIP，CI freshness 会红。做法同地理（人教）那次：下载远端 → 只拼本桶那一段 → 再推。

## 3. 已知缺口（如实记录）

1. 八上第三章（中国的自然资源）与原「探究与实践」章重挂时补了 4 节，内容由补写批回填，已过门禁。
2. 两处无节章（八下第九章「建设永续发展的美丽中国」等）只有单元点，不虚构课时。
3. 乡土地理未建点（与人教版 `geography` 同口径缺口）。
4. 卷面/学层/讲解均未经一线教师审读，机检只保证结构、分值、覆盖、原创性。

## 4. 峰段纪律

- 峰段只做：读盘、跑门禁、单点修改、汇报、等用户确认；不派单、不批量渲染、不推送。
- 距边界 <30 分钟不启新批次；跨峰前先落断点（本文件）。
