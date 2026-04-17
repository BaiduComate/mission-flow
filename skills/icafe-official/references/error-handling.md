# 错误处理参考

本文档详细说明 icafe-cli 的错误处理机制、退出码、错误码，以及各命令特有的错误场景。

---

## CLI 退出码

| 退出码 | 含义 | 触发场景 |
|--------|------|----------|
| 0 | 成功 | 命令正常执行完毕 |
| 1 | 认证失败或 Cobra 通用错误 | Token 无效/过期 (`PersistentPreRun`)；**缺少必需 flag、未知子命令、用法错误** 等 Cobra 在 `Execute()` 里返回的错误（与退出码 2 区分见下） |
| 2 | `exitWithError` 本地校验 | 仅由 CLI 显式 `exitWithError` 触发，例如 `card update` 未提供任何修改项、`history`/`status-changes` 序列号格式非法或超过个数上限 |
| 4 | API 调用失败 | 服务端返回 HTTP 非 2xx 状态码 |

**说明**: Cobra 对「未传必填 flag」类问题走 `Execute()` 错误路径，进程退出码为 **1**，不是 2。退出码 **2** 只对应代码里主动输出的 JSON 校验错误（`{"error":"...","message":"..."}` 到 stderr）。

---

## 两种错误响应机制

iCafe 后端有两套错误返回机制，**agent 必须同时处理**:

### 1. HTTP 错误 (非 2xx 状态码)

CLI 会拦截并输出到 stderr，退出码 4。格式化为 JSON:

```json
{"error":"http_404","message":"资源不存在...","status":404,"traceId":"xxx","requestId":"xxx","body":"原始响应"}
```

| HTTP 状态码 | 含义 | 常见触发场景 |
|-------------|------|-------------|
| 400 | 请求参数错误 | IQL 语法错误、max-records 超过 100 |
| 401 | 认证失败 | Token 无效或已过期 |
| 403 | 权限不足 | 当前用户无权操作该空间或卡片 |
| 404 | 资源不存在 | space 或 sequence 不正确 |
| 500 | 服务端异常 | 字段值不合法、状态流转违规、内部错误 |

### 2. 业务错误 (HTTP 200 + 业务层失败)

CLI **不会拦截**，直接输出到 stdout。即使操作失败，后端也可能返回 HTTP 200。

```json
{"status": 304, "message": "The space required does not exist."}
```

**不同命令的成功标识字段和成功值不同**，agent 必须根据具体命令检查对应字段:

| 命令 | 成功标识字段 | 成功值 |
|------|-------------|--------|
| `card get`, `card update`, `card query` | `code` | `200` |
| `devinfo card`, `plan update-date` | `status` | `0` |
| `ai-pre-review start/result`, `ai-codegen start/result` | `status` | `"OK"` (字符串，macross BaseResponse 格式，数据在 `data` 字段中) |
| 其他所有命令 | `status` | `200` |

简便做法: 同时检查 `code` 和 `status`，值为 `200` 或 `0` 即为成功，否则为业务失败。

---

## 业务错误码速查表

| 业务错误码 | 含义 | 常见触发命令 | 建议处理方式 |
|-----------|------|-------------|-------------|
| 100 | 认证用户名或密码错误 | 所有命令 | 检查 Token 是否有效 |
| 101 | 无权限 | 所有命令 | 告知用户联系空间管理员。评论更新时可能是在编辑他人评论 |
| 200 | 成功 | — | 正常处理 |
| 304 | 空间不存在 | 所有带 `--space` 的命令 | 用 `space latest` 确认正确的 prefixCode |
| 306 | 卡片类型不存在 | card create | 用 `space issue-types` 确认可用类型 (注意区分大小写) |
| 401 | 字段名或值不合法 | card create, card update | 用 `space type-fields` 确认字段名和可选值 |
| 404 | 卡片不存在 | card get, current-status | 核实 sequence 是否正确 |
| 601 | 参数错误 | 多个命令 | 根据 message 修正参数 |
| 603 | 批量查询超限 | devinfo card | 每次最多 100 个序列号 |
| 704 | 用户不存在 | space latest, card create (--assignee) | 确认用户名是否正确 (邮箱前缀) |
| 901 | 数据量过大 | card history, status-changes | 每次最多 50 个序列号 |
| 902 | 未知错误 | 所有命令 | 检查参数后重试，如持续失败告知用户 |
| 1011 | IQL 解析失败 | card query | 检查 IQL 语法是否正确 |

---

## 各命令特有的错误场景

### card create

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 601 | 缺少必填字段 | 用 `space type-fields` 查询必填项后补充 |
| 304 | 空间不存在 | 确认 `--space` 值 |
| 101 | 无创建权限 | 告知用户 |
| 306 | `--type` 值不存在 (区分大小写) | 用 `space issue-types` 确认 |
| 704 | `--assignee` 用户不存在 | 确认用户名 |

### card update

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| HTTP 500 + `"流程状态不存在"` | 目标状态名在该卡片类型中不存在 | 用 `space type-statuses` 确认合法状态名 |
| HTTP 500 + `"无法流转到该流程状态"` | 当前状态不允许直接流转到目标状态 | 使用 `--no-check-status` 重试 |
| HTTP 500 + `"无法到达该流程状态，还有必填字段没有填写: fieldName"` | 状态流转要求填写额外必填字段 | 在 `--fields` 中补充 |
| HTTP 500 + `"field value error : 字段名=值"` | 字段值不在可选项中 | 用 `space type-fields` 查询合法值 |
| HTTP 500 | 标题为空 | 标题不允许设为空字符串 |
| HTTP 403 | 无编辑权限 | 告知用户联系管理员 |
| HTTP 404 | 空间或卡片不存在 | 核实 space 和 sequence |

### card query

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| HTTP 400 | IQL 语法错误 | 检查 IQL 表达式 |
| HTTP 400 | max-records 超过 100 | 限制在 100 以内 |

### comment create / get

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 601 + "card is not exist!" | 卡片不存在 | 核实 sequence |
| 304 | 空间不存在 | 核实 space |

### comment update

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 601 + "comment is not exist!" | 评论不存在或已删除 | 用 `comment get` 确认 |
| 101 + "current user can not edit other's comment" | 不能编辑他人评论 | 只能编辑自己的评论 |

### space type-fields

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 601 | 卡片类型在该空间不存在 | 用 `space issue-types` 确认 |

### plan create

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 601 + "startDate must before endDate" | 结束日期早于开始日期 | 修正日期 |
| 601 + "所属计划不能包含特殊字符" | 名称含 `\|,<>()/\"` | 移除特殊字符 |
| 601 + "父计划不存在!" | `--parent` 路径不正确 | 用 `plan list` 确认 |

### plan update-date

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 601 + "this planBox not exist!" | 计划 ID 不存在 | 用 `plan list` 确认 |
| 601 + "startDate must before endDate" | 日期范围不合法 | 修正日期 |

### devinfo card

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 603 | 序列号数量超过 100 个 | 分批查询 |

### devinfo active-cards

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| "结束时间不能在开始时间前" | end-time 早于 start-time | 修正时间 |
| "page 参数不能小于1" | 页码 < 1 | 设置 >= 1 |

### card history / status-changes

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 901 | 序列号超过 50 个 | CLI 层已做前置校验 |
