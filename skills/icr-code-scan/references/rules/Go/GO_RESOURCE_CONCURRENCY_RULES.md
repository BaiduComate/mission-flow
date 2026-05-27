# Go 资源并发类规则

涵盖资源管理、内存泄漏、并发竞态、错误处理、性能及接口鉴权问题。

---

## 一、资源管理与内存泄漏

### RES_GO_01. 文件/网络连接/数据库行未关闭 [high]
- **检测**：`os.Open`/`http.Get`/`db.Query` 后未 `defer Close()`；HTTP 响应体 `resp.Body` 未关闭；`rows` 未调用 `rows.Close()`
- **排除**：使用了自动管理资源的库；finally/defer 有关闭

### RES_GO_02. goroutine 泄漏 [high]
- **检测**：goroutine 阻塞在无消费者的 channel 发送；调用方超时/取消后 goroutine 因 channel 满/无缓冲永久阻塞；无退出条件的 `for {}` goroutine
- **排除**：使用有缓冲 channel；有 `ctx.Done()` 退出；有 done 信号

```go
func handleRequest() {
    ch := make(chan Result)        // 无缓冲
    go func() { ch <- doWork() }()
    select {
    case r := <-ch: return r
    case <-time.After(1 * time.Second): return // goroutine 泄漏：doWork 永久阻塞在发送
    }
}
// 修复：ch := make(chan Result, 1)
```

### RES_GO_03. 全局缓存无限增长导致 OOM [high]
- **检测**：全局 `var cache = make(map[...])` 只增不删，无 TTL/LRU/容量限制
- **排除**：有定期清理；数量有界；使用带淘汰策略的缓存库

### RES_GO_04. defer 在循环中导致资源延迟释放 [middle]
- **检测**：循环体内 `defer f.Close()`，资源直到函数返回才释放，大批量时同时持有大量 fd
- **排除**：循环次数极少（<5）；已提取为独立函数使 defer 生效

---

## 二、并发与竞态

### RACE_GO_01. 全局变量并发读写无锁保护 [high]
- **检测**：多 goroutine 并发读写同一 map/slice/结构体字段，无 `sync.Mutex`/`sync.RWMutex`/`atomic` 保护
- **排除**：只读操作；有锁保护；使用 `sync.Map`

### RACE_GO_02. 死锁导致服务挂起 [high]
- **检测**：多 goroutine 加锁顺序不一致（A→B 和 B→A）；向无缓冲 channel 发送但无接收者；channel 操作无 select/超时
- **排除**：固定加锁顺序；有 select+超时；有缓冲 channel

### RACE_GO_03. sync.WaitGroup 使用不当 [high]
- **检测**：`wg.Add(1)` 在 goroutine 内部调用（可能 Wait 已返回时还未 Add）；panic 路径导致 `Done()` 未调用（未用 defer）
- **排除**：`wg.Add` 在 goroutine 启动前调用；`defer wg.Done()`

```go
// 错误写法 — Add 在 goroutine 内，可能 Wait 提前返回
go func() {
    wg.Add(1)      // 太晚了
    defer wg.Done()
    doWork()
}()
wg.Wait()

// 正确写法
wg.Add(1)
go func() {
    defer wg.Done()
    doWork()
}()
wg.Wait()
```

### RACE_GO_04. 并发修改共享 slice 导致竞态 [high]
- **检测**：多 goroutine 并发对同一 slice 执行 append 或索引赋值，无锁保护
- **排除**：预分配 slice 且各 goroutine 操作不同索引；用 channel 收集结果

---

## 三、错误处理

### ERR_GO_01. 忽略错误返回值 [high]
- **检测**：函数返回 error 被 `_` 丢弃，或调用时直接忽略（`f.Write(data)` 不接收返回值）
- **排除**：明确确认错误可忽略且有注释说明

### ERR_GO_02. 错误被静默吞掉 [high]
- **检测**：`recover()` 后不记录日志也不向上传递；接收 error 后 `_ = err`
- **排除**：确认是预期的静默处理且有注释

### ERR_GO_03. defer 中修改非命名返回值无效 [middle]
- **检测**：在非命名返回值函数的 defer 中修改局部 `err` 变量，以为会影响返回值，实则无效
- **排除**：使用命名返回值（`func f() (result string, err error)`）

```go
// 错误写法 — 修改的是局部变量，返回值不受影响
func getUser() (string, error) {
    var err error
    defer func() {
        if err != nil { err = fmt.Errorf("wrap: %w", err) } // 无效！
    }()
    return fetch()
}

// 正确写法 — 命名返回值
func getUser() (name string, err error) {
    defer func() {
        if err != nil { err = fmt.Errorf("wrap: %w", err) } // 有效
    }()
    name, err = fetch()
    return
}
```

---

## 四、性能

### PERF_GO_01. 无限循环或轮询无 sleep 耗尽 CPU [high]
- **检测**：`for {}` 内无 sleep/channel/ticker，CPU 空转；`for !done {}` 自旋等待
- **排除**：有 `time.Sleep`；有 channel 等待；有 `ticker.C`

### PERF_GO_02. N+1 查询 [middle]
- **检测**：循环内对每条记录单独发起数据库查询
- **排除**：循环次数确认极少；有 IN 批量查询

---

## 五、效率与正确性补充（4项）

### EFF_GO_01. 可并行的串行 goroutine 等待 [middle]
- **检测**：多个互不依赖的操作被顺序串行执行（逐个同步调用），而非启动多个 goroutine 并用 `sync.WaitGroup` 或 channel 并行等待
- **排除**：后一个操作依赖前一个的返回值；操作间有顺序语义；并发写入同一资源

```go
// 反例 — 串行，总耗时 = tA + tB
user, _ := fetchUser(uid)    // 同步阻塞
config, _ := fetchConfig()   // 再同步阻塞

// 正例 — 并行 goroutine
var wg sync.WaitGroup
var user User
var cfg Config
wg.Add(2)
go func() { defer wg.Done(); user, _ = fetchUser(uid) }()
go func() { defer wg.Done(); cfg, _ = fetchConfig() }()
wg.Wait()
```

### EFF_GO_02. 文件/资源存在性预检查（TOCTOU） [low]
- **检测**：操作前先调用 `os.Stat()`/`os.IsExist()` 检查存在性，再执行实际操作，形成 check-then-act 竞态
- **排除**：业务逻辑确实需要分支且不可用错误处理替代；有文件锁保证原子性

```go
// 反例
if _, err := os.Stat(path); err == nil {
    data, _ = os.ReadFile(path)
}

// 正例 — 直接操作，检查错误类型
data, err := os.ReadFile(path)
if err != nil {
    if errors.Is(err, os.ErrNotExist) {
        // 文件不存在
    } else {
        return err
    }
}
```

### EFF_GO_03. 正则校验缺少锚点 [middle]
- **检测**：用于输入校验的正则表达式缺少 `^` 和 `$` 锚点，`regexp.MatchString` 或 `re.FindString` 导致部分匹配通过本应拒绝的字符串
- **排除**：明确需要部分匹配；已使用完整字符串匹配语义

```go
// 反例 — "123abc" 能通过纯数字校验
matched, _ := regexp.MatchString(`\d+`, input)

// 正例
matched, _ := regexp.MatchString(`^\d+$`, input)
```

### EFF_GO_04. 错误链断裂（未使用 %w 包装） [middle]
- **检测**：在错误处理中使用 `fmt.Errorf("msg: %v", err)` 或 `errors.New("msg")` 重新包装错误，未使用 `%w` 动词，导致 `errors.Is`/`errors.As` 无法在调用链上匹配原始错误类型
- **排除**：有意隐藏底层错误类型（安全场景）；原始错误已在日志中记录

```go
// 反例 — %v 仅转为字符串，errors.Is() 无法匹配原始类型
return fmt.Errorf("查询用户失败: %v", err)

// 正例 — %w 保留错误链，errors.Is(err, sql.ErrNoRows) 可正常工作
return fmt.Errorf("查询用户失败: %w", err)
```

