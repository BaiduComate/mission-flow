# AI 卡片预审与代码生成工作流

本文档包含使用 AI 预审卡片内容和根据卡片自动生成代码的完整交互流程。

---

## 场景1: AI 卡片预审

使用 AI 对卡片内容进行质量检查。异步操作：先发起，等待处理，再查结果。

### 确定目标卡片

按以下优先级确定要预审的卡片：

**用户明确指定了卡片** (如 "预审一下 cloud-iCafe-22229")
→ 直接解析 space 和 sequence，跳到"发起预审"

**用户指定了空间但没指定卡片** (如 "预审 cloud-iCafe 的卡片")
→ 查询该空间用户的活跃卡片，列出候选：
```bash
icafe-cli card query --space cloud-iCafe \
  --iql "负责人 = currentUser AND 流程状态 != 已关闭" --brief
```

**用户什么都没指定** (如 "帮我预审卡片")
→ 用 smart-find 获取用户的活跃卡片和空间：
```bash
icafe-cli card smart-find
```
从结果中列出候选卡片（优先显示未关闭的、最近修改的），让用户选择。

### 检查评审规则（可选）

确定卡片后，检查该空间是否配置了预审规则：
```bash
icafe-cli ai-pre-review rules --space <space>
```

- 如果 `data` 为空数组 → 该空间没有配置规则，跳过，不传 `--rules`
- 如果有规则 → 默认全部带上（规则是空间管理员配置的评审标准），或列出让用户选择
- 注意：不传规则时 AI 使用默认评审维度，也能正常工作

### 发起预审

```bash
# 不带规则
icafe-cli ai-pre-review start --space <space> --sequence <sequence>

# 带规则 (规则 ID 从 ai-pre-review rules 获取)
icafe-cli ai-pre-review start --space <space> --sequence <sequence> --rules 65,84
```

成功返回：
```json
{
  "status": "OK",
  "data": { "conversationId": "abc123..." }
}
```

验证：检查 `status` 为 `"OK"` 且 `data.conversationId` 非空。

### 查询预审结果

发起后 AI 需要处理时间（通常 20 秒 ~ 1 分钟），**等待 20-40 秒后再查询**：

```bash
# 通过空间+序列号查 (推荐，issueId 有缓存不会额外调接口)
icafe-cli ai-pre-review result --space <space> --sequence <sequence>

# 或通过 conversationId 查
icafe-cli ai-pre-review result --conversation-id <conversationId>
```

**状态处理**：
| `data.status` | 含义 | 处理 |
|---------------|------|------|
| `RUNNING` | AI 正在处理中 | 等待 20-40 秒后重试，**最多重试 3 次** |
| `FINISHED` | 处理完成 | 提取 `data.content` 展示给用户 |
| `FAIL` | 处理失败 | 告知用户失败，建议重新发起 |
| `TIMEOUT` | 处理超时 | 告知用户超时，建议重新发起 |

> **重试 3 次仍为 RUNNING**: 告知用户"预审仍在处理中，请稍后手动查询"，并给出查询命令让用户自行检查。

**结果解析**：`data.content` 是 JSON 字符串，需要二次解析：
```json
{
  "content": "{\"elements\":[{\"type\":\"text\",\"content\":\"评审意见...\"}]}"
}
```
提取 `elements[].content` 中 `type=text` 的文本展示给用户。

### 多用户提示

如果返回的 `data.user` 不是当前用户，说明这是其他人发起的预审结果。CLI 会在 stderr 提示。如需只查自己的结果：
```bash
icafe-cli ai-pre-review result --space <space> --sequence <sequence> --mine
```

### 决策流程图

```
用户要求预审卡片
  │
  ├─ 确定目标卡片
  │   ├─ 用户指定了 space+sequence？ → 直接用
  │   ├─ 指定了 space？ → card query 查用户活跃卡片 → 选择
  │   └─ 都没指定？ → card smart-find → 选择
  │
  ├─ 检查评审规则 (可选)
  │   ├─ ai-pre-review rules 查规则
  │   ├─ 有规则 → 默认全带上，或让用户选
  │   └─ 无规则 → 不传 --rules
  │
  ├─ 发起预审
  │   └─ ai-pre-review start --space --sequence [--rules]
  │       └─ 检查 status="OK" + conversationId 非空
  │
  └─ 查询结果 (等待 20-40s 后)
      └─ ai-pre-review result --space --sequence
          ├─ RUNNING → 等 20-40s 重试 (最多 3 次)
          │   └─ 3 次后仍 RUNNING → 提示用户稍后手动查询
          ├─ FINISHED → 解析 content 展示给用户
          └─ FAIL/TIMEOUT → 告知用户，建议重试
```

---

## 场景2: AI 卡片代码生成

根据卡片内容让 AI 自动生成代码。需要指定代码仓库，AI 会分析卡片需求并生成对应代码。

### 确定目标卡片

与预审流程相同 — 用户明确指定、查询选择、或 smart-find。

### 确定代码仓库

**在 git 仓库目录下执行** → CLI 自动检测 repo 和 branch：
- `--repo`: 从 `git remote get-url origin` 解析仓库路径（如 `baidu/icafe/luigi-service`）
- `--branch`: 从 `git rev-parse --abbrev-ref HEAD` 获取当前分支

**不在 git 目录下** → 必须手动指定 `--repo`：
```bash
icafe-cli ai-codegen start --space <space> --sequence <sequence> --repo baidu/myrepo
```

如果 `--repo` 不传且自动检测失败，CLI 会报错并提示手动指定。
`--branch` 不传时不报错，服务端会使用默认分支。

### 发起代码生成

```bash
# 在 git 仓库目录下 (自动检测 repo 和 branch)
icafe-cli ai-codegen start --space <space> --sequence <sequence>

# 手动指定 repo 和 branch
icafe-cli ai-codegen start --space <space> --sequence <sequence> \
  --repo baidu/myrepo --branch master
```

成功返回与预审相同：`status="OK"` + `data.conversationId`。

### 查询代码生成结果

代码生成时间通常比预审长（1 ~ 几分钟），**等待 30-50 秒后再查询**：

```bash
icafe-cli ai-codegen result --space <space> --sequence <sequence>
```

状态处理与预审一致（RUNNING/FINISHED/FAIL/TIMEOUT）。
RUNNING 时每次等待 30-50 秒，**最多重试 4 次**。

> **重试 4 次仍为 RUNNING**: 告知用户"代码生成仍在处理中，请稍后手动查询"，并给出查询命令让用户自行检查。

### 结果解析

`data.content` 包含 AI 生成的分析和代码，结构与预审类似（JSON 字符串中的 elements 数组）。
内容通常包含：
- 需求分析和技术方案
- 涉及的文件和改动说明
- 生成的代码（可能已自动提交到仓库的 CR）
- 如果 CR 推送失败，会说明原因（如仓库不存在、无权限等）

### 决策流程图

```
用户要求根据卡片生成代码
  │
  ├─ 确定目标卡片 (同预审流程)
  │
  ├─ 确定代码仓库
  │   ├─ 在 git 目录下？ → 自动检测 repo + branch
  │   └─ 不在？ → 必须手动 --repo，或询问用户
  │
  ├─ 发起代码生成
  │   └─ ai-codegen start --space --sequence [--repo --branch]
  │       └─ 检查 status="OK" + conversationId 非空
  │
  └─ 查询结果 (等待 30-50s 后)
      └─ ai-codegen result --space --sequence
          ├─ RUNNING → 等 30-50s 重试 (最多 4 次)
          │   └─ 4 次后仍 RUNNING → 提示用户稍后手动查询
          ├─ FINISHED → 解析 content 展示给用户
          └─ FAIL/TIMEOUT → 告知用户，建议重试
```

---

## 通用注意事项

### 成功判断

预审和代码生成的 start/result 接口都使用 macross BaseResponse 格式：
- 成功标识：`status` 字段值为字符串 `"OK"`（不是数字 200）
- 数据在 `data` 字段中
- 与 iCafe 卡片接口的 `code: 200` 判断方式不同

### issueId 缓存

`ai-pre-review start` 和 `ai-codegen start` 内部会调 `card get` 获取卡片信息，同时缓存 issueId 映射（1 天）。后续 `result` 查询通过 `--space --sequence` 时会优先读缓存，不再重复调 `card get`。

所以典型流程 `start → result` 中，只有 start 调一次 `card get`，result 直接用缓存。

### 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| start 返回 `status` 非 `"OK"` | 参数错误、卡片内容为空等 | 检查 message 字段的错误信息 |
| result 返回 HTTP 错误 | conversationId 不存在、服务异常 | 提示用户重新发起 |
| FAIL/TIMEOUT | AI 处理失败或超时 | 建议用户重新发起，可能是卡片内容不够详细 |
| 代码生成 CR 推送失败 | 仓库不存在、无 MEMBER 权限 | 检查 --repo 是否正确，确认用户有仓库权限 |
