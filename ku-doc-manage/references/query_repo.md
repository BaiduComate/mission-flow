# 分页查询知识库文档列表

根据知识库ID分页查询文档列表,支持多种筛选条件和互动数据展示。

## API信息

- **接口**: `POST /ku/openapi/queryRepo`
- **Python方法**: `client.query_repo(repo_id, page_num, page_size, ...)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| repo_id | string | 是 | - | 知识库ID(repositoryGuid) |
| page_num | int | 否 | 1 | 页码 |
| page_size | int | 否 | 10 | 每页数量 |
| parent_doc_guid | string | 否 | null | 父文档ID("00000000000000"表示根目录) |
| doc_guids | array | 否 | null | 文档ID列表,限制查询范围 |
| urls | array | 否 | null | 文档URL列表,限制查询范围 |
| show_doc_creator_info | boolean | 否 | false | 是否展示文档作者信息 |
| show_doc_publisher_info | boolean | 否 | false | 是否展示文档最近更新者信息 |
| order_by | string | 否 | null | 排序字段(如"publishTime") |
| order_direction | string | 否 | "desc" | 排序方向(desc=倒序,asc=正序) |
| show_doc_views | boolean | 否 | false | 是否展示文档浏览数* |
| show_doc_likes | boolean | 否 | false | 是否展示文档获赞数* |
| show_doc_coins | boolean | 否 | false | 是否展示文档获币数* |
| show_doc_comments | boolean | 否 | false | 是否展示文档评论数* |

*注：互动数据需联系运营开通配置后才会返回

## 响应示例

```json
{
    "msg": "OK",
    "result": {
        "count": 622,
        "data": [
            {
                "childCount": 0,
                "created": 1640966400000,
                "creatorUserInfo": {
                    "email": "zhangsan@baidu.com",
                    "nickname": "张三",
                    "username": "zhangsan"
                },
                "docGuid": "1xosIYvQX3qxeI",
                "name": "示例文档标题",
                "publishTime": 1641052800000,
                "publisherUserInfo": {
                    "email": "lisi@baidu.com",
                    "nickname": "李四",
                    "username": "lisi"
                },
                "repositoryGuid": "E3d4LRExEl",
                "type": 1,
                "url": "https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/2tsPs8CtSd/E3d4LRExEl/1xosIYvQX3qxeI"
            }
        ],
        "total": 622
    },
    "returnCode": 200,
    "returnMessage": "OK",
    "status": 200,
    "success": true,
    "traceId": "123456789012345678"
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()

# 基础查询
result = client.query_repo(
    repo_id="E3d4LRExEl",
    page_num=1,
    page_size=10
)

# 按更新时间倒序排列
result = client.query_repo(
    repo_id="E3d4LRExEl",
    order_by="publishTime",
    order_direction="desc",
    page_size=20
)
```

## 使用场景

- 列出知识库的所有文档
- 按时间/作者等条件筛选文档
- 统计文档的互动数据
