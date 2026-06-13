#!/usr/bin/env bash
# make_appimage.sh — Wrap "dist/Photos Sorter" (PyInstaller onefile binary)
# into a standard AppImage for distribution on Linux.
# Called by the GitHub Actions release workflow on the ubuntu runner.
# Output: Photos-Sorter-linux.AppImage (in the repo root / working directory).
set -euo pipefail

BINARY_NAME="Photos Sorter"
BINARY_PATH="dist/${BINARY_NAME}"
APPDIR="AppDir"
ICON_SRC="photos_sorter/assets/icon.png"
OUTPUT="Photos-Sorter-linux.AppImage"

echo "==> Assembling AppDir"

# Clean any previous attempt
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"

# Copy the PyInstaller single-file binary into AppDir
cp "${BINARY_PATH}" "${APPDIR}/usr/bin/photos-sorter"
chmod +x "${APPDIR}/usr/bin/photos-sorter"

# AppImage requires an icon at the root of AppDir
cp "${ICON_SRC}" "${APPDIR}/photos-sorter.png"

# AppRun — the entry point executed when the AppImage is launched
cat > "${APPDIR}/AppRun" <<'APPRUN'
#!/usr/bin/env bash
exec "$(dirname "$(readlink -f "$0")")/usr/bin/photos-sorter" "$@"
APPRUN
chmod +x "${APPDIR}/AppRun"

# .desktop file — required by appimagetool
cat > "${APPDIR}/photos-sorter.desktop" <<DESKTOP
[Desktop Entry]
Name=Photos Sorter
Exec=photos-sorter
Icon=photos-sorter
Type=Application
Categories=Graphics;
DESKTOP

echo "==> Downloading appimagetool"
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
curl -fsSL -o appimagetool "${APPIMAGETOOL_URL}"
chmod +x appimagetool

echo "==> Building AppImage"
ARCH=x86_64 ./appimagetool "${APPDIR}" "${OUTPUT}"

echo "==> Created ${OUTPUT}"
ls -lh "${OUTPUT}"
