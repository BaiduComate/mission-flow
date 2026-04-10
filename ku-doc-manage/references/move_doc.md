# 移动文档

将文档移动到指定知识库或目录。

## API信息

- **接口**: `POST /ku/openapi/moveDoc`
- **Python方法**: `client.move_doc(doc_id, to_repo_guid, operator_username, to_parent_guid, to_adjacent_doc_guid, upper)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| docId | string | 是 | - | 待移动的源文档ID |
| toRepoGuid | string | 是 | - | 目标知识库ID |
| operatorUsername | string | 否 | ak对应用户 | 操作者用户名 |
| toParentGuid | string | 否 | 根目录 | 目标父目录ID |
| toAdjacentDocGuid | string | 否 | null | 目标相邻文档ID |
| upper | boolean | 否 | false | 是否移动到目标上方 |

## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "success": true,
        "docInfo": {
            "repositoryGuid": "E3d4LRExEl",
            "docGuid": "1xosIYvQX3qxeI",
            "name": "示例文档",
            "url": "https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/E3d4LRExEl/1xosIYvQX3qxeI",
            "type": 1,
            "childCount": 0,
            "created": 1640966400000,
            "publishTime": 1641052800000
        }
    },
    "traceId": "123456789012345678",
    "status": 200,
    "msg": "OK",
    "success": true
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()
result = client.move_doc(
    doc_id="WKoT7ltTnjU1oW",
    to_repo_guid="E3d4LRExEl",
    operator_username="zhangsan",
    to_parent_guid="parent_doc_id"
)
```
