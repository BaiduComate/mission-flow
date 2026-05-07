#!/bin/bash
cat <<'EOF'
{"additionalContext": "You have the mission-flow skill set available. Use the Skill tool to invoke them:\n\n- `ai-prd-split`: ALWAYS trigger first for ANY coding-related request (bug fixes, features, refactoring). It decides internally whether to split tasks or proceed directly.\n- `architecture-design`: Trigger when user asks for a technical design/implementation plan, or when an iCafe card title starts with 【SDD】.\n- `using-git-worktrees`: Trigger when starting feature work that needs isolation, or before executing an implementation plan.\n- `finishing-a-development-branch`: Trigger when a task is completed in a worktree dir.\n- `deepwiki`: Trigger when user needs info from a repository's DeepWiki (architecture docs, browsing wiki, semantic search)."}
EOF
