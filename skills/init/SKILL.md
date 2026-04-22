---
name: init
description: use this skill when user ask for an AGENTS.md
---

Create or update `AGENTS.md` for this repository.

The goal is a compact instruction file that helps future sessions avoid mistakes and ramp up quickly. Every line should answer: "Would an agent likely miss this without help?" If not, leave it out.

## How to investigate

Read the highest-value sources first:

- `README*`, root manifests, workspace config, lockfiles
- build, test, lint, formatter, typecheck, and codegen config
- CI workflows and pre-commit / task runner config

Then spawn an **Explore sub-agent** to explore project's existing instruction files (`AGENTS.md`, `CLAUDE.md`, `.comate/rules/`, `.cursor/rules/` and so on) and cross-check these files against the actual codebase.

- **DON'T** read these files directly because they are **unverified claims**.
- **DON'T** ask the sub-agent to report discrepancies or errors, the main agent does not need that. Only use the verified output as input for writing `AGENTS.md`.

If architecture is still unclear after reading config and docs, inspect a small number of representative code files to find the real entrypoints, package boundaries, and execution flow. Prefer reading the files that explain how the system is wired together over random leaf files.

Prefer executable sources of truth over prose. If docs conflict with config or scripts, trust the executable source and only keep what you can verify.

## What to extract

Look for the highest-signal facts for an agent working in this repo:

- exact developer commands, especially non-obvious ones
- how to run a single test, a single package, or a focused verification step
- required command order when it matters, such as `lint -> typecheck -> test`
- monorepo or multi-package boundaries, ownership of major directories, and the real app/library entrypoints
- framework or toolchain quirks: generated code, migrations, codegen, build artifacts, special env loading, dev servers, infra deploy flow
- repo-specific style or workflow conventions that differ from defaults
- testing quirks: fixtures, integration test prerequisites, snapshot workflows, required services, flaky or expensive suites
- important constraints from existing instruction files worth preserving

Good `AGENTS.md` content is usually hard-earned context that took reading multiple files to infer.

## Questions

Only ask the user questions if the repo cannot answer something important. Use the `question` tool for one short batch at most.

Good questions:

- undocumented team conventions
- branch / PR / release expectations
- missing setup or test prerequisites that are known but not written down

Do not ask about anything the repo already makes clear.

## Output structure

Generate two files: `AGENTS.md` as a navigation map, and `ARCHITECTURE.md` as a standalone architecture reference.

### AGENTS.md (~100 lines, 3-4 sections max)

```markdown
# {Project Name}

{One sentence: what is this project.}

## Commands

{Only the 3-5 commands an agent needs most. Non-obvious flags, exact invocations.}

## Key Constraints

{5-10 bullets. Each one is a trap an agent would fall into without warning.
 Merge formatting, linting, TypeScript, conventions, testing quirks — all here as flat bullets.
 No sub-sections.}

## Project Map

{Index pointing to deeper docs. One line per entry, path + what it covers.}

- `ARCHITECTURE.md`: system architecture and package structure
- `.comate/rules/`: project-specific development rules (if present)
- `.comate/specs/`: historical spec documents from spec-mode tasks (if present)
- {other docs, rule directories, or reference files worth reading}
```

### ARCHITECTURE.md

A standalone file describing the system's high-level structure. Keep it concise, the goal is orientation, not exhaustive documentation.

Required content:

- A **mermaid diagram** showing major components and their relationships (communication flow, data flow, or dependency direction, pick whichever best explains the system)
- A **brief legend** below the diagram: one line per component explaining what it is and where it lives
- If the project is a monorepo, list packages with one-line descriptions and note the build order or dependency direction

Do NOT include detailed API surfaces, config options, or implementation details. Those belong in more specific docs.

## Writing rules

Include only high-signal, repo-specific guidance such as:

- exact commands and shortcuts the agent would otherwise guess wrong
- architecture notes that are not obvious from filenames
- conventions that differ from language or framework defaults
- setup requirements, environment quirks, and operational gotchas
- references to existing instruction sources that matter

Exclude:

- generic software advice
- long tutorials or exhaustive file trees
- obvious language conventions
- speculative claims or anything you could not verify

When in doubt, omit.

Prefer short sections and bullets. If the repo is simple, keep the file simple. If the repo is large, summarize the few structural facts that actually change how an agent should work.

If `AGENTS.md` already exists at current repo, improve it in place rather than rewriting blindly. Preserve verified useful guidance, delete fluff or stale claims, and reconcile it with the current codebase.
