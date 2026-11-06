# 物理 · 鲁科版（高中）知识图谱桶 `physics-luke`

> 结构源：`~/Desktop/中小学教材/高中教材/高中物理/鲁科版/` 的 6 册真实教材 PDF（均有文字层）+ 32 份大单元 docx（提供章-课时表）。
> ⚠️ 另一路径 `中小学教材/物理/高中/鲁科版/` 的 6 个 PDF **有错标**（「必修第二册」实为选必二、「必修第三册」实为选必三内容），不要作为结构源。

## 规模（数据层已交付）

| 项 | 数值 |
|---|---|
| 册 | 6（必修第一/二/三册、选择性必修第一/二/三册） |
| 章（单元点 `level=unit`） | 32 |
| 节（课时点 `level=lesson`） | 126 |
| 知识点合计 | **158** |
| 先修边 | 120（同章成链 + 跨章接链；`prereqUpper` 表达章-节归属，不建 unit→lesson 边） |
| 诊断题 | **1168**（课时点 8 题、单元点 5 题） |
| 题/点 | 7.4（参照语文 7.3） |
| 课标挂标 | 158/158（quote 逐字回表 100%，条目池 `data/_phys2017_items.json`，67 个条目 id） |

分册：必修一 25 点/185 题、必修二 23/169、必修三 33/246、选必一 27/201、选必二 21/153、选必三 29/214。

## 口径

- 册 → 年级学期：必修一 10 上、必修二 10 下、必修三 11 上、选必一 11 下、选必二 12 上、选必三 12 下。
- 领域（高中物理五领域）：力学 12 章、电磁学 10 章、热学 4 章、光学 2 章、近代物理 4 章。
  - 必修二第5章「科学进步无止境」→ 近代物理；必修三第6章「能源与可持续发展」→ 热学。
- `chapter`：单元点 `必修第一册 第1章 运动的描述`；课时点同串 + ` · 第N节 X`。
- id：单元点 `plk_u001…plk_u032`、课时点 `plk_l001…plk_l126`；题目 `plk_q00001…plk_q01168`（父级统一分配，禁子代理自编）。
- 题型构成：choice 442 / fill 284 / numeric 284 / short-answer 158；难度 basic 432 / standard 455 / hard 281；
  选择题答案位 A/B/C/D = 25.1/25.1/24.9/24.9%（≥15% 闸门）。

## 门禁

```bash
env -u PYTHONPATH /usr/bin/python3 scripts/test_physics-luke.py        # 26/26 通过
npx ajv-cli@5 validate -c ajv-formats -s data/schema-topic.json -d data/physics-luke/topics.json
npx ajv-cli@5 validate -c ajv-formats -s data/schema-question.json -d data/physics-luke/questions.json
env -u PYTHONPATH /usr/bin/python3 scripts/validate.py physics-luke    # 0 error
env -u PYTHONPATH /usr/bin/python3 scripts/check_physics-luke_exam.py --all      # 56 卷 · 不合格 0
env -u PYTHONPATH /usr/bin/python3 scripts/check_physics-luke_learn.py --dir data/physics-luke/learn
env -u PYTHONPATH /usr/bin/python3 scripts/check_exam_lecture.py --subject physics-luke
env -u PYTHONPATH /usr/bin/python3 /tmp/plk/dup_audit.py                         # 跨卷查重（0 配对）
```

## 已交付层（数据层 + 试卷 + 学层）

| 层 | 规模 | 口径 |
|---|---|---|
| 知识点 | 158（32 单元 + 126 课时） | 五领域；`prereqUpper` 表达章-节归属 |
| 诊断题 | 1168 | 课时点 8 题 / 单元点 5 题；答案位 A/B/C/D ≈ 25% |
| 先修边 | 120 | 同章成链 + 跨章接链 |
| **试卷** | **56 卷 / 1344 题** | 高中 150 分 / 150 分钟 / 24 题＝选择 18×3 + 综合 6×16；期中＝前 ⌈n/2⌉ 章、期末＝全册 |
| **学层精讲** | **126 篇 / 224,740 汉字** | 六册 `learn/<册>.json`；七段式 1200–2800 字（中位 1789）|
| **试卷讲解** | **56 份 / 356,709 汉字** | 六段式 4500–8800 字（中位 6262，最短 5286 / 最长 8119）|
| 教材目录 | 6 册 `ke_toc/`（158 条，全部挂 topicId）+ 6 册文本包 | 印刷页口径，与图谱 1:1 |
| 站点注册 | learn 6 册 / 讲解 6 册 56 卷 / diagnose 56 卷 | `merge_bucket_site_index.py --bucket physics-luke` |

## docx 交付（`~/Desktop/学科图谱相关资料/`）

| 交付件 | 数量 | 路径 |
|---|---|---|
| 试卷（原卷 + 参考答案与评分标准） | 56 × 2 = 112 | `学科图谱原创试卷/物理/鲁科版/<册>/` |
| 学层精讲（学生打印版） | 126 | `学层精讲/物理/鲁科版/<册>/` |
| 试卷讲解 | 56 | `试卷讲解/物理/鲁科版/<册>/` |
| 讲解合订本（封面+目录+连续页码） | 6（9/9/10/9/9/10 份） | `试卷讲解/物理/鲁科版/<册>/_合订本/` |

渲染入口（学科名必须显式给，否则会按默认「数学」落盘）：
```bash
SUBJECT_NAME=物理 MATH_BUCKET=physics-luke MATH_EDITION=鲁科版 \
  python3 scripts/build_math_exam_docx.py        # 试卷 ×2
SUBJECT_NAME=物理 MATH_BUCKET=physics-luke MATH_EDITION=鲁科版 \
  python3 scripts/build_math_learn_docx.py       # 学层
SUBJECT_NAME=物理 MATH_BUCKET=physics-luke MATH_EDITION=鲁科版 \
  python3 scripts/build_exam_lecture_docx.py     # 讲解
SUBJECT_NAME=物理 MATH_BUCKET=physics-luke MATH_EDITION=鲁科版 \
  python3 scripts/build_exam_lecture_booklet.py <册>   # 合订本（逐册）
```

## 待建

1. **`build-dist.sh`** 打包上线（数据层已注册进三份站点索引）。
2. 遗留：3 篇物理讲解的五步标签为「八个固定标签」表述由工位自述，实际闸门只查五个，已通过；
   后续若统一口径需回刷 `check_exam_lecture.py` 的 STEPS 与正文措辞。

