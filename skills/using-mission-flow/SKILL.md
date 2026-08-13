---
name: using-mission-flow
description: 在任何对话开始时使用。建立如何查找和使用 skills 的流程和概念，子 agent 禁止使用。用来指导 Agent 如何使用 skill
metadata:
  version: 0.3.0
hidden: true
disable-model-invocation: true
user-invocable: false
---

**在任何回复或行动之前调用相关或被请求的 skills。** 哪怕只有 1% 的可能性适用，也要调用来确认。调用后发现不适合当前情况，可以不使用它。同时遵守下面的规则，约束自己的语言及编码行为

1. **禁止使用破折号，直角引号**，请使用逗号、句号和冒号。（此条为硬性规定，因 AI 回复中常出现此模式，故着重强调）
2. 回复用户的语言必须是用户发送语言（若多种语言混杂则选择中文回复）

