# Python 正确性规则

静态模式可识别的确定性错误，单次执行可触发。

---

## 一、空值与类型安全（7项）

### CORRECTNESS_PY_01. 对 None 对象进行属性或方法调用 [Critical]
- **检测**：函数返回值可能为 None 时直接调用属性/方法，触发 `AttributeError`；`re.search()` 结果未判断
- **排除**：有 `if result:` 或 `if x is not None:` 检查

### CORRECTNESS_PY_02. 空集合首元素访问 [Critical]
- **检测**：`users[0]` 在可能为空列表时；`min([])`/`max([])` 空集合；`first, *rest = []` 空列表解包
- **排除**：有 `if users:` 检查；有长度验证

### CORRECTNESS_PY_03. 列表索引越界访问 [Critical]
- **检测**：`parts[2]` 等硬编码索引未校验长度；循环边界 `range(len(arr)+1)` 越界
- **排除**：有 `len()` 检查

### CORRECTNESS_PY_04. 字典键不存在错误 [Critical]
- **检测**：`data["key"]` 直接访问可能不存在的键，触发 `KeyError`；`os.environ["KEY"]` 未配置时崩溃
- **排除**：已用 `.get(key, default)`；已有 `key in dict` 检查

### CORRECTNESS_PY_05. 类型不匹配运算错误 [Critical]
- **检测**：字符串与数字拼接 `"text: " + count`；None 参与算术运算；列表与非列表 `+` 操作
- **排除**：有类型转换

### CORRECTNESS_PY_06. 解包数量不匹配 [Critical]
- **检测**：`x, y, z = line.split(",")` 但分割结果可能不足3个；数据库行列数与解包变量数不一致
- **排除**：有长度检查；使用 `*rest` 弹性解包

### CORRECTNESS_PY_07. 对 None 或非可迭代对象迭代 [Critical]
- **检测**：`for item in get_items()` 但函数可能返回 None；`for x in data.get("records")` 字段可能为 null
- **排除**：已用 `for item in (get_items() or [])` 等保护

---

## 二、数据结构操作错误（5项）

### CORRECTNESS_PY_08. 可变对象作为函数默认参数 [Critical]
- **检测**：`def f(items=[])` 或 `def f(config={})` —— 默认参数共享同一对象，多次调用互相污染

```python
def add_item(item, items=[]):  # 错误：每次调用共享同一 items
    items.append(item)
    return items
# 正确：items=None，函数内 if items is None: items = []
```

### CORRECTNESS_PY_09. 迭代列表时修改列表 [Critical]
- **检测**：for-each 遍历时 `list.remove(item)` 或 `del list[i]`，导致跳过元素；迭代字典时 `del dict[key]` 抛 RuntimeError
- **排除**：用列表推导式/`removeIf` 等安全方式

### CORRECTNESS_PY_10. 在哈希集合中使用可变对象 [Critical]
- **检测**：`set.add([1,2])` 或 `{[1]:v}` —— list/dict 不可哈希，触发 TypeError
- **排除**：已改用 tuple

### CORRECTNESS_PY_11. 使用 is 比较数值/字符串 [Critical]
- **检测**：`if a is 1000:` —— is 比较内存地址，小整数池外返回 False，应用 `==`
- **排除**：`is None`/`is not None` 是正确用法

### CORRECTNESS_PY_12. 闭包循环变量捕获陷阱 [Critical]
- **检测**：`[lambda: i for i in range(5)]` —— 所有 lambda 捕获同一变量引用，执行时都是最终值
- **排除**：已用默认参数固定值 `lambda i=i: i`

```python
# 错误写法 — 全部输出 4
funcs = [lambda: i for i in range(5)]
print(funcs[0]())  # 4，不是 0

# 正确写法 — 用默认参数固定值
funcs = [lambda i=i: i for i in range(5)]
print(funcs[0]())  # 0
```

---

## 三、异常处理错误（6项）

### CORRECTNESS_PY_13. 捕获所有异常隐藏真实错误 [Critical]
- **检测**：`except:` 裸异常或 `except Exception: pass` 吞掉所有错误，包括 KeyboardInterrupt；捕获后返回默认值隐藏错误
- **排除**：有充分日志；顶层框架兜底处理且已记录

### CORRECTNESS_PY_14. 异常后资源未清理 [Critical]
- **检测**：`lock.acquire()` 后无 try-finally，异常时锁未释放
- **排除**：已用 `with` 上下文管理器

### CORRECTNESS_PY_15. 静默忽略异常（except pass）[Critical]
- **检测**：`except SomeError: pass` 捕获后完全不处理，后续代码可能使用未定义变量

### CORRECTNESS_PY_16. finally 中 return 覆盖异常 [Critical]
- **检测**：`finally: return None` 覆盖 try 块中抛出的异常，异常消失

### CORRECTNESS_PY_17. JSON 序列化不支持的对象 [Critical]
- **检测**：`json.dumps` 包含 datetime/Decimal/自定义对象，触发 TypeError
- **排除**：有自定义 JSONEncoder；已序列化为基础类型

### CORRECTNESS_PY_18. assert 用于业务逻辑校验 [Critical]
- **检测**：`assert amount > 0` 用于业务规则校验，Python -O 优化模式下 assert 被移除失效
- **排除**：assert 仅用于开发期内部不变式断言

---

## 四、静态检查：参数与变量错误（9项）

### CORRECTNESS_PY_19. 访问未定义变量 [Critical]
- **检测**：使用了从未声明的变量名，触发 NameError；条件分支中部分路径未赋值就使用

### CORRECTNESS_PY_20. 访问未赋值的局部变量 [Critical]
- **检测**：局部变量在 try/except 的 except 分支中未赋值就在函数末尾使用，触发 UnboundLocalError

```python
# 错误写法 — except 分支没有给 result 赋值
def get_data():
    try:
        result = fetch()
    except NetworkError:
        log_error()   # result 未赋值
    return result     # UnboundLocalError！

# 正确写法
def get_data():
    result = None     # 先赋初始值
    try:
        result = fetch()
    except NetworkError:
        log_error()
    return result
```

### CORRECTNESS_PY_21. 调用函数时缺少必要参数 [Critical]
- **检测**：传入位置参数少于函数定义的必要参数数量，触发 TypeError

### CORRECTNESS_PY_22. 调用函数时传递参数过多 [Critical]
- **检测**：传入位置参数多于函数定义的参数数量，触发 TypeError

### CORRECTNESS_PY_23. 重复传递关键字参数 [Critical]
- **检测**：同一参数通过位置和关键字两种方式传递，触发 TypeError

### CORRECTNESS_PY_24. 函数参数名重复定义 [Critical]
- **检测**：`def f(x, y, x)` 参数名重复，触发 SyntaxError

### CORRECTNESS_PY_25. 实例方法缺少 self 参数 [Critical]
- **检测**：类中实例方法第一个参数（self）缺失，调用时触发 TypeError

### CORRECTNESS_PY_26. __all__ 中引用未定义变量 [Critical]
- **检测**：`__all__` 列表包含模块中不存在的名称

### CORRECTNESS_PY_27. 实例成员在赋值前被访问 [Critical]
- **检测**：`__init__` 中先调用方法再赋值属性，方法中访问了尚未赋值的 self 属性

```python
# 错误写法 — setup() 访问 self.config，但此时尚未赋值
class Service:
    def __init__(self):
        self.setup()          # setup 中访问 self.config
        self.config = {}      # 赋值在 setup 之后

    def setup(self):
        print(self.config)    # AttributeError: 'Service' has no attribute 'config'

# 正确写法 — 先赋值再调用
class Service:
    def __init__(self):
        self.config = {}
        self.setup()
```

---

## 五、静态检查：格式化字符串（4项）

### CORRECTNESS_PY_28. 格式化字符串参数过多/过少 [Critical]
- **检测**：`%` 格式化提供的参数个数与占位符数量不符，触发 TypeError

### CORRECTNESS_PY_29. 不支持的格式化字符 [Critical]
- **检测**：`%q`/`%h` 等不受支持的格式符，触发 ValueError

### CORRECTNESS_PY_30. 格式化字符串不完整 [Critical]
- **检测**：`"Value: %"` 格式符不完整，触发 ValueError

### CORRECTNESS_PY_31. 对不支持下标访问的对象使用下标 [Critical]
- **检测**：对整数/None/set 使用 `[]`，触发 TypeError；`slice` 索引非整数触发 TypeError

---

## 六、静态检查：OOP 错误（5项）

### CORRECTNESS_PY_32. 实例化抽象类 [Critical]
- **检测**：直接实例化含未实现抽象方法的 ABCMeta 类，触发 TypeError

### CORRECTNESS_PY_33. 继承非类对象 [Critical]
- **检测**：继承函数/None/实例而非类，触发 TypeError

### CORRECTNESS_PY_34. 类 MRO 解析顺序不一致 [Critical]
- **检测**：多重继承中基类顺序冲突，无法确定 MRO，触发 TypeError

### CORRECTNESS_PY_35. 错误使用 NotImplemented 代替 NotImplementedError [Critical]
- **检测**：`raise NotImplemented` —— NotImplemented 是常量非异常，应用 `raise NotImplementedError`

### CORRECTNESS_PY_36. break/continue 在循环外使用 [Critical]
- **检测**：`break`/`continue` 出现在函数体或模块顶层而非循环内，触发 SyntaxError

---

## 七、静态检查：控制流（3项）

### CORRECTNESS_PY_37. return 在函数外使用 [Critical]
- **检测**：`return` 出现在模块级或类定义外，触发 SyntaxError；缩进错误导致 return 跑出方法

### CORRECTNESS_PY_38. continue 在 finally 中使用 [Critical]
- **检测**：`finally: continue` 抑制异常（3.8+语法合法但语义危险）；3.7及以下为 SyntaxError

### CORRECTNESS_PY_39. except 捕获顺序不当 [Critical]
- **检测**：通用异常（Exception）在具体异常（ValueError）之前，导致具体处理永不执行

---

## 八、数据处理错误（2项）

### CORRECTNESS_PY_40. 除零错误未处理 [Critical]
- **检测**：除法操作未检查除数为 0，触发 ZeroDivisionError
- **排除**：有 `if count != 0:` 检查；有 try-except ZeroDivisionError

### CORRECTNESS_PY_41. 字符串编码解码错误 [Critical]
- **检测**：字节流按错误编码（如 utf-8 解码 GBK 数据），触发 UnicodeDecodeError
- **排除**：有 `errors='ignore'/'replace'` 参数；有编码检测

---

## 九、其他（1项）

### CORRECTNESS_PY_42. __len__ 返回非负整数 [Critical]
- **检测**：`__len__` 方法返回负数、浮点数或 None，触发 ValueError/TypeError

```python
# 错误写法 — 返回负数
class MyList:
    def __len__(self):
        return -1        # ValueError: __len__() should return >= 0

# 错误写法 — 返回浮点数
class MyList:
    def __len__(self):
        return 1.5       # TypeError: 'float' object cannot be interpreted as an integer

# 正确写法
class MyList:
    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)  # 返回非负整数
```
