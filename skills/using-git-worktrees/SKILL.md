---
name: using-git-worktrees
description: 在开始需要与当前工作区隔离的功能开发，或执行实现计划前使用
metadata:
  version: "0.1.0"
---

## 概览

Git worktrees 会创建共享同一仓库的隔离工作空间，允许在不切换分支的情况下同时处理多个分支。

**开始时声明：** "我正在使用 using-git-worktrees skill 来设置独立工作空间"

## 路径规则

所有 worktree 都位于一个固定的基础目录下，并按仓库名称区分：`~/.comate/worktree/<repo-name>/<verb>-<obj>`

- `<repo-name>`：仓库顶层目录的 basename（`basename "$(git rev-parse --show-toplevel)"`）。
- `<verb>-<obj>`：从任务派生出的简短 kebab-case 名称（例如 `fix-login`、`add-oauth`、`refactor-router`）。
  - `<verb>`：祈使动词，例如 `fix`、`add`、`refactor`、`remove`、`update`。
  - `<obj>`：描述变更对象的单个目标名词或短语。
- 分支名与目录名完全相同。

如果 `git worktree add -b` 因目录或分支已存在而失败，则在 `<verb>-<obj>` 后追加 `-2`、`-3`、...，直到成功。

## 创建步骤

### 1. 解析名称

```bash
repo=$(basename "$(git rev-parse --show-toplevel)")
base_branch=$(git rev-parse --abbrev-ref HEAD)
# name = 从任务派生出的 <verb>-<obj>
path=~/.comate/worktree/$repo/$name
```

### 2. 从当前分支创建 worktree

```bash
mkdir -p ~/.comate/worktree/$repo
git worktree add -b "$name" "$path" "$base_branch"
cd "$path"
git branch --set-upstream-to="$base_branch" "$name" # 这会在 git 自身元数据中记录合回目标（`.git/config` 中的 `branch.<name>.merge`）
```

### 3. 运行项目初始化

委托给 sub-agent。不要根据单个 manifest 文件猜测命令。提供给 sub-agent 的路径：

1. 先识别项目的语言组成
2. 对每种语言，按权威性从高到低定位其工具链：CI 配置、README/CONTRIBUTING、lockfile、manifest。
3. 使用项目实际采用的包管理器运行初始化；优先使用 frozen/locked 变体，确保 worktree 与已提交的 lockfile 一致。
4. 遇到歧义（多个 lockfile、缺少版本、未知构建系统）时，停止并报告，不要猜测选择。

### 4. 报告位置

```
Worktree 已准备好：<full-path>
分支：<name>（upstream：<base_branch>）
准备实现 <task>
```

## 常见错误

### 偏离 `<verb>-<obj>` 约定

- **问题：** 不一致的名称会让列表查看和清理更困难；查找工具期望这种形状。
- **修复：** 始终选择单个祈使动词 + 对象；仅使用 kebab-case。

### 忘记设置 upstream

- **问题：** 没有 upstream 时，`git status` / `git rebase` 不知道要与哪里比较；一旦继续后续工作，基础分支就会丢失。
- **修复：** 始终在 `git worktree add` 之后立即运行 `git branch --set-upstream-to="$base_branch" "$name"`。

### 根据单个文件硬编码初始化命令

- **问题：** 存在 `package.json` → 运行 `npm install` 可能覆盖 `pnpm-lock.yaml`；存在 `pyproject.toml` → 运行 `pip install .` 会忽略已提交的 `uv.lock`。worktree 最终会使用真实项目从未使用的工具链。
- **修复：** 将发现过程委托给 sub-agent。优先 CI / 文档，其次 lockfile，再其次 manifest。遇到歧义时停止并询问。

## 示例工作流

```
任务："fix login bug"，仓库 comate-plugin-host，当前分支 feature/agent-mode。

[解析名称：repo=comate-plugin-host，base_branch=feature/agent-mode，name=fix-login]
[mkdir -p ~/.comate/worktree/comate-plugin-host]
[git worktree add -b fix-login ~/.comate/worktree/comate-plugin-host/fix-login feature/agent-mode]
[cd ~/.comate/worktree/comate-plugin-host/fix-login]
[git branch --set-upstream-to=feature/agent-mode fix-login]
[npm install]

Worktree 已准备好：~/.comate/worktree/comate-plugin-host/fix-login
分支：fix-login（upstream：feature/agent-mode）
准备实现 fix-login
```

## 警示项

**绝不要：**

- 将 worktree 放在 `~/.comate/worktree/<repo>/` 之外的任何位置
- 跳过 `git branch --set-upstream-to`：丢失基础分支会让合回目标变得不明确

**始终：**

- 从任务派生 `<verb>-<obj>`；分支名 == 目录名
- 基于当前分支创建新分支（`git rev-parse --abbrev-ref HEAD`）
- 将基础分支绑定为 upstream，以便可通过 `@{upstream}` 恢复合回目标
- **通过 sub-agent** 自动检测并运行项目初始化，尊重 lockfile 和项目已有的 CI

## 集成

**配合使用：**

- **finish**：工作完成后清理时必需
