---
name: using-mission-flow
description: 在任何对话开始时使用。建立如何查找和使用 skills 的流程和概念，子 agent 禁止使用。用来指导 Agent 如何使用 skill
---

> [!IMPORTANT]
> 如果你是作为 subagent 被派发来执行某个具体任务，请跳过这个 skill。

## 指令优先级

Mission flow skills 覆盖默认 system prompt 行为，但**用户指令始终优先**：

1. 用户的显式指令（AGENTS.md、直接请求）是**最高**优先级
2. Mission flow skills 在冲突时覆盖默认系统行为
3. 默认 system prompt 是**最低**优先级

如果 AGENTS.md 说“不要使用 TDD”，而某个 skill 说“始终使用 TDD”，遵循用户指令。用户拥有控制权。

# Skills 使用规则

## 规则

**在任何回复或行动之前调用相关或被请求的 skills。** 哪怕只有 1% 的可能性适用，也意味着你应该调用 skill 来确认。如果发现调用后的 skill 不适合当前情况，你可以不使用它。

> [!IMPORTANT]
> - **不要**因为用户给出的是一个简单任务就放弃调用 skill
> - 同理，你如果想探索代码库，也必须按照 skill 的指示去探索，skill 会教你如何收集信息，而不是直接去派发子 agent

## Skill 优先级

当多个 skills 都可能适用时，按以下顺序使用：

1. **流程类 skills 优先**（think-and-design、debugging）：它们决定如何处理任务
2. **实现类 skills 其次**（create-skill、create-rule）：它们指导执行

“帮我增加 xxx 功能” → 先 think-and-design，再使用实现类 skills。
“修复 xxx bug” → 先 debugging，再使用领域特定 skills。
