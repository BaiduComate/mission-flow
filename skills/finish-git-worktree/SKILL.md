---
name: finish-git-worktree
description: 当实现已完成并需要处理由 git worktree 承载的开发分支时使用。用于呈现 rebase、保留、丢弃等结构化选项，并安全收尾 worktree 和开发分支
metadata:
  version: 0.2.0
---

# 结束 Git Worktree

## 概览

通过呈现清晰选项并处理所选工作流，引导结束由 git worktree 承载的开发工作。

**开始时声明：** "我正在使用 finish-git-worktree skill 来结束该任务"

## 流程

### 1. 确定基础分支

由 `using-git-worktrees` 创建的分支，其 upstream 已绑定到基础分支。优先使用它，而不是猜测 `main` / `master`：

```bash
base_branch=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null)
```

如果未设置 `@{upstream}`（分支不是由 `using-git-worktrees` 创建的），则回退到检测：

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或请用户确认。

### 2. 呈现选项

**使用 questions tools** 精确呈现以下 3 个选项：

```
实现已完成。你想怎么处理？

1. 将 <feature-branch> rebase 到 <base-branch>，并清理 worktree 和本地分支
2. 保持该分支原样（我稍后处理）
3. 丢弃本次工作

选择哪个选项？
```

### 3. 执行选择

#### Option 1: 本地 rebase

```bash
git checkout <feature-branch>
git fetch
git rebase <base-branch>
```

然后：报告 `feature-branch` 已基于 `<base-branch>` 重放，并清理 worktree 与本地 feature 分支（Step 4）。

#### Option 2: 保持原样

报告："保留分支 `<name>`。Worktree 保留在 `<path>`。"

**不要清理 worktree。**

#### Option 3: 丢弃

**先确认：**

```
这将永久删除：
- 分支 <name>
- 所有提交：<commit-list>
- 位于 <path> 的 worktree

输入 'discard' 以确认。
```

等待用户精确确认。如果已确认则执行：

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后：清理 worktree（Step 4）

### Step 4: 清理 Worktree

**对于 Option 1、3：**

由 `using-git-worktrees` 创建的 worktree 位于 `~/.comate/worktree/<repo>/<name>`。检查当前分支是否运行在其中：

```bash
git worktree list | grep "$(git rev-parse --show-toplevel)"
```

如果是，请从 worktree **外部** 移除它（不能移除当前所在的 worktree）。Option 1 在移除 worktree 后删除本地 feature 分支；Option 3 删除分支已经在上一步完成。

```bash
cd "$(git rev-parse --git-common-dir)/.."   # 跳转到主仓库
git worktree remove ~/.comate/worktree/<repo>/<name>
git branch -D <feature-branch>               # 仅 Option 1 执行
```

**对于 Option 2：** 保留 worktree。

## 常见错误

**开放式问题**

- **问题：** "接下来我该做什么？" → 含糊不清
- **修复：** 精确呈现 3 个结构化选项

**自动清理 worktree**

- **问题：** 在 worktree 可能仍然需要时将其移除（Option 2）
- **修复：** 仅对 Option 2 保留 worktree；对 1、3 移除

**丢弃时未确认**

- **问题：** 意外删除工作
- **修复：** 要求输入 "discard" 确认

## 危险信号

**绝不：**

- 未经确认就删除工作

**始终：**

- 在回退到检测前，优先使用 `@{upstream}` 作为基础分支
- 精确呈现 3 个选项
- 获取 Option 3 的输入确认
- 仅对 Option 2 保留 worktree

## 集成

**配合使用：**

- **using-git-worktrees** - 清理由该 skill 创建的 worktree
