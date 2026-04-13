# 更新文档成员权限

更新文档已有成员的访问权限。

## API信息

- **接口**: `POST /ku/openapi/updateMember`
- **Python方法**: `client.update_member(doc_id, username, role_name)`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| docId | string | 是 | 文档ID |
| username | string | 是 | 待更新的用户名(邮箱前缀) |
| roleName | string | 是 | 新的角色名称:DocReader、DocMember、DocAdmin |

## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "docGuid": "1xosIYvQX3qxeI",
        "success": true,
        "memberResultList": [
            {
                "memberType": 5,
                "memberGuid": "zhangsan"
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
result = client.update_member(
    doc_id="WKoT7ltTnjU1oW",
    username="zhangsan",
    role_name="DocMember"
)
```
