# 历史题库「补点 + 补题」作业合同（父代写，工位只读不改）

## 你的活

1. 只读自己那一份作业单：`data/history/_bank_shards/HNN.json`（父代已排好点、题量、**题目 id** 与**答案位**）。
2. 只写一个文件：作业单里的 `out` 绝对路径（形如 `data/history/_bank_shards/HNN_out.json`）。
   ⛔ 不许改 `topics.json` / `questions.json` / 别人的分片。
3. 写完自己跑一次自检，输出最后一行必须是 `RESULT: PASS`：
   ```bash
   cd ~/Desktop/cn-k12-dxyc2286 && python3 scripts/check_history_bank.py --shard <你的 out 绝对路径>
   ```

## 输出形状

```json
{"shard": "H01",
 "topics": [ {"id": "his_h0xx", "name": "…", "type": "conceptual",
              "description": "…", "mastery_criteria": ["…"],
              "diagnostic_question": {"question": "…", "answer": "B"}} ],
 "questions": [ {"id": "his_q0172", "topicId": "his_p011", "prompt": "…",
                 "question": "…（与 prompt 同值）",
                 "options": [{"label":"A","text":"…"},{"label":"B","text":"…"},
                             {"label":"C","text":"…"},{"label":"D","text":"…"}],
                 "answer": "B", "type": "choice", "difficulty": "standard",
                 "explanation": "…"} ]}
```

- `topics` 只给 `isNew: true` 的点写（存量点已有内容，不要重复写）。
- `questions` 覆盖作业单里每个点的全部 `questions[]` 槽位，**id 逐字照抄**，不许增删。

## 硬约束（checker 与本合同逐条对应）

1. **只出选择题**：`type` 一律 `"choice"`，4 个选项、文本互不相同（本轮不出填空/简答，`test_history.py` 的答案分布判据按单选字母统计）。
2. **答案位照抄作业单**：每个槽位给了 `label`，正确选项必须放在该 label 上（父代按 A/B/C/D 轮转，全库分布靠这个守住）。
3. **题干 ≥12 汉字**，且必须带主题限定。⛔ 禁止「关于…下列说法正确的是」这类空壳题；⛔ 禁止「以上都不对/以上都对/都不正确」凑数项。
4. **解析 ≥25 汉字**：写清「为什么对 + 三个干扰项错在哪」或「背景—经过—影响的因果链」，并与 `answer` 一致。禁用「本题考查…」套话占位。
5. **难度**：每点 8 题按 `basic×4 / standard×3 / hard×1` 铺（basic=识记年代/人物/事件；standard=因果/比较；hard=史料推断、长时段影响）。`difficulty` 只认 `basic|standard|hard`。
6. 同一点的 8 道题**不许同问一件事**（换年代、换人物、换角度、换史料），也不许把同一句材料换数字。
7. 历史事实必须准确：年代、条约、人物、制度名以统编教材为准；不确定就换一个你确定的角度出题。⛔ 不编造史料原文。

## 新点的 `topics` 内容

- `type`：多为 `conceptual`；「史料实证/历史解释/时空观念」类可写 `procedural` 或 `reasoning`。
- `description`：**40–120 汉字**，写「本课讲什么 + 核心结论」，不要罗列。
- `mastery_criteria`：1–3 条，每条 ≤50 汉字，用行为动词开头（知道/理解/分析/比较/评价…）。
- `diagnostic_question`：取该点第 1 题的题面与答案（同值）。

## 禁则

- ⛔ 不用 `search_files`（会超时）；只读派单里给的路径。
- ⛔ 不写「扫描件/OCR/抽取」这类元话语。
- ⛔ 不在题干里放未定稿的「（见图）」；纯文字表述。
