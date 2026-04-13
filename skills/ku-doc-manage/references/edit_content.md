# 编辑文档正文

通过编辑操作列表对文档内容进行增删改操作，支持追加、覆盖两种操作模式。

## API信息

- **接口**: `POST /ku/openapi/editContent`
- **Python方法**: `client.editor_ku_page(doc_guid, editor_username, operations, publish)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| doc_guid | string | 是 | - | 文档ID |
| editor_username | string | 是 | - | 编辑者用户名（UUAP格式，即邮箱前缀，一般是当前用户名） |
| operations | list | 是 | - | 编辑操作列表（见下方说明） |
| publish | boolean | 否 | True | 是否编辑后同步发布 |

## operations 操作列表说明

每个操作是一个字典，包含以下字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| mode | string | 否 | `append` | 操作模式：`append`/`cover` |
| json | list | 是 | - | 编辑器 JSON 元素数组 |
| withNewCard | boolean | 是 | true | 是否使用新版卡片格式 |

### 操作模式说明

| mode | 说明 |
|------|------|
| `append` | 追加内容到文档末尾 |
| `cover` | 覆盖全文（完全替换文档所有内容） |

## json 元素格式说明

`json` 字段为编辑器节点数组，常用节点类型：

### 段落 (paragraph)
```json
{
    "type": "paragraph",
    "content": [
        {"type": "text", "text": "这是一段普通文字"}
    ]
}
```

### 标题 (heading)
```json
{
    "type": "heading",
    "level": 1,
    "children": [
        {"text": "分级标题一"}
    ]
}
```

### 有序列表 (orderedList)
```json
{
    "type": "ordered-list-item",
    "depth": 0,
    "index": 1,
    "children": [
        {"text": "11111"}
    ]
},
{
    "type": "ordered-list-item",
    "depth": 0,
    "index": 2,
    "children": [
        {"text": "222222"}
    ]
}
```

### 代码块 (codeBlock)
```json
{
    "type": "block-code",
    "language": "plain",
    "children": [
        {
            "type": "block-code-line",
            "children": [
                {"text": "这是是代码块"}
            ],
            "textIndent": 0,
            "textAlign": "left"
        }
    ]
}
```


## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "docGuid": "WSuIrx09hfg6zr",
        "success": true,
        "operations": [
            {
                "success": true
            }
        ]
    },
    "traceId": "694507417572758528",
    "status": 200,
    "msg": "OK",
    "success": true
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()

# 示例1: 追加一段文字到文档末尾（最简单用法）
result = client.editor_ku_page(
    doc_guid="WKoT7ltTnjU1oW",
    editor_username="zhangsan",
    operations=[{
        "mode": "append",
        "withNewCard": True,
        "json": [{"type": "paragraph", "children": [{"text": "追加的新内容"}]}]
    }]
)

# 示例2: 覆盖全文
result = client.editor_ku_page(
    doc_guid="WKoT7ltTnjU1oW",
    editor_username="zhangsan",
    operations=[{
        "mode": "cover",
        "withNewCard": True,
        "json": [
            {
                "type": "heading",
                "level": 1,
                "children": [{"text": "新标题"}]
            },
            {
                "type": "paragraph",
                "children": [{"text": "新文档内容，完全替换原内容"}]
            }
        ]
    }]
)

# 示例3: 批量操作（先追加标题，再追加内容）
result = client.editor_ku_page(
    doc_guid="WKoT7ltTnjU1oW",
    editor_username="zhangsan",
    operations=[
        {
            "mode": "append",
            "withNewCard": True,
            "json": [{
                "type": "heading",
                "level": 2,
                "children": [{"text": "新章节"}]
            }]
        },
        {
            "mode": "append",
            "withNewCard": True,
            "json": [{
                "type": "paragraph",
                "children": [{"text": "章节内容"}]
            }]
        }
    ]
)

if result.get('returnCode') == 200:
    print(f"✅ 文档编辑成功: {result['result'].get('docGuid')}")
else:
    print(f"❌ 编辑失败: {result.get('returnMessage')}")
```

## 使用场景

- 向现有文档追加新内容（如日志、记录）
- 完全更新文档内容（如文档同步）
- 批量编辑文档结构

## 注意事项

- `editor_username` 必须是有权限编辑该文档的用户
- `cover` 模式会清空文档所有内容后重写，操作不可逆，请谨慎使用
- 默认 `publish=True`，编辑完成后会自动发布；若需要草稿状态，设为 `False`
