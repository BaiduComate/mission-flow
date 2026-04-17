# 复杂场景工作流指南

本文档包含使用 icafe-cli 处理复杂多步骤场景的详细操作指南和决策流程。

---

## 场景1: Git 提交/发起评审时智能绑定卡片

用户在 iCode (Gerrit 模式) 提交代码后发起评审，需要绑定 iCafe 卡片。核心逻辑：**自动查找最相关的已有卡片，找不到则新建**。

### 第一步：确定目标空间

空间的确定有优先级，按以下顺序逐级尝试。

**1.1 用户对话上下文直接指定了空间**

如果用户说"提交到 cloud-iCafe 空间"，直接使用 `cloud-iCafe` 作为 space。

**1.2 从 git log 历史提交记录中解析空间**

```bash
git log --oneline -20
```

分析历史提交信息，提取卡片绑定信息。提交记录中通常包含如下格式：

```
cloud-iCafe-22210 [Task] 【前端】智能预审结果支持发起LR
cloud-iCafe-22211【前端】智能预审结果支持xxx发起LR
myspace-1568 [Bug] 修复登录异常
```

解析规则：
- 格式为 `{空间标识}-{卡片序列号 (sequence)}`，如 `cloud-iCafe-22210`
- **序列号 (sequence) 是最后一个 `-` 后的纯数字部分**，前面的所有内容是空间标识 (prefixCode)。空间标识本身可能包含 `-`，例如 `cloud-iCafe-22210` 中 space 是 `cloud-iCafe`、sequence 是 `22210`
- `[Task]`、`[Bug]` 等方括号内容是卡片类型（可能没有）
- 如果多条提交记录指向不同空间，统计出现最多的空间，或列出让用户选择

**解析结果暂存**：将解析出的所有 `{space, sequence, type(可能为空)}` 记录下来，供第二步和第三步复用。

**1.3 smart-find + git remote 交叉匹配推断空间**

如果 git log 中没有卡片信息（新项目、第一次提交等），组合使用 smart-find 和 git remote 推断：

```bash
# 获取仓库名关键词
git remote get-url origin
# 例如: icode.baidu.com/baidu/icafe/luigi-service → 关键词 "luigi", "icafe"

# 获取用户活跃卡片和空间
icafe-cli card smart-find
```

从 smart-find 结果中推断空间的策略（**直接读 `stats.bySpace` 字段，已按数量降序排列**）：

1. **仓库名匹配**: 从 `git remote` URL 提取仓库关键词（如 `luigi-service` → "luigi"、"icafe"），与 `stats.bySpace` 中的空间名和 `cards` 中的卡片标题做模糊匹配，匹配度高的空间优先
2. **空间分布统计**: 统计 smart-find 结果中各空间出现的卡片数量，出现最多的空间最可能是用户当前工作的空间
3. **活跃度权重**: `lastModified` 越近的卡片所在空间权重越高
4. **单空间直接使用**: 如果只有一个空间，直接使用
5. **多空间候选**: 如果无法自动确定，列出 top 3 候选空间（附卡片数量和最近活跃时间）让用户选择
6. **无结果**: smart-find 也无结果，必须询问用户

> **注意**: `smart-find` 结果缓存 10 分钟，同一会话内多次调用不会重复请求 API。

### 第二步：在选定空间中查找已有卡片

确定空间后，优先查找可以复用的已有卡片，避免重复创建。

**2.1 从 smart-find 结果中匹配**

如果第一步中使用了 `smart-find`，其结果已包含用户的活跃卡片列表。直接从中筛选属于目标空间的卡片：
- 排除已结束的卡片（status 为终态的，如"已完成"、"已关闭"）
- 检查标题是否与本次代码变更相关（用 git diff 摘要、分支名、commit message 做关键词匹配）
- 如果有多张候选，按标题相关性 + lastModified 时间综合排序

如果找到合适的卡片，推荐给用户使用。**用户确认 → 跳到第五步。**

**2.2 从 git log 中提取的卡片批量查询**

如果第一步中解析出了该空间的卡片序列号，**一次性批量查询**（同时验证空间有效性）：

```bash
# 将同一空间的所有序列号合并查询，避免逐个调用
icafe-cli card get --space cloud-iCafe --sequence 22210,22211,22215 --brief
```

> **复用提示**: 本步返回的卡片数据（类型、状态等）在第三步确定卡片类型时直接复用，无需再次调用 `card get`。

从返回结果中筛选适合本次提交的卡片：
- 排除 `isFinishedStatus` 为 `true` 的卡片（已结束，不适合绑定）
- 检查标题和类型是否与本次代码变更相关
- 结合当前用户对话的上下文判断
- 如果有多张候选，按相关性排序推荐

如果找到合适的卡片，推荐给用户使用。**用户确认 → 跳到第五步。用户拒绝或没有合适的 → 继续 2.3 IQL 搜索。**

**2.3 用 IQL 搜索相关卡片**

如果前两步都没有找到合适的卡片，使用 IQL 查询。结合当前上下文（git diff 内容、分支名、用户编写的 commit message）构建查询：

```bash
# 查找当前用户负责的未关闭卡片 (currentUser 是 IQL 内置关键字，自动匹配当前认证用户)
icafe-cli card query --space <space> \
  --iql "负责人 = currentUser AND 流程状态 != 已关闭" \
  --max-records 10 --brief

# 如果能从分支名或 commit message 中提取关键词，用标题模糊匹配缩小范围
icafe-cli card query --space <space> \
  --iql "负责人 = currentUser AND 标题 ~ <关键词> AND 流程状态 != 已关闭" --brief
```

> **注意**: `流程状态 != 已关闭` 中的 "已关闭" 只是常见的终态名称，不同空间的终态名可能不同（如 "已完成"、"Done" 等）。建议对查询结果再用返回的 `isFinishedStatus` 字段做二次过滤，排除所有已结束的卡片。

- 如果找到匹配的卡片，列出候选卡片（序列号、标题、类型、状态），让用户确认使用哪张
- 如果找到多张，根据标题与本次代码变更的相关性排序推荐
- 用户确认后，直接使用该卡片，跳到第五步

**2.4 没有找到合适的已有卡片 → 进入第三步新建**

### 第三步：确定新建卡片的类型

> **重要约束: 卡片类型可绑定性**
>
> 每个空间可以配置哪些卡片类型允许绑定代码（即 Git 提交可以关联该类型的卡片）。有些空间只允许特定类型（如 Task、Bug）绑定代码，有些空间未配置则所有类型都可绑定。**目前没有 API 可以查询哪些类型可绑定代码**，因此必须优先参考 git log 中已有的历史绑定记录——历史上成功绑定过的卡片类型大概率是该空间允许的。

按以下优先级确定类型，**多个信号综合判断比单一信号更可靠**：

**3.1 用户上下文中指定了类型** (可信度: 最高)

如果用户明确说"创建一个 Bug"，直接使用。

**3.2 git log 历史绑定类型** (可信度: 高，已验证可绑定)

从第一步解析的 `[Task]`、`[Bug]` 类型标记中提取。这些是该空间**已验证可绑定代码**的类型：
- 如果历史只有一种类型（如全是 Task），本次优先用 Task
- 如果有多种类型，暂存供后续交叉验证

**3.3 git 分支名模式匹配** (可信度: 中)

解析当前 git 分支名，很多团队有分支命名规范：

```bash
git rev-parse --abbrev-ref HEAD
```

| 分支名模式 | 推断类型 |
|-----------|---------|
| `bugfix/*`, `fix/*`, `hotfix/*` | Bug |
| `feature/*`, `feat/*` | Story 或 Feature |
| `task/*`, `chore/*`, `docs/*` | Task |
| `release/*`, `deploy/*` | 不推断（通常不新建卡片） |

> **注意**: 分支名推断的类型需要和 3.2 的历史类型交叉验证。如果分支名推断为 Bug，但历史上该空间从未绑定过 Bug 类型，应该提示用户确认。

**3.4 smart-find 该空间的类型分布** (可信度: 中)

如果第一步使用了 smart-find，**直接读 `stats.bySpaceType` 字段**（已按数量降序排列，无需自己遍历 cards 计算）：

```
例如 smart-find 返回的 stats.bySpaceType:
  [{"space":"cloud-iCafe", "type":"Task", "count":8},
   {"space":"cloud-iCafe", "type":"Story", "count":4},
   {"space":"cloud-iCafe", "type":"Bug", "count":2}]
→ cloud-iCafe 空间最常用 Task
```

- 结合 3.3 的分支名提示交叉验证：分支名推断 Bug + 该空间有 Bug 类型 → 高置信度选 Bug
- 如果无分支名提示，用出现最多的类型作为默认值

**3.5 commit message / git diff 关键词** (可信度: 低，辅助参考)

| 关键词 | 推断类型 |
|--------|---------|
| "修复", "fix", "bug", "repair", "patch" | Bug |
| "新增", "feat", "add", "implement", "新功能" | Story/Feature |
| "优化", "refactor", "重构", "perf" | Task |
| "文档", "doc", "readme" | Task |
| "测试", "test", "ut" | Task |

> 这些只是辅助信号，不能单独决定类型。应与 3.2~3.4 的结果综合判断。

**3.6 综合决策**

将以上信号按权重综合：

```
最终类型 =
  用户指定 (最高优先)
  > git log 历史类型 (高优先，已验证可绑定)
  > 分支名 + smart-find 类型分布交叉验证 (中优先)
  > smart-find 该空间最常用类型 (中低优先)
  > commit/diff 关键词 (低优先，仅辅助)
```

如果有足够置信度（至少两个信号指向同一类型），直接使用并告知用户；否则列出候选类型让用户选择。

**3.7 查询空间支持的类型列表 (兜底)**

仅当以上所有信号都无法确定类型时（新项目、新空间、无历史记录）：

```bash
icafe-cli space issue-types --space <space>
```

获取该空间所有可用类型，结合上下文让模型判断最合适的类型，不确定时询问用户。注意：这里返回的是空间支持的所有类型，不代表所有类型都能绑定代码。

> **避免重复调用**: 如果确定了类型后紧接着要调 `space type-fields --type <type>` 获取字段，`type-fields` 调用成功即隐含"该类型存在"的验证，不需要先调 `issue-types` 确认类型再调 `type-fields`。只有在**需要列出所有类型让用户选择**时才调 `issue-types`。

### 第四步：获取字段信息并创建卡片

**4.1 获取该空间该类型下的所有字段**

```bash
icafe-cli space type-fields --space <space> --type <type>
```

这个接口返回每个字段的：
- 字段名称（中文，如"负责人"、"优先级"）
- 字段类型（文本、选择、人员等）
- 是否必填
- 可选值列表（如优先级的 P0-Highest ~ P4-Lowest）

**注意：不同空间的字段可能不同，同一字段的可选值也可能不同，必须通过此接口动态获取，不能硬编码。**

**4.2 填充字段值**

结合上下文信息尽可能填充所有字段：

| 字段 | 值来源 |
|------|--------|
| 标题 (title) | 从 commit message 或 git diff 摘要生成，或询问用户 |
| 正文 (detail) | 从 git diff 生成变更摘要，转换为 HTML 格式 |
| 类型 (type) | 第三步确定的类型 |
| 负责人 (assignee) | 当前用户的百度用户名 (邮箱前缀) |
| 优先级 (priority) | 根据 type-fields 返回的优先级选项动态选择。如有 P2-Middle 可作为默认值；如该类型无优先级字段则不传 |
| 流程状态 (status) | 通常不需要指定，使用默认的初始状态 |
| 自定义必填字段 | 从 fields 接口获取必填字段，尽量填充；无法确定值时直接跳过 (API 不强制校验自定义必填字段) |

**4.3 创建卡片**

```bash
icafe-cli card create \
  --space <space> \
  --title "从代码变更和上下文推断的标题" \
  --detail "<p>变更摘要的HTML描述</p>" \
  --type <type> \
  --assignee <username> \
  --priority <从 type-fields 获取的优先级值> \
  --fields "自定义必填字段1=值1,自定义必填字段2=值2"
```

> **注意**: `--priority` 的值必须来自 `space type-fields` 返回的选项列表，不能硬编码。如该类型无优先级字段则不传此参数。

如果必填字段无法全部填充，仍然可以创建成功 (API 层不强制校验自定义必填字段，只校验 title 和 type)。但建议尽量填充以保证卡片信息完整。

### 第五步：返回卡片信息

无论是复用已有卡片还是新建卡片，最终都要返回：

1. **卡片 URL**（用于绑定到 git commit / 评审）：
```
https://console.cloud.baidu-int.com/devops/icafe/issue/<space>-<sequence>/show
```

2. **卡片基本信息**：序列号、标题、类型、状态

3. **供用户使用的 commit message 格式**：
```
<space>-<sequence> [<type>] <title>
```
例如：`cloud-iCafe-22210 [Task] 【前端】智能预审结果支持发起LR`

### 决策流程图

```
用户准备提交代码 / 发起评审
  │
  ├─ 1. 确定空间
  │   ├─ 用户上下文指定？ → 使用指定空间
  │   ├─ git log 中有历史卡片？ → 解析 {空间标识}-{序列号} (序列号=最后一个-后的纯数字)
  │   │   暂存所有 {space, sequence, type} 记录
  │   └─ 都没有？ → card smart-find + git remote 交叉匹配
  │       ├─ 仓库名与卡片标题/空间名匹配 → 优先推荐匹配的空间
  │       ├─ 统计空间分布 + 活跃度 → 推荐 top 空间
  │       └─ 无法确定 → 列候选让用户选择
  │
  ├─ 2. 查找已有卡片
  │   ├─ smart-find 结果中有该空间的卡片？ → 标题关键词匹配推荐
  │   │   ├─ 用户确认 → 跳到第 5 步
  │   │   └─ 用户拒绝 → 继续 2.2
  │   ├─ 有解析出的序列号？ → card get 批量查询 (同时验证空间 + 获取类型信息)
  │   │   ├─ 有未结束且相关的卡片 → 推荐给用户
  │   │   │   ├─ 用户确认 → 跳到第 5 步
  │   │   │   └─ 用户拒绝 → 继续 IQL 搜索
  │   │   └─ 全部已结束或不相关 → 继续 IQL 搜索 (但保留类型信息供第 3 步用)
  │   ├─ IQL 搜索用户未关闭的卡片 (用 currentUser + isFinishedStatus 过滤)
  │   │   ├─ 找到 → 列出候选，用户选择 → 跳到第 5 步
  │   │   └─ 没找到 → 进入第 3 步
  │
  ├─ 3. 确定卡片类型 (多信号综合判断)
  │   ├─ 用户指定？ → 直接使用
  │   ├─ 收集信号:
  │   │   ├─ [高] git log 历史类型标记 [Task]/[Bug] (已验证可绑定)
  │   │   ├─ [中] git 分支名模式: bugfix→Bug, feature→Story, task→Task
  │   │   ├─ [中] smart-find 该空间类型分布统计 (最常用类型)
  │   │   └─ [低] commit/diff 关键词: "修复"→Bug, "新增"→Story
  │   ├─ 交叉验证: 多个信号指向同一类型？ → 高置信度使用
  │   ├─ 信号冲突？ → 优先 git log 历史 > 分支名+类型分布 > 关键词
  │   └─ 无任何信号？ → issue-types 获取列表 → 询问用户
  │
  ├─ 4. 创建卡片
  │   ├─ type-fields 获取字段定义、必填项和可选值 (含优先级选项)
  │   ├─ 从 git diff + commit message 生成 title 和 detail (HTML)
  │   ├─ 填充负责人、优先级 (从 type-fields 动态获取)、自定义必填字段
  │   ├─ card create 创建
  │   │   ├─ 成功 → 进入第 5 步
  │   │   └─ 失败（缺必填字段等） → 分析报错，询问用户补充后重试
  │
  └─ 5. 返回结果
      ├─ 卡片 URL: https://console.cloud.baidu-int.com/devops/icafe/issue/{space}-{sequence}/show
      ├─ 卡片基本信息
      └─ commit message 格式: {space}-{sequence} [{type}] {title}
```

---

> 智能修改卡片的完整流程已移至 [智能修改卡片工作流](smart-update-workflow.md)。
