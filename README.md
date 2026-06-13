# Photos Sorter

A cross-platform Tkinter desktop application that organises photos and videos into dated folder trees by reading EXIF metadata. Originals are **never** moved or deleted — the app always copies.

## Features

- **Date resolution order** (highest to lowest priority):
  1. Google Takeout sidecar JSON (`photoTakenTime`) — only when the Google Takeout option is enabled.
  2. EXIF capture date from the image (`DateTimeOriginal` → `DateTimeDigitized` → `DateTime`, read from the correct Exif sub-IFD).
  3. Filesystem timestamp — `min(birthtime, mtime)`.
  4. `Unknown/` folder — only as a last resort when no date is available.
- **Month folder format** (user-selectable):
  - `MM` — e.g. `2024/06`
  - `MM-MonthName` — e.g. `2024/06-June` (month name is localised to the selected UI language)
- **Google Takeout format** — when enabled, reads the capture date from each media file's sidecar JSON before falling back to EXIF/filesystem. `.json` sidecar files are never copied to the output.
- **Supported file types** — JPEG, PNG, HEIC/HEIF (via `pillow-heif`), `.mov`, `.mp4`. Input scanning is recursive.
- **Collision handling** — duplicate filenames are auto-renamed: `IMG_001.jpg` → `IMG_001 (1).jpg`.
- **Bilingual UI** — English and Spanish, including localised month names in the `MM-MonthName` format.
- **Persistent settings** — saved to `~/.photos_sorter/config.json`.
- **Progress display** and a final summary showing copied / skipped / unknown counts.

## Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- A modern Tcl/Tk (**8.6+ or 9.x**). The deprecated macOS system Tk 8.5 does **not** render the UI correctly.

  On macOS, install a modern Tk via Homebrew:

  ```bash
  brew install python-tk@3.13
  ```

  This also pulls in the `tcl-tk` formula. The Homebrew Python 3.13 will then use Tk 9.x automatically.

## Setup & Run

```bash
cd app
uv sync
uv run python run.py
```

### Running tests

```bash
cd app
uv run pytest
```

## Settings

Open the **Settings** window from the main UI to adjust these options:

| Setting | Options | Default |
|---|---|---|
| Month folder format | `MM` (e.g. `2024/06`) or `MM-MonthName` (e.g. `2024/06-June`) | `MM` |
| Language | English, Spanish | English |
| Google Takeout format | Enabled / Disabled | Disabled |

**Month folder format** controls the subfolder created inside each year folder. With `MM-MonthName`, the month name is localised to whichever language is selected.

**Google Takeout format** should be enabled when the input folder was exported from Google Takeout. The app will look for a sidecar `.json` file next to each media file and read its `photoTakenTime` timestamp. Sidecar files themselves are never copied.

## Building standalone executables

Dev dependencies including PyInstaller are installed automatically by `uv sync --group dev`.

### Build the installer from source

An `app/Makefile` provides one-command installer builds. Run `uv sync --group dev` once first (or let the target do it), then:

| OS | Command | Artifact |
|---|---|---|
| macOS | `cd app && make macos` | `app/Photos-Sorter-macos.dmg` |
| Windows | `cd app && make windows` | `app\Photos-Sorter-windows.exe` |
| Linux | `cd app && make linux` | `app/Photos-Sorter-linux.AppImage` |

> **Cross-compile caveat:** PyInstaller cannot cross-compile. Each target must be run on its matching OS.

Run `cd app && make help` to list all available targets, and `make clean` to remove build artefacts.

### macOS

```bash
cd app
uv run pyinstaller --windowed --name "Photos Sorter" \
  --icon=photos_sorter/assets/icon.icns \
  --add-data "photos_sorter/assets/icon.png:photos_sorter/assets" \
  run.py
open "dist/Photos Sorter.app"
```

### Windows

```bash
cd app
uv run pyinstaller --onefile --windowed --name "Photos Sorter" ^
  --icon=photos_sorter/assets/icon.ico ^
  --add-data "photos_sorter/assets/icon.png;photos_sorter/assets" ^
  run.py
# Output: dist\Photos Sorter.exe
```

### Linux

```bash
cd app
uv run pyinstaller --onefile --name "Photos Sorter" run.py
# Output: dist/Photos Sorter
```

The resulting binary can be distributed without a Python installation.

## Releases & installation

### Cutting a release

Push a version tag and GitHub Actions does the rest:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Both `v`-prefixed tags (`v1.0.0`) and bare version tags (`1.0.0`) trigger the release build.

The `Build & Release` workflow runs on macOS, Windows, and Linux runners in parallel. Each runner builds a native artifact with PyInstaller (from the `app/` directory) and uploads it to the GitHub Release created for that tag. The three download URLs are stable:

- `https://github.com/oscaroteromar/photos_sorter/releases/latest/download/Photos-Sorter-macos.dmg`
- `https://github.com/oscaroteromar/photos_sorter/releases/latest/download/Photos-Sorter-windows.exe`
- `https://github.com/oscaroteromar/photos_sorter/releases/latest/download/Photos-Sorter-linux.AppImage`

The app is **not code-signed or notarized** on any platform. Follow the platform-specific workarounds below after downloading.

### macOS — bypass Gatekeeper quarantine

macOS will refuse to open an unsigned `.app` downloaded from the internet. The old right-click → Open trick is unreliable on recent macOS versions. Instead, after dragging the app to `/Applications`, run this once in Terminal:

```bash
xattr -dr com.apple.quarantine "/Applications/Photos Sorter.app"
```

Then open the app normally from Finder or Spotlight.

### Windows — bypass SmartScreen

Windows SmartScreen will warn that the publisher is unknown. Click **More info** on the warning dialog, then click **Run anyway**.

### Linux — make the AppImage executable

```bash
chmod +x Photos-Sorter-linux.AppImage
./Photos-Sorter-linux.AppImage
```

## Project layout

```
photos_sorter/                     (repo root)
├── .github/workflows/release.yml
├── .gitignore
├── README.md
├── app/
│   ├── photos_sorter/
│   │   ├── __init__.py
│   │   ├── app.py        # Tkinter GUI
│   │   ├── config.py     # Config load/save (~/.photos_sorter/config.json)
│   │   ├── core.py       # EXIF extraction, path building, collision handling, copy logic
│   │   └── strings.py    # UI string table (en/es)
│   ├── scripts/
│   │   ├── make_dmg.sh
│   │   └── make_appimage.sh
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_core.py
│   ├── run.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── uv.lock
└── frontend/              # Future SPA (placeholder)
```
