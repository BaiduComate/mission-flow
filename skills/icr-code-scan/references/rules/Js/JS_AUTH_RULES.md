# 接口鉴权与越权检测规则

本文件检测对外暴露接口的鉴权缺失与越权访问风险。适用于 JS/TS Node.js 后端服务。

---

### AUTH_01. 对外接口缺少鉴权 [high]
- **检测**：有路由定义（router.get/post/put/delete）但无身份校验（req.user/req.session/ctx.user 校验）且无鉴权中间件（auth/authenticate/jwt/passport）
- **排除**：健康检查（/health/ping/status）、登录注册、静态资源、Swagger、Webhook 回调、全局中间件统一鉴权
- **复核**：确认无全局 auth 中间件；确认非公开接口

### AUTH_02. 越权访问 - 未校验资源归属 [high]
- **检测**：接口能获取用户身份（req.user），但操作资源时只用传入 ID（req.params.id/req.body.userId），未关联校验资源所有者
- **排除**：管理员接口有角色校验；公共资源；ORM 关联查询间接校验
- **复核**：确认能获取用户身份；确认未校验归属；确认非公共资源

### AUTH_03. 身份校验逻辑错误 [high]
- **检测**：用 `==` 而非 `===` 做 ID 比较；校验变量来自请求参数而非 token（req.params/query/body）；校验条件有赋值操作（`=` 代替 `==`）；校验位置在 early return 之后可被跳过
- **排除**：校验逻辑有效；框架内置权限；中间件统一处理
- **复核**：确认缺陷可被利用；确认变量来源错误

```javascript
// 错误写法 — 校验变量来自请求参数，可被伪造
router.get('/orders/:id', (req, res) => {
    const userId = req.params.userId;  // 来自请求，不可信
    if (order.userId === userId) { ... }
});

// 正确写法 — 从已验证的 token 中获取
router.get('/orders/:id', authMiddleware, (req, res) => {
    const userId = req.user.id;  // 来自解析后的 token
    if (order.userId === userId) { ... }
});
```

### AUTH_04. 鉴权中间件配置遗漏 [middle]
- **检测**：有全局鉴权中间件但部分路由组未被覆盖；中间件只保护特定 HTTP 方法
- **排除**：明确分开的公开/受保护路由文件；NestJS Guards 等框架统一鉴权
- **复核**：确认中间件确实未覆盖

### AUTH_05. 垂直越权 - 敏感操作缺少角色/权限校验 [high]
- **检测**：删除用户/修改权限/导出数据等管理员级别操作，未校验 `req.user.role` 或权限标记，普通用户可执行
- **排除**：有角色校验（admin/superuser）；框架级权限管理（RBAC 中间件）
- **复核**：确认该操作需要特权；确认无权限校验

---

**通用排除**：健康检查/登录/静态资源/Webhook 回调；全局中间件统一鉴权；框架统一权限管理（NestJS Guards、Passport）
