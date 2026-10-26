# 中国 K-12 全学科知识图谱（cn-k12-dxyc2286）

**17 个学科 · 1,924 个知识点 · 2,199 条先修边 · 1,924 道诊断题 · 972 条课标条目**，覆盖小学到高中。每个知识点带**可观察的掌握标准**、**节点级诊断题**、**课标条目与置信度**；先修边分 hard / soft 两档，可直接驱动前置诊断与学习路径推荐。

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgreen.svg)](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)
[![知识点](https://img.shields.io/badge/%E7%9F%A5%E8%AF%86%E7%82%B9-1924-2ea44f)](data/topics.json)
[![先修边](https://img.shields.io/badge/%E5%85%88%E4%BF%AE%E8%BE%B9-2199-1f6feb)](data/dependencies.json)
[![课标引文](https://img.shields.io/badge/%E5%B8%A6%E5%8E%9F%E6%96%87%E5%BC%95%E6%96%87-647%2F1924-orange)](data/cn-curriculum-standards.json)
[![GitHub Pages](https://img.shields.io/badge/%E7%AB%99%E7%82%B9-GitHub%20Pages-lightgrey)](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/)

**[→ 在线浏览](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/)** · [知识图谱](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/explore/) · [自适应诊断](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/diagnose/) · [学习档案](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/children/) · [诊断记录](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/children/history.html) · [❤️ 赞助支持](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/sponsor/)

![首页：一句话说明、三步用法、实时统计与 17 个学科入口](screenshots/01-home.png)

![知识图谱：当前知识点附近的先修关系（向上 2 层，向下 1 层）](screenshots/02-explore.png)

![诊断结果：薄弱根因、按学习顺序排好的路径与逐题记录](screenshots/03-diagnose.png)

| 学段 | 知识点 | 诊断题 | 说明 |
| --- | ---: | ---: | --- |
| 小学（1–6 年级） | 406 | 406 | 语文、数学、英语、科学、信息科技、音乐、美术、俄语、西班牙语 |
| 初中（7–9 年级） | 734 | 734 | 语文、数学、英语、物理、化学、生物、历史、地理、信息科技、音乐、美术、俄语、西班牙语 |
| 高中（10–14 册次） | 784 | 784 | 语文、数学、英语、物理、化学、生物、历史、地理、日语、俄语、德语、法语、西班牙语、音乐、美术 |
| **合计** | **1,924** | **1,924** | **17 个学科 · 2,199 条先修边（hard 2,093 / soft 106）** |

> 年级用 `1`–`14` 表示：`1`–`9` 为义务教育年级，`10`–`14` 为高中册次（必修一/二、选必一/二/三），**不是**「高一到高四」，也不写教学进度。

数据格式参考 [Marble os-taxonomy](https://github.com/withmarbleapp/os-taxonomy)（`topics` + `dependencies`），并按本仓库需要扩了诊断题、课标条目、版本映射与学习档案。

**反馈 / 挑错：** 知识点拆分、掌握标准、先修关系（某条边该不该有、该是 hard 还是 soft）、诊断题答案有异议，或想提功能建议，请 [提交 Issue](https://github.com/grantleyzyf-spec/cn-k12-dxyc2286/issues/new)。

> **状态声明：这是 AI 生成的初稿，未经一线教师审核。**
> 知识点粒度、掌握标准、先修关系强度、诊断题难度都没有经过教师评审，也没有真实答题数据校准；请勿直接用于正式教学或升学判断。
> **课标对齐分两级口径**：`standards` 非空 **1,918 / 1,924**；其中**带课标原文引文（`quote`）可逐字复核的只有 647 / 1,924**。其余 1,271 个是**课标编号引用**，不等于已对齐，见下方「已知局限」。
> 高中与小语种课标条目多为公开转述，未与教育部 PDF 逐页核对。

## 数据来源与对齐依据

- **课程标准**：`data/cn-curriculum-standards.json` 收录 **972** 条课标条目（17 个学科分桶，每桶含 `entryCount` 与 `entries`，`totals` 为 17 / 972 / 1,924 / 1,918）。依据教育部《义务教育课程方案和课程标准（2022 年版）》及 2025 年日常修订版、《普通高中课程方案和课程标准（2017 年版 2020 年修订）》的公开文本；原件按学科存放在本地 `中小学教材/2025修订课程标准/`（义教 17 份、高中 24 份），另有一批 `pdftotext` 抽出的 TXT 快照。
- **课标条目 id**：按学科自编，格式 `{学科前缀}-{年份}:{学段或模块}.{序号}`，例如数学 `cms-2022:1.NA.05`、语文 `cyw-2022:1.SX.02`、德语 `dyu-2017:G.ZT.03`。**不是教育部原编号**，只在本仓库内部可追溯。
- **`quote` 规则**：`standards[]` 里出现 `quote` 时，该片段必须逐字出自对应课标文本（CI 可回表核验 `quote in 课标原文`），`sourceLine` 记录定位；做不到逐字命中的**一律不写 `quote`**，只留 id + `confidence`，不为凑满而编造。
- **`confidence`**：`exact`（课标有直接对应条款）/ `partial`（部分对应）/ `inferred`（据学段与教材推断）。
- **教材顺序**：按人教版等主流版本教材的册次与章节编排；册次地图见 `data/mappings/volume-map.json`（自动生成，覆盖全部 1,924 个知识点），跨版本字段映射见 `data/mappings/schema-mapping.json`。
- **小语种边界**：义务教育阶段外语课标只有英语 / 日语 / 俄语；法语、德语、西班牙语的义教段知识点在课标体系里无对应条文，只能挂高中课标并标 `confidence: inferred`（已如实标注，不冒充对齐）。

## 文件与字段

```
data/
  topics.json                 # 全学科知识点（1,924 条，汇总，脚本生成，别手改）
  dependencies.json           # 先修边（2,199 条）
  questions.json              # 诊断题（1,924 道）
  cn-curriculum-standards.json# 课标条目索引（972 条，脚本生成）
  stats.json                  # 站点与 README 用的现算统计（scripts/build_stats.py）
  subjects.json               # 学科元数据（id / 名称 / 图标 / 数量）
  schema-topic.json           # JSON Schema（根节点是 array，items 显式 type: object）
  schema-question.json
  schema-dependency.json
  curriculum-standards.json   # 课标来源元数据（各学科课标名称/版本）
  verification_report.json    # 数据核验报告
  mappings/                   # 册次地图（volume-map）、跨版本字段映射
  <subject>/                  # 17 个学科，各含 topics / dependencies / questions.json
```

### `topics.json` 字段（节点契约 v2）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | `{学科前缀}_{p\|h}NNN`，全库唯一（前缀 2–6 字母，序号 2–4 位） |
| `name` / `subject` / `domain` | string | 名称 / 学科 id / 领域 |
| `grade` / `semester` | string | 年级 `1`–`14` / `上`、`下`、`全`（旧 `fall`/`spring` 已迁移） |
| `chapter` | string | 教材册次 + 章节 |
| `type` | enum | `conceptual` / `procedural` / `reasoning` / `modeling` / `application` |
| `description` | string | 概念说明 |
| `mastery_criteria[]` | string[] | 1–3 条**可观察**的掌握标准，用于判定「会不会」 |
| `diagnostic_question` | object | 节点级快诊题 `{question, answer}`（题库在 `questions.json`） |
| `standards[]` | object[] | `{id, confidence, quote?, sourceLine?}`；`quote` 是防编造的硬约束 |
| `prerequisites[]` | string[] | 直接先修 id（与 `dependencies.json` 互为镜像） |
| `curriculumRef` / `tags[]` / `external` / `verified` | | 课标定位 / 标签 / 是否跨学科外部节点 / 审核标记 |

### `dependencies.json` 字段

`{ "from": "<先修知识点 id>", "to": "<后继知识点 id>", "type": "hard" | "soft" }`
`hard` = 不掌握前者基本学不会后者；`soft` = 有帮助但非必需（多为教材编排顺序）。

### `questions.json` 字段

`{ id, topicId, prompt（规范字段，12–120 字）, question（兼容别名，同值）, answer, type, difficulty, explanation, options?, verify? }`
`choice` 必须给 4 个 `{label, text}` 且 `answer` 是 label；`numeric` 的 `verify` 是能被 Python `eval` 复算的表达式。

## 分学科覆盖

| 学科 | 学段 | 教材版本 | 知识点 | 先修边 | 诊断题 | 已挂课标 | 其中带原文引文 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 数学（`math`） | 小·初·高 | 人教版（含人教 A 版 2019） | 479 | 527 | 479 | 479 | 0 |
| 语文（`chinese`） | 小·初·高 | 统编版 | 205 | 203 | 205 | 204 | 204 |
| 英语（`english`） | 小·初·高 | 人教 PEP / Go for it! / 人教版 2019 | 204 | 209 | 204 | 204 | 0 |
| 物理（`physics`） | 初·高 | 人教版 | 177 | 205 | 177 | 177 | 0 |
| 生物（`biology`） | 高 | 人教版 | 140 | 246 | 140 | 140 | 0 |
| 历史（`history`） | 初·高 | 统编版 | 138 | 159 | 138 | 138 | 138 |
| 德语（`german`） | 高 | 外研社版 | 100 | 60 | 100 | 98 | 98 |
| 俄语（`russian`） | 小·初·高 | 人教版 | 96 | 106 | 96 | 93 | 93 |
| 地理（`geography`） | 初·高 | 人教版 | 85 | 104 | 85 | 85 | 0 |
| 化学（`chemistry`） | 初·高 | 人教版 | 62 | 79 | 62 | 62 | 0 |
| 信息科技（`information-technology`） | 小·初 | 人教版 | 51 | 76 | 51 | 51 | 0 |
| 法语（`french`） | 高 | 外研社版 / 沪外教版 | 46 | 61 | 46 | 46 | 46 |
| 日语（`japanese`） | 高 | 人教版 | 39 | 60 | 39 | 39 | 39 |
| 西班牙语（`spanish`） | 小·初·高 | 外研社版 | 29 | 30 | 29 | 29 | 29 |
| 美术（`art`） | 小·初·高 | 人教版 | 26 | 26 | 26 | 26 | 0 |
| 音乐（`music`） | 小·初·高 | 人教版 | 24 | 25 | 24 | 24 | 0 |
| 科学（`science`） | 小 | 教科版 | 23 | 23 | 23 | 23 | 0 |
| **合计** | — | — | **1,924** | **2,199** | **1,924** | **1,918** | **647** |

（上表由 `python3 scripts/build_stats.py` 从 `data/` 现算，改数据后重跑即可，别手改数字。）

**读表要点：**

- 「已挂课标」只表示写了 `standards` 条目；**「带原文引文」才是可逐字复核**的部分。数学、英语、物理、生物、地理、化学、信息科技、美术、音乐、科学仍是课标编号引用，属待补引文状态。
- 语文、历史、德语、俄语、法语、日语、西班牙语已完成引文回填（`quote` + `sourceLine`），可用脚本全量复核。
- 仍未挂课标的 6 个知识点（语文 1、德语 2、俄语 3）在课标原文里找不到可对应表述，**留空不编造**。

## 页面

四个静态页，共用 `assets/site.css` 与顶部导航（学科切换 / 首页 / 知识图谱 / 诊断 / 档案 / 关于）；数据全部通过 `fetch` 读 `data/*.json`，**不从外网 CDN 加载脚本、样式或字体**。

**首页**（`index.html`）：一句话定位 + 三步用法（选知识点 → 自适应答题 → 找到根因和学习路径）+ 四张统计卡（知识点 / 先修边 / 诊断题 / 课标条目，打开时读 `data/stats.json` 现算，不写死）+ 17 个学科入口卡片 + 学段/年级入口 + 特性区 + 常见问题 + 页脚。

**知识图谱**（`explore/`）：左侧搜索与筛选（学科 / 学段 / 年级 / 领域），中间用 Cytoscape + dagre 只画**当前知识点的局部图**（默认向上 2 层先修、向下 1 层；可切 1 / 2 / 3 层或全部祖先），hard 实线、soft 虚线，小学 / 初中 / 高中三色；右侧详情含名称、年级册章、领域、类型、描述、掌握标准、课标条目、样题、先修与被依赖列表，以及「诊断这个知识点」按钮。

**诊断**（`diagnose/`）：先按学科 / 学段 / 年级筛范围，再沿先修关系自适应出题（每个知识点最多 2 题，支持整册筛查）；结果页把**薄弱根因**、**不稳**、**按学习顺序排好的路径**分成卡片，附逐题记录，可导出 JSON、可打印。

**学习档案**（`children/`）：本地存储（`localStorage`，键 `k12kids.v1`）记录多个孩子的诊断历史，`history.html` 看趋势；数据不出本机，换设备不同步。

## 运行校验

```bash
cd cn-k12-dxyc2286
python3 scripts/normalize_to_ref_schema.py --check   # 体检：结构完整度 / 缺口
python3 scripts/normalize_to_ref_schema.py --write   # 规范化 + 重建三份汇总
python3 scripts/build_standards_index.py             # 重建课标条目索引 + 册次地图
python3 scripts/validate.py --all                    # 17 学科结构 / 引用（CI 同款）
python3 scripts/validate_mappings.py                 # 版本映射
python3 scripts/build_stats.py --write               # 现算统计（README / 首页数字来源）
```

`validate.py --all` 检查：JSON 合法、id 唯一、必填字段齐全、枚举值合法、每条边两端都存在、无自环 / 重复边 / 环、非外部知识点要么有先修边要么有 `root_reason`、`standards` 引用的课标 id 必须存在于索引、`confidence` 只能是 `exact` / `partial` / `inferred`。全通过输出 `VALIDATION PASSED`，退出码 0。

## 本地打开

页面用 `fetch` 读数据，**不能直接双击 `file://` 打开**：

```bash
python3 -m http.server 8000
# 首页        http://localhost:8000/
# 知识图谱    http://localhost:8000/explore/
# 诊断        http://localhost:8000/diagnose/
# 学习档案    http://localhost:8000/children/
```

## 已知局限

- **审核缺位**：先修关系、hard / soft 强度、诊断题难度与区分度都没有经过教师评审，也没有学生答题数据校准。
- **引文覆盖不均**：647 / 1,924 带可复核引文；数学（479）、英语（204）、物理（177）、生物（140）、地理（85）、化学（62）、信息科技（51）、美术（26）、音乐（24）、科学（23）仍是课标编号引用，**不要把「覆盖率」当成「已对齐」**。
- **课标版本并行**：义教 2022 版与 2025 日常修订版并行使用，个别条目措辞有变化；高中各科为 2017 年版 2020 年修订。德语只有高中课标。
- **小语种**：法语 / 德语 / 西班牙语义教段无课标条文，只能挂高中课标并标 `inferred`。
- **粒度不统一**：数学按教材小节拆得细，音乐 / 美术 / 科学偏主题式，跨学科横向比较要注意口径。
- **题库规模**：每点 1–2 道代表题，够做定位，不足以做完整测评；难度标签未经数据校准。
- **教材目录来源**：部分册次目录取自第三方电子课本站或国家中小学智慧教育平台目录页预览，未逐页与纸质教材核对。

## 后续建议（Roadmap）

1. **补引文**：把数学、英语、物理、生物、地理、化学、信息科技、美术、音乐、科学的 `standards` 升级为带 `quote` + `sourceLine` 的可复核形态（647 → 目标 1,900+）。
2. **教师审边**：优先审数学 527 条、生物 246 条、英语 209 条、物理 205 条先修边里的 hard 判定。
3. **毕业年级对齐**：中考 / 高考复习单元与课标条目的映射单独建表，避免与教材册次混淆。
4. **题库扩充**：每点 2 → 4 题，数值题补 `verify` 自动复算，选择题补干扰项来源说明。
5. **诊断校准**：用真实答题数据回归题目难度与先修强度。

## 部署

- **GitHub Pages**：`main` 分支推送后由 `.github/workflows/deploy.yml` 发布静态站（仓库已启用 Pages，`build_type=workflow`）；
- **数据闸门**：`.github/workflows/validate.yml` 跑数据校验，并检查「重生成后 diff 为空」（课标索引与统计的新鲜度闸门）；
- **本地预览**：`python3 -m http.server 8000`，无需构建（纯静态 + Python 脚本）；
- 提交后自查：`gh run list -R grantleyzyf-spec/cn-k12-dxyc2286 -L 3`，两条 workflow 都 success 才算完。

## 贡献

欢迎 Issue / PR。提 PR 前请把上面的「运行校验」五步跑一遍，确保 `validate.py --all` 通过，且 `build_standards_index.py`、`build_stats.py` 的产物一并提交。数据改动请改 `data/<subject>/` 源文件，**不要手改汇总的 `data/topics.json`**。

## ❤️ 支持本项目

- 🐙 **GitHub Sponsors**：<https://github.com/sponsors/grantleyzyf-spec>
- ⚡ **爱发电**：<https://afdian.com/a/cn-k12-dxyc2286>
- 💰 **Open Collective**：<https://opencollective.com/cn-k12-dxyc2286>

赞助用于站点运维、教师审核与数据补齐，明细见 [赞助页](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/sponsor/)。

## 第三方库

`assets/vendor/` 本地打包，页面不访问外网 CDN：

| 文件 | 包 | 版本 | 许可证 |
|---|---|---|---|
| `cytoscape.min.js` | cytoscape | 3.30.4 | MIT |
| `dagre.min.js` | dagre | 0.8.5 | MIT |
| `cytoscape-dagre.js` | cytoscape-dagre | 2.5.0 | MIT |

这些库保持各自许可证，不纳入本仓库的 CC BY 4.0。

## 许可证 / License

本仓库的知识图谱数据、题库与文档采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)（署名 4.0 国际），完整条款见 [LICENSE](LICENSE)。

- ✅ 可用于个人学习、教学、研究，也可商用、修改、再分发，需**署名并注明来源**（本仓库链接）。
- `assets/vendor/` 的第三方库保留各自 MIT 许可。

## 参考

- 教育部《义务教育课程方案和各学科课程标准（2022 年版 2025 年修订）》
- 教育部《普通高中课程方案和学科课程标准（2017 年版 2020 年修订）》
- [cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy) — 节点结构、诊断引擎与页面组织参考项目
- [Marble os-taxonomy](https://github.com/withmarbleapp/os-taxonomy) — `topics` + `dependencies` 数据格式参考
