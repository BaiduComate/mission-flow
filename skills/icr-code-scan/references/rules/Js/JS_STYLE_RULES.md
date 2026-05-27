# JavaScript/TypeScript 规范类规则

格式与代码风格规则，来源于 JAVASCRIPT_SMELL_LIST_details.md（共35条）。

---

### JS 通用规则

#### 1. no-trailing-spaces - 禁止行尾空白 [Critical]
**描述**：不允许在行尾出现空白字符（空格或制表符）。

#### 2. quotes - 引号风格 [Critical]
**描述**：强制使用单引号（`'`），只有在字符串本身包含单引号时才允许使用双引号转义。

```javascript
// 错误写法
const str = "hello";
const msg = "it's a test";

// 正确写法
const str = 'hello';
const msg = 'it\'s a test';
```

#### 3. semi - 分号要求 [Critical]
**描述**：要求每条语句后面必须使用分号（`;`）结尾。

#### 4. max-len - 行长度限制 [Critical]
**描述**：每行代码不得超过120个字符（URL除外）。

#### 5. curly - 花括号要求 [Critical]
**描述**：所有控制语句（`if`、`else`、`for`、`while`、`do`）都必须使用花括号包裹语句体，即使只有一行代码。

```javascript
// 错误写法
if (condition) doSomething();
for (let i = 0; i < 10; i++) console.log(i);

// 正确写法
if (condition) {
    doSomething();
}
for (let i = 0; i < 10; i++) {
    console.log(i);
}
```

#### 6. comma-dangle - 尾逗号规则 [Critical]
**描述**：多行数组、对象、导入、导出必须使用尾逗号；函数参数不允许使用尾逗号。

```javascript
// 错误写法 — 多行对象缺少尾逗号
const obj = {
    a: 1,
    b: 2
};

// 正确写法 — 多行必须有尾逗号
const obj = {
    a: 1,
    b: 2,
};

// 正确写法 — 单行无需尾逗号
const arr = [1, 2, 3];
```

#### 7. no-multi-spaces - 禁止多个连续空格 [Critical]
**描述**：不允许在代码中出现多个连续的空格（行尾注释前的空格和对象属性对齐除外）。

#### 8. comma-spacing - 逗号空格 [Critical]
**描述**：逗号前不允许有空格，逗号后必须有一个空格。

```javascript
// 错误写法
const arr = [1,2,3];
foo(1,2 ,3);

// 正确写法
const arr = [1, 2, 3];
foo(1, 2, 3);
```

#### 9. space-infix-ops - 运算符空格 [Critical]
**描述**：二元运算符（`+`, `-`, `*`, `/`, `=`, `==`, `===`, `!=`, `!==`, `<`, `>`, `<=`, `>=` 等）两侧必须有空格。

```javascript
// 错误写法
const x = 1+2*3;
if (a===b) {}

// 正确写法
const x = 1 + 2 * 3;
if (a === b) {}
```

#### 10. space-before-function-paren - 函数括号前空格 [Critical]
**描述**：匿名函数（箭头函数、function表达式）的括号前必须有空格；命名函数声明的括号前不允许有空格。

```javascript
// 错误写法
const foo = function() {};   // 匿名函数缺少空格
function test () {}          // 命名函数多余空格

// 正确写法
const foo = function () {};
function test() {}
```

#### 11. spaced-comment - 注释空格 [Critical]
**描述**：注释标记（`//` 或 `/*`）后必须有一个空格。

#### 12. key-spacing - 对象键空格 [Critical]
**描述**：对象字面量的冒号前不允许有空格，冒号后必须有一个空格。

```javascript
// 错误写法
const obj = {a :1, b : 2};

// 正确写法
const obj = {a: 1, b: 2};
```

#### 13. keyword-spacing - 关键字空格 [Critical]
**描述**：关键字（`if`, `else`, `for`, `while`, `do`, `switch`, `case`, `break`, `continue`, `return`, `try`, `catch`, `finally`, `throw`, `typeof`, `instanceof`, `new`, `delete`, `void`, `in`, `await`, `async` 等）前后必须有空格。

```javascript
// 错误写法
if(condition) {}
for(let i = 0; i < 10; i++) {}

// 正确写法
if (condition) {}
for (let i = 0; i < 10; i++) {}
```

#### 14. object-curly-spacing - 对象花括号空格 [Critical]
**描述**：对象字面量的花括号内部不允许有空格（使用 `never` 配置，`{a: 1}` 而非 `{ a: 1 }`）。

```javascript
// 错误写法
const obj = { a: 1, b: 2 };

// 正确写法
const obj = {a: 1, b: 2};
```

#### 15. dot-notation - 点号访问 [Critical]
**描述**：强制使用点号访问对象属性，仅当属性名包含特殊字符或使用变量时才允许使用方括号语法。

```javascript
// 错误写法
const name = user['name'];

// 正确写法
const name = user.name;
const value = obj['special-key'];  // 含特殊字符，允许方括号
const key = 'age';
const val = person[key];           // 动态变量，允许方括号
```

#### 16. space-before-blocks - 代码块前空格 [Critical]
**描述**：代码块（`{}`）前必须有一个空格。

```javascript
// 错误写法
if (condition){}
function test(){}

// 正确写法
if (condition) {}
function test() {}
```

#### 17. arrow-parens - 箭头函数参数括号 [Critical]
**描述**：仅在需要时使用箭头函数参数的括号（单个参数时省略括号，零个或多个参数时保留括号）。

```javascript
// 错误写法
const add = (a) => a + 1;   // 单参数不应有括号

// 正确写法
const add = a => a + 1;
const sum = (a, b) => a + b;
const greet = () => 'Hello';
```

#### 18. max-statements-per-line - 每行最多语句数 [Critical]
**描述**：每行只允许一条语句。

#### 19. eqeqeq - 严格相等比较 [Critical]
**描述**：必须使用严格相等（`===`）和严格不等（`!==`），禁止使用宽松相等（`==`）和不等（`!=`）。`null` 比较时忽略此规则。

```javascript
// 错误写法
if (name == 'John') {}
if (count != 0) {}

// 正确写法
if (name === 'John') {}
if (count !== 0) {}
if (value == null) {}  // null 比较时例外，允许同时匹配 null/undefined
```

#### 20. operator-linebreak - 运算符换行 [Critical]
**描述**：运算符换行时，运算符必须放在行的开头（不是结尾）。

```javascript
// 错误写法
const result = veryLongVariable +
               anotherLongVariable;

// 正确写法
const result = veryLongVariable
               + anotherLongVariable;
```

#### 21. no-mixed-spaces-and-tabs - 禁止混用空格和Tab [Critical]
**描述**：不允许在缩进中混用空格和制表符（Tab）。

#### 22. arrow-spacing - 箭头函数箭头空格 [Critical]
**描述**：箭头函数的箭头（`=>`）前后必须各有一个空格。

```javascript
// 错误写法
const add = (a, b)=>a + b;
const multiply = (x, y) =>x * y;

// 正确写法
const add = (a, b) => a + b;
```

#### 23. no-confusing-arrow - 禁止混淆箭头函数 [Critical]
**描述**：禁止使用可能与比较运算符混淆的箭头函数（如 `x => x === y`），建议使用括号区分（如 `x => (x === 0)`）。

```javascript
// 错误写法 — => 与比较运算符视觉上易混淆
const isZero = x => x === 0;
const isPositive = x => x > 0;

// 正确写法 — 加括号明确是箭头函数返回值
const isZero = x => (x === 0);
const isPositive = x => (x > 0);
```

#### 24. radix - parseInt 必须指定基数 [Critical]
**描述**：使用 `parseInt()` 时必须指定第二个参数（基数），如 `parseInt('10', 10)`。

```javascript
// 错误写法
const num = parseInt('10');

// 正确写法
const num = parseInt('10', 10);
const hex = parseInt('ff', 16);
```

---

### Vue 规则

#### 25. vue/max-attributes-per-line - 每行最多属性数 [Critical]
**描述**：单行标签最多2个属性，多行标签每行最多2个属性。

```html
<!-- 错误写法 — 超过2个属性未换行 -->
<MyComponent id="app" class="container" title="Hello" @click="handleClick" />

<!-- 正确写法 — 多属性时每行最多2个 -->
<MyComponent
    id="app" class="container"
    title="Hello" @click="handleClick"
/>
```

#### 26. vue/html-closing-bracket-newline - HTML闭合括号换行 [Critical]
**描述**：单行标签的闭合括号在同一行；多行标签的闭合括号单独占一行。

```html
<!-- 错误写法 — 多行标签的 > 不应缩进在属性后 -->
<MyComponent
    id="app"
    class="container"
    >

<!-- 正确写法 — 多行标签的 > 单独占一行顶格 -->
<MyComponent
    id="app"
    class="container"
>
```

#### 27. vue/attribute-hyphenation - Vue属性命名 [Critical]
**描述**：自定义组件的属性名必须使用短横线命名法（kebab-case）。

```html
<!-- 错误写法 -->
<MyComponent userName="John" maxCount="10" />

<!-- 正确写法 -->
<MyComponent user-name="John" max-count="10" />
```

#### 28. vue/no-unused-refs - 禁止未使用的ref [Critical]
**描述**：禁止声明但未使用的 ref 引用。

#### 29. vue/mustache-interpolation-spacing - 插值空格 [Critical]
**描述**：Mustache 插值表达式中的花括号内部必须有单个空格（`{{ message }}`）。

#### 30. vue/no-unused-vars - 禁止未使用的v-for变量 [Critical]
**描述**：禁止在 `v-for` 中声明但未使用的变量。

#### 31. vue/no-multiple-template-root - 禁止多个模板根元素 [Critical]
**描述**：Vue 2 的模板只能有一个根元素；Vue 3 允许多个根元素但此规则强制要求单一根元素。

#### 32. vue/html-button-has-type - 按钮必须有type属性 [Critical]
**描述**：`<button>` 元素必须显式指定 `type` 属性（button/submit/reset）。

---

### React 规则

#### 33. react/jsx-indent - JSX缩进 [Critical]
**描述**：JSX 元素必须使用4个空格缩进。

```jsx
// 错误写法（2空格）
<div>
  <span>Text</span>
</div>

// 正确写法（4空格）
<div>
    <span>Text</span>
</div>
```

---

### San 规则

#### 34. san/html-indent - HTML缩进 [Critical]
**描述**：San 模板中的 HTML 元素使用4个空格缩进（配置：4空格，attribute: 1, baseIndent: 1, closeBracket: 0）。

---

### CSS 规则

#### 35. rule-empty-line-before - 规则前空行 [Critical]
**描述**：CSS 规则（选择器块）之间需要空行分隔。
