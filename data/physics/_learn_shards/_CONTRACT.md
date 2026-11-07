# 人教版物理 · 学层精讲分片合同（PHYS_L01–L54）

> 只读本文件 ＋ 自己的分片 JSON ＋ 分片 `text_file` 指向的本册教材全文。
> **只写 `data/physics/learn/_parts/<册>/<你的 shard>_out.json`**；不改仓库其它文件、不改 checker。

## 1. 输入

`data/physics/_learn_shards/PHYS_Lnn.json`：
- `lessons[]`：`topicId / title / chapter / description / mastery_criteria / standards`（课标原句）
  ＋ **`excerpt`：本课教材节选（已裁好，直接用）**
- `text_file`：本册教材全文绝对路径（**只在需要补一句节选里没有的原文时才 grep**；⛔ 不要通读整册）
- `out`：落盘目录

## 2. 落盘形状

```json
{"book": "九年级上册",
 "lessons": [{"topicId": "chem_p001", "title": "物质的变化和性质",
              "markdown": "## 一、开场\n…", "words": 1680}]}
```
文件名：`<你的 shard>_out.json`（如 `CHEM_L01_out.json`）。

## 3. 七段标题（逐字，不许改写）

```
## 一、开场
## 二、课本原文
## 三、费曼翻译
## 四、例题精讲
## 五、易错点拨
## 六、五步学习法
## 七、自查清单
```

## 4. 内容硬指标

- 全篇 **1200–2600 汉字**（`words` 必须等于实测汉字数，用 `len(re.findall(r"[\u4e00-\u9fa5]", md))` 现算）。
- **二、课本原文**：`> ` 开头的引文 **≥2 处**，直接取自该课的 `excerpt`（**逐字**，标点空格可不同、字要一样），每处后面紧跟「这句话的意思是……」解释。
  ⛔ 不要凭印象写原文；excerpt 里挑完整的句子。
- **四、例题精讲**：2 道例题，各配 `❌ 常见错解` 与 `✅ 正确解法`。
- **六、五步学习法**：350–700 汉字，五条**逐字固定序**：
  ①每天锻炼一个小时 ②扎实掌握第一个知识点 ③能积微者速成 ④运用对标思维突破学习困境 ⑤运用杠铃法则缓解学习疲劳。
  每条写 72–88 汉字（整节自然落在 380–450）。
- **七、自查清单**：`- [ ]` 打勾项 **≥3 条**。
- ⛔ 禁 `**`、`##`（除七段标题）、`|`、`$`、`\frac`；⛔ 禁写「扫描件 / OCR / 抽取 / 文字层 / 分片」等元话语。
- ⛔ 正文里不要出现「开场」「课本原文」「费曼翻译」「例题精讲」「易错点拨」「自查清单」这些词（checker 按关键词切节，提前出现会把该段判成空）。

## 5. 自检（必跑）

```bash
python3 scripts/check_chem_learn.py "data/physics/learn/_parts/<册>/PHYS_Lnn_out.json"
```
到 `RESULT: PASS`。报错改自己的文件，⛔ 不改 checker、不改 `_text`。

## 6. 汇报

```
DONE PHYS_Lnn | lessons=4 | selfcheck=PASS
```
