---
name: ku-doc-manage
description: 百度知识库(ku.baidu-int.com)文档管理。触发词:知识库URL/文档/知识库/库/ku文档/创建文档/查询文档/复制文档/移动文档/编辑文档/文档权限/文档列表/文档评论/文档内容/浏览记录/流程图导出。
---

# 知识库文档管理 Skill

百度知识库文档操作技能集，基于知识库OpenAPI官方文档开发。

**核心特性**:
- ✅ 提供14个核心API，覆盖文档管理、权限控制、互动数据等场景
- ✅ 支持两种认证方式自动降级（个人身份认证 → 数字员工身份认证）
- ✅ 个人身份认证完全委托 get-ugate-token SKILL，每次请求都调用 SKILL 获取 token

## 术语说明

### 用户名 (username/creator_username/editor_username)

在API中涉及的 `username`、`creator_username`、`operator_username` 、`editor_username`等涉及username参数,**默认指当前用户的邮箱前缀或用户名**。

**获取当前用户名的方法**（按优先级）:
1. **环境变量** - 优先从以下环境变量获取：
   - `SANDBOX_USERNAME` - 沙箱用户名（如果已设置）
   - `BAIDU_CC_USERNAME` - 百度账号用户名（推荐）
   - 示例代码:
     ```python
     import os
     username = os.environ.get('SANDBOX_USERNAME') or os.environ.get('BAIDU_CC_USERNAME')
     ```
     ```bash
     username=${SANDBOX_USERNAME:-$BAIDU_CC_USERNAME}
     ```
2. **Git配置** - 如果环境变量不可用，从本地 git 配置获取：
   ```bash
   git config user.email  # 取邮箱前缀
   git config user.name   # 或直接使用用户名
   ```
3. **用户明确指定** - 如果用户明确提供了username值，应优先使用用户提供的值

**用户名格式说明**:
- 邮箱前缀示例: `zhangsan@baidu.com` → 用户名为 `zhangsan`
- 适用于所有需要用户身份标识的API操作(创建文档、复制文档、修改权限等)

### 文档ID (doc_id) 和知识库ID (repo_id/repository_guid)

知识库URL中包含了文档ID和知识库ID信息,可以通过URL路径来识别:

**知识库URL格式**: `https://ku.baidu-int.com/knowledge/{path1}/{path2}/{path3}/{path4}`
  - **文档ID**: 最后一个斜杆后的字符串 (path4) → `AseK3nnVbJTu1J`
  - **知识库ID**: 倒数第二个斜杆后的字符串 (path3) → `E3d4LRExEl`

- **包含3个path值的URL** (知识库首页):
  - **知识库ID**: 最后一个斜杆后的字符串 (path3) → `E3d4LRExEl`

**提取示例**:

| URL类型 | 示例URL | 文档ID | 知识库ID |
|---------|---------|--------|----------|
| 文档页面 | `https://ku.baidu-int.com/knowledge/A/B/C/D` | `D` | `C` |
| 知识库首页 | `https://ku.baidu-int.com/knowledge/A/B/C/` | - | `C` |

**在API中的使用**:
- `doc_id` / `docId` / `doc_guid` - 都指文档ID
- `repo_id` / `repository_guid` - 都指知识库ID

## 功能概览

本技能集提供13个核心API,按功能分类:

### 📄 文档管理类 (6个)
- **query_content** - 查询文档正文内容
- **query_repo** - 分页查询知识库文档列表
- **create_doc** - 创建文档(支持3种模式，可直接传入md文件路径)
- **edit_content** - 编辑文档正文(追加/覆盖)
- **copy_doc** - 复制文档
- **upload_attachment** - 上传文档附件

### 👥 权限管理类 (4个)
- **query_permission** - 查询用户对文档的权限
- **add_member** - 为文档添加成员
- **update_member** - 更新文档成员权限
- **change_scope** - 修改文档公开范围

### 💬 互动数据类 (2个)
- **query_comments** - 查询文档评论
- **query_recent_view** - 查询文档浏览记录

### 🎨 高级功能类 (2个)
- **query_flowchart** - 导出流程图数据
- **query_user_info** - 查询用户个人信息(含个人知识库ID)

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 基本使用

```python
# 导入客户端
from scripts import KuApiClient

# 方式1: 自动认证（推荐）- 依次尝试两种认证方式
client = KuApiClient()

# 方式2: 指定认证方式
client = KuApiClient(auth_mode="xiaolongxia")  # 仅使用个人身份认证
client = KuApiClient(auth_mode="digital")      # 仅使用数字员工认证

# 查询文档内容
result = client.query_content(doc_id="WKoT7ltTnjU1oW")

# 查询知识库文档列表
result = client.query_repo(repo_id="E3d4LRExEl", page_num=1, page_size=10)

# 创建文档到个人知识库
result = client.create_doc(
    creator_username="zhangsan",
    title="我的笔记",
    content="笔记内容"
)

# 从 Markdown 文件直接创建文档
result = client.create_doc(
    creator_username="zhangsan",
    md_file_path="./notes/README.md"
)
```

## API详细文档

每个API的详细文档(参数说明、调用示例、应用场景)已拆分到独立文件中。

**Agent使用说明**:
1. 根据用户需求判断需要哪个API
2. 读取 `references/` 目录下对应的markdown文档
3. 参考文档中的参数说明和示例代码完成任务

**文档索引**: 查看 [references/API_INDEX.md](./references/API_INDEX.md) 获取完整API列表和使用说明。

## 认证配置

### 两种认证方式（自动降级）

本技能支持两种认证方式，按以下优先级自动降级：

#### 1. 个人身份认证（第一优先级，默认推荐）⭐

- **API基础URL**: `https://apigo.baidu-int.com`
- **双token认证机制**:
- **优势**:
  - 本地文件读取速度快，无需每次调用 SKILL
  - 认证失败自动重试，提高成功率
  - 支持多用户，自动识别当前用户身份
- **适用场景**: OpenClaw 场景个人使用，需要以个人身份操作文档

#### 2. 数字员工身份认证（第二优先级，兜底方案）

- **配置文件**: `scripts/config.yaml`
  ```yaml
  digital_auth:
    ak: "your_access_key"
    sk: "your_secret_key"
  ```
- **特点**:
  - 当个人身份认证失败时自动切换
  - 适用于自动化脚本、CI/CD等场景
- **手动指定**: `client = KuApiClient(auth_mode="digital")`

### 认证流程说明

**自动降级流程** (默认 `auth_mode="auto"`):

```
1. 尝试个人身份认证（本地文件）
   ↓ 失败
2. 尝试个人身份认证（强制刷新 token）
   ↓ 失败
3. 尝试数字员工认证
   ↓ 失败
4. 抛出异常，提示配置帮助信息
```

**降级触发条件**:
- HTTP状态码: 401, 403
- 响应码: 401, 403, 60413
- **个人身份认证特殊处理**: 响应码 500 代表 token 过期，会触发 token 刷新
- Token为空或获取失败

**个人身份认证重试机制**:
- 当响应码为 500 时，判定为 token 过期，自动调用 `get-ugate-token` SKILL 刷新 token 并重试
- 首次请求失败时（其他错误码），也会自动调用 `get-ugate-token` SKILL 刷新 token 并重试
- 只有在刷新后仍然失败时，才会降级到数字员工认证方式

**用户引导信息**:
当所有认证方式都失败时，系统会打印详细的配置帮助信息，引导用户完成配置。

### 认证模式选择

```python
# 自动降级模式（推荐，默认）
client = KuApiClient()  # 或 KuApiClient(auth_mode="auto")

# 仅使用个人身份认证
client = KuApiClient(auth_mode="xiaolongxia")

# 仅使用数字员工认证
client = KuApiClient(auth_mode="digital")
```

### 配置文件位置

`scripts/config.yaml`:
```yaml
# 个人身份认证配置
xiaolongxia_auth:
  enabled: true  # 是否启用个人身份认证

# 数字员工认证配置
digital_auth:
  ak: "your_access_key"
  sk: "your_secret_key"
```

**注意**：
- `x-ku-open-ugate-token` 优先从本地文件 `~/.config/uuap/.eac_ugate_token_{username}` 读取
- 用户名从环境变量 `SANDBOX_USERNAME` 或 `BAIDU_CC_USERNAME` 获取
- 认证失败时自动调用 `get-ugate-token` SKILL 刷新 token

**环境变量要求**：
- 必须设置 `SANDBOX_USERNAME` 或 `BAIDU_CC_USERNAME` 环境变量
- 这些环境变量用于确定当前用户身份和 token 文件路径

## 客户端方法速查

| 方法 | 说明 | 详细文档 |
|------|------|---------|
| `query_content(doc_id, url, show_doc_info)` | 查询文档内容 | [query_content.md](./references/query_content.md) |
| `query_repo(repo_id, page_num, page_size, ...)` | 查询文档列表 | [query_repo.md](./references/query_repo.md) |
| `create_doc(repository_guid, title, content, ...)` | 创建文档 | [create_doc.md](./references/create_doc.md) |
| `editor_ku_page(doc_guid, editor_username, operations, publish)` | 编辑文档正文 | [edit_content.md](./references/edit_content.md) |
| `copy_doc(doc_id, operator_username, ...)` | 复制文档 | [copy_doc.md](./references/copy_doc.md) |
| `query_permission(doc_id, usernames)` | 查询权限 | [query_permission.md](./references/query_permission.md) |
| `add_member(doc_id, usernames, role_name)` | 添加成员 | [add_member.md](./references/add_member.md) |
| `update_member(doc_id, username, role_name)` | 更新成员 | [update_member.md](./references/update_member.md) |
| `change_scope(doc_id, scope, operator_username)` | 修改公开范围 | [change_scope.md](./references/change_scope.md) |
| `query_comments(doc_id, page_num, page_size, ...)` | 查询评论 | [query_comments.md](./references/query_comments.md) |
| `query_recent_view(doc_id, begin_time, end_time, ...)` | 查询浏览记录 | [query_recent_view.md](./references/query_recent_view.md) |
| `query_flowchart(doc_guid, flowchart_id)` | 导出流程图 | [query_flowchart.md](./references/query_flowchart.md) |
| `query_user_info(username)` | 查询用户信息 | [query_user_info.md](./references/query_user_info.md) |
| `upload_attachment(doc_guid, file_content, file_name)` | 上传文档附件 | [upload_attachment.md](./references/upload_attachment.md) |

## Markdown 图片自动上传

`create_doc` 方法支持自动处理 Markdown 中的图片：

```python
client.create_doc(
    repository_guid="xxx",
    title="文档标题",
    content=markdown_content,
    base_dir="/path/to/md/dir"  # 可选，默认使用当前工作目录
)

# 直接从文件创建，base_dir 会自动设为文件所在目录
client.create_doc(
    creator_username="zhangsan",
    md_file_path="/path/to/document.md"
)
```

**处理规则**（代码自动执行，无需手动处理）：
- 内部域名 (`rte.weiyun.baidu.com`) → 保留原链接
- 本地路径图片 → 自动上传并替换 URL
- 外部 URL 图片 → 下载后上传并替换 URL

处理后的图片 URL 会自动替换到返回的 `result.processedContent` 中。

## 常见错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未授权(Token无效或过期) |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 60413 | 无权限访问用户 |

## 权限角色说明

| 角色名称 | canRead | canUpdate | 说明 |
|----------|---------|-----------|------|
| DocReader | ✓ | ✗ | 只读成员,可查看文档 |
| DocMember | ✓ | ✓ | 可编辑成员,可查看、编辑文档 |
| DocAdmin | ✓ | ✓ | 页面管理员,可查看、编辑、管理文档和成员 |
