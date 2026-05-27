# JavaScript/TypeScript 资源并发类规则

涵盖性能、内存、资源释放、并发竞态、计算准确性及 SQL 操作问题。需考虑时序、资源生命周期、并发场景才能暴露的问题。

---

## 一、性能问题

### PERF_01. 大数组/大数据集循环操作 [middle]
- 全量查询无 limit + 内存遍历；O(n²) 嵌套循环；主线程大数据量 sort/filter/map 链式
- **排除**：有分页/limit；数据量 <100；Web Worker/流式处理

### PERF_02. 频繁 DOM 操作 [low]
- 循环内 appendChild/innerHTML/style.*/classList.*；读写交替触发重排
- **排除**：DocumentFragment；数据量 <5

### PERF_03. 缺少缓存 [low]
- 循环内重复调用同参函数/接口；高频纯函数未 memoize；同周期多次查库
- **排除**：函数有副作用不适合缓存；数据量小

### PERF_04. 同步 XMLHttpRequest 阻塞主线程 [high]
- **检测**：`xhr.open('GET', url, false)`（第三个参数为 false）
- **排除**：Service Worker 中的同步 XHR（特定场景）

### PERF_05. 主线程大循环阻塞 [middle]
- **检测**：主线程执行超大循环（>10万次迭代）或重计算，未使用 Web Worker 或 requestIdleCallback 分片
- **排除**：已用 Web Worker；循环量确认有限

---

## 二、接口限流

### RATE_01. API 调用无限流 [middle]
- 对外/第三方接口无 rate-limit 中间件；发短信/邮件等敏感操作无限流
- **排除**：有全局限流中间件；内部接口；天然幂等

### RATE_02. 循环内调用外部接口 [high]
- for/forEach/while 内 axios/fetch/request/http.get
- **排除**：循环 ≤3 次；有 delay/throttle；有批量接口

### RATE_03. 并发请求未控制 [middle]
- `Promise.all(array.map(...))` 且 array 可能 >20；无并发控制库
- **排除**：数组明确很少；有 p-limit/bottleneck

---

## 三、内存泄漏

### MEM_01. 未清理的定时器 [high]
- setInterval 未保存引用；Vue/React 组件中 setInterval 无 beforeDestroy/unmount 对应清理；setTimeout 递归无退出条件
- **排除**：有 clearInterval/clearTimeout；一次性短定时器且不在组件内

### MEM_02. 未清理的事件监听器 [high]
- addEventListener 在组件中使用，对应 removeEventListener 未在销毁时调用
- **排除**：有清理逻辑；全局持久监听且有意设计

### MEM_03. 闭包引用大对象 [middle]
- 闭包引用大数组/DOM/请求结果且被长期持有（模块级变量、全局缓存）
- **排除**：闭包生命周期短；引用对象小

### MEM_04. 无限制增长的缓存 [high]
- 模块级 Map/Object/Array 只增不删；无 TTL/LRU/容量限制
- **排除**：有清理逻辑；数量有界（枚举/配置）

---

## 四、资源释放

### RES_01. 文件句柄未关闭 [high]
- fs.open/createReadStream/createWriteStream 后无 close；catch/finally 未关闭
- **排除**：使用 readFile/writeFile 等自动关闭 API；finally 有关闭

### RES_02. 数据库连接/事务未释放 [high]
- getConnection 无 release；beginTransaction 后 catch 无 rollback；finally 无释放
- **排除**：连接池自动管理（ORM）；finally 有释放

---

## 五、高危缺陷（运行时崩溃）

### FATAL_01. 空指针/undefined 解引用 [high]
- 链式访问无 `?.` 且可能为 null；异步结果未判空；find/[index] 结果未判断 undefined
- **排除**：有 null 判断；使用了 `?.`；上下文确保非空

### FATAL_02. 数组越界访问 [middle]
- 动态索引未校验范围；`arr[arr.length]`；外部输入索引未校验
- **排除**：有长度检查

### FATAL_03. 类型错误 [middle]
- 对非数组调用 .map/.filter/.forEach；字符串 ID 做数字运算；Promise 当同步值用
- **排除**：有类型检查或 TypeScript 类型保护

---

## 六、并发竞态

### RACE_01. 缺少事务/锁保护 [high]
- 多个数据库写操作无事务；先查后更新无行锁；数量字段未用原子操作
- **排除**：有事务；有 SELECT FOR UPDATE；有乐观锁/Redis 原子操作

### RACE_02. 重复提交防护缺失 [high]
- 创建订单/支付/领取等敏感接口无幂等 token；无唯一约束；无防抖防重
- **排除**：有 idempotencyKey；有唯一索引；操作天然幂等

---

## 七、计算准确性

### CALC_01. 大数整数溢出 [middle]
- 大 ID（雪花 ID/时间戳）或大金额直接数值运算未用 BigInt
- **排除**：值域确认在 Number.MAX_SAFE_INTEGER 范围内

### CALC_02. 并发下计数丢失 [high]
- 先查数量再更新，中间无原子操作或事务保护（详见 SQL_CONC_01）

---

## 八、SQL 操作问题

### SQL_PERF_01. N+1 查询 [middle]
- for/forEach/map/while 循环内调用数据库方法或 await 异步查询
- **排除**：有 break 且数量有限；Promise.all 并行；已用 IN 批量查询

### SQL_CONC_01. 库存/数量非原子操作 [high]
- 先 SELECT 后 UPDATE 模式（findOne → stock - quantity → save），无事务/行锁/原子操作
- **排除**：`UPDATE SET stock = stock - 1 WHERE stock > 0` 原子操作；SELECT FOR UPDATE；乐观锁；Redis DECR

### SQL_CONC_02. check-then-act 非原子 [high]
- 先查询判断（findOne/count）再插入/更新，中间无锁/事务保护，无唯一约束
- **排除**：有唯一索引；有事务+行锁；有幂等 token

### SQL_TRANS_01. 事务完整性缺失 [high]
- 多个连续数据库写操作构成原子业务单元，无 beginTransaction/startTransaction，无 rollback
- **排除**：单个写操作；已有事务；操作相互独立

### SQL_PERF_02. 缺少查询索引 [middle]
- 原生 SQL WHERE 条件字段无索引；ORM 用低选择/无索引字段；上下文表明大表
- **排除**：用主键查询；已注释说明有索引；表数据量明确小
- **复核**：需明确证据（注释/表结构），不确定不上报

---

## 九、效率问题补充（3项）

### EFF_01. 可并行的串行 await [middle]
- **检测**：连续多个 `await asyncA()` + `await asyncB()` 且两个操作互不依赖（B 不使用 A 的返回值），应改为 `Promise.all`
- **排除**：B 依赖 A 的结果；操作间有顺序语义（如日志记录、事务步骤）；有意串行限流

```javascript
// 反例 — 串行，总耗时 = tA + tB
const user = await fetchUser(id);
const config = await fetchConfig(); // 不依赖 user，可并行

// 正例 — 并行，总耗时 = max(tA, tB)
const [user, config] = await Promise.all([fetchUser(id), fetchConfig()]);
```

### EFF_02. 文件/资源存在性预检查（TOCTOU） [low]
- **检测**：操作前先调用 `fs.existsSync`/`fs.access` 检查存在性，再执行实际操作，形成 check-then-act 竞态，且增加额外 I/O
- **排除**：业务逻辑确实需要分支判断（如"不存在则创建"但使用了原子 flags）
- **复核**：确认可以用 try-catch 处理 ENOENT 替代预检查

```javascript
// 反例 — 两次 I/O，且存在竞态
if (fs.existsSync(filePath)) {
    const data = fs.readFileSync(filePath);
}

// 正例 — 直接操作，catch 处理不存在
try {
    const data = fs.readFileSync(filePath);
} catch (e) {
    if (e.code !== 'ENOENT') throw e;
}
```

### EFF_03. 无变化时触发的无效更新 [low]
- **检测**：在轮询、定时器或事件处理器中，无条件更新状态/存储（如 `setState(value)`），未在写入前比较新旧值，导致下游无意义重渲染/重计算
- **排除**：已有 `if (prev !== next)` 守卫；状态管理框架内置了浅比较
- **复核**：确认触发频率较高（如 setInterval ≤1s 或高频事件）；确认下游有实际渲染开销
