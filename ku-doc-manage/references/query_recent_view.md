# 查询文档浏览记录

查询文档在指定时间范围内的浏览人身份和浏览时间信息。

## API信息

- **接口**: `POST /ku/openapi/queryRecentView`
- **Python方法**: `client.query_recent_view(doc_id, begin_time, end_time, page_num, page_size)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| docId | string | 是 | - | 文档ID |
| beginTime | long | 否 | 当天起始时间 | 记录起始时间(毫秒级时间戳) |
| endTime | long | 否 | 当前时间 | 记录结束时间(毫秒级时间戳) |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |

## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "repositoryGuid": "E3d4LRExEl",
        "docGuid": "1xosIYvQX3qxeI",
        "totalViewers": 1,
        "count": 1,
        "data": [
            {
                "username": "zhangsan",
                "nickname": "张三",
                "email": "zhangsan@baidu.com",
                "viewTime": 1640966400000
            }
        ]
    },
    "traceId": "123456789012345678"
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()
# 查询今天的浏览记录
result = client.query_recent_view(
    doc_id="WKoT7ltTnjU1oW",
    page_num=1,
    page_size=20
)
```
