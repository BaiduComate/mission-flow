# 知识库文档管理 Skill - 目录结构说明

## 📁 目录结构

```
ku-doc-manage/
├── SKILL.md                    # 主入口文档 (精简版)
├── scripts/                    # Python客户端代码
│   ├── __init__.py
│   ├── ku_api_client.py
│   └── config.yaml
├── references/                 # API详细文档目录
    ├── API_INDEX.md           # API索引和使用说明
    ├── query_content.md       # 查询文档内容
    ├── query_repo.md          # 查询文档列表
    ├── create_doc.md          # 创建文档
    ├── copy_doc.md            # 复制文档
    ├── query_permission.md    # 查询权限
    ├── add_member.md          # 添加成员
    ├── update_member.md       # 更新成员
    ├── change_scope.md        # 修改公开范围
    ├── query_comments.md      # 查询评论
    ├── query_recent_view.md   # 查询浏览记录
    ├── query_flowchart.md     # 导出流程图
    └── query_user_info.md     # 查询用户信息
```

## 🎯 设计理念

### 渐进式加载
- **SKILL.md**: 提供功能概览、快速开始、配置说明
- **references/**: 存放13个API的详细文档,按需加载
- **Agent工作流程**:
  1. 初次加载只读取 SKILL.md
  2. 根据用户需求判断所需API
  3. 动态读取对应的API文档
  4. 参考文档中的参数和示例完成任务


## 📖 Agent使用指南

### 1. 初次触发
当用户提到知识库相关操作时,Agent读取 SKILL.md 了解:
- 有哪些功能分类(文档管理/权限管理/互动数据/高级功能)
- 每个分类下有哪些API
- 基本的使用方式和认证配置

### 2. 确定API
根据用户具体需求,判断需要使用哪个API:
- "查询这个文档的内容" → query_content
- "列出知识库的所有文档" → query_repo
- "创建一个文档" → create_doc
- "给文档添加成员" → add_member
- ...

### 3. 按需加载
读取 `references/` 目录下对应的API文档:
```python
# Agent内部逻辑示例
api_name = "query_content"  # 根据用户需求确定
doc_path = f"references/{api_name}.md"
# 读取该文档获取详细的参数说明和调用示例
```

### 4. 执行任务
参考文档中的示例代码,调用KuApiClient完成任务

## 🔍 快速查找

### 按功能查找
- **查询类**: query_content, query_repo, query_permission, query_comments, query_recent_view, query_flowchart, query_user_info
- **写入类**: create_doc, copy_doc
- **权限类**: query_permission, add_member, update_member, change_scope

### 按使用频率
**高频API** (建议优先了解):
1. query_content - 查询文档内容
2. query_repo - 列出文档列表
3. create_doc - 创建文档
4. query_user_info - 获取用户个人知识库ID

**中频API**:
- add_member - 添加文档成员
- query_permission - 查询权限
- copy_doc - 复制文档

**低频API**:
- query_comments, query_recent_view, query_flowchart 等

## 💡 维护建议

### 添加新API
1. 在 `references/` 下创建新的 `{api_name}.md`
2. 按现有格式编写文档(API信息/参数/示例/场景)
3. 更新 `references/API_INDEX.md` 添加索引
4. 更新 `SKILL.md` 的功能概览和方法速查表

### 更新现有API
直接修改 `references/` 下对应的文档即可,不影响主入口文件

### 文档规范
每个API文档应包含:
- API信息(接口地址、Python方法)
- 请求参数表格
- 响应示例
- Python调用示例(至少2-3个场景)
- 使用场景说明(可选)
