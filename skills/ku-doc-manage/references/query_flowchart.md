# 导出流程图数据

导出文档中指定流程图的原始数据(mxGraph格式的XML文本)。

## API信息

- **接口**: `POST /ku/openapi/queryFlowchart`
- **Python方法**: `client.query_flowchart(doc_guid, flowchart_id)`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| docGuid | string | 是 | 文档ID |
| flowchartId | string | 是 | 流程图ID |

## 响应示例

```json
{
  "returnCode": 200,
  "returnMessage": "SUCCESS",
  "result": {
    "docGuid": "doc_id",
    "flowchartId": "flowchart_id",
    "content": "<mxGraphModel>...</mxGraphModel>"
  }
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()
result = client.query_flowchart(
    doc_guid="WKoT7ltTnjU1oW",
    flowchart_id="flowchart_123"
)
```
