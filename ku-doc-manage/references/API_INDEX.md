# 知识库API完整文档索引

本目录包含14个知识库OpenAPI的详细文档,Agent可按需加载。

## 文档管理类

- [query_content.md](./query_content.md) - 查询文档正文内容
- [query_repo.md](./query_repo.md) - 分页查询知识库文档列表
- [create_doc.md](./create_doc.md) - 创建文档(支持3种模式)
- [edit_content.md](./edit_content.md) - 编辑文档正文(追加/覆盖)
- [copy_doc.md](./copy_doc.md) - 复制文档
- [upload_attachment.md](./upload_attachment.md) - 上传文档附件

## 权限管理类

- [query_permission.md](./query_permission.md) - 查询用户对文档的权限
- [add_member.md](./add_member.md) - 为文档添加成员
- [update_member.md](./update_member.md) - 更新文档成员权限
- [change_scope.md](./change_scope.md) - 修改文档公开范围

## 互动数据类

- [query_comments.md](./query_comments.md) - 查询文档评论
- [query_recent_view.md](./query_recent_view.md) - 查询文档浏览记录

## 高级功能类

- [query_flowchart.md](./query_flowchart.md) - 导出流程图数据
- [query_user_info.md](./query_user_info.md) - 查询用户个人信息(含个人知识库ID)

## 使用说明

当用户请求某个具体功能时,Agent应:
1. 根据用户意图判断需要哪个API
2. 读取对应的markdown文档
3. 参考文档中的参数说明和示例代码
4. 调用KuApiClient的对应方法完成任务
