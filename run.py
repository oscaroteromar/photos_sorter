"""Entry point: launch the Photos Sorter GUI."""

import os

os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")

from photos_sorter.app import App


def main() -> None:
    """Create and run the application."""
    App().run()


if __name__ == "__main__":
    main()
