# iCafe API 参考文档

## 概述

iCafe 是百度内部的项目管理和协同平台，本技能提供了与 iCafe 平台卡片系统交互的 API 客户端。

> **📢 认证说明**: 所有 API 请求需要在请求头中携带认证 token。
> - 支持环境变量 `COMATE_AUTH_TOKEN` 设置
> - 或将 token 存储在 `~/.comate/login` 文件中
> - token 格式：`Bearer-{JWT_TOKEN}`

## API 基础信息

### 请求头

所有 API 请求需要包含以下请求头：

```http
Content-Type: application/json
x-ac-Authorization: Bearer-{your_token}
User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)
```

### 基础 URL

```
http://10.11.152.208:8701/api/process/icafe
```

## API 接口

---

### 1. 获取卡片详情

**Endpoint:** `GET /api/spaces/{space_id}/cards/{sequence}`

**描述:** 根据空间 ID 和卡片序列号获取单张卡片的详细信息。

> **注意**: `sequence` 参数使用的是卡片的序列号（数字，如：2008），而不是内部 ID（issueId）。例如：如果卡片链接是 `https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2008/show`，则 sequence 应为 `2008`。

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID（如：joytest, mapcio-qatools） |
| sequence | string | 是 | 卡片序列号（数字，如：2008） |

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| showAssociations | - | 否 | 显示关联信息（传空字符串启用） |
| showChildren | - | 否 | 显示子卡片（传空字符串启用） |
| showOkr | - | 否 | 显示 OKR 信息（传空字符串启用） |
| showAccumulate | - | 否 | 显示累计信息（传空字符串启用） |

**请求示例:**

```bash
curl -X GET "http://10.11.152.208:8701/api/process/icafe/api/spaces/joytest/cards/2008?showAssociations&showChildren" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)"
```

**响应示例:**

```json
{
  "cards": [
    {
      "id": "186279038",
      "sequence": 2667,
      "title": "API测试卡片",
      "detail": "这是一张通过API创建的测试卡片",
      "type": {
        "localId": 5007,
        "name": "Story"
      },
      "status": "待开发",
      "createdTime": "2026-03-10 11:24:34",
      "lastModifiedTime": "2026-03-10 11:25:12",
      "createdUser": {
        "username": "shijiazheng",
        "name": "史佳正",
        "email": "shijiazheng@baidu.com",
        "id": 590045
      },
      "responsiblePeople": [
        {
          "username": "shijiazheng",
          "name": "史佳正",
          "email": "shijiazheng@baidu.com",
          "id": 590045
        }
      ],
      "spaceName": "王杰的空间",
      "spacePrefixCode": "joytest",
      "isFinishedStatus": false,
      "properties": [...]
    }
  ],
  "code": 200,
  "currentPage": 1,
  "message": "OK, ",
  "pageSize": 1,
  "result": "success",
  "total": 1
}
```

---

### 2. 创建卡片

**Endpoint:** `POST /api/v2/space/{space_id}/issue/new`

**描述:** 在指定空间中创建一张新卡片。

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID |

**请求体:**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| issues | array | 是 | 卡片数组（支持批量创建） |
| issues[].title | string | 是 | 卡片标题 |
| issues[].detail | string | 是 | 卡片描述 |
| issues[].type | string | 否 | 卡片类型（Story/Bug/Task/Epic 等） |
| issues[].parent | string | 否 | 父卡片编号（sequence），用于创建子卡片 |
| issues[].comment | string | 否 | 初始评论 |
| issues[].fields | object | 否 | 自定义字段 |
| issues[].fields.负责人 | string | 否 | 负责人用户名（如：shijiazheng） |
| issues[].fields.流程状态 | string | 否 | 初始状态（根据空间配置） |
| issues[].fields.优先级 | string | 否 | 优先级（P0-Highest / P1-High / P2-Middle / P3-Low / P4-Lowest） |

> **注意**:
> - 优先级字段值因空间配置而异，标准格式为 `P0-Highest` / `P1-High` / `P2-Middle` / `P3-Low` / `P4-Lowest`。如果设置失败，说明该空间可能不支持该字段配置。
> - `parent` 字段需要放在 issue 对象的根级别（不是在 `fields` 中），值为父卡片的 `sequence`（序列号）。

**请求示例:**

```bash
# 创建普通卡片
curl -X POST "http://10.11.152.208:8701/api/process/icafe/api/v2/space/joytest/issue/new" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)" \
  -d '{
    "issues": [
      {
        "title": "测试卡片",
        "detail": "卡片描述内容",
        "type": "Story",
        "fields": {
          "负责人": "shijiazheng",
          "流程状态": "新建"
        },
        "comment": "初始评论"
      }
    ]
  }'

# 创建子卡片（设置 parent 字段）
curl -X POST "http://10.11.152.208:8701/api/process/icafe/api/v2/space/joytest/issue/new" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)" \
  -d '{
    "issues": [
      {
        "title": "子任务卡片",
        "detail": "子卡片描述内容",
        "type": "Task",
        "parent": "2667",
        "fields": {
          "负责人": "shijiazheng"
        }
      }
    ]
  }'
```

**响应示例:**

```json
{
  "issueSequences": [
    2667
  ],
  "issues": [
    {
      "sequence": 2667,
      "title": "测试卡片",
      "issueId": 186279038,
      "url": "https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2667/show"
    }
  ],
  "failures": null,
  "issueIdMap": null,
  "status": 200,
  "message": "OK."
}
```

---

### 3. 创建评论

**Endpoint:** `POST /api/v2/space/{space_id}/issue/{sequence}/comment`

**描述:** 为指定卡片添加评论。

> **注意**: `sequence` 参数使用的是卡片的序列号（数字，如：2008），而不是内部 ID（issueId）。

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID |
| sequence | string | 是 | 卡片序列号（数字，如：2008） |

**请求体:**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| commentMsg | string | 是 | 评论内容 |

**请求示例:**

```bash
curl -X POST "http://10.11.152.208:8701/api/process/icafe/api/v2/space/joytest/issue/2008/comment" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)" \
  -d '{
    "commentMsg": "这是一条新评论"
  }'
```

**响应示例:**

```json
{
  "status": 200,
  "message": "OK.",
  "commentMsg": {
    "id": 57877467
  }
}
```

---

### 4. 获取最近访问的空间

**Endpoint:** `GET /api/v2/space/latest`

**描述:** 获取当前用户最近访问的空间列表。

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| currentUser | string | 否 | 当前用户名 |

**请求示例:**

```bash
curl -X GET "http://10.11.152.208:8701/api/process/icafe/api/v2/space/latest?currentUser=shijiazheng" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)"
```

**响应示例:**

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    {
      "id": 75554,
      "name": "王杰的空间",
      "prefixCode": "joytest"
    },
    {
      "id": 66728,
      "name": "如流-工作流",
      "prefixCode": "workflow"
    },
    {
      "id": 70852,
      "name": "DevOps-项目协同iCafe",
      "prefixCode": "cloud-iCafe"
    }
  ]
}
```

---

### 5. 获取空间计划列表

**Endpoint:** `GET /api/v2/space/{space_id}/plans`

**描述:** 获取指定空间内的所有计划。

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID |

**请求示例:**

```bash
curl -X GET "http://10.11.152.208:8701/api/process/icafe/api/v2/space/joytest/plans" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)"
```

**响应示例:**

```json
{
  "result": [
    {
      "id": 871667,
      "name": "12.28~12.30",
      "path": "2022Q4/12.28~12.30",
      "parentId": 871666,
      "status": "ACTIVE"
    },
    {
      "id": 871666,
      "name": "2022Q4",
      "path": "2022Q4",
      "parentId": null,
      "status": "ACTIVE"
    }
  ],
  "status": 200,
  "message": "OK."
}
```

---

### 6. 查询卡片（IQL）

**Endpoint:** `GET /api/spaces/{space_id}/cards`

**描述:** 使用 IQL（iCafe Query Language）查询满足条件的卡片。

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID |

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| iql | string | 是 | IQL 查询表达式 |
| page | integer | 否 | 页码 |
| showDetail | - | 否 | 显示详情（传空字符串启用） |
| showAssociations | - | 否 | 显示关联信息（传空字符串启用） |
| isDesc | - | 否 | 降序排列（传空字符串启用） |
| order | string | 否 | 排序字段 |
| showChildren | - | 否 | 显示子卡片（传空字符串启用） |
| maxRecords | integer | 否 | 最大返回记录数 |
| showOkr | - | 否 | 显示 OKR 信息（传空字符串启用） |
| showAccumulate | - | 否 | 显示累计信息（传空字符串启用） |

**请求示例:**

```bash
curl -X GET "http://10.11.152.208:8701/api/process/icafe/api/spaces/joytest/cards?iql=类型%3D%20Bug%20AND%20负责人%3D%20currentUser&maxRecords=5&isDesc" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)"
```

**响应示例:**

```json
{
  "cards": [
    {
      "id": "186073926",
      "sequence": 2023,
      "title": "Bug 卡片",
      "type": {
        "localId": 5009,
        "name": "Bug"
      },
      "status": "新建",
      "createdTime": "2026-03-10 11:24:34",
      "lastModifiedTime": "2026-03-10 11:25:12",
      "createdUser": {
        "username": "shijiazheng",
        "name": "史佳正",
        "email": "shijiazheng@baidu.com",
        "id": 590045
      },
      "responsiblePeople": [
        {
          "username": "v_liuxiang",
          "name": "刘祥",
          "email": "v_liuxiang@baidu.com",
          "id": 590001
        }
      ],
      "spacePrefixCode": "joytest",
      "spaceName": "王杰的空间"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 5
}
```

---

### 7. 更新卡片

**Endpoint:** `POST /api/spaces/{space_id}/cards/{sequence}`

**描述:** 更新指定卡片的内容。

> **注意**:
> 1. `sequence` 参数使用的是卡片的序列号（数字，如：2008）
> 2. 更新字段时，某些字段（如 `流程状态`）可能触发状态流转检查，建议设置 `isCheckStatus=false`

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID |
| sequence | string | 是 | 卡片序列号（数字，如：2008） |

**请求头:**

```http
Content-Type: application/x-www-form-urlencoded
x-ac-Authorization: Bearer-{your_token}
User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)
```

**请求体 (form-data):**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| isCheckStatus | boolean | 否 | 是否检查状态流转，默认 false |
| fields | string | 否 | 更新字段列表，逗号分隔，格式：字段名=字段值 |
| comment | string | 否 | 更新评论 |
| labels | string | 否 | 标签列表，逗号分隔 |

**字段格式示例:**

```
fields=标题=新标题,内容=新描述,负责人=v_liuxiang,流程状态=进行中,优先级=P1-High,截止日期=2025-01-31
```

**请求示例:**

```bash
curl -X POST "http://10.11.152.208:8701/api/process/icafe/api/spaces/joytest/cards/2008" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)" \
  -d "isCheckStatus=false" \
  -d "fields=标题=更新后的标题,内容=更新后的描述,负责人=v_liuxiang,流程状态=进行中" \
  -d "comment=更新说明"
```

**响应示例:**

```json
{
  "code": 200,
  "message": "OK, ",
  "result": "success"
}
```

---

### 8. 查询卡片研发数据链信息

**Endpoint:** `GET /api/v2/space/{space_id}/issue/{sequence}/devInfo`

**描述:** 查询指定卡片的研发数据链相关信息，包括代码评审、代码合并、发布信息、测试记录、部署记录等研发流程数据。

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| space_id | string | 是 | 空间 ID（如：mapcio-qatools） |
| sequence | string | 是 | 卡片序列号（数字，如：1368） |

> **注意**: `sequence` 参数使用的是卡片的序列号（数字，如：1368），而不是内部 ID（issueId）。

**请求示例:**

```bash
curl -X GET "http://10.11.152.208:8701/api/process/icafe/api/v2/space/mapcio-qatools/issue/1368/devInfo" \
  -H "Content-Type: application/json" \
  -H "x-ac-Authorization: Bearer-{your_token}" \
  -H "User-Agent: iAPI/1.0.0 (http://iapi.baidu-int.com)"
```

**响应示例:**

```json
{
  "status": 0,
  "message": "success",
  "result": [
    {
      "sequence": 1368,
      "codeReview": [
        {
          "id": 120073414,
          "projectName": "baidu/soqa/workflow-project",
          "commitMessage": "mapcio-qatools-1368 [用户需求] 工作卡数字员工工单群打招呼消息建设",
          "branch": "stable",
          "url": "http://icode.baidu.com/myreview/changes/c/baidu/soqa/workflow-project/+/120073414",
          "commitId": "6594822ef6c816c349c2cd28fd5133713ec82164",
          "status": "MERGED",
          "codeReviewTime": "Mar 12, 2026 9:36:54 PM",
          "submitter": {
            "id": 590045,
            "name": "shijiazheng",
            "chineseName": "史佳正",
            "email": "shijiazheng@baidu.com"
          },
          "changeId": "I57d70c3c8aeb79763f6435acb06eda64ff750696"
        }
      ],
      "codeMerge": [
        {
          "projectName": "baidu/soqa/workflow-project",
          "branch": "stable",
          "gitCommits": [
            {
              "commitTime": "Mar 12, 2026 9:36:54 PM",
              "commitId": "6594822ef6c816c349c2cd28fd5133713ec82164",
              "changeUrl": "http://icode.baidu.com/myreview/changes/c/baidu/soqa/workflow-project/+/120073414",
              "pipeLineCommit": {
                "pipelineId": 244385903,
                "status": "SUCC",
                "pipeLineUrl": "http://agile.baidu.com//#/detail/244385903/job/0"
              }
            }
          ]
        }
      ],
      "releaseInfo": [
        {
          "id": 6743583,
          "module": "baidu/soqa/workflow-project",
          "branch": "stable",
          "versionId": "1.0.38.1",
          "releaseTime": "Mar 12, 2026 9:38:07 PM",
          "status": "SUCC",
          "agileReleaseUrl": "http://agile.baidu.com/#/detail/244385904/job/923581364",
          "triggerUser": "shijiazheng"
        }
      ],
      "initiateTest": [],
      "passTest": [],
      "deploy": [
        {
          "id": 6438030,
          "module": "baidu/soqa/workflow-project",
          "triggerTime": "Mar 12, 2026 6:51:11 PM",
          "triggerType": "DEPLOY_SUCCESS",
          "jobUrl": "http://console.cloud.baidu-int.com/devops/ipipe/workspaces/372767/pipeline-builds/244022649/stage-builds/581959064/task-builds/922142746/view"
        }
      ]
    }
  ]
}
```

**响应字段说明:**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| status | integer | 状态码，0 表示成功 |
| message | string | 响应消息 |
| result | array | 研发数据链结果数组 |
| result[].sequence | integer | 卡片序列号 |
| result[].codeReview | array | 代码评审记录列表 |
| result[].codeReview[].id | integer | 代码评审 ID |
| result[].codeReview[].url | string | 代码评审链接 |
| result[].codeReview[].status | string | 评审状态（MERGED、PASSED 等） |
| result[].codeMerge | array | 代码合并记录 |
| result[].codeMerge[].gitCommits | array | Git 提交记录 |
| result[].releaseInfo | array | 发布信息列表 |
| result[].releaseInfo[].versionId | string | 版本号 |
| result[].releaseInfo[].agileReleaseUrl | string | 发布流水线链接 |
| result[].initiateTest | array | 发起测试记录 |
| result[].passTest | array | 通过测试记录 |
| result[].deploy | array | 部署记录 |

---

## IQL 查询语法

### 基本运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| AND | 且 | `类型 = Bug AND 负责人 = currentUser` |
| OR | 或 | `类型 = Bug OR 类型 = Story` |
| = | 等于 | `状态 = 新建` |
| != | 不等于 | `状态 != 已关闭` |
| > | 大于 | `创建时间 > "2025-01-01"` |
| < | 小于 | `创建时间 < "2025-01-31"` |
| >= | 大于等于 | `优先级 >= P2` |
| <= | 小于等于 | `优先级 <= P1` |
| in | 包含 | `类型 in (Bug, Story, Epic)` |
| not in | 不包含 | `状态 not in (已关闭, 已取消)` |
| is empty | 为空 | `截止日期 is empty` |
| is not empty | 不为空 | `截止日期 is not empty` |
| ~ | 包含（文本） | `标题 ~ 测试` |
| !~ | 不包含（文本） | `标题 !~ 私有` |

### 常用字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| 类型 | 单选 | 卡片类型 | `类型 = Bug` |
| 流程状态 | 单选 | 当前状态 | `流程状态 = 开发中` |
| 负责人 | 人员 | 负责人用户 | `负责人 = currentUser` |
| 优先级 | 单选 | 优先级 | `优先级 = P1-High` |
| 标题 | 文本 | 卡片标题 | `标题 ~ 测试` |
| 创建时间 | 日期 | 创建日期时间 | `创建时间 > "2025-01-01"` |
| 更新时间 | 日期 | 更新日期时间 | `更新时间 > "2025-01-01"` |
| 截止日期 | 日期 | 计划完成日期 | `截止日期 <= "2025-01-31"` |
| 关键字 | 标签 | 关键词标签 | `关键字 ~ 重要` |
| 所属计划 | 树结构 | 所属的计划 | `所属计划 = 迭代1` |

### IQL 查询示例

| 需求 | IQL 表达式 |
|------|------------|
| 查询 Bug 类型 | `类型 = Bug` |
| 查询当前用户负责的卡片 | `负责人 = currentUser` |
| 查询新建状态的卡片 | `流程状态 = 新建` |
| 查询 Bug 且负责人是当前用户 | `类型 = Bug AND 负责人 = currentUser` |
| 查询创建时间在指定日期之后 | `创建时间 > "2025-01-01"` |
| 查询多种类型卡片 | `类型 in (Bug, Epic, Story)` |
| 查询标题包含关键词 | `标题 ~ 测试` |
| 查询负责人在指定列表中 | `负责人 in (user1, user2, user3)` |
| 查询截止日期为空的任务 | `类型 = Task AND 截止日期 is empty` |
| 查询高优先级 Bug | `类型 = Bug AND 优先级 = P1-High` |

---

## 响应状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 请求成功 | 正常处理响应数据 |
| 400 | 请求参数错误 | 检查请求参数格式和内容 |
| 401 | 认证失败 | 检查 token 是否有效 |
| 403 | 权限不足 | 确认用户有访问该空间/卡片的权限 |
| 404 | 资源不存在 | 检查 space_id、sequence 是否正确 |
| 500 | 服务器错误 | 联系 iCafe 平台支持 |

---

## 常见错误

### 错误示例

```json
{
  "code": "error",
  "message": "Invalid space_id",
  "details": "Space 'invalid-space' does not exist"
}
```

### 错误处理建议

1. **认证错误**: 检查 `~/.comate/login` 文件是否存在且内容正确
2. **参数错误**: 确保必填参数都已提供，格式正确
3. **权限错误**: 确认当前用户对目标空间和卡片有访问权限
4. **网络错误**: 检查网络连接和 API 服务可用性

---

## 卡片链接模板

### 卡片 URL 格式

```
https://console.cloud.baidu-int.com/devops/icafe/issue/{space_id}-{card_sequence}/show
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| space_id | 空间前缀码 (prefixCode) | `joytest`, `mapcio-qatools` |
| card_sequence | 卡片序号 (sequence) | `2008`, `1360` |

> **注意**: URL 中的卡片编号使用的是 `sequence`（序列号），而非内部 ID `issueId`。
> - `sequence`: 卡片的可读序号，如 2008（对应链接 joytest-2008）
> - `issueId`: 卡片的内部 ID，如 186061811（仅在 API 内部使用）

### 链接示例

```
https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2008/show
https://console.cloud.baidu-int.com/devops/icafe/issue/mapcio-qatools-1360/show
```

### Python 生成链接

```python
def generate_card_url(space_prefix: str, sequence: str) -> str:
    """生成 iCafe 卡片链接"""
    return f"https://console.cloud.baidu-int.com/devops/icafe/issue/{space_prefix}-{sequence}/show"

# 使用示例
url = generate_card_url("joytest", "2008")
# 返回: https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2008/show
```

### 从 API 响应生成链接

```python
def generate_card_url_from_data(card: dict) -> str:
    """从 API 响应数据生成链接"""
    # 从响应中获取空间前缀和序号
    space_prefix = card.get('spacePrefixCode', '')
    sequence = card.get('sequence', '')
    return generate_card_url(space_prefix, str(sequence))

# 使用示例
card = {
    "spacePrefixCode": "joytest",
    "sequence": 2008,
    "title": "测试卡片"
}
url = generate_card_url_from_data(card)
# 返回: https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2008/show
```

### 从创建卡片响应生成链接

```python
def get_card_url_from_create_response(response: dict) -> str:
    """从创建卡片的 API 响应中提取链接"""
    if response and 'issues' in response and response['issues']:
        return response['issues'][0].get('url', '')
    return ''

# 使用示例
response = {
    "issues": [
        {
            "sequence": 2008,
            "url": "https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2008/show"
        }
    ]
}
url = get_card_url_from_create_response(response)
# 返回: https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2008/show
```

---

## 最佳实践

### 1. 认证管理

```bash
# 推荐使用环境变量
export COMATE_AUTH_TOKEN="Bearer-{your_token}"

# 或存储到登录文件
echo "Bearer-{your_token}" > ~/.comate/login
```

### 2. 错误处理

```python
try:
    card = client.get_card_by_id("joytest", "2008")  # 2008 是卡片序列号
except ValueError as e:
    print(f"参数错误: {e}")
except requests.RequestException as e:
    print(f"请求失败: {e}")
    if e.response:
        print(f"状态码: {e.response.status_code}")
        print(f"响应: {e.response.text}")
```

### 3. 批量操作

```python
# 批量创建卡片
issues = [
    {"title": f"任务{i}", "detail": f"任务{i}的描述"}
    for i in range(1, 6)
]
client.create_cards_batch("joytest", issues)
```

### 4. 分页查询

```python
page = 1
page_size = 50
while True:
    result = client.query_cards(
        space_id="joytest",
        iql="类型 = Bug",
        page=page,
        max_records=page_size
    )
    cards = result.get('cards', [])
    if not cards:
        break
    process_cards(cards)
    page += 1
```

---

## 相关资源

- [iCafe 控制台](https://console.cloud.baidu-int.com/devops/icafe)
- [iCafe 开发者文档](http://iapi.baidu-int.com)
- [技能文档](../SKILL.md)
