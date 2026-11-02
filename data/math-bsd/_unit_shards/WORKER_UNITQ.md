# 北师大版数学「单元点诊断题」工位合同 · 初高中

## 你的活

读派单 `data/math-bsd/_unit_shards/U###.json`（含 3 个单元：`unitId / name / chapter / lessonNames[] / qidRange[5]`），
为**每个单元**写 **5 道诊断题**，落到派单 `out` 指定的 `data/math-bsd/_unit_parts/U###.json`：

```json
{"units": [
  {"unit": <派单里那一整个 unit 对象，原样照抄>,
   "questions": [ <5 道题，id 依次取 qidRange[0..4]> ]}
]}
```

⛔ `unit` 对象必须**原样整段照抄**（不要精简字段）；⛔ 题 id 只能用派单给的 `qidRange`，不许自编号；
⛔ 只写自己这一份 `_unit_parts` 文件，不改 `topics.json` / `questions.json` / 别人的分片。

## 5 道题的类型配方（逐单元固定，写死以免全库比例失衡）

| 题序 | type | difficulty | 必备字段 |
| --- | --- | --- | --- |
| 1 | `choice` | `basic` | `options` 4 项 ＋ `choices` 与 `options` **完全相同** ＋ `answer` 为 A/B/C/D |
| 2 | `choice` | `standard` | 同上 |
| 3 | `fill` | `standard` | `choices: []`，`answer` 为答案文本（可含符号） |
| 4 | `numeric` | `standard` | `choices: []`，`answer` 为数值字符串，`verify` 为可 `eval` 的算式且结果等于 `answer`（如 `answer: "7"`, `verify: "3+4"`） |
| 5 | `short-answer` | `hard` | `choices: []`，`answer` 为一句话结论，另给 `keypoints` 数组 ≥2 条 |

五道题都要：`prompt`（**≥12 字**，全库唯一，别与别单元撞句）、`explanation`（**≥20 字**，讲清为什么）、
`topicId` 与 `topicIds` 都写该单元的 `unitId`。

## 内容要求

- 题目要落在**该单元的核心方法**上（看 `lessonNames` 列出的课时），是「本单元学完能判断/能不能算对」的题，
  不是课时细节的复读；四个单元题之间不要互相重复套路。
- 用词按学段（初中 / 高中），不超纲；数值题的数字自己算准，`verify` 必须真能算出 `answer`。
- 纯文本：禁 Markdown 符号（`* _ # [ ] |`）、禁 LaTeX、禁 HTML；公式写 `x²`、`√2`、`a²+b²=c²` 这类纯文本。
- 选择题四个选项**互不相同**，干扰项要像真错法（符号错、漏条件、混淆概念），不能凑数。

## 自检（交前必跑）

```bash
cd ~/Desktop/cn-k12-dxyc2286
python3 - <<'EOF'
import json,re,sys
d=json.load(open("data/math-bsd/_unit_parts/U###.json"))   # ← 换成你自己的文件名
err=[]
for u in d["units"]:
    qs=u["questions"]; uid=u["unit"]["id"]
    if len(qs)!=5: err.append(f"{uid} 题数 {len(qs)}")
    if len({q["type"] for q in qs})<3: err.append(f"{uid} 题型不足 3 种")
    if {q["difficulty"] for q in qs}!={"basic","standard","hard"}: err.append(f"{uid} 三档不齐")
    for q in qs:
        if len(q["prompt"])<12: err.append(q["id"]+" 题干过短")
        if len(q["explanation"])<20: err.append(q["id"]+" 解析过短")
        if re.search(r"[*_#\[\]|]", q["prompt"]+q["explanation"]): err.append(q["id"]+" 有 Markdown 符号")
        if q["type"]=="choice":
            o=q["options"]
            if len(o)!=4 or q["answer"] not in [x["label"] for x in o] or len({x["text"] for x in o})!=4:
                err.append(q["id"]+" 选项不合规")
            if q["choices"]!=o: err.append(q["id"]+" choices≠options")
        else:
            if q.get("choices"): err.append(q["id"]+" 非选择题 choices 应为空")
        if q["type"]=="numeric" and str(eval(q["verify"]))!=str(q["answer"]):
            err.append(q["id"]+f" verify 不符 {q['verify']} ≠ {q['answer']}")
        if q["type"]=="short-answer" and len(q.get("keypoints") or [])<2:
            err.append(q["id"]+" keypoints<2")
print("ERR",err) if err else print("OK")
EOF
```

末行必须是 `OK`。

## 交付

文件 UTF-8 无 BOM。回复一行：`U### / 单元数 / 每单元 5 题 / 自检 OK`。
