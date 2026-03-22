# WidgetSystem - Qt ADS Docking Application

Vollständig typsichere Python-Anwendung mit Qt6 (PySide6) und Advanced Docking System (QtAds).

## Requirements

- **Python**: 3.12+ (getestet mit 3.12.7)
- **OS**: Windows, Linux, macOS

## Installation & Setup

### 1. Virtuelle Umgebung aktivieren

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

Für Entwicklung (mit Type-Checking, Linting, Testing):

```bash
pip install -e ".[dev]"
```

## Starten der Anwendung

### Mit Play-Button (VS Code)
1. `F5` oder klick auf den Play-Button
2. Wähle "Run WidgetSystem" aus der Debug-Konfiguration

### Aus dem Terminal

```bash
# Mit aktivierter venv
python main.py

# Oder direkt
.venv\Scripts\python.exe main.py
```

## Code Quality & Typsicherheit

###  Linting (Pylint)
```bash
python -m pylint main.py
```

**Bewertung:** ~9.4/10 (sehr gut)

### Type Checking (Mypy)
```bash
python -m mypy main.py --ignore-missing-imports
```

### Code Formatting

**Black** (Code-Format):
```bash
black main.py
```

**isort** (Import-Sorting):
```bash
isort main.py
```

### Testing (Pytest)
```bash
python -m pytest tests/
```

## Konfiguration

### VS Code Settings
- **Interpreter**: `./.venv/Scripts/python.exe` (auto-konfiguriert)
- **Linter**: Pylint (aktiviert)
- **Terminal**: Aktiviert venv auf Startup automatisch

### Konfigurationsdateien

| Datei | Zweck |
|-------|------|
| `pyproject.toml` | Python-Projekt & Tool-Konfiguration |
| `.pylintrc` | Pylint-Einstellungen |
| `pyrightconfig.json` | Pyright/Pylance Typ-Einstellungen |
| `.vscode/settings.json` | VS Code Editor-Einstellungen |
| `.vscode/launch.json` | Debug-Konfiguration |

## Struktur

```
WidgetSystem/
├── main.py                 # Entry-Point
├── *_factory.py           # Factory Pattern Implementierung
├── config/
│   ├── *.json             # Konfigurationsdateien
├── schemas/               # JSON-Schema Validierungen
├── themes/                # QSS Stylesheets
├── data/                  # Runtime Daten
└── .venv/                 # Virtual Environment
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6QtAds'"

```bash
# Stelle sicher, dass die venv aktiviert ist
.\.venv\Scripts\Activate.ps1

# Dann nochmal starten
python main.py
```

### Pylint findet PySide6 nicht

Das ist normal! Pylint kann Compiled C++ Extensions nicht immer analysieren.  
Konfiguriert in `.pylintrc` zu ignorieren (`extension-pkg-allow-list`).

### VS Code zeigt noch Import-Fehler

1. **Reload Window**: `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Interpreter neu wählen**: `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Wähle `.\.venv\Scripts\python.exe`

##  Tipps für Entwicklung

- Nutze **Black** für konsistentes Code-Formatting
- Nutze **isort** vor einer Commit für saubere Imports
- Führe **pylint** vor Commits aus (Mindestens 9.0/10)
- Type Hints sind optional, aber empfohlen!

## Lizenz & Kontakt

> Vollständig sichere, typsichere Qt-Anwendung mit Factory Pattern
