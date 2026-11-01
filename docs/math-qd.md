# 数学（青岛版，`math-qd`）

青岛版数学按「教材清点 → 骨架 → 课标回表 → 题库 → 自检 → 文档 → 站点 → CI」落地，口径对齐 `k12-subject-closeout` 与 `cn-k12-knowledge-graph-build`。

> 与人教版 `math` 的边界：**人教版是存量学科（19 册 / 1044 点），青岛版是并列的新学科桶**。
> 两者同属义务教育数学课标，青岛版不覆盖高中（青岛版只有 1–9 年级教材），因此没有高中段。

## 1. 教材清点（骨架的唯一来源）

| 项目 | 结果 |
| --- | --- |
| 有原件册次 | **14 册**：小学 9（一上・一下・二上・二下・三上・三下・四上・五上・六上）＋初中 5（七上・七下・八上・八下・九上） |
| 缺教材（不造点） | **4 册**：四年级下册、五年级下册、六年级下册、九年级下册（`~/Desktop/中小学教材/中小学教材/数学/<学段>/青岛版/` 无 PDF） |
| 结构源 | 小学＝大单元整体教学设计 docx 的单元目录 ＋「信息窗」；扫描版册次（一下・二上・二下・四上・五上）以 docx 为准<br>初中＝教材 PDF 目录页（`第1章 有理数` / `1.1 正数和负数`），全部册次有文字层 |
| 单元 / 课时点 | 107 单元 / 265 信息窗・小节（另有 31 个单元教材本身只有单元页，无信息窗，如「创意拼搭」「总复习」「智慧广场」） |

清点产物：`data/math-qd/_inventory.json`（由 `scripts/qd_inventory.py`、`scripts/qd_skeleton_source.py` 生成）。

## 2. 骨架

- **知识点 361**：单元点 106（`level: unit`，展示/上位）＋ 课时点 255（`level: lesson`，可诊断）。
  其中 11 个目录噪声点已剔除（见 §6「骨架清洗」）。
- **id**：`qdm_p001…`，按「册序 → 单元序 → 课时序」连续发号；**只增不改**（二次扩点从最大号续编，否则 `_bank` 里的 `topicId` 全部失联）。
- **chapter**：`<册> 第<中文>单元 <情境名>`；课时点再追加 ` 信息窗N <名>` / ` 第N节 <名>`。页面册名从该前缀派生。
- **先修边 493**：`hard 435`（单元→课时、课内课时顺次）· `soft 58`（册内单元衔接、册际衔接）；镜像回 `prerequisites`，无环、无重复。
- **根节点 107**：每个单元点都是自己子树的根，全部带 `root_reason`。
- **domain**：课标四领域 —— 数与代数 254 · 图形与几何 88 · 综合与实践 17 · 统计与概率 13。
  ⚠️ 关键词判定会把「数据的收集、整理与描述」误判为综合与实践（含「整理」），已把「整理与复习 / 总复习」限定为整词匹配修正。

## 3. 课标回表

- 依据《义务教育数学课程标准（2022 年版 2025 年修订）》本地 TXT（`2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准…》.txt`）。
- 372 条 `quote` **全部来自本库人教版 `math` 的课标条目**（那些条目已在 601/601 回表过），按「同学段 + 知识点名最相似（difflib ≥0.55）」借调，同一条目按 id 复用；`confidence` 一律 `inferred`（**跨教材版本借调，不是逐点人工对齐**），这条口径必须写进文档，避免被当成 `exact` 用。
- 0 条无课标；`quote` 逐字回表由 `scripts/test_math_qd.py` 复核（课标 TXT 缺失时跳过，CI 安全）。

## 4. 题库

| 项目 | 数值 |
| --- | --- |
| 已交题库册次 | **全部 14 册**（361 个知识点 / 2570 题） |
| 题量口径 | 课时点 8 题、单元点 5 题 |
| 难度 | basic 806 · standard 1007 · hard 757 |
| 答案位 | A 652 · B 659 · C 634 · D 625 |
| 题型 | 全部 `choice`（4 选项、真干扰项：多算、少算、符号看错、顺序错、把「比多少」当「合起来」） |
| 分片 | 46 片（`data/math-qd/_bank/S01–S46.json`），每片自带 `_shards/S{NN}/WORKER.md` 派单与 checker |

## 5. 本轮怎么跑出来的

1. `python3 scripts/qd_inventory.py` → 初盘单元/信息窗（发现小学 4 册是扫描版、初中 14 册目录可直读）。
2. `python3 scripts/qd_skeleton_source.py --write` → `_inventory.json`（14 册 / 107 单元 / 265 课时点；缺 4 册登记）。
3. `python3 scripts/qd_build.py --write` → `topics.json` + `dependencies.json`（372 点 / 517 边 / 课标借调 / 根节点 reason）。
4. 分片派单：一年级上册拆 4 片（37＋53＋39＋52 题）并发写库，每片跑 `scripts/qd_check_bank.py` 到 `PASS`；父代再逐片复跑一遍（不信自报）。
5. `python3 scripts/qd_merge_bank.py` → `questions.json`（合并 46 片、排序、回写 `diagnostic_question`）。
6. `rebuild_aggregates_only.py` → `build_standards_index.py` → `build_stats.py --write` → `test_math_qd.py`（28/28）。

## 6. 骨架清洗（2026-11）

教材目录页里混入了表格行、页码行与栏目标题，被当成小节名写进骨架：

| 现象 | 位置 | 处置 |
| --- | --- | --- |
| 空名 / `°` / `乙` / `m。` / `-,` | 七上、七下、八下、九上各 1–2 个 | 剔除该点及其题目（共 11 点 / 85 题） |
| 整章「有理数的运算」 | 八年级下册（教材实际止于「数据的分析」） | 整章 5 点剔除（目录页串入） |
| 单元名只剩序号「四/五/六/七」 | 六年级上册 | 按教材补回：完美的图形—圆 / 中国的世界遗产—解决问题 / 抽奖转盘—可能性 / 走进军营—方向与位置 |

清洗脚本 `scripts/qd_fix_names.py`（显式清单，不按正则批量删——「角」「圆」是教材正名，单字不能误删）。
自检新增两条闸门：知识点名须含汉字且不含目录噪声；14 册全部纳入题库白名单。

## 7. 已知缺口

- **教材缺 4 册**：四下、五下、六下、九下；这 4 册不建点（不猜章节），站点上也不显示。
- **题库 14 册全覆盖**（361 点 / 2570 题）：全部 `choice`，无填空、无开放题；`application` 类（如统计调查）建议后续补情境简答。
- **课标全部 `inferred`**：借调自人教版同段条目，逐点人工对齐（`exact/partial`）还没做。
- **小学课时名取教材情境名**（如「箱子里有什么」「折纸鹤」）：这是青岛版教材的真实栏目标题，与人教版「小节名」口径不同，跨版本横向比较时要注意。
- 单元 `description` 目前多为情境名（大单元 docx 的知识要素句还没提取进 `description`）。

## 8. 自检与站点

```bash
python3 scripts/qd_inventory.py             # 册/单元/信息窗初盘
python3 scripts/qd_skeleton_source.py       # 结构源对账（14 册 / 107 单元 / 265 课时）
python3 scripts/qd_build.py                 # 骨架 dry-run（--write 落盘）
python3 scripts/qd_check_bank.py <shard>    # 分片自检（末行 PASS）
python3 scripts/qd_merge_bank.py            # 合并分片 → questions.json
python3 scripts/test_math_qd.py             # 28 项不变量
python3 scripts/validate.py math-qd         # 结构/引用
```

- 学科页：`index.html?subject=math-qd`
- 图谱：`explore/?subject=math-qd&grade=1`
- 诊断：`diagnose/?subject=math-qd#qdm_p002`
