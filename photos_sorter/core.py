"""Core logic: EXIF extraction, destination-path generation, collision handling, and copy operation.

All functions here are pure / side-effect-free where possible so they can be unit-tested
without a running display or real filesystem (except `copy_file`).
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS
import pillow_heif

# Register HEIF/HEIC support with Pillow once at import time.
pillow_heif.register_heif_opener()

# EXIF tag ids
_EXIF_DATETIME_ORIGINAL = 36867   # DateTimeOriginal — lives in the Exif sub-IFD (0x8769)
_EXIF_DATETIME_DIGITIZED = 36868  # DateTimeDigitized — also in the Exif sub-IFD
_EXIF_DATETIME_BASE = 306         # DateTime — base IFD
_EXIF_SUB_IFD = 0x8769            # Pointer to the Exif sub-IFD inside the base IFD
_EXIF_DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}
SUPPORTED_VIDEO_EXTENSIONS = {".mov", ".mp4"}
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS

MONTH_NAMES_EN = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

MONTH_NAMES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

_MONTH_NAMES_BY_LANG: dict[str, dict[int, str]] = {
    "en": MONTH_NAMES_EN,
    "es": MONTH_NAMES_ES,
}


def read_takeout_date(media_path: Path) -> Optional[datetime]:
    """Return the photoTakenTime from a Google Takeout sidecar JSON, or None.

    Locates the sidecar by trying several naming conventions next to the media file:
    ``{name}.suppl.json``, ``{name}.json``, ``{name}.supplemental-metadata.json``, and finally
    a directory scan for any file starting with the media filename and ending in ``.json``.

    Args:
        media_path: Path to the media file.

    Returns:
        A `datetime` parsed from ``photoTakenTime.timestamp``, or None on any error.
    """
    parent = media_path.parent
    name = media_path.name
    candidates = [
        parent / f"{name}.suppl.json",
        parent / f"{name}.json",
        parent / f"{name}.supplemental-metadata.json",
    ]
    sidecar: Optional[Path] = None
    for c in candidates:
        if c.exists():
            sidecar = c
            break
    if sidecar is None:
        for f in parent.iterdir():
            if f.name.startswith(name) and f.name.endswith(".json"):
                sidecar = f
                break
    if sidecar is None:
        return None
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        timestamp = data["photoTakenTime"]["timestamp"]
        return datetime.fromtimestamp(int(timestamp))
    except Exception:  # noqa: BLE001 — treat any error as "no date"
        return None


def read_exif_date(file_path: Path) -> Optional[datetime]:
    """Attempt to read the EXIF DateTimeOriginal tag from an image file.

    For video files or files without EXIF data, returns None.

    Args:
        file_path: Path to the image file.

    Returns:
        A `datetime` object if DateTimeOriginal is found and parseable, otherwise None.
    """
    suffix = file_path.suffix.lower()
    if suffix in SUPPORTED_VIDEO_EXTENSIONS:
        return None
    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        return None

    try:
        with Image.open(file_path) as img:
            exif_data = img.getexif()
            if exif_data is None:
                return None

            # Build the list of candidate raw values to try in priority order:
            # 1. DateTimeOriginal (36867) from the Exif sub-IFD
            # 2. DateTimeDigitized (36868) from the Exif sub-IFD
            # 3. DateTime (306) from the base IFD
            candidates: list = []
            try:
                sub_ifd = exif_data.get_ifd(_EXIF_SUB_IFD)
                candidates.append(sub_ifd.get(_EXIF_DATETIME_ORIGINAL))
                candidates.append(sub_ifd.get(_EXIF_DATETIME_DIGITIZED))
            except Exception:  # noqa: BLE001 — no sub-IFD present
                pass
            candidates.append(exif_data.get(_EXIF_DATETIME_BASE))

            for raw in candidates:
                if not raw:
                    continue
                try:
                    return datetime.strptime(str(raw).strip(), _EXIF_DATETIME_FORMAT)
                except (ValueError, TypeError):
                    continue
            return None
    except Exception:  # noqa: BLE001 — treat any error as "no date"
        return None


def get_filesystem_date(file_path: Path) -> Optional[datetime]:
    """Return the earliest filesystem timestamp for a file as a `datetime`.

    Uses `min(st_birthtime, st_mtime)` on platforms that expose `st_birthtime` (e.g. macOS),
    falling back to `st_mtime` (and `st_ctime`) where it is not available. Returns `None` only
    if `os.stat` raises (e.g. the file does not exist).

    Args:
        file_path: Path to the file.

    Returns:
        A `datetime` representing the earliest available filesystem timestamp, or `None` on error.
    """
    try:
        st = os.stat(file_path)
        birthtime = getattr(st, "st_birthtime", None)
        mtime = st.st_mtime
        ctime = st.st_ctime
        candidates = [t for t in [birthtime, mtime, ctime] if t is not None]
        return datetime.fromtimestamp(min(candidates))
    except OSError:
        return None


def build_dest_subpath(date: datetime, month_format: str, language: str = "en") -> Path:
    """Build the relative destination sub-path (year/month folder) for a given date and format.

    The structure is always ``<year>/<month_part>``, where `month_part` is determined by `month_format`.
    Unknown or invalid `month_format` values fall back gracefully to the numeric ``MM`` behavior.

    Args:
        date: The date to use for constructing the path.
        month_format: One of the MONTH_FORMAT_* constants from `config` — ``"MM"`` or ``"MM-MonthName"``.
        language: Language code (``"en"`` or ``"es"``) used to localise month names when `month_format`
            is ``"MM-MonthName"``. Defaults to English for any unrecognised code.

    Returns:
        A relative `Path` representing the destination folder (e.g. ``Path("2024/06")``).
    """
    year = date.year
    month = date.month
    month_str = f"{month:02d}"
    month_names = _MONTH_NAMES_BY_LANG.get(language, MONTH_NAMES_EN)

    match month_format:
        case "MM-MonthName":
            return Path(str(year)) / f"{month_str}-{month_names[month]}"
        case _:
            # "MM" and any unrecognised/legacy value all fall back to numeric month.
            return Path(str(year)) / month_str


def resolve_dest_path(
    output_root: Path,
    date: Optional[datetime],
    month_format: str,
    language: str = "en",
    file_path: Optional[Path] = None,
) -> Path:
    """Determine the full destination directory for a file.

    Uses a three-tier date fallback: EXIF date → filesystem date → ``Unknown/``.
    When `date` (EXIF) is None and `file_path` is provided, the filesystem timestamp
    (`min(birthtime, mtime)`) is used instead. Only files where both EXIF and filesystem
    timestamps are unavailable end up in ``Unknown/``.

    Args:
        output_root: The root output directory chosen by the user.
        date: The EXIF date, or None if not available.
        month_format: One of the MONTH_FORMAT_* constants from `config`.
        language: Language code used to localise month names (``"en"`` or ``"es"``).
        file_path: Optional path to the source file, used to read filesystem timestamps
            when `date` is None.

    Returns:
        A `Path` pointing to the destination directory (not yet created).
    """
    resolved = date
    if resolved is None and file_path is not None:
        resolved = get_filesystem_date(file_path)
    if resolved is None:
        return output_root / "Unknown"

    subpath = build_dest_subpath(resolved, month_format, language)
    return output_root / subpath


def resolve_collision_free_name(dest_dir: Path, filename: str) -> Path:
    """Return a collision-free destination path, appending `` (N)`` suffixes as needed.

    Args:
        dest_dir: The directory where the file will be written.
        filename: The desired filename (e.g. ``"IMG_001.jpg"``).

    Returns:
        A `Path` inside `dest_dir` that does not currently exist.
    """
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    candidate = dest_dir / filename
    counter = 1
    while candidate.exists():
        candidate = dest_dir / f"{stem} ({counter}){suffix}"
        counter += 1
    return candidate


def copy_file(
    src: Path,
    output_root: Path,
    month_format: str,
    language: str = "en",
    google_takeout: bool = False,
) -> tuple[str, Optional[Path]]:
    """Copy a single file to its date-based destination, handling collisions.

    The source file is never moved or deleted. Files without an EXIF date are always
    copied to the ``Unknown/`` subfolder and reported with status ``"unknown"``.

    Args:
        src: Absolute path to the source file.
        output_root: Root of the output directory tree.
        month_format: One of the MONTH_FORMAT_* constants from `config`.
        language: Language code used to localise month names (``"en"`` or ``"es"``).
        google_takeout: When True, attempt to read the capture date from a Google Takeout
            sidecar JSON before falling back to EXIF/filesystem timestamps.

    Returns:
        A tuple ``(status, dest_path)`` where status is ``"copied"``, ``"skipped"``,
        or ``"unknown"``, and ``dest_path`` is the path the file was written to
        (or None for skipped files).
    """
    suffix = src.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return ("skipped", None)

    date = read_takeout_date(src) if google_takeout else None
    if date is None:
        date = read_exif_date(src)
    dest_dir = resolve_dest_path(output_root, date, month_format, language, file_path=src)
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = resolve_collision_free_name(dest_dir, src.name)
    shutil.copy2(src, dest_path)

    status = "unknown" if dest_dir == output_root / "Unknown" else "copied"
    return (status, dest_path)


def collect_files(input_root: Path) -> list[Path]:
    """Recursively collect all supported files under `input_root`.

    Args:
        input_root: Directory to scan.

    Returns:
        A sorted list of `Path` objects for each supported file found.
    """
    files = []
    for p in input_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(p)
    return sorted(files)
