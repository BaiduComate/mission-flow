---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Fixed base directory + task-derived naming + safety verification = reliable isolation.

**Announce at start:** "我正在使用 using-git-worktrees skill 来设置独立工作空间"

## Path Rule

All worktrees live under a single, fixed base directory keyed by repository name: `~/.comate/worktree/<repo-name>/<verb>-<obj>`

- `<repo-name>`: basename of the repository toplevel (`basename "$(git rev-parse --show-toplevel)"`).
- `<verb>-<obj>`: short, kebab-case name derived from the task (e.g. `fix-login`, `add-oauth`, `refactor-router`).
  - `<verb>`: imperative verb such as `fix`, `add`, `refactor`, `remove`, `update`.
  - `<obj>`: single target noun/phrase describing what is being changed.
- The branch name is identical to the directory name.

If `git worktree add -b` fails because the directory or branch already exists, append `-2`, `-3`, ... to `<verb>-<obj>` until it succeeds.

## Creation Steps

### 1. Resolve names

```bash
repo=$(basename "$(git rev-parse --show-toplevel)")
base_branch=$(git rev-parse --abbrev-ref HEAD)
# name = <verb>-<obj> derived from the task
path=~/.comate/worktree/$repo/$name
```

### 2. Create the worktree from the current branch

```bash
mkdir -p ~/.comate/worktree/$repo
git worktree add -b "$name" "$path" "$base_branch"
cd "$path"
git branch --set-upstream-to="$base_branch" "$name" # This records the merge-back target in git's own metadata (`branch.<name>.merge` in `.git/config`)
```

### 3. Run project setup

Delegate to a sub-agent. Do **not** guess commands from a single manifest file. Path to give the sub-agent:

1. Identify the project's language composition first
2. For each language, locate its toolchain signals: CI config, README/CONTRIBUTING, lockfile, manifest, from high authority to low.
3. Run setup with the package manager the project actually uses; prefer the frozen/locked variant so the worktree matches the committed lockfile.
4. On ambiguity (multiple lockfiles, missing version, unknown build system), stop and report — do not pick one by guessing.

### 4. Verify clean baseline

Also delegate to a sub-agent. Path to give the sub-agent:

1. Look at what CI runs on PRs — that is the de facto test command.
2. Otherwise check task runners (Makefile / justfile / `scripts` / task aliases).
3. Only fall back to language-default frameworks as a last resort.
4. Run it once; report pass/fail counts and a failure summary.

Handling the result:

| Result                | Action                                                                                         |
| --------------------- | ---------------------------------------------------------------------------------------------- |
| All pass              | Continue to step 5                                                                             |
| Any failure           | Report verbatim and ask: investigate pre-existing failures, or proceed? Never proceed silently |
| No test command found | Report "no baseline available" and skip; do not fabricate a test run                           |

### 5. Report location

```
Worktree ready at <full-path>
Branch: <name> (upstream: <base_branch>)
Tests passing (<N> tests, 0 failures)
Ready to implement <task>
```

## Quick Reference

| Situation                    | Action                                                         |
| ---------------------------- | -------------------------------------------------------------- |
| Recovering base branch       | `git rev-parse --abbrev-ref '@{upstream}'` inside the worktree |
| Tests fail during baseline   | Report failures + ask                                          |
| Setup / test command unclear | Delegate to sub-agent; never guess from a single file          |
| No test runner discoverable  | Report "no baseline available" and continue, do not fabricate  |

## Common Mistakes

### Drifting from the `<verb>-<obj>` convention

- **Problem:** Inconsistent names make listing and cleanup harder; lookup tools expect this shape.
- **Fix:** Always pick a single imperative verb + object; kebab-case only.

### Forgetting to set upstream

- **Problem:** Without upstream, `git status` / `git rebase` have no idea where to compare against, and the base branch is lost once you move on.
- **Fix:** Always run `git branch --set-upstream-to="$base_branch" "$name"` right after `git worktree add`.

### Proceeding with failing tests

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

### Hardcoding setup / test commands from a single file

- **Problem:** `package.json` exists → running `npm install` may overwrite a `pnpm-lock.yaml`; `pyproject.toml` exists → running `pip install .` ignores a committed `uv.lock`. The worktree ends up with a toolchain the real project never uses, and the "clean baseline" lies.
- **Fix:** Delegate discovery to a sub-agent. Prioritize CI / docs, then lockfiles, then manifests. Stop and ask when ambiguous.

## Example Workflow

```
Task: "fix login bug", repo comate-plugin-host, current branch feature/agent-mode.

[Resolve names: repo=comate-plugin-host, base_branch=feature/agent-mode, name=fix-login]
[mkdir -p ~/.comate/worktree/comate-plugin-host]
[git worktree add -b fix-login ~/.comate/worktree/comate-plugin-host/fix-login feature/agent-mode]
[cd ~/.comate/worktree/comate-plugin-host/fix-login]
[git branch --set-upstream-to=feature/agent-mode fix-login]
[npm install]
[npm test - 47 passing]

Worktree ready at ~/.comate/worktree/comate-plugin-host/fix-login
Branch: fix-login (upstream: feature/agent-mode)
Tests passing (47 tests, 0 failures)
Ready to implement fix-login
```

## Red Flags

**Never:**

- Place worktrees anywhere other than `~/.comate/worktree/<repo>/`
- Skip `git branch --set-upstream-to` - losing the base branch makes merge-back ambiguous
- Skip baseline test verification
- Proceed with failing tests without asking

**Always:**

- Derive `<verb>-<obj>` from the task; branch name == directory name
- Base the new branch on the current branch (`git rev-parse --abbrev-ref HEAD`)
- Bind the base branch as upstream so merge-back is recoverable via `@{upstream}`
- Auto-detect and run project setup **via a sub-agent**, respecting lockfile and CI signals
- Verify clean test baseline **via a sub-agent** using the project's canonical test command

## Integration

**Pairs with:**

- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
