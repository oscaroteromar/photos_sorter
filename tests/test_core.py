"""Unit tests for photos_sorter.core."""

import os
from datetime import datetime
from pathlib import Path

import piexif
import pytest
from PIL import Image

from photos_sorter.core import (
    build_dest_subpath,
    collect_files,
    copy_file,
    get_filesystem_date,
    read_exif_date,
    read_takeout_date,
    resolve_collision_free_name,
    resolve_dest_path,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_jpeg_with_exif(path: Path, dt: datetime) -> None:
    """Write a JPEG embedding `dt` as DateTimeOriginal in the Exif sub-IFD (tag 36867).

    Uses piexif to ensure the tag is placed in the proper Exif sub-IFD so that
    Pillow's `get_ifd(0x8769).get(36867)` retrieves it correctly.

    Args:
        path: Destination path.
        dt: Datetime to embed.
    """
    img = Image.new("RGB", (8, 8), color=(10, 20, 30))
    dt_str = dt.strftime("%Y:%m:%d %H:%M:%S").encode("ascii")
    exif_dict = {"Exif": {piexif.ExifIFD.DateTimeOriginal: dt_str}}
    img.save(path, format="JPEG", exif=piexif.dump(exif_dict))


def _write_plain_jpeg(path: Path) -> None:
    """Write a JPEG with no EXIF.

    Args:
        path: Destination path.
    """
    Image.new("RGB", (8, 8), color=(200, 200, 200)).save(path, format="JPEG")


def _write_plain_png(path: Path) -> None:
    """Write a PNG with no EXIF.

    Args:
        path: Destination path.
    """
    Image.new("RGB", (8, 8), color=(200, 200, 200)).save(path, format="PNG")


# ---------------------------------------------------------------------------
# EXIF extraction
# ---------------------------------------------------------------------------


class TestReadExifDate:
    def test_jpeg_with_exif_returns_datetime(self, tmp_path: Path) -> None:
        """Reading a JPEG with embedded DateTimeOriginal returns the correct datetime."""
        p = tmp_path / "img.jpg"
        expected = datetime(2023, 6, 21, 14, 0, 0)
        _write_jpeg_with_exif(p, expected)
        result = read_exif_date(p)
        assert result == expected

    def test_jpeg_without_exif_returns_none(self, tmp_path: Path) -> None:
        """Reading a JPEG with no EXIF returns None."""
        p = tmp_path / "img.jpg"
        _write_plain_jpeg(p)
        assert read_exif_date(p) is None

    def test_png_without_exif_returns_none(self, tmp_path: Path) -> None:
        """Reading a PNG with no EXIF returns None."""
        p = tmp_path / "img.png"
        _write_plain_png(p)
        assert read_exif_date(p) is None

    def test_video_returns_none(self, tmp_path: Path) -> None:
        """Video files are not parsed for EXIF and return None."""
        p = tmp_path / "clip.mov"
        p.write_bytes(b"not really a video")
        assert read_exif_date(p) is None

    def test_nonexistent_file_returns_none(self, tmp_path: Path) -> None:
        """A file that does not exist returns None instead of raising."""
        p = tmp_path / "ghost.jpg"
        assert read_exif_date(p) is None

    def test_unsupported_extension_returns_none(self, tmp_path: Path) -> None:
        """Files with unsupported extensions return None without attempting a read."""
        p = tmp_path / "doc.pdf"
        p.write_bytes(b"%PDF-1.0")
        assert read_exif_date(p) is None

    def test_jpeg_with_exif_sub_ifd_date_returns_datetime(self, tmp_path: Path) -> None:
        """DateTimeOriginal stored in the Exif sub-IFD (tag 36867) is read correctly.

        This is a regression test for the bug where getexif().get(36867) always returned
        None because tag 36867 lives in the Exif sub-IFD, not the base IFD.
        """
        p = tmp_path / "sub_ifd.jpg"
        expected = datetime(2023, 1, 7, 21, 1, 58)
        dt_str = expected.strftime("%Y:%m:%d %H:%M:%S").encode("ascii")
        exif_dict = {
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: dt_str,
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        img = Image.new("RGB", (8, 8), color=(10, 20, 30))
        img.save(p, format="JPEG", exif=exif_bytes)
        result = read_exif_date(p)
        assert result == expected

    def test_jpeg_with_base_ifd_datetime_fallback(self, tmp_path: Path) -> None:
        """DateTime (tag 306) in the base IFD is used as a fallback when sub-IFD has no date."""
        p = tmp_path / "base_ifd.jpg"
        expected = datetime(2021, 5, 15, 10, 30, 0)
        dt_str = expected.strftime("%Y:%m:%d %H:%M:%S").encode("ascii")
        # Only populate the 0th (base) IFD — no Exif sub-IFD date tags.
        exif_dict = {
            "0th": {
                piexif.ImageIFD.DateTime: dt_str,
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        img = Image.new("RGB", (8, 8), color=(10, 20, 30))
        img.save(p, format="JPEG", exif=exif_bytes)
        result = read_exif_date(p)
        assert result == expected


# ---------------------------------------------------------------------------
# Filesystem date extraction
# ---------------------------------------------------------------------------


class TestGetFilesystemDate:
    def test_returns_datetime_for_existing_file(self, tmp_path: Path) -> None:
        """get_filesystem_date returns a datetime for an existing file."""
        p = tmp_path / "img.jpg"
        _write_plain_jpeg(p)
        result = get_filesystem_date(p)
        assert isinstance(result, datetime)

    def test_uses_mtime_when_set(self, tmp_path: Path) -> None:
        """When mtime is set to a known past timestamp, get_filesystem_date reflects it."""
        p = tmp_path / "img.jpg"
        _write_plain_jpeg(p)
        known_ts = datetime(2022, 4, 15, 12, 0, 0).timestamp()
        os.utime(p, (known_ts, known_ts))
        result = get_filesystem_date(p)
        assert result is not None
        # The result should be at or before 2022-04-15 (birthtime may be older on some platforms).
        assert result <= datetime(2022, 4, 15, 12, 0, 1)

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        """get_filesystem_date returns None when the file does not exist."""
        p = tmp_path / "ghost.jpg"
        assert get_filesystem_date(p) is None


# ---------------------------------------------------------------------------
# Destination path generation
# ---------------------------------------------------------------------------


class TestBuildDestSubpath:
    def test_mm_numeric(self) -> None:
        """MM format produces a two-level year/month path like ``2024/03``."""
        dt = datetime(2024, 3, 15)
        assert build_dest_subpath(dt, "MM") == Path("2024/03")

    def test_mm_monthname_english(self) -> None:
        """MM-MonthName format appends the English month name."""
        dt = datetime(2024, 3, 15)
        assert build_dest_subpath(dt, "MM-MonthName", "en") == Path("2024/03-March")

    def test_mm_monthname_spanish(self) -> None:
        """MM-MonthName format appends the Spanish month name when language is 'es'."""
        dt = datetime(2024, 6, 15)
        assert build_dest_subpath(dt, "MM-MonthName", "es") == Path("2024/06-Junio")

    def test_unknown_format_falls_back_to_mm(self) -> None:
        """An unrecognised format string falls back to numeric MM behaviour."""
        dt = datetime(2024, 1, 1)
        assert build_dest_subpath(dt, "bad-format") == Path("2024/01")

    def test_zero_padded_month(self) -> None:
        """Single-digit months are zero-padded."""
        dt = datetime(2024, 1, 5)
        assert build_dest_subpath(dt, "MM") == Path("2024/01")

    def test_december_english(self) -> None:
        """December (12) is handled correctly in English."""
        dt = datetime(2022, 12, 31)
        assert build_dest_subpath(dt, "MM-MonthName", "en") == Path("2022/12-December")

    def test_december_spanish(self) -> None:
        """December (12) is handled correctly in Spanish."""
        dt = datetime(2022, 12, 31)
        assert build_dest_subpath(dt, "MM-MonthName", "es") == Path("2022/12-Diciembre")

    def test_june_english(self) -> None:
        """June produces the correct English month name."""
        dt = datetime(2024, 6, 15)
        assert build_dest_subpath(dt, "MM-MonthName", "en") == Path("2024/06-June")


# ---------------------------------------------------------------------------
# Collision handling
# ---------------------------------------------------------------------------


class TestResolveCollisionFreeName:
    def test_no_collision(self, tmp_path: Path) -> None:
        """If the filename does not exist, it is returned as-is."""
        result = resolve_collision_free_name(tmp_path, "photo.jpg")
        assert result == tmp_path / "photo.jpg"

    def test_first_collision(self, tmp_path: Path) -> None:
        """When the filename exists, a `` (1)`` suffix is appended."""
        (tmp_path / "photo.jpg").write_bytes(b"x")
        result = resolve_collision_free_name(tmp_path, "photo.jpg")
        assert result == tmp_path / "photo (1).jpg"

    def test_second_collision(self, tmp_path: Path) -> None:
        """When both the base and `` (1)`` exist, `` (2)`` is used."""
        (tmp_path / "photo.jpg").write_bytes(b"x")
        (tmp_path / "photo (1).jpg").write_bytes(b"x")
        result = resolve_collision_free_name(tmp_path, "photo.jpg")
        assert result == tmp_path / "photo (2).jpg"


# ---------------------------------------------------------------------------
# Dateless handling
# ---------------------------------------------------------------------------


class TestResolveDestPath:
    def test_with_date_uses_format(self, tmp_path: Path) -> None:
        """When a date is provided, the dest path uses the chosen date format."""
        dt = datetime(2024, 7, 4)
        dest = resolve_dest_path(tmp_path, dt, "MM")
        assert dest == tmp_path / "2024" / "07"

    def test_dateless_no_file_path_goes_to_unknown(self, tmp_path: Path) -> None:
        """With no date and no file_path, the file goes to ``Unknown/``."""
        dest = resolve_dest_path(tmp_path, None, "MM")
        assert dest == tmp_path / "Unknown"

    def test_dateless_with_file_path_uses_filesystem_date(self, tmp_path: Path) -> None:
        """With no EXIF date but a file_path, filesystem mtime is used instead of Unknown."""
        p = tmp_path / "img.jpg"
        _write_plain_jpeg(p)
        # Set mtime to a known past date (2022-04-15).
        known_ts = datetime(2022, 4, 15, 12, 0, 0).timestamp()
        os.utime(p, (known_ts, known_ts))
        dest = resolve_dest_path(tmp_path, None, "MM", file_path=p)
        assert dest == tmp_path / "2022" / "04"

    def test_exif_date_wins_over_filesystem(self, tmp_path: Path) -> None:
        """EXIF date takes priority even when filesystem mtime differs."""
        p = tmp_path / "img.jpg"
        exif_dt = datetime(2020, 1, 10, 0, 0, 0)
        _write_jpeg_with_exif(p, exif_dt)
        # Set mtime to a different date.
        other_ts = datetime(2018, 6, 1, 0, 0, 0).timestamp()
        os.utime(p, (other_ts, other_ts))
        date = read_exif_date(p)
        dest = resolve_dest_path(tmp_path, date, "MM", file_path=p)
        assert dest == tmp_path / "2020" / "01"


# ---------------------------------------------------------------------------
# copy_file integration
# ---------------------------------------------------------------------------


class TestCopyFile:
    def test_copies_jpeg_with_exif(self, tmp_path: Path) -> None:
        """A JPEG with EXIF is copied to the correct date folder, original is untouched."""
        src = tmp_path / "input" / "photo.jpg"
        src.parent.mkdir()
        out = tmp_path / "output"
        out.mkdir()

        dt = datetime(2023, 8, 20, 9, 0, 0)
        _write_jpeg_with_exif(src, dt)

        status, dest = copy_file(src, out, "MM")
        assert status == "copied"
        assert dest is not None
        assert dest.exists()
        assert src.exists(), "Original must not be deleted"
        assert dest == out / "2023" / "08" / "photo.jpg"

    def test_copies_no_exif_uses_filesystem_date(self, tmp_path: Path) -> None:
        """A JPEG without EXIF is sorted by its filesystem mtime, not sent to Unknown/."""
        src = tmp_path / "input" / "photo.jpg"
        src.parent.mkdir()
        out = tmp_path / "output"
        out.mkdir()
        _write_plain_jpeg(src)
        known_ts = datetime(2022, 4, 15, 12, 0, 0).timestamp()
        os.utime(src, (known_ts, known_ts))

        status, dest = copy_file(src, out, "MM")
        assert status == "copied"
        assert dest is not None
        assert dest.parent == out / "2022" / "04"

    def test_unsupported_file_is_skipped(self, tmp_path: Path) -> None:
        """Files with unsupported extensions are skipped."""
        src = tmp_path / "document.pdf"
        src.write_bytes(b"%PDF")
        out = tmp_path / "output"
        out.mkdir()

        status, dest = copy_file(src, out, "MM")
        assert status == "skipped"
        assert dest is None

    def test_collision_auto_rename(self, tmp_path: Path) -> None:
        """When a file already exists in the destination, a `` (1)`` suffix is used."""
        src1 = tmp_path / "input" / "img.jpg"
        src2 = tmp_path / "input2" / "img.jpg"
        src1.parent.mkdir()
        src2.parent.mkdir()
        out = tmp_path / "output"
        out.mkdir()

        dt = datetime(2022, 2, 14, 8, 0, 0)
        _write_jpeg_with_exif(src1, dt)
        _write_jpeg_with_exif(src2, dt)

        copy_file(src1, out, "MM")
        status2, dest2 = copy_file(src2, out, "MM")

        assert status2 == "copied"
        assert dest2 is not None
        assert dest2.name == "img (1).jpg"

    def test_video_file_sorted_by_filesystem_date(self, tmp_path: Path) -> None:
        """A .mp4 video (no EXIF) is sorted by filesystem mtime, not sent to Unknown/."""
        src = tmp_path / "clip.mp4"
        src.write_bytes(b"\x00\x00\x00 ftyp")
        out = tmp_path / "output"
        out.mkdir()
        known_ts = datetime(2021, 9, 5, 8, 0, 0).timestamp()
        os.utime(src, (known_ts, known_ts))

        status, dest = copy_file(src, out, "MM")
        assert status == "copied"
        assert dest is not None
        assert dest.parent == out / "2021" / "09"

    def test_mov_file_sorted_by_filesystem_date(self, tmp_path: Path) -> None:
        """A .mov video (no EXIF) is sorted by filesystem mtime, not sent to Unknown/."""
        src = tmp_path / "clip.mov"
        src.write_bytes(b"not really a video")
        out = tmp_path / "output"
        out.mkdir()
        known_ts = datetime(2022, 11, 22, 10, 0, 0).timestamp()
        os.utime(src, (known_ts, known_ts))

        status, dest = copy_file(src, out, "MM")
        assert status == "copied"
        assert dest is not None
        assert dest.parent == out / "2022" / "11"


# ---------------------------------------------------------------------------
# HEIC reading
# ---------------------------------------------------------------------------


class TestHeicReading:
    def test_heic_without_exif_returns_none(self, tmp_path: Path) -> None:
        """A HEIC file without accessible EXIF metadata returns None from read_exif_date.

        Note: creating a real HEIC with EXIF in tests requires pillow-heif and a valid
        HEIF encoder, which may not be available in CI. We verify that the function
        handles the .heic extension without crashing.
        """
        p = tmp_path / "photo.heic"
        # Write random bytes — pillow-heif will fail gracefully; read_exif_date returns None.
        p.write_bytes(b"\x00" * 64)
        result = read_exif_date(p)
        assert result is None


# ---------------------------------------------------------------------------
# collect_files
# ---------------------------------------------------------------------------


class TestCollectFiles:
    def test_collects_supported_extensions(self, tmp_path: Path) -> None:
        """collect_files returns only supported image/video files, not arbitrary ones."""
        (tmp_path / "a.jpg").write_bytes(b"x")
        (tmp_path / "b.PNG").write_bytes(b"x")
        (tmp_path / "c.mp4").write_bytes(b"x")
        (tmp_path / "d.txt").write_bytes(b"x")
        (tmp_path / "e.pdf").write_bytes(b"x")

        results = collect_files(tmp_path)
        names = {p.name for p in results}
        assert "a.jpg" in names
        assert "b.PNG" in names
        assert "c.mp4" in names
        assert "d.txt" not in names
        assert "e.pdf" not in names

    def test_recurses_into_subdirectories(self, tmp_path: Path) -> None:
        """collect_files descends recursively into subdirectories."""
        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (sub / "nested.jpg").write_bytes(b"x")
        results = collect_files(tmp_path)
        assert any(p.name == "nested.jpg" for p in results)

    def test_json_files_not_collected(self, tmp_path: Path) -> None:
        """JSON sidecar files are not included in collect_files results."""
        (tmp_path / "photo.jpg").write_bytes(b"x")
        (tmp_path / "photo.jpg.suppl.json").write_text('{"title": "photo.jpg"}')
        results = collect_files(tmp_path)
        names = {p.name for p in results}
        assert "photo.jpg" in names
        assert "photo.jpg.suppl.json" not in names


# ---------------------------------------------------------------------------
# read_takeout_date
# ---------------------------------------------------------------------------


class TestReadTakeoutDate:
    def _write_sidecar(self, path: Path, timestamp: int) -> None:
        """Write a minimal Google Takeout sidecar JSON with the given Unix timestamp.

        Args:
            path: Path to write the JSON file to.
            timestamp: Unix epoch integer for photoTakenTime.
        """
        data = {"title": path.stem, "photoTakenTime": {"timestamp": str(timestamp), "formatted": ""}}
        path.write_text(__import__("json").dumps(data), encoding="utf-8")

    def test_suppl_json_returns_correct_datetime(self, tmp_path: Path) -> None:
        """A ``.suppl.json`` sidecar with photoTakenTime returns the correct datetime."""
        media = tmp_path / "photo.jpg"
        _write_plain_jpeg(media)
        ts = 1704092534  # 2024-01-01 07:02:14 UTC
        self._write_sidecar(tmp_path / "photo.jpg.suppl.json", ts)
        result = read_takeout_date(media)
        assert result is not None
        assert result == __import__("datetime").datetime.fromtimestamp(ts)

    def test_plain_json_returns_correct_datetime(self, tmp_path: Path) -> None:
        """A plain ``.json`` sidecar is also recognised and returns the correct datetime."""
        media = tmp_path / "photo.jpg"
        _write_plain_jpeg(media)
        ts = 1704092534
        self._write_sidecar(tmp_path / "photo.jpg.json", ts)
        result = read_takeout_date(media)
        assert result is not None
        assert result == __import__("datetime").datetime.fromtimestamp(ts)

    def test_no_sidecar_returns_none(self, tmp_path: Path) -> None:
        """When no sidecar JSON exists, read_takeout_date returns None."""
        media = tmp_path / "photo.jpg"
        _write_plain_jpeg(media)
        assert read_takeout_date(media) is None

    def test_malformed_json_returns_none(self, tmp_path: Path) -> None:
        """A sidecar with invalid JSON returns None without raising."""
        media = tmp_path / "photo.jpg"
        _write_plain_jpeg(media)
        (tmp_path / "photo.jpg.suppl.json").write_text("not valid json", encoding="utf-8")
        assert read_takeout_date(media) is None

    def test_missing_key_returns_none(self, tmp_path: Path) -> None:
        """A sidecar missing the photoTakenTime key returns None without raising."""
        media = tmp_path / "photo.jpg"
        _write_plain_jpeg(media)
        (tmp_path / "photo.jpg.suppl.json").write_text('{"title": "photo.jpg"}', encoding="utf-8")
        assert read_takeout_date(media) is None


# ---------------------------------------------------------------------------
# copy_file with google_takeout
# ---------------------------------------------------------------------------


class TestCopyFileGoogleTakeout:
    def _write_sidecar(self, path: Path, timestamp: int) -> None:
        """Write a minimal Google Takeout sidecar JSON next to a media file.

        Args:
            path: Full path for the sidecar file (e.g. ``photo.jpg.suppl.json``).
            timestamp: Unix epoch integer for photoTakenTime.
        """
        data = {"photoTakenTime": {"timestamp": str(timestamp), "formatted": ""}}
        path.write_text(__import__("json").dumps(data), encoding="utf-8")

    def test_takeout_date_wins_over_exif(self, tmp_path: Path) -> None:
        """With google_takeout=True, the JSON sidecar date takes priority over EXIF."""
        src = tmp_path / "input" / "photo.jpg"
        src.parent.mkdir()
        out = tmp_path / "output"
        out.mkdir()

        exif_dt = datetime(2020, 6, 15, 10, 0, 0)
        _write_jpeg_with_exif(src, exif_dt)

        # Sidecar timestamp corresponds to 2024-01-01
        takeout_ts = 1704092534
        self._write_sidecar(src.parent / "photo.jpg.suppl.json", takeout_ts)

        status, dest = copy_file(src, out, "MM", google_takeout=True)
        assert status == "copied"
        assert dest is not None
        # Should use the sidecar date (2024), not the EXIF date (2020)
        assert dest.parts[-3] == "2024"

    def test_takeout_no_sidecar_falls_back_to_exif(self, tmp_path: Path) -> None:
        """With google_takeout=True but no sidecar, falls back to EXIF/filesystem."""
        src = tmp_path / "input" / "photo.jpg"
        src.parent.mkdir()
        out = tmp_path / "output"
        out.mkdir()

        exif_dt = datetime(2021, 3, 10, 8, 0, 0)
        _write_jpeg_with_exif(src, exif_dt)

        status, dest = copy_file(src, out, "MM", google_takeout=True)
        assert status == "copied"
        assert dest is not None
        assert dest.parts[-3] == "2021"

    def test_google_takeout_false_ignores_sidecar(self, tmp_path: Path) -> None:
        """With google_takeout=False, a sidecar is ignored and EXIF date is used."""
        src = tmp_path / "input" / "photo.jpg"
        src.parent.mkdir()
        out = tmp_path / "output"
        out.mkdir()

        exif_dt = datetime(2020, 6, 15, 10, 0, 0)
        _write_jpeg_with_exif(src, exif_dt)

        # Sidecar says 2024 — should be ignored
        takeout_ts = 1704092534
        self._write_sidecar(src.parent / "photo.jpg.suppl.json", takeout_ts)

        status, dest = copy_file(src, out, "MM", google_takeout=False)
        assert status == "copied"
        assert dest is not None
        # Should use EXIF date (2020), not sidecar (2024)
        assert dest.parts[-3] == "2020"
