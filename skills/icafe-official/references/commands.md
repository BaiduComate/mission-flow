# 命令详细参考

本文档包含 icafe-cli 所有命令的参数表、返回数据结构和使用示例。

**通用返回格式**: 所有命令的返回都是 JSON。HTTP 层错误 (非 2xx) 由 CLI 拦截到 stderr，退出码 4。进程退出码 1/2/4 的区分见 [错误处理参考](error-handling.md#cli-退出码)。

**业务成功判断**: 不同命令的成功标识字段和成功值不同，agent 必须根据具体命令检查对应字段:

| 命令 | 成功标识字段 | 成功值 |
|------|-------------|--------|
| `card get`, `card update`, `card query` | `code` | `200` |
| `devinfo card`, `plan update-date` | `status` | `0` |
| `ai-pre-review start/result`, `ai-codegen start/result` | `status` | `"OK"` (macross BaseResponse) |
| 其他所有命令 | `status` | `200` |

简便做法: 对 iCafe 类命令检查 `code`/`status` 为 `200` 或 `0`；对 ai-pre-review/ai-codegen 命令检查 `status` 为 `"OK"`。

---

## card 命令组

### card get — 获取卡片详情

根据空间标识和序列号获取卡片的完整信息。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | 是 | 空间前缀码 (prefixCode)，可通过 `space latest` 获取 |
| `--sequence` | 是 | 卡片序列号，支持逗号分隔批量查询，如 `1001,1002` |
| `--show-associations` | 否 | 额外返回关联的其他卡片 |
| `--show-children` | 否 | 额外返回子卡片列表 |
| `--show-okr` | 否 | 额外返回关联的 OKR 信息 |

```bash
icafe-cli card get --space myspace --sequence 1001
icafe-cli card get --space myspace --sequence 1001,1002
```

**返回示例**:

```json
{
  "cards": [
    {
      "sequence": 1001,
      "title": "修复登录白屏",
      "id": "186604712",
      "status": "开发中",
      "type": { "localId": 5009, "name": "Bug" },
      "isFinishedStatus": false,
      "detail": "<p>卡片正文 HTML</p>",
      "responsiblePeople": [
        { "username": "zhangsan", "name": "张三", "email": "zhangsan@baidu.com" }
      ],
      "createdUser": { "username": "lisi", "name": "李四" },
      "createdTime": "2026-03-25 10:00:00",
      "lastModifiedUser": { "username": "zhangsan", "name": "张三" },
      "lastModifiedTime": "2026-03-25 15:30:00",
      "spacePrefixCode": "myspace",
      "properties": [
        { "propertyName": "优先级", "displayValue": "P1-High", "fieldType": "SELECT_LIST" },
        { "propertyName": "所属计划", "displayValue": "Sprint1", "fieldType": "PLAN_BOX" }
      ]
    }
  ],
  "code": 200, "total": 1, "currentPage": 1, "pageSize": 1,
  "result": "success", "message": "OK, "
}
```

**关键字段说明**:
- `sequence`: 卡片编号，用于 URL 和 commit message
- `status`: 当前流程状态的中文名
- `type.name`: 卡片类型名
- `isFinishedStatus`: 是否处于终态 (已关闭/已完成)
- `responsiblePeople[].username`: 负责人的用户名
- `properties[]`: 所有自定义字段，通过 `propertyName` 和 `displayValue` 读取字段值

---

### card create — 创建卡片

在指定空间中创建新卡片。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--title` | **是** | 卡片标题，不能为空，最大 500 字符 |
| `--type` | **是** | 卡片类型名称，**区分大小写** (如 `Story` 不是 `story`)。通过 `space issue-types` 查询 |
| `--detail` | 否 | 卡片正文，**必须 HTML 格式**。不传则使用模板默认正文 |
| `--assignee` | 否 | 负责人百度用户名。不传则 CLI 自动填充当前用户 |
| `--status` | 否 | 初始状态 (中文)。不传则使用工作流默认初始状态 |
| `--priority` | 否 | 优先级如 `P1-High`。并非所有类型都有此字段，先用 `type-fields` 确认 |
| `--comment` | 否 | 创建时同时添加的评论 |
| `--parent` | 否 | 父卡片序列号，用于创建子卡片 (如 Epic 下创建 Story) |
| `--fields` | 否 | 自定义字段: `"字段中文名1=值1,字段中文名2=值2"`。多选字段值可含逗号 (如 `"标签=tag1,tag2,模块=前端"`)，CLI 按 `key=value` 边界智能拆分。通过 `type-fields` 查询字段名和合法值 |

```bash
# 最简创建 (仅必填参数)
icafe-cli card create --space myspace --title "修复登录白屏" --type Bug

# 完整创建
icafe-cli card create --space myspace --title "修复登录白屏" \
  --detail "<p>Chrome 浏览器上登录页面白屏</p>" \
  --type Bug --priority P1-High --assignee zhangsan

# 创建子卡片
icafe-cli card create --space myspace --title "子任务" --type Task --parent 1001

# 多选字段 (标签值含逗号，CLI 自动识别)
icafe-cli card create --space myspace --title "新功能" --type Story \
  --fields "标签=tag1,tag2,模块=前端"
```

**返回示例** (成功):

```json
{
  "status": 200,
  "message": "OK.",
  "issueSequences": [1001],
  "issues": [
    {
      "issueId": 186604909,
      "sequence": 1001,
      "title": "修复登录白屏",
      "url": "https://console.cloud.baidu-int.com/devops/icafe/issue/myspace-1001/show"
    }
  ],
  "failures": null
}
```

**返回示例** (失败 — 类型不存在):

```json
{
  "status": 401,
  "message": "Field name or value is incorrect.",
  "failures": [
    {
      "issueName": "卡片标题",
      "failures": { "type": "REQUIRED" }
    }
  ]
}
```

**返回示例** (失败 — 父卡片不合法):

```json
{
  "status": 401,
  "message": "Field name or value is incorrect.",
  "failures": [
    {
      "issueName": "卡片标题",
      "failures": { "parent": "INVAILD" }
    }
  ]
}
```

**关键字段说明**:
- `status`: 200=成功，401=字段校验错误 (类型不存在/父卡片不合法/字段值不合法)，304=空间不存在，101=无权限
- `issues[].sequence`: 新创建的卡片序列号，用于后续操作和 URL
- `issues[].url`: 卡片在 iCafe 上的完整链接
- **注意**: OpenAPI 层面创建接口只返回基本信息 (`sequence`, `title`, `url`)，不返回完整卡片详情。如需确认自动分配的状态、负责人等字段值，创建后需再调用 `card get` 查询
- `failures[]`: 字段校验失败详情，`failures.failures` 是一个 map，key 为字段名，value 为错误类型:
  - `REQUIRED` — 必填字段缺失 (title 或 type)
  - `INVAILD` — 值不合法 (parent 不存在或类型层级不匹配，creator 不存在)
  - `NOT_IMPORTED` — 字段在该空间/类型下不存在，或字段值不合法 (如负责人用户名不存在)
- **注意**: 退出码 0 不代表业务成功，必须检查 JSON 中的 `status` 字段!

**后端行为**:
- **API 层校验的字段**: `title` (非空, 最长 500)、`type` (必须在该空间的类型列表中, 区分大小写)、`parent` (如有, 父卡片必须存在且类型层级关系合法)
- 其他字段 (包括 `space type-fields` 中标记为 `required: true` 的自定义必填字段) **API 不做校验，不传也能创建成功**
- `detail` 为空时回退到类型模板的默认正文；如模板也无则正文为空
- 流程状态未指定时，自动使用工作流中第一个可达的初始状态。如果传了状态但不在该类型的状态列表中，也会使用默认状态
- 负责人 (`--assignee` / `fields.负责人`): 不存在时返回 401 + `failures` 中标记 `NOT_IMPORTED`。CLI 未指定 `--assignee` 时自动填充当前用户
- 未在 `--fields` 中传入的自定义字段，使用模板默认值 (如有)；模板未配默认值的字段为空
- `--parent` 只支持当前空间内的父卡片 (后端支持跨空间父卡片 `parentSpacePrefixCode`，CLI 暂未实现)
- 可一次创建多张卡片 (API 层支持最多 100 张，CLI 层当前为单张)
- **注意**: `space type-fields` 返回的 `required` 字段仅反映 **Web UI** 的校验规则，API 不受此约束。即使 `required: true` 的字段未传，API 也会返回 200 成功

**覆盖优先级**:
- `--fields` 中的键如果与 `--assignee`/`--status`/`--priority` 设置了相同字段，`--fields` 的值会覆盖前者
- 例如 `--assignee a --fields "负责人=b"` 最终负责人为 b

---

### card update — 更新卡片

修改已有卡片的字段值。**至少需要提供一个修改项或 `--comment`**。

**注意: 卡片类型 (type) 创建后不可修改**，`--fields "类型=xxx"` 也无效。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |
| `--title` | 否 | 新标题。**不能设为空** |
| `--detail` | 否 | 新正文，**HTML 格式** |
| `--assignee` | 否 | 新负责人用户名 |
| `--status` | 否 | 新流程状态，传**中文名称** (如 `开发中`)，不是 ID |
| `--priority` | 否 | 新优先级，如 `P1-High` |
| `--comment` | 否 | 本次更新的操作评论 |
| `--fields` | 否 | 自定义字段: `"字段中文名=值"`，多个逗号分隔。如果与 `--assignee`/`--status`/`--priority` 同名，`--fields` 的值会覆盖前者 |
| `--no-check-status` | 否 | 跳过状态流转规则校验 |

```bash
# 修改状态
icafe-cli card update --space myspace --sequence 1001 --status 开发中

# 修改多个字段
icafe-cli card update --space myspace --sequence 1001 \
  --assignee zhangsan --priority P1-High --comment "紧急处理"

# 强制跳过状态流转校验
icafe-cli card update --space myspace --sequence 1001 --status 已完成 --no-check-status
```

**返回示例** (成功):

```json
{
  "code": 200,
  "result": "success",
  "message": "OK, "
}
```

**关键字段说明**:
- `code`: 200=成功
- 失败时通过 HTTP 状态码返回: 404=卡片不存在, 403=无权限, 500=字段/状态错误

**更新行为**:
- 选择类字段的值必须传 `space type-fields` 返回的 displayValue (如 `P1-High`)
- `--status` 传中文状态名，默认会校验状态流转。如果流转不合法需加 `--no-check-status`
- **改状态前建议先用 `card next-statuses` 查询当前可达的目标状态**
- 状态流转要求填写的必填字段，可在同一次 `--fields` 中传入
- 后端有 Redis 锁 (15秒超时)，同一卡片不能同时更新
- 字段值可以包含 `=` 号 (如 `--fields "备注=a=b"` 会正确解析为字段名 `备注`、值 `a=b`，后端按第一个 `=` 拆分)
- 传空字符串可清空字段值 (如 `--fields "模块="`)，后端将 `""`、`"null"`、`","` 均视为空值。**标题不能设为空**
- **清空字段只能用 `--fields`**: 命名 flag (`--detail ""`, `--assignee ""` 等) 传空值会被 CLI 忽略 (不发送给后端)，不等于清空。要清空字段请用 `--fields "内容="` 或 `--fields "负责人="`
- **表单约定**: luigi 的 `OneIssueApiUpdateBean.fields` 为 `String[]`，每个元素是一条 `显示名=值`。CLI 会将 `--title`/`--detail`/`--assignee`/`--status`/`--priority` 以及 `--fields` 中逗号分隔的各对键值，分别作为多个同名表单参数 `fields` 提交（而非拼成一条逗号串）。

**常见 HTTP 500 错误**:
- `"field value error : 字段名=值"` — 字段值不在合法选项中
- `"字段名: field does not exist!"` — 字段名在该类型中不存在，请通过 `space type-fields` 确认
- `"流程状态不存在"` — 状态名在该类型中不存在，请通过 `space type-statuses` 确认
- `"无法流转到该流程状态"` — 当前状态到目标状态的流转路径不合法，需加 `--no-check-status` 或先用 `card next-statuses` 确认可达状态
- `"还有必填字段没有填写: fieldName"` — 状态流转要求某些字段非空，在 `--fields` 中补充

---

### card query — 查询卡片

按条件查询空间中的卡片。不传 `--iql` 时返回所有卡片。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--iql` | 否 | IQL 查询表达式，字段名用中文。详见 [IQL 语法](iql-syntax.md) |
| `--page` | 否 | 页码，从 1 开始，最大 100 |
| `--max-records` | 否 | 每页数量，CLI 默认 20，最大 100，超过返回 400 |
| `--order` | 否 | 排序字段，默认 `createTime`。支持: `createTime`, `lastModifiedTime`, `sequence`, `creatorId`, `responsiblePeopleId`, `issueStatusId`, `title`; 别名: `status`, `owner`, `creator`。不支持文本类型字段 |
| `--desc` | 否 | 是否降序，默认 `true` |
| `--show-detail` | 否 | 返回完整字段 (默认只返回基本信息) |
| `--show-associations` | 否 | 返回关联卡片 |
| `--show-children` | 否 | 返回子卡片 |

```bash
# 查询当前用户负责的未关闭卡片
icafe-cli card query --space myspace --iql "负责人 = currentUser AND 流程状态 != 已关闭"

# 查询高优先级 Bug
icafe-cli card query --space myspace --iql "类型 = Bug AND 优先级 = P1-High" --max-records 50
```

**返回示例**:

```json
{
  "cards": [
    {
      "sequence": 1001,
      "title": "修复登录白屏",
      "status": "开发中",
      "type": { "name": "Bug" },
      "isFinishedStatus": false,
      "responsiblePeople": [{ "username": "zhangsan" }],
      "createdTime": "2026-03-25 10:00:00",
      "properties": [...]
    }
  ],
  "code": 200, "total": 15, "currentPage": 1, "pageSize": 10,
  "result": "success", "message": "OK, "
}
```

**关键字段说明**:
- `cards[]`: 卡片列表，结构与 `card get` 返回的 `cards[]` 一致
- `total`: 满足条件的卡片总数 (不是当前页数量)
- `currentPage`: 当前页码
- `pageSize`: **总页数** (注意: 不是每页记录数，是 `ceil(total/maxRecords)`)
- 分页上限: 最大 100 页 x 100 条 = 10000 张卡片

---

### card current-status — 获取卡片当前流程状态

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |

```bash
icafe-cli card current-status --space myspace --sequence 1001
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "statusName": "新建",
  "statusId": 52,
  "isFinishedStatus": false
}
```

**关键字段说明**:
- `statusName`: 当前状态中文名 (如 `新建`、`开发中`、`已关闭`)
- `isFinishedStatus`: 是否终态
- 此命令**不返回可流转的目标状态列表**。要查看从当前状态可以流转到哪些目标状态，用 `card next-statuses`。要查看该类型所有合法的流程状态名，用 `space type-statuses`

---

### card next-statuses — 获取卡片可流转的目标状态

基于卡片当前状态、类型工作流规则和当前用户角色权限，返回可以直接流转到的目标状态列表。**修改卡片状态前推荐使用此命令，比 `space type-statuses` 更精确**。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |

```bash
icafe-cli card next-statuses --space myspace --sequence 1001
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    { "statusId": 53, "statusName": "开发中" },
    { "statusId": 54, "statusName": "待测试" },
    { "statusId": 55, "statusName": "测试中" }
  ]
}
```

**关键字段说明**:
- `result[]`: 可流转的目标状态列表
- `result[].statusName`: 状态中文名 — **可直接用于 `card update --status` 的值**
- `result[].statusId`: 状态数字 ID
- `result` 为空数组: 当前状态没有可达的目标状态 (可能是终态，或工作流未配置出边)

**错误场景**:
- `status: 304` — 空间不存在
- `status: 902` — 卡片不存在或服务端异常

**后端行为**:
- 接口从卡片上读取当前 spaceId、issueTypeId、issueStatusId，再结合当前用户的角色权限查询工作流
- 如果该类型**未开启工作流**，返回该类型下的全部状态 (此时和 `type-statuses` 等价)
- 如果该类型**开启了工作流**，根据工作流配置的出边 + 用户角色过滤，返回可达状态的子集

**与 `space type-statuses` 的区别**:
- `type-statuses` 返回该类型**所有合法状态** (不考虑起始状态)
- `next-statuses` 以卡片当前状态为起点，结合当前用户的角色权限，返回**工作流中可达的目标状态**
- 改状态前优先用 `next-statuses`，如果目标状态不在列表中，说明需要 `--no-check-status` 强制跳过

---

### card history — 卡片全量操作历史

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequences` | **是** | 序列号，逗号分隔，最多 50 个 |

```bash
icafe-cli card history --space myspace --sequences 1001
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    {
      "sequence": 1001,
      "type": { "name": "Bug" },
      "histories": [
        {
          "operator": "zhangsan",
          "operationTime": "2026-03-25 19:24:32",
          "comment": "由API新建",
          "diffDescription": "张三 创建了卡片[修复登录白屏]",
          "diffDescriptionStructured": [
            {
              "fieldName": "流程状态",
              "oldValue": "",
              "newValue": "开发中",
              "opType": "MODIFY",
              "opUser": { "username": "zhangsan" }
            }
          ],
          "sourceStatusName": "新建",
          "targetStatusName": "开发中"
        }
      ]
    }
  ]
}
```

**关键字段说明**:
- `histories[]`: 按时间倒序排列的操作记录
- `diffDescriptionStructured[]`: 结构化变更详情，包含 `fieldName`/`oldValue`/`newValue`
- `sourceStatusName`/`targetStatusName`: 操作前后的流程状态 (新建时 source 为 null)
- `comment`: 操作时附带的评论

---

### card status-changes — 卡片状态流转历史

仅返回状态变更记录，不含字段变更。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequences` | **是** | 序列号，逗号分隔，最多 50 个 |

```bash
icafe-cli card status-changes --space myspace --sequences 1001
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    {
      "sequence": 1001,
      "histories": [
        {
          "sourceStatusName": "新建",
          "targetStatusName": "开发中",
          "operator": "zhangsan",
          "operationTime": "2026-03-25 19:24:32",
          "opType": "MODIFY"
        },
        {
          "sourceStatusName": null,
          "targetStatusName": "新建",
          "operator": "zhangsan",
          "operationTime": "2026-03-25 10:00:00",
          "opType": "INSERT"
        }
      ]
    }
  ]
}
```

---

## comment 命令组

### comment create — 添加评论

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |
| `--content` | **是** | 评论内容，支持 HTML |

```bash
icafe-cli comment create --space myspace --sequence 1001 --content "已完成代码评审，LGTM"
```

**返回示例** (成功): `{"status": 200, "message": "OK."}`

**失败**: 卡片不存在返回 `{status: 601, message: "card is not exist!"}`，空间不存在返回 `{status: 304}`。

---

### comment get — 获取评论列表

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |

```bash
icafe-cli comment get --space myspace --sequence 1001
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    {
      "id": 58250539,
      "content": "已完成代码评审，LGTM",
      "username": "zhangsan",
      "chineseName": "张三",
      "createTime": "2026-03-25 19:24:39",
      "isDeleted": false,
      "parentCommentId": 0
    }
  ]
}
```

**关键字段说明**:
- `id`: 评论 ID，`comment update` 需要此值
- `username`: 评论作者的用户名
- `parentCommentId`: 父评论 ID (0 表示顶级评论)

---

### comment update — 修改评论

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--comment-id` | **是** | 评论 ID (通过 `comment get` 获取) |
| `--content` | **是** | 修改后的内容 |

**只能编辑自己的评论**，编辑他人评论返回 `{status: 101}`。

```bash
icafe-cli comment update --space myspace --comment-id 58250539 --content "补充: 需要增加单元测试"
```

---

## space 命令组

### space latest — 获取最近访问的空间

无需传参，通过 Token 自动识别用户。**这是获取空间 prefixCode 的首选方式**。

```bash
icafe-cli space latest
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    { "id": 56355, "name": "DevOps-项目协同iCafe", "prefixCode": "cloud-iCafe" },
    { "id": 56492, "name": "xu-c01", "prefixCode": "xu-c01" }
  ]
}
```

**关键字段说明**:
- `result[].prefixCode`: **这就是所有命令 `--space` 参数需要的值**
- `result[].name`: 空间显示名称

---

### space tree — 获取空间树

| 参数 | 必需 | 说明 |
|------|------|------|
| `--username` | 否 | 百度用户名 (邮箱前缀，如 `zhangsan`)，查询该用户有权限的空间树。不传则默认查当前登录用户 |
| `--permission` | 否 | 权限过滤。不传则默认返回 read 及以上权限的所有空间。可选值: `permission.read`, `permission.create`, `permission.write`, `permission.spaceadmin` |

```bash
icafe-cli space tree
icafe-cli space tree --permission permission.write
```

---

### space issue-types — 获取空间卡片类型

**创建卡片前必须先调此命令确认可用类型**。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |

```bash
icafe-cli space issue-types --space myspace
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": {
    "issueTypes": [
      { "id": 56075, "name": "Epic", "color": "41a7fa" },
      { "id": 5007, "name": "Story", "color": "EBC400" },
      { "id": 54444, "name": "Task", "color": "78bf13" },
      { "id": 5009, "name": "Bug", "color": "EB7600" }
    ]
  }
}
```

**关键字段说明**:
- `issueTypes[].name`: **这就是 `card create --type` 需要的值，区分大小写**

---

### space type-fields — 获取类型字段定义

返回指定类型在**创建阶段**的所有字段：名称、类型、是否必填、可选值。**创建/更新卡片前必须调此命令了解字段规则**。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--type` | **是** | 类型名称，通过 `issue-types` 获取 |

```bash
icafe-cli space type-fields --space myspace --type Story
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    {
      "display": "负责人",
      "name": "responsiblePeopleId",
      "type": "user_picker",
      "required": false,
      "defaultValue": null,
      "valueItems": []
    },
    {
      "display": "优先级",
      "name": null,
      "type": "select_list",
      "required": false,
      "defaultValue": null,
      "valueItems": ["P0-Highest", "P1-High", "P2-Middle", "P3-Low", "P4-Lowest"]
    },
    {
      "display": "所属计划",
      "type": "plan_box",
      "required": false,
      "valueItems": ["2026Q1/Sprint1", "2026Q1/Sprint2"]
    },
    {
      "display": "下拉列表",
      "type": "select_list",
      "required": true,
      "valueItems": ["选项A", "选项B", "选项C"]
    }
  ]
}
```

**关键字段说明**:
- `display`: 字段中文名 — **`--fields` 参数的 key 就用这个值**
- `type`: 字段类型 (select_list, user_picker, number_field 等)
- `required`: 是否在 Web UI 上必填。**注意: API 层不强制校验此标记，即使 `required: true` 的字段未传，API 创建也会成功**。建议尽量填充，但不必因为无法确定值而阻塞创建
- `valueItems[]`: 选择类字段的**合法可选值列表**。创建/更新时传的值必须在此列表中
- `defaultValue`: 模板默认值

---

### space type-statuses — 获取类型流程状态列表

返回指定空间中某卡片类型配置的所有流程状态。**修改卡片状态前建议先调此命令确认合法的状态名称**。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--type` | **是** | 类型名称，通过 `issue-types` 获取 |

```bash
icafe-cli space type-statuses --space myspace --type Task
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    { "issueStatusId": 52, "name": "新建", "color": "78bf13", "addSub": false },
    { "issueStatusId": 53, "name": "开发中", "color": "e65055", "addSub": false },
    { "issueStatusId": 54, "name": "待测试", "color": "5069e6", "addSub": false },
    { "issueStatusId": 55, "name": "测试中", "color": "EB7600", "addSub": false },
    { "issueStatusId": 56, "name": "待上线", "color": "e048ae", "addSub": false },
    { "issueStatusId": 57, "name": "已完成", "color": "0098b3", "addSub": false }
  ]
}
```

**关键字段说明**:
- `name`: 状态中文名 — **`card update --status` 就用这个值**
- `issueStatusId`: 状态数字 ID
- `color`: 状态颜色 (十六进制)
- `addSub`: 该状态下是否允许拆分子卡片
- 此命令返回的是该类型所有合法状态，**不考虑起始状态**。要查看从当前卡片当前状态可流转到哪些目标状态，用 `card next-statuses`

---

## plan 命令组

### plan list — 获取计划列表

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |

```bash
icafe-cli plan list --space myspace
```

**返回示例**:

```json
{
  "status": 200,
  "message": "OK.",
  "result": [
    { "id": 618149, "name": "06.16~06.22", "path": "05.27~06.23/06.16~06.22", "parentId": 610684, "status": "ARCHIVED" },
    { "id": 878635, "name": "12.12~12.18", "path": "12.12~12.18", "parentId": null, "status": "ACTIVE" }
  ]
}
```

**关键字段说明**:
- `id`: 计划数字 ID，用于 `plan update-date --plan-id`
- `path`: 计划路径，用于 `plan get --path`。子计划路径格式为 `父计划/子计划`
- `status`: `ACTIVE` 或 `ARCHIVED`

---

### plan get — 获取计划详情

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--path` | **是** | 计划路径 (通过 `plan list` 获取) |

```bash
icafe-cli plan get --space myspace --path "2026Q1/Sprint1"
```

---

### plan create — 创建计划

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--name` | **是** | 计划名称，不能包含 `\|,<>()/\"` |
| `--start-date` | **是** | 开始日期 `YYYY-MM-DD` |
| `--end-date` | **是** | 结束日期 `YYYY-MM-DD`，必须晚于开始日期 |
| `--desc` | 否 | 计划描述 |
| `--parent` | 否 | 父计划路径，用于创建子计划 |
| `--stick` | 否 | 是否置顶计划 |

```bash
icafe-cli plan create --space myspace --name "Sprint1" --start-date 2024-01-01 --end-date 2024-01-14
```

---

### plan update-date — 更新计划日期

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--plan-id` | **是** | 计划数字 ID (通过 `plan list` 获取) |
| `--start-date` | 否 | 新开始日期 |
| `--end-date` | 否 | 新结束日期 |

至少提供一个日期。

```bash
icafe-cli plan update-date --space myspace --plan-id 878635 --end-date 2024-01-21
```

**注意**: 此命令成功时返回 `status: 0`，不是 `200`。

---

### plan milestones — 获取计划和里程碑

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--start-date` | 否 | 按开始日期过滤 |
| `--end-date` | 否 | 按结束日期过滤 |
| `--page` | 否 | 页码 |
| `--include-archived` | 否 | 包含已归档的计划 |

```bash
icafe-cli plan milestones --space myspace --start-date 2024-01-01 --end-date 2024-03-31
```

---

## devinfo 命令组

### devinfo card — 获取卡片研发数据链

查询卡片关联的代码评审、合入、部署等研发活动。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequences` | **是** | 序列号，逗号分隔，最多 100 个 |

不存在的序列号会被静默跳过。

```bash
icafe-cli devinfo card --space myspace --sequences 1001,1002
```

**返回示例**:

```json
{
  "status": 0,
  "message": "success",
  "result": [
    {
      "sequence": 1001,
      "codeReview": [...],
      "codeMerge": [...],
      "deploy": [...],
      "initiateTest": [...],
      "passTest": [...],
      "releaseInfo": [...]
    }
  ]
}
```

**注意**: `devinfo card` 成功时 `status` 为 `0`，不是 `200`。`devinfo active-cards` 成功时 `status` 为 `200`。

---

### devinfo active-cards — 查询有研发活动的卡片

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--start-time` | 否 | 起始时间，格式 `yyyy-MM-dd HH:mm:ss` |
| `--end-time` | 否 | 截止时间，格式 `yyyy-MM-dd HH:mm:ss` |
| `--page` | 否 | 页码 |
| `--max-records` | 否 | 每页数量 |

```bash
icafe-cli devinfo active-cards --space myspace --start-time "2024-01-01 00:00:00" --end-time "2024-01-31 23:59:59"
```

---

## ai-pre-review 命令组

卡片预审命令，使用 AI 对卡片内容进行质量检查。**异步操作**：先发起，再查结果。

### ai-pre-review rules — 查询预审规则

获取指定空间配置的卡片预审规则列表。规则用于在发起 AI 预审时指导 AI 关注特定方面。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |

```bash
icafe-cli ai-pre-review rules --space myspace
```

**返回示例**:

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "验收标准",
      "content": "需求必须包含明确的验收标准和测试用例",
      "enabled": true,
      "spaceId": 12345,
      "creator": { "userName": "zhangsan", "name": "张三" },
      "createTime": 1712000000000
    }
  ],
  "message": null
}
```

**关键字段说明**:
- `data[].id`: 规则 ID — 用于 `ai-pre-review start --rules 1,2,3`
- `data[].content`: 规则内容
- `data[].name`: 规则名称
- `data[].enabled`: 是否启用

---

### ai-pre-review start — 发起卡片预审

CLI 会自动从 iCafe 获取卡片标题和内容（HTML 转 Markdown），然后提交给 AI 进行预审。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |
| `--rules` | 否 | 评审规则 ID，逗号分隔（如 `--rules 1,2,3`）。CLI 自动从空间配置获取规则内容传给 AI。通过 `ai-pre-review rules` 查看可用规则及 ID |

```bash
icafe-cli ai-pre-review start --space myspace --sequence 1001

# 带评审规则 (规则 ID 从 ai-pre-review rules 获取)
icafe-cli ai-pre-review start --space myspace --sequence 1001 --rules 1,2,3
```

**返回示例** (成功):

```json
{
  "status": "OK",
  "message": "操作成功！",
  "data": {
    "conversationId": "abc123def456"
  }
}
```

**关键字段说明**:
- `data.conversationId`: 会话 ID，用于后续查询结果
- 发起成功后 CLI 会在 stderr 提示查询命令

**业务成功判断**: 检查 `status` 为 `"OK"` 且 `data.conversationId` 非空。

---

### ai-pre-review result — 查询预审结果

支持两种查询方式：通过 `--conversation-id` 直接查，或通过 `--space` + `--sequence` 按卡片查最新结果。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--conversation-id` | 二选一 | 发起预审时返回的 conversationId |
| `--space` | 二选一 | 空间前缀码（需配合 `--sequence`） |
| `--sequence` | 二选一 | 卡片序列号（需配合 `--space`） |
| `--mine` | 否 | 只返回当前用户发起的结果（默认返回所有用户的最新结果） |

```bash
# 通过 conversationId 查询
icafe-cli ai-pre-review result --conversation-id abc123def456

# 通过卡片查询
icafe-cli ai-pre-review result --space myspace --sequence 1001

# 只查自己的结果
icafe-cli ai-pre-review result --space myspace --sequence 1001 --mine
```

**返回示例** (已完成):

```json
{
  "status": "OK",
  "message": "操作成功！",
  "data": {
    "conversationId": "abc123def456",
    "status": "FINISHED",
    "content": "AI 预审结果内容...",
    "contentType": "TEXT",
    "messageId": "msg789",
    "time": "2026-04-07 10:30:00",
    "latestRunning": false,
    "user": "zhangsan"
  }
}
```

**返回示例** (还在执行中):

```json
{
  "status": "OK",
  "message": "操作成功！",
  "data": {
    "conversationId": "abc123def456",
    "status": "RUNNING",
    "latestRunning": true,
    "user": "zhangsan"
  }
}
```

**关键字段说明**:
- `data.status`: Agent 消息状态 — `RUNNING`=执行中，`FINISHED`=已完成，`FAIL`=失败，`TIMEOUT`=超时
- `data.content`: AI 回答内容（仅终态时有值）
- `data.latestRunning`: `true` 表示有最新一次任务还在执行中，当前返回的可能是上一次已完成的结果
- `data.user`: 发起该任务的用户名
- `--mine` 仅在通过 `--space` + `--sequence` 查询时生效；通过 `--conversation-id` 查询时服务端会校验会话归属（只有创建者可查）

**CLI 提示行为**: 通过 `--space` + `--sequence` 查询且未指定 `--mine` 时，如果返回的结果不是当前用户发起的，CLI 会在 stderr 输出提示。

---

## ai-codegen 命令组

卡片代码生成命令，使用 AI 根据卡片内容自动生成代码。**异步操作**：先发起，再查结果。

### ai-codegen start — 发起代码生成

CLI 会自动从 iCafe 获取卡片信息，并检测当前 git 仓库和分支。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--space` | **是** | 空间前缀码 |
| `--sequence` | **是** | 卡片序列号 |
| `--repo` | 否 | 代码仓库名（如 `baidu/myrepo`）。不传则从当前 git 目录的 `origin` remote 自动检测 |
| `--branch` | 否 | 目标分支。不传则从当前 git 目录自动检测当前分支 |

```bash
# 在 git 仓库目录下执行 (自动检测 repo 和 branch)
icafe-cli ai-codegen start --space myspace --sequence 1001

# 手动指定 repo 和 branch
icafe-cli ai-codegen start --space myspace --sequence 1001 --repo baidu/myrepo --branch master
```

**返回示例** (成功):

```json
{
  "status": "OK",
  "message": "操作成功！",
  "data": {
    "conversationId": "xyz789abc012"
  }
}
```

**关键字段说明**:
- `data.conversationId`: 会话 ID，用于后续查询结果
- `--repo` 不传时 CLI 通过 `git remote get-url origin` 自动检测，失败则报错退出
- `--branch` 不传时 CLI 通过 `git rev-parse --abbrev-ref HEAD` 自动检测，失败则不指定分支（不报错）
- 卡片标题为空时会报错退出（`missing_title`）
- 代码生成需要仓库 MEMBER 权限，无权限时服务端返回鉴权错误

---

### ai-codegen result — 查询代码生成结果

支持两种查询方式，参数和行为与 `ai-pre-review result` 一致。

| 参数 | 必需 | 说明 |
|------|------|------|
| `--conversation-id` | 二选一 | 发起代码生成时返回的 conversationId |
| `--space` | 二选一 | 空间前缀码（需配合 `--sequence`） |
| `--sequence` | 二选一 | 卡片序列号（需配合 `--space`） |
| `--mine` | 否 | 只返回当前用户发起的结果（默认返回所有用户的最新结果） |

```bash
# 通过 conversationId 查询
icafe-cli ai-codegen result --conversation-id xyz789abc012

# 通过卡片查询
icafe-cli ai-codegen result --space myspace --sequence 1001

# 只查自己的结果
icafe-cli ai-codegen result --space myspace --sequence 1001 --mine
```

返回结构与 `ai-pre-review result` 完全一致，参见上方返回示例和字段说明。

---

## cache 命令组

### cache clean — 清除本地缓存

```bash
icafe-cli cache clean
```

以下数据会被缓存 (TTL 20 分钟): `space latest`, `space tree`, `space issue-types`, `space type-fields`, `space type-statuses`, `plan list`。用 `--no-cache` 全局 flag 可跳过缓存。

---

## 字段类型与值格式速查

`space type-fields` 返回的字段中 `type` 表示字段类型，不同类型需要传不同格式的值:

| type | 含义 | 传值格式 |
|------|------|---------|
| `select_list` | 单选下拉 | 必须是 `valueItems` 中的值 (如 `P1-High`) |
| `select_list_multiple` | 多选下拉 | 逗号分隔多个值 |
| `radio_field` | 单选框 | 必须是 `valueItems` 中的值 |
| `check_box_field` | 复选框 | 逗号分隔多个值 |
| `user_picker` | 多选用户 | 逗号分隔的用户名 (如 `zhangsan,lisi`) |
| `user_picker_single` | 单选用户 | 单个用户名 |
| `number_field` | 数字 | 整数或小数 (如 `8`, `3.5`) |
| `date_time` | 日期 | `YYYY-MM-DD` |
| `datetime_field` | 日期时间 | `YYYY-MM-DD HH:mm:ss` |
| `free_text_field` | 单行文本 | 任意文本 |
| `text_area_field` | 多行文本 | 任意文本 |
| `url_field` | URL | URL 字符串 |
| `rich_text` | 富文本 | HTML 格式 |
| `plan_box` | 计划 | 计划完整路径 (如 `2026Q1/Sprint1`) |
| `tree_field` | 树 (多选) | 逗号分隔的节点值 |
| `multi_suggest_text_field` | 标签 | 逗号分隔的标签值 |

**核心规则**: 选择类字段的值**必须**是 `valueItems` 中列出的值，否则返回字段值错误。
