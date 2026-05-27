# Java 接口鉴权规则

检测对外接口的鉴权缺失与越权访问风险。

---

### AUTH_JAVA_01. 对外接口缺少鉴权 [high]
- **检测**：Spring MVC Controller 方法无 @PreAuthorize/@Secured/自定义鉴权注解，且为对外接口
- **排除**：健康检查/登录/静态资源；有全局拦截器统一鉴权；@PermitAll

### AUTH_JAVA_02. 越权访问 - 未校验资源归属 [high]
- **检测**：通过 @PathVariable 或 @RequestParam 获取资源 ID，未校验资源归属当前用户

### AUTH_JAVA_03. 身份校验逻辑错误 [high]
- **检测**：用 `==` 比较 Long/Integer userId（应用 `.equals()`）；校验变量来自请求参数而非 SecurityContext

```java
// 错误写法 — Long 用 == 比较，超出缓存范围时失效
if (order.getUserId() == currentUserId) { ... }

// 正确写法
if (order.getUserId().equals(currentUserId)) { ... }
```

### AUTH_JAVA_04. 鉴权注解或拦截器配置遗漏 [middle]
- **检测**：SecurityConfig 中部分 URL pattern 遗漏配置；permitAll 范围过宽

### AUTH_JAVA_05. 垂直越权 - 敏感操作缺少角色校验 [high]
- **检测**：管理员操作缺少 `hasRole('ADMIN')` 或等效校验
- **排除**：RBAC 中间件统一处理

---

**通用排除**：健康检查/登录/静态资源；Spring Security 全局配置；框架统一权限管理
