# 上传文档附件

上传附件到指定的知识库文档，支持各种文件类型。

## API信息

- **接口**: `POST /ku/openapi/uploadAttachment`
- **Python方法**: `client.upload_attachment(doc_guid, file)`
- **Content-Type**: `multipart/form-data`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| docGuid | string | 是 | 文档ID |
| file | string | 是 | 文件路径字符串，如 `"/path/to/file.pdf"` |

**file 参数说明**：
- **仅支持文件路径字符串**：传入文件的完整路径，函数会自动读取文件并提取文件名
- ❌ **不支持**：文件对象（open()返回）、字节流（bytes）等其他类型

## 响应示例

```json
{
  "returnCode": 200,
  "returnMessage": "OK",
  "result": {
    "docGuid": "rTgOMg1EhXhrC3",
    "attachId": "f49c39d17cc24d34ae3fef0ebf295fe3",
    "name": "4f0aa189-b877-42a9-bbdf-ced163b6e954.xlsx",
    "extension": "xlsx",
    "size": 3764
  },
  "traceId": "1967920467357294592",
  "status": 200,
  "msg": "OK",
  "success": true
}
```

**响应字段说明**：
- `returnCode`: 返回码，200表示成功
- `returnMessage`: 返回消息
- `result`: 上传结果对象
  - `docGuid`: 文档ID
  - `attachId`: 附件ID
  - `name`: 文件名
  - `extension`: 文件扩展名
  - `size`: 文件大小（字节）

## Python调用示例

### 示例1: 上传本地文件

```python
from scripts import KuApiClient

client = KuApiClient()

# 直接传入文件路径，函数会自动读取文件并提取文件名
result = client.upload_attachment(
    doc_guid="WKoT7ltTnjU1oW",
    file="/path/to/file.pdf"
)

if result.get("returnCode") == 200:
    attach_info = result.get("result", {})
    print(f"附件上传成功！")
    print(f"文档ID: {attach_info.get('docGuid')}")
    print(f"附件ID: {attach_info.get('attachId')}")
    print(f"文件名: {attach_info.get('name')}")
    print(f"文件扩展名: {attach_info.get('extension')}")
    print(f"文件大小: {attach_info.get('size')} 字节")
else:
    print(f"上传失败: {result.get('returnMessage')}")
```

### 示例2: 上传从网络下载的文件

```python
import requests
from scripts import KuApiClient
import tempfile
import os

client = KuApiClient()

# 从网络下载文件
file_url = "https://example.com/report.xlsx"
response = requests.get(file_url)

# 保存到临时文件后上传（只支持文件路径）
with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
    tmp_file.write(response.content)
    tmp_path = tmp_file.name

try:
    result = client.upload_attachment(
        doc_guid="WKoT7ltTnjU1oW",
        file=tmp_path  # 使用临时文件路径
    )
    if result.get("returnCode") == 200:
        print("网络文件上传成功！")
finally:
    os.unlink(tmp_path)  # 清理临时文件
```

### 示例3: 批量上传多个文件

```python
from scripts import KuApiClient
import os

client = KuApiClient()
doc_guid = "WKoT7ltTnjU1oW"
files_dir = "/path/to/files"

# 遍历目录中的所有文件
for file_name in os.listdir(files_dir):
    file_path = os.path.join(files_dir, file_name)

    # 只处理文件，跳过目录
    if os.path.isfile(file_path):
        result = client.upload_attachment(
            doc_guid=doc_guid,
            file=file_path  # 直接传入文件路径即可
        )

        if result.get("returnCode") == 200:
            attach_info = result.get("result", {})
            print(f"✓ {file_name} 上传成功 (ID: {attach_info.get('attachId')})")
        else:
            print(f"✗ {file_name} 上传失败: {result.get('returnMessage')}")
```

## 使用场景

- 向文档添加支撑材料（PDF、Word、Excel等）
- 批量上传项目相关文件
- 自动化文档附件管理
- 从其他系统迁移附件到知识库