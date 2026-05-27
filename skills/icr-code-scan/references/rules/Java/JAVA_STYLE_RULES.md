# Java 代码风格扫描规则（共14条）

---

## 一、Import 规则（2项）

### 1. JAVA010 UnusedImports - 未使用的 import 必须删除 [Critical]

**缺陷描述**：所有未使用的 import 语句应该被删除。

**判定方法**：在 import 声明之后的整个文件正文中（包括代码、注解、泛型参数），搜索该 import 引入的**简单类名**（最后一个 `.` 之后的部分）。如果该简单类名在文件正文中**从未以独立标识符形式出现**，则判定为未使用。

**经典案例**：
```java
// 错误写法
import java.util.HashMap;  // 文件中从未使用 HashMap
import java.util.List;     // 文件中从未使用 List

public class Example {
    private String name;
}
```

**注意 — 以下场景中 import 视为「已使用」，不应报告**：类名出现在类型声明、注解、泛型参数、Javadoc（`@see`/`@link`）、throws 子句、静态方法调用、instanceof 中。

**核心原则：仅在确信类名在整个文件中完全不存在时才报告。如果无法确定，不报告。**

---

### 2. JAVA008 AvoidStarImport - 禁止通配符 import [Critical]

**缺陷描述**：非 static 的 import 语句，禁止使用通配符（`*`）导入。

**经典案例**：
```java
// 错误写法
import java.util.*;
import com.baidu.service.*;

// 正确写法
import java.util.List;
import java.util.Map;
```

**不应报告的场景**：`import static org.junit.Assert.*` 等 static import 不受此规则限制。

---

## 二、命名规则（3项）

### 3. JAVA028 MethodName - 方法名必须小驼峰 [Critical]

**缺陷描述**：方法名必须以小写字母开头，遵循驼峰命名方式，匹配正则 `^[a-z][a-zA-Z0-9]*$`。

**经典案例**：
```java
// 错误写法
public void GetUserName() {}   // Pascal 风格
public void get_user_name() {} // 蛇形命名
public void _init() {}         // 下划线开头

// 正确写法
public void getUserName() {}
public void init() {}
```

**不应报告的场景**：`@Test` 注解标记的测试方法；`@Override` 覆写父类/框架方法。

---

### 4. JAVA029 ConstantName - 常量命名必须全大写下划线分隔 [Critical]

**缺陷描述**：`static final` 修饰的基本类型或 String 字段（常量）命名全部大写，单词间用下划线隔开。

**「常量」判定标准**：同时满足：① `static final` 修饰；② 类型为基本数据类型或 String；③ 字段名不是 `serialVersionUID`。

**经典案例**：
```java
// 错误写法
public static final String max_count = "100";
public static final int defaultSize = 10;

// 正确写法
public static final String MAX_COUNT = "100";
public static final int DEFAULT_SIZE = 10;
```

**不应报告的场景**：Logger 对象、集合类型、工具对象、非 static 的 final 字段、枚举值、`serialVersionUID`（均不属于「常量」）。

---

### 5. JAVA032 PackageName - 包名只允许小写字母和数字 [Critical]

**缺陷描述**：包名统一使用小写，每个 `.` 分隔的片段只包含小写字母 `[a-z]` 和数字 `[0-9]`。

**经典案例**：
```java
// 错误写法
package com.baidu.UserService;
package com.baidu.user_service;

// 正确写法
package com.baidu.userservice;
package org.apache.logging.log4j;
```

---

## 三、格式规则（5项）

### 6. JAVA018 LineLength - 单行不超过120字符 [Critical]

**缺陷描述**：单行字符数不超过 120 个字符，超出需要换行。Tab 按 1 个字符计算。

---

### 7. JAVA003 FileTabCharacter - 禁止使用 Tab 字符 [Critical]

**缺陷描述**：缩进必须使用空格而不是 Tab（ASCII 0x09）。

**不应报告的场景**：字符串字面量内部的 `\t` 转义序列；无法确定是 Tab 还是空格时不报告。

---

### 8. JAVA014 LeftCurly - 左花括号遵循 K&R 风格 [Critical]

**缺陷描述**：左花括号 `{` 不单独另起一行，放在前一语句的行末（K&R 风格）。

**经典案例**：
```java
// 错误写法（Allman 风格）
public class Example
{
    public void method()
    {
        if (condition)
        {
            doSomething();
        }
    }
}

// 正确写法（K&R 风格）
public class Example {
    public void method() {
        if (condition) {
            doSomething();
        }
    }
}
```

**不应报告的场景**：空代码块 `{}` 可直接使用。

---

### 9. JAVA068 NeedBraces - if/else/for/while/do 必须使用花括号 [Critical]

**缺陷描述**：`if`、`else`、`for`、`while`、`do` 语句中即使只有一行代码也必须使用花括号。

**经典案例**：
```java
// 错误写法
if (condition) doSomething();
for (int i = 0; i < 10; i++) count++;

// 正确写法
if (condition) {
    doSomething();
}
for (int i = 0; i < 10; i++) {
    count++;
}
```

**不应报告的场景**：Lambda 表达式；switch-case 语句。

---

### 10. JAVA020 WhitespaceAround - 关键字和运算符周围空格 [Critical]

**缺陷描述**：以下位置必须加空格：① `if`/`for`/`while`/`switch` 等关键字与括号之间；② 左花括号 `{` 之前；③ 二元和三元运算符两边；④ 逗号后。

**经典案例**：
```java
// 错误写法
if(condition){}
int result=a+b;
method(a,b,c);

// 正确写法
if (condition) {}
int result = a + b;
method(a, b, c);
```

**核心原则：仅对上述 4 个场景中最明显的违规进行报告。对于不确定或边界情况，不报告。**

---

## 四、结构规则（1项）

### 11. JAVA013 OverloadMethodsDeclarationOrder - 重载方法必须相邻 [Critical]

**缺陷描述**：同名的构造函数或方法之间禁止插入其他成员，重载方法必须放在一起。

**经典案例**：
```java
// 错误写法
public class Example {
    public void process(String s) {}
    public void handle() {}          // 插入了其他方法
    public void process(int n) {}    // 与上面的 process 被隔开
}

// 正确写法
public class Example {
    public void process(String s) {}
    public void process(int n) {}    // 紧跟同名方法
    public void handle() {}
}
```

**不应报告的场景**：内部类中的同名方法与外部类独立判断；不同名方法之间的顺序不受约束。

---

## 五、注释规则（1项）

### 12. JAVA070 CommentsMustBeJavadocInSomeCase - 类/属性/方法注释必须用 Javadoc [Critical]

**缺陷描述**：所有类声明（含 public 和包级类）、public/protected 字段、public/protected 方法的注释必须使用 `/** 内容 */` 格式，不得使用 `// xxx` 方式。

**重要说明**：
- **方法必须独立检查**：类有 Javadoc 不豁免类中方法的注释要求，每个 public/protected 方法都必须有独立的 Javadoc
- **不要跳过类内的方法**：遍历所有方法声明时，需要特别关注类内部的方法是否缺少 `/** */` 格式注释
- **字段同样必须独立检查**：类有 Javadoc 不豁免字段的注释要求

**经典案例**：
```java
// 错误写法 — 类有Javadoc但方法缺失（常见漏检场景）
/** 用户服务类 */
public class UserService {
    public Order createOrder(OrderDTO dto) {}  // [DEFECT] public方法缺少Javadoc
    public User getUser(Long id) {}             // [DEFECT] public方法缺少Javadoc

    // 处理退款                            // [DEFECT] 使用 // 而非 /** */
    public void processRefund(Long orderId) {}
}

// 正确写法 — 类和方法都有Javadoc
/** 用户服务类 */
public class UserService {

    /** 创建订单 */
    public Order createOrder(OrderDTO dto) {}

    /** 根据ID获取用户 */
    public User getUser(Long id) {}

    /** 处理退款 */
    public void processRefund(Long orderId) {}
}

// 错误写法 — 使用 // 注释
// 用户服务类
public class UserService {}

// 辅助类：缺陷实现
class DefectExample {}

// 创建订单
public Order createOrder(OrderDTO dto) {}

// 正确写法
/** 用户服务类 */
public class UserService {}

/** 辅助类：缺陷实现 */
class DefectExample {}

/** 创建订单 */
public Order createOrder(OrderDTO dto) {}
```

**不应报告的场景**：分隔线注释（`// ===...===`）；行末尾的 `//` 注释（与代码同行，非独占一行描述用途的注释）；private 方法。

**核心原则：有 `//` 注释就算，不看内容。**

---

## 六、编程实践规则（2项）

### 13. JAVA044 ObjectEquals - equals 方法防空指针 [Critical]

**缺陷描述**：`Object.equals()` 方法容易抛空指针异常，应使用常量或确定有值的对象来调用 equals（字面量放左侧），或使用 `Objects.equals()`。

**判定方法**：检查 **变量在左、字符串字面量在右** 的 `.equals(字面量)` 模式。

**经典案例**：
```java
// 错误写法
if (name.equals("admin")) {}
if (status.equals("SUCCESS")) {}

// 正确写法
if ("admin".equals(name)) {}
if (Objects.equals(status, "SUCCESS")) {}
```

**不应报告的场景**：字面量已在左侧；使用 `Objects.equals`；两侧都是变量（`a.equals(b)`）；枚举类型比较。

**核心原则：只报告「变量.equals(字符串字面量)」的明确模式，其余情况不报告。**

---

### 14. JAVA041 OverrideWithAnnotation - 覆写方法必须加 @Override [Critical]

**缺陷描述**：所有覆写方法必须加 `@Override` 注解，防止方法签名拼写错误时编译器不报错。

**经典案例**：
```java
// 错误写法
public class User {
    public String toString() { return "User{" + name + "}"; }  // 缺少 @Override
    public boolean equals(Object o) { return this == o; }       // 缺少 @Override
}

// 正确写法
public class User {
    @Override
    public String toString() { return "User{" + name + "}"; }
    @Override
    public boolean equals(Object o) { return this == o; }
}
```

**不应报告的场景**：类没有 extends/implements 且方法名不是 Object 的标准方法；无法从当前文件确定是否为覆写方法。

**核心原则：只报告能高度确信是覆写方法（toString/equals/hashCode/clone/finalize，或有 super 调用）且缺少 @Override 的情况。**
