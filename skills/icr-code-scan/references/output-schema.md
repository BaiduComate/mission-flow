# SubAgent 输出格式规范

所有 Review SubAgent 必须按以下 JSON 格式输出审查结果，以便主控 Agent 进行合并和去重。

## JSON Schema

```json
{
  "reviewer": "reuse | style | correctness | reliability | custom",
  "summary": "本维度的整体评估，1-2 句话",
  "findings": [
    {
      "id": "R001",
      "severity": "P0 | P1 | P2 | P3",
      "category": "分类标识",
      "file": "相对路径/文件名",
      "line": 42,
      "endLine": 50,
      "title": "简短标题（10字以内）",
      "description": "问题的详细描述，说明为什么这是个问题",
      "suggestion": "具体的修复建议，包含代码示例（如适用）",
      "evidence": "支撑判断的证据，如已有函数的路径、调用链分析等"
    }
  ]
}
```

## 字段说明

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `reviewer` | string | 是 | 审查维度标识：`reuse` / `style` / `correctness` / `reliability` / `custom` / `meta` |
| `summary` | string | 是 | 本维度的整体评估摘要 |
| `findings` | array | 是 | 发现的问题列表，无问题时为空数组 `[]` |

### Finding 字段

| 字段 | 类型 | 必填 | 长度限制 | 说明 |
|------|------|------|----------|------|
| `id` | string | 是 | - | 问题编号 |
| `severity` | string | 是 | - | 严重等级：`P0` / `P1` / `P2` / `P3` |
| `locked` | boolean | 否 | - | `true` 表示该 finding 来自 `[Critical]` 标记规则，Meta-Review **禁止**对其执行 `adjust_severity` 操作；缺省或 `false` 时 Meta-Review 可自由调整 |
| `category` | string | 是 | - | 问题分类，见下方分类表 |
| `file` | string | 是 | - | 问题所在文件的相对路径 |
| `line` | number | 是 | - | 问题起始行号 |
| `endLine` | number | 否 | - | 问题结束行号（跨多行时提供） |
| `title` | string | 是 | ≤15字 | 简短标题，一目了然 |
| `description` | string | 是 | 1-2句话 | 说明风险和触发条件，不展开论证 |
| `suggestion` | string | 是 | 1-2句话 | 修复方向，只在关键处给代码片段 |
| `evidence` | string | 否 | 1句话 | 支撑证据（已有函数路径、调用链等） |

**长度要求**：SubAgent 输出的每个 finding 应尽量精简。`description` 和 `suggestion` 各控制在 1-2 句话以内，避免大段文字。主控 Agent 在最终报告中会进一步压缩为表格单行。

### Category 分类表

#### 复用审查 (reuse)
| category | 含义 |
|----------|------|
| `duplicate-function` | 与已有函数功能重复 |
| `inline-reimplementation` | 内联逻辑可用已有工具函数替代 |
| `similar-pattern` | 存在近似实现，建议考虑复用 |

#### 风格审查 (style)
| category | 含义 |
|----------|------|
| `code-format` | 格式类规则（空格、缩进、行长、分号、引号等） |
| `naming-convention` | 命名规范（类名、方法名、常量名、包名等） |
| `code-style` | 代码结构风格（花括号要求、操作符换行、箭头函数括号等） |
| `comment-style` | 注释规范（Docstring、Javadoc、注释空格等） |
| `vue-style` | Vue 模板专属规范（属性命名、插值空格、模板根元素等） |
| `react-style` | React/JSX 专属规范（JSX 缩进等） |

#### 正确性审查 (correctness)
| category | 含义 |
|----------|------|
| `null-safety` | 空值与类型安全（空指针、None 访问、空集合越界等） |
| `type-error` | 类型不匹配运算（字符串+数字、不可哈希对象等） |
| `data-structure` | 数据结构操作错误（迭代时修改、可变默认参数等） |
| `exception-handling` | 异常处理错误（吞异常、finally return、资源泄漏等） |
| `variable-param` | 变量/参数错误（未定义变量、参数数量不符、重复参数等） |
| `string-format` | 格式化字符串错误（占位符数量不符、不支持的格式符等） |
| `control-flow` | 控制流错误（break/continue 在循环外、return 在函数外等） |
| `oop-error` | OOP 错误（实例化抽象类、MRO 冲突、方法缺少 self 等） |
| `framework-bug` | 框架特定缺陷（Vue/React 生命周期、Hook 规则、双向数据流等） |

#### 可靠性审查 (reliability)
| category | 含义 |
|----------|------|
| `resource-leak` | 资源泄漏（文件/连接/锁未关闭释放） |
| `concurrency-race` | 并发竞态（无锁共享变量、死锁、WaitGroup 误用等） |
| `thread-safety` | 线程安全（非线程安全集合共享、SimpleDateFormat 等） |
| `db-operation` | 数据库操作（N+1、大批量未分批、事务失效、免密/明文密码） |
| `async-issue` | 异步问题（未 await、事件循环阻塞、Task GC 等） |
| `auth-missing` | 鉴权缺失（对外接口无鉴权） |
| `auth-bypass` | 越权访问（未校验资源归属、垂直越权） |
| `auth-logic-error` | 鉴权逻辑错误（校验变量来源错误、宽松比较） |
| `performance-issue` | 性能问题（线程池无界、ReDoS、循环字符串拼接等） |

## 输出示例

```json
{
  "reviewer": "correctness",
  "summary": "发现 2 个正确性问题：一个空指针风险和一处异常被吞",
  "findings": [
    {
      "id": "001",
      "severity": "P0",
      "category": "null-safety",
      "file": "src/api/user.ts",
      "line": 42,
      "endLine": 48,
      "title": "空指针访问",
      "description": "data.user 可能为 null，直接访问 data.user.name 会在运行时崩溃",
      "suggestion": "添加空值检查：if (data.user) { ... }",
      "locked": true
    },
    {
      "id": "002",
      "severity": "P1",
      "category": "exception-handling",
      "file": "src/service/init.ts",
      "line": 20,
      "endLine": 23,
      "title": "异常被吞",
      "description": "catch 块中只有 console.log，异常未向上传播，调用方无法感知失败",
      "suggestion": "catch 后重新抛出或返回错误状态"
    }
  ]
}
```

## 合并规则

主控 Agent 在收集到所有 SubAgent 的输出后，按以下规则合并：

1. **去重**：`file` + `line`（±5行范围内）+ `category` 相同的视为重复，保留 description 最详细的
2. **合并相近**：同一文件中多个同类问题（如多处硬编码字符串）合并为一条，在 description 中列出所有位置
3. **重新编号**：合并后按 severity 排序，分配连续编号（1, 2, 3...）
4. **统计汇总**：计算各等级的数量，生成总体评估

---

## Meta-Reviewer 输出格式

Meta-Reviewer 的输出格式与审查 Agent 不同，它不直接产出 findings，而是对已有 findings 进行修正和补充。

### JSON Schema

```json
{
  "reviewer": "meta",
  "summary": "Meta-Review 整体评估",
  "actions": [
    {
      "action": "remove | adjust_severity | supplement | refine_suggestion",
      "target_id": "E001",
      "reason": "为什么要做这个调整",
      "new_severity": "P2",
      "new_suggestion": "更具体的建议"
    }
  ],
  "missed_findings": [
    {
      "id": "001",
      "severity": "P1",
      "category": "分类标识",
      "file": "相对路径/文件名",
      "line": 42,
      "title": "遗漏的问题",
      "description": "描述",
      "suggestion": "建议"
    }
  ]
}
```

### Action 字段说明

| action | 含义 | 必填字段 |
|--------|------|---------|
| `remove` | 移除误报 | `target_id`, `reason` |
| `adjust_severity` | 调整严重等级 | `target_id`, `reason`, `new_severity` |
| `refine_suggestion` | 细化修复建议 | `target_id`, `reason`, `new_suggestion` |
| `supplement` | 补充已有 finding 的信息 | `target_id`, `reason` |

### missed_findings

遗漏的问题使用标准 finding 格式。这些条目在合并阶段会被追加到 findings 列表中。

### 合并时应用 Meta-Review 的顺序

1. 先应用 `actions`（remove → adjust_severity → refine_suggestion → supplement）
2. 再追加 `missed_findings`
3. 最后执行去重、合并、排序、编号
