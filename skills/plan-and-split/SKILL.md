---
name: plan-and-split
description: 在接触代码之前，且已有 doc.md 文档时使用。基于 split 创建 iCafe Feature/Story，并将 Story 转写为 tasks.md 实施计划
---

**开始时声明：** "我正在使用 plan-and-split skill 创建 iCafe 卡片并编写实施计划。"

## 目标

先创建 iCafe Feature/Story 卡片，再将每个 Story 写成 `.comate/specs/{feature_name}/tasks.md` 中的一个 Task。

> [!IMPORTANT]
>
> - 假设实施者能力熟练，但对这个代码库和领域并不熟悉
> - 除非 `doc.md` 要求某个具体细节，否则不包含详细的实现代码，将实现选择留给实施者。

## iCafe 拆卡前置流程

生成 `tasks.md` 前，必须完成 iCafe 拆卡并获得卡片编号。

1. 基于已批准的 `doc.md` 理解整体需求。
2. 读取 `../split/SKILL.md`，以其 Story 拆分规则为唯一拆分标准：
   - 读取用户偏好
   - 创建 Feature 卡片
   - 创建 Story 卡片
   - **必须**使用 question 工具询问用户是否创建 Story 下 Task 卡片
3. Feature 描述整体需求。
4. Story 是 `tasks.md` 的任务单位和后续提交绑定单位。
5. Story 下 Task 只描述内部步骤，不进入 `tasks.md` 主任务列表。
6. 如果无法创建或确认 Story 卡片，停止流程，不生成 `tasks.md`。

## 实施契约补充原则

`tasks.md` 只把 Story 转写为可执行契约，不重新拆分任务。

- 一个 Story 对应 `tasks.md` 中一个 Task。
- 不得把一个 Story 拆成多个 Task。
- 不得把多个 Story 合并成一个 Task。
- 如果 Story 边界不合理，回到 `split` 拆卡流程调整。
- 每个 Task 补充目标、上下文、范围、相关文件、验收标准、测试预期和约束。

## 文档结构

### 计划文档头部

**每个计划 MUST 以这个头部开始：**

```markdown
# [Feature Name] 实施计划

> **面向 agentic workers：** REQUIRED SUB-SKILL: 使用 execute-task-plan 逐个任务实施此计划。步骤使用 checkbox (`- [ ]`) 语法进行跟踪。

**目标（Goal）：** [用一句话描述这将构建什么]

**架构（Architecture）：** [用 2-3 句话描述方案]

**技术栈（Tech Stack）：** [关键技术/库]

**Feature 卡片（Feature Card）：** [Feature 卡片 ID]

**提交绑定策略（Commit Binding）：** 仅绑定 Story 卡片，不绑定 Feature 或 Story 下的 Task

## Story 任务列表

| Task   | Story 卡片      | Story 标题   |
| ------ | --------------- | ------------ |
| Task N | [Story 卡片 ID] | [Story 标题] |

---
```

### 各 task 结构

在 `tasks.md` 中为每个任务编写一个类似这样的章节。

```markdown
### Task N: [Story 标题]

## 目标（Goal）

[此任务必须产出的可观察结果]

## 上下文（Context）

[此任务如何契合已批准的 `doc.md`、架构和相邻任务]

## iCafe 绑定

- Feature 卡片：[Feature 卡片 ID]
- Story 卡片：[Story 卡片 ID]

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
