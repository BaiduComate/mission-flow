#!/usr/bin/env bash
# upload.sh - Pack skills and upload to Vercel Stash (图床)
#
# Usage:
#   ./upload.sh                    # use default app ID 5657
#   APP_ID=1234 ./upload.sh        # use custom app ID
#   ZT_TOKEN="xxx" ./upload.sh     # pass token directly
#
# Prerequisites:
#   - SECURE_ZT_GW_TOKEN: obtained from browser cookie (or pass via ZT_TOKEN env)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ID="${APP_ID:-5657}"
STASH_PATH="/harness/skills.zip"
BASE_URL="https://console.cloud.baidu-int.com/api/vercel/stash/application/${APP_ID}"
ZIP_FILE="$SCRIPT_DIR/../skills.zip"

# --- Token ---
ZT_TOKEN="${ZT_TOKEN:-}"
if [[ -z "$ZT_TOKEN" ]]; then
  echo "Error: ZT_TOKEN is not set."
  echo "Get it from browser cookie 'SECURE_ZT_GW_TOKEN' and run:"
  echo "  ZT_TOKEN=\"your_token\" ./upload.sh"
  exit 1
fi

# --- Pack skills ---
echo "Packing skills..."
(cd "$SCRIPT_DIR/.." && zip -r -q skills.zip skills/ -x "*.DS_Store")
echo "  Created: $ZIP_FILE ($(du -h "$ZIP_FILE" | cut -f1))"

# --- Upload ---
echo "Uploading to stash (app=$APP_ID, path=$STASH_PATH)..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "$BASE_URL" \
  -X PUT \
  -H 'Accept: application/json' \
  -b "SECURE_ZT_GW_TOKEN=${ZT_TOKEN}" \
  -F "path=${STASH_PATH}" \
  -F "file=@${ZIP_FILE};type=application/zip" \
  -F "cache=no-cache, must-revalidate")

if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
  echo "Upload success (HTTP $HTTP_CODE)"
  echo ""
  echo "Download URL (CDN):"
  echo "  https://vercel-static.bj.bcebos.com/stash/v1/0b72aae/comate-plus-web/7a0aaaf/harness/skills.zip"
else
  echo "Upload failed (HTTP $HTTP_CODE)"
  echo "Run with verbose mode for details:"
  echo "  ZT_TOKEN=\"...\" bash -x ./upload.sh"
  exit 1
fi
