# 北师大版数学（math-bsd）· 知识点「内容层」工位合同 · WF

## 你的活

读派单 `data/math-bsd/_fill_shards/F<NN>.json`，为其中**每个点**补齐三个字段，落到
`data/math-bsd/_fill_parts/F<NN>.json`（UTF-8、无 BOM）：

```json
{"shard": "F01",
 "points": [
   {"id": "mbs_p001",
    "description": "……（40–120 汉字）",
    "mastery_criteria": ["……", "……"],
    "standards": [{"id": "mat-2022:1.SD.01", "quote": "……"}]}
 ]}
```

⛔ **只写这三个字段**。`id / name / chapter / grade / semester` 一律不动（那是骨架权威）；
不写题库、不写卷、不写 `_parts`（学层）、不碰别的分片。

## 字段口径（门禁逐条查）

1. **`description`：40–120 汉字**（按 `[\u4e00-\u9fa5]` 数，标点不算）。
   写「这一课教什么 + 学生要会做什么」，用教师看的书面语，**不要**写「本课是…」这类空话套话开头，
   直接说内容，例如：`借助分苹果的情境理解平均分的含义，会用除法算式表示平均分的过程与结果，能说出算式中每个数表示什么。`
2. **`mastery_criteria`：2–3 条**，每条 15–40 汉字，必须是**可观察、可计数**的行为（「能说出…」「会用…计算…题」「能指出…」），
   不许写「理解…的含义」这种不可测表述当唯一标准。
3. **`standards`：1–2 条**，`id` 与 `quote` **从派单的 `standards_pool` 里逐字复制**（不许改写、不许自拟、不许拼接）。
   挑与该点最贴合的条目；同一册内的点尽量别全挤在同一条上（一条覆盖 3–5 个点是正常的）。
   ⛔ 池里没有的 id 一律不许出现——门禁会按全仓同 id 原文池逐字比对，编造直接判不合格。

## 怎么知道这一课教什么

- 派单每个点带 `ocr_dir`（如 `/tmp/mbsd/mbsd1a/ocr`）：
  ① 先按点名的关键词 `grep` 该目录的 `pNNN.txt`；命中就读那一页及其后 2–3 页；
  ② `grep` 不到就用 `chapter` 里的**单元名**定位起始页，再顺读 5–10 页（北师大版小学按「情境+问题串」编排，
     一个课时通常 2 页）；
  ③ 依据教材里的**实际例题、情境名、练习题**写 description 与掌握标准，不要按常识空写。
- `ocr_dir` 为 `null` 的点（四下 / 五下 / 六下，教材库缺该册 PDF）：按**点名 + 同一单元前后课时**推断内容，
  只写该学段能站得住的内容（如「认识小数的意义」不写「小数的性质」），`standards` 照旧从池里挑，
  并在你汇报里单列「无教材依据的点 id」清单。
- 遇到 OCR 明显错字（`巳` 当 `已`、`囗` 当 `口`）按正确字写；不要把 OCR 残片（`@ © 月`）写进 description。

## 自检（不跑不许交）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 - <<'EOF'
import json,re,sys
p='data/math-bsd/_fill_parts/F01.json'
d=json.load(open(p,encoding='utf-8'))
pool={x['id']:x['quote'] for x in json.load(open('data/math-bsd/_fill_shards/F01.json',encoding='utf-8'))['standards_pool']}
bad=[]
for x in d['points']:
    n=len(re.findall(r'[\u4e00-\u9fa5]',x.get('description','')))
    if not 40<=n<=120: bad.append((x['id'],'description 汉字',n))
    if not 2<=len(x.get('mastery_criteria') or [])<=3: bad.append((x['id'],'mastery 条数',len(x.get('mastery_criteria') or [])))
    if not 1<=len(x.get('standards') or [])<=2: bad.append((x['id'],'standards 条数',len(x.get('standards') or [])))
    for s in x.get('standards') or []:
        if pool.get(s.get('id'))!=s.get('quote'): bad.append((x['id'],'quote 与池不一致',s.get('id')))
print('点',len(d['points']),'| 不合格',len(bad))
for b in bad[:10]: print(' -',b)
sys.exit(1 if bad else 0)
EOF
```

末行必须是 `点 N | 不合格 0`。

## 汇报格式

一行：分片号 / 点数 / description 汉字区间（最小–最大）/ 课标条目用了几条不同 id / 无教材依据的点数 /
自检末行。不要贴正文。
