# Java 资源并发类规则

涵盖线程安全、资源泄漏、数据库操作、性能及接口鉴权问题。

---

## 一、并发与线程安全（11项）

### RACE_JAVA_01. 非线程安全集合在多线程环境并发修改 [high]
- **检测**：多线程共享 HashMap/ArrayList 并发修改，可能死循环（JDK7）、数据错乱、ConcurrentModificationException
- **排除**：已用 ConcurrentHashMap/CopyOnWriteArrayList；有锁保护

### RACE_JAVA_02. SimpleDateFormat 多线程共享 [high]
- **检测**：`static` 或 `@Service` 单例中的 `SimpleDateFormat` 成员变量被多线程共用
- **排除**：已用 ThreadLocal；已改用 DateTimeFormatter（线程安全）

### RACE_JAVA_03. 双重检查锁单例未用 volatile [high]
- **检测**：DCL 单例 `instance` 字段缺少 `volatile`，可能因指令重排返回未完成初始化的对象

```java
private static Singleton instance; // 缺 volatile
// 正确：private static volatile Singleton instance;
```

### RACE_JAVA_04. synchronized 锁对象选择不当 [Critical]
- **检测**：
  - 锁 String 常量池对象（`synchronized("lock")`）—— 不同类共享同一 String 常量，跨类互相阻塞
  - 锁 Integer 缓存值（`synchronized(Integer.valueOf(n))`）—— -128~127 范围内对象被缓存共享
  - 锁非 `private final` 对象 —— 字段可被外部替换，锁失效
  - `synchronized(this.getClass())` —— 子类共享父类锁对象
- **排除**：使用 `private final Object lock = new Object()`

```java
// 错误写法 — String 常量池共享
synchronized ("myLock") { ... }

// 错误写法 — 非 private final，可被外部替换
public Object lock = new Object();
synchronized (lock) { ... }

// 正确写法
private final Object lock = new Object();
synchronized (lock) { ... }
```

### RACE_JAVA_05. 死锁导致线程挂起 [high]
- **检测**：多线程加锁顺序不一致（线程1: A→B，线程2: B→A）形成循环等待
- **排除**：固定加锁顺序；使用 tryLock 超时

### RACE_JAVA_06. ConcurrentHashMap 复合操作非原子 [high]
- **检测**：`if(!map.containsKey(k)) { map.put(k,v) }` 两步操作间有竞态
- **排除**：已用 `computeIfAbsent`/`putIfAbsent`

### RACE_JAVA_07. volatile 使用错误 [high]
- **检测**：误以为 volatile 保证原子性（`volatile int count; count++` 仍非原子）；应用 volatile 保可见性却未用（stop flag 死循环）
- **排除**：用 AtomicInteger 等原子类；volatile 仅用于可见性保证

### RACE_JAVA_08. ThreadLocal 使用后未清理 [high]
- **检测**：线程池中 ThreadLocal.set() 后无 remove()，线程复用时数据串用或内存泄漏
- **排除**：在 finally/拦截器后置处理中有 remove()

### RACE_JAVA_09. 线程池使用无界队列或无上限线程数 [high]
- **检测**：`Executors.newFixedThreadPool`（无界队列）/`newCachedThreadPool`（无上限线程）；`new ThreadPoolExecutor(..., new LinkedBlockingQueue<>())` 无容量限制
- **排除**：有界队列且容量合理；已用 ThreadPoolExecutor 显式配置

### RACE_JAVA_10. Future.get() 未设置超时 [high]
- **检测**：`future.get()` 无超时参数，远程任务挂起时线程永久阻塞，耗尽线程池
- **排除**：已用 `future.get(timeout, unit)`

### RACE_JAVA_11. @Async 注解失效 [middle]
- **检测**：同类内部调用 @Async 方法（通过 this 调用，不经代理）；@Async 加在 private/final 方法上
- **排除**：通过注入自身代理调用；从外部 Bean 调用

---

## 二、资源泄漏（6项）

### RES_JAVA_01. 数据库连接未正确关闭 [high]
- **检测**：Connection/Statement/ResultSet 未在 finally 或 try-with-resources 中关闭
- **排除**：已用 try-with-resources；框架自动管理（Spring JdbcTemplate/MyBatis）

### RES_JAVA_02. IO 流未关闭 [high]
- **检测**：InputStream/OutputStream/Reader/Writer 未 close
- **排除**：已用 try-with-resources

### RES_JAVA_03. HTTP 连接未释放 [high]
- **检测**：CloseableHttpResponse 未消费 entity 或未 close，连接无法归还连接池
- **排除**：已用 try-with-resources + EntityUtils.consume

### RES_JAVA_04. ReentrantLock 未在 finally 中 unlock [high]
- **检测**：lock() 后无 try-finally 包裹，异常时锁永不释放导致死锁

```java
lock.lock();
try { process(); } finally { lock.unlock(); } // 正确
```

### RES_JAVA_05. 本地缓存无限增长 OOM [high]
- **检测**：静态 Map/List 只增不删，无容量限制/TTL/淘汰策略
- **排除**：有 Guava Cache/Caffeine 等带淘汰策略的缓存；数量有界

### RES_JAVA_06. ExecutorService 未 shutdown [middle]
- **检测**：方法/类中创建的 ExecutorService 未调用 shutdown/shutdownNow，线程泄漏
- **排除**：Spring 管理的 ThreadPoolTaskExecutor；有 shutdown 调用

---

## 三、数据库操作（5项）

### DB_JAVA_01. N+1 查询 [middle]
- **检测**：循环中对每条记录单独执行 SQL 查询
- **排除**：已用 IN 批量查询；JOIN 查询；循环次数极少

### DB_JAVA_02. 大批量数据操作未分批 [high]
- **检测**：`selectAll()` 百万条数据一次加载到内存；批量 insert 无分批
- **排除**：数据量确认有限；有分页/分批处理

### DB_JAVA_03. Spring 事务失效 [high]
- **检测**：同类内部方法调用 @Transactional 方法（不经代理）；@Transactional 加在 private 方法；catch 住异常未重新抛出导致事务不回滚
- **排除**：通过代理 Bean 调用；有 @Transactional(rollbackFor=Exception.class) + 异常传播

### DB_JAVA_04. 数据库免密连接 [Critical]
- **检测**：JDBC URL 中 password 为空；无密码认证
- **排除**：受信任的内网场景且有其他安全控制

### DB_JAVA_05. 数据库密码明文硬编码 [Critical]
- **检测**：源码中直接写死数据库密码字符串
- **排除**：已从配置中心/KMS 获取；已加密存储

---

## 四、性能（3项）

### PERF_JAVA_01. 循环中字符串 + 拼接 [low]
- **检测**：循环内 `result += item`，每次创建新 String 对象，应用 StringBuilder
- **排除**：循环次数极少（<10）

### PERF_JAVA_02. 正则表达式灾难性回溯 ReDoS [high]
- **检测**：`(a+)+`、`(a|aa)+` 等嵌套量词匹配长字符串，CPU 耗尽
- **排除**：输入长度有限制；正则已优化

### PERF_JAVA_03. 循环中创建重量级对象 [middle]
- **检测**：循环内 `new ObjectMapper()`/`new SimpleDateFormat()` 等代价高的对象每次新建
- **排除**：已提取到循环外；已用静态/线程本地实例

---

## 五、效率与正确性补充（4项）

### EFF_JAVA_01. 可并行的串行 Future.get() [middle]
- **检测**：连续提交多个互不依赖的 `CompletableFuture` 或 `Future`，却串行调用各自的 `.get()` 阻塞等待，而非用 `CompletableFuture.allOf()` 并行等待
- **排除**：后一个操作依赖前一个的返回值；操作间有顺序语义

```java
// 反例 — 串行阻塞，总耗时 = tA + tB
CompletableFuture<User> userFuture = fetchUserAsync(uid);
User user = userFuture.get();                   // 阻塞等待
CompletableFuture<Config> cfgFuture = fetchConfigAsync();
Config cfg = cfgFuture.get();                   // 再阻塞等待

// 正例 — 并行，总耗时 = max(tA, tB)
CompletableFuture<User> userFuture = fetchUserAsync(uid);
CompletableFuture<Config> cfgFuture = fetchConfigAsync();
CompletableFuture.allOf(userFuture, cfgFuture).join();
User user = userFuture.get();
Config cfg = cfgFuture.get();
```

### EFF_JAVA_02. 文件/资源存在性预检查（TOCTOU） [low]
- **检测**：操作前先调用 `file.exists()`/`Files.exists()` 检查存在性，再执行实际操作，形成 check-then-act 竞态
- **排除**：业务逻辑确实需要分支且不可用异常替代

```java
// 反例
if (file.exists()) {
    Files.readAllBytes(file.toPath());
}

// 正例
try {
    Files.readAllBytes(file.toPath());
} catch (NoSuchFileException e) {
    // 处理不存在
}
```

### EFF_JAVA_03. 正则校验缺少锚点 [middle]
- **检测**：用于输入校验的正则表达式缺少 `^` 和 `$` 锚点，`Pattern.matcher(input).find()` 导致部分匹配通过本应拒绝的字符串
- **排除**：明确需要部分匹配；已使用 `matches()` 方法（自带全串匹配语义）

```java
// 反例 — "123abc" 能通过纯数字校验
Pattern.compile("\\d+").matcher(input).find();

// 正例
Pattern.compile("^\\d+$").matcher(input).matches();
// 或直接用 String.matches()，它等价于全串匹配
input.matches("\\d+");
```

### EFF_JAVA_04. 抛出异常时未保留原始异常（错误链断裂） [middle]
- **检测**：在 `catch` 块中 `throw new XxxException("msg")` 时未将原始异常作为 `cause` 参数传入，导致原始堆栈信息丢失
- **排除**：有意隐藏底层异常（安全场景）；原始异常已记录到日志

```java
// 反例 — 原始 cause 丢失
try {
    db.execute(sql);
} catch (SQLException e) {
    throw new ServiceException("数据库写入失败");  // e 丢失
}

// 正例
try {
    db.execute(sql);
} catch (SQLException e) {
    throw new ServiceException("数据库写入失败", e);
}
```

