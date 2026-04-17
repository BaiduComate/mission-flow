---
name: icafe-official
description: |
  当用户涉及以下任何场景时，应使用此技能:
  - 查询、创建、更新 iCafe 卡片 (Card/Issue)，包括 Story、Bug、Task、Epic
  - 管理卡片评论 (Comment)，如新建评论、获取评论
  - 查询卡片的流程状态 (Status)、操作历史和状态变更记录
  - 查询空间 (Space) 信息、卡片类型、字段定义
  - 管理迭代计划 (Plan)、里程碑 (Milestone)
  - 查询研发数据链 (DevInfo): 代码评审、代码合入、部署等
  - 使用 IQL 查询语言按条件筛选卡片
  - 在 iCode (Git/Gerrit) 提交代码时需要绑定 iCafe 卡片
  - 发起代码评审 (CR) 需要关联卡片信息
  - 使用 AI 对卡片内容进行预审 (ai-pre-review)
  - 使用 AI 根据卡片内容自动生成代码 (ai-codegen)
metadata:
  cli_version: "0.1.0"
allowed-tools:
  - Bash(*icafe-cli *)
  - Bash(*/.icafe-cli/bin/icafe-cli *)
  - Bash(ICAFE_CLI_VERSION=* bash -c *)
  - Bash(git log *)
  - Bash(git rev-parse *)
  - Bash(git remote *)
  - Bash(git diff *)
  - Bash(git status *)
  - Bash(git branch *)
  - Read(*icafe-official*)
  - Read(*icafe-official/**)
  - Read(*icafe-official/**/*)
---

# iCafe CLI

iCafe Assistant 通过 `icafe-cli` 命令行工具与 iCafe 平台交互，支持卡片管理、计划管理、研发数据查询和 AI 预审/代码生成。

## 安装与认证

### 首次执行前检查（每次会话仅需一次）

```bash
icafe-cli version
```

- **command not found** → 尝试 `~/.icafe-cli/bin/icafe-cli version`，仍失败则安装:
  ```bash
  curl -fsSL https://issue-luigi-public.bj.bcebos.com/icafe-cli/install_icafe_cli.sh | ICAFE_CLI_VERSION=0.1.0 bash
  ```
- **版本低于 `0.1.0`** → 执行上面安装命令覆盖升级
- **版本正常** → 后续直接使用

### 未登录错误 (auth_failed, exit code 1)

```bash
icafe-cli login --token <ugate-token>    # Token 获取: https://uuap.baidu.com/agent/token
icafe-cli login status                    # 查看登录状态
```

## 核心约束

1. **涉及 Git/iCode/CR/Gerrit 时禁止问用户**: 当用户涉及 git commit、代码提交、发起评审 (CR)、iCode、Gerrit 等场景需要绑定卡片时，**必须全自动决策，禁止让用户选空间、选卡片、选类型**。**必须先调 `card smart-find` 搜索已有卡片，禁止跳过直接建卡**。详见 [零交互版 Git 绑定工作流](references/git-auto-bindcard-workflow.md)
2. **space 不要猜**: 其他场景缺少空间时优先 `card smart-find` 推断，或 `space latest` 获取，或询问用户
2. **space 用 prefixCode**: `--space myspace`（字符串），不是数字 ID
3. **detail 必须 HTML**: `--detail "<p>内容</p>"`，Markdown 需先转换（见下方对照表）
4. **字段名用中文**: `--fields "负责人=zhangsan,优先级=P1-High"`
5. **card get/query 始终用 --brief**: 仅 `card get` 和 `card query` 支持 `--brief`，节省 70-90% 上下文。`smart-find` 本身已是精简输出，不支持也不需要 `--brief`
6. **命令路径**: 如果 `icafe-cli` 报 command not found，改用完整路径 `~/.icafe-cli/bin/icafe-cli`（安装脚本的 PATH 配置仅在新终端生效）

## 命令总览

```
icafe-cli
├── card                          卡片管理
│   ├── get                       获取卡片详情 (--space, --sequence, --brief)
│   ├── create                    创建卡片 (--space, --title, --type)
│   ├── update                    更新卡片 (--space, --sequence, +可选字段)
│   ├── query                     查询卡片 (--space, --iql, --brief)
│   ├── next-statuses             可流转的目标状态 (--space, --sequence)
│   ├── current-status            当前流程状态 (--space, --sequence)
│   ├── history                   全量操作历史 (--space, --sequences)
│   └── status-changes            状态流转历史 (--space, --sequences)
├── comment                       评论管理
│   ├── create                    添加评论 (--space, --sequence, --content)
│   ├── get                       获取评论 (--space, --sequence)
│   └── update                    修改评论 (--space, --comment-id, --content)
├── space                         空间管理
│   ├── latest                    最近访问的空间
│   ├── tree                      空间树 (--username, --permission)
│   ├── issue-types               卡片类型列表 (--space)
│   ├── type-fields               类型字段定义 (--space, --type)
│   ├── type-statuses             类型流程状态 (--space, --type)
├── plan                          计划管理
│   ├── list / get / create / update-date / milestones
├── devinfo                       研发数据链
│   ├── card                      卡片研发数据 (--space, --sequences)
│   └── active-cards              有研发活动的卡片 (--space)
├── ai-pre-review                 卡片预审 (AI)
│   ├── start                     发起预审 (--space, --sequence; --rules 可选)
│   ├── result                    查询结果 (--conversation-id 或 --space+--sequence)
│   └── rules                    查询预审规则 (--space)
├── ai-codegen                    代码生成 (AI)
│   ├── start                     发起生成 (--space, --sequence; --repo, --branch 可选)
│   └── result                    查询结果 (--conversation-id 或 --space+--sequence)
├── login / logout / cache clean / completion / version
```

每个命令的完整参数、返回 JSON 结构和字段说明 → [命令详细参考](references/commands.md)

## 常用命令速查

### 智能寻卡（不确定空间/卡片时首选）

```bash
icafe-cli card smart-find              # 返回活跃卡片 + stats.bySpace/bySpaceType 统计
```

### 查询卡片

```bash
icafe-cli card get --space myspace --sequence 1001 --brief
icafe-cli card query --space myspace --iql "负责人 = currentUser AND 流程状态 != 已关闭" --brief
```

### 创建卡片

```bash
icafe-cli card create --space myspace --title "修复登录Bug" --type Bug
icafe-cli card create --space myspace --title "新功能" --type Story \
  --detail "<p>描述</p>" --priority P1-High --assignee zhangsan
```

> 空间/类型不确定时 → 参考 [智能建卡工作流](references/smart-create-workflow.md)

### 更新卡片

```bash
icafe-cli card update --space myspace --sequence 1001 --status 开发中
icafe-cli card update --space myspace --sequence 1001 --assignee zhangsan --priority P1-High
```

> 改状态前先 `card next-statuses` 确认可达状态。完整流程 → [智能改卡工作流](references/smart-update-workflow.md)

### AI 预审 & 代码生成

```bash
# 预审
icafe-cli ai-pre-review start --space myspace --sequence 1001
icafe-cli ai-pre-review result --space myspace --sequence 1001

# 代码生成 (在 git 仓库目录下自动检测 repo)
icafe-cli ai-codegen start --space myspace --sequence 1001
icafe-cli ai-codegen result --space myspace --sequence 1001
```

> 完整的异步轮询流程 → [AI 预审与代码生成工作流](references/ai-workflows.md)

### 空间与字段

```bash
icafe-cli space latest                                         # 最近访问的空间
icafe-cli space issue-types --space myspace                    # 卡片类型列表
icafe-cli space type-fields --space myspace --type Story       # 字段定义和可选值
icafe-cli space type-statuses --space myspace --type Story     # 流程状态列表
icafe-cli ai-pre-review rules --space myspace                   # 预审规则
```

## Markdown → HTML 对照表

| Markdown | HTML |
|----------|------|
| `**粗体**` | `<strong>粗体</strong>` |
| `*斜体*` | `<em>斜体</em>` |
| `# 标题` | `<h1>标题</h1>` |
| `- 列表` | `<ul><li>列表</li></ul>` |
| `1. 列表` | `<ol><li>列表</li></ol>` |
| `` `代码` `` | `<code>代码</code>` |
| `[链接](url)` | `<a href="url">链接</a>` |
| `换行` | `<br>` |

## IQL 速查

字段名用**中文**，详见 [IQL 语法参考](references/iql-syntax.md)。

```
负责人 = currentUser                              # 当前用户的卡片
类型 = Bug AND 优先级 = P1-High                    # 高优 Bug
标题 ~ 登录                                        # 标题含"登录"
流程状态 in (新建, 开发中)                           # 多状态
创建时间 > "2024-01-01"                             # 日期（不支持 >=）
```

## 错误处理

- **退出码**: `0` 成功 / `1` 未登录 / `2` 参数校验 / `4` HTTP 错误
- **业务成功判断**: `card get/update/query` 检查 `code=200`，`ai-pre-review/ai-codegen` 检查 `status="OK"`，其他检查 `status=200`
- 详见 [错误处理参考](references/error-handling.md)

## 缓存

| 对象 | TTL |
|------|-----|
| space/plan 相关查询 | 20 分钟 |
| `card smart-find` 结果 | 5 分钟 |
| 最近访问空间列表 | 1 小时 |
| spaceId / issueId 映射 | 1 天 |

```bash
icafe-cli cache clean          # 清除所有缓存
icafe-cli space latest --no-cache  # 跳过缓存
```

## 卡片 URL

```
https://console.cloud.baidu-int.com/devops/icafe/issue/{space}-{sequence}/show
```

## 工作流参考

| 场景 | 参考文档 |
|------|---------|
| 不确定空间/卡片 → 智能定位 | [智能寻卡](references/smart-find-workflow.md) |
| 不确定空间/类型 → 智能创建 | [智能建卡](references/smart-create-workflow.md) |
| 修改字段/状态 → 安全更新 | [智能改卡](references/smart-update-workflow.md) |
| **Git 提交/评审 → 绑定卡片** | **默认使用 [零交互版](references/git-auto-bindcard-workflow.md)**（全自动决策，不问用户） |
| Git 绑定卡片（交互式） | [交互版](references/git-bindcard-workflow.md)（仅当用户明确要求"让我选卡片"时使用） |
| AI 预审 / 代码生成 | [AI 工作流](references/ai-workflows.md) |

## 参考资料

| 文件 | 内容 |
|------|------|
| [命令详细参考](references/commands.md) | 所有命令的参数表、返回 JSON、字段类型格式 |
| [错误处理](references/error-handling.md) | 退出码、错误码、诊断方法 |
| [IQL 语法](references/iql-syntax.md) | 查询语言完整语法 |
| [平台概念](references/platform-concepts.md) | 空间、卡片、状态、计划等核心概念 |
