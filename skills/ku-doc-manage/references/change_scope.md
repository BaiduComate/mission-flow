# 修改文档公开范围

修改文档的公开范围设置。

## API信息

- **接口**: `POST /ku/openapi/changeScope`
- **Python方法**: `client.change_scope(doc_id, scope, operator_username)`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| docId | string | 是 | 文档ID |
| scope | int | 是 | 权限范围:5-公开可读,6-公开可编辑,20-私密 |
| operatorUsername | string | 否 | 操作者用户名,不传则使用ak对应的用户名 |

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
result = client.change_scope(
    doc_id="WKoT7ltTnjU1oW",
    scope=5,  # 5-公开可读
    operator_username="zhangsan"
)
```
