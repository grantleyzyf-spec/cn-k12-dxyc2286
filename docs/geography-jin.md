# 地理（晋教版·山西教育出版社·初中）— 知识图谱桶 `geography-jin`

> 参照标准：**语文桶（`data/chinese`）走通的全链路完整度** —— 点 / 题 / 卷 / 学层 / 讲解 / 站点 / docx / CI 八层齐，
> 不照抄它的人文科学口径（地理按义教地理四领域与初中卷面模板）。
> 与本文件同步维护的门禁：`scripts/test_geo_jin.py`、`check_geo_jin_points.py`、`check_geo_jin_bank.py`、
> `check_geo_jin_exam.py`、`check_geo_jin_learn.py`、`scripts/check_exam_lecture.py --subject geography-jin`。

## 一、范围（教材决定，不是缺口）

晋教版（山西教育出版社，主编 林培英／安祥生，本册主编 杨光）**只有初中四册**：

| 册 | 主题（单元） | 课时 | grade |
|---|---|---|---|
| 七年级上册 | 主题一 探寻人类的太空家园 / 主题二 模拟地球运动 / 主题三 探索地球海陆面貌 / 主题四 寻找地球上的居住地 | 32 | 7 |
| 七年级下册 | 主题五 探究大洲地理特征 / 主题六 探寻"一带一路"沿线地区 / 主题七 认识国家发展差异 / 主题八 共谋区域发展与合作 | 32 | 7 |
| 八年级上册 | 主题一 探知中国版图与自然环境 / 主题二 探讨中国人口与自然资源 / 主题三 探寻中国工农业与交通运输业 / 主题四 探究中国的大河与生态 | 32 | 8 |
| 八年级下册 | 主题五 描绘北京图景 / 主题六 探秘一方水土一方人 / 主题七 探寻区域联系与合作发展 / 主题八 走进家乡 | 32 | 8 |

合计 **16 个主题 / 128 课时 / 144 个知识点**（16 单元点 ＋ 128 课时点）。
晋教版不出小学与高中地理教材 ⇒ 这两学段**不在本桶范围**。

## 二、结构源（三级，本桶实际用到前两级）

1. **分课时教学设计 docx**（七上、八上各 37 份，文件名片名自带「主题X <主题名>·第N课时 <课时名>」）——最可靠。
2. **大单元整体教学设计 docx**（四册 16 份齐全）：取「十五、'教-学-评'一致性课时设计」段里的
   `（一）第一课时：<课时名>` 列表 —— 用于七下、八下（这两册没有分课时 docx）。
3. 教材 PDF 目录 —— 只作核对。

抽取脚本：`scripts/build_geo_jin_outline.py` → `data/geography-jin/_outline.json`（16 主题 × 8 课时，无缺号）。

## 三、教材文本包（学层引文回表的唯一权威源）

`~/Desktop/中小学教材/中小学教材/精准提取各学科教材TXT文档/地理/晋教版/初中/<册>/`
- `整册全文.txt`（全册逐页拼接，已去排版空格）
- `ocr/pNNN.txt`（逐页；名沿惯例保留 `ocr/` 前缀，实为 PDF **文字层**直转）

四册实测：129 / 129 / 133 / 117 页，28 451–31 696 汉字，**PDF 有文字层（InDesign 出品），无需 OCR**。
生成脚本：`scripts/make_geo_jin_textpack.py`。

## 四、口径（五条，改前先看 SKILL §3）

1. **编号**：单元点 `gjin_u0NN`、课时点 `gjin_j0NN`，按「册 → 主题号 → 课时号」连续分配；`examId` 前缀按册
   `j7a/j7b/j8a/j8b`，单元卷 `_u0N`（N＝主题号），期中期末 `_mid_a/_mid_b/_fin_a/_fin_b`。
2. **chapter**：单元点 = `<册> 主题X <主题名>`；课时点 = 同上 ＋ ` · 第N课时 <课时名>`。
   卷面 `scope` 匹配必须是 `chapter == sc or chapter.startswith(sc + " · ")`，等值比较会让覆盖审计变假齐。
3. **领域**：只用**义教地理**四领域 —— 地球与地图（七上主题一/二/三）、世界地理（七上主题四、七下四主题）、
   中国地理（八上四主题、八下主题五/六/七）、乡土地理（八下主题八）。
   ⛔ 不用高中四领域，⛔ 不用「地球与宇宙」「地图与地理工具」这类自造名（`data/geography` 桶的历史病）。
4. **题量**：课时点 **恰好 8 题**、单元点 **恰好 5 题**；每点三档齐（basic/standard/hard）。
   配方：课时 1–4 = 5 choice ＋ 2 fill ＋ 1 short ；课时 5–8 = 4 choice ＋ 2 fill ＋ 1 short ＋ 1 numeric；
   单元点 = 2 choice ＋ 1 fill ＋ 1 numeric ＋ 1 short。全库 1104 题。
5. **卷面**：初中地理 **120 分 / 120 分钟 / 24 题** —— 选择题 18×3＝54，综合题 6×11＝66；
   单元卷必须覆盖本主题全部 8 个课时点各 ≥1 次。全库 **32 卷** = 16 单元卷 ＋ 4 册 × 4（期中 A/B、期末 A/B）。

## 五、规模（实测）

| 项 | 数 |
|---|---|
| 知识点 | 144（单元 16 ＋ 课时 128） |
| 诊断题 | 1104（choice 608 / fill 272 / short-answer 144 / numeric 80；basic 416 / standard 544 / hard 144） |
| 先修边 | 127（课时链，hard；`prerequisites` 镜像同源） |
| 课标挂标 | 144/144，quote 逐字回表 100%（exact 60 / partial 70 / inferred 14，用到 39 条条目） |
| 试卷 | 32 卷 |
| 学层精讲 | 128 篇 |
| 试卷讲解 | 32 份 |

## 六、放量节奏（本次实测）

| 波次 | 片数 | 内容 | 结果 |
|---|---|---|---|
| 第 1 波 | 16（T01–T16，一主题一片） | 9 点内容 ＋ 69 题 | 16/16 两个 checker PASS，1104 题一次到位 |
| 第 2 波 | 8（E01–E08，一册一片） | 32 卷 | 见交付记录 |
| 第 3 波 | 16（L01–L16，一主题一片） | 128 篇学层 | 见交付记录 |
| 第 4 波 | 4（K01–K04，一册一片） | 32 份讲解 | 见交付记录 |

## 七、门禁命令

```bash
python3 scripts/test_geo_jin.py                                   # 库不变式（34 项）
python3 scripts/check_geo_jin_points.py data/geography-jin/_points/T01.json
python3 scripts/check_geo_jin_bank.py --all                       # 16 片 1104 题
python3 scripts/check_geo_jin_exam.py --all                       # 32 卷
python3 scripts/check_geo_jin_learn.py --dir data/geography-jin/learn/_parts
python3 scripts/check_exam_lecture.py --subject geography-jin     # 32 份讲解
```

CI：`.github/workflows/validate-geography-jin.yml`（不变式 → itemId → 逐卷 → 学层逐册 → 讲解逐份）。

## 八、已知边界与缺口

1. **七下、八下没有分课时 docx** —— 结构取自大单元 docx 的「十五」段，与教材目录已核对一致；
   若日后补齐分课时 docx，应重跑 `build_geo_jin_outline.py` 比对课时名。
2. **课标挂标是跨版本借标**（同一份《义务教育地理课程标准（2022 年版 2025 年修订）》，与教材版本无关），
   台账见 `data/_std_waivers.json` 的 `geography-jin` 键；14 个 inferred 点是复习/实践类课时，语义只到主题级。
3. **无小学、无高中**：晋教版不出这两学段教材，属教材侧边界，不是本桶缺口。
