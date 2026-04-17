# iCafe 平台概念指南

## 概述

iCafe 是百度内部的项目管理和敏捷研发平台，类似于 Jira。本文档介绍 iCafe 的核心概念。

官网: `https://console.cloud.baidu-int.com/devops/icafe`

---

## 空间 (Space)

空间是 iCafe 的项目容器，是组织卡片和计划的基本单元。

### 关键属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `id` | 内部数字 ID | `12345` |
| `name` | 空间名称 | `我的项目` |
| `prefixCode` | 空间标识 (prefixCode)，CLI 中 `--space` 参数的值 | `myspace` |

### JSON 响应示例

```json
{ "id": 87531, "name": "Dodo", "prefixCode": "dododododoit" }
```

### 重要说明

- CLI 中所有 `--space` 参数使用 `prefixCode`，不是数字 `id`
- 可通过 `icafe-cli space latest` 获取用户最近访问的空间列表
- 空间树 (`icafe-cli space tree`) 可查看完整的空间层级结构

---

## 卡片 (Card / Issue)

卡片是 iCafe 的核心工作单元，代表一个具体的任务、需求或缺陷。

### 标识符

| 标识符 | 说明 | 在哪使用 |
|--------|------|----------|
| `sequence` | 序列号，空间内自增整数，人类可读 | URL、CLI 命令的 `--sequence` |
| `issueId` | 内部数据库 ID | 仅内部使用，不要用于 CLI |

### 卡片关键字段

| 字段 | 说明 |
|------|------|
| `sequence` | 卡片编号（整数，空间内唯一） |
| `title` | 标题 |
| `type.name` | 卡片类型（Epic / Story / Task / Bug） |
| `status` | 当前流程状态 |
| `responsiblePeople` | 负责人列表（含 username、name） |
| `createdUser` | 创建人 |
| `createdTime` | 创建时间，格式 `yyyy-MM-dd HH:mm:ss` |
| `lastModifiedTime` | 最近修改时间 |
| `detail` | 描述，HTML 富文本 |
| `parent` | 父卡片引用（含 sequence、title） |
| `properties` | 自定义属性列表（见下方"自定义属性"章节） |
| `isFinishedStatus` | 是否已完结状态（布尔值） |

### 卡片类型

| 类型 | 说明 | 典型用途 |
|------|------|---------|
| `Epic` | 史诗 | 大型功能模块，包含多个 Story |
| `Story` | 用户故事 | 一个完整的功能需求 |
| `Task` | 任务 | 技术任务、子任务、杂项工作 |
| `Bug` | 缺陷 | 功能异常、线上问题 |

> **注意**: 类型名称在 IQL 查询中区分大小写，使用英文原名。每个空间可以自定义卡片类型与名称，通过 `icafe-cli space issue-types` 查询。

### 卡片 URL 格式

```
https://console.cloud.baidu-int.com/devops/icafe/issue/{space}-{sequence}/show
```

例如: `https://console.cloud.baidu-int.com/devops/icafe/issue/myspace-1001/show`

---

## 流程状态 (Workflow Status)

卡片的生命周期通过流程状态管理。状态有定义好的流转规则。

### 常见状态流转

```
新建 → 待开发 → 开发中 → 开发完成 → 测试中 → 已完成
```

### 常见状态

| 状态 | 说明 |
|------|------|
| `新建` | 刚创建的卡片 |
| `待开发` | 等待开发 |
| `开发中` | 正在开发 |
| `进行中` | 正在进行 |
| `待测试` | 等待测试 |
| `测试中` | 正在测试 |
| `已完成` | 开发完成 |
| `已关闭` | 卡片关闭 |

### 状态流转规则

- 状态有顺序，支持 IQL 中的比较操作 (`>=`, `<=`)
- `isFinishedStatus: true` 表示该卡片处于终态
- 默认情况下，更新状态时会检查流转规则 (`isCheckStatus=true`)
- 使用 `--no-check-status` 可跳过检查，强制设置任意状态
- **查询时不要假设状态名称**，先通过 `space type-statuses` 确认该类型的合法状态列表

---

## 优先级 (Priority)

卡片的紧急程度，使用标准的 5 级优先级:

| 优先级 | 含义 |
|--------|------|
| `P0-Highest` | 最高优先级，紧急 |
| `P1-High` | 高优先级 |
| `P2-Middle` | 中等优先级 |
| `P3-Low` | 低优先级 |
| `P4-Lowest` | 最低优先级 |

> **注意**: 部分空间可能使用 `P2-Medium` 而非 `P2-Middle`，以 `space type-fields` 返回的值为准。

---

## 计划 (Plan)

计划是 iCafe 中的迭代/版本管理单元。

### 关键属性

| 属性 | 说明 |
|------|------|
| `id` | 计划 ID |
| `name` | 计划名称 |
| `path` | 计划路径 (层级路径) |
| `parentId` | 父计划 ID |
| `status` | 计划状态 (`ACTIVE` 或 `ARCHIVED`) |
| `startDate` | 开始日期 |
| `endDate` | 结束日期 |

### JSON 响应示例

```json
{ "id": 1107361, "name": "03.02~03.08", "path": "2026Q1/03.02~03.08", "status": "ACTIVE" }
```

### 层级结构

计划支持层级嵌套，通过路径表示:
- 顶级计划: `2024Q1`
- 子计划: `2024Q1/Sprint1`
- 孙计划: `2024Q1/Sprint1/Week1`

在 IQL 中使用 `所属计划` 字段查询时，需要使用完整路径。

---

## 自定义属性 (Properties)

每张卡片包含一组 `properties`，内容因空间和卡片类型而异。

### Properties 数据结构

```json
{
  "fieldType": "SELECT_LIST",
  "localId": 22797,
  "propertyName": "优先级",
  "displayValue": "P0-Highest",
  "value": "17185"
}
```

- `fieldType`: 字段类型 (SELECT_LIST, USER_PICKER, DATE_TIME, NUMBER_FIELD 等)
- `localId`: 字段内部 ID
- `propertyName`: 字段中文名称 (用于 `--fields` 参数和 IQL 查询)
- `displayValue`: 人类可读的展示值
- `value`: 内部存储值 (更新时可以使用 displayValue)

### 常见属性字段

以下是各空间中常见的自定义属性 (不同空间可能有所不同，以 `space type-fields` 返回为准):

| 属性名 | fieldType | 说明 |
|--------|-----------|------|
| 优先级 | SELECT_LIST | P0-Highest / P1-High / P2-Middle / P3-Low / P4-Lowest |
| 所属计划 | PLAN_BOX | 关联的迭代计划 |
| 所属项目 | PROJECT_MANAGEMENT | 关联项目 |
| 截止日期 | DATE_TIME | 卡片截止时间 |
| 计划上线日期 | DATE_TIME | 预计上线时间 |
| 实际上线日期 | DATE_TIME | 实际上线时间 |
| 估算工时 | NUMBER_FIELD | 预估研发工时 (小时) |
| 实际工时 | NUMBER_FIELD | 实际花费工时 |
| RD负责人 | USER_PICKER | 研发负责人 |
| FE负责人 | USER_PICKER | 前端负责人 |
| QA负责人 | USER_PICKER | 测试负责人 |
| PM负责人 | USER_PICKER | 产品负责人 |
| 关注人 | USER_PICKER | 卡片关注人 |
| 是否免测 | SELECT_LIST | 是/否 |
| Severity | SELECT_LIST | Bug 严重程度 (S1/S2/S3/S4) |
| Bug根因 | SELECT_LIST | Bug 根本原因分类 |
| 线上问题级别 | SELECT_LIST | P0/P1/P2/P3 |

### 系统字段

以下字段通过专用参数 (`--title`, `--assignee` 等) 或 `--fields` 中文名更新:

| 字段名 (中文) | 说明 |
|---------------|------|
| `标题` | 卡片标题 |
| `内容` | 卡片描述 (HTML 格式) |
| `类型` | 卡片类型 |
| `负责人` | 负责人用户名 |
| `流程状态` | 当前流程状态 |
| `优先级` | 优先级等级 |
| `创建人` | 创建者用户名 |
| `创建时间` | 创建时间 |
| `更新时间` | 最后更新时间 |
| `截止日期` | 截止日期 |
| `所属计划` | 关联的计划 |
| `标签` | 卡片标签 |

> **操作约束**: 通用属性 (状态、负责人、优先级等) 通过 `--status`、`--assignee`、`--priority` 参数直接设置；自定义属性通过 `--fields "属性名=值"` 更新。

---

## 研发数据链 (DevInfo)

研发数据链记录卡片从代码到上线的完整研发活动。

### 数据类型

| 类型 | 说明 | 包含信息 |
|------|------|----------|
| `codeReview` | 代码评审 | 评审 ID、URL、状态 (MERGED/PASSED)、提交人、changeId |
| `codeMerge` | 代码合并 | Git 提交记录、分支信息、流水线构建状态 |
| `releaseInfo` | 发布信息 | 版本号、敏捷流水线 URL |
| `initiateTest` | 提测记录 | 测试阶段信息 |
| `passTest` | 测试通过 | 测试通过记录 |
| `deploy` | 部署 | 部署 Job URL、环境信息 |

### codeMerge JSON 示例

```json
{
  "branch": "master",
  "commitId": "c8f0b1a89e316502e9f892f2754baef414dc0b86",
  "commitMessage": "dododododoit-5 前端增加routes和links",
  "commitTime": "Mar 11, 2026 4:51:51 PM",
  "projectName": "baidu/bapi/dodo",
  "changeUrl": "http://icode.baidu.com/myreview/changes/c/baidu/bapi/dodo/+/120034262",
  "pipeLineCommit": {
    "pipelineId": 244154168,
    "pipeLineUrl": "http://agile.baidu.com//#/detail/244154168/job/0",
    "status": "SUCC"
  }
}
```

---

## 用户标识

iCafe 使用百度内部用户名标识用户:
- 正式员工: 如 `zhangsan`
- 外包员工: 通常以 `v_` 开头，如 `v_liuxiang`

在 IQL 中可以使用 `currentUser` 表示当前认证用户。

---

## 评论 (Comment)

卡片上的讨论和记录信息。每条评论包含:
- `id`: 评论 ID
- `content`: 评论内容
- `username`: 创建人用户名
- `chineseName`: 创建人中文名
- `createTime`: 创建时间
- `isDeleted`: 是否已删除
- `parentCommentId`: 父评论 ID (回复场景)

---

## IQL 关键约束

详细语法见 `references/iql-syntax.md`，以下是使用时的关键注意事项:

1. **字段名使用中文**: IQL 中所有字段名均为中文 (`类型`、`负责人`、`流程状态` 等)
2. **日期不支持 `>=`/`<=`**: 日期字段只支持 `>` 和 `<`，需要范围时用 AND 组合
3. **`currentUser` 魔法变量**: 表示当前登录用户，可用于 `负责人 = currentUser`
4. **状态顺序比较**: `流程状态 <= 开发中` 会匹配所有顺序在"开发中"之前 (含) 的状态
5. **计划路径需完整**: `所属计划 = "2026Q1/03.02~03.08"`，不能只写叶子节点名
6. **字符串值可不加引号**: 但含空格或特殊字符时必须加引号
7. **不要猜测状态值**: 不同空间的状态配置不同，应先通过查询确认可用状态

---

## 重要约束与最佳实践

1. **`--space` 必须使用 prefixCode** (如 `myspace`)，不是数字 id
2. **`--sequence` 是空间内自增序号**，不是全局唯一 id
3. **描述和评论字段必须是 HTML**，不能直接传 Markdown (详见 SKILL.md 转换规则)
4. **批量查询 devinfo 最多 100 张卡片** (`--sequences` 逗号分隔)
5. **批量查询 history/changes 最多 50 张卡片**
6. **查询结果默认不含子卡片**，需要时加 `--show-children`
7. **优先级格式含数字前缀**: `P0-Highest`、`P1-High`、`P2-Middle`、`P3-Low`、`P4-Lowest`
