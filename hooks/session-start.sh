#!/bin/bash
set -euo pipefail

script_path="${BASH_SOURCE[0]}"
case "$script_path" in
  */*) script_dir="${script_path%/*}" ;;
  *) script_dir="." ;;
esac
script_dir="$(cd -- "$script_dir" && pwd)"
skill_path="${script_dir}/../skills/using-mission-flow/SKILL.md"

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\t'/\\t}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\f'/\\f}"
  value="${value//$'\b'/\\b}"
  printf '%s' "$value"
}

printf '{"additionalContext":"'
printf '%s' '<EXTREMELY_IMPORTANT>\n'
printf '%s' 'You have mission-flow skills.\n\n'
printf '%s' 'IMPORTANT: The using-mission-flow skill content is included below. It is ALREADY LOADED - you are currently following it. Do NOT use the skill tool to load \"using-mission-flow\" again - that would be redundant.\n\n'

line_number=0
in_frontmatter=0
while IFS= read -r line || [ -n "$line" ]; do
  line_number=$((line_number + 1))

  if [ "$line_number" -eq 1 ] && [ "$line" = '---' ]; then
    in_frontmatter=1
    continue
  fi

  if [ "$in_frontmatter" -eq 1 ]; then
    if [ "$line" = '---' ]; then
      in_frontmatter=0
    fi
    continue
  fi

  json_escape "$line"
  printf '%s' '\n'
done < "$skill_path"

printf '%s' '</EXTREMELY_IMPORTANT>"}'
