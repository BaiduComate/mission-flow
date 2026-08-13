# Mission Flow

Mission Flow 是一套面向百度厂内研发流程的轻量 Agent 工作流插件。只做两件事：会话启动时注入一份常驻的技能使用规则，再用少量 skill 覆盖研发过程中最容易出错的环节，需求澄清、改动判据、工作区隔离、会话交接和文档写作

## 快速开始

Mission Flow 已上架 Comate Plugin 市场，安装和更新都在厂内 IDE 里完成。

1. 打开厂内 IDE，进入 Plugin 市场。
2. 切换到 `Plugins 市场` tab。
3. 搜索 `mission-flow`，点击添加，安装到个人。
4. 回到 `已安装` tab，确认 `mission-flow` 出现在个人插件列表。

| 进入 Plugin 市场 | 切换到 Plugins 市场 |
| --- | --- |
| ![进入厂内 IDE 的 Plugin 市场](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-0-plugin-market.png) | ![切换到 Plugins 市场 tab](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-1-plugin-tab.png) |

| 搜索并添加插件 | 检查已安装插件 |
| --- | --- |
| ![搜索 mission-flow 并添加插件](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-2-search-mission-flow.png) | ![在已安装 tab 检查 mission-flow](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/install-step-3-installed-tab.png) |

安装完成后新建一个 Chat 对话即可使用。像平时一样描述需求，Comate 会自动召回插件里的 skills。

| 输入需求 prompt | 自动触发技能流程 |
| --- | --- |
| ![在 Chat 中输入需求 prompt](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/usage-input-prompt.png) | ![Comate 自动触发 mission-flow skills](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/usage-auto-trigger.png) |

如果项目还没有 `AGENTS.md`，先运行：

```text
/init
```

它会生成 `AGENTS.md` 和 `ARCHITECTURE.md`，让后续会话更快掌握项目结构、命令、研发流程和代码约定。

## 技能

| 技能 | 何时触发 | 做什么 |
| --- | --- | --- |
| `think` | 动手改代码前 | 成轮提问把需求收敛到可实现，能自己查的信息派子代理去查，最后确认本次推进到哪一步 |
| `impl` | 编写或修改代码时 | 给出可判定的改动判据；将要改的文件不是本轮产出且尚未提交时，先建 worktree 隔离 |
| `worktree` | 需要与当前工作区隔离，或要收尾开发分支时 | 约定 worktree 路径并把基础分支记进 upstream；收尾给出 rebase、保留、丢弃三条路径 |
| `handoff` | 需要把当前会话交给另一个 agent 时 | 写一份交接文档到系统临时目录，并给出绝对路径 |
| `write` | 写或改中文文稿时 | 去掉 AI 味同时保留作者原意，覆盖普通文稿和发版说明 |
| `using-mission-flow` | 每次会话启动 | 由 hook 注入，约束 skill 的调用时机和回复语言，不由用户直接调用 |

`think` 和 `worktree` 会读取项目里的 `workflow.md`：其中声明了推进范围或默认收尾方式时按它执行，不再询问。

## 工作原理

会话启动时，`SessionStart` hook 把隐藏的 `using-mission-flow` 注入上下文，让 Agent 在任何回复或行动之前先检查相关 skills。另外两个 hook 挂在 `PostToolUse` 的 `Skill` 和 `Bash` 上，用于统计技能调用和识别 iCafe 建卡。

Hook 由 `hooks/mission-flow-hook` 启动脚本调起，优先使用仓库内置的 darwin-arm64 与 linux-amd64 二进制，其他平台按需下载。任何一步失败都 fail open，不阻塞会话。

## DUCC

仓库同时包含 DUCC / Claude Code 的插件清单与 hook 配置，本地开发可以直接加载目录：

```bash
ducc --plugin-dir /path/to/mission-flow
```

DUCC 产物会额外内置 iCafe skill。上报时附带 `client_type=ducc` 和可选的客户端版本；`session_id` 是后端完整定位会话的标识，也是跨 hook 归因的唯一会话键，当前 DUCC 不提供 `conversation_id`，插件不会用 `session_id` 伪造该字段。

Comate 与 DUCC 的完整打包、发布和验证步骤见[发版流程](https://github.com/BaiduComate/mission-flow/blob/main/docs/releasing.md)。维护者本机的发版脚本不提交到插件仓库。

## 理念

- 先理解再实现：研发任务从 `think` 开始，而不是从改代码开始。
- 隔离工作区：需要动手时优先用 worktree，保护当前工作区和用户已有改动。
- 证据优先：完成前要有验证或自审证据，而不是只说应该可以。
- 如无必要勿增实体：防御性编码要有调研支撑，不凭感觉加。
- 厂内工具优先：iCafe、iCode 和 Comate hook 是这个插件的实际上下文，它不假装是通用开源脚手架。

## 更新

用户侧更新也在厂内 IDE 完成：进入 Plugin 市场，插件卡片出现 `Update` 标签时，在已安装插件的更多菜单里点击更新。

| 自动检查更新 | 从更多菜单更新 |
| --- | --- |
| ![进入 IDE 后自动检查插件更新](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/update-auto-check.png) | ![点击更多菜单中的更新按钮](https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/mission-flow/readme/update-from-menu.png) |

参考文档：[mission-flow 插件](https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/_SKPgSwp2G/Hb6OQz5Jc7/En-fwvHu5LG2ZK)
