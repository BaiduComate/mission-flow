---
name: plan
description: 仅在卡片拆分完成后，且用户通过 question 明确选择编写计划文档时使用。用于将已创建的 iCafe 卡片转写为 `tasks.md` 计划文档
metadata:
  version: 0.2.1
---

## 目标

基于 `split` 已创建并经用户确认的 Feature / Story，生成可由 `subagent-impl` 执行的 `.comate/specs/{feature_name}/tasks.md` 计划文档

**开始时声明：**“已进入编写计划文档阶段，我会把已确认的 Story 转写为可审阅、可执行的计划文档。”不得向用户展示 `plan` 这一内部 skill 名称。

## 流程

按顺序完成下面流程。本 skill 生成供用户审阅的计划文档，不使用 TodoWrite

1. 转写 Story 为 Task
2. 编写 `tasks.md`
3. 自审计划文档
4. 请求用户审阅文档

### 转写 Story 为 Task

`tasks.md` 只把 Story 转写为可执行契约，不重新拆分任务。

规则：

1. 一个 Story 对应 `tasks.md` 中一个 Task，不得把一个 Story 拆成多个 Task 或者把多个 Story 合并成一个 Task
2. Story 下 Task 卡片只描述 Story 内部步骤，不进入 `tasks.md` 主任务列表
3. 每个 Task 补充目标、上下文、范围、相关文件、验收标准、测试预期和约束

### 编写 `tasks.md`

写入路径：

```text
.comate/specs/{feature_name}/tasks.md
```

每份计划文档必须以这个头部开始：

```markdown
# [Feature Name] 计划文档

> 面向 agentic workers：REQUIRED SUB-SKILL: 使用 subagent-impl 逐个任务实施此文档。步骤使用 checkbox (`- [ ]`) 语法进行跟踪。

**目标：** [用一句话描述这将构建什么]

**架构：** [用 2-3 句话描述方案；如果没有 doc.md，则基于 split 上下文简述]

**技术栈：** [关键技术/库]

**Feature 卡片：** [Feature 卡片 ID]

**提交绑定策略：** 仅绑定 Story 卡片，不绑定 Feature 或 Story 下 Task

## Story 任务列表

| Task | Story 卡片 | Story 标题 |
| --- | --- | --- |
| Task N | [Story 卡片 ID] | [Story 标题] |
```

每个 Task 使用这个结构：

```markdown
### Task N: [Story 标题]

## 目标
[此任务必须产出的可观察结果]

## 上下文
[此任务如何契合已批准的 doc.md 或 split 上下文]

## iCafe 绑定
- Feature 卡片：[Feature 卡片 ID]
- Story 卡片：[Story 卡片 ID]

## 范围
- 范围内：[此任务可以变更的内容]
- 范围外：[此任务不得执行的相邻工作]

## 相关文件
- 可能修改：`exact/path/to/existing.py`
- 可能创建：`exact/path/to/new_file.py`
- 参考：`exact/path/to/reference.py`

## 验收标准
- [ ] [可观察行为或交付物]
- [ ] [重要边界情况或失败行为]

## 测试预期
- 单元测试：[要覆盖的具体行为]
- 集成/E2E 或运行时验证：[如果可用]
- 命令：`exact command to run`
- 预期结果：[应当通过或可观察到的内容]

## 约束
- [必需的 API、兼容性、依赖、风格或架构约束]
```

### 自审计划文档

`tasks.md` 不得包含占位符或空泛要求。

以下情况属于计划文档自审失败：

- `TBD`、`TODO`、`implement later`、`fill in details`
- “Add appropriate error handling” 但没有说明哪些错误重要
- “Write tests” 但没有具体行为、命令和预期结果
- “Similar to Task N” 但没有重复必要上下文
- 引用了任何任务中都未定义的类型、函数或方法

### 请求用户审阅文档

自审通过后，必须使用 question 工具请求用户审阅文档：

```text
计划文档已完成并保存到 `.comate/specs/{feature_name}/tasks.md`。请您审阅，如果需要调整，请告诉我。
```

问题必须包含两个选项：

- 确认文档：启动子 Agent 进行实施，内部调用 `subagent-impl`
- 修改文档：根据用户意见修改 `tasks.md`，并重新自审

## 状态机

```mermaid
flowchart TD
    A[转写 Story 为 Task] --> C[编写 tasks.md]
    C --> D[自审计划文档]
    D --> E{自审通过?}
    E -->|否| C
    E -->|是| F[请求用户审阅文档]
    F --> G{用户是否确认计划文档?}
    G -->|修改文档| C
    G -->|确认文档| H((启动子 Agent 进行实施))
```
