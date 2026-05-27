# Go 代码风格扫描规则（共17条）

---

## 一、命名规则（4项）

### 1. GoRule001 NamingCamelCase - 变量、常量、函数名使用驼峰命名，缩写词应全大写 [Critical]

**缺陷描述**：变量、常量、函数名统一使用驼峰命名法（camelCase / PascalCase）。常用缩写词（如 HTTP、ID、URL 等）应保持全大写；当作为非导出标识符的首部时则全小写（如 `httpServer`）。

**常用缩写名单（应全大写）**：
`ACL`, `API`, `ASCII`, `CPU`, `CSS`, `DNS`, `EOF`, `GUID`, `HTML`, `HTTP`, `HTTPS`, `ID`, `IP`, `JSON`, `QPS`, `RAM`, `RPC`, `SLA`, `SMTP`, `SQL`, `SSH`, `TCP`, `TLS`, `TTL`, `UDP`, `UI`, `GID`, `UID`, `UUID`, `URI`, `URL`, `UTF8`, `VM`, `XML`, `XMPP`, `XSRF`, `XSS`, `SIP`, `RTP`, `AMQP`, `DB`, `TS`

**经典案例**：
```go
// 错误写法
var userId int64
func GetUserId() int64 { return 0 }
func ParseXmlData() {}

// 正确写法
var userID int64
func GetUserID() int64 { return 0 }
func ParseXMLData() {}
```

**不应报告的场景**：非导出标识符中缩写词作首部时全小写是正确的（如 `httpServer`、`urlPath`）。

---

### 2. GoRule002 ErrVarPrefix - error 类型的顶级变量必须添加 err 或 Err 前缀 [Critical]

**缺陷描述**：包级别（顶级）的 `error` 类型变量，导出变量使用 `Err` 前缀，包内私有变量使用 `err` 前缀。

**经典案例**：
```go
// 错误写法
var NotFound = errors.New("not found")
var invalidInput = errors.New("invalid input")

// 正确写法
var ErrNotFound = errors.New("not found")
var errInvalidInput = errors.New("invalid input")
```

**不应报告的场景**：函数内部的局部 error 变量不受此规则约束。

---

### 3. GoRule004 ReceiverName - receiver 的名称应该简短且保持一致 [Critical]

**缺陷描述**：方法的接收者名称应简短（通常取类型名首字母），且同一类型的所有方法中接收者名称必须保持一致。不得使用 `this`、`self` 等。

**经典案例**：
```go
// 错误写法
func (client *Client) GetName() string { return client.name }  // 名称过长
func (c *Client) GetName() string { return c.name }
func (cli *Client) SetName(name string) { cli.name = name }    // 不一致
func (this *Server) Start() error { return nil }               // 禁用 this/self

// 正确写法
func (c *Client) GetName() string { return c.name }
func (c *Client) SetName(name string) { c.name = name }
func (s *Server) Start() error { return nil }
```

---

### 4. GoRule006 NoPkgNamePrefix - 包内类型不应以包名为前缀 [Critical]

**缺陷描述**：包内的 struct、函数等，不应再以包名作为前缀，否则调用方会出现冗余（如 `net.NetDial`）。

**经典案例**：
```go
// 错误写法（package: net）
type NetAddr struct{}    // 调用方：net.NetAddr（冗余）
func UserCreate() {}     // 调用方：user.UserCreate（冗余）

// 正确写法
type Addr struct{}       // 调用方：net.Addr
func Create() {}         // 调用方：user.Create
```

---

## 二、格式规则（3项）

### 5. GoRule102 UTF8Encoding - 所有源文件编码必须是 UTF-8 [Critical]

**缺陷描述**：Go 只能处理 UTF-8 编码的源文件。使用 GBK、GB2312、Latin-1 等其他编码会导致编译失败或乱码。

**不应报告的场景**：纯 ASCII 内容的文件（无法判断编码时不报告）。

---

### 6. GoRule103 LineLength - 每行代码不超过 160 个字符 [Critical]

**缺陷描述**：单行字符数不超过 160 个字符，超出需要换行。Tab 按 1 个字符计算。

**豁免场景**：包含 URL 的行；RSA 密钥等不可拆分的字符串字面量。

---

### 7. GoRule301 GofmtFormat - 使用 tab 进行缩进，.go 文件应统一格式化 [Critical]

**缺陷描述**：Go 代码使用 `tab` 进行缩进，所有 `.go` 文件应通过格式化工具（如 `gofmt`）统一格式化。

**推荐工具**：`gorgeous`、`gofumpt`、`gofmt -w -s`、`goimports`

**经典案例**：
```go
// 错误写法（使用空格缩进）
func main() {
    if true {
        fmt.Println("hello")
    }
}

// 正确写法（使用 tab 缩进）
func main() {
	if true {
		fmt.Println("hello")
	}
}
```

---

## 三、Import 规则（3项）

### 8. GoRule307 ImportGroupOrder - import 按标准库、第三方库、项目自身库分组排列 [Critical]

**缺陷描述**：import 按 **标准库 → 第三方库 → 项目自身库** 顺序分三组排列，每组之间用一个空行分隔，组内按字典序升序排列。

**经典案例**：
```go
// 错误写法
import (
    "fmt"
    "github.com/some/thirdparty"
    "context"
    "your.company.com/yourproject/pkg"
    "strings"
)

// 正确写法
import (
    "context"
    "fmt"
    "strings"

    "github.com/some/thirdparty"

    "your.company.com/yourproject/pkg"
)
```

**不应报告的场景**：只有一组 import（全是标准库或全是第三方库）时无需分组。

---

### 9. GoRule308 NoDotImport - 禁止使用点号格式 import [Critical]

**缺陷描述**：禁止使用 `. "pkg"` 格式的 import。点号导入会将包的所有导出标识符注入当前命名空间，使代码阅读者无法判断标识符来源。

**经典案例**：
```go
// 错误写法
import . "fmt"
import . "your.company.com/yourproject/models"

// 正确写法
import "your.company.com/yourproject/models"
user := models.User{Name: "Alice"}
```

---

### 10. GoRule309 BlankImportComment - 使用 "_" import 的包需要添加注释说明原因 [Critical]

**缺陷描述**：使用空白标识符 `_` 导入包时，必须添加注释说明导入原因（通常是为了执行包的 `init()` 函数）。

**经典案例**：
```go
// 错误写法
import (
    _ "github.com/go-sql-driver/mysql"
    _ "image/jpeg"
)

// 正确写法
import (
    _ "github.com/go-sql-driver/mysql" // 注册 MySQL driver
    _ "image/jpeg"                      // 注册 JPEG 解码器
)
```

---

## 四、错误处理规则（4项）

### 11. GoRule201 GoVetCheck - 文件应通过 go vet 的检查 [Critical]

**缺陷描述**：所有代码必须通过 `go vet ./...` 检查，无报错。主要检查项：

| 检查项 | 说明 |
|--------|------|
| copy locks | 复制了含锁的结构体，可能引发死锁 |
| loop closure | goroutine 中错误引用循环变量 |
| lost cancel | context.WithCancel 返回的 cancel 函数未被调用 |
| struct tag | struct 的 tag 格式不标准 |
| printf | printf 系列函数的格式串与参数不匹配 |

**经典案例**：
```go
// 错误写法 — copy locks
func doWork(c SafeCounter) { c.mu.Lock(); ... }  // 传值复制了锁

// 正确写法
func doWork(c *SafeCounter) { c.mu.Lock(); ... } // 传指针

// 错误写法 — lost cancel
ctx, _ := context.WithCancel(context.Background()) // cancel 未调用

// 正确写法
ctx, cancel := context.WithCancel(context.Background())
defer cancel()
```

---

### 12. GoRule202 NoBoolCompare - 禁止在 if、for 中对 bool 类型进行等值判断 [Critical]

**缺陷描述**：`if`/`for` 中直接使用 bool 值作为条件，无需与 `true` 或 `false` 进行显式比较。

**经典案例**：
```go
// 错误写法
if isValid == true { process() }
if hasError == false { continue }

// 正确写法
if isValid { process() }
if !hasError { continue }
```

---

### 13. GoRule204 ErrorLastReturn - error 类型始终放在返回参数末尾 [Critical]

**缺陷描述**：当函数有多个返回值且包含 `error` 类型时，`error` 必须作为最后一个返回参数。

**经典案例**：
```go
// 错误写法
func GetUser(id int) (error, *User) { ... }

// 正确写法
func GetUser(id int) (*User, error) { ... }
```

---

### 14. GoRule205 HandleError - 函数返回值中的 error 必须处理，defer 调用除外 [Critical]

**缺陷描述**：函数返回的 `error` 必须判断处理。若确实要忽略，应使用 `_ = f()` 显式忽略，而非直接丢弃。

**经典案例**：
```go
// 错误写法
os.Remove(tmpFile)     // error 被丢弃
json.Marshal(data)     // error 被丢弃

// 正确写法
if err := os.Remove(tmpFile); err != nil {
    log.Warnf("remove tmp file failed: %v", err)
}
// 或明确忽略
_ = writer.Close()
```

---

### 15. GoRule206 WrapErrorWithW - 包装 error 时应使用 fmt.Errorf 配合 %w [Critical]

**缺陷描述**：包装 error 时，应使用 `fmt.Errorf("...: %w", err)` 而非 `%s`/`%v`。使用 `%w` 包装的 error 可通过 `errors.Is()` 和 `errors.As()` 进行类型判断和解包。

**经典案例**：
```go
// 错误写法
return fmt.Errorf("query user failed: %s", err.Error())  // 丢失类型信息
return fmt.Errorf("connect failed: %v", err)

// 正确写法
return fmt.Errorf("query user failed, id=%d: %w", id, err)
```

**不应报告的场景**：`errors.New` 和不带 `err` 参数的 `fmt.Errorf` 是创建新 error，不是包装。

---

## 五、Error String 规则（1项）

### 16. GoRule310 ErrorStringFormat - error string 不得以大写字母开头，结尾不带标点符号 [Critical]

**缺陷描述**：错误字符串（传给 `errors.New`、`fmt.Errorf` 的字面量）：首字母不得大写（专有名词除外）；结尾不得带标点符号（句号、感叹号、问号）。

**经典案例**：
```go
// 错误写法
errors.New("Something went wrong")
fmt.Errorf("User not found, id=%d", id)
errors.New("invalid input.")

// 正确写法
errors.New("something went wrong")
fmt.Errorf("user not found, id=%d", id)
errors.New("invalid input")
```

**不应报告的场景**：专有名词（如 MySQL、Redis）可以首字母大写；普通日志字符串不受约束。

---

## 六、编程实践规则（1项）

### 17. GoRule203 NoElseAfterReturn - 当 if 块以 return 结尾时，应删除 else 语句 [Critical]

**缺陷描述**：当 `if` 分支以 `return`（或 `panic`、`continue`、`break`）结尾时，后续的 `else` 块是多余的，应直接去掉 `else`，将代码提升到外层（early return 风格）。

**经典案例**：
```go
// 错误写法
func validate(x int) error {
    if x < 0 {
        return errors.New("negative value")
    } else {
        return nil
    }
}

// 正确写法
func validate(x int) error {
    if x < 0 {
        return errors.New("negative value")
    }
    return nil
}
```

**不应报告的场景**：
- `if` 块不以 return/panic/continue/break 结尾时，`else` 是必要的
- `if-else if-else` 链中间的 `else` 不适用此规则
