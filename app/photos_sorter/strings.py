"""UI string table for internationalisation (English and Spanish)."""

from typing import Literal

Language = Literal["en", "es"]

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "Photos Sorter",
        "input_folder": "Input Folder:",
        "output_folder": "Output Folder:",
        "browse": "Browse",
        "start": "Start",
        "settings": "Settings",
        "progress": "Progress: {done} / {total}",
        "summary": "Done! Copied: {copied}  Skipped: {skipped}  Unknown: {unknown}",
        "idle": "Ready",
        "running": "Running…",
        "select_input": "Select Input Folder",
        "select_output": "Select Output Folder",
        "settings_title": "Settings",
        "date_format_label": "Month folder format:",
        "language_label": "Language:",
        "save": "Save",
        "cancel": "Cancel",
        "no_folder_selected": "Please select both input and output folders.",
        "error_copy": "Error copying {file}: {error}",
        "lang_en": "English",
        "lang_es": "Spanish",
        "google_takeout_label": "Google Takeout format",
        "help_button": "Help",
        "help_title": "Help",
        "close": "Close",
        "help_text": (
            "How to use Photos Sorter\n\n"
            "1. Click \"Browse\" next to Input Folder and choose the folder that contains your photos and videos.\n"
            "2. Click \"Browse\" next to Output Folder and choose where the organized copies should be saved.\n"
            "3. Click \"Start\". Your files are COPIED into folders by year and month (for example 2024/06). "
            "Your original files are never modified or moved.\n"
            "4. When it finishes, you will see a summary of how many files were copied.\n\n"
            "How the date is chosen\n\n"
            "For each file the tool looks for a date in this order:\n"
            "1. Google Takeout data (if that setting is on).\n"
            "2. The photo's EXIF capture date.\n"
            "3. The file's date on your disk.\n"
            "If none of these exist, the file is placed in an \"Unknown\" folder.\n\n"
            "Settings\n\n"
            "- Month folder format: how the month folder is named.\n"
            "   MM gives folders like 2024/06.\n"
            "   MM-MonthName gives folders like 2024/06-June.\n"
            "- Language: switch the app between English and Spanish. This also changes the month names.\n"
            "- Google Takeout format: turn this on if your folder comes from Google Takeout, where each photo "
            "has a matching .json file. The tool will read the real date from that .json file. "
            "The .json files are not copied.\n\n"
            "More help\n\n"
            "For more guides and help, visit https://photos-sorter.oterom.xyz"
        ),
    },
    "es": {
        "app_title": "Organizador de Fotos",
        "input_folder": "Carpeta de entrada:",
        "output_folder": "Carpeta de salida:",
        "browse": "Examinar",
        "start": "Iniciar",
        "settings": "Ajustes",
        "progress": "Progreso: {done} / {total}",
        "summary": "Listo! Copiados: {copied}  Omitidos: {skipped}  Sin fecha: {unknown}",
        "idle": "Listo",
        "running": "Procesando…",
        "select_input": "Seleccionar carpeta de entrada",
        "select_output": "Seleccionar carpeta de salida",
        "settings_title": "Ajustes",
        "date_format_label": "Formato de carpeta de mes:",
        "language_label": "Idioma:",
        "save": "Guardar",
        "cancel": "Cancelar",
        "no_folder_selected": "Selecciona las carpetas de entrada y salida.",
        "error_copy": "Error copiando {file}: {error}",
        "lang_en": "Inglés",
        "lang_es": "Español",
        "google_takeout_label": "Formato de Google Takeout",
        "help_button": "Ayuda",
        "help_title": "Ayuda",
        "close": "Cerrar",
        "help_text": (
            "Cómo usar Organizador de Fotos\n\n"
            "1. Haz clic en \"Examinar\" junto a Carpeta de entrada y elige la carpeta que contiene tus fotos y vídeos.\n"
            "2. Haz clic en \"Examinar\" junto a Carpeta de salida y elige dónde se guardarán las copias organizadas.\n"
            "3. Haz clic en \"Iniciar\". Tus archivos se COPIAN en carpetas por año y mes (por ejemplo 2024/06). "
            "Tus archivos originales nunca se modifican ni se mueven.\n"
            "4. Cuando termine, verás un resumen de cuántos archivos se copiaron.\n\n"
            "Cómo se elige la fecha\n\n"
            "Para cada archivo, la herramienta busca una fecha en este orden:\n"
            "1. Datos de Google Takeout (si ese ajuste está activado).\n"
            "2. La fecha de captura EXIF de la foto.\n"
            "3. La fecha del archivo en tu disco.\n"
            "Si no existe ninguna, el archivo se coloca en una carpeta \"Unknown\".\n\n"
            "Ajustes\n\n"
            "- Formato de carpeta de mes: cómo se nombra la carpeta del mes.\n"
            "   MM da carpetas como 2024/06.\n"
            "   MM-MonthName da carpetas como 2024/06-Junio.\n"
            "- Idioma: cambia la aplicación entre inglés y español. También cambia los nombres de los meses.\n"
            "- Formato de Google Takeout: actívalo si tu carpeta proviene de Google Takeout, donde cada foto "
            "tiene un archivo .json correspondiente. La herramienta leerá la fecha real de ese archivo .json. "
            "Los archivos .json no se copian.\n\n"
            "Más ayuda\n\n"
            "Para más guías y ayuda, visita https://photos-sorter.oterom.xyz"
        ),
    },
}


def t(key: str, lang: Language = "en", **kwargs: str) -> str:
    """Return a translated string for the given key and language.

    Args:
        key: The string key to look up.
        lang: The language code ("en" or "es"). Falls back to English for unknown codes.
        **kwargs: Named placeholders that will be formatted into the string.

    Returns:
        The translated (and optionally formatted) string.
    """
    table = STRINGS.get(lang, STRINGS["en"])
    raw = table.get(key, STRINGS["en"].get(key, key))
    if kwargs:
        return raw.format(**kwargs)
    return raw
