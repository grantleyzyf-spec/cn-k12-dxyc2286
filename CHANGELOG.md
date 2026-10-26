# 变更日志

本文件记录 cn-k12-dxyc2286 项目的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [Unreleased]

### 新增（0.3.0-dev）
- **节点结构对齐 cn-math-taxonomy（v2）**
  - 知识点新增 `mastery_criteria`（可观察掌握标准）、`diagnostic_question`（节点级快诊题）、
    `external`、`standards[{id,confidence}]` 四个字段；补齐 `domain`、`type`
  - `semester` 由 `fall/spring` 统一为 `上/下`（与参考项目一致）
  - 诊断题以 `prompt` 为规范字段，`question` 保留为兼容别名；新增可选 `verify` 可复算校验式
  - 同步更新 `data/schema-topic.json`、`data/schema-question.json` 与 `scripts/validate.py`
- **修复数学数据只暴露 24 个知识点**：`data/math/topics.json` 是旧存根，站点只读到 24 条；
  新增 `scripts/rebuild_canonical_from_splits.py` 由 `topics_grade*.json` 重建单文件
  ⇒ 数学 24 → **479** 知识点、14 → **469** 题、26 → **527** 先修边
- **新增汇总数据**：`data/topics.json` / `data/dependencies.json` / `data/questions.json`
  （全学科合并，与参考仓库同口径，便于外部直接消费）
- **修数据一致性**：english 先修边缺 `type`、german 用了 `prerequisite` 别名、history 的
  `type` 字段混入难度值、english 题目 `answer` 为空（改用选项 `correct` 标记）、
  german 选项为字符串（"A. ß"）—— 全部在 `scripts/normalize_to_ref_schema.py` 中规范化
- **CI**：`validate.yml` 由「只查 4 学科语法」升级为「全 17 学科 + 结构与引用校验 + JSON Schema 校验」
- **部署**：启用 GitHub Pages（workflow 构建），修复 Deploy 工作流 `Get Pages site failed`
- **README**：补 v2 节点结构说明、目录结构、脚本用法、真实统计与覆盖缺口（124 个知识点暂无诊断题）
- **新增「学习档案」页面组**（对齐参考仓库 children/ 的能力，按本库口径重写）
  - `children/index.html` + `page.js` + `children.css`：建档（称呼/年级/教材版本）、编辑、删除、切换当前孩子
  - `children/history.html` + `history.js`：诊断明细 + **反复未掌握知识点聚合**（按出现次数排序）
  - `assets/children.js`：localStorage 存储层（`k12kids.v1`），`diagnose/` 完成后自动按当前孩子写入记录
  - 首页新增「学习档案」入口
- **本地第三方库**：`assets/vendor/` 打包 cytoscape 3.30.4 / dagre 0.8.5 / cytoscape-dagre 2.5.0（均 MIT，附许可证原文），
  页面不再依赖外网 CDN
- **课标条目索引** `data/cn-curriculum-standards.json`：758 个课标条目，覆盖 1481/1924 知识点，
  每条带覆盖的 `topicIds`、年级与 `confidence`；由 `scripts/build_standards_index.py` 从数据本身生成
  （缺口：语文 205、历史 138、德语 100 个知识点尚未挂课标条目）
- **教材版本映射** `data/mappings/`：`volume-map.json`（册次 → 知识点，自动生成）+ `schema-mapping.json`
  + `README.md`（如何按教材目录建版本映射，禁止无依据填写）+ `example.template.json`
- **CI 增补**：`validate_mappings.py` 校验映射 id 合法性；课标索引/册次地图**新鲜度校验**（提交物与脚本重生成不一致即失败）

### 待办
- [ ] 教师审核各学科知识点拆分粒度
- [ ] 教师审核先修关系(hard/soft)合理性
- [ ] 教师验证诊断题答案准确性
- [ ] 课标条目逐页核对
- [ ] 添加更多版本教材支持（北师大版、苏教版等）
- [ ] 完善高中选修课程数据
- [ ] 补齐物理(74)、俄语(40)、数学(10) 缺失的诊断题

---

## [0.2.0] - 2026-10-26

### 新增
- **项目结构完善**：参考 cn-math-taxonomy 项目结构
  - 添加 `data/curriculum-standards.json` 课标元数据汇总
  - 添加 `data/id-aliases.json` ID别名映射（支持知识点重命名兼容）
  - 添加 `data/verification_report.json` 数据验证报告
  - 添加 PWA 支持 (`manifest.webmanifest` + `sw.js`)
  - 添加 `.nojekyll` 支持 GitHub Pages 部署
  - 添加 `screenshots/` 目录（待填充截图）
  - 添加 `assets/icons/` 目录（待填充图标）

### 完善
- 更新 README.md 添加完整数据规模统计
- 更新诊断工具和图谱浏览器支持多学科切换

---

## [0.1.0] - 2026-10-26

### 新增
- **项目初始化**：建立 cn-k12-dxyc2286 开源知识图谱项目
- **17个学科数据生成**（AI初稿）：
  - 数学：479个知识点，527条先修关系，469道诊断题（小学1-6年级+初中7-9年级+高中10-12年级）
  - 英语：204个知识点，209条先修关系，204道诊断题
  - 语文：205个知识点，203条先修关系，205道诊断题
  - 物理：177个知识点，205条先修关系，103道诊断题
  - 生物：140个知识点，246条先修关系，140道诊断题
  - 历史：138个知识点，159条先修关系，138道诊断题
  - 地理：85个知识点，104条先修关系，85道诊断题
  - 德语：100个知识点，60条先修关系，100道诊断题
  - 俄语：96个知识点，106条先修关系，56道诊断题
  - 信息科技：51个知识点，76条先修关系，51道诊断题
  - 化学：62个知识点，79条先修关系，62道诊断题
  - 法语：46个知识点，61条先修关系，46道诊断题
  - 日语：39个知识点，60条先修关系，39道诊断题
  - 美术：26个知识点，26条先修关系，26道诊断题
  - 音乐：24个知识点，25条先修关系，24道诊断题
  - 西班牙语：29个知识点，30条先修关系，29道诊断题
  - 科学：23个知识点，23条先修关系，23道诊断题
  - **总计：1924个知识点，2199条先修关系，1800道诊断题**

- **工具与基础设施**：
  - 自适应诊断工具 (`diagnose/index.html`)
  - 知识图谱浏览器 (`explore/index.html`)
  - 项目主页 (`index.html`)
  - 数据验证脚本 (`scripts/validate.py`)
  - 数据合并脚本 (`scripts/merge_math_data.py`)
  - JSON Schema 定义 (`data/schema-*.json`)
  - GitHub Actions CI 工作流 (`.github/workflows/validate.yml`)
  - Issue 模板 (`.github/ISSUE_TEMPLATE/bug-report.md`)

- **文档**：
  - README.md（项目说明、数据规模、使用方法）
  - CONTRIBUTING.md（贡献指南）
  - docs/standards-mapping.md（课标对齐说明）
  - LICENSE（CC BY 4.0）

### 已知问题
- ⚠️ 所有数据为 AI 生成初稿，未经教师审核
- ⚠️ 知识点拆分粒度、先修关系、诊断题答案需要一线教师验证
- ⚠️ 部分课标条目编号为自编，未与教育部原文逐页核对
- ⚠️ 仅覆盖人教版教材，其他版本待扩展

---

## 参考项目

本项目结构参考了以下开源项目：
- [cn-math-taxonomy](https://github.com/xiaoyang111222/cn-math-taxonomy) - 数学知识图谱（3900+ stars）

---

[Unreleased]: https://github.com/grantleyzyf-spec/cn-k12-dxyc2286/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/grantleyzyf-spec/cn-k12-dxyc2286/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/grantleyzyf-spec/cn-k12-dxyc2286/releases/tag/v0.1.0
