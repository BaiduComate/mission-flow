---
name: plan-and-split
description: 在接触代码之前，且已有 doc.md 文档时使用。用来编写 tasks.md 实施计划，并根据用户反馈进行任务拆分，创建相应的 icafe 卡片
---

**开始时声明：** "我正在使用 plan-and-split skill 创建实施计划并拆分任务。"

## 目标

编写 `.comate/specs/{feature_name}/tasks.md` 实施计划文件，内容包含任务目标、范围、上下文、验收标准、约束和验证。

> [!IMPORTANT]
>
> - 假设实施者能力熟练，但对这个代码库和领域并不熟悉
> - 除非 `doc.md` 要求某个具体细节，否则不包含详细的实现代码，将实现选择留给实施者。

## 拆分原则

在定义任务之前，先梳理将创建或修改哪些文件，以及每个文件负责什么。这是确定拆解决策的地方。同时有以下原则：

- 设计边界清晰、接口明确的单元。每个文件都应当只有一个明确职责。
- 当代码能一次性放入上下文中时，agent 对代码的推理效果最好；当文件聚焦时，你的编辑也更可靠。优先选择更小、更聚焦的文件，而不是承担过多职责的大文件。
- 会一起变更的文件应当放在一起。按职责拆分，而不是按技术层拆分。
- 在已有代码库中，遵循既有模式。如果代码库使用大文件，不要单方面重构；但如果你正在修改的文件已经变得难以维护，在计划中包含拆分是合理的。
- 拆分的每个任务都**必须**是一个连贯的实施单元，subagent 可以完成、测试、提交并汇报该任务。

## 文档结构

### 计划文档头部

**每个计划 MUST 以这个头部开始：**

```markdown
# [Feature Name] 实施计划

> **面向 agentic workers：** REQUIRED SUB-SKILL: 使用 execute-task-plan 逐个任务实施此计划。步骤使用 checkbox (`- [ ]`) 语法进行跟踪。

**目标（Goal）：** [用一句话描述这将构建什么]

**架构（Architecture）：** [用 2-3 句话描述方案]

**技术栈（Tech Stack）：** [关键技术/库]

---
```

### 各 task 结构

在 `tasks.md` 中为每个任务编写一个类似这样的章节。

```markdown
### Task N: [组件名称]

## 目标（Goal）

[此任务必须产出的可观察结果]

## 上下文（Context）

[此任务如何契合已批准的 `doc.md`、架构和相邻任务]

## 范围（Scope）

- 范围内（In scope）：[此任务可以变更的内容]
- 范围外（Out of scope）：[此任务不得执行的相邻工作]

## 相关文件（Relevant Files）

- 可能修改（Likely modify）：`exact/path/to/existing.py`
- 可能创建（Likely create）：`exact/path/to/new_file.py`
- 参考（Reference）：`exact/path/to/reference.py`

## 验收标准（Acceptance Criteria）

- [ ] [可观察行为或交付物]
- [ ] [重要边界情况或失败行为]
- [ ] [集成预期]
- [ ] [回归预期]

## 测试预期（Testing Expectations）

- 单元测试（Unit tests）：[要覆盖的具体行为]
- 集成/E2E 或运行时验证（Integration/E2E or runtime verification）：[如果可用]
- 命令（Commands）：`exact command to run`
- 预期结果（Expected result）：[应当通过或可观察到的内容]

## 约束（Constraints）

- [必需的 API、兼容性、依赖、风格或架构约束]

## 备注（Notes）

[仅包含非显而易见的指导。除非必要，不要规定实现方式。]
```

## 设计要点

### 不得包含占位符

每个任务都必须包含具体契约。以下情况属于**编写计划失败**：

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"，但没有说明哪些情况重要
- "Write tests"，但没有具体行为、命令和预期结果
- "Similar to Task N"，但没有重复相关上下文
- 在目标和约束已经足够时，规定每一行代码
- 引用了任何任务中都未定义的类型、函数或方法

### 必须遵守的规范

- 始终使用精确文件路径
- 结果和验收标准优先于实现代码
- 精确的验证命令，以及预期输出
- 优先使用行为层面的验证：单元测试，以及在可用时的集成/运行时检查。
- `tasks.md` 不要包含完整实现代码，除非精确的代码/API/配置本身就是需求
- DRY、YAGNI、TDD、频繁提交

## 执行交接

完成 `tasks.md` 后，向用户声明："计划已完成并保存到 `.comate/specs/{feature_name}/tasks.md`。开始 subagent 驱动的执行流程，每个任务派发一个新的 subagent，并在任务之间进行审查。"。并调用 `execute-task-plan` skill 进行开发流程：
