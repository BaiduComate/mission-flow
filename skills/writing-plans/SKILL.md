---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write implementation plans as task contracts: goal, scope, context, acceptance criteria, constraints, and verification. Leave implementation choices to the implementer unless the spec requires a specific detail.

Assume the implementer is skilled, but new to this codebase and domain.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If working in an isolated worktree, it should have been created via the `using-git-worktrees` skill at execution time.

**Save plans to:** `.comate/specs/{feature_name}/tasks.md`

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

Each task is one coherent implementation unit that a subagent can complete, test, commit, and report back on.

- Use goal-based tasks, not mechanical micro-steps.
- Do not split one natural task into "write test", "implement", "run tests", and "commit" tasks.
- Acceptance criteria define success; constraints define boundaries.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

Write one section like this per task in `tasks.md`.

````markdown
### Task N: [Component Name]

## Goal
[Observable outcome this task must produce]

## Context
[How this task fits the approved `doc.md`, architecture, and nearby tasks]

## Scope
- In scope: [what this task may change]
- Out of scope: [nearby work this task must not do]

## Relevant Files
- Likely modify: `exact/path/to/existing.py`
- Likely create: `exact/path/to/new_file.py`
- Reference: `exact/path/to/reference.py`

## Acceptance Criteria
- [ ] [Observable behavior or deliverable]
- [ ] [Important edge case or failure behavior]
- [ ] [Integration expectation]
- [ ] [Regression expectation]

## Testing Expectations
- Unit tests: [specific behaviors to cover]
- Integration/E2E or runtime verification: [if available]
- Commands: `exact command to run`
- Expected result: [what should pass or be observable]

## Constraints
- [Required API, compatibility, dependency, style, or architecture constraint]

## Notes
[Only non-obvious guidance. Do not prescribe implementation unless required.]
````

## No Placeholders

Every task must contain a concrete contract. These are **plan failures**:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases" without saying which cases matter
- "Write tests" without concrete behaviors, commands, and expected results
- "Similar to Task N" without repeating the relevant context
- Prescribing every line of code when goal and constraints are enough
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Outcomes and acceptance criteria over implementation scripts
- Exact verification commands with expected output
- Prefer behavior-level verification: unit tests plus integration/runtime checks when available.
- Do not include full implementation code unless the exact code/API/config is itself the requirement
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Can every spec requirement be traced to a task? List gaps.

**2. Placeholder scan:** Search for the red flags above. Fix them.

**3. Type consistency:** Do names, APIs, and data shapes match across tasks?

**4. Implementation freedom:** If a task reads like a typing script, rewrite it as outcomes and acceptance criteria.

**5. Verification realism:** Include runtime or integration verification when the environment allows it.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, proceed with subagent-driven execution:

**"Plan complete and saved to `.comate/specs/{feature_name}/tasks.md`. Starting subagent-driven execution — dispatching a fresh subagent per task with review between tasks."**

- **REQUIRED SUB-SKILL:** Use subagent-driven-development
- Fresh subagent per task + two-stage review
