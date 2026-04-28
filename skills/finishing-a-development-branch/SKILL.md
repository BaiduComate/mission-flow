---
name: finishing-a-development-branch
description: Use when a task is completed in the worktree dir
metadata:
  version: "0.1.0"
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

**Announce at start:** "我正在使用 finishing-a-development-branch skill 来结束该任务"

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass.** Do not hardcode a test command from a single manifest file — delegate to a sub-agent, same path as `using-git-worktrees` step 4:

1. Look at what CI runs on PRs — that is the de facto test command
2. Otherwise check task runners (Makefile / justfile / `scripts` / task aliases)
3. Only fall back to language-default frameworks as a last resort
4. Run it once; report pass/fail counts and a failure summary

**If tests fail:**

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge until tests pass.
```

Stop. Don't proceed to Step 2.

**If no test command exists:** Report "no baseline available" and ask the user whether to proceed without verification. Never fabricate a test run.

**If tests pass:** Continue to Step 2.

### Step 2: Determine Base Branch

The branch created by `using-git-worktrees` has its upstream bound to the base branch. Prefer that over guessing `main` / `master`:

```bash
base_branch=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null)
```

If `@{upstream}` is unset (branch not created by `using-git-worktrees`), fall back to detection:

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask the user to confirm.

### Step 3: Present Options

**Using questions tools** to present exactly these 3 options:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Keep the branch as-is (I'll handle it later)
3. Discard this work

Which option?
```

**Don't add explanation** - keep options concise.

### Step 4: Execute Choice

#### Option 1: Merge Locally

```bash
# Switch to base branch
git checkout <base-branch>

# Pull latest
git pull

# Merge feature branch
git merge <feature-branch>

# Verify tests on merged result (same discovery path as Step 1)

# If tests pass
git branch -d <feature-branch>
```

Then: Cleanup worktree (Step 5)

#### Option 2: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 3: Discard

**Confirm first:**

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation.

If confirmed:

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: Cleanup worktree (Step 5)

### Step 5: Cleanup Worktree

**For Options 1, 3:**

Worktrees created by `using-git-worktrees` live at `~/.comate/worktree/<repo>/<name>`. Check if the current branch is running inside one:

```bash
git worktree list | grep "$(git rev-parse --show-toplevel)"
```

If yes, remove it from **outside** the worktree (you cannot remove the worktree you are standing in):

```bash
cd "$(git rev-parse --git-common-dir)/.."   # jump to main repo
git worktree remove ~/.comate/worktree/<repo>/<name>
```

**For Option 2:** Keep worktree.

## Quick Reference

| Option           | Merge | Keep Worktree | Cleanup Branch |
| ---------------- | ----- | ------------- | -------------- |
| 1. Merge locally | ✓     | -             | ✓              |
| 2. Keep as-is    | -     | ✓             | -              |
| 3. Discard       | -     | -             | ✓ (force)      |

## Common Mistakes

**Skipping test verification**

- **Problem:** Merge broken code
- **Fix:** Always verify tests before offering options

**Open-ended questions**

- **Problem:** "What should I do next?" → ambiguous
- **Fix:** Present exactly 3 structured options

**Automatic worktree cleanup**

- **Problem:** Remove worktree when it might still be needed (Option 2)
- **Fix:** Only keep the worktree for Option 2; remove for 1, 3

**Hardcoding test commands**

- **Problem:** `npm test` / `pytest` / `cargo test` may not match the project's canonical command; produces false verification
- **Fix:** Delegate test discovery to a sub-agent; follow CI → task runner → language default

**No confirmation for discard**

- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**

- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation

**Always:**

- Verify tests before offering options (via sub-agent, never hardcoded commands)
- Prefer `@{upstream}` for base branch before falling back to detection
- Present exactly 3 options
- Get typed confirmation for Option 3
- Keep the worktree only for Option 2

## Integration

**Pairs with:**

- **using-git-worktrees** - Cleans up worktree created by that skill
