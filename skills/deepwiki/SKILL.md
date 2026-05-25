---
name: deepwiki
description: Use when the user needs information from a repository's DeepWiki or wiki-style documentation, such as understanding architecture, browsing documentation structure, reading a specific page, or semantically searching repo docs. Do not use for direct source-code inspection, code modification, runtime debugging, test execution, or general web search.
metadata:
  version: 0.2.0
---

# DeepWiki

Use the bundled CLI wrappers in `bin/` to query DeepWiki for a repository's table of contents, page content, and semantic search results.

## Preconditions

- Ensure the auth token exists at `~/.comate/login`.
- Ensure network access to `mcp-proxy.baidu-int.com`.
- **Run commands from inside the target git repository**, or pass `repoName` explicitly. The scripts call `git config remote.origin.url` to auto-detect the repo; running them from outside a git repo (e.g. from the skill directory itself) will fail with `ERROR: not in a git repo and no repoName provided`.

## Commands

Use the scripts under this skill's `bin/` directory.

### Get the wiki structure

```bash
bin/deepwiki-toc [repoName]
```

- Omit `repoName` to auto-detect it from `git config remote.origin.url`.
- Use this first for architecture questions, broad exploration, or when the correct page path is unknown.

### Read a specific page

```bash
bin/deepwiki-read <path> [repoName]
```

- Pass the page path using **Chinese names only, without numeric prefixes**.
- The TOC displays entries like `3.1 文本模型管理`; the correct path is `编辑器核心/文本模型管理`, not `3.1 文本模型管理` or `文本模型管理`.
- Path format rules:
  - Sub-pages: `父级名/子页面名` (e.g. `编辑器核心/文本模型管理`)
  - Top-level leaf pages (no children in the TOC): just the page name (e.g. `快速开始`)
  - Top-level sections that have children may have empty content; read their sub-pages instead.
- Use this after `deepwiki-toc` when the question maps to a known page or section.

### Search wiki content semantically

```bash
bin/deepwiki-search <query> [repoName]
```

- Pass a natural-language question.
- Use this for fuzzy questions, terminology lookup, or when the exact page is unclear.

## Workflow

1. Start with `bin/deepwiki-toc` for architecture, overview, or documentation-structure questions.
2. Use `bin/deepwiki-read` when the user asks about a specific page or when the TOC reveals an obviously relevant section.
3. Use `bin/deepwiki-search` for fuzzy or cross-cutting questions.
4. If search results are ambiguous, fall back to TOC plus targeted page reads.
5. Summarize findings for the user in plain language instead of returning raw JSON-RPC output.

## Output Handling

The scripts return a JSON-RPC envelope whose useful payload is nested JSON text.

Extraction flow:

1. Parse the outer JSON response.
2. Read `result.content[0].text`.
3. Parse that string as JSON.
4. Use `content[].text` as the actual page or search content.
5. For search results, also use `page` and `range` when citing where a match came from.

Do not dump the raw envelope to the user unless they explicitly ask for it. Prefer a concise answer with page names, key findings, and any uncertainty.

## Repo Resolution

- Accept an explicit `repoName` whenever the caller already knows the target repository.
- Otherwise rely on auto-detection from `git config remote.origin.url`.
- The helper currently supports remote formats such as:
  - `ssh://user@host:port/baidu/devops-ai/repo`
  - `git@host:baidu/devops-ai/repo.git`
  - `https://host/baidu/devops-ai/repo.git`

## Failure Handling

- If auth is missing, stop and tell the user to log in first.
- If repo auto-detection fails, ask for an explicit `repoName`.
- If search returns weak or noisy results, inspect the TOC and read likely pages directly.
- If a page returns `400 未找到路径`: the path does not exist. Strip any numeric prefixes and ensure the parent name is included (e.g. use `内置扩展/主题和外观扩展`, not `6.3 主题和外观扩展`). Refresh the TOC and retry with the exact path.
- If a page returns `400 该wiki页面内容为空`: the path is valid but the page has no content (common for top-level section nodes). Read its sub-pages instead.

## Environment

- `DEEPWIKI_MCP_URL`: override the MCP proxy URL. Default is `https://mcp-proxy.baidu-int.com/server/DeepWiki/mcp-plugin-center/mcp/`.

## Example

For a question like `这个仓库的架构是什么？`, run from **inside the target repository**:

```bash
# Step 1: get the TOC to see page names
cd /path/to/your-repo
bin/deepwiki-toc

# TOC might show:
#   - 3 编辑器核心
#     - 3.1 文本模型管理
#     - 3.2 视图渲染引擎
#   - 6 内置扩展
#     - 6.3 主题和外观扩展

# Step 2: read relevant pages — strip the numbers, include the parent for sub-pages
bin/deepwiki-read "编辑器核心/文本模型管理"       # ✓ correct
bin/deepwiki-read "内置扩展/主题和外观扩展"       # ✓ correct

# Wrong formats (all return 400):
# bin/deepwiki-read "3.1 文本模型管理"            # ✗ has numeric prefix
# bin/deepwiki-read "文本模型管理"                # ✗ missing parent path
# bin/deepwiki-read "6.3 主题和外观扩展"          # ✗ has numeric prefix
```
