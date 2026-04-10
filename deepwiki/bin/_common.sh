#!/bin/sh
# Common functions for deepwiki scripts

DEEPWIKI_MCP_URL="${DEEPWIKI_MCP_URL:-https://mcp-proxy.baidu-int.com/server/DeepWiki/mcp-plugin-center/mcp/}"

# Read auth token from ~/.comate/login
get_token() {
  LOGIN_FILE="$HOME/.comate/login"
  if [ ! -f "$LOGIN_FILE" ]; then
    echo "ERROR: $LOGIN_FILE not found, please login first" >&2
    exit 1
  fi
  cat "$LOGIN_FILE"
}

# Get repo name from argument or git config
# Parses formats:
#   ssh://user@host:port/baidu/devops-ai/repo
#   git@host:baidu/devops-ai/repo.git
#   https://host/baidu/devops-ai/repo.git
get_repo_name() {
  if [ -n "$1" ]; then
    echo "$1"
    return
  fi
  REMOTE_URL=$(git config remote.origin.url 2>/dev/null)
  if [ -z "$REMOTE_URL" ]; then
    echo "ERROR: not in a git repo and no repoName provided" >&2
    exit 1
  fi
  echo "$REMOTE_URL" | sed \
    -e 's|^ssh://[^/]*/||' \
    -e 's|^https\{0,1\}://[^/]*/||' \
    -e 's|^[^:]*:||' \
    -e 's|\.git$||'
}

# Call MCP tool and extract response from SSE stream
# $1 = tool name
# $2 = arguments JSON object
mcp_call() {
  TOOL_NAME="$1"
  ARGUMENTS="$2"
  TOKEN=$(get_token)

  curl -s -N --max-time 60 -X POST "$DEEPWIKI_MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "x-ac-Authorization: $TOKEN" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"$TOOL_NAME\",\"arguments\":$ARGUMENTS},\"id\":1}" \
    | grep '^data: ' \
    | sed 's/^data: //'
}
