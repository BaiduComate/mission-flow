# 智能建卡工作流

当用户需要创建卡片但没有提供完整的空间、类型等信息时，使用本流程智能推断并创建。

---

## 适用场景

- 用户说"帮我建个卡片记录一下"
- 用户说"创建一个 Bug"但没说哪个空间
- 用户说"在 cloud-iCafe 建个卡片"但没说类型
- 任何需要新建卡片但信息不完整的场景

## 第一步：确定空间

**1.1 用户明确指定了空间** → 直接使用

**1.2 从上下文推断**

如果用户没指定空间，调 smart-find 获取用户活跃空间：

```bash
icafe-cli card smart-find
```

从 `stats.bySpace` 推断空间：
- 只有 1 个空间 → 直接使用
- 有多个空间 → 结合以下信号选择：
  - 用户描述中的关键词与空间名/卡片标题匹配
  - 如果在 git 仓库中，`git remote get-url origin` 提取仓库关键词与空间匹配
  - `stats.bySpace[0]` 是最活跃的空间，优先推荐
- 无法确定 → 列出候选空间（附卡片数量），让用户选择

**1.3 无任何线索** → 必须询问用户

## 第二步：确定类型

按以下优先级，**多个信号综合判断**：

**2.1 用户明确指定了类型** (如"建个 Bug") → 直接使用

**2.2 smart-find 该空间的类型分布**

直接读 `stats.bySpaceType`（已按数量降序排列）：
```
例如: [{"space":"cloud-iCafe", "type":"Task", "count":8},
       {"space":"cloud-iCafe", "type":"Story", "count":4}]
→ 该空间最常用 Task
```

**2.3 用户描述关键词**

| 关键词 | 推断类型 |
|--------|---------|
| "修复", "fix", "bug", "缺陷", "问题" | Bug |
| "新增", "功能", "需求", "feature" | Story/Feature |
| "任务", "task", "优化", "重构" | Task |
| "史诗", "大需求", "epic" | Epic |

**2.4 git 分支名模式**（如果在 git 仓库中）

```bash
git rev-parse --abbrev-ref HEAD
```

| 分支名模式 | 推断类型 |
|-----------|---------|
| `bugfix/*`, `fix/*`, `hotfix/*` | Bug |
| `feature/*`, `feat/*` | Story/Feature |
| `task/*`, `chore/*`, `docs/*` | Task |

**2.5 综合决策**

```
最终类型 =
  用户指定 (最高优先)
  > smart-find 该空间最常用类型 + 用户关键词交叉验证
  > 分支名模式推断
  > 单独的 smart-find 最常用类型
```

至少两个信号指向同一类型 → 自动使用并告知用户。
只有一个信号或信号冲突 → 推荐但让用户确认。
无信号 → 询问用户，可用 `space issue-types` 列出选项。

> **避免重复调用**: 如果确定了类型后紧接着要调 `space type-fields`，不需要先调 `issue-types` 确认类型。`type-fields` 调用成功即隐含类型存在的验证。

## 第三步：获取字段信息

```bash
icafe-cli space type-fields --space <space> --type <type>
```

关注：
- **优先级字段**: 有则用默认值（如 `P2-Middle`），无此字段则不传
- **必填字段**: 尽量填充，但 API 不强制校验自定义必填字段，不必因此阻塞创建
- **字段可选值**: 选择类字段的值必须从 `valueItems` 中取

## 第四步：填充信息并创建

| 字段 | 来源 |
|------|------|
| 标题 (title) | 用户提供，或从用户描述中提取 |
| 正文 (detail) | 用户提供的详细描述，转 HTML。不确定可不传（使用模板默认值）|
| 类型 (type) | 第二步确定 |
| 负责人 (assignee) | 不传时 CLI 自动填充当前用户 |
| 优先级 (priority) | 从 type-fields 获取选项动态选择，不能硬编码 |
| 自定义字段 (fields) | 从 type-fields 获取必填项，尽量填充 |

```bash
icafe-cli card create \
  --space <space> \
  --title "用户提供或推断的标题" \
  --type <type> \
  --priority <从 type-fields 获取的值> \
  --fields "自定义字段1=值1,自定义字段2=值2"
```

**创建前向用户确认**：汇总空间、类型、标题等信息，确认后再执行。

## 第五步：返回结果

创建成功后返回：
- **卡片序列号**: 从返回的 `issues[0].sequence` 获取
- **卡片 URL**: `issues[0].url` 或拼接 `https://console.cloud.baidu-int.com/devops/icafe/issue/{space}-{sequence}/show`
- **卡片信息摘要**: 空间、序列号、标题、类型

> **注意**: OpenAPI 创建接口只返回基本信息（sequence, title, url），不返回完整卡片详情。如需确认自动分配的状态、负责人等，创建后再调 `card get --brief`。

## 决策流程图

```
用户要创建卡片
  │
  ├─ 1. 确定空间
  │   ├─ 用户指定？ → 直接用
  │   ├─ card smart-find → stats.bySpace
  │   │   ├─ 1 个空间 → 直接用
  │   │   ├─ 多个 → 关键词匹配/git remote 匹配 → 推荐或让用户选
  │   │   └─ 无结果 → 问用户
  │   └─ 无任何线索 → 问用户
  │
  ├─ 2. 确定类型 (多信号综合)
  │   ├─ 用户指定？ → 直接用
  │   ├─ 收集信号:
  │   │   ├─ smart-find stats.bySpaceType 该空间最常用类型
  │   │   ├─ 用户描述关键词: "bug"→Bug, "功能"→Story
  │   │   └─ git 分支名: bugfix→Bug, feature→Story
  │   ├─ 多信号一致 → 自动使用
  │   ├─ 信号冲突/不足 → 推荐 + 让用户确认
  │   └─ 无信号 → issue-types 列出选项 → 问用户
  │
  ├─ 3. type-fields 获取字段信息 + 填充
  │   ├─ 优先级: 有则选默认值，无则不传
  │   ├─ 必填项: 尽量填，不阻塞创建
  │   └─ 标题: 用户提供或从描述提取
  │
  ├─ 4. 向用户确认 → card create
  │   ├─ 成功 → 返回 sequence + URL
  │   └─ 失败 → 分析错误 (类型不存在/字段不合法) → 修正重试
  │
  └─ 5. 返回卡片信息
```

## 关键原则

1. **不确定就问**: 空间和类型是最重要的两个参数，不确定时必须确认，不要自己猜
2. **smart-find 优先**: 先从 stats 获取用户习惯，再用其他信号验证
3. **创建前确认**: 汇总所有信息让用户确认后再执行，避免建错卡片
4. **始终用 --brief**: 创建后如需查看详情，用 `card get --brief`
5. **标题很重要**: 标题是唯一不能为空的用户侧必填项，确保有意义
