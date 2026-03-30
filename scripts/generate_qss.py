"""
QSS-Generator für WidgetSystem
Erzeugt QSS-Dateien aus zentralen Design-Tokens (config/theme_tokens.json).
Nur die Tokens editieren, nicht die QSS direkt!
"""

import json
from pathlib import Path

TOKENS_PATH = Path(__file__).parent.parent / "config" / "theme_tokens.json"
QSS_OUT_PATH = Path(__file__).parent.parent / "themes" / "generated_theme.qss"

QSS_TEMPLATE = """
QWidget {
    background-color: {bg-root};
    color: {text-primary};
    border-radius: {md};
}

QPushButton {
    background-color: {accent-soft};
    color: {text-bright};
    border-radius: {md};
}
/* ... weitere Komponenten nach Bedarf ... */
"""

def main() -> None:
    with TOKENS_PATH.open("r", encoding="utf-8") as f:
        tokens = json.load(f)
    colors = tokens["colors"]
    radius = tokens["radius"]
    sizes = tokens["sizes"]
    qss = QSS_TEMPLATE.format(
        **colors,
        **radius,
        **sizes
    )
    QSS_OUT_PATH.write_text(qss, encoding="utf-8")
    print(f"QSS generiert: {QSS_OUT_PATH}")

if __name__ == "__main__":
    main()
