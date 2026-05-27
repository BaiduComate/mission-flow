# Python 资源并发类规则

涵盖资源管理、内存泄漏、并发/协程问题、性能及接口鉴权问题。

---

## 一、资源管理与内存泄漏

### RES_PY_01. 文件句柄未关闭 [high]
- **检测**：`f = open(...)` 未用 `with` 包裹，异常时文件未关闭，fd 泄漏
- **排除**：已用 `with open(...) as f`

### RES_PY_02. 数据库连接未释放 [high]
- **检测**：`conn = db_pool.get_connection()` 后未在 finally/with 中关闭，连接池耗尽
- **排除**：已用 `with db_pool.get_connection() as conn`

### RES_PY_03. 网络连接/Socket 未关闭 [middle]
- **检测**：Socket 未关闭；requests 未用 Session 导致连接无法复用（每次新建短连接）
- **排除**：已用 `requests.Session`；已用 `with` 管理 socket

### RES_PY_04. 线程/进程资源未清理 [high]
- **检测**：`Process.start()` 后未 `join()`，产生僵尸进程；`ThreadPoolExecutor` 未 `shutdown()`
- **排除**：已用 `with ThreadPoolExecutor(...) as executor`；有 `p.join()`

### RES_PY_05. 临时文件未删除磁盘占满 [middle]
- **检测**：`NamedTemporaryFile(delete=False)` 后未在 finally 中删除；上传文件处理后未清理
- **排除**：`delete=True`（默认）；有 finally 删除

### RES_PY_06. 内存泄漏（循环引用与全局容器）[high]
- **检测**：父子对象相互持有引用形成环；全局 list/dict 无上限持续 append，无清理策略
- **排除**：使用 `weakref`；使用 `deque(maxlen=N)` 有界容器

### RES_PY_07. 大文件一次性加载到内存 [high]
- **检测**：`f.read()` 读取大文件全部内容；ORM `Model.objects.all()` 百万级数据全量加载
- **排除**：已用逐行迭代；已用 `.iterator(chunk_size=N)` 分批

### RES_PY_08. 大对象未及时释放 [middle]
- **检测**：大型 DataFrame/数组用完后未 `del df`，函数返回后仍持有引用，内存无法回收
- **排除**：函数返回后对象自然超出作用域；有 `del` + `gc.collect()`

---

## 二、并发与协程问题

### RACE_PY_01. 全局变量并发修改无锁保护 [high]
- **检测**：多线程同时修改全局变量/共享字典，无 `threading.Lock` 保护；check-then-act 竞态
- **排除**：有 Lock/RLock；只读操作；GIL 足以保护的原子操作

### RACE_PY_02. 死锁导致服务挂起 [high]
- **检测**：多线程加锁顺序不一致（lock1→lock2 与 lock2→lock1）形成循环等待
- **排除**：固定加锁顺序（如按 `id()` 排序）

### RACE_PY_03. 线程不安全数据结构并发修改 [high]
- **检测**：多线程并发 `list.append`/迭代修改 dict（虽 CPython GIL 保护单步，但复合操作仍不安全）
- **排除**：已用 `queue.Queue`；有锁保护

### RACE_PY_04. 异步函数未 await 导致逻辑跳过 [high]
- **检测**：`save_data(data)` 而非 `await save_data(data)`，协程未执行，关键逻辑被跳过

```python
# 错误写法 — 仅创建协程对象，未执行
async def handle():
    save_data(data)      # 没有 await，save_data 是 async 函数时什么都没做
    return "ok"

# 正确写法
async def handle():
    await save_data(data)
    return "ok"
```

### RACE_PY_05. asyncio 事件循环中执行阻塞 IO [high]
- **检测**：async 函数内 `time.sleep()`/`requests.get()`/`open()` 等同步阻塞调用，阻塞整个事件循环
- **排除**：已用 `asyncio.sleep`；已用 `aiohttp`/`aiofiles`；已用 `run_in_executor`

### RACE_PY_06. 协程未正确启动或 Task 无强引用被 GC [high]
- **检测**：`send_email()` 未 await，仅创建协程对象未执行；`asyncio.create_task(...)` 结果未保持引用，可能被 GC 回收
- **排除**：有 await；Task 引用被保存

```python
# 错误写法 — Task 可能被 GC 回收
asyncio.create_task(send_notification(user))  # 返回值未保存

# 正确写法
task = asyncio.create_task(send_notification(user))
background_tasks.add(task)
task.add_done_callback(background_tasks.discard)
```

### RACE_PY_07. 队列满无超时导致无限阻塞 [middle]
- **检测**：`q.put(item)` 队列已满时无限阻塞；无 `timeout` 参数
- **排除**：`q.put(item, timeout=N)` 有超时；队列有足够容量

---

## 三、性能

### PERF_PY_01. 无限循环 CPU 耗尽 [high]
- **检测**：`while True:` 无 break/sleep 条件，CPU 占满
- **排除**：有明确退出条件；有 sleep/等待

### PERF_PY_02. N+1 查询 [middle]
- **检测**：循环中 `User.objects.get(id=order.user_id)` 每条记录单独查库
- **排除**：已用 `select_related`/`prefetch_related`；已用 IN 批量查询

### PERF_PY_03. 正则表达式回溯爆炸 ReDoS [high]
- **检测**：`(a+)+`/`(a|aa)+` 嵌套量词匹配长字符串，CPU 耗尽
- **排除**：输入长度有限制；正则已优化无嵌套量词

### PERF_PY_04. 无限制创建线程 [high]
- **检测**：循环中 `Thread(target=...).start()` 无上限，大量 URL 创建大量线程
- **排除**：已用 `ThreadPoolExecutor(max_workers=N)`

---

## 四、效率与正确性补充（4项）

### EFF_PY_01. 可并行的串行 await [middle]
- **检测**：连续多个 `await coro_a()` + `await coro_b()` 且两个协程互不依赖，应改为 `asyncio.gather()`
- **排除**：coro_b 依赖 coro_a 的返回值；操作间有顺序语义（如写日志、事务步骤）

```python
# 反例 — 串行，总耗时 = tA + tB
user = await fetch_user(uid)
config = await fetch_config()  # 不依赖 user，可并行

# 正例 — 并行，总耗时 = max(tA, tB)
user, config = await asyncio.gather(fetch_user(uid), fetch_config())
```

### EFF_PY_02. 文件/资源存在性预检查（TOCTOU） [low]
- **检测**：操作前先调用 `os.path.exists()`/`os.path.isfile()` 检查存在性，再执行实际操作，形成 check-then-act 竞态并增加额外 I/O
- **排除**：业务逻辑确实需要分支判断且不可用异常替代；检查结果用于路由逻辑而非仅判断能否继续

```python
# 反例 — 两次 I/O，存在竞态
if os.path.exists(path):
    with open(path) as f:
        data = f.read()

# 正例 — 直接操作，catch 处理不存在
try:
    with open(path) as f:
        data = f.read()
except FileNotFoundError:
    data = None
```

### EFF_PY_03. 正则校验缺少锚点 [middle]
- **检测**：用于输入校验的正则表达式缺少 `^` 和 `$`（或 `\A`/`\Z`）锚点，`re.search`/`re.match` 导致部分匹配通过本应拒绝的字符串
- **排除**：明确需要部分匹配（如在文本中提取内容）；已使用 `re.fullmatch()`

```python
# 反例 — "123abc" 能通过纯数字校验
if re.search(r'\d+', user_input):  # 只要含数字就通过

# 正例
if re.fullmatch(r'\d+', user_input):
# 或
if re.match(r'^\d+$', user_input):
```

### EFF_PY_04. 抛出异常时未保留原始异常（错误链断裂） [middle]
- **检测**：在 `except` 块中 `raise NewException("msg")` 时未使用 `raise NewException("msg") from e`，导致原始异常的 traceback 和信息丢失，上层难以溯源
- **排除**：有意隐藏底层错误（安全场景）；原始异常已记录到日志

```python
# 反例 — 原始 traceback 丢失
try:
    db.execute(sql)
except Exception as e:
    raise ServiceError("数据库写入失败")  # e 的 traceback 消失

# 正例
try:
    db.execute(sql)
except Exception as e:
    raise ServiceError("数据库写入失败") from e
```

