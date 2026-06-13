"""Tkinter GUI application for Photos Sorter."""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from .config import (
    LANGUAGE_EN,
    LANGUAGE_ES,
    MONTH_FORMAT_MM,
    MONTH_FORMAT_MM_MONTHNAME,
    load_config,
    save_config,
)
from .core import collect_files, copy_file
from .strings import t


class SettingsWindow(tk.Toplevel):
    """Modal settings dialog."""

    def __init__(self, parent: "App") -> None:
        """Initialise the settings window.

        Args:
            parent: The main App instance.
        """
        super().__init__(parent.root)
        self._parent = parent
        lang = parent.config["language"]

        self.title(t("settings_title", lang))
        self.resizable(False, False)
        self.grab_set()

        # Padded container so widgets don't hug the window edges
        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")

        pad = {"padx": 6, "pady": 5}

        # Date format
        ttk.Label(container, text=t("date_format_label", lang)).grid(row=0, column=0, sticky="w", **pad)
        self._date_var = tk.StringVar(value=parent.config["date_format"])
        date_formats = [MONTH_FORMAT_MM, MONTH_FORMAT_MM_MONTHNAME]
        ttk.Combobox(container, textvariable=self._date_var, values=date_formats, state="readonly", width=22).grid(
            row=0, column=1, sticky="w", **pad
        )

        # Language
        ttk.Label(container, text=t("language_label", lang)).grid(row=1, column=0, sticky="w", **pad)
        self._lang_var = tk.StringVar(value=parent.config["language"])
        lang_frame = ttk.Frame(container)
        lang_frame.grid(row=1, column=1, sticky="w", **pad)
        ttk.Radiobutton(lang_frame, text=t("lang_en", lang), variable=self._lang_var, value=LANGUAGE_EN).pack(
            anchor="w"
        )
        ttk.Radiobutton(lang_frame, text=t("lang_es", lang), variable=self._lang_var, value=LANGUAGE_ES).pack(
            anchor="w"
        )

        # Google Takeout format
        self._takeout_var = tk.BooleanVar(value=parent.config.get("google_takeout", False))
        self._takeout_chk = tk.Checkbutton(
            container,
            variable=self._takeout_var,
        )
        self._takeout_chk.grid(row=2, column=0, columnspan=2, sticky="w", **pad)
        self._refresh_takeout_label(lang)

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text=t("save", lang), command=self._save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=t("cancel", lang), command=self.destroy).pack(side="left", padx=5)

    def _refresh_takeout_label(self, lang: str) -> None:
        """Update the Google Takeout checkbox label for the given language.

        Args:
            lang: Language code (``"en"`` or ``"es"``).
        """
        self._takeout_chk.config(text=t("google_takeout_label", lang))

    def _save(self) -> None:
        """Persist settings and refresh the parent window labels."""
        self._parent.config["date_format"] = self._date_var.get()
        self._parent.config["language"] = self._lang_var.get()
        self._parent.config["google_takeout"] = self._takeout_var.get()
        save_config(self._parent.config)
        self._parent.refresh_labels()
        self.destroy()


class HelpWindow(tk.Toplevel):
    """Modal help dialog showing a localized usage guide."""

    def __init__(self, parent: "App") -> None:
        """Initialise the help window.

        Args:
            parent: The main App instance.
        """
        super().__init__(parent.root)
        lang = parent.config["language"]

        self.title(t("help_title", lang))
        self.resizable(False, False)
        self.geometry("560x460")
        self.grab_set()

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Scrollable text area
        text_frame = ttk.Frame(container)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        text_widget = tk.Text(
            text_frame,
            wrap="word",
            padx=8,
            pady=8,
            yscrollcommand=scrollbar.set,
            state="normal",
        )
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=text_widget.yview)

        text_widget.insert("1.0", t("help_text", lang))
        text_widget.config(state="disabled")

        # Close button
        ttk.Button(container, text=t("close", lang), command=self.destroy).grid(row=1, column=0, pady=(8, 0))


class App:
    """Main application window."""

    def __init__(self) -> None:
        """Initialise the application, loading config and building the UI."""
        self.config = load_config()
        self.root = tk.Tk()
        self._set_icon()

        self._input_var = tk.StringVar()
        self._output_var = tk.StringVar()
        self._status_var = tk.StringVar()
        self._progress_var = tk.DoubleVar()
        self._widgets: dict[str, ttk.Widget] = {}
        self._build_ui()
        self.refresh_labels()
        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())

    def _set_icon(self) -> None:
        """Set the application window icon from the bundled PNG asset.

        Resolves the asset path relative to the package directory so the icon works both when running
        from source and when running from a PyInstaller bundle (where `sys._MEIPASS` points to the
        extraction directory).  Failures are silently swallowed so a missing or unreadable icon never
        prevents the app from starting.
        """
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
            icon_path = base / "assets" / "icon.png"
            self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build all widgets and lay them out inside a padded ttk.Frame container."""
        root = self.root
        root.resizable(True, True)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        # Padded container frame — widgets are placed here, not directly on root
        container = ttk.Frame(root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(1, weight=1)

        pad = {"padx": 6, "pady": 4}

        # Input folder row
        lbl_input = ttk.Label(container, text="")
        lbl_input.grid(row=1, column=0, sticky="w", **pad)
        self._widgets["lbl_input"] = lbl_input

        ttk.Entry(container, textvariable=self._input_var, width=40).grid(row=1, column=1, sticky="ew", **pad)

        btn_input = ttk.Button(container, text="", command=self._pick_input)
        btn_input.grid(row=1, column=2, **pad)
        self._widgets["btn_input"] = btn_input

        # Output folder row
        lbl_output = ttk.Label(container, text="")
        lbl_output.grid(row=2, column=0, sticky="w", **pad)
        self._widgets["lbl_output"] = lbl_output

        ttk.Entry(container, textvariable=self._output_var, width=40).grid(row=2, column=1, sticky="ew", **pad)

        btn_output = ttk.Button(container, text="", command=self._pick_output)
        btn_output.grid(row=2, column=2, **pad)
        self._widgets["btn_output"] = btn_output

        # Progress bar
        self._progress_bar = ttk.Progressbar(container, variable=self._progress_var, maximum=100, length=350)
        self._progress_bar.grid(row=3, column=0, columnspan=3, padx=6, pady=6, sticky="ew")

        # Status label
        lbl_status = ttk.Label(container, textvariable=self._status_var, wraplength=380)
        lbl_status.grid(row=4, column=0, columnspan=3, **pad)
        self._widgets["lbl_status"] = lbl_status

        # Bottom button row
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=8)

        btn_help = ttk.Button(btn_frame, text="", command=self._open_help)
        btn_help.pack(side="left", padx=6)
        self._widgets["btn_help"] = btn_help

        btn_settings = ttk.Button(btn_frame, text="", command=self._open_settings)
        btn_settings.pack(side="left", padx=6)
        self._widgets["btn_settings"] = btn_settings

        btn_start = ttk.Button(btn_frame, text="", command=self._start)
        btn_start.pack(side="left", padx=6)
        self._widgets["btn_start"] = btn_start

    def refresh_labels(self) -> None:
        """Re-apply translated strings to all labelled widgets using the current language."""
        lang = self.config["language"]
        self.root.title(t("app_title", lang))
        self._widgets["lbl_input"].config(text=t("input_folder", lang))
        self._widgets["lbl_output"].config(text=t("output_folder", lang))
        self._widgets["btn_input"].config(text=t("browse", lang))
        self._widgets["btn_output"].config(text=t("browse", lang))
        self._widgets["btn_start"].config(text=t("start", lang))
        self._widgets["btn_settings"].config(text=t("settings", lang))
        self._widgets["btn_help"].config(text=t("help_button", lang))
        self._status_var.set(t("idle", lang))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _pick_input(self) -> None:
        """Open a folder dialog and set the input path."""
        lang = self.config["language"]
        folder = filedialog.askdirectory(title=t("select_input", lang))
        if folder:
            self._input_var.set(folder)

    def _pick_output(self) -> None:
        """Open a folder dialog and set the output path."""
        lang = self.config["language"]
        folder = filedialog.askdirectory(title=t("select_output", lang))
        if folder:
            self._output_var.set(folder)

    def _open_settings(self) -> None:
        """Open the settings dialog."""
        SettingsWindow(self)

    def _open_help(self) -> None:
        """Open the help dialog."""
        HelpWindow(self)

    def _start(self) -> None:
        """Validate inputs and kick off the organise thread."""
        lang = self.config["language"]
        inp = self._input_var.get().strip()
        out = self._output_var.get().strip()
        if not inp or not out:
            messagebox.showwarning(t("app_title", lang), t("no_folder_selected", lang))
            return
        self._widgets["btn_start"].config(state="disabled")
        self._status_var.set(t("running", lang))
        threading.Thread(target=self._run, args=(Path(inp), Path(out)), daemon=True).start()

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    def _run(self, input_root: Path, output_root: Path) -> None:
        """Organise files in a background thread and post progress to the UI via `after`.

        Args:
            input_root: Directory to scan for images/videos.
            output_root: Root of the destination folder tree.
        """
        lang = self.config["language"]
        date_format = self.config["date_format"]
        google_takeout = self.config.get("google_takeout", False)

        files = collect_files(input_root)
        total = len(files)
        copied = skipped = unknown = 0

        for i, src in enumerate(files, start=1):
            try:
                status, _ = copy_file(src, output_root, date_format, lang, google_takeout=google_takeout)
            except Exception as exc:  # noqa: BLE001
                status = "skipped"
                print(t("error_copy", lang, file=src.name, error=str(exc)))

            match status:
                case "copied":
                    copied += 1
                case "unknown":
                    unknown += 1
                case _:
                    skipped += 1

            pct = (i / total * 100) if total else 100
            progress_text = t("progress", lang, done=str(i), total=str(total))
            self.root.after(0, self._update_progress, pct, progress_text)

        summary = t("summary", lang, copied=str(copied), skipped=str(skipped), unknown=str(unknown))
        self.root.after(0, self._finish, summary)

    def _update_progress(self, pct: float, text: str) -> None:
        """Update the progress bar and status label (called on the main thread).

        Args:
            pct: Percentage complete (0–100).
            text: Status text to display.
        """
        self._progress_var.set(pct)
        self._status_var.set(text)

    def _finish(self, summary: str) -> None:
        """Reset UI state after the organise run completes.

        Args:
            summary: The summary string to display.
        """
        self._status_var.set(summary)
        self._progress_var.set(100)
        self._widgets["btn_start"].config(state="normal")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the Tkinter main loop."""
        self.root.mainloop()
