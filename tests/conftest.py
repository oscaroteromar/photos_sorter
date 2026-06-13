"""Shared pytest fixtures for Photos Sorter tests."""

import struct
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image


def _make_jpeg_with_exif(path: Path, dt: datetime) -> None:
    """Write a minimal JPEG file with DateTimeOriginal EXIF set to `dt`.

    Args:
        path: Destination file path.
        dt: The datetime to embed as DateTimeOriginal.
    """
    img = Image.new("RGB", (10, 10), color=(100, 150, 200))

    # Build a minimal EXIF blob manually using piexif if available, else use Pillow's internal API.
    try:
        import piexif  # optional; not in our Pipfile but try gracefully

        dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict = {"Exif": {piexif.ExifIFD.DateTimeOriginal: dt_str.encode()}}
        exif_bytes = piexif.dump(exif_dict)
        img.save(path, format="JPEG", exif=exif_bytes)
    except ImportError:
        # Build a raw Exif blob: header + IFD with one entry (tag 0x9003 = DateTimeOriginal)
        dt_str = dt.strftime("%Y:%m:%d %H:%M:%S").encode("ascii") + b"\x00"  # 20 bytes with null
        # Minimal Exif: "Exif\x00\x00" + TIFF header (little-endian) + IFD
        # TIFF LE header: II + 0x002A + offset to IFD (8)
        tiff_header = b"II" + struct.pack("<H", 42) + struct.pack("<I", 8)
        # IFD: 1 entry count
        ifd_entry_count = struct.pack("<H", 1)
        # Entry: tag=0x9003, type=2 (ASCII), count=20, value_offset=26 (after IFD)
        # IFD offset=8, entry=12 bytes, next_ifd=4 bytes → data starts at 8+2+12+4=26
        ifd_entry = struct.pack("<HHII", 0x9003, 2, 20, 26)
        ifd_next = struct.pack("<I", 0)  # no next IFD
        exif_blob = b"Exif\x00\x00" + tiff_header + ifd_entry_count + ifd_entry + ifd_next + dt_str
        img.save(path, format="JPEG", exif=exif_blob)


def _make_jpeg_no_exif(path: Path) -> None:
    """Write a plain JPEG with no EXIF metadata.

    Args:
        path: Destination file path.
    """
    img = Image.new("RGB", (10, 10), color=(50, 60, 70))
    img.save(path, format="JPEG")


@pytest.fixture()
def tmp_input(tmp_path: Path) -> Path:
    """Return a temporary input directory.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        A `Path` pointing to the input subdirectory.
    """
    d = tmp_path / "input"
    d.mkdir()
    return d


@pytest.fixture()
def tmp_output(tmp_path: Path) -> Path:
    """Return a temporary output directory.

    Args:
        tmp_path: Pytest-provided temporary directory.

    Returns:
        A `Path` pointing to the output subdirectory.
    """
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture()
def jpeg_with_exif(tmp_input: Path) -> tuple[Path, datetime]:
    """Create a JPEG with a known DateTimeOriginal EXIF value.

    Args:
        tmp_input: Temporary input directory fixture.

    Returns:
        A tuple of ``(path_to_file, expected_datetime)``.
    """
    dt = datetime(2024, 3, 15, 10, 30, 0)
    p = tmp_input / "photo_exif.jpg"
    _make_jpeg_with_exif(p, dt)
    return p, dt


@pytest.fixture()
def jpeg_no_exif(tmp_input: Path) -> Path:
    """Create a JPEG without EXIF metadata.

    Args:
        tmp_input: Temporary input directory fixture.

    Returns:
        Path to the created file.
    """
    p = tmp_input / "photo_no_exif.jpg"
    _make_jpeg_no_exif(p)
    return p
