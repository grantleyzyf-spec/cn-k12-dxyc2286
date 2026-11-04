# 历史学科桶（data/history）断点续跑

**状态时间**：2026-11-04 09:0x（波峰前停下）。用户令：**12:00 波谷再启动**。

## 已完成（全部有门禁实跑）
| 层 | 量 | 校验 |
|---|---|---|
| 知识点 | 224（11 册，全课级点） | `validate.py history` 0 错；`test_history.py` 35/35 |
| 题库 | 1792（每点恰好 8 题，全 choice） | `check_history_bank.py --all --strict` PASSED（**存量不合规 0 项**，2026-11-04 12:30 清零） |
| 试卷 | 117（73 单元＋22 期中＋22 期末） | 逐卷 `check_history_exam.py` 117/117 PASS |
| 期中卷返修 | 22 卷 scope 已改「前半册」 | 0 卷越界；mid 与 fin 覆盖集合已不同 |
| 学层 | 224 篇 / 11 册 | 56 片逐片 PASS（含引文回表 0 失配）；合并件 11 册 0 不合格 |
| 讲解 | 117 份 / 11 册 | 117/117 PASS；与卷 1:1 无缺无余 |
| 站点 | 学层索引 11 册 224 课时；讲解索引 11 册 117 卷；整卷索引 117 卷 | `dist` 已构建（201M / 2516 文件） |

**上线**：第一次推送已把 `data/history/exams` 117 卷推到远端（commit c20e3a1，抽查七上期中 A scope=前半册 ✓）。
第二次推送（learn/讲解/索引，349 件）在波峰前已发，**未完成则先核远端**：
```bash
gh api repos/grantleyzyf-spec/cn-k12-dxyc2286/git/trees/main?recursive=1 \
  --jq '[.tree[]|select(.path|startswith("data/history/exam_lectures/"))|select(.type=="blob")]|length'   # 期望 117
```

## 待办（按顺序做）
1. ~~**推送收尾核验**~~ ✅ 2026-11-04 12:10 已核：远端 `data/history/learn/*.json`=11、`exam_lectures/*.json`=117（另有 2 个杂散 `.md`）、`learn/exam/data/history-*.json`=11、`exams/*.json`=117，全部齐。
   ```bash
   /usr/bin/python3 ~/.hermes/profiles/agent11/skills/writing/cn-k12-knowledge-graph-build/scripts/push_prefix_robust.py \
     --repo grantleyzyf-spec/cn-k12-dxyc2286 \
     --prefix data/history/learn data/history/exam_lectures data/history/_lecture_shards \
              learn/index.json learn/exam/index.json learn/exam/data diagnose/exam-index.json \
              scripts/verify_history_quotes.py scripts/merge_history_learn.py \
     --message "feat(history): 学层 224 篇 + 讲解 117 份 + 索引同步"
   ```
2. **题库存量不合规 12 项**（`check_history_bank.py --all` 列「解析不足 20 汉字／题干不足 12 字」）：就地补解析/题干，⛔ 不重派；改完 `test_history.py` 与 bank 双跑。
3. **课标 OCR 讹字（真数据缺陷）**：`data/cn-curriculum-standards.json` 历史段的 `quote` 带错字（商蒜→商鞅、郧县人人、良清／陶村→良渚／陶寺、神话传阅、政权更欠→更迭、威继光→戚继光、拿破仓→拿破仑、南各大屠杀）。改字会让学层「逐字回表」全红 ⇒ 正确顺序：先用**docx 直转的课标文本**替换该段 txt 源 → 重挂 quote → 用 `scripts/verify_history_quotes.py` 全量复跑 224 篇（期望失配 0）。
4. **docx 交付（阶段 8，尚未开始）**：学层 224 篇 / 讲解 117 份 / 试卷 117×2 / 合订本 4 类，落 `~/Desktop/学科图谱相关资料/历史/`；用 `scripts/build_math_learn_booklet.py` 等参数化生成器（`MATH_BUCKET=history MATH_EDITION=统编版 SUBJECT_NAME=历史`），⛔ 不克隆新脚本。
5. **题型扩容（可选，需用户确认）**：现全 choice、0 条 `verify`；要上 fill/numeric/short 必须先改 `test_history.py` 的「答案位均衡」断言口径（只统计 `type=='choice'`），否则整库必红。
6. **教材缺口**：九年级下册 PDF 教材库里**没有**，该册 14 篇学层引文全部走课标语（已在派单与汇报里注明）；若要补真引文，需要先找到九下 PDF。

## 复跑全部门禁
```bash
cd ~/Desktop/cn-k12-dxyc2286
/usr/bin/python3 scripts/validate.py history
/usr/bin/python3 scripts/test_history.py
/usr/bin/python3 scripts/check_history_bank.py --all
while IFS= read -r x; do /usr/bin/python3 scripts/check_history_exam.py "$x" | tail -1; done < <(find data/history/exams -name '*.json' -print)
while IFS= read -r x; do /usr/bin/python3 scripts/check_history_learn.py "$x" | tail -1; /usr/bin/python3 scripts/verify_history_quotes.py "$x" | tail -1; done < <(find data/history/learn -maxdepth 1 -name '*.json' -print)
while IFS= read -r x; do /usr/bin/python3 scripts/check_exam_lecture.py "$x" --subject history | tail -1; done < <(find data/history/exam_lectures -name '*.json' -print)
```

## 口径备忘
- 学层合并器按**每课自己的 `book`** 归册（已改；按分片 book 会错册）。
- 学层 checker 要求「≥1 处引文逐字等于课标 quote」，故每篇引文结构＝1 课标语＋2 教材原文；`verify_history_quotes.py` 双源判定（教材 txt 或课标 quote）。
- 期中卷规范：scope＝该册**前半册**（前 ceil(n/2) 个单元），期末＝全册。
- `_mid_backup/` 已移出仓库，旧卷在 `~/Desktop/学科图谱相关资料/历史_期中卷旧版/`；教材文本在 `~/Desktop/学科图谱相关资料/历史_教材文本/`。

## 2026-11-04 12:00 波谷续跑（本轮已完成）

1. **远端核验通过**（未重推）：learn 11 / exam_lectures 117 / learn-exam-data 11 / exams 117。远端 `data/history/exam_lectures/中外历史纲要（上）/` 下多出 2 个无引用杂散文件：`第三单元测试卷.md`、`第九单元测试卷.md`（不在任何索引中，不影响站点）。
2. **题库存量不合规 87 项 → 0**（HANDOFF 原记「12 项」是检查器只打印前 12 条的错觉；真实为题干<12 字 21 处 ＋ 解析<20 汉字 66 处，涉及 75 题）。
   就地改 `prompt`/`explanation`，并**同步 `question` 别名字段**（漏同步会新红「question 别名与 prompt 不同值」）。answer/options/id 一律未动。
   验证：`test_history.py` 35/35、`check_history_bank.py --all --strict` PASSED 且「存量题硬约束」计数 0、117 卷逐卷「不合格 0」、`validate.py history` 0 错。
3. **课标 OCR 讹字已根治**：课标 txt 源（`~/Desktop/中小学教材/2025修订课程标准TXT /{义务教育,高中教育}/历史*.txt`）本是 OCR 件，
   已用教材库 **docx 直转文本**整篇替换（原件留 `.ocr.bak`）；`data/history` 内 10 类讹字共 70 处就地更正
   （商蒜→商鞅、良清→良渚、陶村→陶寺、郧县人人→郧县人、神话传阅→神话传说、政权更欠→政权更迭、威继光→戚继光、
   拿破仓→拿破仑、南各大屠杀→南京大屠杀、**玄装→玄奘**（原 HANDOFF 未列）），涉及 topics 14 处 ＋ 学层成品 3 册 14 处 ＋ 分片/parts 42 处。
   验证：245 条 quote 对新源**逐字回表 0 失配**；11 册学层 `check_history_learn.py` 全 PASS、`verify_history_quotes.py` 引文 673 处失配 0（九下仍走课标退路）。
   ⚠️ 学层 `words` 已按新文本重算（净变化仅七上 1 篇）。
4. 余下待办不变：**docx 交付（阶段 8）**、题型扩容（需先改 `test_history.py` 答案位断言口径）、九下教材 PDF 缺口、聚合发布（`publish_aggregates.py`，本轮未做）。
