# 教材版本映射（data/mappings/）

本目录放「**教材版本 / 册次 → 知识点**」的映射。目的：同一批知识点要能对应到人教版、北师大版、沪教版、
山东五四制等不同教材的册次与课次，供学校按自己用的书来找知识点。

## 文件

| 文件 | 内容 | 生成方式 |
|---|---|---|
| `volume-map.json` | 学科 → 册（一年级上册 / 必修第一册 …）→ 知识点数、年级、章节数 | **自动生成**：`python3 scripts/build_standards_index.py`，取自 `chapter` 字段 |
| `schema-mapping.json` | 版本映射文件的 JSON Schema | 手写 |
| `renjiao-math.example.json` | 人教版数学的**映射样例**（结构演示，非全量） | 手写样例 |

## 版本映射文件格式

```json
{
  "subject": "math",
  "edition": "沪教版",
  "stage": "小学",
  "alignedTo": "人教版",
  "generated": "2026-10-26",
  "note": "只写两版教材的对应关系，不重复知识点正文",
  "volumes": [
    {
      "volume": "一年级上册",
      "chapters": [
        {
          "chapter": "第一单元 10以内的数",
          "topicIds": ["mat_p001", "mat_p002"],
          "confidence": "exact",
          "source": "沪教版一年级上册目录 · 2024年印"
        }
      ]
    }
  ]
}
```

- `topicIds` 必须是 `data/<subject>/topics.json` 里存在的 id；
- `confidence`：`exact`（课次一一对应）/ `partial`（合并或拆分）/ `inferred`（按主题推测，需教师复核）；
- `source` 写清依据（哪版教材、哪一年印次、目录还是页码），**不许凭印象填**。

## 怎么新增一个版本

1. 拿到该版本教材目录（拍照或 PDF），按册整理「单元 → 课次」；
2. 对每一课次，找本库中对应的 `topicIds`（可用 `explore/` 页面按年级浏览）；
3. 落盘 `data/mappings/<edition>-<subject>.json`，跑：
   ```bash
   python3 scripts/validate_mappings.py        # 校验 id 存在、字段合法
   ```
4. 在 PR 里附上目录出处，`confidence: inferred` 的部分要单独列出待教师复核。

## 现状

- `volume-map.json` 覆盖 17 学科、全部 1924 个知识点的册次分布（自动生成，可直接用）；
- 其它教材版本的**逐课次映射尚未填充** —— 这需要人工对照教材目录，不能由 AI 猜。
