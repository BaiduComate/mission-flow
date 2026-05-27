# JavaScript/TypeScript 正确性规则

静态模式可识别的确定性错误，仅看代码结构即可判断，单次执行可触发。

---

## 一、控制流与逻辑错误（9项）

### CORRECTNESS_JS_01. 条件表达式中出现赋值操作符 [Critical]
- **检测**：`if`/`while`/`for` 条件中使用 `=` 而非 `===`/`==`，导致条件判断逻辑错误或死循环
- **排除**：有注释明确说明意图是赋值后判断；`while (item = queue.shift())` 等惯用模式

```javascript
// 错误写法
if (x = 1) { ... }        // 永远为 true
while (data = fetch()) {}  // 非惯用模式，易误读

// 排除场景（允许的惯用模式）
while (item = queue.shift()) { process(item); } // 已知惯用，可排除
```

### CORRECTNESS_JS_02. 正则表达式中使用控制字符 [Critical]
- **检测**：正则表达式中包含控制字符（如 `\t`、`\n` 等不可见字符），可能导致匹配行为不可预测或 ReDoS
- **排除**：显式使用 `\t`、`\n` 转义序列（非字面控制字符）

### CORRECTNESS_JS_03. finally 块中使用控制流语句 [Critical]
- **检测**：`finally` 中使用 `return`/`throw`/`break`/`continue`，导致 `try`/`catch` 中的原始返回值或异常被覆盖丢失
- **排除**：无正当场景

```javascript
function getData() {
    try { throw new Error('原始错误'); }
    finally { return 'fallback'; } // 原始异常被吞没，调用方拿到 'fallback'
}
```

### CORRECTNESS_JS_04. 否定关系运算符左操作数 [Critical]
- **检测**：`!key in object` 因运算符优先级实际执行为 `(!key) in object`，与 `!(key in object)` 语义不同
- **排除**：已用括号明确优先级

```javascript
// 错误写法 — 实际执行 (!key) in obj，即 false in obj
if (!key in obj) { ... }

// 正确写法
if (!(key in obj)) { ... }
```

### CORRECTNESS_JS_05. 无限循环 [Critical]
- **检测**：循环条件永真且循环体内无 `break`/`return`，或循环变量在循环体内未被更新
- **排除**：`while(true)` 内有明确 `break`/`return` 退出逻辑

### CORRECTNESS_JS_06. 无限递归 / 缺少递归基准条件 [Critical]
- **检测**：递归函数无终止条件，或终止条件在某些输入下（如负数）永不可达
- **排除**：有充分的终止条件覆盖所有输入范围

### CORRECTNESS_JS_07. 错误的逻辑运算符 [Critical]
- **检测**：布尔表达式使用 `&&` 但语义需要 `||`（或反之），导致条件永真/永假，如 `type === 'a' && type === 'b'`
- **排除**：逻辑正确

### CORRECTNESS_JS_08. `||` 短路误用导致 falsy 值被覆盖 [Critical]
- **检测**：`const x = options.value || default`，当 `options.value` 为 `0`/`false`/`""` 时被错误替换为默认值
- **排除**：确认不存在合法 falsy 值的场景；已改用 `??`

```javascript
// 错误写法 — count=0 时被覆盖为 10
const count = options.count || 10;

// 正确写法 — ?? 只在 null/undefined 时取默认值
const count = options.count ?? 10;
```

### CORRECTNESS_JS_09. 一成不变的循环条件（死循环/无效循环）[Critical]
- **检测**：循环条件中的变量在循环体内从未被修改，导致死循环或循环体永不执行
- **排除**：`while(true)` 内有退出逻辑

---

## 二、类型与访问错误（7项）

### CORRECTNESS_JS_10. 错误的数组索引访问 [Critical]
- **检测**：使用动态索引访问数组时未做范围校验；直接 `arr[arr.length]`；外部输入索引未校验
- **排除**：有长度检查；索引来源可信且范围有界

### CORRECTNESS_JS_11. 对象属性链式访问未判空 [Critical]
- **检测**：`a.b.c` 形式的链式访问，中间节点可能为 `null`/`undefined`，未使用 `?.` 可选链或判空
- **排除**：上下文保证对象非空；已使用 `?.`

```javascript
const city = user.address.city; // user 或 address 可能为 undefined
// 正确：user?.address?.city
```

### CORRECTNESS_JS_12. 异步结果未 await 直接使用 [Critical]
- **检测**：async 函数返回 Promise 但被当作同步值使用（缺少 `await`）；在 `async` 函数中调用异步函数未 await

```javascript
async function init() {
    const result = fetchUser(); // 未 await，result 是 Promise 对象
    displayUser(result);
}
```

### CORRECTNESS_JS_13. 函数调用依赖顺序错误 [Critical]
- **检测**：后续函数使用了前一个尚未完成的异步操作的结果，缺少 `await` 或回调处理
- **排除**：结果来自同步函数

### CORRECTNESS_JS_14. 变量未定义直接使用 [Critical]
- **检测**：使用了未通过 `var`/`let`/`const` 声明的变量，导致 `ReferenceError`
- **排除**：全局变量已在其他文件声明；框架注入的全局变量

### CORRECTNESS_JS_15. 循环引用导致 JSON 序列化失败 [Critical]
- **检测**：两个或多个对象相互引用形成环，在 `JSON.stringify` 时抛出循环引用错误，或导致内存泄漏
- **排除**：有自定义 replacer 处理循环引用

### CORRECTNESS_JS_16. 无效的 JSDoc 注释 [Critical]
- **检测**：JSDoc 中 `@param` 参数名与函数实际参数名不一致；`@returns` 标注了返回值但函数无 return；`@param` 数量与实际参数数量不符
- **排除**：参数名确实一致；无返回值函数不标 @returns

```javascript
// 错误写法 — @param 名称与实际参数不匹配
/**
 * @param {string} usre - 用户名  ← 应为 user
 * @returns {boolean}             ← 函数实际无返回值
 */
function login(user) {
    doLogin(user);
}
```

---

## 三、Vue 框架缺陷（8项）

### CORRECTNESS_VUE_01. 模板中使用未定义变量 [Critical]
- **检测**：Vue 模板中引用了未在 `data`/`props`/`computed`/`methods` 中定义的变量，导致渲染错误

### CORRECTNESS_VUE_02. created 生命周期中访问 DOM [Critical]
- **检测**：在 `created` 钩子中使用 `$refs` 或 `document.querySelector`，此时 DOM 尚未挂载
- **排除**：已改在 `mounted` 中访问

### CORRECTNESS_VUE_03. computed 中修改响应式数据 [Critical]
- **检测**：计算属性函数体内修改 `this.xxx`（data 或其他状态），违反响应式原则，可能导致无限更新

### CORRECTNESS_VUE_04. watch 中修改被观察的值导致无限循环 [Critical]
- **检测**：`watch` 回调中直接修改被监听的同一属性，触发再次 watch，形成无限循环

### CORRECTNESS_VUE_05. setup 中直接修改 props [Critical]
- **检测**：`setup(props)` 中对 props 属性直接赋值，违反单向数据流，应通过 emit 通知父组件

### CORRECTNESS_VUE_06. 组件 data 不是函数 [Critical]
- **检测**：组件选项中 `data` 直接返回对象而非函数，导致多个实例共享同一数据对象

```javascript
// 错误写法 — 所有实例共享同一个对象
export default {
    data: {count: 0}
};

// 正确写法 — 每个实例有独立数据
export default {
    data() { return {count: 0}; }
};
```

### CORRECTNESS_VUE_07. computed 没有 return 语句 [Critical]
- **检测**：计算属性函数体内有计算逻辑但缺少 `return`，导致值为 `undefined`

### CORRECTNESS_VUE_08. 绑定未定义的事件处理函数 [Critical]
- **检测**：`@click="method"` 但 `method` 未在 `methods` 中定义，点击时报错

---

## 四、React 框架缺陷（9项）

### CORRECTNESS_REACT_01. useEffect 依赖数组缺失或不完整 [Critical]
- **检测**：`useEffect` 无依赖数组（每次渲染都执行）；或依赖数组缺少实际使用的变量（闭包陷阱）
- **排除**：刻意设计为每次渲染执行且有注释说明

```javascript
useEffect(() => { document.title = count; }); // 缺少 [count]
```

### CORRECTNESS_REACT_02. 直接修改 state [Critical]
- **检测**：`this.state.x = value` 或对 useState 返回的数组/对象直接 `push`/赋值，React 无法检测变化
- **排除**：使用了 `setState`/`dispatch`/setter 函数

### CORRECTNESS_REACT_03. render/函数组件主体中调用 setState [Critical]
- **检测**：在 `render()` 方法或函数组件主体（非事件处理、非 effect）中直接调用 `setState`，导致无限渲染循环

### CORRECTNESS_REACT_04. useEffect 直接使用 async 函数 [Critical]
- **检测**：`useEffect(async () => {...})` —— cleanup 返回值为 Promise 而非函数，行为异常
- **排除**：已在 effect 内部定义 async 函数后调用

```javascript
// 错误写法 — cleanup 收到 Promise 而非清理函数
useEffect(async () => {
    const data = await fetchData();
    setData(data);
}, []);

// 正确写法
useEffect(() => {
    const fetchAsync = async () => {
        const data = await fetchData();
        setData(data);
    };
    fetchAsync();
}, []);
```

### CORRECTNESS_REACT_05. useEffect 未清理订阅/定时器 [Critical]
- **检测**：`useEffect` 中注册了 `addEventListener`/`setInterval`/订阅，但未返回清理函数
- **排除**：有 return `() => { ... }` 清理逻辑

### CORRECTNESS_REACT_06. useCallback/useMemo 依赖数组缺失 [Critical]
- **检测**：`useCallback`/`useMemo` 的依赖数组未包含回调中使用的外部变量，导致闭包陷阱
- **排除**：变量确实不需要触发重新创建

### CORRECTNESS_REACT_07. Hook 在条件/循环中调用 [Critical]
- **检测**：`useState`/`useReducer`/`useEffect` 等 Hook 在 `if`/`for`/嵌套函数中调用，违反 Hook 规则

### CORRECTNESS_REACT_08. useLayoutEffect 在服务端使用 [Critical]
- **检测**：SSR 场景中使用 `useLayoutEffect`，服务端不执行 DOM 操作，产生警告
- **排除**：有 `typeof window !== 'undefined'` 保护；纯客户端渲染

### CORRECTNESS_REACT_09. useEffect 异步请求未处理组件卸载 [Critical]
- **检测**：`useEffect` 内部发起异步请求，但未在 cleanup 中设置取消标志或 AbortController，组件卸载后仍调用 `setState`

```javascript
// 错误写法 — 组件卸载后仍 setState
useEffect(() => {
    fetch('/api/data').then(res => res.json()).then(setData);
}, []);

// 正确写法 — AbortController 取消请求
useEffect(() => {
    const controller = new AbortController();
    fetch('/api/data', {signal: controller.signal})
        .then(res => res.json()).then(setData)
        .catch(err => { if (err.name !== 'AbortError') throw err; });
    return () => controller.abort();
}, []);
```

---

## 五、坏习惯与 ES6 规范问题（13项）

> 原属规范类，因会引发实际逻辑隐患或运行错误，归入缺陷类一并扫描。

### CORRECTNESS_JS_HABIT_01. case 子句中使用词法声明 [Critical]
- **检测**：switch 的 case 子句中使用 `let`/`const` 且无 `{}` 块包裹，作用域贯穿整个 switch，可能导致重复声明报错

```javascript
// 错误写法
switch (type) {
    case 'a':
        let msg = 'hello'; // 作用域泄漏到整个 switch
        break;
    case 'b':
        let msg = 'world'; // SyntaxError: already been declared
}

// 正确写法 — 用 {} 包裹
switch (type) {
    case 'a': {
        let msg = 'hello';
        break;
    }
}
```

### CORRECTNESS_JS_HABIT_02. 使用空解构模式 [Critical]
- **检测**：`const {} = obj` 或 `const [] = arr` 等空解构，无实际意义

### CORRECTNESS_JS_HABIT_03. 宽松相等与 null 比较 [Critical]
- **检测**：`value == null` 宽松比较同时匹配 null 和 undefined，通常非预期
- **排除**：明确需要同时判断 null/undefined 且已知的场景

### CORRECTNESS_JS_HABIT_04. 魔术数字 [Critical]
- **检测**：代码中直接出现无命名的数字常量（如 `status === 1`），含义不明
- **排除**：0、1、-1 等通用数字；数组索引；明确语境下的简单值

### CORRECTNESS_JS_HABIT_05. 自我赋值 [Critical]
- **检测**：`x = x`、`arr[i] = arr[i]` 等无操作的自我赋值，可能掩盖真实 bug

### CORRECTNESS_JS_HABIT_06. 一成不变的循环条件 [Critical]
- **检测**：循环条件中的变量在循环体内从未被修改，导致死循环或循环体永不执行
- **排除**：`while(true)` 内部有明确 break/return 逻辑

### CORRECTNESS_JS_HABIT_07. 将 undefined 作为标识符 [Critical]
- **检测**：函数参数名或变量名使用 `undefined`，覆盖全局 undefined 导致判断失效

```javascript
// 错误写法 — undefined 被覆盖，typeof undefined === 'string'
function check(undefined) {
    if (x === undefined) { ... } // 判断失效
}
```

### CORRECTNESS_JS_HABIT_08. function 声明与表达式风格不一致 [Critical]
- **检测**：同文件中混用 `function foo(){}` 声明和 `const bar = () => {}` 表达式，风格不统一
- **排除**：有意区分提升特性的场景

### CORRECTNESS_JS_HABIT_09. 行注释位置不规范 [Critical]
- **检测**：行注释 `//` 位置不规范，影响可读性

### CORRECTNESS_JS_HABIT_10. 文件中使用制表符 [Critical]
- **检测**：代码缩进使用 Tab 字符与空格混用，不同编辑器显示不一致
- **排除**：项目统一使用 Tab 缩进

### CORRECTNESS_JS_HABIT_11. 对象字面量未使用简写语法 [Critical]
- **检测**：`{ method: function() {} }` 可简写为 `{ method() {} }`；`{ prop: prop }` 可简写为 `{ prop }`

### CORRECTNESS_JS_HABIT_12. 未用 const 声明不变变量 [Critical]
- **检测**：使用 `let` 声明但后续从未重新赋值的变量，语义上应为 `const`
- **排除**：循环变量；明确预留赋值位的变量

### CORRECTNESS_JS_HABIT_13. 字符串连接未使用模板字面量 [Critical]
- **检测**：使用 `+` 号拼接含变量的字符串，应改为模板字符串
- **排除**：纯静态字符串拼接（无变量）

---

## 六、正确性与逻辑（4项）

### CORRECTNESS_JS_COR_01. 正则表达式缺少锚点 [high]
- **检测**：用于输入校验的正则表达式缺少 `^` 和 `$` 锚点，导致部分匹配通过本应拒绝的字符串（如 `/<script>/` 匹配 `safe<script>attack`）
- **排除**：明确需要部分匹配场景（如搜索文本中提取内容）；已使用 `test()` 并知晓语义

```javascript
// 错误写法 — "123abc" 能通过纯数字校验
const isNum = /\d+/.test(input);

// 正确写法
const isNum = /^\d+$/.test(input);
```

### CORRECTNESS_JS_COR_02. 错误链断裂 [middle]
- **检测**：`throw new Error('操作失败')` 重新抛出错误时丢失原始 cause，导致上层无法溯源；应使用 `{ cause: originalError }` 或在 message 中保留原始信息
- **排除**：有意隐藏底层错误（如安全场景）；日志中已记录原始错误

```javascript
// 错误写法 — 原始 stack 丢失
} catch (e) {
    throw new Error('数据库写入失败'); // e 的信息消失
}

// 正确写法
} catch (e) {
    throw new Error('数据库写入失败', { cause: e });
}
```

### CORRECTNESS_JS_COR_03. 乐观更新未回滚 [middle]
- **检测**：UI 先乐观更新（修改 state/store），随后 API 调用失败后未将状态回滚到操作前的值
- **排除**：无乐观更新逻辑；失败后有明确回滚代码
- **复核**：确认存在"先改 state 再 await api"的模式；确认 catch 块中没有还原操作

### CORRECTNESS_JS_COR_04. 竞态条件：快速操作结果覆盖 [middle]
- **检测**：异步操作（如搜索、tab 切换、翻页）无取消前一次请求的机制，后发先至的响应会覆盖最新请求的结果
- **排除**：有 AbortController 取消；有请求序列号校验；有防抖/节流保证只发最后一次
- **复核**：确认存在用户可快速重复触发的场景；确认无序列号或取消逻辑
