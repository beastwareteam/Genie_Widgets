"""
QSS-Validator für WidgetSystem
Prüft alle QSS-Dateien im themes/-Verzeichnis auf ungültige CSS-Attribute (z.B. transition, animation, etc.).
Bricht mit Fehler ab, wenn ungültige Properties gefunden werden.
"""

import sys
from pathlib import Path
import re

# Liste aller in Qt/QSS NICHT unterstützten CSS-Properties
FORBIDDEN_PROPERTIES = [
    "transition",
    "animation",
    "animation-name",
    "animation-duration",
    "animation-timing-function",
    "animation-delay",
    "animation-iteration-count",
    "animation-direction",
    "animation-fill-mode",
    "animation-play-state",
    "filter",
    "backdrop-filter",
    "box-shadow",
    "text-shadow",
    "appearance",
    "user-select",
    "will-change",
    "scrollbar-width",
    "scrollbar-color",
    # ggf. weitere Properties ergänzen
]

QSS_DIR = Path(__file__).parent.parent / "themes"

# Regex für Properties
PROPERTY_REGEX = re.compile(r"^\s*([\w-]+)\s*:")


def validate_qss_file(qss_path: Path) -> list[str]:
    """Prüft eine QSS-Datei auf verbotene Properties."""
    errors = []
    with qss_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            match = PROPERTY_REGEX.match(line)
            if match:
                prop = match.group(1).strip().lower()
                if prop in FORBIDDEN_PROPERTIES:
                    errors.append(f"{qss_path.name}:{lineno}: Verbotene Property: '{prop}'")
    return errors


def main() -> None:
    qss_files = list(QSS_DIR.glob("*.qss"))
    all_errors = []
    for qss_file in qss_files:
        errors = validate_qss_file(qss_file)
        all_errors.extend(errors)
    if all_errors:
        print("FEHLER: Ungültige CSS-Properties in QSS gefunden:")
        for err in all_errors:
            print("  ", err)
        sys.exit(1)
    print("QSS-Validierung erfolgreich: Keine ungültigen Properties gefunden.")


if __name__ == "__main__":
    main()
