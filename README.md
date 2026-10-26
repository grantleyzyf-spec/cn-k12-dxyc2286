# 中国 K-12 全学科知识图谱（cn-k12-dxyc2286）

对齐中国教育部课程标准的**全学科知识图谱开源数据库**，覆盖小学到高中 17 个学科。
节点结构对齐参考项目 [cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy)：
每个知识点都带**可观察的掌握标准**、**节点级诊断题**、**课标条目与置信度**，可直接驱动前置诊断与学习路径推荐。

- 🌐 在线浏览：<https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/>
- 🧭 图谱浏览器：<https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/explore/>
- 🩺 自适应诊断：<https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/diagnose/>

## ⚠️ 状态声明

**这是 AI 生成的初稿，未经教师审核。** 知识点的拆分粒度、掌握标准、诊断题答案，尤其是**先修关系**都需要一线教师审核后才能用于教学、诊断或学习路径推荐。请勿直接用于正式教学。

## 覆盖学科

| 学科 | 小学 | 初中 | 高中 | 教材版本 | 对齐课标 |
|------|:----:|:----:|:----:|----------|----------|
| 数学 | ✅ | ✅ | ✅ | 人教版 | 2022版(2025修订) / 2017版(2025修订) |
| 英语 | ✅ | ✅ | ✅ | 人教版PEP / Go for it! / 人教版(2019) | 同上 |
| 语文 | ✅ | ✅ | ✅ | 部编版(统编版) | 同上 |
| 物理 | — | ✅ | ✅ | 人教版 | 同上 |
| 化学 | — | ✅ | ✅ | 人教版 | 同上 |
| 生物学 | — | — | ✅ | 人教版 | 2017版(2020修订) |
| 历史 | — | ✅ | ✅ | 部编版(统编版) | 同上 |
| 地理 | — | ✅ | ✅ | 人教版 | 同上 |
| 科学 | ✅ | — | — | 教科版 | 2022版(2025修订) |
| 信息科技 | ✅ | ✅ | — | 人教版 | 同上 |
| 日语 | — | — | ✅ | 人教版 | 同上 |
| 俄语 | ✅ | ✅ | ✅ | 人教版 | 同上 |
| 德语 | — | — | ✅ | 外研社版 | 同上 |
| 法语 | — | — | ✅ | 外研社版/沪外教版 | 同上 |
| 西班牙语 | ✅ | ✅ | ✅ | 外研社版 | 同上 |
| 音乐 | ✅ | ✅ | ✅ | 人教版 | 同上 |
| 美术 | ✅ | ✅ | ✅ | 人教版 | 同上 |

## 数据规模（2026-10-26）

| 学科 | 知识点 | 先修边 | 诊断题 | 覆盖缺口 |
|------|--------|--------|--------|----------|
| 数学 | 479 | 527 | 469 | 题量缺 10 |
| 英语 | 204 | 209 | 204 | — |
| 语文 | 205 | 203 | 205 | — |
| 物理 | 177 | 205 | 103 | 题量缺 74 |
| 生物 | 140 | 246 | 140 | — |
| 历史 | 138 | 159 | 138 | — |
| 地理 | 85 | 104 | 85 | — |
| 德语 | 100 | 60 | 100 | 先修边偏少 |
| 俄语 | 96 | 106 | 56 | 题量缺 40 |
| 信息科技 | 51 | 76 | 51 | — |
| 化学 | 62 | 79 | 62 | — |
| 法语 | 46 | 61 | 46 | — |
| 日语 | 39 | 60 | 39 | — |
| 美术 | 26 | 26 | 26 | — |
| 音乐 | 24 | 25 | 24 | — |
| 西班牙语 | 29 | 30 | 29 | — |
| 科学 | 23 | 23 | 23 | — |
| **总计** | **1924** | **2199** | **1800** | 124 个知识点暂无诊断题 |

## 节点结构（v2）

每个知识点（`topics.json` 的数组元素）：

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

| 字段 | 说明 |
|---|---|
| `semester` | `上` / `下`（与参考项目一致；旧数据的 `fall` / `spring` 已迁移） |
| `type` | `conceptual` / `procedural` / `reasoning` / `modeling` / `application` |
| `mastery_criteria` | 1–3 条**可观察**的掌握标准，用于判定是否掌握 |
| `diagnostic_question` | 节点级快诊题（`questions.json` 是题库，此处是单题入口） |
| `standards[].confidence` | `exact` / `partial` / `inferred`，标注课标对齐的确定程度 |
| `external` | 是否为跨学科/外部引用节点 |

诊断题（`questions.json`）：

```json
{
  "id": "cnm_p001_q1",
  "topicId": "cnm_p001",
  "prompt": "9 + 4 = ?",
  "answer": "13",
  "type": "numeric",
  "difficulty": "basic",
  "explanation": "9 凑十需要 1，4 拆成 1 和 3，10 + 3 = 13。",
  "verify": "9+4"
}
```

- `prompt` 为规范字段，`question` 保留为兼容别名（同值）
- `difficulty`：`basic` / `standard` / `hard`
- `verify` 可选的**可复算校验式**（数值题），便于自动校验答案解析

先修边（`dependencies.json`）：`{"from": "...", "to": "...", "type": "hard" | "soft"}`

## 目录结构

```
data/
├── topics.json              # 全学科知识点汇总（1924）
├── dependencies.json        # 全学科先修边汇总（2199）
├── questions.json           # 全学科诊断题汇总（1800）
├── subjects.json            # 学科清单与元数据
├── schema-topic.json        # 知识点 JSON Schema（v2）
├── schema-question.json     # 诊断题 JSON Schema（v2）
├── schema-dependency.json   # 先修边 JSON Schema
├── curriculum-standards.json# 课标条目库
├── verification_report.json # 数据核验报告
└── {subject}/               # 17 个学科，各含 topics/dependencies/questions.json
    └── math/                # 数学另保留按学段拆分的 topics_grade*.json（历史文件）
```

## 脚本

```bash
python3 scripts/validate.py --all        # 全学科结构与引用校验（CI 同款）
python3 scripts/validate.py math         # 单学科
python3 scripts/normalize_to_ref_schema.py --check   # 体检：节点结构完整度
python3 scripts/normalize_to_ref_schema.py --write   # 规范化到 v2 结构 + 重建汇总
python3 scripts/rebuild_canonical_from_splits.py --write  # 由拆分文件重建单文件
python3 scripts/merge_math_data.py       # 数学按学段合并（归档用）
```

## 许可证

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — 可商用，需署名。

## 反馈

发现知识点错误、先修关系问题或有改进建议，请 [提交 Issue](https://github.com/grantleyzyf-spec/cn-k12-dxyc2286/issues/new)。

## 参考

- 教育部《义务教育课程方案和各学科课程标准（2022年版2025年修订）》
- 教育部《普通高中课程方案和学科课程标准（2017年版2025年修订）》
- [cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy) — 数学/英语/物理知识图谱参考项目（节点结构、诊断引擎与页面组织均参考该项目）
