# Python 接口鉴权规则

检测对外接口的鉴权缺失与越权访问风险。

---

### AUTH_PY_01. 对外接口缺少鉴权 [high]
- **检测**：Flask/Django/FastAPI 路由定义无 `@login_required`/`@require_auth`/JWT 验证，且非公开接口
- **排除**：健康检查/登录/静态资源；全局中间件/装饰器统一鉴权

### AUTH_PY_02. 越权访问 - 未校验资源归属 [high]
- **检测**：接口通过 request 参数获取资源 ID，未校验该资源是否属于当前登录用户
- **排除**：管理员接口有角色校验；公共资源

### AUTH_PY_03. 身份校验逻辑错误 [high]
- **检测**：用 `==` 而非 `hmac.compare_digest` 等时序安全比较做 token 校验；校验变量来自请求参数而非已验证的会话

```python
# 错误写法 — 普通 == 比较存在时序攻击风险，且变量来自请求
token = request.args.get('token')
if token == SECRET_TOKEN: ...

# 正确写法
import hmac
if hmac.compare_digest(token, SECRET_TOKEN): ...
```

### AUTH_PY_04. 鉴权中间件配置遗漏 [middle]
- **检测**：部分路由/蓝图未被鉴权中间件覆盖
- **排除**：有全局 before_request 统一鉴权

### AUTH_PY_05. 垂直越权 - 敏感操作缺少角色校验 [high]
- **检测**：管理员级别操作缺少 `current_user.is_admin` 或权限校验
- **排除**：RBAC 中间件统一处理

---

**通用排除**：健康检查/登录/Webhook；全局中间件；框架内置权限管理（Django permissions、FastAPI Dependencies）
