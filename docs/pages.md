# 站点结构（四个静态页 · 共用样式 · URL 参数）

站点是纯静态页 + `fetch` 读 `data/*.json`，**不需要构建**。所有页面共用 `assets/site.css`（青绿主色、跟随系统深色模式）与顶部导航；图形库与 d3 都在 `assets/vendor/`，**不从外网 CDN 加载脚本、样式或字体**。

## 1. 页面清单

| 路径 | 作用 | 关键交互 |
| --- | --- | --- |
| `index.html` | 首页 | 一句话定位、三步、5 张统计卡（读 `data/stats.json`）、17 个学科卡、特性、FAQ |
| `explore/` | 知识图谱 | 学科/学段/年级/领域筛选、局部先修图（Cytoscape + dagre）、右侧详情 |
| `diagnose/` | 自适应诊断 | 选范围 → 沿 hard 边出题 → 结果分「根因/不稳/未测 + 路径」 |
| `children/` | 学习档案 | 建档、切换当前孩子、诊断记录（`localStorage: k12kids.v1`） |
| `children/history.html` | 诊断记录 | 反复未掌握知识点聚合 + 明细 |

## 2. URL 参数

| 页面 | 参数 | 说明 |
| --- | --- | --- |
| `explore/` | `?subject=<id>` | 进入即选中该学科（17 个 id 见 `data/subjects.json`），学科下拉同步 |
| `diagnose/` | `?subject=<id>` | 同上；不传则默认数学 |
| 根路径 | `#<topic-id>` | 兼容旧链接：根路径带 `#cnm_…` 会转到知识图谱对应知识点 |

首页的学科卡就是 `explore/?subject=<id>`，所以从首页点卡片能直接落到该学科的图。

## 3. 数据依赖

```
index.html      → data/stats.json（失败时回退内置基线并提示）
explore/        → data/<subject>/topics.json + dependencies.json
diagnose/       → data/<subject>/topics.json + dependencies.json + questions.json
children/       → localStorage（不读网络数据）
```

> 注意：`explore/`、`diagnose/` 读的是**分学科文件**，不是汇总的 `data/topics.json`。新增学科要保证 `data/<subject>/` 三件文件齐备。

## 4. 本地打开

```bash
cd cn-k12-dxyc2286
python3 -m http.server 8000
# http://localhost:8000/           首页
# http://localhost:8000/explore/?subject=math
# http://localhost:8000/diagnose/?subject=physics
# http://localhost:8000/children/
```

`fetch` 不能跨 `file://`，所以必须起静态服务器；直接双击 HTML 会看到「统计读取失败」提示（已做兜底，不会白屏）。

## 5. PWA 与缓存

- `manifest.webmanifest`：名称「中国 K-12 全学科知识图谱」，主题色 `#0f6e62`；
- `sw.js`：`CACHE_NAME = 'k12-taxonomy-v3'`，预缓存首页、三张页面、`assets/site.css`、`assets/home.js`、`data/stats.json`、`data/subjects.json`；
- **改样式或数据后必须升 `CACHE_NAME`**，否则老用户继续吃旧缓存。

## 6. 改版注意

1. 统计数字**不要写死**在 HTML 里：跑 `python3 scripts/build_stats.py --write` 生成 `data/stats.json`，页面自己读；
2. 新增页面要接同一套 `site-header` / `site-footer`，否则字号与配色会跳；
3. 首页学科卡的学段标签写在 `assets/home.js` 的 `SUBJECT_LABEL` 里，增删学科时同步改；
4. 截图放 `screenshots/`，README 直接引用（`screenshots/01-home.png` 等），改版后重截。
