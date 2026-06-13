"""Configuration management: load/save user preferences to ~/.photos_sorter/config.json."""

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".photos_sorter"
CONFIG_FILE = CONFIG_DIR / "config.json"

MONTH_FORMAT_MM = "MM"
MONTH_FORMAT_MM_MONTHNAME = "MM-MonthName"

LANGUAGE_EN = "en"
LANGUAGE_ES = "es"

VALID_MONTH_FORMATS = {MONTH_FORMAT_MM, MONTH_FORMAT_MM_MONTHNAME}

DEFAULTS: dict[str, Any] = {
    "date_format": MONTH_FORMAT_MM,
    "language": LANGUAGE_EN,
    "google_takeout": False,
}


def load_config() -> dict[str, Any]:
    """Load configuration from disk, creating with defaults if the file does not exist.

    Returns:
        A dict containing all configuration keys, merged with defaults for any missing keys.
    """
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(DEFAULTS, indent=2))
        return dict(DEFAULTS)

    try:
        data = json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        data = {}

    config = dict(DEFAULTS)
    config.update(data)
    # Fall back to default if the stored month format is no longer valid (e.g. old "YYYY-MM" or "YYYY/MM" values).
    if config.get("date_format") not in VALID_MONTH_FORMATS:
        config["date_format"] = DEFAULTS["date_format"]
    return config


def save_config(config: dict[str, Any]) -> None:
    """Persist configuration dict to disk.

    Args:
        config: The configuration dict to save.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
