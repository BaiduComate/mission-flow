# 创建文档

在指定知识库中创建新文档,支持三种创建模式。

## API信息

- **接口**: `POST /ku/openapi/createDoc`
- **Python方法**: `client.create_doc(repository_guid, title, content, ...)`

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| repository_guid | string | 否* | - | 知识库ID(不提供则自动查询用户个人知识库) |
| creator_username | string | 否 | - | 文档创建者名称(数字员工或员工邮箱前缀) |
| create_mode | int | 否 | 2 | 创建模式:1=空文档,2=指定内容,3=复制文档 |
| parent_doc_guid | string | 否 | null | 父目录ID(不传则为根目录) |
| title | string | 否 | null | 文档名称(不传则为"未命名文档") |
| content | string | 否 | "" | 文档正文内容(create_mode=2时使用) |
| template_doc_guid | string | 否** | null | 源文档ID(create_mode=3时必填) |
| set_top | boolean | 否 | false | 是否置顶到当前目录 |
| process_images | boolean | 否 | true | 是否自动处理Markdown中的图片 |
| base_dir | string | 否 | null | 基础目录(用于解析相对路径的本地图片) |
| md_file_path | string | 否 | null | Markdown文件路径，直接从文件读取内容 |

*注:不提供repository_guid时,会自动调用query_user_info获取用户个人知识库ID
**注:当create_mode=3时,template_doc_guid为必填项

## 创建模式说明

- **模式1**: 创建空文档,不需要额外参数
- **模式2**: 指定文档内容创建,需要提供`content`(纯文本内容或Markdown)
- **模式3**: 复制现有文档创建,需要提供`template_doc_guid`

## 图片处理说明

**自动检测规则**：当用户待写入的 `content` 中包含任意格式的图片时（包括 Markdown 图片 `![](url)`、HTML `<img>` 标签、Base64 内嵌图片等），`process_images` 自动设为 `true`，无需手动指定。

当 `process_images=true` (默认) 且 `create_mode=2` 时，会自动处理Markdown中的图片：

1. **处理流程**：先处理图片，再创建文档
2. **图片规则**：
   - 内部域名图片 (`rte.weiyun.baidu.com`): 跳过，保留原链接
   - 本地路径图片: 读取文件并上传
   - 外部URL图片: 下载后上传

使用 `base_dir` 参数可以指定基础目录，用于解析相对路径的本地图片。

## md_file_path 参数说明

当使用 `md_file_path` 参数时：

1. **自动读取文件内容**：从指定的 Markdown 文件读取内容作为 `content`
2. **自动设置 base_dir**：自动将 `base_dir` 设为文件所在目录，便于处理相对路径的本地图片
3. **自动推断标题**：如果未提供 `title`，将使用文件名（不含扩展名）作为文档标题

## 响应示例

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "docGuid": "1xosIYvQX3qxeI",
        "repositoryGuid": "E3d4LRExEl",
        "title": "示例文档",
        "creatorUsername": "zhangsan",
        "url": "https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/2tsPs8CtSd/E3d4LRExEl/1xosIYvQX3qxeI"
    },
    "traceId": "123456789012345678"
}
```

**当 process_images=true 时，result 中会额外包含：**

```json
{
    "returnCode": 200,
    "returnMessage": "OK",
    "result": {
        "docGuid": "1xosIYvQX3qxeI",
        "repositoryGuid": "E3d4LRExEl",
        "title": "示例文档",
        "creatorUsername": "zhangsan",
        "url": "https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/2tsPs8CtSd/E3d4LRExEl/1xosIYvQX3qxeI",
        "processedContent": "处理后的Markdown内容(图片URL已替换)",
        "imageUrls": {
            "./images/pic.png": "https://rte.weiyun.baidu.com/image/xxx"
        }
    },
    "traceId": "123456789012345678"
}
```

## Python调用示例

```python
from scripts import KuApiClient

client = KuApiClient()

# 方式1: 指定知识库ID创建文档
result = client.create_doc(
    repository_guid="E3d4LRExEl",
    creator_username="zhangsan",
    title="新文档",
    content="文档内容"
)

# 方式2: 自动获取个人知识库ID(推荐)
result = client.create_doc(
    creator_username="zhangsan",
    title="我的个人笔记",
    content="这将创建到zhangsan的个人知识库中"
)

# 模式1: 创建空文档
result = client.create_doc(
    creator_username="zhangsan",
    title="新空文档",
    create_mode=1
)

# 模式3: 复制现有文档创建
result = client.create_doc(
    repository_guid="E3d4LRExEl",
    creator_username="zhangsan",
    title="复制的文档",
    create_mode=3,
    template_doc_guid="cdERycpiX3nMjz"
)

# 处理本地图片的Markdown文档
result = client.create_doc(
    creator_username="zhangsan",
    title="带图片的文档",
    content="# 标题\n\n![图片](./images/pic.png)",
    base_dir="/path/to/markdown/file/dir"  # 指定相对路径的基础目录
)

# 方式5: 直接从 Markdown 文件创建（推荐）
result = client.create_doc(
    creator_username="zhangsan",
    md_file_path="/path/to/document.md"
)

# 方式6: 从 Markdown 文件创建，同时指定标题和知识库
result = client.create_doc(
    repository_guid="E3d4LRExEl",
    creator_username="zhangsan",
    title="指定标题的文档",
    md_file_path="./notes/README.md"
)
```

## 使用场景

- 快速创建新文档到用户个人知识库
- 在团队知识库中创建文档
- 基于模板批量创建文档
- 创建文档并置顶显示
