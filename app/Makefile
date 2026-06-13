# Photos Sorter — installer build targets
#
# NOTE: PyInstaller cannot cross-compile. Each target must be run on its
# matching OS:  `make macos` on macOS, `make windows` on Windows,
# `make linux` on Linux.
#
# Prerequisites: Python 3.13+ and the uv package manager.
# Run `uv sync --group dev` once to install deps (including PyInstaller),
# or simply rely on the `uv sync` step embedded in each target below.

.PHONY: help macos windows linux clean

help:
	@echo ""
	@echo "Photos Sorter — installer build targets"
	@echo ""
	@echo "  make macos    Build Photos-Sorter-macos.dmg   (run on macOS)"
	@echo "  make windows  Build Photos-Sorter-windows.exe (run on Windows)"
	@echo "  make linux    Build Photos-Sorter-linux.AppImage (run on Linux)"
	@echo "  make clean    Remove build artefacts"
	@echo ""
	@echo "PyInstaller cannot cross-compile: run each target on its matching OS."
	@echo "Run 'uv sync --group dev' once to install deps (including PyInstaller)."
	@echo ""

macos:
	uv sync --group dev
	uv run pyinstaller \
		--windowed \
		--name "Photos Sorter" \
		--icon=photos_sorter/assets/icon.icns \
		--add-data "photos_sorter/assets/icon.png:photos_sorter/assets" \
		run.py
	bash scripts/make_dmg.sh

windows:
	uv sync --group dev
	uv run pyinstaller \
		--onefile \
		--windowed \
		--name "Photos Sorter" \
		--icon=photos_sorter/assets/icon.ico \
		--add-data "photos_sorter/assets/icon.png;photos_sorter/assets" \
		run.py
	copy "dist\Photos Sorter.exe" "Photos-Sorter-windows.exe"

linux:
	uv sync --group dev
	uv run pyinstaller \
		--onefile \
		--name "Photos Sorter" \
		--add-data "photos_sorter/assets/icon.png:photos_sorter/assets" \
		run.py
	bash scripts/make_appimage.sh

clean:
	rm -rf build dist AppDir *.spec
	rm -f Photos-Sorter-macos.dmg Photos-Sorter-windows.exe Photos-Sorter-linux.AppImage
