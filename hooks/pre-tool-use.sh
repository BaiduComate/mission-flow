#!/bin/bash
set -euo pipefail

input="$(cat)"
endpoint="https://comate.baidu-int.com/api/mission-flow"

script_path="$0"
case "$script_path" in
  */*) script_dir="${script_path%/*}" ;;
  *) script_dir="." ;;
esac
plugin_dir="$(cd -- "$script_dir/.." && pwd)"
plugin_version="$(
  if [ -f "${plugin_dir}/plugin.json" ]; then
    sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"\\]*\(\\.[^"\\]*\)*\)".*/\1/p' "${plugin_dir}/plugin.json"
  fi | sed -n '1p'
)"
if [ -z "$plugin_version" ]; then plugin_version="unknown"; fi

extract_string() {
  local key="$1"
  printf '%s' "$input" \
    | tr '\n' ' ' \
    | sed -n 's/.*"'"$key"'"[[:space:]]*:[[:space:]]*"\([^"\\]*\(\\.[^"\\]*\)*\)".*/\1/p' \
    | sed 's/\\"/"/g; s/\\\\/\\/g' \
    | sed -n '1p'
}

extract_object_string() {
  local object_key="$1"
  local key="$2"
  printf '%s' "$input" \
    | tr '\n' ' ' \
    | sed -n 's/.*"'"$object_key"'"[[:space:]]*:[[:space:]]*{[^}]*"'"$key"'"[[:space:]]*:[[:space:]]*"\([^"\\]*\(\\.[^"\\]*\)*\)".*/\1/p' \
    | sed 's/\\"/"/g; s/\\\\/\\/g' \
    | sed -n '1p'
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\t'/\\t}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\f'/\\f}"
  value="${value//$'\b'/\\b}"
  printf '%s' "$value"
}

call_name="$(extract_object_string 'tool_input' 'name')"
if [ -z "$call_name" ]; then call_name="$(extract_object_string 'tool_input' 'call_name')"; fi
if [ -z "$call_name" ]; then call_name="$(extract_object_string 'tool_input' 'skill_name')"; fi
if [ -z "$call_name" ]; then call_name="$(extract_object_string 'input' 'name')"; fi
if [ -z "$call_name" ]; then call_name="$(extract_string 'call_name')"; fi
if [ -z "$call_name" ]; then call_name="$(extract_string 'skill_name')"; fi

case "$call_name" in
  ''|.*|*/*|*'..'*|*[!A-Za-z0-9._-]*) printf '{"decision":"allow"}'; exit 0 ;;
esac

if [ ! -f "${plugin_dir}/skills/${call_name}/SKILL.md" ]; then
  printf '{"decision":"allow"}'
  exit 0
fi

timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
hook_event_name="$(extract_string 'hook_event_name')"
license="$(extract_string 'license')"
cwd="$(extract_string 'cwd')"
conversation_id="$(extract_string 'conversation_id')"
tool_name="$(extract_string 'tool_name')"
tool_use_id="$(extract_string 'tool_use_id')"
model="$(extract_string 'model')"

if [ -z "$hook_event_name" ]; then hook_event_name="PreToolUse"; fi
if [ -z "$license" ]; then license="unknown"; fi

payload="{\"call_name\":\"$(json_escape "$call_name")\",\"timestamp\":\"$(json_escape "$timestamp")\",\"hook_event_name\":\"$(json_escape "$hook_event_name")\",\"user_id\":\"$(json_escape "$license")\",\"license\":\"$(json_escape "$license")\",\"input\":{\"name\":\"$(json_escape "$call_name")\"},\"cwd\":\"$(json_escape "$cwd")\",\"conversation_id\":\"$(json_escape "$conversation_id")\",\"tool_name\":\"$(json_escape "$tool_name")\",\"tool_use_id\":\"$(json_escape "$tool_use_id")\",\"model\":\"$(json_escape "$model")\",\"plugin_name\":\"mission-flow\",\"plugin_version\":\"$(json_escape "$plugin_version")\"}"

curl -fsS -m 2 -H 'Content-Type: application/json' -X POST --data "$payload" "$endpoint" >/dev/null 2>&1 || true

printf '{"decision":"allow"}'
