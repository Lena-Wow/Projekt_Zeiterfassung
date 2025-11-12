# courses_module.py
from pathlib import Path
from typing import List

# Standard-Dateiname (neben app.py)
DEFAULT_FILENAME = "courses.txt"

# Default-Kurse, falls Datei nicht existiert
DEFAULT_COURSES = [
    "Projekt",
    "Python",
    "SQL",
    "ML",
    "Excel",
    "EDA",
    "ETL",
    "PowerBI",
    "AWS",
    "ScrumPO",
]


def _default_path() -> Path:
    """Pfad zur Datei relativ zum Modul (oder Arbeitsverzeichnis)."""
    return Path.cwd() / DEFAULT_FILENAME


def load_courses(path: Path | str | None = None) -> List[str]:
    """
    Lädt die Kursliste aus einer Textdatei (eine Zeile = ein Kurs).
    Falls die Datei nicht existiert, werden DEFAULT_COURSES zurückgegeben
    und die Datei optional erzeugt.
    """
    p = Path(path) if path else _default_path()
    if p.exists():
        text = p.read_text(encoding="utf-8")
        lines = [line.strip() for line in text.splitlines()]
        # Filtere leere Zeilen
        return [ln for ln in lines if ln]
    else:
        # Schreibe Default-Datei (optional) und gib Defaults zurück
        try:
            p.write_text("\n".join(DEFAULT_COURSES), encoding="utf-8")
        except Exception:
            # Wenn Schreiben fehlschlägt (z. B. Berechtigung), ignoriere still
            pass
        return DEFAULT_COURSES.copy()


def save_courses(courses: List[str], path: Path | str | None = None) -> None:
    """
    Speichert die Kursliste in der Datei (eine Zeile = ein Kurs).
    Überschreibt vorhandene Datei.
    """
    p = Path(path) if path else _default_path()
    # Säubere die Liste: Strings trimmen, leere raus
    cleaned = [str(c).strip() for c in courses if str(c).strip()]
    p.write_text("\n".join(cleaned), encoding="utf-8")


def ensure_courses_file(path: Path | str | None = None) -> None:
    """Erstellt die Datei mit Default-Kursen, falls sie nicht existiert."""
    p = Path(path) if path else _default_path()
    if not p.exists():
        p.write_text("\n".join(DEFAULT_COURSES), encoding="utf-8")
