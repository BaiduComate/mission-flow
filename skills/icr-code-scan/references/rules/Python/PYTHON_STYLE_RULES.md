# Python 代码风格扫描规则（共8条）

---

## 一、格式规则（4项）

### 1. PY023 LineLength - 每行不得超过120个字符 [Critical]

**缺陷描述**：单行字符数不超过 120 个字符，超出需要换行。

---

### 2. PY030 Whitespace - 逗号、分号、冒号前不加空格，后边加一个空格 [Critical]

**缺陷描述**：逗号（`,`）、分号（`;`）、冒号（`:`）前不加空格，其后需加一个空格。

**经典案例**：
```python
# 错误写法
x = [1 , 2 , 3]
d = {"key" : "value"}
x = [1,2,3]

# 正确写法
x = [1, 2, 3]
d = {"key": "value"}
```

**豁免场景**：切片中的冒号（`x[1:2]`）；字符串字面量内部；类型注解中的冒号。

---

### 3. PY031 WhitespaceAroundOperator - 所有二元运算符前后各加一个空格 [Critical]

**缺陷描述**：所有二元运算符（赋值、算术、比较、逻辑、位运算、类型注解箭头 `->` 等）前后均需各加一个空格。

**经典案例**：
```python
# 错误写法
x=1
if x>0 and y<10:
    pass
def get_name()->str:
    return self.name

# 正确写法
x = 1
if x > 0 and y < 10:
    pass
def get_name() -> str:
    return self.name
```

**豁免场景**：关键字参数或默认值中的等号（见 PY032）；一元运算符；切片中的冒号。

---

### 4. PY032 WhitespaceAroundNamedParameterEquals - 关键字参数或参数默认值里的等号前后不加空格 [Critical]

**缺陷描述**：函数定义中的默认参数值和函数调用中的关键字参数，其等号（`=`）前后不应加空格。

**经典案例**：
```python
# 错误写法
def func(x = 1, y = 2):
    pass
result = func(x = 10, y = 20)

# 正确写法
def func(x=1, y=2):
    pass
result = func(x=10, y=20)
```

**豁免场景**：带类型注解的默认参数（`def func(x: int = 1)` 中等号前后需加空格）。

---

## 二、文档规则（2项）

### 5. PY033 Docstring - 使用docstring描述module、function、class和method接口 [Critical]

**缺陷描述**：module、function、class 和 method 的接口必须使用 docstring 进行描述，格式为三个双引号（`"""`），不得使用单引号（`'''`）或 `//` 注释替代。

**重要说明**：
- **method 必须独立检查**：类中的每个方法都必须有独立的 docstring，类有 docstring 不豁免方法
- **不要跳过 class 内的方法**：遍历所有 `def` 时，需要特别关注缩进在 class 内部的方法

**经典案例**：
```python
# 错误写法 — 函数缺少docstring
def calculate_total(price, quantity, discount):
    return price * quantity * (1 - discount)

# 错误写法 — 使用单引号
def get_user(user_id):
    '''根据ID获取用户信息。'''
    return db.query(user_id)

# 错误写法 — 使用注释替代
def process_order(order_id):
    # 处理订单逻辑
    return get_order(order_id).process()

# 错误写法 — 类有docstring但方法缺失（常见漏检场景）
class DataProcessor:
    """数据处理器。"""

    def run(self):  # [DEFECT] 方法缺少docstring
        pass

    def validate(self, data):  # [DEFECT] 方法缺少docstring
        return data is not None

# 正确写法
def calculate_total(price, quantity, discount):
    """计算商品总价。"""
    return price * quantity * (1 - discount)

# 正确写法 — 类和方法都有docstring
class DataProcessor:
    """数据处理器。"""

    def run(self):
        """执行数据处理流程。"""
        pass

    def validate(self, data):
        """验证输入数据。"""
        return data is not None
```

**豁免场景**：`__init__` 方法（如果类已有 docstring）；`__str__`、`__repr__`、`__eq__`、`__hash__` 等魔术方法；一行体的简单 property。

---

### 6. PY034 DocstringContent - 接口docstring描述至少包括功能简介、参数、返回值 [Critical]

**缺陷描述**：函数和方法的 docstring 至少需要包含：功能简介、参数（Args）、返回值（Returns）。如果函数可能抛出异常，必须注明（Raises）。

**标准 docstring 格式**（Google 风格）：
```
"""功能简介。

Args:
    参数名 (类型): 参数描述。

Returns:
    类型: 返回值描述。

Raises:
    异常类型: 触发条件描述。
"""
```

**经典案例**：
```python
# 错误写法 — 只有功能简介，缺少参数和返回值
def get_user_by_id(user_id):
    """获取用户信息。"""
    return db.query(User).filter(User.id == user_id).first()

# 正确写法
def get_user_by_id(user_id):
    """根据用户ID查询用户信息。

    Args:
        user_id (int): 用户唯一标识符。

    Returns:
        User: 用户对象，若不存在则返回 None。
    """
    return db.query(User).filter(User.id == user_id).first()
```

**豁免场景**：无参数且无返回值的简单函数（只需功能简介）；`__init__` 方法（参数在类 docstring 中描述）。

---

## 三、编程实践规则（2项）

### 7. PY018 CompareToNone - 禁止使用==或!=判断表达式是否为None [Critical]

**缺陷描述**：判断对象是否为 `None` 时，禁止使用 `==` 或 `!=`，应使用 `is` 或 `is not`。

**经典案例**：
```python
# 错误写法
if result == None:
    return
if user != None and user.is_active:
    grant_access(user)

# 正确写法
if result is None:
    return
if user is not None and user.is_active:
    grant_access(user)
```

---

## 四、命名规则（1项）

### 8. PY039 ClassName - 类（包括异常）名使用首字母大写驼峰式命名 [Critical]

**缺陷描述**：类名必须使用首字母大写的驼峰式命名（PascalCase），匹配正则 `^[A-Z][a-zA-Z0-9]*$`。

**经典案例**：
```python
# 错误写法
class userService: pass
class user_service: pass
class invalidInputError(Exception): pass

# 正确写法
class UserService: pass
class InvalidInputError(Exception): pass
```

**核心原则：只报告能明确看到 `class` 关键字后的类名不符合大驼峰规范的情况。动态类创建等场景不报告。**
