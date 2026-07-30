# Code Quality Reviewer 提示词模板

派发 code quality reviewer subagent 时使用此模板。

**目的：** 验证实现构建良好（清晰、有测试、可维护）

**仅在 spec compliance review 通过后派发。**

```
Task tool (general-purpose):
  使用 requesting-code-review/code-reviewer.md 中的模板

  DESCRIPTION: [task summary, from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
```

**除标准代码质量关注点外，reviewer 还应检查：**
- 每个文件是否只有一个清晰职责，并拥有明确定义的接口？
- 任务是否被拆分到可以独立理解和测试？
- 实现是否遵循计划中的文件结构？
- 此实现是否创建了已经很大的新文件，或显著扩大了现有文件？（不要标记已有文件大小；聚焦此变更带来的影响。）

**Code reviewer 返回：** 优点、问题（严重/重要/轻微）、评估
