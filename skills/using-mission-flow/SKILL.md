---
name: using-mission-flow
description: 在任何对话开始时使用。建立如何查找和使用 skills 的流程和概念，子 agent 禁止使用。用来指导 Agent 如何使用 skill
---

> [!IMPORTANT]
> 如果你是作为 subagent 被派发来执行某个具体任务，请跳过这个 skill。

## 指令优先级

Mission flow skills 覆盖默认 system prompt 行为，但**用户指令始终优先**：

1. **用户的显式指令**（AGENTS.md、直接请求）是最高优先级
2. **Mission flow skills** 在冲突时覆盖默认系统行为
3. **默认 system prompt** 是最低优先级

如果 AGENTS.md 说“不要使用 TDD”，而某个 skill 说“始终使用 TDD”，遵循用户指令。用户拥有控制权。

# Skills 使用规则

## 规则

**在任何回复或行动之前调用相关或被请求的 skills。** 哪怕只有 1% 的可能性适用，也意味着你应该调用 skill 来确认。如果发现调用后的 skill 不适合当前情况，你可以不使用它。

## 危险信号

出现这些想法时请停止，这是在给自己开脱：

| 想法                   | 现实                          |
| -------------------- | --------------------------- |
| “这只是一个简单问题”          | 问题也是任务。检查 skills。           |
| “我需要先获得更多上下文”        | skill 检查发生在澄清问题之前。          |
| “让我先探索代码库”           | skills 会告诉你如何探索。先检查。        |
| “我可以快速看一下 git/files” | 文件缺少对话上下文。检查 skills。        |
| “让我先收集信息”            | skills 会告诉你如何收集信息。          |
| “这不需要正式 skill”       | 如果 skill 存在，就使用它。           |
| “我记得这个 skill”        | skills 会演进。读取当前版本。          |
| “这不算任务”              | 行动 = 任务。检查 skills。          |
| “这个 skill 太重了”       | 简单事情也会变复杂。使用它。              |
| “我就先做这一件事”           | 在做任何事之前检查。                  |
| “这样感觉很高效”            | 无纪律的行动会浪费时间。skills 会防止这种情况。 |
| “我知道那是什么意思”          | 知道概念 ≠ 使用 skill。调用它。        |

## Skill 优先级

当多个 skills 都可能适用时，按以下顺序使用：

1. **流程类 skills 优先**（brainstorming、debugging）：它们决定如何处理任务
2. **实现类 skills 其次**（create-skill、create-rule）：它们指导执行

“Let's build X” → 先 brainstorming，再使用实现类 skills。
“Fix this bug” → 先 debugging，再使用领域特定 skills。