# physics-bsd-lcm 建桶断点（北师大版·李春密·初中物理）

更新：2026-11-06 20:55

## 已完成
1. **教材来源**：`~/Desktop/中小学教材/中小学教材/物理/初中/北师大版（李春密）/`
   - 20 份大单元 docx（八全一册 11 章 / 九全一册 9 章）
   - 2 份教材 PDF（八全一册 296 页 / 九全一册 220 页，**扫描件**）
2. **OCR**：`/tmp/plcm/ocr8|ocr9/pages/` → 文本包已落桶：
   `data/physics-bsd-lcm/_text/{八年级全一册,九年级全一册}/{整册全文.txt,pages/}`
   汉字数 104,481 / 80,547。
3. **结构**：`data/physics-bsd-lcm/_outline.json`（教材目录 OCR ＋ docx 课时数互证）
   **20 章 / 81 节 / 164 课时**（八：11 章 45 节 92 课时；九：9 章 36 节 72 课时）
4. **骨架**：`topics.json` 101 点（20 unit ＋ 81 lesson）／`dependencies.json` 61 边／`_skeleton.json`
   课标挂标 101/101，`quote` 对课标 TXT 严格回表 0 失配；`scripts/validate.py physics-bsd-lcm` 0 error。
5. **题库分片**：`_bank_shards/PLCM_C01..C20.json`（748 题槽 = 81×8 + 20×5）
   已 PASS：C13（声现象 21 题）、C03（欧姆定律 37 题，待复验）；其余 18 片在跑。
6. **学层分片**：`_learn_shards/PLCM_L01..L20.json`（81 篇）；L13、L03 试跑中。
7. **脚本**：`scripts/check_plcm_bank.py` / `merge_plcm_bank.py` / `gen_plcm_bank_shards.py` /
   `check_plcm_learn.py` / `gen_plcm_learn_shards.py`
8. **注册**：`data/schema-topic.json` enum 已加 `physics-bsd-lcm`；`build_subjects_registry.py` 的
   `EDITIONS` 已加「北师大版·李春密」。**尚未**重建 subject-groups / subjects / dist。

## 待办（按顺序）
1. ~~收题库 20 片 → merge~~ ✅ 2026-11-06 21:40：748 题、20/20 片 PASS、跨片查重 0；
   修了三处：`stem/analysis`→`prompt/explanation`、numeric 答案转字符串、选择题答案位均衡（A96/B95/C60/D52）。
2. ~~学层 81 篇~~ ✅ 21:55：20 片全 PASS，合并 `learn/八年级全一册.json`(45) + `learn/九年级全一册.json`(36)，
   汉字 187,315（篇均 2,313，1,822–2,598）。
3. **卷 28**：作业单已生成 `_exam_spec/PLCM_E01..E28.json`；`check_plcm_exam.py` 已克隆就绪；
   E01（第1章）与 E12（八上期中 A）试写中，过闸后放余 26 份。
4. 讲解 28 份 → `exam_lectures/<册>/<卷名>.json`；`check_exam_lecture.py --subject physics-bsd-lcm`
5. 站点：`build_learn_site.py` / `build_exam_index.py` / `build_exam_lecture_site_v2.py` /
   `build_subjects_registry.py` / `bash scripts/build-dist.sh`
6. docx 交付（学层 81 ＋ 卷 28×2 ＋ 讲解 28 ＋ 合订本）
7. CI `validate-physics-bsd-lcm.yml`；`git add` 后重建注册表

## 口径备忘
- `semester` 全一册统一 `上`；`grade` 8/9；`domain` 四领域：物质 / 运动和相互作用 / 能量（跨学科实践节归入所属章领域）。
- lesson `chapter` 形如「八年级全一册 第1章 热现象 · 第1节 温度及其测量」；unit 不带 ` · `。
- 学层七段标题必须含 checker 关键词：开场 / 课本原文 / 费曼翻译 / 例题 / 易错 / 五步学习法 / 自查。
- 课标引文只能取 `2025修订课程标准TXT /义务教育/7.…物理…txt`，逐字不改 OCR 错字。

## 完结记录（2026-11-07 09:20）
- 题库 748 题（20/20 片 PASS，跨片查重 0）｜学层 81 篇（187,315 汉字，2 册合并件 PASS）
- 卷 28 份（20 单元 + 4×2 期中期末，24 题/120 分/120 分钟，28/28 PASS）
- 讲解 28 份（4000–7800 汉字，28/28 PASS）
- 站点：learn/index.json（八全 45、九全 36 课时）、learn/exam/index.json（15+13 卷）、
  diagnose/exam-index.json（28 卷）、data/subject-groups.json（物理 9 版，本桶 101 点/748 题）、
  `bash scripts/build-dist.sh` 已跑（dist 含 data/physics-bsd-lcm/** 与 learn/exam/data/physics-bsd-lcm-*.json）
- docx：学层 81 + 合订 2；试卷 56（28×2）+ 合订 2 + 答案合订 2；讲解 28 + 合订 2
- CI：`.github/workflows/validate-physics-bsd-lcm.yml`（validate + 桶不变量 + 四层逐件闸门）
- 桶级门禁：`scripts/test_physics_bsd_lcm.py` 21/21 通过
- 本轮修掉的错：① `build_exam_index.py` 的 SUBJECTS/SUBJECT_EDITION 缺本桶（整卷索引会 0 卷）；
  ② `build_learn_site.py` 不认「全一册」（stage 被判成高中、grade=99）；③ merge 的 stem/analysis 字段、
  numeric 答案非字符串、答案位失衡（D 7.6%）。
- 未做：`git push`（Pages）与腾讯云主站部署（需用户点头）。
