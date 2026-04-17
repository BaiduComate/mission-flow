#!/usr/bin/env bash
# remote-install.sh - Download skills from stash and install to .comate/skills
#
# One-liner usage (用户直接执行):
#   curl -fsSL https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/harness/install.sh | bash
#
# Options:
#   -f, --force    Overwrite existing skill directories
#   -d, --dir DIR  Install to DIR/.comate/skills (default: current directory)

set -euo pipefail

DOWNLOAD_URL="https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/harness/skills.zip"

# --- Parse args ---
FORCE=false
INSTALL_DIR="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--force) FORCE=true; shift ;;
    -d|--dir)   INSTALL_DIR="$2"; shift 2 ;;
    *)          INSTALL_DIR="$1"; shift ;;
  esac
done

TARGET_DIR="${INSTALL_DIR}/.comate/skills"

# --- Download ---
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Downloading skills..."
if ! curl -fsSL -o "$TMP_DIR/skills.zip" "$DOWNLOAD_URL"; then
  echo "Error: Failed to download from stash."
  echo "URL: $DOWNLOAD_URL"
  exit 1
fi

echo "Extracting..."
unzip -q "$TMP_DIR/skills.zip" -d "$TMP_DIR"

# The zip contains a skills/ directory at root
if [[ -d "$TMP_DIR/skills" ]]; then
  SRC_DIR="$TMP_DIR/skills"
else
  echo "Error: Unexpected zip structure, 'skills/' directory not found."
  exit 1
fi

# --- Install ---
mkdir -p "$TARGET_DIR"
echo "Installing to $TARGET_DIR"
echo ""

for skill_path in "$SRC_DIR"/*/; do
  [[ -d "$skill_path" ]] || continue
  skill_name="$(basename "$skill_path")"

  dest="$TARGET_DIR/$skill_name"

  if [[ -e "$dest" ]]; then
    if [[ "$FORCE" == true ]]; then
      echo "  [overwrite] $skill_name"
      rm -rf "$dest"
      cp -r "$skill_path" "$dest"
    else
      echo "  [skip]      $skill_name (exists, use -f to overwrite)"
    fi
  else
    echo "  [install]   $skill_name"
    cp -r "$skill_path" "$dest"
  fi
done

echo ""
echo "Done. Skills installed to: $TARGET_DIR"
