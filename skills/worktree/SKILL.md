---
name: worktree
description: 需要与当前工作区隔离地开发，或需要收尾一个 worktree 分支时使用
---

## 约定

路径 `~/.comate/worktree/<repo>/<verb>-<obj>`。`<repo>` 取 `basename "$(git rev-parse --show-toplevel)"`，`<verb>-<obj>` 是从任务派生的 kebab-case 短名，例如 fix-login、add-oauth。分支名与目录名相同。目录或分支已存在时依次追加 `-2`、`-3`。

## 创建

```bash
repo=$(basename "$(git rev-parse --show-toplevel)")
base=$(git rev-parse --abbrev-ref HEAD)
path=~/.comate/worktree/$repo/$name
mkdir -p ~/.comate/worktree/$repo
git worktree add -b "$name" "$path" "$base"
git -C "$path" branch --set-upstream-to="$base" "$name"
```

`set-upstream-to` 不能省。基础分支只记录在这里，丢了就无法通过 `@{upstream}` 找回合回目标。

项目初始化命令交给子 agent 探测，按 CI 配置、README/CONTRIBUTING、lockfile、manifest 的顺序取权威来源，用项目实际使用的包管理器，优先 frozen 或 locked 变体。不要因为看见 `package.json` 就跑 `npm install`，那会覆盖 `pnpm-lock.yaml`。多个 lockfile 或构建系统不明时停下来问，不要猜。

## 收尾

基础分支取 `git rev-parse --abbrev-ref '@{upstream}'`，取不到再回退 `git merge-base HEAD main`，都不行就问用户。不要直接假定 main 或 master。

项目 workflow.md 声明了默认收尾方式时按它执行，不再询问。否则用 question 给三个选项：

- 本地 rebase（推荐）：rebase 到基础分支，随后清理 worktree 和本地分支
- 保持原样：保留分支和 worktree，用户自己处理
- 丢弃工作：删除分支、提交和 worktree，需用户输入 `discard` 才执行

清理必须先离开 worktree，不能移除当前所在的 worktree：

```bash
cd "$(git rev-parse --git-common-dir)/.."
git worktree remove ~/.comate/worktree/<repo>/<name>
git branch -D <name>
```
