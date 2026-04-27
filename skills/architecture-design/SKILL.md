---
name: architecture-design
description: |
  Generate architecture and technical design documents (doc.md) for user's requirement. Must trigger this skill when:
  1. after using icafe skill, and the title of icafe card start with "【SDD】"
  2. user provides an iCafe card link/ID
  3. user describes a requirement and asks for a technical design or implementation plan
---

**Announce at start:** "正在进行调研来完成需求的架构设计"

## Dependencies

- `deepwiki`: used to retrieve deepwiki information about the project
- `icafe`: used to read iCafe card content when upstream context is available

## Input

This skill supports two input modes:

### Mode A: iCafe Story Card (from requirement-splitter)

When the user provides an iCafe Story card link or ID:

1. Use `icafe` skill (`icafe-cli card get`) to read the Story card's description
2. Follow the parent Feature link in the Story's "背景" section to read the Feature card's description
3. Extract from the Feature card: tech stack, module mapping, key findings
4. Extract from the Story card: relevant files/directories, technical notes, detailed description, dependencies

### Mode B: Raw Requirement Text (fallback)

When the user describes the requirement directly without an iCafe card, run the full research workflow in fallback mode.

## Workflow

### Mode A: With iCafe Context

After reading Story + Feature card content, you **must** launch two subagents in parallel:

1. **deepwiki subagent**: Use `references/deepwiki-agent.md` as prompt, fill in:
   - `{{REQUIREMENT}}`: Story's "目标" + "详细说明" sections
   - `{{TECH_STACK}}`: Feature's "技术栈" section
   - `{{FOCUS_MODULES}}`: module names from Story's "关注文件与目录" table

2. **explore subagent**: Use `references/explore-agent.md` as prompt, fill in:
   - `{{REQUIREMENT}}`: Story's "目标" + "详细说明" sections
   - `{{KNOWN_PATHS}}`: Story's full "关注文件与目录" table

Combine both subagent reports with the Feature card's global context (module mapping, key findings) to produce `doc.md`.

### Mode B: Without iCafe Context (fallback)

Launch two subagents in parallel:

1. **deepwiki subagent**: Use `references/deepwiki-agent.md` as prompt, fill in:
   - `{{REQUIREMENT}}`: user's requirement verbatim
   - `{{TECH_STACK}}`: leave empty
   - `{{FOCUS_MODULES}}`: relevant module names inferred from the requirement text

2. **explore subagent**: Use `references/explore-agent.md` as prompt, fill in:
   - `{{REQUIREMENT}}`: user's requirement verbatim
   - `{{KNOWN_PATHS}}`: leave empty

Combine both subagent reports to produce `doc.md`.

## Document Style

The generated `doc.md` must follow these style rules:

1. The "Architecture and Technical Design" and "Data Flow" sections must use mermaid diagrams instead of ASCII art. Use the default mermaid theme, don't set background colors manually.
2. The "Implementation Details" section must not contain full code snippets. Only include key code (e.g., function signatures, key data structures), avoid concrete implementations.
3. Only use a subset of markdown syntax: headings, bold, italic, code blocks, etc. **Don't** use horizontal line or other low-information syntax.
