# Go 正确性规则

静态模式可识别的确定性错误，仅看代码结构即可判断，单次执行可触发。

---

## 一、空值与 nil 安全（4项）

### CORRECTNESS_GO_01. 对 nil 指针进行方法调用或字段访问 [Critical]
- **检测**：对可能为 nil 的指针直接访问字段或调用方法，无 nil 判断；接口断言未用 comma-ok 模式；map 取值后直接解引用
- **排除**：有 nil 判断；上下文保证非 nil

```go
user := db.FindUser(id)
name := user.Name // user 为 nil 时 panic

s := i.(*MyStruct) // 断言失败时 panic，应用 s, ok := i.(*MyStruct)
```

### CORRECTNESS_GO_02. 未检查 context.WithCancel 返回的 cancel 函数 [Critical]
- **检测**：`context.WithCancel`/`WithTimeout`/`WithDeadline` 返回的 cancel 未调用（用 `_` 丢弃，或在错误路径提前 return 前未执行）
- **排除**：有 `defer cancel()`；cancel 在所有路径均有调用

### CORRECTNESS_GO_03. 对 nil map 进行写操作 [Critical]
- **检测**：map 类型字段或变量未通过 `make` 初始化就进行写操作，导致 `panic: assignment to entry in nil map`
- **排除**：有 `make` 初始化；有 nil 判断后初始化

### CORRECTNESS_GO_04. 切片越界访问 [Critical]
- **检测**：访问切片索引前未校验长度；假设固定元素数量直接用索引；`parts[0]` 在可能为空切片上使用
- **排除**：有 `len()` 检查；索引来源确认有界

---

## 二、类型与接口问题（3项）

### CORRECTNESS_GO_05. 接口值与 nil 比较陷阱 [Critical]
- **检测**：函数返回接口类型，但实际返回一个底层值为 nil 的具体类型指针（`return (*MyError)(nil)`），导致调用方 `if err != nil` 判断为 true
- **排除**：直接 `return nil`

```go
func getError() error {
    var p *MyError = nil
    return p // 此时 err != nil 为 true！接口含有类型信息但值为 nil
}
// 正确：直接 return nil
```

### CORRECTNESS_GO_06. 类型断言未用 comma-ok 模式 [Critical]
- **检测**：`v := i.(SomeType)` 未使用 `v, ok := i.(SomeType)` 形式，断言失败时 panic
- **排除**：确认接口值类型；已有 recover

```go
// 错误写法 — 断言失败直接 panic
s := i.(*MyStruct)

// 正确写法
s, ok := i.(*MyStruct)
if !ok {
    return errors.New("type assertion failed")
}
```

### CORRECTNESS_GO_07. printf 格式化动词与参数类型不匹配 [Critical]
- **检测**：`fmt.Printf`/`Sprintf`/`log.Printf` 格式化动词数量或类型与参数不匹配（如 `%s` 传 int，参数多于占位符）；直接 `log.Printf(err.Error())` 若含 `%` 则格式化出错
- **排除**：`%v` 通用动词使用正确

---

## 三、代码静态检测（5项）

### CORRECTNESS_GO_08. 不可达的死代码 [Critical]
- **检测**：`return`/`panic` 语句之后存在永远不会执行的代码
- **排除**：编译期可检出的场景（编译器通常已报告）

### CORRECTNESS_GO_09. 布尔运算符使用错误 [Critical]
- **检测**：布尔表达式中存在永真/永假条件（如 `x < 0 && x > 0`）；冗余条件（如 `err != nil || err == io.EOF`）
- **排除**：防御性代码；逻辑确实正确

### CORRECTNESS_GO_10. unsafe.Pointer 使用不当 [Critical]
- **检测**：将 `unsafe.Pointer` 转换为 `uintptr` 后存储，再将 `uintptr` 转回指针（GC 可能已移动对象）
- **排除**：原子操作中的合规用法；遵循 `unsafe.Pointer` 规则的转换

### CORRECTNESS_GO_11. struct 字段 tag 格式错误 [Critical]
- **检测**：struct tag 格式不合规，导致反射解析失败，JSON/ORM 行为异常
- **排除**：工具已检查过格式

```go
// 错误写法 — 冒号后有空格（json: "name" 而非 json:"name"）
type User struct {
    Name string `json: "name"`  // 错误：冒号后有空格
    Age  int    `json:"age,"`   // 错误：多余逗号
}

// 正确写法
type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
```

### CORRECTNESS_GO_12. 测试/示例代码误用 [Critical]
- **检测**：Example 函数的 `// Output:` 注释与实际输出不一致；测试函数名不以 `Test` 开头（如 `Testlogin`），导致测试用例永远不执行
- **排除**：`// Unordered output:` 等合规注释形式

---

## 四、数值与逻辑（1项）

### CORRECTNESS_GO_13. 整数溢出导致逻辑错误 [Critical]
- **检测**：int32/int 类型做大数乘法（如金额×数量）结果溢出变负数；切片长度相加可能溢出（32位系统）
- **排除**：已用 int64 或 math/big；值域确认不会溢出
