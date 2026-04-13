---
name: icafe-card-assistant
description: 当用户询问关于 iCafe 平台卡片的问题、需要查询卡片信息、创建或更新卡片、管理评论，或访问相关研发数据链信息时，应使用此技能。它提供了全面的 API 客户端，支持卡片的检索、创建、更新、评论和相关数据查询。
---

# iCafe 卡片操作助手

## 概述

本技能提供了一个与 iCafe 平台卡片系统交互的 API 客户端。支持卡片操作，包括查询、创建、更新和管理评论，以及访问相关的空间计划。

## 重要说明

**以下参数必须由用户提供，不要使用任何默认值：**

1. **空间 ID（space_id）**：操作卡片、查询卡片等都需要明确的空间 ID
2. **用户 ID（userId）**：查询最近访问空间、指定负责人、IQL 查询中指定创建人/负责人等

用户 ID 是百度内部的唯一用户标识，如 "shijiazheng"、"v_liuxiang" 等。

**在调用 API 前，如果缺少空间 ID 或用户 ID，必须先询问用户。**

## 快速开始

使用 iCafe API 客户端，客户端会自动从环境变量或登录文件读取认证 token：

```python
from scripts.icafe_client import ICafeClient, ICafeConfig

# 方式一：使用默认配置（自动读取认证 token）
client = ICafeClient()

# 方式二：自定义配置
config = ICafeConfig(
    base_url="http://10.11.152.208:8701/api/process/icafe",
    timeout=30
)
client = ICafeClient(config)
```

## 核心 API 方法

### 1. 根据空间 ID 和卡片序列号获取卡片信息

```python
card = client.get_card_by_id(
    space_id="your-space-id",      # 必须提供，如 "joytest"
    sequence="1856",              # 卡片序列号（如 1856，即 URL 中的卡片编号）
    show_associations=True,
    show_children=True,
    show_okr=True,
    show_accumulate=True
)
# 返回：卡片 id、标题、描述、状态、负责人、创建时间、更新时间等
```

### 2. 创建卡片

```python
card = client.create_card(
    title="测试一下",
    description="<a href=\"https://www.baidu.com\">链接</a>",
    space_id="your-space-id",      # 必须提供
    card_type="Bug",
    assignee_id="your-user-id",    # 必须提供
    status="新建",
    priority="P1-High",
    parent="2667",                  # 可选：父卡片编号（sequence），用于创建子卡片
    comment="评论"
)
# 返回：新卡片，包含 issueId、sequence、title、url 等
```

### 3. 创建卡片评论

```python
comment = client.create_card_comment(
    space_id="your-space-id",      # 必须提供
    sequence="1856",              # 卡片序列号（如 1856，即 URL 中的卡片编号）
    content="这是一条新评论"
)
# 返回：新评论，包含 id、内容、作者、创建时间等
```

### 4. 查询最近访问的空间列表

```python
spaces = client.get_latest_spaces("your-user-id")  # 需要提供用户 ID
# 返回：最近访问的空间列表，包含 id、名称、prefix_code、访问时间等
```

### 5. 获取空间内所有计划

```python
plans = client.get_space_plans("your-space-id")  # 必须提供
# 返回：计划列表，包含 id、名称、日期、状态、卡片等
```

### 6. 查询满足条件的卡片

```python
result = client.query_cards(
    space_id="your-space-id",      # 必须提供
    iql="类型 = Bug AND 负责人 = currentUser",
    max_records=5,
    is_desc=True
)
# 返回：满足条件的卡片列表和分页信息
```

#### IQL 规则说明

**基本运算符：**

| 参数 | 含义 |
|------|------|
| AND | 且 |
| OR | 或 |
| >, <, =, >=, <=, != | 大于、小于、等于(是)、大于等于、小于等于、不等于(不是)，后面只能跟一个参数 |
| in, not in | 包含多个，也可以跟 () 一起使用，in 空括号例：in ()，不包含 |
| is empty, is not empty | 为空、不为空，is 跟 empty 一起使用 |
| ~, !~ | 包含的意思，常用于文本、关键词、标题的筛选，不包含 |
| - | 减，不支持 "+" |
| () | 可以将筛选条件括起来当做一个整体 |
| "" | 字段值支持引号使用，也可以不加 |

**按字段类型分类：**

| 字段类型 | 支持的参数 | 说明 | 示例 |
|---------|-----------|------|------|
| 日期 / 时间 | <, >, =, is empty, is not empty | 不支持 >= <=；时间是点逻辑 | 创建时间 > "2023-12-01 06:00:00" AND 创建时间 < "2023-12-19 00:00:00" |
| 人员字段 | =, !=, in(), not in(), is empty, is not empty | | 负责人 = v_liuxiang, 创建人 = shijiazheng |
| 类型 | =, !=, in(), not in(), is empty, is not empty | | 类型 in (Bug, Epic, Story) |
| 流程状态 | <, <=, =, >, >=, !=, in(), not in(), is empty, is not empty | 大小比较基于状态顺序 | 流程状态 in (新建, 开发中, 待开发, 进行中) |
| 所属计划 | =, !=, in(), not in(), is empty, is not empty | 需要完整路径；也可勾选父计划并包含子计划 | 所属计划 in (测试, 测试/测试1, 测试/测试1/测试3) |
| 关键字 | ~ | 只支持包含；不包含请用标题字段 | 关键字 ~ 测试 AND 关键字 ~ "测试" |
| 标题 | ~, !~, is empty, is not empty | | 标题 ~ 测试 |
| 数字类型 | <, >, =, is empty, is not empty | | 数字字段 > 1 |
| 单选 / 多选 / 单选框 / 复选框 | =, !=, in(), not in(), is empty, is not empty | | 单选框 in (是, 否) |
| 树类型 / TAG | =, !=, in(), not in(), is empty, is not empty | | 树字段 is empty |
| 单行文本 / 多行文本 | ~, !~, is empty, is not empty | | 多行文本 !~ 测试 |
| URL 类型 | ~, !~, =, is empty, is not empty | | URL = "www.baidu.com" |
| Label 标签 | =, !=, in(), not in(), is empty, is not empty | | Label = aaa |

**常用 IQL 示例：**

| 查询需求 | IQL 表达式 |
|----------|------------|
| 查询 Bug 类型卡片 | `类型 = Bug` |
| 查询当前用户负责的卡片 | `负责人 = currentUser` |
| 查询指定用户创建的卡片 | `创建人 = shijiazheng` |
| 查询指定用户创建且在指定日期之后的卡片 | `创建人 = shijiazheng AND 创建时间 > "2026-02-01"` |
| 查询新建状态的卡片 | `状态 = 新建` |
| 查询 Bug 且负责人是当前用户的卡片 | `类型 = Bug AND 负责人 = currentUser` |
| 查询创建时间在指定日期之后的卡片 | `创建时间 > "2025-01-01"` |
| 查询多种类型的卡片 | `类型 in (Bug, Epic, Story)` |
| 查询标题包含关键词的卡片 | `标题 ~ 测试` |
| 查询负责人在指定列表中的卡片 | `负责人 in (user1, user2, user3)` |
| 查询流程状态在指定范围的卡片 | `流程状态 <= 开发中` |

### 7. 更新卡片内容

```python
card = client.update_card(
    space_id="your-space-id",      # 必须提供
    sequence="1856",              # 卡片序列号（如 1856，即 URL 中的卡片编号）
    title="更新的标题",
    description="更新的描述",
    assignee_id="user-456",
    status="in_progress",
    priority="medium"
)
# 返回：更新后的卡片信息
```

### 8. 查询卡片研发数据链信息

```python
dev_info = client.get_card_dev_info(
    space_id="mapcio-qatools",     # 必须提供，空间 ID
    sequence="1368"               # 必须提供，卡片序列号
)
# 返回：研发数据链信息字典，包含：
# - codeReview: 代码评审记录列表
# - codeMerge: 代码合并记录
# - releaseInfo: 发布信息列表
# - initiateTest: 发起测试记录
# - passTest: 通过测试记录
# - deploy: 部署记录
```

**说明：** 此接口用于查询卡片的研发数据链相关信息，包括代码评审、测试用例、构建记录、测试记录等与卡片关联的研发流程数据。

## 错误处理

所有 API 方法可能抛出以下异常：
- `ValueError`：当缺少或无效的必需参数时
- `requests.RequestException`：当 HTTP 请求失败时

建议适当处理这些异常：

```python
try:
    card = client.get_card_by_id("your-space-id", "628")
except ValueError as e:
    print(f"参数无效: {e}")
except requests.RequestException as e:
    print(f"API 请求失败: {e}")
```

## 配置

### 认证配置

客户端使用 `x-ac-Authorization` header 进行认证，认证 token 按以下优先级读取：

1. **环境变量**：`COMATE_AUTH_TOKEN`
2. **登录文件**：`~/.comate/login`

登录文件格式：纯 token（单行）

示例设置环境变量：
```bash
export COMATE_AUTH_TOKEN="your-token-here"
```

示例创建登录文件：
```bash
echo "your-token-here" > ~/.comate/login
```

### 可选配置

可以通过 `ICafeConfig` 自定义以下参数：
- `base_url`：iCafe API 基础 URL，默认为 `http://10.11.152.208:8701/api/process/icafe`
- `timeout`：请求超时时间（秒），默认为 30
- `username`、`password`：已废弃，保留以兼容旧代码

## 卡片链接模板

### URL 格式

iCafe 卡片链接遵循以下格式：

```
https://console.cloud.baidu-int.com/devops/icafe/issue/{space_id}-{sequence}/show
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| space_id | 空间 ID | `mapcio-qatools` |
| sequence | 卡片序列号（sequence） | `1360` |

> **注意**: URL 中的卡片编号使用的是 `sequence`（序列号），而非内部 ID `issueId`。
> - `sequence`: 卡片的可读序列号，如 1360（对应链接 mapcio-qatools-1360）
> - `issueId`: 卡片的内部 ID，如 186061811（仅在 API 内部使用）

### 链接示例

```
https://console.cloud.baidu-int.com/devops/icafe/issue/mapcio-qatools-1360/show
```

### Python 生成链接

```python
# 使用客户端提供的静态方法
from scripts.icafe_client import ICafeClient

# 方法一：直接生成链接
url = ICafeClient.generate_card_url("mapcio-qatools", 1360)
# 返回: https://console.cloud.baidu-int.com/devops/icafe/issue/mapcio-qatools-1360/show

# 方法二：从卡片数据生成链接
result = client.query_cards("joytest", "创建人 = shijiazheng", max_records=1)
if result.get('cards'):
    card = result['cards'][0]
    url = ICafeClient.generate_card_url_from_card("joytest", card)
```

### 从 API 响应获取链接

当创建或查询卡片时，API 响应中通常会包含卡片链接：

```python
# 创建卡片后获取链接
result = client.create_card(...)
card_url = result.get('url')  # 或从 issues[0].url 获取

# 查询卡片后获取链接（使用 sequence 字段）
result = client.query_cards("joytest", "创建人 = shijiazheng", max_records=1)
if result.get('cards'):
    card = result['cards'][0]
    url = ICafeClient.generate_card_url_from_card("joytest", card)
```

## 资源

### scripts/icafe_client.py

主要的 API 客户端实现，包含所有卡片相关的方法。此脚本用于：
- 执行卡片查询和操作
- 管理卡片评论
- 使用 IQL 表达式筛选卡片

该脚本使用 `requests` 库进行 HTTP 请求，并为每个方法包含完整的文档字符串。

### references/api_reference.md

详细的 API 参考文档，包含：
- 所有 API 端点的详细说明
- 请求/响应示例
- IQL 查询语法完整参考
- 错误处理指南
- 最佳实践

详见 [references/api_reference.md](references/api_reference.md)
