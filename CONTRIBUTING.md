# 贡献指南

感谢你考虑为 cn-k12-dxyc2286 做出贡献！

## ⚠️ 重要声明

**本项目的数据是 AI 生成的初稿，未经教师审核。** 在用于正式教学之前，必须经过一线教师审核。

## 如何贡献

### 1. 报告问题

发现知识点错误、先修关系问题或题目答案错误，请 [提交 Issue](https://github.com/your-username/cn-k12-dxyc2286/issues/new)。

请使用以下模板：

```markdown
**学科**：数学/英语/...
**年级**：X年级
**知识点ID**：mat_p001
**问题类型**：知识点描述错误 / 先修关系错误 / 题目答案错误 / 其他
**问题描述**：...
**建议修正**：...
```

### 2. 提交修正

如果你是教师或学科专家，欢迎直接提交 PR 修正数据。

#### 修正流程

1. Fork 本仓库
2. 创建分支：`git checkout -b fix/math-grade3`
3. 修改对应的 JSON 文件
4. 提交：`git commit -m "fix: 修正三年级分数知识点描述"`
5. 推送：`git push origin fix/math-grade3`
6. 提交 Pull Request

### 3. 审核标准

我们特别需要以下方面的审核：

- **知识点拆分粒度**：是否符合教学实际
- **先修关系**：hard/soft 边是否合理
- **诊断题**：题目是否准确、答案是否正确
- **课标对齐**：curriculumRef 是否正确对应课标条目

## 数据格式规范

### topics.json

```json
{
  "id": "mat_p001",
  "name": "知识点名称",
  "subject": "math",
  "grade": 1,
  "semester": "fall",
  "chapter": "完整章节路径",
  "description": "学生应掌握的内容描述",
  "tags": ["课标主题", "子主题"],
  "prerequisites": ["先修知识点ID"],
  "curriculumRef": "cms-2022:1.1.1"
}
```

### dependencies.json

```json
{
  "from": "mat_p001",
  "to": "mat_p002",
  "type": "hard"
}
```

- `hard`：必须先掌握才能学习后续知识点
- `soft`：建议先掌握，但不是必须

### questions.json

```json
{
  "id": "mat_q001",
  "topicId": "mat_p001",
  "question": "题目内容",
  "options": [
    {"label": "A", "text": "选项A"},
    {"label": "B", "text": "选项B"}
  ],
  "answer": "A",
  "type": "choice",
  "difficulty": "easy",
  "explanation": "答案解析"
}
```

## 许可证

通过提交 Pull Request，你同意将你的贡献以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可证发布。

## 联系方式

- 问题反馈：[GitHub Issues](https://github.com/your-username/cn-k12-dxyc2286/issues)
- 讨论交流：[GitHub Discussions](https://github.com/your-username/cn-k12-dxyc2286/discussions)
