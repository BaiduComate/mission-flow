# Java 正确性规则

静态模式可识别的确定性错误，单次执行可触发。

---

## 一、空指针异常（9项）

### CORRECTNESS_JAVA_01. 对象引用未判空直接调用 [Critical]
- **检测**：数据库/Map/远程调用返回值未判 null 直接调用方法，可能触发 NPE
- **排除**：有 null 判断；有 Optional 包裹；上下文保证非 null

### CORRECTNESS_JAVA_02. 包装类型自动拆箱导致空指针 [Critical]
- **检测**：Integer/Long/Boolean 等包装类可能为 null 时，直接参与算术运算、`if(flag)` 或三元表达式发生自动拆箱
- **排除**：有 null 检查；确认不会返回 null

### CORRECTNESS_JAVA_03. 级联调用链路中任一环节为空 [Critical]
- **检测**：`a.getB().getC().getName()` 形式的多级调用，任一层为 null 则 NPE；`Optional.get()` 未判断 `isPresent()`
- **排除**：有每层 null 检查；使用 `Optional.map` 链式调用

### CORRECTNESS_JAVA_04. 集合迭代时元素为 null 未处理 [Critical]
- **检测**：遍历 List/Stream 时元素可能为 null，直接调用方法
- **排除**：集合确保无 null 元素；有 `filter(Objects::nonNull)`

### CORRECTNESS_JAVA_05. equals 调用顺序导致空指针 [Critical]
- **检测**：`variable.equals("CONSTANT")` —— variable 可能为 null，应写成 `"CONSTANT".equals(variable)`
- **排除**：已知 variable 非 null

### CORRECTNESS_JAVA_06. Optional 使用不当 [Critical]
- **检测**：`Optional.get()` 未判断 `isPresent()`；`Optional.of(null)` 应用 `ofNullable`；`orElse(createObj())` 误用（会无条件执行创建对象）
- **排除**：已判断 `isPresent()`；已改用 `orElseGet`

```java
// 错误写法 — 无论是否需要，createDefault() 必定执行
String result = optional.orElse(createDefault());

// 正确写法 — 仅在 Optional 为空时执行
String result = optional.orElseGet(() -> createDefault());
```

### CORRECTNESS_JAVA_07. 隐式 toString 调用未判空 [Critical]
- **检测**：`obj.toString()` 或字符串拼接中 obj 可能为 null
- **排除**：已确认非 null

### CORRECTNESS_JAVA_08. @NonNull 方法返回值存在 null 分支 [Critical]
- **检测**：标注 `@NonNull`/`@NotNull` 的方法，存在 `return null` 的代码路径，违反非空契约

### CORRECTNESS_JAVA_09. @Nonnull 字段未在构造方法中初始化 [Critical]
- **检测**：标注 `@Nonnull` 的成员变量未在构造方法或静态代码块中赋值
- **排除**：通过 `@Autowired` 注入（Spring 管理）

---

## 二、集合使用错误（6项）

### CORRECTNESS_JAVA_10. 循环中修改集合导致 ConcurrentModificationException [Critical]
- **检测**：for-each 遍历集合时直接调用集合的 add/remove 方法
- **排除**：用 `Iterator.remove()`；用 `removeIf()`；用副本遍历

### CORRECTNESS_JAVA_11. Arrays.asList 返回的 List 不可修改 [Critical]
- **检测**：`Arrays.asList(...)` 返回后调用 add/remove，抛 `UnsupportedOperationException`
- **排除**：已用 `new ArrayList<>(Arrays.asList(...))`

### CORRECTNESS_JAVA_12. SubList 操作不当 [Critical]
- **检测**：`list.subList()` 后修改原 List，再操作 subList 抛 `ConcurrentModificationException`
- **排除**：已用 `new ArrayList<>(list.subList(...))`

### CORRECTNESS_JAVA_13. 可变对象作为 HashMap key [Critical]
- **检测**：将 List/自定义对象（未正确重写 hashCode/equals）作为 HashMap key，状态变化后无法 get/remove
- **排除**：对象不可变；对象重写了 hashCode/equals 且不会变化

### CORRECTNESS_JAVA_14. Integer 缓存范围外用 == 比较 [Critical]
- **检测**：Integer 变量用 `==` 比较，值可能超出 -128~127 缓存范围，返回 false
- **排除**：明确值在 -128~127 范围内；已用 `equals()`

```java
// 错误写法 — 超出缓存范围时 == 比较失败
Integer a = 200;
Integer b = 200;
if (a == b) { ... }  // false！

// 正确写法
if (a.equals(b)) { ... }  // true
```

### CORRECTNESS_JAVA_15. 集合 toArray 强转类型错误 [Critical]
- **检测**：`(String[]) list.toArray()` 抛 ClassCastException，应用 `list.toArray(new String[0])`

---

## 三、异常处理错误（5项）

### CORRECTNESS_JAVA_16. catch 后静默忽略不处理 [Critical]
- **检测**：`catch(Exception e) {}` 或 `catch(Exception e) { /* ignore */ }` 完全不记录日志也不抛出

### CORRECTNESS_JAVA_17. finally 中 return/throw 覆盖原始值 [Critical]
- **检测**：finally 块中 `return` 覆盖 try/catch 的返回值；finally 中 `throw` 覆盖原始异常

### CORRECTNESS_JAVA_18. catch 后继续执行导致数据不一致 [Critical]
- **检测**：捕获关键步骤（如扣款）的异常后仅记录日志，继续执行后续步骤（如发货），导致数据不一致
- **排除**：异常后有事务回滚；后续步骤有幂等保护

### CORRECTNESS_JAVA_19. catch 范围过于宽泛掩盖编程错误 [Critical]
- **检测**：catch Exception/Throwable 将 NPE、ClassCastException 等编程错误也捕获，返回默认值掩盖问题
- **排除**：顶层 controller/filter 兜底处理；有充分日志记录

### CORRECTNESS_JAVA_20. 无限递归导致 StackOverflowError [Critical]
- **检测**：递归无终止条件；终止条件在特定输入（负数/null）下不可达；toString/hashCode 相互调用形成无限递归
- **排除**：有充分的终止条件

---

## 四、数值与逻辑错误（7项）

### CORRECTNESS_JAVA_21. BigDecimal 用 double 构造导致精度丢失 [Critical]
- **检测**：`new BigDecimal(0.1)` 精度不准确，应用 `new BigDecimal("0.1")` 或 `BigDecimal.valueOf(0.1)`

### CORRECTNESS_JAVA_22. BigDecimal 除法未指定精度 [Critical]
- **检测**：`a.divide(b)` 结果为无限小数时抛 ArithmeticException
- **排除**：已指定 `scale` 和 `RoundingMode`

### CORRECTNESS_JAVA_23. BigDecimal 用 equals 比较忽略精度差异 [Critical]
- **检测**：`a.equals(b)` 比较 BigDecimal 时，`1.0` 不等于 `1.00`，金融场景应用 `compareTo`

### CORRECTNESS_JAVA_24. 整数溢出导致逻辑错误 [Critical]
- **检测**：int 类型大数乘法（如金额×数量）结果溢出变负数
- **排除**：已用 long；值域确认不会溢出

### CORRECTNESS_JAVA_25. switch 缺少 break 导致 fall-through [Critical]
- **检测**：case 分支缺少 break/return，穿透到下一 case 执行
- **排除**：有 `// fall through` 注释明确意图

```java
// 错误写法 — case 1 执行后穿透到 case 2
switch (status) {
    case 1:
        doA();      // 缺少 break，继续执行 case 2
    case 2:
        doB();
        break;
}

// 正确写法
switch (status) {
    case 1:
        doA();
        break;
    case 2:
        doB();
        break;
}
```

### CORRECTNESS_JAVA_26. 使用 == 比较字符串内容 [Critical]
- **检测**：`status == "SUCCESS"` 比较字符串引用，动态字符串场景返回 false
- **排除**：字符串字面量与字面量比较（编译期优化）

### CORRECTNESS_JAVA_27. equals/hashCode 实现不当 [Critical]
- **检测**：重写 equals 未同步重写 hashCode；equals 方法参数不是 Object 类型（实为重载非覆写）；破坏对称原则
- **排除**：Lombok @EqualsAndHashCode 等工具生成

---

## 五、代码静态检测（9项）

### CORRECTNESS_JAVA_28. 循环不应无限 [Critical]
- **检测**：`while(true)` 内无 break/return/throw；循环退出条件永不满足

### CORRECTNESS_JAVA_29. 不可变对象方法返回值被忽略 [Critical]
- **检测**：`String.trim()`/`replace()` 等不可变对象方法的返回值未赋值（原对象不变）

### CORRECTNESS_JAVA_30. read/readLine 返回值未使用 [Critical]
- **检测**：`InputStream.read(buffer)` 返回的实际读取字节数被忽略，可能处理不完整数据

### CORRECTNESS_JAVA_31. 对数组调用 toString/hashCode/equals [Critical]
- **检测**：`arr.toString()` 得到内存地址而非内容，应用 `Arrays.toString(arr)`

### CORRECTNESS_JAVA_32. PreparedStatement/ResultSet 索引越界 [Critical]
- **检测**：`setInt(2, ...)` 但 SQL 只有 1 个占位符；`ResultSet.getXxx()` 索引超出列数

### CORRECTNESS_JAVA_33. 子类覆写时参数类型来自不同 package [Critical]
- **检测**：子类方法与父类方法参数类型名相同但来自不同包，实为重载非覆写，调用时选择错误

```java
// 父类（父包）
package com.a;
public class Base {
    public void handle(com.a.Request req) { ... }
}

// 子类（子包）—— 错误写法，实为重载不是覆写
package com.b;
public class Child extends Base {
    public void handle(com.b.Request req) { ... } // Request 来自不同包
    // 调用 child.handle(aRequest) 实际仍走父类方法
}
```

### CORRECTNESS_JAVA_34. toString/clone 不应返回 null [Critical]
- **检测**：`toString()` 返回 null，字符串拼接时输出 "null" 或 NPE；`clone()` 返回 null 违反语义

### CORRECTNESS_JAVA_35. 集合强转未验证继承关系 [Critical]
- **检测**：`(String) map.get("key")` 类型未验证，可能 ClassCastException
- **排除**：类型已通过泛型保证；有 instanceof 检查

### CORRECTNESS_JAVA_36. 子类方法名与父类相同但非覆写 [Critical]
- **检测**：子类方法参数类型为父类对应类型的子类（如 ArrayList vs List），实为重载非覆写，需加 @Override 验证
