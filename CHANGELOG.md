# 变更日志

本文件记录 cn-k12-dxyc2286 项目的所有重要变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [Unreleased]

### 待办
- [ ] 教师审核各学科知识点拆分粒度
- [ ] 教师审核先修关系(hard/soft)合理性
- [ ] 教师验证诊断题答案准确性
- [ ] 课标条目逐页核对
- [ ] 添加更多版本教材支持（北师大版、苏教版等）
- [ ] 完善高中选修课程数据

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
