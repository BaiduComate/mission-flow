#!/usr/bin/env bash
# install.sh - Link project skills to a .comate/skills directory
#
# Usage:
#   ./install.sh                  # links to ~/.comate/skills
#   ./install.sh /path/to/proj    # links to /path/to/proj/.comate/skills
#   ./install.sh -f               # force overwrite existing files
#   ./install.sh -f /path/to/proj # force overwrite in specified project

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"

FORCE=false
if [[ "${1:-}" == "-f" || "${1:-}" == "--force" ]]; then
  FORCE=true
  shift
fi

if [[ $# -ge 1 ]]; then
  TARGET_DIR="$(realpath "$1")/.comate/skills"
else
  TARGET_DIR="$HOME/.comate/skills"
fi

mkdir -p "$TARGET_DIR"

echo "Linking skills → $TARGET_DIR"
echo ""

for skill_path in "$SKILLS_SRC"/*/; do
  skill_name="$(basename "$skill_path")"
  link="$TARGET_DIR/$skill_name"

  if [[ -L "$link" ]]; then
    current_target="$(readlink "$link")"
    if [[ "$current_target" == "$skill_path" ]]; then
      echo "  [skip]   $skill_name (already linked)"
      continue
    else
      echo "  [update] $skill_name ($current_target → $skill_path)"
      ln -sf "$skill_path" "$link"
    fi
  elif [[ -e "$link" ]]; then
    if [[ "$FORCE" == true ]]; then
      echo "  [force]  $skill_name"
      rm -rf "$link"
      ln -s "$skill_path" "$link"
    else
      echo "  [warn]   $skill_name — target exists and is not a symlink, skipping (use -f to overwrite)"
    fi
  else
    echo "  [link]   $skill_name"
    ln -s "$skill_path" "$link"
  fi
done

echo ""
echo "Done. Skills available in: $TARGET_DIR"
