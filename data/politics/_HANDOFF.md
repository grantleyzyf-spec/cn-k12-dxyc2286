# politics（道德与法治／思想政治）交接单

> 新会话执行：说「继续 politics」，按本文件续跑；所有已完成产物均已落盘，不依赖聊天历史。

## 已完成（可验证）

| 产物 | 说明 |
| --- | --- |
| `data/politics/_inventory.json` | 21 册 / 教材单元 78（义教 57 ＋ 高中 21）/ 高中课 58 / 高中框 135 / 综合探究 20（不建点） |
| `data/politics/topics.json` | **435 点**（领域：道德 132 ／ 政治认同 128 ／ 法治 94 ／ 哲学 63 ／ 经济 18）（unit 115 ＝ 义教 57 单元 ＋ 高中 58 课；lesson 320 ＝ 义教 185 课 ＋ 高中 135 框），id `pol_p001…pol_p435`；已挂课标引文 **517 条**（义教 112/134 条被引用、高中 65/65） |
| `data/politics/dependencies.json` | **646 边**（hard 576 ／ soft 70）：课/单元→框 hard、框内顺次 hard、课顺次 hard、单元衔接 soft |
| `data/politics/questions.json` | **3135 题**（全 choice，435 点每点 8/5，答案位 A794·B804·C779·D758） |
| `data/politics/_standards_src/` | 课标快照（义教 134 条 / 高中 65 条）＋ `unit_map.json`（115 个单元点人工定标） |
| `data/politics-standards-entries.json` | 199 条课标条目目录（id/学段/主题/序/行号/全文） |
| `data/politics/_audit.json` | 结构体检结果（目录点 0、框号乱序 0、重复点 0） |
| `scripts/ddfz_inventory.py` | 义教盘点脚本（已修 4 个解析坑） |
| `scripts/ddfz_hs_rebuild.py` | 高中 7 册结构重建（`--show` 看结构 / `--write` 落盘），读 PDF 目录页 |
| `scripts/ddfz_standards.py` | 课标回表（`--rebuild-src` / `--write`），含逐字回表校验 |
| `scripts/ddfz_audit.py` | 结构体检（目录点／框号／占位字段） |
| `scripts/ddfz_domain_fix.py` | 义教 domain 重挂（幂等，`--write` 落盘） |
| `scripts/ddfz_extra_citations.py` | 补挂义教未引用课标条目（幂等；定标表 `_standards_src/extra_citations.json`） |
| `scripts/ddfz_make_shards.py` | 切分片 + 派单（57 片 / 3135 题） |
| `scripts/ddfz_merge_bank.py` | 合并分片 + 回写 diagnostic_question + schema 校验 |
| `scripts/test_politics.py` | 39 项不变量自检（结构/课标/题库） |
| `.github/workflows/validate-politics.yml` | politics 专用 CI |
| `docs/politics.md` | 规模、高中结构口径、课标口径、回表结果、已知缺口、自检命令 |
| `data/schema-topic.json` / `data/subjects.json` | 已含 `politics` |

`python3 scripts/validate.py politics` → Total Errors: 0
`jsonschema.validate(topics, schema-topic)` → OK
课标引文逐字回表 → 489/489（按 `sourceLine` 读快照再比对）
先修图无环、prerequisites 与 dependencies 双向镜像 → 通过

## 第 1 步（已完成）：课标回表

- **源用 docx 不用 TXT**：`2025修订课程标准TXT ` 里那份义教 TXT 是扫描件 OCR 底本（三列表格逐行交错、部分字形成拉丁字母），无法承载可读引文。改从《…2025修订/word/*.docx》的「内容要求」列抽条，落干净快照到 `data/politics/_standards_src/`。
- 义教 134 条 / 高中 65 条；编号 `ddf-2022:{学段}.{板块}.{序}`、`zz-2017:G.{模块}.{序}`。
- 匹配两级：单元点走 `unit_map.json` 人工定标（1–2 条）；课时点在同一学习主题/模块池内做 IDF 加权词面择优（需命中 df≤4 的稀有二元组，且连续 3 字重合或 ≥2 个二元组），择优不到继承单元条目记 `inferred`。
- 结果：435/435 有引文，confidence `exact` 31 / `partial` 268 / `inferred` 190，被引用条目 149/199。

## 第 1.5 步（已完成）：高中结构返修

- 原病：5 个「目录」点、14 个单元框号乱序/重号、选必册序倒置（选必3→2→1）、「目」级子标题当框（246 点虚高）。
- 现做法：`ddfz_hs_rebuild.py` 只读 7 册 PDF **目录页**，按缩进还原 `第X单元 → 第Y课 → 第Z框`；课名折行合并；册序按课程顺序写死；`综合探究` 不建点。义教 242 点原样保留（id 不变）。
- 结果：高中 193 点（58 课 ＋ 135 框），目录点 0、框号乱序 0、重复点 0；`unit_map.json` 已按新课 id 重标 58 条。

## 已知缺口

- 教材缺 4 册：四下、五下、六下、九下（无 PDF，不造点）
- 字段占位：435 点的 `description`＝`name`，`mastery_criteria`/`diagnostic_question` 全为同一模板 ⇒ 第 2–4 步逐点重写
- 高中 `综合探究`（20 个）不建点，只留在盘点表
- 引文语义精度分层：`partial` 是同主题块词面择优（抽样约 8–9 成贴题），`inferred` 是继承单元上位条目；逐句精确须人工逐条审定 320 个课时点
- 高中按「课＝单元点、框＝课时点」入图；若改按课诊断，只动 `level` 一处

## 续跑

1. ~~课标回表~~ ✅
2. ~~高中结构返修~~ ✅
3. ~~切分片~~ ✅ 57 片 / 3135 题（`scripts/ddfz_make_shards.py --write`，派单在 `data/politics/_shards/S{01..57}/WORKER.md`，题目落 `data/politics/_bank/S{NN}.json`）
   - 试点两片在跑：S01（一年级上册 66 题）、S110（选必3 逻辑与思维 68 题）；跑通后按片并发。
4. ~~并发写题~~ ✅ 57 片全部 PASS，共 **3135 题**（`data/politics/_bank/S01…S57.json`）
5. ~~合并 + 门禁~~ ✅ `scripts/ddfz_merge_bank.py` 合并 → `questions.json`（3135 题，schema OK，回写 435 个 `diagnostic_question`）；`scripts/test_politics.py` **39/39**；`validate.py politics` 0 错误
6. ~~文档与上线~~ ✅（2026-11-02：commit `ce8a62b`，远端 head 已含 politics；CI `Validate Politics Subject Data` success、`Deploy` success；线上 `data/politics/{topics,questions,dependencies}.json` 与本地 md5 一致；explore 下拉 19 学科含「道德与法治／思想政治」，深链 `?subject=politics` 出图）

### 上线备注→ 已备 `.github/workflows/validate-politics.yml`（politics 专用，validate --all ＋ test_politics ＋ 索引新鲜度）；待办：`build_standards_index.py` 生成 politics 桶、README 加分学科行/小节、推送走 Git Data API（只动 `data/politics/**`＋`data/politics-standards-entries.json`＋自己脚本＋派生文件按桶增量改）

## 口径备忘

- 义教以「课」为可诊断点（每点 8 题），单元 5 题；高中以「框」为可诊断点、课为单元点
- 领域五板块：道德教育 / 政治认同 / 法治教育 / 经济发展 / 哲学思维
- 上课时长限制：`github.com:443` 不通，推走 `api.github.com` ＋ `gh auth token`（详见技能 `cn-k12-knowledge-graph-build` §8.5）

- 远端聚合（`data/topics.json` / `questions.json` / `dependencies.json` / 课标索引 / volume-map / stats）**在我推送前已含 politics**（另一会话在本机工作树里跑过聚合脚本并推送），且与我分学科数据逐条一致（topics 435 / deps 646 / questions 3135）⇒ 本次只补源文件与站点注册，没再重算聚合。
- ⛔ 不要为刷新人这个仓库的全局 `build_standards_index.py`：它按分学科文件重算，而 `math-bsd` 的分学科文件（31 点）与已提交聚合（562 点）不一致，重算会把 531 点从聚合里抹掉。politics 的索引新鲜度改用 `scripts/check_politics_standards_index.py`（只核本学科桶）。
- ⛔ `build_subjects_registry.py` 全量重生成会因 `data/math-hebei/` 缺 `topics.json` 而删掉「冀教版」版本 ⇒ politics 是**手工插入** `data/subject-groups.json`（并在脚本 `SUBJECT_LABEL` 里登记，供以后正常重生成时保留）。
- 共享 workflow `validate.yml` 的 `Validate JSON Data` 仍红，红在 `Subject invariants · math-qd`（另一会话的青岛版数学），与 politics 无关；politics 自己的 workflow 是绿的。
