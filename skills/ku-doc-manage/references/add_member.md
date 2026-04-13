# 添加文档成员

为文档添加成员并设置访问权限。

## API信息

- **接口**: `POST /ku/openapi/addMember`
- **Python方法**: `client.add_member(doc_id, usernames, role_name)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| docId | string | 是 | - | 文档ID |
| usernames | array | 是 | - | 用户名列表(邮箱前缀) |
| roleName | string | 否 | DocReader | 角色名称:DocReader(可读)、DocMember(可编辑)、DocAdmin(管理员) |

## 响应示例

```json
{
  "returnCode": 200,
  "returnMessage": "SUCCESS",
  "result": {}
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()
result = client.add_member(
    doc_id="WKoT7ltTnjU1oW",
    usernames=["zhangsan", "lisi"],
    role_name="DocReader"
)
```
