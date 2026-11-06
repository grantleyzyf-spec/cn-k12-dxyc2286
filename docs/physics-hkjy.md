# 沪科教版（高中物理）知识图谱桶 · `physics-hkjy`

## 范围与结构源
- 教材：`中小学教材/物理/高中/沪科教版/` 六册（必修第一/二/三册、选择性必修第一/二/三册）。
- 结构源：各册 PDF 目录页（p4–p5）逐条抄录，**31 章 / 129 节**。
- 建点口径：章＝`unit`（31 个）、节＝`lesson`（129 个）；开篇（0.1–0.3）、总结与评价、研究课题示例、评价表**不建点**。
- id 前缀：章 `phk_u001–u031`、节 `phk_j001–j129`；先修边 128 条（每册链式，册间不跨）。
- 领域分布：力学 62 / 电磁学 49 / 热学 22 / 近代物理 19 / 光学 8。

## 规模（对表）
- 点 **160**（31＋129）· 题 **1187** · 试卷 **55 卷**（31 章卷 ＋ 6 册×4 期中期末）
- 题型：选择 578 / 填空 289 / 简答 160 / 数值 160；难度 basic 320 / standard 449 / hard 418
- 每点题量：章点 5 题、节点 8 题（题槽由 `_bank_spec/T*.json` 预分配，工位只填内容）

## 卷制（区别于初中与人文科）
- **150 分 / 90 分钟 / 21 题**：单选 10×3＝30、多选 5×4＝20、实验 2×15＝30、计算 4 题（15+18+18+19）＝70。
- `examId` 形如 `phk_exam_<b1|b2|b3|x1|x2|x3>_<uNN|qza|qzb|qma|qmb>`。

## 门禁
| 层 | 脚本 | 读数 |
|---|---|---|
| 结构 | `scripts/validate.py physics-hkjy` | 0 error |
| 题库 | `scripts/check_phys_hkjy_bank.py --all` | 31 片 / 不合格 0 |
| 试卷 | `scripts/check_phys_hkjy_exam.py --all` | 55 卷 / 不合格 0 |
| 学层 | `scripts/check_phys_hkjy_learn.py --all` | 129 篇 / 不合格 0 |
| 讲解 | `scripts/check_exam_lecture.py --subject physics-hkjy --book <册>` | 逐册 PASS |

## 专用脚本
- `build_phys_hkjy_skeleton.py` —— 从目录抄录生成 `_skeleton.json`（31/129）
- `build_phys_hkjy_bucket.py` —— 生成 `topics.json` 占位 ＋ `_bank_spec/T*.json`（题槽预分配）
- `check_phys_hkjy_bank.py` —— 分片题库/点内容门禁（照抄物理苏科版口径改桶名）
- `gen_phys_hkjy_exam_specs.py` —— 55 卷 spec
- `check_phys_hkjy_exam.py` —— 单卷门禁（结构、覆盖、原创性 <0.85、解答题 scoreRule 求和）
- `check_phys_hkjy_learn.py` / `merge_phys_hkjy_learn.py` —— 学层七段门禁与合并
- `merge_phys_hkjy.py` —— `_points` + `_bank` → `topics.json` + `questions.json`
- `merge_phys_hkjy_lectures.py` —— 讲解合并

## 已知缺口 / 注意
- 教材 PDF 为文字层可直接抽文本（`_text/<册>.txt`，5.0–8.1 万汉字/册，带 `[[pN]]`）。
- 讲解门禁的「数值与单位之间须空一格」会把 `20m/s` 判错，物理稿必须写 `20 m/s`。
- 章卷必须覆盖全章课时点；期中卷章点各 ≥1 题、课时点 ≥80%。
