# Git 提交自动绑定卡片工作流（零交互版）

Git 提交/发起评审时，自动为代码变更绑定 iCafe 卡片。**核心原则: 全自动决策，结合上下文智能判断，不与用户交互，直接给出结果。**

**⚠️ 严禁跳过 smart-find 直接建卡！必须先搜索已有卡片，确认没有可复用的卡片后才能新建。**

---

## 设计理念

1. **必须先搜后建**: **禁止跳过 smart-find 直接创建卡片**。即使 git log 中有空间信息，也必须先调 smart-find 查找已有卡片。只有确认所有已有卡片都不相关时，才新建
2. **结合上下文判断**: 每一步决策都要结合 git diff 内容、分支名、commit message、仓库名等上下文，不能机械地"选第一个"
3. **优先复用已有卡片**: 先从 smart-find 的活跃卡片中找最相关的，找不到再建
4. **找不到就建**: 新建时结合 git log 历史和 smart-find 统计确定空间和类型
5. **先做后说**: 直接给出结果 + 简短解释，不问问题
6. **只在极端情况下才问**: 完全无法判断空间时才询问

## Phase 1: 收集上下文信号（纯本地，零 API）

并行执行以下本地操作，收集所有可用信号：

```bash
git log --oneline -20                       # 历史提交中的卡片绑定
git rev-parse --abbrev-ref HEAD             # 当前分支名
git remote get-url origin                   # 仓库 URL
git diff --cached --stat                    # 本次变更的文件列表
```

从结果中提取：

| 信号 | 来源 | 示例 |
|------|------|------|
| 历史绑定记录 | git log | `cloud-iCafe-22210 [Task] 智能预审支持LR` |
| 分支名 | git branch | `feature/smart-find` |
| 仓库关键词 | git remote | `baidu/icafe/luigi-service` → "luigi", "icafe" |
| 变更内容摘要 | git diff | 修改了哪些文件、哪些模块 |
| commit message | 用户输入 | "修复登录白屏问题" |

**这些信号在后续每一步都要参考，不是只用一次。**

## Phase 2: 调 smart-find 搜索已有卡片（必须执行，不可跳过）

**⚠️ 这一步是必须的！不管 git log 里有没有空间信息，都必须先调 smart-find 查找已有卡片。**

```bash
icafe-cli card smart-find
```

返回：
- `cards`: 用户活跃卡片列表（含 space、sequence、title、status、type、lastModified 等）
- `stats.bySpace`: 各空间的卡片数量分布
- `stats.bySpaceType`: 各空间+类型的数量分布

## Phase 3: 从活跃卡片中找最相关的（必须在 Phase 2 之后）

**Phase 2 的 smart-find 结果 + Phase 1 的 git log 历史卡片序列号，综合分析找到最相关的卡片。同时，如果 git log 中有该空间的卡片序列号，也可以用 `card get --brief` 批量查询验证这些卡片是否仍然活跃。**

判断维度（综合考虑，不是单一条件）：

| 维度 | 高相关性 | 低相关性 |
|------|---------|---------|
| 标题与变更内容 | 卡片标题的关键词与 commit message、分支名、diff 文件名有交集 | 完全无关 |
| 空间与仓库 | 卡片空间名和仓库关键词有关联 | 完全不同的业务领域 |
| git log 历史 | 该卡片的 `{space}-{sequence}` 出现在近期 git log 中 | 从未出现 |
| 卡片状态 | 未结束（开发中、待测试等） | 已完成、已关闭 |
| 卡片类型 | 类型与变更性质匹配（bug fix → Bug，新功能 → Story） | 不匹配 |
| 时间 | 最近修改过 | 很久没动 |

**决策**：
- 找到明确相关的卡片 → 直接使用，**跳到 Phase 6**
- 多张可能相关但不确定哪个最好 → 选综合相关性最高的那张
- 所有卡片都不相关（如 smart-find 返回的卡片全是其他项目的） → **进入 Phase 4 新建**
- smart-find 无结果 → **进入 Phase 4 新建**

## Phase 4: 确定新建卡片的空间

走到这一步说明没有合适的已有卡片。需要确定空间和类型来新建。

**结合上下文从以下信息源推断空间**：

- **git log 历史绑定的空间**: 当前仓库历史提交绑定过哪些空间，这是最强信号（说明这个仓库就在这个空间管理）
- **smart-find 的 stats.bySpace**: 用户活跃的空间分布
- **仓库名与空间名的关联**: git remote URL 的关键词与空间名做匹配

**判断逻辑**（结合上下文综合判断，不是机械选第一个）：
- git log 和 smart-find 指向同一个空间 → 高置信度，直接用
- git log 有空间但 smart-find 最活跃的是另一个 → 以 git log 为准（git log 是当前仓库的上下文）
- git log 无历史（新仓库） → 结合仓库关键词和 smart-find 空间名匹配
- 完全无法判断 → **此时才询问用户**（极少发生）

## Phase 5: 确定新建卡片的类型

**结合上下文从以下信息源推断类型**：

- **git log 历史绑定的类型标记** `[Task]`/`[Bug]` → 该空间已验证可绑定代码的类型
- **smart-find 该空间的 stats.bySpaceType** → 该空间最常用的类型
- **分支名模式** → `bugfix/*` → Bug, `feature/*` → Story, `task/*` → Task
- **commit message / diff 关键词** → "修复" → Bug, "新增" → Story, "优化" → Task

**判断逻辑**（结合上下文综合判断）：
- git log 历史类型 + 分支名/关键词指向一致 → 高置信度
- git log 无历史类型 → 结合分支名 + smart-find 类型分布 + 变更内容判断
- 多个信号冲突 → 选 git log 历史类型（已验证可绑定）
- 完全无信号 → 用 `Task`（最通用，几乎所有空间都支持绑定代码）

## Phase 5.5: 创建卡片

```bash
icafe-cli card create --space <space> --title "<title>" --type <type>
```

- **标题**: 优先用 commit message 第一行（去掉已有的 `{space}-{seq}` 前缀），其次用分支名转可读文本
- **负责人**: 不传 `--assignee`，CLI 默认自动将当前登录用户设为负责人
- **其他字段**: 不传。自动绑定场景下标题+类型+负责人足够，优先级和自定义字段可后续补充

## Phase 6: 输出结果

直接输出，不问用户确认。

**commit message 必须严格遵循以下格式**：
```
{space}-{sequence} [{type}] {title}
```
- `{space}`: 空间 prefixCode
- `{sequence}`: 卡片序列号
- `[{type}]`: 方括号包裹的卡片类型，**不能省略**
- `{title}`: 卡片标题或 commit 描述

示例: `DevOps-iScan-36730 [Bug] 修复FixedSplitter构造函数chunkLines字段赋值错误`

**复用已有卡片**：
```
已找到关联卡片: cloud-iCafe-22210 [Task] 智能预审结果支持发起LR
（匹配原因: 标题与分支名 feature/smart-preview 相关，且为该空间最近活跃的开发中卡片）

commit message:
cloud-iCafe-22210 [Task] 智能预审结果支持发起LR

卡片链接: https://console.cloud.baidu-int.com/devops/icafe/issue/cloud-iCafe-22210/show
```

**自动新建卡片**：
```
未找到合适的已有卡片，已自动创建: cloud-iCafe-22235 [Task] smart-find 功能实现
（空间 cloud-iCafe 来自 git 历史绑定记录，类型 Task 为该空间最常用的可绑定类型）

commit message:
cloud-iCafe-22235 [Task] smart-find 功能实现

卡片链接: https://console.cloud.baidu-int.com/devops/icafe/issue/cloud-iCafe-22235/show
```

> **关键**: 输出中附带简短的匹配/创建原因说明，让用户知道为什么选了这张卡片或为什么这样创建。

## 决策流程图

```
git commit 需要绑定卡片
  │
  ├─ Phase 1: 收集本地信号 (零 API)
  │   git log / branch / remote / diff / commit message
  │
  ├─ Phase 2: card smart-find (1次 API，有缓存)
  │   → 活跃卡片列表 + 空间/类型统计
  │
  ├─ Phase 3: 从活跃卡片中找最相关的
  │   结合上下文判断每张卡片的相关性:
  │   标题匹配 + 空间匹配 + git log 出现过 + 未结束 + 类型合理
  │   ├─ 找到相关卡片 → Phase 6 输出
  │   └─ 都不相关 / 无结果 → Phase 4 新建
  │
  ├─ Phase 4: 确定空间 (结合上下文判断)
  │   git log 空间 + smart-find 空间 + 仓库关键词匹配
  │   └─ 极端无法判断 → 才问用户
  │
  ├─ Phase 5: 确定类型 (结合上下文判断)
  │   git log 类型 + smart-find 类型统计 + 分支名 + 关键词
  │   └─ 无法判断 → 兜底 Task
  │
  ├─ Phase 5.5: card create (负责人自动设为当前用户)
  │
  └─ Phase 6: 直接输出结果
      commit message 格式: {space}-{sequence} [{type}] {title}
      卡片 URL + 匹配/创建原因
```

## API 调用统计

| 场景 | 调用次数 | 明细 |
|------|---------|------|
| smart-find 有匹配卡片 | 1 次 | smart-find (缓存) |
| smart-find 无匹配 + git log 有 sequence | 2 次 | smart-find + card get |
| 需要新建 | 2 次 | smart-find + card create |

## 核心原则重申

1. **每一步决策都结合上下文**: 不是"选 stats 第一个"，而是综合 git diff 内容、分支名、commit message、仓库名来判断
2. **smart-find 优先**: 先看有没有能直接用的卡片，再考虑新建
3. **git log 是空间/类型的最强信号**: 因为它代表"这个仓库历史上在哪个空间用什么类型绑定过代码"
4. **输出时解释原因**: 让用户知道 Agent 的判断依据，如果判断错了用户能及时纠正
5. **负责人默认当前用户**: 新建卡片不需要指定 `--assignee`，CLI 自动处理
