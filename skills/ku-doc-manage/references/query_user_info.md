# 查询用户个人知识库信息

查询指定用户的个人知识库信息,包括个人知识库ID等。当需要创建文档但不知道目标知识库ID时,可以使用此API获取用户的个人知识库ID。

## API信息

- **接口**: `POST /ku/openapi/queryUserInfo`
- **Python方法**: `client.query_user_info(username)`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名(邮箱前缀) |

## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "userGuid": "userGuid",
        "username": "zhangsan",
        "nickname": "张三",
        "email": "<EMAIL>",
        "userPersonalRepo": {
            "spaceGuid": "HFVrC7hq1Q",
            "groupGuid": "pKzJfZczuc",
            "repositoryGuid": "repositoryGuid",
            "name": "张三的知识库",
            "url": "https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/repositoryGuid",
            "ownerType": 5
        }
    }
}
```

## 返回字段说明

- `username`: 用户名
- `nickname`: 用户昵称
- `repositoryGuid`: **用户个人知识库ID** - 可用于创建文档到用户个人空间
- `userGuid`: 用户唯一标识

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()

# 查询用户个人信息
result = client.query_user_info(username="zhangsan")

if result.get('returnCode') == 200:
    user_info = result['result']['userPersonalRepo']
    personal_repo_id = user_info['repositoryGuid']
    print(f"用户 {user_info['name']} 的个人知识库ID: {personal_repo_id}")

    # 使用获取到的个人知识库ID创建文档
    doc_result = client.create_doc(
        repository_guid=personal_repo_id,
        creator_username="zhangsan",
        title="我的笔记",
        content="这是一篇笔记内容"
    )
```

## 应用场景

- 创建文档到用户个人知识库时,先调用此API获取用户的`repositoryGuid`
- 未指定知识库但依赖知识库ID数据时,先调用此API获取用户的`repositoryGuid`
- 批量为多个用户创建文档时,循环获取每个用户的个人知识库ID
- 查询用户的知识库基本信息
