# 查询文档评论

查询文档的底部评论和侧边评论。

## API信息

- **接口**: `POST /ku/openapi/queryComments`
- **Python方法**: `client.query_comments(doc_id, query_bottom_comment, query_side_comment, page_num, page_size)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| docId | string | 是 | - | 文档ID |
| queryBottomComment | boolean | 否 | true | 是否查询底部评论 |
| querySideComment | boolean | 否 | true | 是否查询侧边评论 |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |

## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "docGuid": "1xosIYvQX3qxeI",
        "bottomCommentResult": {
            "totalCount": 2,
            "rootCount": 1,
            "comments": [
                {
                    "commentType": 1,
                    "commentGuid": "5356d6774d",
                    "text": "这是一条底部评论示例",
                    "content": [
                        {
                            "type": "paragraph",
                            "children": [
                                {
                                    "text": "这是一条底部评论示例"
                                }
                            ],
                            "textAlign": "left",
                            "blockId": "docyg-377e18e0-e141-11f0-a9d1-2d329f98e194"
                        }
                    ],
                    "replyCommentGuid": "0000000000",
                    "rootCommentGuid": "0000000000",
                    "quote": null,
                    "status": 20,
                    "created": 1640966400000,
                    "commentUserInfo": {
                        "username": "zhangsan",
                        "nickname": "张三",
                        "email": "zhangsan@baidu.com"
                    },
                    "childrenComments": [
                        {
                            "commentType": 2,
                            "commentGuid": "d7818e9c77",
                            "text": "这是一条回复评论示例",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "children": [
                                        {
                                            "text": "这是一条回复评论示例"
                                        }
                                    ],
                                    "textAlign": "left",
                                    "blockId": "docyg-43b514b0-e141-11f0-a9d1-2d329f98e194",
                                    "textIndent": 0,
                                    "diffId": "7408clTA"
                                }
                            ],
                            "replyCommentGuid": "5356d6774d",
                            "rootCommentGuid": "5356d6774d",
                            "quote": null,
                            "status": 20,
                            "created": 1640970000000,
                            "commentUserInfo": {
                                "username": "lisi",
                                "nickname": "李四",
                                "email": "lisi@baidu.com"
                            },
                            "childrenComments": []
                        }
                    ]
                }
            ]
        },
        "sideCommentResult": {
            "totalCount": 0,
            "rootCount": 0,
            "comments": []
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
result = client.query_comments(
    doc_id="WKoT7ltTnjU1oW",
    query_bottom_comment=True,
    query_side_comment=True,
    page_num=1,
    page_size=10
)
```
