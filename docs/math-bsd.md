# 数学（北师大版，`math-bsd`）

北师大版数学知识图谱。与「数学（`math`，人教版）」并列的**独立学科**：`subject` 不同、
`id` 前缀不同（`mbs_`），页面按学科切换即可，两版互不干扰。
教材口径：小学 12 册（一上～六下）＋ 初中 5 册（七上～九上）＋ 高中 4 册（必修一/二、选必一/二）。

## 1. 当前规模（以 `topics.json` / `questions.json` 现算为准）

| 项目 | 数量 | 说明 |
| --- | ---: | --- |
| 知识点 | 1317 | 单元点 132（小学 84 ＋ 初高中 48，展示用）＋ 课时点 1179（一课时一点） |
| 先修边 | 1051+ | 同单元课时顺次 `hard` ＋ 册际衔接 `soft` |
| 诊断题 | 10122 | 每课时点 **8 题**（4916 小学 ＋ 4936 初高中）＋ 单元点 5 题（270），四题型三档齐 |
| 试卷 | 219 | 小学 132（84 单元＋48 期中期末）＋ 初高中 87（51 单元＋36 期中期末） |
| 试卷讲解 | 219 | 与试卷 1:1（全量 checker 不合格 0） |
| 学层精讲 | 1179 | 21 册课时点全覆盖（1179/1179，逐册 checker 全 PASS） |

**分学段覆盖**

| 学段 | 册 | 知识点 | 诊断题 | 学层 | 试卷 | 讲解 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 小学 | 12 | 646（单元 84 ＋ 课时 562） | 4916＋420 | 562 | 132 | 132 |
| 初中 | 5 | 444（单元 48 分册里 30＋课时 396） | 3168＋150 | 396 | 56 | 56 |
| 高中 | 4 | 227（单元 18＋课时 221） | 1768＋90 | 221 | 31 | 31 |

## 2. 口径（与 `data/math` 人教版一致）

1. **一个教材课时 = 一个知识点**（课时级）；习题课、巩固练习、回顾与思考、单元整理不成点
   （建库时已剔除 51 条，见 `scripts/build_bsd_skeleton.py` 的 `SKIP_LESSON`）。
2. `chapter` = `<册> 第<中文>单元/章 <单元名>`，页面册名从 `chapter` 首段派生；
   `grade` 1–6（小学）、7–9（初中）、必修一=10 / 必修二=11 / 选必一=12 / 选必二=13（高中）；
   `semester` 上册=上、下册=下。
3. `domain` 只用课标四领域（数与代数 / 图形与几何 / 统计与概率 / 综合与实践）；
   关键词规则覆盖不到的单元用 `UNIT_DOMAIN_OVERRIDE` 人工裁定（如「整理与分类」→统计与概率、
   「测量（一）(二)」→图形与几何）。
4. 题库：每课时点 8 题、单元点 5 题；`choice/fill/numeric/short-answer` 四类齐备，`numeric` 的 `verify`
   必须可 `eval` 复算且等于 `answer`，答案位 A/B/C/D 各 ≥15%，题干 ≥12 字、解析 ≥20 字、全域不重复。
5. 试卷满分：小学 100 分 90 分钟；初中 120 分；高中 150 分（体例见 checker 的 `TEMPLATES`）；
   讲解六段、字数带按学段。

## 3. 结构源（为什么不是「凭印象写单元」）

| 源 | 路径 | 用在哪 |
| --- | --- | --- |
| 分课时教学设计 docx（权威） | `中小学教材/各学科分课时设计/数学/北师大版/<学段>/<册>/` | 文件名自带「第N单元 X·第K课时 名」与「全册共N课时」；上册 6 册（小学）＋ 3 册（初中） |
| 大单元整体教学设计 docx（兜底） | `1.0标准合集/小学数学/北师大版小学数学大单元整体教学设计`（83 份）、`中小学教材/数学/<学段>/北师大版/大单元整体教学设计` | 取「十五、教-学-评一致性课时设计」段的课时名，覆盖全部 21 册（含下册） |
| 教材 PDF | `中小学教材/数学/<学段>/北师大版/*.pdf` | 正文核对；小学 9 册、初中 5 册、高中 4 册有 PDF（四上/五上/六上/九上/高中四册有文字层，其余为扫描版） |
| **教材 textpack（永久）** | `精准提取各学科教材TXT文档/数学/北师大版/<学段>/<册>/{ocr/pNNN.txt, 整册全文.txt}` | 学层引文回表。产出器 `scripts/make_bsd_textpack.py`：文字层直转、扫描件 tesseract OCR。已落：九年级上册＋高中 4 册（文字层）、七上/七下/八上/八下（OCR） |

对账（`scripts/scan_bsd_structure.py` 打印）：册级「各单元课时之和 vs 分课时 docx 声明的全册课时」、
单元级「解析条数 vs（共M课时）」、单元号 1..N 连续性。

## 4. 课标引文口径（重要：不用 OCR 版）

- 引文源＝`…/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订)（docx转换）.txt`
  （由官方 **docx** 直接转换，100 684 字符）。
- ⛔ **不要用同目录的 OCR 版 TXT**：它把「减法」识别成「袜法」、「熟练」→「郊练」、「时间」→「时问」，
  引文会带错字。人教版 `math` 的旧引文回表用的就是 OCR 版，属历史遗留，不在本学科沿用。
- 引文库在 `scripts/attach_bsd_std.py` 里**人工裁定**，每条都做「去空白后必须是课标原文子串」自检：
  - 义务教育 **第一学段（1–2 年级）9 条**、**第四学段（7–9 年级）45 条**，源＝上面那份 docx 转换文本；
  - 高中 **37 条**，源＝`…/2025修订课程标准TXT /高中教育/（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt`。
- 知识点按「课时名 + 单元名」的规则表 `RULES1 / RULES4 / RULESH` 归条：规则命中且**领域一致**判 `partial`，
  兜底判 `inferred`。`standards.id` 形如 `mbs-2022:4.SD.07`（义教第四学段）、`mbs-2017:H.TX.07`（高中）。
  当前覆盖：初中 366/396 `partial`（30 兜底）、高中 185/221 `partial`（36 兜底）。
- 第二、三学段（3–6 年级）不在本脚本口径内（小学归并行工位），遇 grade 3–6 直接跳过、不动其 `standards`。
- **学层引文的回表源＝永久 textpack**：`check_math_bsd_learn.py` 先读 `<TXT_ROOT>/<学段>/<册>/`，
  `/tmp` 只作历史回退。某册缺 textpack 时 checker 会打印「教材 TXT 不在本机，跳过课本原文回表」，
  等于该册引文未受校验——**收口前必须逐册确认回表源在位**。

## 5. 已知缺口（按优先级）

1. ~~初高中文案层未做~~ → **已完成**：初高中学层 617 篇、试卷 87 卷、讲解 87 份全部落盘并通过 checker。
2. **初高中无单元点**（`level=unit`）：小学有 84 个；初高中出单元卷前需按 `chapter` 聚合补建。
3. **九下无结构源**：北师大版九年级下册既无分课时 docx 也无大单元 docx（教材 PDF 也缺），
   需新教材到位后再建。九上第五单元是**二次函数**（PDF 目录已核），反比例函数属九下，
   相关题目暂存 `data/math-bsd/_orphan/`。
4. **小学 textpack 未逐册生成**：9 册有 PDF（四下/五下/六下无 PDF，只能以 docx 结构源为准），
   生成后小学 562 篇学层的引文才会真正受回表校验。
5. **交付件已出齐**：学层精讲 1179 篇 ＋ 21 册合订本；原创试卷 219 卷 × 2（试卷＋参考答案）＋ 21 册两份合订本；试卷讲解 219 份。

## 6. 自检与工具

```bash
python3 scripts/validate.py math-bsd                  # 结构/引用
python3 scripts/test_math_bsd.py                      # 48 项不变量（quote 回表；无 TXT 时跳过）
python3 scripts/scan_bsd_structure.py --stage 小学    # 结构盘点与三重对账
python3 scripts/build_bsd_skeleton.py --stage 小学 --scan /tmp/bsd_小学.json \
        --out data/math-bsd/_skeleton_小学.json      # 骨架重建
python3 scripts/check_bsd_bank.py <spec> <bank>       # 单个题库分片
python3 scripts/check_math_bsd_learn.py data/math-bsd/learn/<册>.json   # 学层逐册
python3 scripts/check_math_bsd_exam.py "<卷.json>"    # 试卷逐卷
python3 scripts/check_math_bsd_lecture.py             # 讲解全量
python3 scripts/merge_bsd_bank.py                     # 合并 _bank → topics/questions
python3 scripts/gen_bsd_learn_shards.py --books <册…> --per-shard 6     # 学层派单（初高中）
python3 scripts/make_bsd_textpack.py --books <册…> [--ocr]              # 教材 textpack
MATH_BUCKET=math-bsd MATH_EDITION=北师大版 python3 scripts/build_math_learn_docx.py      # 学层 docx
MATH_BUCKET=math-bsd MATH_EDITION=北师大版 python3 scripts/build_math_learn_booklet.py   # 学层合订本
```

## 7. 页面用法

- 学科下拉「📐 数学」，版本为其二级分支（`data/subject-groups.json` 里 `math` 组下的「北师大版」）；
  册次下拉从 `chapter` 派生。
- 深链：`explore/?subject=math-bsd&book=一年级上册#mbs_p001`。

## 验收状态（2026-11）

| 闸门 | 判据 | 现状 |
|---|---|---|
| 库不变式 | `python3 scripts/test_math_bsd.py` | 48/48 通过 |
| 卷面结构 | `check_math_bsd_exam.py --no-dup <卷>`（219 卷） | 全部 PASS |
| 原创性 | `scan_bsd_exam_dupes.py --min 0.85` | 219 卷命中 **0 处**（曾 10 处，已改写） |
| 学层 | `check_math_bsd_learn.py <册>`（21 册） | 1179 篇全 PASS |
| 讲解 | `check_math_bsd_lecture.py`（全量） | 219 份 · 不合格 0 |
| CI | `.github/workflows/validate-math-bsd.yml` | 六步全绿 |

**已交付成品**：学层精讲 1179 篇 ＋ 21 册合订本；原创试卷 219 卷 × 2（试卷·参考答案与评分标准）＋ 21 册两份合订本；试卷讲解 219 份 ＋ 21 册合订本。位置见文首目录约定。

**唯一库级缺口**：九年级下册 —— 教材 PDF、分课时设计、大单元设计三样源件均无，无法开工（不是漏做）。
