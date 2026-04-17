# 智能修改卡片工作流

用户要修改某张卡片时，需要先充分了解卡片当前状态、字段的合法值、状态流转规则，避免盲目修改导致失败。修改后要验证结果，失败时要分析原因。

---

## 适用场景

- 用户说"帮我改一下卡片状态到开发中"
- 用户说"把负责人改成 zhangsan"
- 用户说"更新一下优先级为 P1"
- 用户说"帮我修改卡片的自定义字段"

## 第一步：获取卡片当前信息

```bash
icafe-cli card get --space <space> --sequence <sequence> --brief
```

按需添加可选参数：
- `--show-associations`: 需要查看关联卡片时添加
- `--show-children`: 需要查看子卡片时添加

记录当前状态，包括：标题、**类型名称 (`type.name`)**、负责人、流程状态、优先级等。后续对比用。

> 如果用户没给完整的 space+sequence，先参考 [智能寻卡工作流](smart-find-workflow.md) 定位卡片。

## 第二步：获取字段定义和状态流转规则

第一步获取到 `type.name` 后，**以下两个查询没有依赖关系，可以并行调用**以节省时间：

```bash
# 查询 1: 获取字段定义和合法值
icafe-cli space type-fields --space <space> --type <card_type>

# 查询 2: 如需修改状态，获取可达的目标状态
icafe-cli card next-statuses --space <space> --sequence <sequence>
```

**字段定义** (`type-fields`) 重点关注：
- 要修改的目标字段是否存在
- 字段的可选值列表（如优先级有哪些值、下拉列表的选项等）
- **注意**: `type-fields` **不包含流程状态字段**，流程状态用 `next-statuses` 查询
- 字段的类型（文本、选择、人员、日期等），决定了值的格式
- 如果用户要修改的值不在选项列表中，提前告知用户，不要盲目调用

**状态流转规则** (`next-statuses`，仅修改状态时需要)：
- 第一步的 `card get` 已返回卡片当前状态 (`status` 和 `isFinishedStatus`)，无需再单独调用 `card current-status`
- 返回的 `result[].statusName` 即为从当前状态可直接到达的目标状态列表
- 如果 `result` 为空数组，说明当前状态没有可达的目标 (可能是终态或工作流未配置出边)，告知用户
- 检查用户要修改的目标状态是否在返回的列表中
- 如果目标状态不在列表中 → 提前告知用户"当前状态无法直接流转到目标状态"，确认是否使用 `--no-check-status` 强制跳过
- 如果目标状态在列表中 → 向用户确认："当前状态为 X，将修改为 Y，是否继续？"

> **提示**: `next-statuses` 比 `space type-statuses` 更精确。`type-statuses` 返回该类型所有合法状态，`next-statuses` 返回从当前状态可达的目标状态。但如果该类型未开启工作流，两者结果相同。

> **提示**: `card current-status` 是一个轻量接口，仅返回状态信息 (statusName, isFinishedStatus)，适合只需查询状态而不需要完整卡片信息的场景。在本流程中，第一步已获取完整卡片信息，无需额外调用。

## 第三步：向用户确认修改内容后执行

汇总所有修改项，向用户展示并确认后执行：

```bash
icafe-cli card update --space <space> --sequence <sequence> \
  --status <new_status> \
  --assignee <new_assignee> \
  --priority <new_priority> \
  --fields "自定义字段=新值" \
  --comment "修改原因说明"
```

## 第四步：验证更新结果

```bash
icafe-cli card get --space <space> --sequence <sequence> --brief
```

对比更新前后的数据，确认修改成功。

**如果更新失败**，分析错误信息:

| 常见错误 | 原因 | 解决方案 |
|----------|------|----------|
| HTTP 500 + `"流程状态不存在"` | 状态名不存在 | 用 `space type-statuses` 确认合法状态名 |
| HTTP 500 + `"无法流转到该流程状态"` | 流转路径不合法 | 使用 `--no-check-status` 重试，或先用 `card next-statuses` 确认可达状态 |
| HTTP 500 + `"无法到达该流程状态，还有必填字段没有填写: fieldName"` | 缺必填字段 | 在 `--fields` 中补充 |
| HTTP 500 + `"field value error : 字段名=值"` | 值不合法 | 用 `space type-fields` 查询合法值 |
| HTTP 500 + `"字段名: field does not exist!"` | 字段不存在 | 用 `space type-fields` 确认该类型有哪些字段 |
| HTTP 403 | 无权限 | 告知用户联系管理员 |
| HTTP 404 | space 或 sequence 错误 | 核实参数 |

对于可重试的错误（如缺必填字段、字段值不合法），修正参数后自动重试一次；对于权限类错误，直接告知用户。

## 决策流程图

```
用户要求修改卡片
  │
  ├─ 0. 确定卡片 (如果用户没给完整 space+sequence，参考智能寻卡工作流)
  │
  ├─ 1. card get --brief 获取卡片当前信息 (记录 type.name 用于后续查询)
  │
  ├─ 2. 并行获取: type-fields 字段定义 + next-statuses 可达状态 (如需改状态)
  │   ├─ 字段值合法？
  │   │   ├─ 合法 → 继续
  │   │   └─ 不合法 → 告知用户正确的可选值 → 用户提供新值 → 重新检查
  │   └─ 目标状态可达？
  │       ├─ 可达 → 继续
  │       └─ 不可达 → 告知用户，确认后使用 --no-check-status
  │
  ├─ 3. 汇总修改项，向用户确认 → card update 执行
  │
  └─ 4. card get --brief 验证结果
      ├─ 成功 → 展示修改前后对比
      └─ 失败 → 分析错误
          ├─ 可重试（字段值/必填项/字段不存在） → 修正后重试
          └─ 不可重试（权限等） → 告知用户
```
