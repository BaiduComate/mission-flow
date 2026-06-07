# Mission Flow

Mission Flow 是一套面向百度厂内研发流程的 Agent 工作流插件。它用一组可组合的 skills、会话启动注入和工具调用埋点，把“想法 -> 设计 -> 拆卡 -> 计划 -> 实现 -> Review -> 收尾”串成一条可以复用的研发路径。

它的流程很朴素：
1. 让 Agent 在写代码前先弄清楚需求和代码库
2. 在动手前把研发承载落到 iCafe Feature / Story
3. 在实现中保持隔离、验证和审查
4. 在结束时把分支、worktree 和提交绑定处理干净

## 快速开始

Mission Flow 已上架 Comate Plugin 市场。安装和更新都只需要在厂内 IDE 里完成

安装步骤：

1. 打开厂内 IDE，进入 Plugin 市场。
2. 切换到 `Plugins 市场` tab。
3. 搜索 `mission-flow`，点击添加，安装到个人。
4. 回到 `已安装` tab，确认 `mission-flow` 已出现在个人插件列表。

| 进入 Plugin 市场 | 切换到 Plugins 市场 |
| --- | --- |
| ![进入厂内 IDE 的 Plugin 市场](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-0-plugin-market.png) | ![切换到 Plugins 市场 tab](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-1-plugin-tab.png) |

| 搜索并添加插件 | 检查已安装插件 |
| --- | --- |
| ![搜索 mission-flow 并添加插件](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-2-search-mission-flow.png) | ![在已安装 tab 检查 mission-flow](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-3-installed-tab.png) |

安装完成后，新建一个 Chat 对话即可使用。你可以像平时一样描述需求，Comate 会自动召回插件里的 skills，并按照 Mission Flow 规定的流程推进。

如果当前项目还没有 `AGENTS.md`，可以先运行：

```text
/init
```

这个命令会生成 `AGENTS.md` 和 `ARCHITECTURE.md`，帮助后续 Agent 更快理解项目结构、命令、研发流程和代码约束。

| 输入需求 prompt | 自动触发技能流程 |
| --- | --- |
| ![在 Chat 中输入需求 prompt](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/usage-input-prompt.png) | ![Comate 自动触发 mission-flow skills](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/usage-auto-trigger.png) |

参考文档：[mission-flow 插件](https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/_SKPgSwp2G/Hb6OQz5Jc7/En-fwvHu5LG2ZK)

## 工作原理

Mission Flow 从会话开始就介入。

内置的 hook 会把隐藏的 `using-mission-flow` skill 注入到会话上下文里，让 Agent 一开始就知道：任何行动前都要检查相关 skills；会产生代码变更的研发活动必须先走 `think`；后续是否进入 `design`、`plan` 由用户通过 question 确认。

当你提出一个研发需求时，Agent 不应该直接写代码。它会先用 `think` 澄清目标、阅读必要上下文、提出真实可选方案，然后让你选择是否进入设计。

如果你选择设计，`design` 会把方案沉淀到 `.comate/specs/{feature_name}/doc.md`，并派发 reviewer 检查设计文档。设计只解决方案不确定性，不创建卡片，也不写代码。

随后 `split` 会把需求拆成 1 个 iCafe Feature 和若干 Story。这里的 Story 是后续实现和提交绑定的基本单位；Story 下 Task 可以按偏好创建，但不会作为提交绑定单位。

如果你选择写计划，`plan` 会把 Story 转写成 `.comate/specs/{feature_name}/tasks.md`。这个计划不是泛泛的任务清单，而是面向 agentic workers 的执行契约：每个 Task 都要写明目标、上下文、范围、相关文件、验收标准、测试预期和约束。

计划确认后，`subagent-impl` 会逐个 Task 派发实现 subagent，并在实现后派发两个 review subagent 从不同角度把关：先检查是否符合 spec，再检查代码质量。所有任务结束后进入 worktree 收尾。

如果你选择跳过计划，`direct-impl` 会直接基于已确认的 Story 实现，但仍然要求验证、自审、提交绑定 Story，并在完成后进入 `finish-git-worktree`。

这条链路的旁边还有几项辅助能力：`deepwiki` 用于查询仓库 DeepWiki 文档，`icr-code-scan` 和 `icr-code-fixer` 用于代码审查和扫描问题修复。

## 基础流程

1. **using-mission-flow**：会话启动时注入技能使用规则，要求 Agent 在行动前检查相关 skills，并把研发活动导向 Mission Flow 主流程。
2. **think**：任何会产生代码变更的研发活动前必须使用。它负责澄清需求、调研必要上下文、提出方案，并询问是否进入 `design`。
3. **design**：用户选择后使用。它把方案写入 `.comate/specs/{feature_name}/doc.md`，补充 DeepWiki / 代码探索上下文，并通过 reviewer 自检。
4. **split**：在 `think` 或 `design` 后使用。它拆分并创建 iCafe Feature / Story，明确 Story 作为提交绑定单位，并询问是否进入 `plan`。
5. **plan**：用户选择后使用。它把已确认的 Story 转写成 `.comate/specs/{feature_name}/tasks.md`，供后续 subagent 执行。
6. **subagent-impl**：在计划确认后使用。它按 Task 派发 implementer，并依次通过 spec compliance review 和 code quality review。
7. **direct-impl**：在用户选择跳过 `plan` 时使用。它让主 Agent 直接基于 Story 实现，但仍要求验证、自审和 Story 绑定。
8. **using-git-worktrees**：在需要隔离开发空间时使用。它把 worktree 放到 `~/.comate/worktree/<repo>/<verb>-<obj>`，并把基础分支记录为 upstream。
9. **finish-git-worktree**：实现完成后使用。它提供 rebase 后清理、保留分支、丢弃工作三种收尾路径。

## 理念

- **先理解，再实现**：研发任务从 `think` 开始，而不是从改代码开始。
- **Story 是提交单位**：Feature 承载整体需求，Story 承载可验收交付和提交绑定。
- **设计和计划可选，但选择后必须认真执行**：`design` 和 `plan` 由用户确认进入；一旦进入，就要生成可审查、可执行的文档。
- **隔离工作区**：需要实现时优先使用 worktree，保护当前工作区和用户已有改动。
- **证据优先**：完成前要有验证、自审或 review 证据，而不是只说“应该可以”。
- **厂内工具优先**：iCafe、DeepWiki、ICR / aiscan 和 Comate hook 是这个插件的实际上下文，不假装它是一个通用开源脚手架。

## 更新

用户侧更新也通过厂内 IDE 完成：进入 Plugin 市场，如果插件卡片上出现 `Update` 标签，就在已安装插件的更多菜单中点击更新。

| 自动检查更新 | 从更多菜单更新 |
| --- | --- |
| ![进入 IDE 后自动检查插件更新](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/update-auto-check.png) | ![点击更多菜单中的更新按钮](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/update-from-menu.png) |
