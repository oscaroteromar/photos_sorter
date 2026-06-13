#!/usr/bin/env bash
# make_dmg.sh — Package "dist/Photos Sorter.app" into a distributable DMG.
# Called by the GitHub Actions release workflow on the macos runner.
# Output: Photos-Sorter-macos.dmg (in the repo root / working directory).
set -euo pipefail

APP_NAME="Photos Sorter"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="Photos-Sorter-macos.dmg"
# Temporary intermediate DMG before compression
TMP_DMG="tmp_Photos_Sorter.dmg"
VOLUME_NAME="${APP_NAME}"

echo "==> Creating DMG from ${APP_PATH}"

# Create a writable DMG large enough to hold the .app bundle
hdiutil create \
  -volname "${VOLUME_NAME}" \
  -srcfolder "${APP_PATH}" \
  -ov \
  -format UDRW \
  "${TMP_DMG}"

# Convert to a compressed, read-only DMG for distribution
hdiutil convert "${TMP_DMG}" \
  -format UDZO \
  -imagekey zlib-level=9 \
  -o "${DMG_NAME}"

rm -f "${TMP_DMG}"

echo "==> Created ${DMG_NAME}"
ls -lh "${DMG_NAME}"
