# 查询文档正文内容

根据文档ID或URL查询知识库文档的完整正文内容。

## API信息

- **接口**: `POST /ku/openapi/queryContent`
- **Python方法**: `client.query_content(doc_id, url, show_doc_info)`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| docId | string | 否* | 文档ID,知识库文档链接中以/分割后的最后一个字符串 |
| url | string | 否* | 文档完整URL链接 |
| show_doc_info | boolean | 否 | 是否返回文档元信息(标题、创建时间等) |

*注：docId和url至少提供一个

## 响应示例

```json
{
    "msg": "OK",
    "result": {
        "content": [
            {
                "blockId": "docyg-cd25d2a0-1bb3-11f1-a2f8-6fa8bbe5641c",
                "children": [
                    {
                        "children": null,
                        "diffId": null,
                        "text": "示例文档标题",
                        "type": null
                    }
                ],
                "cover": {
                    "clip": {
                        "height": 523,
                        "width": 2880,
                        "x": 0,
                        "y": 221.9572676326334
                    },
                    "coverId": "classic",
                    "height": 1192,
                    "themeColor": "gray",
                    "url": "https://ops-wps.cdn.bcebos.com/morpho-static/slide/classic/classic.jpg",
                    "width": 2880
                },
                "diffId": "SayHappy",
                "html": null,
                "markdown": {
                    "appendJSONContent": [],
                    "content": "",
                    "imageNeedUpload": false,
                    "imageSizes": [],
                    "inserted": false
                },
                "showDocCover": true,
                "showSlideCover": false,
                "slide": false,
                "theme": "light",
                "type": "title"
            },
            {
                "authors": {
                    "wzXq-DUqOL": {
                        "contribute": 4,
                        "time": 1773129094027
                    }
                },
                "blockId": "docyg-cd25d2a1-1bb3-11f1-a2f8-6fa8bbe5641c",
                "children": [
                    {
                        "text": "示例段落内容"
                    }
                ],
                "diffId": "5XgYSsnA",
                "type": "paragraph"
            }
        ],
        "docGuid": "1xosIYvQX3qxeI"
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

# 方式1: 使用文档ID
result = client.query_content(doc_id="WKoT7ltTnjU1oW")

# 方式2: 使用完整URL
result = client.query_content(url="https://ku.baidu-int.com/knowledge/xxx/xxx/xxx/WKoT7ltTnjU1oW")

# 方式3: 同时获取文档元信息
result = client.query_content(doc_id="WKoT7ltTnjU1oW", show_doc_info=True)
```

## 使用场景

- 获取文档的完整正文内容用于分析或处理
- 根据用户提供的URL快速查询文档内容
- 批量获取多个文档的内容
