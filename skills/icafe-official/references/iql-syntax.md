# IQL (iCafe Query Language) 语法参考

## 概述

IQL 是 iCafe 平台的卡片查询语言，用于按条件筛选和检索卡片。通过 `icafe-cli card query --iql` 参数使用。

## 基本语法

```
字段名 操作符 值 [AND|OR 字段名 操作符 值 ...]
```

**不支持 `NOT` 一元逻辑操作符**，不能写 `NOT (类型 = Bug)`。需要用 `!=`、`!~`、`not in` 等取反操作符代替。

判空只能用 `is empty` / `is not empty`，不支持 `= null`。

## 操作符

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `=` | 等于 | `类型 = Bug` |
| `!=` | 不等于 | `流程状态 != 已关闭` |
| `>` | 大于 | `创建时间 > "2024-01-01"` |
| `<` | 小于 | `创建时间 < "2024-12-31"` |
| `>=` | 大于等于 | 仅流程状态支持: `流程状态 >= 开发中` |
| `<=` | 小于等于 | 仅流程状态支持: `流程状态 <= 测试中` |
| `in` | 在集合中 | `类型 in (Bug, Story, Task)` |
| `not in` | 不在集合中 | `优先级 not in (P3-Low, P4-Lowest)` |
| `~` | 包含 | `标题 ~ 登录` |
| `!~` | 不包含 | `标题 !~ 测试` |
| `is empty` | 为空 | `截止日期 is empty` |
| `is not empty` | 不为空 | `负责人 is not empty` |

## 逻辑操作符

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `AND` | 与 | `类型 = Bug AND 优先级 = P1-High` |
| `OR` | 或 | `类型 = Bug OR 类型 = Story` |
| `()` | 分组 | `(类型 = Bug OR 类型 = Story) AND 负责人 = currentUser` |

## 字段类型与支持的操作符

### 日期/时间字段

字段: `创建时间`, `更新时间`, `最后修改时间`, `截止日期`, `解决时间`

支持操作符: `<`, `>`, `=`, `is empty`, `is not empty`

**注意**: 日期字段不支持 `>=`、`<=`、`~`、`!~`。

**`=` 的特殊行为**: `创建时间 = "2024-01-01"` 匹配的是当天 00:00:00 到 23:59:59 的整天范围，不是精确时间点匹配。

```
创建时间 > "2024-01-01"
更新时间 < "2024-06-30"
截止日期 is empty
```

#### 日期特殊值

`=` 操作符支持的周期值（匹配整个周期范围）:

| 值 | 说明 |
|----|------|
| `currentDay` | 今天 |
| `currentWeek` | 本周 |
| `currentMonth` | 本月 |
| `currentQuarter` | 本季度 |
| `currentYear` | 今年 |
| `lastDay` | 昨天 |
| `lastWeek` | 上周 |
| `lastMonth` | 上月 |
| `lastQuarter` | 上季度 |
| `lastYear` | 去年 |
| `nextDay` | 明天 |
| `nextWeek` | 下周 |
| `nextMonth` | 下月 |
| `nextQuarter` | 下季度 |
| `nextYear` | 明年 |

**约束**: `current*`/`last*`/`next*` 只能用于 `=` 操作符。

`>` / `<` 操作符支持的相对时间值:

| 值 | 说明 | 示例 |
|----|------|------|
| `before-N-days` | N 天前 | `创建时间 > before-7-days` |
| `before-N-weeks` | N 周前 | `创建时间 > before-2-weeks` |
| `before-N-months` | N 月前 | `创建时间 > before-1-months` |
| `before-N-quarters` | N 季度前 | |
| `after-N-days` | N 天后 | |
| `after-N-weeks` | N 周后 | |
| `startOfDay` | 今天开始 | `创建时间 > startOfDay` |
| `startOfWeek` | 本周开始 | |
| `startOfMonth` | 本月开始 | |
| `startOfYear` | 今年开始 | |

**约束**: `startOf*` 只能用于 `>` 或 `<` 操作符。

```
# 本周创建的卡片
创建时间 = currentWeek

# 最近 7 天创建的卡片
创建时间 > before-7-days

# 上月更新的卡片
更新时间 = lastMonth
```

### 人员字段

字段: `负责人`, `创建人`, `最后修改人`

支持操作符: `=`, `!=`, `in()`, `not in()`, `is empty`, `is not empty`

```
负责人 = currentUser
创建人 = zhangsan
负责人 in (zhangsan, lisi)
```

### 类型字段

字段: `类型`

支持操作符: `=`, `!=`, `in()`, `not in()`, `is empty`, `is not empty`

```
类型 = Bug
类型 in (Bug, Story, Task, Epic)
类型 != Epic
```

### 流程状态字段

字段: `流程状态`

支持操作符: `=`, `!=`, `>`, `<`, `>=`, `<=`, `in()`, `not in()`, `is empty`, `is not empty`

流程状态有排序位置，`>`/`<`/`>=`/`<=` 基于状态在空间配置中的排序位置进行比较。
例如状态顺序为 [新建, 开发中, 测试中, 已完成]，`流程状态 >= 开发中` 会匹配 开发中、测试中、已完成。
后端实际将 `>=`/`<=` 转换为 `in` 查询。

**注意**: `>=`/`<=` 是流程状态独有的操作符，其他字段（包括日期、选择列表等）均不支持。

```
流程状态 = 开发中
流程状态 >= 开发中
流程状态 in (新建, 待开发, 开发中)
流程状态 != 已关闭
```

### 编号字段

字段: `编号`

支持操作符: `=`, `!=`, `in()`, `not in()`, `~`

```
编号 = 1001
编号 in (1001, 1002, 1003)
```

### 父卡片字段

字段: `父卡片编号`

支持操作符: `=`, `!=`, `in()`, `not in()`, `is empty`, `is not empty`

```
父卡片编号 is empty
父卡片编号 = 1001
```

### 计划字段

字段: `所属计划`

支持操作符: `=`, `!=`, `in()`, `not in()`, `is empty`, `is not empty`

需要使用完整路径，可包含子计划。

```
所属计划 = "2024Q1/Sprint1"
所属计划 is not empty
```

### 关键字字段

字段: `关键字`

支持操作符: `~` (仅包含搜索)

```
关键字 ~ 重要
```

### 标题字段

字段: `标题`

支持操作符: `~`, `!~`, `is empty`, `is not empty`

```
标题 ~ 登录
标题 !~ 测试
```

### 数字字段

支持操作符: `<`, `>`, `=`, `is empty`, `is not empty`

```
预估工时 > 8
```

### 选择/多选/复选框字段

支持操作符: `=`, `!=`, `in()`, `not in()`, `is empty`, `is not empty`

```
优先级 = P1-High
优先级 in (P0-Highest, P1-High)
```

### 文本字段 (单行/多行)

支持操作符: `~`, `!~`, `is empty`, `is not empty`

### URL 字段

支持操作符: `~`, `!~`, `=`, `is empty`, `is not empty`

### 标签字段

字段: `标签`

支持操作符: `=`, `!=`, `in()`, `not in()`, `is empty`, `is not empty`

```
标签 = 紧急
标签 in (紧急, 重要)
```

## 特殊值

| 值 | 适用字段 | 说明 |
|----|---------|------|
| `currentUser` | 人员字段 | 当前认证用户 |
| `currentDay` / `lastWeek` / ... | 日期字段 | 周期值，详见日期特殊值表 |
| `before-N-days` / `startOfMonth` / ... | 日期字段 | 相对时间值，详见日期特殊值表 |
| `当前计划` | 所属计划 | 当前激活的计划 |

```
负责人 = currentUser
创建时间 = currentWeek
创建时间 > before-7-days
所属计划 = 当前计划
```

## 嵌套查询函数

IQL 支持 `subtasksOf` 和 `parentsOf` 函数，用于查询子卡片或父卡片：

```
issues in (subtasksOf[子查询IQL, 深度])
issues in (parentsOf[子查询IQL, 深度])
```

- **深度**: 正整数，表示向下/向上查找的层级数（推荐 1-5）
- **子查询结果上限**: 1000 张卡片
- **最多嵌套**: 15 个 `issues in (...)` 块
- 函数名大小写不敏感

```bash
# 查询某用户 Story 的所有子卡片
icafe-cli card query --space myspace --iql "issues in (subtasksOf[类型 = Story AND 负责人 = currentUser, 1])"

# 查询某些 Task 的父卡片 (向上 2 层)
icafe-cli card query --space myspace --iql "issues in (parentsOf[类型 = Task AND 流程状态 = 开发中, 2])"
```

## 常用查询示例

```bash
# 当前用户负责的所有未关闭卡片
icafe-cli card query --space myspace --iql "负责人 = currentUser AND 流程状态 != 已关闭"

# 高优先级 Bug
icafe-cli card query --space myspace --iql "类型 = Bug AND 优先级 in (P0-Highest, P1-High)"

# 本周创建的卡片
icafe-cli card query --space myspace --iql "创建时间 = currentWeek"

# 最近 7 天创建的卡片
icafe-cli card query --space myspace --iql "创建时间 > before-7-days"

# 特定迭代中的 Story
icafe-cli card query --space myspace --iql "类型 = Story AND 所属计划 = \"2024Q1/Sprint1\""

# 无负责人的卡片
icafe-cli card query --space myspace --iql "负责人 is empty AND 类型 != Epic"

# 标题包含关键词的 Task
icafe-cli card query --space myspace --iql "类型 = Task AND 标题 ~ 优化"

# 复合条件
icafe-cli card query --space myspace --iql "(类型 = Bug OR 类型 = Task) AND 负责人 = currentUser AND 流程状态 != 已关闭"

# 指定编号的卡片
icafe-cli card query --space myspace --iql "编号 in (1001, 1002, 1003)"

# 没有父卡片的顶层卡片
icafe-cli card query --space myspace --iql "父卡片编号 is empty AND 类型 = Story"
```

## 注意事项

1. 值中包含以下字符时，需要用双引号包裹: 空格、`(`、`)`、`=`、`<`、`>`、`~`、`!`
2. `in()` 操作符的值列表用逗号分隔，放在括号内
3. 日期值格式为 `YYYY-MM-DD`，需要用双引号包裹
4. `currentUser` 等特殊值不需要引号
5. `is empty` 和 `is not empty` 后面不需要值
6. 不支持 `NOT` 一元逻辑操作符，用 `!=`、`!~`、`not in` 代替
7. 不支持 `= null`，判空用 `is empty` / `is not empty`
